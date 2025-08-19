"""
Issue tracking database for deduplication and solution caching
"""
import sqlite3
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger(__name__)

class IssueDatabase:
    """SQLite-based issue tracking with deduplication and solution caching"""
    
    def __init__(self, db_path: str = "data/issues.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
                
                # Issues table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS issues (
                        id INTEGER PRIMARY KEY,
                        repo TEXT NOT NULL,
                        error_signature TEXT NOT NULL,
                        job_name TEXT,
                        workflow_name TEXT,
                        error_type TEXT,
                        primary_error TEXT,
                        logs_excerpt TEXT,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        occurrence_count INTEGER DEFAULT 1,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Solutions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS solutions (
                        id INTEGER PRIMARY KEY,
                        error_signature TEXT UNIQUE NOT NULL,
                        solution_text TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        suggested_action TEXT,
                        error_type TEXT,
                        success_rate REAL DEFAULT 0.0,
                        usage_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Analysis cache table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_cache (
                        id INTEGER PRIMARY KEY,
                        error_signature TEXT UNIQUE NOT NULL,
                        analysis_data TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_error_signature ON issues(error_signature)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_repo_error ON issues(repo, error_signature)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_solution_signature ON solutions(error_signature)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_signature ON analysis_cache(error_signature)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON analysis_cache(expires_at)")
                
                conn.commit()
                logger.info("✅ Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def generate_signature(self, failure: Dict) -> str:
        """Generate unique signature for failure deduplication"""
        # Combine key elements for signature
        elements = [
            failure.get('repo', ''),
            failure.get('job_name', ''),
            failure.get('error_type', ''),
            self._normalize_error(failure.get('primary_error', '')),
            self._extract_key_patterns(failure.get('logs', ''))
        ]
        
        # Create hash from combined elements
        signature_text = '|'.join(str(e) for e in elements)
        return hashlib.sha256(signature_text.encode()).hexdigest()[:16]
    
    def _normalize_error(self, error_text: str) -> str:
        """Normalize error text for consistent signatures"""
        if not error_text:
            return ""
        
        import re
        
        # Remove variable parts that change between runs
        normalized = error_text.lower()
        
        # Remove file paths, line numbers, timestamps
        normalized = re.sub(r'/[^\s]+', '<path>', normalized)
        normalized = re.sub(r'line \d+', 'line <num>', normalized)
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '<timestamp>', normalized)
        normalized = re.sub(r'\d+\.\d+\.\d+', '<version>', normalized)
        
        # Remove excessive whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _extract_key_patterns(self, logs: str) -> str:
        """Extract key error patterns from logs for signature"""
        if not logs:
            return ""
        
        import re
        
        # Key patterns that indicate error type
        key_patterns = [
            r'ImportError|ModuleNotFoundError',
            r'docker.*failed|COPY.*failed',
            r'=\d+\.\d+\.\d+',  # UV malformed versions
            r'pytest.*not available',
            r'submodule.*failed',
            r'compilation failed|syntax error',
            r'permission denied|access denied',
            r'timeout|timed out'
        ]
        
        found_patterns = []
        for pattern in key_patterns:
            if re.search(pattern, logs, re.IGNORECASE):
                found_patterns.append(pattern)
        
        return '|'.join(found_patterns)
    
    def has_recent_solution(self, failure: Dict, hours: int = 1) -> bool:
        """Check if we have a recent solution for this failure type"""
        signature = self.generate_signature(failure)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM solutions 
                    WHERE error_signature = ? 
                    AND last_used > datetime('now', '-{} hours')
                    AND confidence > 0.7
                """.format(hours), (signature,))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except sqlite3.Error as e:
            logger.error(f"❌ Database query failed: {e}")
            return False
    
    def get_cached_solution(self, failure: Dict) -> Optional[Dict]:
        """Get cached solution for failure if available"""
        signature = self.generate_signature(failure)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT solution_text, confidence, suggested_action, success_rate
                    FROM solutions 
                    WHERE error_signature = ? 
                    AND confidence > 0.7
                    ORDER BY usage_count DESC, confidence DESC
                    LIMIT 1
                """, (signature,))
                
                row = cursor.fetchone()
                if row:
                    # Update usage statistics
                    conn.execute("""
                        UPDATE solutions 
                        SET usage_count = usage_count + 1, 
                            last_used = CURRENT_TIMESTAMP
                        WHERE error_signature = ?
                    """, (signature,))
                    conn.commit()
                    
                    return {
                        'id': f'cached-{signature}',
                        'status': 'CACHED',
                        'primary_error': row[0],
                        'confidence': row[1],
                        'suggested_action': row[2],
                        'success_rate': row[3],
                        'source': 'cache'
                    }
                
                return None
                
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to get cached solution: {e}")
            return None
    
    def cache_solution(self, analysis: Dict):
        """Cache successful analysis solution"""
        if analysis.get('confidence', 0) < 0.7:
            return  # Only cache high-confidence solutions
        
        signature = analysis.get('error_signature') or 'unknown'
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert or update solution
                conn.execute("""
                    INSERT OR REPLACE INTO solutions 
                    (error_signature, solution_text, confidence, suggested_action, error_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    signature,
                    analysis.get('primary_error', ''),
                    analysis.get('confidence', 0),
                    analysis.get('suggested_action', ''),
                    analysis.get('error_type', '')
                ))
                
                conn.commit()
                logger.info(f"💾 Cached solution for signature: {signature}")
                
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to cache solution: {e}")
    
    def record_issue(self, failure: Dict, analysis: Dict) -> int:
        """Record new issue or update existing one"""
        signature = self.generate_signature(failure)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if issue exists
                cursor = conn.execute("""
                    SELECT id, occurrence_count FROM issues 
                    WHERE error_signature = ?
                """, (signature,))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing issue
                    issue_id, count = existing
                    conn.execute("""
                        UPDATE issues 
                        SET occurrence_count = ?, 
                            last_seen = CURRENT_TIMESTAMP,
                            logs_excerpt = ?
                        WHERE id = ?
                    """, (count + 1, failure.get('logs', '')[:1000], issue_id))
                    
                    logger.info(f"📊 Updated issue {issue_id}: {count + 1} occurrences")
                    return issue_id
                else:
                    # Insert new issue
                    cursor = conn.execute("""
                        INSERT INTO issues 
                        (repo, error_signature, job_name, workflow_name, error_type, 
                         primary_error, logs_excerpt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        failure.get('repo', ''),
                        signature,
                        failure.get('job_name', ''),
                        failure.get('workflow_name', ''),
                        analysis.get('error_type', ''),
                        analysis.get('primary_error', ''),
                        failure.get('logs', '')[:1000]
                    ))
                    
                    issue_id = cursor.lastrowid
                    conn.commit()
                    
                    logger.info(f"📝 Recorded new issue {issue_id}")
                    return issue_id
                
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to record issue: {e}")
            return -1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Total issues
                cursor = conn.execute("SELECT COUNT(*) FROM issues")
                stats['total_issues'] = cursor.fetchone()[0]
                
                # Cached solutions
                cursor = conn.execute("SELECT COUNT(*) FROM solutions")
                stats['cached_solutions'] = cursor.fetchone()[0]
                
                # Top error types
                cursor = conn.execute("""
                    SELECT error_type, SUM(occurrence_count) as total
                    FROM issues 
                    WHERE error_type IS NOT NULL
                    GROUP BY error_type 
                    ORDER BY total DESC 
                    LIMIT 5
                """)
                stats['top_error_types'] = cursor.fetchall()
                
                # Recent activity (last 24 hours)
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM issues 
                    WHERE last_seen > datetime('now', '-1 day')
                """)
                stats['recent_issues'] = cursor.fetchone()[0]
                
                return stats
                
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {}
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM analysis_cache 
                    WHERE expires_at < CURRENT_TIMESTAMP
                """)
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"🧹 Cleaned up {deleted_count} expired cache entries")
                
        except sqlite3.Error as e:
            logger.error(f"❌ Cache cleanup failed: {e}")