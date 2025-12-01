# MCP OSQuery Server - Complete Setup Guide

## What is This?

This project contains a **Model Context Protocol (MCP) Server** that integrates osquery functionality. It allows AI models and applications to:
- Query system information (OS, processes, users, network, etc.)
- Monitor system resources
- Analyze network connections
- Check running services
- Execute custom osquery SQL queries

## Project Structure

```
agentic_python_getting_started/
├── mcp_osquery_server/              # Main MCP server package
│   ├── __init__.py                  # Package initialization
│   ├── server.py                    # MCP server implementation
│   ├── osquery_tools.py             # OSQuery wrapper functions
│   └── README.md                    # Detailed server documentation
├── main.py                          # Claude API example (Haiku)
├── demo_osquery_server.py           # Demo mode showing capabilities
├── test_osquery_server.py           # Test suite for tools
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template (safe)
├── .env                            # Your API keys (git ignored)
├── .gitignore                      # Git ignore rules (protects secrets)
├── .vscode/                        # VS Code configuration
│   └── tasks.json                  # Predefined tasks
├── venv/                           # Virtual environment (git ignored)
├── README.md                       # Main project README
├── SETUP_GUIDE.md                 # This setup guide
└── PROJECT_SUMMARY.md             # Project documentation
```

## Quick Start

### 1. Virtual Environment Setup ✅
The project includes a pre-configured virtual environment. Activate it with:
```bash
source venv/bin/activate
```

### 2. Environment Variables Setup 🔑
**IMPORTANT**: Set up your API keys before running the project:

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Anthropic API key:
```bash
# Edit the .env file
ANTHROPIC_API_KEY=your_actual_api_key_here
```

**Security Note**: The `.env` file is already excluded from git via `.gitignore` to protect your secrets.

### 3. Dependencies ✅
Dependencies are already installed:
- `mcp>=1.21.0` - Model Context Protocol
- `anthropic>=0.72.0` - Anthropic API client
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variables

### 4. Install OSQuery (Optional for Development)

**macOS:**
```bash
brew install osquery
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install osquery
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install osquery
```

### 5. Run the Project

**Using VS Code Task (Recommended):**
- Use Ctrl+Shift+P → "Tasks: Run Task" → "Run Anthropic Project"
- Or use the terminal: 

**Manual Commands:**
```bash
# Activate environment and run main script
source venv/bin/activate
python main.py
```

**Start MCP Server:**
```bash
source venv/bin/activate
python -m mcp_osquery_server.server
```

**Demo Mode (No osquery Required):**
```bash
source venv/bin/activate
python demo_osquery_server.py
```

## 🔒 Security & Configuration

### Environment Variables
The project uses environment variables to securely store API keys:

- **`.env`** - Contains your actual API keys (NEVER commit this)
- **`.env.example`** - Template showing required variables (safe to commit)

### Git Security
The `.gitignore` file protects against accidentally committing:
- Environment files (`.env`, `.env.*`)
- API keys and credentials (`*.key`, `*.pem`, `secrets.json`)
- Virtual environments (`venv/`, `.venv/`)
- OS-specific files (`.DS_Store`, `Thumbs.db`)
- IDE settings with potential secrets

### Best Practices
1. ✅ **Never commit `.env` files**
2. ✅ **Use `.env.example` for documentation**
3. ✅ **Rotate API keys regularly**
4. ✅ **Use different keys for development/production**

## Available Tools in MCP Server

The MCP server provides these tools:

| Tool | Purpose | Parameters |
|------|---------|-----------|
| `system_info` | Get OS, hostname, CPU, memory | None |
| `processes` | Get running processes | `limit` (optional, default 10) |
| `users` | Get system users | None |
| `network_interfaces` | Get network adapters | None |
| `network_connections` | Get active connections | `limit` (optional, default 20) |
| `open_files` | Get open files | `pid` (optional) |
| `disk_usage` | Get disk/mount info | None |
| `installed_packages` | Get installed software | None |
| `running_services` | Get running services | None |
| `custom_query` | Execute custom SQL | `sql` (required) |

## Integration Examples

### With Claude via MCP

Configure in your MCP settings (e.g., `.cursor/mcp-settings.json` or Claude configuration):

```json
{
  "mcpServers": {
    "osquery": {
      "command": "python",
      "args": ["-m", "mcp_osquery_server.server"],
      "cwd": "/home/girish/python_work/agentic_python_getting_started"
    }
  }
}
```

**Note**: Update the `cwd` path to match your actual project location.

### Example Claude Request

Once configured, Claude can use it like:
- "What are the top processes by memory usage?"
- "Show me active network connections"
- "What is the system uptime?"
- "List all users on the system"

### Custom osquery Queries

Send custom SQL queries:
```python
# In Claude or MCP client
{
  "tool": "custom_query",
  "sql": "SELECT pid, name, user FROM processes WHERE name LIKE '%python%';"
}
```

