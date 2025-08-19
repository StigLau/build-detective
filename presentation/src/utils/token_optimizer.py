"""
Token usage optimization for cost-effective AI analysis
"""
import re
from typing import List

class TokenOptimizer:
    """Minimizes token usage while preserving information"""
    
    def compress_logs(self, logs: str, max_tokens: int = 500) -> str:
        """
        Compress logs to essential information for AI analysis
        
        Args:
            logs: Raw log output
            max_tokens: Maximum tokens to target
            
        Returns:
            Compressed log text focusing on error vicinity
        """
        if not logs:
            return ""
        
        lines = logs.split('\n')
        
        # Step 1: Extract stack traces and error patterns
        error_lines = []
        for i, line in enumerate(lines):
            if self._is_error_line(line):
                # Include ±5 lines around error for context
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                error_lines.extend(lines[start:end])
        
        # Step 2: Remove timestamps and clean up
        cleaned_lines = []
        for line in error_lines:
            cleaned = self._clean_line(line)
            if cleaned and cleaned not in cleaned_lines:  # Deduplicate
                cleaned_lines.append(cleaned)
        
        # Step 3: Truncate to token limit
        compressed = '\n'.join(cleaned_lines)
        
        # Rough token estimation: ~4 chars per token
        if len(compressed) > max_tokens * 4:
            # Take first and last parts if too long
            half_size = (max_tokens * 4) // 2
            compressed = compressed[:half_size] + "\n...\n" + compressed[-half_size:]
        
        return compressed
    
    def _is_error_line(self, line: str) -> bool:
        """Check if line contains error indicators"""
        error_patterns = [
            r'\bERROR\b', r'\bFAILED\b', r'\bfatal:', r'exit code [1-9]',
            r'not found', r'ImportError', r'ModuleNotFoundError',
            r'AssertionError', r'Exception', r'Error:',
            r'compilation failed', r'syntax error', r'cannot find symbol',
            r'permission denied', r'connection refused', r'timeout',
            r'=\d+\.\d+\.\d+',  # Malformed UV version files
            r'pytest.*spawn', r'--extra dev'
        ]
        
        line_lower = line.lower()
        for pattern in error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _clean_line(self, line: str) -> str:
        """Clean individual log line"""
        # Remove ANSI escape codes
        line = re.sub(r'\x1b\[[0-9;]*m', '', line)
        
        # Remove timestamps (various formats)
        line = re.sub(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.\d]*\w*\s*', '', line)
        line = re.sub(r'^\[\d{2}:\d{2}:\d{2}\]\s*', '', line)
        
        # Remove excessive whitespace
        line = re.sub(r'\s+', ' ', line).strip()
        
        return line
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count"""
        # Rough heuristic: ~4 characters per token
        return len(text) // 4
    
    def batch_for_efficiency(self, items: List[str], max_batch_tokens: int = 1000) -> List[List[str]]:
        """Group items into batches for efficient processing"""
        batches = []
        current_batch = []
        current_tokens = 0
        
        for item in items:
            item_tokens = self.estimate_tokens(item)
            
            if current_tokens + item_tokens > max_batch_tokens and current_batch:
                batches.append(current_batch)
                current_batch = [item]
                current_tokens = item_tokens
            else:
                current_batch.append(item)
                current_tokens += item_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        return batches