#!/usr/bin/env python
"""Test MCP server with integrated skills."""
import subprocess
import sys
import os

# Change to project directory
os.chdir('/Users/gp/creative-work/imaginary-guide-agent')

print("Testing MCP Server with Skills Integration\n")
print("=" * 50)

# Test 1: Check system health skill directly
print("\n1. Testing system-health skill directly:")
result = subprocess.run(
    ["python", ".claude/skills/system-health/scripts/check_system_health.py"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("✓ system-health skill works")
else:
    print(f"✗ Error: {result.stderr}")

# Test 2: Check top processes skill directly
print("\n2. Testing top-processes skill directly:")
result = subprocess.run(
    ["python", ".claude/skills/top-processes/scripts/get_top_processes.py", "--limit", "3"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("✓ top-processes skill works")
else:
    print(f"✗ Error: {result.stderr}")

# Test 3: Check MCP server can import
print("\n3. Testing MCP server integration:")
result = subprocess.run(
    ["python", "-c", "from mcp_osquery_server.server import server; print('✓ MCP server loads successfully')"],
    capture_output=True,
    text=True
)
print(result.stdout if result.returncode == 0 else f"✗ Error: {result.stderr}")

print("\n" + "=" * 50)
print("\nTo run the MCP server with skills:")
print("  python -m mcp_osquery_server.server")
print("\nAvailable MCP tools now include:")
print("  - check_system_health")
print("  - get_top_processes (with limit parameter)")
print("  - All original osquery tools")
