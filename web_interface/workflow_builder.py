#!/usr/bin/env python3
"""
workflow_builder.py

Interactive workflow builder that generates both Mermaid diagrams and 
executable LangGraph workflows from user-defined OSQuery tool sequences.

Usage:
    python web_interface/workflow_builder.py

Features:
- Visual workflow design using text commands
- Mermaid diagram generation
- LangGraph code export
- Interactive testing
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_osquery_server import osquery_tools


class NodeType(Enum):
    TOOL = "tool"
    CONDITION = "condition"
    START = "start"
    END = "end"


@dataclass
class WorkflowNode:
    id: str
    name: str
    type: NodeType
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    condition: Optional[str] = None
    description: str = ""


@dataclass
class WorkflowEdge:
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: str = ""


@dataclass
class Workflow:
    name: str
    description: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]


class WorkflowBuilder:
    """Interactive workflow builder for OSQuery tool orchestration"""
    
    def __init__(self):
        self.available_tools = {
            "system_info": {
                "description": "Get system information",
                "parameters": {}
            },
            "processes": {
                "description": "Get running processes", 
                "parameters": {"limit": "Number of processes (default: 5)"}
            },
            "users": {
                "description": "Get system users",
                "parameters": {}
            },
            "network_interfaces": {
                "description": "Get network interfaces",
                "parameters": {}
            },
            "network_connections": {
                "description": "Get network connections",
                "parameters": {"limit": "Number of connections (default: 10)"}
            },
            "custom_query": {
                "description": "Execute custom OSQuery SQL",
                "parameters": {"sql": "SQL query to execute"}
            }
        }
        
        self.workflow = Workflow(
            name="New Workflow",
            description="OSQuery workflow",
            nodes=[],
            edges=[]
        )
    
    def list_tools(self):
        """List available OSQuery tools"""
        print("\n🔧 Available OSQuery Tools:")
        print("=" * 40)
        for tool_name, info in self.available_tools.items():
            print(f"• {tool_name}: {info['description']}")
            if info['parameters']:
                params = ", ".join([f"{k} ({v})" for k, v in info['parameters'].items()])
                print(f"  Parameters: {params}")
        print()
    
    def add_node(self, node_id: str, node_name: str, node_type: NodeType, 
                 tool_name: str = None, parameters: Dict[str, Any] = None,
                 condition: str = None, description: str = ""):
        """Add a node to the workflow"""
        node = WorkflowNode(
            id=node_id,
            name=node_name,
            type=node_type,
            tool_name=tool_name,
            parameters=parameters or {},
            condition=condition,
            description=description
        )
        self.workflow.nodes.append(node)
        print(f"✅ Added node: {node_id} ({node_name})")
    
    def add_edge(self, from_node: str, to_node: str, condition: str = None, label: str = ""):
        """Add an edge between nodes"""
        edge = WorkflowEdge(
            from_node=from_node,
            to_node=to_node,
            condition=condition,
            label=label
        )
        self.workflow.edges.append(edge)
        print(f"✅ Added edge: {from_node} → {to_node}")
    
    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid diagram from workflow"""
        lines = ["graph TD"]
        
        # Add nodes
        for node in self.workflow.nodes:
            if node.type == NodeType.START:
                shape = f"{node.id}(({node.name}))"
            elif node.type == NodeType.END:
                shape = f"{node.id}(({node.name}))"
            elif node.type == NodeType.CONDITION:
                shape = f"{node.id}{{{node.name}}}"
            else:  # TOOL
                shape = f"{node.id}[{node.name}]"
            lines.append(f"    {shape}")
        
        # Add edges
        for edge in self.workflow.edges:
            if edge.label:
                lines.append(f"    {edge.from_node} -->|{edge.label}| {edge.to_node}")
            else:
                lines.append(f"    {edge.from_node} --> {edge.to_node}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef toolNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
            "    classDef conditionNode fill:#fff3e0,stroke:#e65100,stroke-width:2px", 
            "    classDef startEndNode fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px",
            ""
        ])
        
        # Apply styles
        for node in self.workflow.nodes:
            if node.type == NodeType.TOOL:
                lines.append(f"    class {node.id} toolNode")
            elif node.type == NodeType.CONDITION:
                lines.append(f"    class {node.id} conditionNode")
            else:
                lines.append(f"    class {node.id} startEndNode")
        
        return "\n".join(lines)
    
    def generate_langgraph_code(self) -> str:
        """Generate executable LangGraph code from workflow"""
        
        code_lines = [
            "#!/usr/bin/env python3",
            '"""',
            f"Generated LangGraph workflow: {self.workflow.name}",
            f"Description: {self.workflow.description}",
            f"Generated with {len(self.workflow.nodes)} nodes and {len(self.workflow.edges)} edges",
            '"""',
            "",
            "import asyncio",
            "import json",
            "from typing import Dict, Any, TypedDict",
            "from langgraph.graph import StateGraph, END",
            "",
            "# Import OSQuery tools",
            "import sys, os",
            "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
            "from mcp_osquery_server import osquery_tools",
            "",
            "",
            "class WorkflowState(TypedDict):",
            '    """State passed between workflow nodes"""',
            "    results: Dict[str, Any]",
            "    current_step: str",
            "    error: str",
            "",
            ""
        ]
        
        # Generate node functions
        for node in self.workflow.nodes:
            if node.type == NodeType.TOOL and node.tool_name:
                func_name = f"node_{node.id.replace('-', '_')}"
                code_lines.extend([
                    f"def {func_name}(state: WorkflowState) -> WorkflowState:",
                    f'    """Execute {node.name}"""',
                    "    try:",
                    f"        print(f'📋 Executing: {node.name}')",
                ])
                
                # Generate tool call based on tool name
                if node.tool_name == "system_info":
                    code_lines.append("        result = osquery_tools.query_system_info()")
                elif node.tool_name == "processes":
                    limit = node.parameters.get('limit', '5')
                    code_lines.append(f"        result = osquery_tools.query_processes({limit})")
                elif node.tool_name == "users":
                    code_lines.append("        result = osquery_tools.query_users()")
                elif node.tool_name == "network_interfaces":
                    code_lines.append("        result = osquery_tools.query_network_interfaces()")
                elif node.tool_name == "network_connections":
                    limit = node.parameters.get('limit', '10')
                    code_lines.append(f"        result = osquery_tools.query_network_connections({limit})")
                elif node.tool_name == "custom_query":
                    sql = node.parameters.get('sql', 'SELECT 1;')
                    code_lines.append(f"        result = osquery_tools.custom_query('{sql}')")
                else:
                    code_lines.append("        result = {'error': 'Unknown tool'}")
                
                code_lines.extend([
                    f"        state['results']['{node.id}'] = result",
                    f"        state['current_step'] = '{node.id}'",
                    "        return state",
                    "    except Exception as e:",
                    f"        state['error'] = f'Error in {node.name}: {{str(e)}}'",
                    "        return state",
                    "",
                    ""
                ])
            
            elif node.type == NodeType.CONDITION:
                func_name = f"node_{node.id.replace('-', '_')}"
                code_lines.extend([
                    f"def {func_name}(state: WorkflowState) -> WorkflowState:",
                    f'    """Condition: {node.name}"""',
                    f"    # TODO: Implement condition logic for: {node.condition or 'N/A'}",
                    f"    state['current_step'] = '{node.id}'",
                    "    return state",
                    "",
                    ""
                ])
        
        # Generate main graph creation function
        code_lines.extend([
            "def create_workflow() -> StateGraph:",
            f'    """Create the {self.workflow.name} workflow graph"""',
            "    ",
            "    workflow = StateGraph(WorkflowState)",
            "    ",
        ])
        
        # Add nodes to graph
        for node in self.workflow.nodes:
            if node.type in [NodeType.TOOL, NodeType.CONDITION]:
                func_name = f"node_{node.id.replace('-', '_')}"
                code_lines.append(f"    workflow.add_node('{node.id}', {func_name})")
        
        code_lines.append("    ")
        
        # Find start node or create default entry
        start_nodes = [n for n in self.workflow.nodes if n.type == NodeType.START]
        if start_nodes:
            first_tool_nodes = [n for n in self.workflow.nodes if n.type == NodeType.TOOL]
            if first_tool_nodes:
                code_lines.append(f"    workflow.set_entry_point('{first_tool_nodes[0].id}')")
        else:
            # Default to first tool node
            tool_nodes = [n for n in self.workflow.nodes if n.type == NodeType.TOOL]
            if tool_nodes:
                code_lines.append(f"    workflow.set_entry_point('{tool_nodes[0].id}')")
        
        code_lines.append("    ")
        
        # Add edges
        for edge in self.workflow.edges:
            code_lines.append(f"    workflow.add_edge('{edge.from_node}', '{edge.to_node}')")
        
        # Connect last nodes to END if no explicit end
        end_nodes = [n for n in self.workflow.nodes if n.type == NodeType.END]
        if not end_nodes:
            # Find nodes with no outgoing edges
            outgoing_nodes = {edge.from_node for edge in self.workflow.edges}
            all_nodes = {node.id for node in self.workflow.nodes if node.type != NodeType.START}
            terminal_nodes = all_nodes - outgoing_nodes
            for terminal_node in terminal_nodes:
                code_lines.append(f"    workflow.add_edge('{terminal_node}', END)")
        
        code_lines.extend([
            "    ",
            "    return workflow.compile()",
            "",
            "",
            "async def run_workflow():",
            f'    """Run the {self.workflow.name} workflow"""',
            "    print(f'🚀 Starting {self.workflow.name} workflow')",
            "    print('=' * 50)",
            "    ",
            "    # Create workflow",
            "    app = create_workflow()",
            "    ",
            "    # Initial state",
            "    initial_state: WorkflowState = {",
            "        'results': {},",
            "        'current_step': '',",
            "        'error': ''",
            "    }",
            "    ",
            "    try:",
            "        # Execute workflow",
            "        result = await app.ainvoke(initial_state)",
            "        ",
            "        # Print results",
            "        print('\\n📊 Workflow Results:')",
            "        print('=' * 30)",
            "        for step, data in result['results'].items():",
            "            print(f'\\n🔸 {step}:')",
            "            print(json.dumps(data, indent=2))",
            "        ",
            "        if result.get('error'):",
            "            print(f'\\n❌ Error: {result[\"error\"]}')",
            "        else:",
            "            print('\\n✅ Workflow completed successfully')",
            "            ",
            "    except Exception as e:",
            "        print(f'❌ Workflow failed: {str(e)}')",
            "",
            "",
            "if __name__ == '__main__':",
            "    asyncio.run(run_workflow())"
        ])
        
        return "\n".join(code_lines)
    
    def save_workflow(self, filepath: str):
        """Save workflow to JSON file"""
        workflow_dict = {
            "name": self.workflow.name,
            "description": self.workflow.description,
            "nodes": [asdict(node) for node in self.workflow.nodes],
            "edges": [asdict(edge) for edge in self.workflow.edges]
        }
        
        with open(filepath, 'w') as f:
            json.dump(workflow_dict, f, indent=2)
        print(f"💾 Workflow saved to {filepath}")
    
    def load_workflow(self, filepath: str):
        """Load workflow from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.workflow.name = data["name"]
        self.workflow.description = data["description"]
        self.workflow.nodes = [
            WorkflowNode(
                id=node["id"],
                name=node["name"],
                type=NodeType(node["type"]),
                tool_name=node.get("tool_name"),
                parameters=node.get("parameters"),
                condition=node.get("condition"),
                description=node.get("description", "")
            )
            for node in data["nodes"]
        ]
        self.workflow.edges = [
            WorkflowEdge(
                from_node=edge["from_node"],
                to_node=edge["to_node"],
                condition=edge.get("condition"),
                label=edge.get("label", "")
            )
            for edge in data["edges"]
        ]
        print(f"📂 Workflow loaded from {filepath}")
    
    def run_interactive_builder(self):
        """Run the interactive workflow builder"""
        print("🎨 Interactive OSQuery Workflow Builder")
        print("=" * 50)
        print("Commands:")
        print("  tools                 - List available tools")
        print("  add <id> <tool_name>  - Add tool node")
        print("  connect <from> <to>   - Connect two nodes")
        print("  show                  - Show current workflow") 
        print("  diagram               - Generate Mermaid diagram")
        print("  export                - Generate LangGraph code")
        print("  save <file>           - Save workflow")
        print("  load <file>           - Load workflow")
        print("  test                  - Test current workflow")
        print("  clear                 - Clear workflow")
        print("  quit                  - Exit builder")
        print("=" * 50)
        
        while True:
            try:
                cmd = input("\n🎯 Builder> ").strip().split()
                if not cmd:
                    continue
                
                action = cmd[0].lower()
                
                if action == "quit" or action == "q":
                    print("👋 Goodbye!")
                    break
                
                elif action == "tools":
                    self.list_tools()
                
                elif action == "add" and len(cmd) >= 3:
                    node_id = cmd[1]
                    tool_name = cmd[2]
                    
                    if tool_name not in self.available_tools:
                        print(f"❌ Unknown tool: {tool_name}")
                        continue
                    
                    # Get parameters if needed
                    params = {}
                    if self.available_tools[tool_name]["parameters"]:
                        print(f"Parameters for {tool_name}:")
                        for param, desc in self.available_tools[tool_name]["parameters"].items():
                            value = input(f"  {param} ({desc}): ").strip()
                            if value:
                                params[param] = value
                    
                    self.add_node(
                        node_id=node_id,
                        node_name=f"{tool_name}_{node_id}",
                        node_type=NodeType.TOOL,
                        tool_name=tool_name,
                        parameters=params,
                        description=self.available_tools[tool_name]["description"]
                    )
                
                elif action == "connect" and len(cmd) >= 3:
                    from_node = cmd[1]
                    to_node = cmd[2]
                    label = " ".join(cmd[3:]) if len(cmd) > 3 else ""
                    self.add_edge(from_node, to_node, label=label)
                
                elif action == "show":
                    print(f"\n📋 Workflow: {self.workflow.name}")
                    print(f"Description: {self.workflow.description}")
                    print(f"Nodes ({len(self.workflow.nodes)}):")
                    for node in self.workflow.nodes:
                        print(f"  • {node.id}: {node.name} ({node.type.value})")
                    print(f"Edges ({len(self.workflow.edges)}):")
                    for edge in self.workflow.edges:
                        print(f"  • {edge.from_node} → {edge.to_node}")
                
                elif action == "diagram":
                    print("\n🎨 Mermaid Diagram:")
                    print("=" * 30)
                    print(self.generate_mermaid_diagram())
                    print("=" * 30)
                
                elif action == "export":
                    print("\n💻 Generated LangGraph Code:")
                    print("=" * 40)
                    print(self.generate_langgraph_code())
                    print("=" * 40)
                
                elif action == "save" and len(cmd) >= 2:
                    filepath = cmd[1]
                    self.save_workflow(filepath)
                
                elif action == "load" and len(cmd) >= 2:
                    filepath = cmd[1]
                    if os.path.exists(filepath):
                        self.load_workflow(filepath)
                    else:
                        print(f"❌ File not found: {filepath}")
                
                elif action == "clear":
                    self.workflow.nodes.clear()
                    self.workflow.edges.clear()
                    print("🗑️ Workflow cleared")
                
                elif action == "test":
                    if not self.workflow.nodes:
                        print("❌ No nodes to test")
                        continue
                    
                    print("🧪 Testing workflow nodes...")
                    for node in self.workflow.nodes:
                        if node.type == NodeType.TOOL and node.tool_name:
                            try:
                                print(f"Testing {node.name}...")
                                # Quick test of tool
                                if node.tool_name == "system_info":
                                    result = osquery_tools.query_system_info()
                                elif node.tool_name == "users":
                                    result = osquery_tools.query_users()
                                print(f"✅ {node.name} - OK")
                            except Exception as e:
                                print(f"❌ {node.name} - Error: {e}")
                
                else:
                    print(f"❌ Unknown command: {action}")
                    print("Type 'help' or see command list above")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def create_sample_workflow():
    """Create a sample security analysis workflow"""
    builder = WorkflowBuilder()
    builder.workflow.name = "Security Analysis"
    builder.workflow.description = "Comprehensive system security analysis"
    
    # Add nodes
    builder.add_node("start", "Start Analysis", NodeType.START)
    builder.add_node("sys_info", "System Info", NodeType.TOOL, "system_info")
    builder.add_node("proc_check", "Process Check", NodeType.TOOL, "processes", {"limit": "15"})
    builder.add_node("user_audit", "User Audit", NodeType.TOOL, "users")
    builder.add_node("net_check", "Network Check", NodeType.TOOL, "network_connections", {"limit": "20"})
    builder.add_node("end", "Analysis Complete", NodeType.END)
    
    # Add edges
    builder.add_edge("start", "sys_info")
    builder.add_edge("sys_info", "proc_check")
    builder.add_edge("proc_check", "user_audit")
    builder.add_edge("user_audit", "net_check")
    builder.add_edge("net_check", "end")
    
    return builder


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OSQuery Workflow Builder")
    parser.add_argument("--sample", action="store_true", help="Create sample workflow")
    parser.add_argument("--export", type=str, help="Export workflow to file")
    
    args = parser.parse_args()
    
    if args.sample:
        builder = create_sample_workflow()
        print("📋 Sample security analysis workflow created")
        
        if args.export:
            # Export as LangGraph code
            code = builder.generate_langgraph_code()
            with open(args.export, 'w') as f:
                f.write(code)
            print(f"💾 Exported to {args.export}")
        else:
            print("\n🎨 Mermaid Diagram:")
            print(builder.generate_mermaid_diagram())
    else:
        builder = WorkflowBuilder()
        builder.run_interactive_builder()