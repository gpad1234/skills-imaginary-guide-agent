#!/usr/bin/env python3
"""
Test script for the MCP OSQuery Server.
Tests the osquery tools directly without starting the MCP server.
"""

import sys
import json
from mcp_osquery_server import osquery_tools

def print_result(name: str, result: dict):
    """Pretty print a result."""
    print(f"\n{'='*60}")
    print(f"Tool: {name}")
    print(f"{'='*60}")
    
    if result.get("success"):
        data = result.get("data", [])
        print(f"✓ Success ({len(data)} items)" if isinstance(data, list) else "✓ Success")
        if data:
            print("\nData:")
            print(json.dumps(data[:3] if isinstance(data, list) and len(data) > 3 else data, indent=2))
            if isinstance(data, list) and len(data) > 3:
                print(f"\n... and {len(data) - 3} more items")
    else:
        print(f"✗ Error: {result.get('error')}")

def main():
    """Run tests."""
    print("Testing MCP OSQuery Server Tools")
    print("=" * 60)
    
    # Check if osqueryi is available
    try:
        client = osquery_tools.get_client()
        result = osquery_tools.query_system_info()
        
        if result.get("success"):
            print("✓ osqueryi is available")
        else:
            print("✗ osqueryi not found or not working")
            print(f"  Error: {result.get('error')}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error initializing osqueryi: {e}")
        sys.exit(1)
    
    # Test each tool
    tests = [
        ("system_info", lambda: osquery_tools.query_system_info()),
        ("users", lambda: osquery_tools.query_users()),
        ("network_interfaces", lambda: osquery_tools.query_network_interfaces()),
        ("processes (limit=5)", lambda: osquery_tools.query_processes(limit=5)),
        ("disk_usage", lambda: osquery_tools.query_disk_usage()),
        ("open_files", lambda: osquery_tools.query_open_files()),
    ]
    
    for name, func in tests:
        try:
            result = func()
            print_result(name, result)
        except Exception as e:
            print(f"\n✗ Exception in {name}: {e}")
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)

if __name__ == "__main__":
    main()
