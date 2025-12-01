#!/usr/bin/env python3
"""
langchain_agent.py

Demonstrates LangChain agent integration with osquery tools. The agent
uses LLM reasoning to decide which tools to call and how to chain them
together for complex system analysis tasks.

Usage:
    python examples/langchain_agent.py

This example shows how an LLM can intelligently select and orchestrate
multiple osquery tools to answer complex questions about system state.
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional

from langchain_core.tools import Tool

# Import our osquery tools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_osquery_server import osquery_tools


class OSQueryAgent:
    """LangChain agent that uses osquery tools for system analysis"""
    
    def __init__(self):
        self.tools = self._create_tools()
        
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from osquery functions"""
        
        def system_info_tool() -> str:
            """Get comprehensive system information including CPU, memory, and OS details"""
            try:
                result = osquery_tools.query_system_info()
                if result.get("success"):
                    data = result["data"][0] if result["data"] else {}
                    summary = f"""System Information:
- Hostname: {data.get('hostname', 'Unknown')}
- CPU: {data.get('cpu_brand', 'Unknown')} ({data.get('cpu_physical_cores', '?')} cores)
- Memory: {int(data.get('physical_memory', '0')) // (1024**3)} GB
- Architecture: {data.get('cpu_type', 'Unknown')}"""
                    return summary
                else:
                    return f"Error retrieving system info: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def top_processes_tool(limit: str = "10") -> str:
            """Get top processes by memory usage - useful for performance analysis"""
            try:
                limit_int = int(limit) if limit.isdigit() else 10
                result = osquery_tools.query_processes(limit_int)
                if result.get("success"):
                    processes = result["data"]
                    if processes:
                        summary = f"Top {len(processes)} processes by memory usage:\n"
                        for proc in processes:
                            memory_mb = int(proc.get("resident_size", "0")) // (1024 * 1024)
                            summary += f"- {proc.get('name', 'Unknown')} (PID: {proc.get('pid', '?')}): {memory_mb} MB\n"
                        return summary
                    else:
                        return "No processes found"
                else:
                    return f"Error retrieving processes: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def list_users_tool() -> str:
            """List system users - useful for security analysis"""
            try:
                result = osquery_tools.query_users()
                if result.get("success"):
                    users = result["data"]
                    active_users = [u for u in users if u.get("shell") and "nologin" not in u.get("shell", "")]
                    
                    summary = f"System Users Summary:\n"
                    summary += f"Total users: {len(users)}\n"
                    summary += f"Interactive users: {len(active_users)}\n\n"
                    
                    if active_users:
                        summary += "Interactive users:\n"
                        for user in active_users[:10]:  # Limit to first 10
                            summary += f"- {user.get('username', 'Unknown')} (UID: {user.get('uid', '?')}, Home: {user.get('directory', '?')})\n"
                    
                    return summary
                else:
                    return f"Error retrieving users: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def network_info_tool() -> str:
            """Get network interface information - useful for connectivity analysis"""
            try:
                result = osquery_tools.query_network_interfaces()
                if result.get("success"):
                    interfaces = result["data"]
                    summary = f"Network Interfaces ({len(interfaces)} found):\n"
                    for iface in interfaces:
                        summary += f"- {iface.get('interface', 'Unknown')}: MAC {iface.get('mac', 'Unknown')}, MTU {iface.get('mtu', '?')}\n"
                    return summary
                else:
                    return f"Error retrieving network info: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def network_connections_tool(limit: str = "20") -> str:
            """Get active network connections - useful for security analysis"""
            try:
                limit_int = int(limit) if limit.isdigit() else 20
                result = osquery_tools.query_network_connections(limit_int)
                if result.get("success"):
                    connections = result["data"]
                    if connections:
                        summary = f"Active Network Connections ({len(connections)} found):\n"
                        for conn in connections[:limit_int]:
                            local = conn.get("local_address", "Unknown")
                            remote = conn.get("remote_address", "Unknown")
                            state = conn.get("state", "Unknown")
                            pid = conn.get("pid", "?")
                            summary += f"- PID {pid}: {local} -> {remote} ({state})\n"
                    else:
                        summary = "No active network connections found"
                    return summary
                else:
                    return f"Error retrieving connections: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        def custom_query_tool(sql: str) -> str:
            """Execute custom osquery SQL for advanced analysis"""
            try:
                result = osquery_tools.custom_query(sql)
                if result.get("success"):
                    data = result["data"]
                    if data:
                        # Format results as a simple table
                        if isinstance(data, list) and len(data) > 0:
                            keys = list(data[0].keys())
                            summary = f"Query Results ({len(data)} rows):\n"
                            # Show first few results
                            for row in data[:5]:
                                row_str = ", ".join([f"{k}: {row.get(k, 'N/A')}" for k in keys[:3]])  # Limit columns
                                summary += f"- {row_str}\n"
                            if len(data) > 5:
                                summary += f"... and {len(data) - 5} more rows\n"
                        else:
                            summary = "Query returned no results"
                    else:
                        summary = "Query executed successfully but returned no data"
                    return summary
                else:
                    return f"Query error: {result.get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error executing query: {str(e)}"
        
        return [
            Tool(
                name="system_info",
                description="Get basic system information including CPU, memory, hostname",
                func=system_info_tool
            ),
            Tool(
                name="top_processes",
                description="Get top processes by memory usage. Argument: limit (number of processes, default 10)",
                func=top_processes_tool
            ),
            Tool(
                name="list_users", 
                description="List system users and identify interactive accounts",
                func=list_users_tool
            ),
            Tool(
                name="network_info",
                description="Get network interface information",
                func=network_info_tool
            ),
            Tool(
                name="network_connections",
                description="Get active network connections. Argument: limit (number of connections, default 20)",
                func=network_connections_tool
            ),
            Tool(
                name="custom_query",
                description="Execute custom osquery SQL. Argument: sql (the SQL query to execute)",
                func=custom_query_tool
            )
        ]
    
    async def analyze(self, query: str) -> str:
        """Analyze a query and execute appropriate tools"""
        print(f"🔍 Analyzing: {query}")
        print("-" * 40)
        
        # Simple rule-based tool selection (in production, you'd use the LLM)
        query_lower = query.lower()
        results = []
        
        if "security" in query_lower or "suspicious" in query_lower:
            # Security analysis workflow
            print("🛡️  Running security analysis...")
            results.append("🛡️ Security Analysis Results:")
            
            # Check for unusual processes
            proc_result = self.tools[1].func("15")  # top_processes
            results.append(f"\n**Process Analysis:**\n{proc_result}")
            
            # Check network connections
            net_result = self.tools[4].func("25")  # network_connections  
            results.append(f"\n**Network Analysis:**\n{net_result}")
            
            # Check users
            user_result = self.tools[2].func()  # list_users
            results.append(f"\n**User Analysis:**\n{user_result}")
            
        elif "performance" in query_lower or "slow" in query_lower:
            # Performance analysis workflow
            print("⚡ Running performance analysis...")
            results.append("⚡ Performance Analysis Results:")
            
            # System info
            sys_result = self.tools[0].func()  # system_info
            results.append(f"\n**System Resources:**\n{sys_result}")
            
            # Top memory consumers
            proc_result = self.tools[1].func("10")  # top_processes
            results.append(f"\n**Memory Usage:**\n{proc_result}")
            
        elif "overview" in query_lower or "summary" in query_lower:
            # Comprehensive overview
            print("📊 Running comprehensive overview...")
            results.append("📊 System Overview:")
            
            # System info
            sys_result = self.tools[0].func()
            results.append(f"\n**System Info:**\n{sys_result}")
            
            # Top processes
            proc_result = self.tools[1].func("5")
            results.append(f"\n**Top Processes:**\n{proc_result}")
            
            # Network info
            net_result = self.tools[3].func()
            results.append(f"\n**Network:**\n{net_result}")
            
        elif "user" in query_lower or "account" in query_lower:
            # User analysis
            print("👤 Running user analysis...")
            results.append("👤 User Analysis Results:")
            
            user_result = self.tools[2].func()
            results.append(f"\n{user_result}")
            
        elif "network" in query_lower:
            # Network analysis
            print("🌐 Running network analysis...")
            results.append("🌐 Network Analysis Results:")
            
            # Network interfaces
            iface_result = self.tools[3].func()
            results.append(f"\n**Interfaces:**\n{iface_result}")
            
            # Active connections
            conn_result = self.tools[4].func("15")
            results.append(f"\n**Connections:**\n{conn_result}")
            
        else:
            # Default: basic system info
            print("ℹ️  Running basic system check...")
            results.append("ℹ️ System Information:")
            
            sys_result = self.tools[0].func()
            results.append(f"\n{sys_result}")
        
        return "\n".join(results)
    
    def run_interactive(self):
        """Run the agent in interactive mode"""
        print("🤖 OSQuery LangChain Agent")
        print("Ask me to analyze your system! Examples:")
        print("- 'Check for security issues'") 
        print("- 'Why is my system slow?'")
        print("- 'Give me a system overview'")
        print("- 'Show me network activity'")
        print("Type 'quit' to exit.")
        print("=" * 50)
        
        while True:
            try:
                query = input("\n💬 What would you like to analyze? ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                    
                if not query:
                    continue
                
                # Run analysis
                result = asyncio.run(self.analyze(query))
                print(f"\n{result}\n")
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


async def run_examples():
    """Run sample analysis scenarios"""
    agent = OSQueryAgent()
    
    scenarios = [
        "Give me a system overview",
        "Check for any security concerns", 
        "Why might my system be running slowly?",
        "Show me network activity"
    ]
    
    print("🚀 OSQuery LangChain Agent Examples")
    print("=" * 50)
    
    for scenario in scenarios:
        print(f"\n🎯 Scenario: {scenario}")
        print("=" * 50)
        
        result = await agent.analyze(scenario)
        print(f"\n{result}\n")
        
        print("=" * 50)
        await asyncio.sleep(1)  # Brief pause between scenarios


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OSQuery LangChain Agent")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        agent = OSQueryAgent()
        agent.run_interactive()
    else:
        asyncio.run(run_examples())