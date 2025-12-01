# MCP OSQuery Server - Architecture Documentation

## System Overview

The MCP OSQuery Server is a Model Context Protocol (MCP) server that provides system information querying capabilities through osquery integration. It enables AI models like Claude to query and analyze system state in real-time.

## High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│   AI Model      │◄────┤   MCP Client    │◄────┤   MCP Server    │◄────┤   OSQuery       │
│   (Claude)      │     │   (JSON-RPC)    │     │   (Python)      │     │   (osqueryi)    │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
        │                         │                         │                         │
        │                         │                         │                         │
        v                         v                         v                         v
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Natural        │     │  JSON-RPC       │     │  Python         │     │  SQL Queries    │
│  Language       │     │  over STDIO     │     │  Functions      │     │  to System      │
│  Queries        │     │                 │     │                 │     │  Tables         │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Component Architecture

### 1. MCP Server Layer (`mcp_osquery_server/server.py`)

```python
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              MCP Server                                          │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐  │
│  │   Tool Registry     │    │   Request Handler   │    │   Response Builder  │  │
│  │                     │    │                     │    │                     │  │
│  │ • system_info       │    │ • Input validation  │    │ • JSON formatting   │  │
│  │ • processes         │◄───┤ • Tool dispatching  │───►│ • Error handling    │  │
│  │ • users             │    │ • Async execution   │    │ • Type safety       │  │
│  │ • network_*         │    │                     │    │                     │  │
│  │ • custom_query      │    │                     │    │                     │  │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘  │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                            Protocol Layer (MCP)                                 │
│                           • JSON-RPC over STDIO                                 │
│                           • Async/Await Support                                 │
│                           • Type-Safe Interfaces                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 2. OSQuery Tools Layer (`mcp_osquery_server/osquery_tools.py`)

```python
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             OSQuery Tools                                       │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐  │
│  │   OSQueryClient     │    │   Query Functions   │    │   Result Processor  │  │
│  │                     │    │                     │    │                     │  │
│  │ • Path resolution   │    │ • System info       │    │ • JSON parsing      │  │
│  │ • Process execution │◄───┤ • Process queries   │───►│ • Error handling    │  │
│  │ • Timeout handling  │    │ • Network queries   │    │ • Data validation   │  │
│  │ • Error recovery    │    │ • Custom SQL        │    │ • Type conversion   │  │
│  │                     │    │                     │    │                     │  │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘  │
│                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│                           System Interface                                      │
│                          • subprocess execution                                 │
│                          • osqueryi binary                                      │
│                          • 30-second timeout                                    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3. System Integration Layer

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            Operating System                                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐  │
│  │   System Tables     │    │   Process Monitor   │    │   Network Monitor   │  │
│  │                     │    │                     │    │                     │  │
│  │ • system_info       │    │ • processes         │    │ • interface_details │  │
│  │ • users             │    │ • process_open_*    │    │ • process_open_*    │  │
│  │ • os_version        │    │ • memory_usage      │    │ • listening_ports   │  │
│  │ • uptime            │    │                     │    │                     │  │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘  │
│                                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐  │
│  │   File System      │    │   Package Manager   │    │   Service Manager   │  │
│  │                     │    │                     │    │                     │  │
│  │ • mounts            │    │ • programs          │    │ • launchd (macOS)   │  │
│  │ • file             │    │ • packages          │    │ • systemd (Linux)   │  │
│  │ • disk_events      │    │ • rpm_packages      │    │ • services          │  │
│  │                     │    │                     │    │                     │  │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘  │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### Request Flow

```
1. User Query
   │
   ├─ "Show me top 5 processes by memory"
   │
   v
2. Claude/AI Model
   │
   ├─ Natural Language Processing
   ├─ Intent Recognition
   ├─ Tool Selection: "processes"
   │
   v
3. MCP Client
   │
   ├─ JSON-RPC Request
   ├─ Method: "call_tool"
   ├─ Parameters: {"name": "processes", "arguments": {"limit": 5}}
   │
   v
4. MCP Server (server.py)
   │
   ├─ Request Validation
   ├─ Tool Dispatch
   ├─ Async Execution
   │
   v
5. OSQuery Tools (osquery_tools.py)
   │
   ├─ SQL Generation: "SELECT pid, name, uid, resident_size FROM processes ORDER BY resident_size DESC LIMIT 5;"
   ├─ Process Execution
   ├─ Result Processing
   │
   v
6. OSQuery Binary (osqueryi)
   │
   ├─ SQL Execution
   ├─ System Table Access
   ├─ JSON Output
   │
   v
7. Response Flow (Reverse)
   │
   ├─ JSON Data
   ├─ Error Handling
   ├─ Format Validation
   ├─ MCP Response
   ├─ Claude Processing
   ├─ User Response
```