## File Descriptions

### `mcp_osquery_server/server.py`
- Main MCP server implementation
- Registers available tools
- Handles tool execution
- Returns formatted results

### `mcp_osquery_server/osquery_tools.py`
- `OSQueryClient` class - wraps osqueryi executable
- Helper functions for common queries
- Error handling and timeout management
- JSON output parsing

### `main.py`
- Example Anthropic Claude API integration
- Uses Claude 3 Haiku model
- Shows how to call Claude from Python

### `demo_osquery_server.py`
- Demonstrates server structure
- Shows example data formats
- Works without osquery installed
- Useful for testing MCP integration

### `test_osquery_server.py`
- Unit tests for osquery tools
- Tests each available function
- Requires osquery to be installed

## Troubleshooting

### "Missing API Key" Error

**Problem**: `Error: Make sure you have set your ANTHROPIC_API_KEY in the .env file`

**Solution**: 
1. Copy the template: `cp .env.example .env`
2. Edit `.env` and add your actual API key
3. Restart the application

### "osqueryi not found" Error

**Solution:** Install osquery
```bash
# macOS
brew install osquery

# Linux
sudo apt-get install osquery
```

### "Module not found" Error

**Solution:** Activate the virtual environment
```bash
source venv/bin/activate
```

### Permission Denied Errors

Some osquery tables require elevated privileges. Run with sudo:
```bash
sudo python -m mcp_osquery_server.server
```

### Server Not Responding

1. Check osquery is running: `osqueryi --version`
2. Test a simple query: `osqueryi "SELECT * FROM system_info;"`
3. Check for error logs in terminal output

### MCP Connection Issues

1. Verify the server path is correct in MCP configuration
2. Ensure virtual environment is activated
3. Check that all dependencies are installed
4. Verify the `cwd` path matches your project location

### Git Security Issues

**Problem**: Accidentally committed `.env` file

**Solution**:
```bash
# Remove from git and add to gitignore
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Remove .env from tracking and update gitignore"
```

## Advanced Usage

### Custom Queries via MCP

You can execute any osquery SQL:

```json
{
  "tool": "custom_query",
  "arguments": {
    "sql": "SELECT COUNT(*) as listening_ports FROM process_open_sockets WHERE state='LISTEN';"
  }
}
```

### Common osquery Tables

- `system_info` - System information
- `processes` - Running processes
- `users` - User accounts
- `groups` - User groups
- `interface_details` - Network interfaces
- `process_open_sockets` - Network connections
- `process_open_files` - Open files
- `mounts` - Disk mounts
- `os_version` - OS version info
- `uptime` - System uptime

See [osquery documentation](https://osquery.io/schema/) for complete table reference.

## Development

### Adding New Tools

To add a new tool to the MCP server:

1. **Add query function in `osquery_tools.py`:**
```python
def query_my_tool() -> Dict[str, Any]:
    """Get my data."""
    client = get_client()
    return client.query("SELECT * FROM my_table;")
```

2. **Register tool in `server.py`:**
```python
Tool(
    name="my_tool",
    description="Description of my tool",
    inputSchema={"type": "object", "properties": {}, "required": []}
)
```

3. **Handle in `call_tool()`:**
```python
elif name == "my_tool":
    result = osquery_tools.query_my_tool()
```

## Dependencies Breakdown

| Package | Purpose |
|---------|---------|
| `mcp` | Model Context Protocol library |
| `pydantic` | Data validation and settings |
| `python-dotenv` | Load .env files |
| `httpx` | HTTP client (MCP dependency) |
| `uvicorn` | ASGI server (MCP dependency) |
| `starlette` | Web framework (MCP dependency) |

## Notes

- The server communicates via JSON-RPC over stdio
- All queries have a 30-second timeout
- Results are automatically formatted as JSON
- The server supports async/await operations
- macOS specific queries (like launchd) won't work on Linux

## Next Steps

1. **Install osquery** on your system
2. **Run the demo** to see available tools
3. **Test the server** with `python -m mcp_osquery_server.server`
4. **Integrate with Claude** using MCP configuration
5. **Build custom queries** for your needs

## Resources

- [osquery Documentation](https://osquery.io/)
- [osquery Schema Reference](https://osquery.io/schema/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)

## Security Checklist

Before deploying or sharing this project:

- [ ] ✅ `.env` file is git ignored
- [ ] ✅ API keys are in `.env` (not hardcoded)
- [ ] ✅ Virtual environment is git ignored
- [ ] ✅ No secrets in source code
- [ ] ✅ Different API keys for dev/prod
- [ ] ✅ Regular API key rotation
- [ ] ⚠️  Review all files before committing

**Remember**: Never commit API keys, passwords, or other secrets to version control!

---

**Project Status**: ✅ Ready to Run  
**Last Updated**: November 9, 2025  
**Python Version**: 3.12.3
