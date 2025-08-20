#!/bin/bash
# diagnose_agent_registration.sh - Debug Claude Code agent registration

echo "=== Claude Code Agent Registration Diagnostic ==="
echo

echo "1. Checking Claude Code version:"
claude --version 2>&1 || echo "Claude CLI not found"

echo -e "\n2. Checking for agent registration commands:"
claude --help 2>&1 | grep -i agent || echo "No agent commands found in help"

echo -e "\n3. Checking file locations:"
echo "Build Detective agent files found:"
find ~ -name "*build-detective*" -type f 2>/dev/null | head -20

echo -e "\n4. Current directory structure:"
ls -la ~/.claude/ 2>/dev/null || echo "~/.claude/ not found"
ls -la .claude/ 2>/dev/null || echo ".claude/ not found"

echo -e "\n5. Validating YAML frontmatter:"
for file in ~/.claude/agents/*.md ~/.claude/subagents/*/*.md .claude/agents/*.md .claude/subagents/*/*.md; do
    if [ -f "$file" ]; then
        echo "Checking: $file"
        head -n 15 "$file" | grep -E "^(---|name:|description:|tools:|model:)"
        echo "---"
    fi
done

echo -e "\n6. Task tool agent discovery:"
echo "Available agents reported by Task tool:"
# This would be from Claude Code's perspective, but we'll check what we can

echo -e "\n7. Environment variables:"
env | grep -i claude || echo "No Claude environment variables found"

echo -e "\n8. Process check:"
ps aux | grep -i claude | grep -v grep || echo "No Claude processes running"

echo -e "\n9. Attempting agent registration commands:"
claude register-agent ~/.claude/agents/build-detective.md 2>&1 || echo "register-agent command not available"
claude init --add-agent build-detective-subagent 2>&1 || echo "init --add-agent command not available"
claude list-agents 2>&1 || echo "list-agents command not available"
claude agents list 2>&1 || echo "agents list command not available"

echo -e "\n10. Checking Task tool directly:"
echo "This would require Claude Code's internal agent discovery mechanism"

echo -e "\nDiagnostic complete."