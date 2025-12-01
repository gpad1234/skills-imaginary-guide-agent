#!/usr/bin/env python3
"""
Demo mode for the MCP OSQuery Server - for systems without osquery installed.
Shows the server structure and simulates data for testing.
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

def demo_mode():
    """Run in demo mode with mock data."""
    print("=" * 60)
    print("MCP OSQuery Server - DEMO MODE")
    print("=" * 60)
    print("\n⚠️  osqueryi is not installed on this system")
    print("In production, install osquery via: brew install osquery (macOS)")
    print("\nThis demo shows the server structure and expected output format.\n")
    
    # Mock system_info
    print("\n" + "="*60)
    print("Example: system_info")
    print("="*60)
    print(json.dumps({
        "hostname": "MacBook.local",
        "sysname": "Darwin",
        "release": "23.0.0",
        "version": "#1 SMP PREEMPT Mon Oct 2 12:00:00 UTC 2023",
        "machine": "arm64",
        "cpu_brand": "Apple M1",
        "cpu_logical_count": 8,
        "cpu_physical_count": 8,
        "physical_memory": 16000000000,
        "timezone": "UTC"
    }, indent=2))
    
    # Mock processes
    print("\n" + "="*60)
    print("Example: processes (top 5 by memory)")
    print("="*60)
    processes_example = [
        {"pid": 1234, "name": "Chrome", "user": "gp", "memory_resident": 1500000000},
        {"pid": 5678, "name": "Python", "user": "gp", "memory_resident": 800000000},
        {"pid": 9012, "name": "Safari", "user": "gp", "memory_resident": 600000000},
        {"pid": 3456, "name": "Slack", "user": "gp", "memory_resident": 400000000},
        {"pid": 7890, "name": "VS Code", "user": "gp", "memory_resident": 350000000},
    ]
    print(json.dumps(processes_example, indent=2))
    
    # Mock network_interfaces
    print("\n" + "="*60)
    print("Example: network_interfaces")
    print("="*60)
    interfaces_example = [
        {"interface": "en0", "mac": "a1:b2:c3:d4:e5:f6", "mtu": 1500, "metric": 0},
        {"interface": "en1", "mac": "a1:b2:c3:d4:e5:f7", "mtu": 1500, "metric": 100},
        {"interface": "lo0", "mac": "00:00:00:00:00:00", "mtu": 16384, "metric": 0},
    ]
    print(json.dumps(interfaces_example, indent=2))
    
    # Mock custom query
    print("\n" + "="*60)
    print("Example: custom_query")
    print("Query: SELECT * FROM system_info LIMIT 1")
    print("="*60)
    print(json.dumps([{
        "hostname": "MacBook.local",
        "sysname": "Darwin",
        "release": "23.0.0"
    }], indent=2))
    
    print("\n" + "="*60)
    print("MCP Server Features")
    print("="*60)
    print("""
✓ system_info - Get system information
✓ processes - Get running processes  
✓ users - Get system users
✓ network_interfaces - Get network interfaces
✓ network_connections - Get active connections
✓ open_files - Get open files
✓ disk_usage - Get disk usage
✓ installed_packages - Get installed programs
✓ running_services - Get running services
✓ custom_query - Execute custom osquery SQL

To use this server in production:
1. Install osquery: brew install osquery
2. Run the server: python -m mcp_osquery_server.server
3. Connect via MCP client or integrate with Claude
    """)

if __name__ == "__main__":
    demo_mode()
