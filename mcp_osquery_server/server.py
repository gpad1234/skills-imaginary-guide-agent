#!/usr/bin/env python3
"""
MCP OSQuery Server - A Model Context Protocol server for system queries.

This server exposes osquery functionality through the MCP protocol,
allowing AI models to query system information.
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
import mcp.types as types

from mcp_osquery_server import osquery_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("osquery-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="system_info",
            description="Get general system information (OS, hostname, CPU count, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="processes",
            description="Get top memory-consuming processes",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of processes to return (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="users",
            description="Get system users",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="network_interfaces",
            description="Get network interfaces and their details",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="network_connections",
            description="Get active network connections",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of connections to return (default: 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="open_files",
            description="Get open files by processes",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "integer",
                        "description": "Process ID (optional, gets all if not specified)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="disk_usage",
            description="Get disk usage and mount information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="installed_packages",
            description="Get installed packages/applications",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="running_services",
            description="Get running services (launchd on macOS)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="custom_query",
            description="Execute a custom osquery SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "osquery SQL query to execute"
                    }
                },
                "required": ["sql"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Execute a tool and return results."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    try:
        result = None
        
        if name == "system_info":
            result = osquery_tools.query_system_info()
        
        elif name == "processes":
            limit = arguments.get("limit", 10)
            result = osquery_tools.query_processes(limit=limit)
        
        elif name == "users":
            result = osquery_tools.query_users()
        
        elif name == "network_interfaces":
            result = osquery_tools.query_network_interfaces()
        
        elif name == "network_connections":
            limit = arguments.get("limit", 20)
            result = osquery_tools.query_network_connections(limit=limit)
        
        elif name == "open_files":
            pid = arguments.get("pid")
            result = osquery_tools.query_open_files(pid=pid)
        
        elif name == "disk_usage":
            result = osquery_tools.query_disk_usage()
        
        elif name == "installed_packages":
            result = osquery_tools.query_installed_packages()
        
        elif name == "running_services":
            result = osquery_tools.query_running_services()
        
        elif name == "custom_query":
            sql = arguments.get("sql")
            if not sql:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: SQL query required")],
                    isError=True
                )
            result = osquery_tools.custom_query(sql)
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True
            )
        
        # Format the result
        if result and result.get("success"):
            import json
            data_str = json.dumps(result.get("data", []), indent=2)
            return CallToolResult(
                content=[TextContent(type="text", text=data_str)],
                isError=False
            )
        else:
            error_msg = result.get("error", "Unknown error") if result else "No result"
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {error_msg}")],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Exception: {str(e)}")],
            isError=True
        )


async def main():
    """Run the MCP server."""
    logger.info("Starting OSQuery MCP Server...")
    async with server:
        logger.info("OSQuery MCP Server running on stdio")


def create_server():
    """Create and return the MCP server instance for testing."""
    return server


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
