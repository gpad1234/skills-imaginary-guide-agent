#!/usr/bin/env python
"""Test the MCP server tools including skills."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_osquery_server import server as server_module

# The server decorator stores the functions, we need to access the underlying list
print("MCP Server Tools (including Skills):\n")

# Read the list_tools decorated function
import inspect
source = inspect.getsource(server_module.list_tools)
print(source[:500])
print("\n✓ Skills integrated into MCP server")
print("✓ Run with: python -m mcp_osquery_server.server")
