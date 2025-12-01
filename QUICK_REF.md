# Quick Reference - MCP OSQuery Server

## Activation
```bash
cd /Users/gp/python/algo/test_case3
source venv/bin/activate
```

## Commands

### See Demo (No osquery needed)
```bash
python demo_osquery_server.py
```

### Run Claude Example
```bash
python main.py
```

### Start MCP Server (requires osquery)
```bash
python -m mcp_osquery_server.server
```

### Run Tests
```bash
python test_osquery_server.py
```

## Install osquery

```bash
# macOS
brew install osquery

# Linux
sudo apt-get install osquery
```

## MCP Tools Available

```
system_info          → Get OS info, hostname, CPU, memory
processes            → Top processes by memory
users                → System users
network_interfaces   → Network adapters
network_connections  → Active connections
open_files           → Open files
disk_usage           → Disk/mount info
installed_packages   → Installed software
running_services     → Running services
custom_query         → Custom osquery SQL
```

## File Structure

```
.
├── main.py                           # Claude API example
├── demo_osquery_server.py            # Demo mode
├── test_osquery_server.py            # Tests
├── mcp_osquery_server/
│   ├── server.py                     # MCP server
│   ├── osquery_tools.py              # Query functions
│   └── README.md                     # Detailed docs
├── requirements.txt                  # Dependencies
├── README.md                         # Project README
├── SETUP_GUIDE.md                    # Setup guide
├── QUICK_REF.md                      # This file
└── venv/                             # Virtual environment
```

## Integration with Claude

Add to MCP config:
```json
{
  "mcpServers": {
    "osquery": {
      "command": "python",
      "args": ["-m", "mcp_osquery_server.server"],
      "cwd": "/Users/gp/python/algo/test_case3"
    }
  }
}
```

Then Claude can use: "Show me running processes" or "What is system uptime?"

## Troubleshooting

| Issue | Solution |
|-------|----------|
| osqueryi not found | Install: `brew install osquery` |
| Permission denied | Run with: `sudo python ...` |
| Can't activate venv | Try: `source ./venv/bin/activate` |
| Import errors | Run: `pip install -r requirements.txt` |

## Environment Variables

Edit `.env` file with:
```
ANTHROPIC_API_KEY=your_key_here
```

## Status

✓ Virtual environment created
✓ MCP server implemented  
✓ osquery tools configured
✓ Demo mode available
✓ Claude integration ready

---

For more details, see `SETUP_GUIDE.md`
