# MCP OSQuery Server

A Model Context Protocol (MCP) server that provides system information querying capabilities through the osquery library.

## Overview

This MCP server exposes osquery functionality, allowing AI models and applications to query system information such as:
- System information (OS, hostname, CPU)
- Running processes
- Users and groups
- Network interfaces and connections
- Open files
- Disk usage
- Installed packages
- Running services
- Custom osquery SQL queries

## Prerequisites

### Required
- Python 3.8+
- osquery installed on your system

### macOS Installation
```bash
# Install osquery via Homebrew
brew install osquery
```

### Linux Installation
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install osquery

# CentOS/RHEL
sudo yum install osquery
```

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Standard Execution
```bash
source venv/bin/activate
python -m mcp_osquery_server.server
```

### With Logging
```bash
source venv/bin/activate
python -m mcp_osquery_server.server 2>&1
```

## Available Tools

### system_info
Get general system information (OS, hostname, CPU count, memory, etc.)

**Usage:**
```json
{
  "name": "system_info",
  "arguments": {}
}
```

### processes
Get top memory-consuming processes

**Arguments:**
- `limit` (integer, optional): Number of processes to return (default: 10)

**Usage:**
```json
{
  "name": "processes",
  "arguments": {"limit": 5}
}
```

### users
Get system users

**Usage:**
```json
{
  "name": "users",
  "arguments": {}
}
```

### network_interfaces
Get network interfaces and their details

**Usage:**
```json
{
  "name": "network_interfaces",
  "arguments": {}
}
```

### network_connections
Get active network connections

**Arguments:**
- `limit` (integer, optional): Number of connections to return (default: 20)

**Usage:**
```json
{
  "name": "network_connections",
  "arguments": {"limit": 10}
}
```

### open_files
Get open files by processes

**Arguments:**
- `pid` (integer, optional): Process ID to filter by

**Usage:**
```json
{
  "name": "open_files",
  "arguments": {"pid": 1234}
}
```

### disk_usage
Get disk usage and mount information

**Usage:**
```json
{
  "name": "disk_usage",
  "arguments": {}
}
```

### installed_packages
Get installed packages/applications

**Usage:**
```json
{
  "name": "installed_packages",
  "arguments": {}
}
```

### running_services
Get running services (launchd on macOS)

**Usage:**
```json
{
  "name": "running_services",
  "arguments": {}
}
```

### custom_query
Execute a custom osquery SQL query

**Arguments:**
- `sql` (string, required): osquery SQL query

**Usage:**
```json
{
  "name": "custom_query",
  "arguments": {"sql": "SELECT * FROM system_info;"}
}
```

## Project Structure

```
mcp_osquery_server/
├── __init__.py           # Package initialization
├── server.py             # Main MCP server implementation
├── osquery_tools.py      # OSQuery query functions
└── README.md             # This file
```

## How It Works

1. **osquery_tools.py**: Contains the OSQueryClient class that:
   - Finds the osqueryi executable on the system
   - Executes osquery SQL queries via subprocess
   - Handles JSON output parsing
   - Manages error handling and timeouts

2. **server.py**: Implements the MCP protocol with:
   - Tool registration through `@server.list_tools()`
   - Tool execution through `@server.call_tool()`
   - Error handling and response formatting
   - Async/await support

## Integration with Claude

To use this server with Claude via MCP, configure it in your MCP settings:

```json
{
  "mcpServers": {
    "osquery": {
      "command": "python",
      "args": ["-m", "mcp_osquery_server.server"],
      "cwd": "/path/to/mcp_osquery_server"
    }
  }
}
```

## Troubleshooting

### osqueryi not found
If you get "osqueryi not found" errors:
1. Ensure osquery is installed: `which osqueryi`
2. If not installed, follow the installation instructions above

### Permission denied errors
Some osquery tables require elevated privileges. Run the server with `sudo` if needed:
```bash
sudo -u root python -m mcp_osquery_server.server
```

### Query timeouts
If queries are timing out (default 30 seconds), check:
1. Your system performance
2. The complexity of your query
3. Consider limiting results with LIMIT clauses

## Example Queries

```sql
-- Get top 5 processes by memory
SELECT pid, name, user, memory_resident FROM processes ORDER BY memory_resident DESC LIMIT 5;

-- Get network connections
SELECT protocol, local_address, local_port, remote_address, remote_port FROM process_open_sockets;

-- Get system uptime
SELECT system_time, total_seconds FROM uptime;

-- Get kernel version
SELECT kernel_version FROM os_version;

-- Get all listening ports
SELECT pid, protocol, local_address, local_port FROM process_open_sockets WHERE state='LISTEN';
```

## Dependencies

- `mcp>=1.0.0` - Model Context Protocol library
- `python-dotenv>=1.0.0` - Environment variable management
- `pydantic>=2.0.0` - Data validation

## Notes

- This server communicates via JSON-RPC over stdio
- All query results are returned as JSON
- Queries have a 30-second timeout by default
- The server runs in async mode for efficient I/O handling
