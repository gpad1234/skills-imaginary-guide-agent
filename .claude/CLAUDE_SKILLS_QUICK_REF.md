# Claude Skills Quick Reference

## What are Claude Skills?

Claude Skills are reusable scripts that Claude can automatically discover and execute in Claude Code. They provide:
- **Token efficiency**: Up to 65% reduction vs. MCP-only
- **Automatic discovery**: Claude finds the right skill based on your question
- **Consistent output**: Structured JSON for reliable parsing
- **Quick execution**: Pre-tested scripts run immediately

## How to Use

Simply ask Claude questions in natural language. Claude will automatically detect and run the appropriate skill.

### System Health Check

**Ask:**
- "Check system health"
- "What's the system status?"
- "Show me resource usage"
- "How is my computer performing?"

**Claude will:**
- Run `system-health` skill
- Return OS info, memory usage, top processes, network status
- Provide natural language summary

**Example Response:**
```
Your system is healthy:
- macOS 14.2 with 8 CPU cores
- 10 processes consuming 12.4 GB total
- 2 network interfaces active
- 45 active connections
```

### Top Memory Processes

**Ask:**
- "Which processes are using the most memory?"
- "Show me top processes"
- "What's consuming resources?"
- "List memory-heavy applications"

**Claude will:**
- Run `top-processes` skill
- Return sorted list of processes by memory usage
- Show PID, memory consumption, process path

**Example Response:**
```
Top memory consumers:
1. Chrome (PID 1234) - 2.4 GB
2. VSCode (PID 5678) - 1.8 GB
3. Docker (PID 9012) - 1.2 GB
```

## Creating Your Own Skills

### Step 1: Create Skill Directory

```bash
mkdir -p .claude/skills/my-skill-name/scripts
```

### Step 2: Write SKILL.md

```markdown
---
name: my-skill-name
description: Clear description of when to use this skill
allowed-tools: Bash
---

# My Skill Title

Run this when the user asks about [trigger scenarios].

## Run using:

\`\`\`bash
python3 scripts/my_script.py
\`\`\`
```

### Step 3: Implement Script

```python
#!/usr/bin/env python
import json
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from mcp_osquery_server import osquery_tools

def main():
    result = {
        "status": "success",
        "data": {}  # Your data here
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Step 4: Test

```bash
# Activate venv first
source venv/bin/activate
python .claude/skills/my-skill-name/scripts/my_script.py
```

### Step 5: Use with Claude

Ask Claude questions that match your skill description.

## Best Practices

### Skill Design
- ✅ Focus on one clear task per skill
- ✅ Use descriptive names
- ✅ Include multiple trigger phrase examples
- ✅ Return structured JSON

### Script Implementation
- ✅ Handle errors gracefully
- ✅ Return concise output
- ✅ Use clear variable names
- ✅ Add helpful comments

### Descriptions
- ✅ Be specific about when to use the skill
- ✅ List trigger phrases users might ask
- ✅ Document expected output format
- ✅ Include usage examples

## Troubleshooting

### Skill Not Found
- Check `.claude/skills/` directory structure
- Verify `SKILL.md` has proper frontmatter
- Ensure description matches use cases

### Execution Errors
- Test script independently
- Check Python path includes parent project
- Verify imports work from skill directory

### Unexpected Output
- Validate JSON format
- Check for interfering print statements
- Test error handling

## Why Use Skills vs. MCP Server Alone?

| Feature | MCP Server | Claude Skills | Benefit |
|---------|-----------|---------------|---------|
| **Token Usage** | High (schema exploration) | Low (pre-packaged) | 65% reduction |
| **Speed** | Slower (query construction) | Faster (direct execution) | Immediate results |
| **Accuracy** | May vary | Consistent | Tested scripts |
| **Reusability** | Manual | Automatic | Claude remembers |
| **Discoverability** | Limited | Natural language | Easy to use |

## Example Workflow

### Without Skills (MCP Server Only)
1. User: "Show me system info"
2. Claude explores schema (~2,000 tokens)
3. Claude constructs query (~500 tokens)
4. Executes and parses result (~1,000 tokens)
5. **Total: ~3,500 tokens**

### With Skills
1. User: "Show me system info"
2. Claude detects `system-health` skill
3. Executes pre-packaged script (~800 tokens)
4. Parses structured JSON (~400 tokens)
5. **Total: ~1,200 tokens (65% reduction)**

## Further Resources

- Full documentation: [.claude/skills/README.md](.claude/skills/README.md)
- MCP Server docs: [mcp_osquery_server/README.md](mcp_osquery_server/README.md)
- Blog post: https://www.cdata.com/blog/mcp-skills-part-2-building-skills