### Error Handling Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Client Error  │     │   Server Error  │     │  System Error   │
│                 │     │                 │     │                 │
└─────────┬───────┘     └─────────┬───────┘     └─────────┬───────┘
          │                       │                       │
          v                       v                       v
┌─────────────────────────────────────────────────────────────────────┐
│                      Error Handler                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   Validation    │  │   Logging       │  │   Recovery      │     │
│  │                 │  │                 │  │                 │     │
│  │ • Input check   │  │ • Error details │  │ • Retry logic   │     │
│  │ • Type safety   │  │ • Stack trace   │  │ • Fallback      │     │
│  │ • Range limits  │  │ • Context info  │  │ • Graceful fail │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
│  Result: Structured Error Response with isError=true               │
└─────────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Security Layers                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        Application Layer                                │   │
│  │                                                                         │   │
│  │  • API Key Management (.env files)                                     │   │
│  │  • Git Secret Protection (.gitignore)                                  │   │
│  │  • Environment Isolation (virtual env)                                 │   │
│  │  • Input Validation (Pydantic schemas)                                 │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         Protocol Layer                                 │   │
│  │                                                                         │   │
│  │  • JSON-RPC over STDIO (no network exposure)                           │   │
│  │  • Type-safe interfaces (CallToolResult)                               │   │
│  │  • Timeout protection (30s limit)                                      │   │
│  │  • Error containment (exception handling)                              │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          System Layer                                  │   │
│  │                                                                         │   │
│  │  • User-level permissions (no sudo by default)                         │   │
│  │  • Read-only system access (osquery tables)                            │   │
│  │  • SQL injection protection (parameterized)                            │   │
│  │  • Resource limits (query timeouts)                                    │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Performance Architecture

### Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Performance Optimizations                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐ │
│  │   Async Processing  │    │   Query Optimization│    │   Resource Management│ │
│  │                     │    │                     │    │                     │ │
│  │ • Non-blocking I/O  │    │ • LIMIT clauses     │    │ • 30s timeout       │ │
│  │ • Concurrent tools  │◄───┤ • Indexed columns   │───►│ • Memory limits     │ │
│  │ • Event-driven      │    │ • Efficient joins   │    │ • Process cleanup   │ │
│  │ • Async/await       │    │                     │    │                     │ │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐ │
│  │   Caching Strategy  │    │   Error Handling    │    │   Monitoring        │ │
│  │                     │    │                     │    │                     │ │
│  │ • Client instance   │    │ • Fast failures     │    │ • Query timing      │ │
│  │ • Path caching      │◄───┤ • Circuit breakers  │───►│ • Error rates       │ │
│  │ • Result streaming  │    │ • Graceful degrader │    │ • Resource usage    │ │
│  │                     │    │                     │    │                     │ │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Development Setup                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐ │
│  │   Local Environment │    │   Version Control   │    │   Security Config   │ │
│  │                     │    │                     │    │                     │ │
│  │ • Python 3.12.3     │    │ • Git repository    │    │ • .env files        │ │
│  │ • Virtual env       │◄───┤ • .gitignore rules  │───►│ • API key mgmt      │ │
│  │ • VS Code tasks     │    │ • Branch strategy   │    │ • Secret protection │ │
│  │ • osquery binary    │    │                     │    │                     │ │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Production Deployment

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Production Architecture                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          AI Model Integration                           │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │   │
│  │  │   Claude API    │    │   Cursor IDE    │    │   Custom Client │      │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘      │   │
│  │                                   │                                     │   │
│  └───────────────────────────────────┼─────────────────────────────────────┘   │
│                                      │                                         │
│  ┌───────────────────────────────────┼─────────────────────────────────────┐   │
│  │                          MCP Configuration                              │   │
│  │                                   │                                     │   │
│  │  ┌─────────────────┐    ┌─────────▼─────────┐    ┌─────────────────┐   │   │
│  │  │   Settings JSON │    │   MCP Server      │    │   Process Mgmt  │   │   │
│  │  └─────────────────┘    └───────────────────┘    └─────────────────┘   │   │
│  │                                   │                                     │   │
│  └───────────────────────────────────┼─────────────────────────────────────┘   │
│                                      │                                         │
│  ┌───────────────────────────────────┼─────────────────────────────────────┐   │
│  │                          System Resources                               │   │
│  │                                   │                                     │   │
│  │  ┌─────────────────┐    ┌─────────▼─────────┐    ┌─────────────────┐   │   │
│  │  │   OSQuery       │    │   System Tables   │    │   Permissions   │   │   │
│  │  └─────────────────┘    └───────────────────┘    └─────────────────┘   │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Dependencies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Protocol** | Model Context Protocol | 1.21.0 | AI-tool communication |
| **Language** | Python | 3.12.3 | Core implementation |
| **Validation** | Pydantic | 2.12.4 | Type safety & validation |
| **Environment** | python-dotenv | 1.2.1 | Configuration management |
| **AI Integration** | Anthropic | 0.72.0 | Claude API client |
| **System Queries** | OSQuery | 5.x | System information access |

