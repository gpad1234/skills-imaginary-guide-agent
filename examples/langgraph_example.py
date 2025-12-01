#!/usr/bin/env python3
"""
langgraph_example.py

Concrete runtime example showing how to use LangGraph to orchestrate
osquery tools in a workflow graph. This demonstrates the alternate
design approach using graph-based orchestration.

Usage:
    python examples/langgraph_example.py

This example creates a graph with multiple osquery tool nodes and shows
how to execute them based on conditions and user input.
"""

import asyncio
import json
from typing import Dict, Any, List, TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.tools import Tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Import our osquery tools
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_osquery_server import osquery_tools


class OSQueryState(TypedDict):
    """State passed between graph nodes"""
    messages: List[BaseMessage]
    query_type: str
    results: Dict[str, Any]
    next_action: str


def create_osquery_tools() -> List[Tool]:
    """Create LangChain tools from our osquery functions"""
    
    def system_info_tool() -> str:
        """Get system information"""
        try:
            result = osquery_tools.query_system_info()
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def processes_tool(limit: int = 5) -> str:
        """Get running processes"""
        try:
            result = osquery_tools.query_processes(limit)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def users_tool() -> str:
        """Get system users"""
        try:
            result = osquery_tools.query_users()
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def network_tool() -> str:
        """Get network interfaces"""
        try:
            result = osquery_tools.query_network_interfaces()
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    return [
        Tool(
            name="system_info",
            description="Get basic system information",
            func=system_info_tool
        ),
        Tool(
            name="processes", 
            description="Get running processes",
            func=processes_tool
        ),
        Tool(
            name="users",
            description="Get system users", 
            func=users_tool
        ),
        Tool(
            name="network",
            description="Get network interfaces",
            func=network_tool
        )
    ]


def analyzer_node(state: OSQueryState) -> OSQueryState:
    """Analyze user request and determine query type"""
    messages = state["messages"]
    last_message = messages[-1].content.lower() if messages else ""
    
    if "process" in last_message or "running" in last_message:
        query_type = "processes"
    elif "user" in last_message or "account" in last_message:
        query_type = "users"
    elif "network" in last_message or "interface" in last_message:
        query_type = "network"
    elif "system" in last_message or "info" in last_message:
        query_type = "system_info"
    else:
        query_type = "system_info"  # default
    
    state["query_type"] = query_type
    state["next_action"] = "execute_query"
    
    return state


def executor_node(state: OSQueryState) -> OSQueryState:
    """Execute the determined query"""
    query_type = state["query_type"]
    
    try:
        if query_type == "system_info":
            result = osquery_tools.query_system_info()
        elif query_type == "processes":
            result = osquery_tools.query_processes(5)
        elif query_type == "users":
            result = osquery_tools.query_users()
        elif query_type == "network":
            result = osquery_tools.query_network_interfaces()
        else:
            result = {"error": f"Unknown query type: {query_type}"}
        
        state["results"] = result
        state["next_action"] = "format_response"
        
    except Exception as e:
        state["results"] = {"error": str(e)}
        state["next_action"] = "format_response"
    
    return state


def formatter_node(state: OSQueryState) -> OSQueryState:
    """Format the results for presentation"""
    results = state["results"]
    query_type = state["query_type"]
    
    if "error" in results:
        formatted = f"❌ Error executing {query_type} query: {results['error']}"
    else:
        formatted = f"✅ {query_type.replace('_', ' ').title()} Results:\n"
        formatted += json.dumps(results, indent=2)
    
    # Add formatted response as AI message
    state["messages"].append(AIMessage(content=formatted))
    state["next_action"] = "end"
    
    return state


def create_osquery_graph() -> StateGraph:
    """Create the LangGraph workflow for osquery operations"""
    
    workflow = StateGraph(OSQueryState)
    
    # Add nodes
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("executor", executor_node) 
    workflow.add_node("formatter", formatter_node)
    
    # Set entry point
    workflow.set_entry_point("analyzer")
    
    # Add edges
    workflow.add_edge("analyzer", "executor")
    workflow.add_edge("executor", "formatter") 
    workflow.add_edge("formatter", END)
    
    return workflow.compile()


async def run_example():
    """Run the LangGraph example with sample queries"""
    
    print("🚀 LangGraph OSQuery Example")
    print("=" * 50)
    
    # Create the graph
    app = create_osquery_graph()
    
    # Sample queries to test different paths
    test_queries = [
        "Show me system information",
        "What processes are running?", 
        "List system users",
        "Show network interfaces"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 30)
        
        # Initial state
        initial_state: OSQueryState = {
            "messages": [HumanMessage(content=query)],
            "query_type": "",
            "results": {},
            "next_action": ""
        }
        
        try:
            # Run the graph
            result = await app.ainvoke(initial_state)
            
            # Print the final response
            final_message = result["messages"][-1]
            print(final_message.content)
            
        except Exception as e:
            print(f"❌ Error running query: {e}")
        
        print("\n" + "="*50)


def run_interactive():
    """Run interactive mode where user can input queries"""
    
    print("🔍 Interactive OSQuery LangGraph")
    print("Type 'quit' to exit")
    print("=" * 40)
    
    # Create the graph
    app = create_osquery_graph()
    
    while True:
        try:
            query = input("\n💬 Enter your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
            
            # Initial state
            initial_state: OSQueryState = {
                "messages": [HumanMessage(content=query)],
                "query_type": "",
                "results": {},
                "next_action": ""
            }
            
            # Run synchronously for interactive use
            import asyncio
            result = asyncio.run(app.ainvoke(initial_state))
            
            # Print response
            final_message = result["messages"][-1]
            print("\n" + final_message.content)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGraph OSQuery Example")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    else:
        asyncio.run(run_example())