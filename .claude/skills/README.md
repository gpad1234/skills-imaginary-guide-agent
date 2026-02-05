# Claude Skills for OSQuery MCP Server

This directory contains Claude Skills that make the OSQuery MCP server's capabilities easily reusable and discoverable by Claude in Claude Code.

## What are Claude Skills?

Claude Skills are reusable, pre-packaged actions that Claude can discover and run automatically. Each skill:
- Has a clear purpose defined in `SKILL.md`
- Contains executable scripts that perform specific tasks
- Returns structured JSON output for consistent parsing
- Can be triggered by natural language queries

## Available Skills

### 1. system-health
**Purpose**: Get comprehensive system health metrics

**Trigger phrases**:
- "Check system health"
- "Show me system status"
- "What's the current resource usage?"
- "How is the system performing?"

**Output**: JSON with system info, memory usage, top processes, network status

### 2. top-processes
**Purpose**: Get top resource-consuming processes

**Trigger phrases**:
- "Which processes are using the most memory?"
- "Show me top processes"
- "What's consuming resources?"
- "List memory-heavy applications"

**Output**: JSON array of processes sorted by memory usage

## How Claude Uses These Skills

When you ask a question in Claude Code, Claude:

1. **Detects intent** - Matches your question to skill descriptions
2. **Selects the skill** - Chooses the most relevant skill
3. **Executes the script** - Runs the skill's Python script
4. **Interprets results** - Parses the JSON and responds in natural language

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md              # Metadata and usage instructions
├── scripts/              # Executable scripts
│   └── main_script.py    # Primary skill logic
└── requirements.txt      # Dependencies (if any)
```

### SKILL.md Format

```markdown
---
name: skill-name
description: Brief description for Claude to understand when to use this skill
allowed-tools: Bash
---

# Skill Title

Usage instructions and context...

## Run using:
```bash
python3 scripts/script_name.py
```
```

## Creating New Skills

To create a new skill:

1. **Identify a common query pattern** from your MCP server usage
2. **Create the skill directory**:
   ```bash
   mkdir -p .claude/skills/your-skill-name/scripts
   ```

3. **Write the SKILL.md** with:
   - Clear description
   - Trigger phrases
   - Usage examples
   - Expected output format

4. **Implement the script** that:
   - Imports from `mcp_osquery_server`
   - Returns clean JSON output
   - Handles errors gracefully
   - Exits with proper status codes

5. **Test manually**:
   ```bash
   source venv/bin/activate
   python .claude/skills/your-skill-name/scripts/your_script.py
   ```

6. **Test with Claude** by asking related questions in Claude Code

## Best Practices

### For Skill Design
- ✅ Make skills focused on one clear task
- ✅ Use descriptive, searchable names
- ✅ Include multiple trigger phrase examples
- ✅ Return structured JSON for consistent parsing
- ✅ Handle errors and edge cases

### For Script Implementation
- ✅ Use clear variable names
- ✅ Add docstrings and comments
- ✅ Validate inputs
- ✅ Return meaningful error messages
- ✅ Keep output concise (minimize token usage)

### For Performance
- ✅ Cache results when appropriate
- ✅ Limit output size (use --limit parameters)
- ✅ Avoid unnecessary data transformation
- ✅ Use compact JSON formatting

## Example Usage in Claude Code

**User**: "What's using the most memory on my system?"

**Claude** (behind the scenes):
1. Detects `top-processes` skill matches this query
2. Runs: `python .claude/skills/top-processes/scripts/get_top_processes.py`
3. Receives JSON output
4. Responds with natural language summary

**Claude**: "Here are your top memory consumers:
1. Chrome (2.4 GB)
2. VSCode (1.8 GB)
3. Docker (1.2 GB)
..."

## Integration with MCP Server

These skills complement the MCP server by:
- **Reducing token usage**: Pre-packaged queries avoid schema exploration
- **Improving consistency**: Standardized output formats
- **Enabling automation**: Skills can be chained or scheduled
- **Enhancing discoverability**: Clear descriptions help Claude choose the right tool

## Token Efficiency

According to the blog post referenced in `skills.md`, combining Claude Skills with MCP can reduce token usage by up to **65%** because:
- Skills avoid re-parsing schemas
- No need to construct queries from scratch each time
- Focused, compact output formats
- Reusable logic prevents redundant tool calls

## Migration from MCP-Only to Skills

If you have existing MCP tool usage patterns:

1. **Identify frequent queries** from your usage logs
2. **Extract the query logic** into standalone scripts
3. **Package as skills** following the structure above
4. **Document trigger phrases** that match how users ask questions
5. **Test both approaches** to compare token usage and performance

## Troubleshooting

### Skill not being discovered
- Check that `SKILL.md` has proper frontmatter
- Ensure description clearly matches use cases
- Verify the `.claude/skills/` directory structure

### Script execution errors
- Activate venv first: `source venv/bin/activate`
- Test scripts independently before using with Claude
- Check that imports work from the skill directory
- Verify Python path includes parent project

### Unexpected output
- Ensure JSON is valid and well-formatted
- Check for print statements that might interfere
- Validate that error handling works correctly

## Further Reading

- [Original blog post on MCP Skills](https://www.cdata.com/blog/mcp-skills-part-2-building-skills)
- [MCP Server Documentation](../mcp_osquery_server/README.md)
- [Claude Code Documentation](https://docs.anthropic.com/)

## Contributing

When adding new skills:
1. Follow the existing structure
2. Test thoroughly
3. Document trigger phrases clearly
4. Update this README with the new skill