### Development Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Editor** | VS Code | Development environment |
| **Version Control** | Git | Source code management |
| **Package Manager** | pip/venv | Dependency management |
| **Documentation** | Markdown | Technical documentation |
| **Testing** | Python unittest | Quality assurance |

## Extension Points

### Adding New Tools

```python
# 1. Define query function in osquery_tools.py
def query_new_feature() -> Dict[str, Any]:
    """Query new system feature."""
    client = get_client()
    return client.query("SELECT * FROM new_table;")

# 2. Register tool in server.py
Tool(
    name="new_feature",
    description="Get new system feature information",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter"}
        },
        "required": []
    }
)

# 3. Add handler in call_tool()
elif name == "new_feature":
    result = osquery_tools.query_new_feature()
```

### Custom Query Extensions

```sql
-- Security monitoring
SELECT pid, name, cmdline FROM processes WHERE cmdline LIKE '%password%';

-- Network analysis
SELECT protocol, local_address, remote_address, state 
FROM process_open_sockets 
WHERE state = 'ESTABLISHED';

-- System performance
SELECT name, interval, executions, avg_system_time 
FROM osquery_schedule;
```

## Best Practices

### 1. Security Guidelines
- Never commit `.env` files
- Use least-privilege access
- Validate all inputs
- Implement proper timeouts
- Log security events

### 2. Performance Guidelines
- Use LIMIT clauses in queries
- Implement proper error handling
- Cache expensive operations
- Monitor resource usage


## Alternate orchestrator: LangChain + LangGraph

As an optional alternate design, you can use LangChain with LangGraph to
orchestrate the same osquery tool callables. This approach is useful when
you want graph-based planning, richer LLM-driven control flow, or a visual
authoring surface for tool workflows.

This repository includes a lightweight adapter (`langgraph_adapter.py`) that
returns a serializable design map when the runtime packages are not
installed, and a runtime-friendly representation when `langchain` and
`langgraph` are available. See `docs/ALTERNATE_DESIGN_LANGCHAIN.md` for
detailed tradeoffs and a quick-start.

Notes:
- Keep `mcp_osquery_server/osquery_tools.py` as the canonical implementation
   of tools. The LangGraph design should map graph nodes to those callables.
- Installing the optional packages is required only if you plan to run the
   LangChain/Graph runtime. The adapter itself is safe to import without
   those packages.

- Use async/await patterns

### 3. Maintenance Guidelines
- Regular dependency updates
- Monitor osquery versions
- Test on target platforms
- Document configuration changes
- Backup configuration files

---

**Architecture Version**: 1.0  
**Last Updated**: November 9, 2025  
**Compatibility**: MCP 1.21.0, Python 3.12+, OSQuery 5.x