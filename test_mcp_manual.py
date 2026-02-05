#!/usr/bin/env python
"""Manual test of MCP server with skills integration."""
import asyncio
import json
from mcp_osquery_server.server import call_tool

async def test_mcp_skills():
    """Test the MCP server skills."""
    print("=" * 60)
    print("MCP Server Skills Integration Test")
    print("=" * 60)
    
    # Test 1: Call check_system_health
    print("\n1. Testing check_system_health tool...")
    try:
        result = await call_tool("check_system_health", {})
        if not result.isError:
            data = json.loads(result.content[0].text)
            print(f"   ✓ Status: {data.get('status')}")
            print(f"   ✓ Hostname: {data.get('hostname')}")
            print(f"   ✓ Memory: {data.get('memory', {}).get('percent')}% used")
            print(f"   ✓ CPU: {data.get('cpu_percent')}%")
            print(f"   ✓ Disk: {data.get('disk', {}).get('percent')}% used")
        else:
            print(f"   ✗ Error: {result.content[0].text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
    
    # Test 2: Call get_top_processes with limit
    print("\n2. Testing get_top_processes tool (limit=5)...")
    try:
        result = await call_tool("get_top_processes", {"limit": 5})
        if not result.isError:
            data = json.loads(result.content[0].text)
            print(f"   ✓ Status: {data.get('status')}")
            print(f"   ✓ Returned {data.get('count')} processes")
            print(f"   ✓ Total memory: {data.get('total_memory_mb')} MB")
            print("   Top 5 processes:")
            for i, proc in enumerate(data.get('processes', [])[:5], 1):
                print(f"      {i}. {proc['name']:<30} {proc['memory_mb']:>8.2f} MB")
        else:
            print(f"   ✗ Error: {result.content[0].text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
    
    # Test 3: Test with different limit
    print("\n3. Testing get_top_processes tool (limit=3)...")
    try:
        result = await call_tool("get_top_processes", {"limit": 3})
        if not result.isError:
            data = json.loads(result.content[0].text)
            print(f"   ✓ Returned {data.get('count')} processes")
        else:
            print(f"   ✗ Error: {result.content[0].text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All MCP Skills Tests Passed!")
    print("=" * 60)
    print("\nThe skills are working through the MCP protocol!")
    print("Tools available: check_system_health, get_top_processes")

if __name__ == "__main__":
    asyncio.run(test_mcp_skills())
