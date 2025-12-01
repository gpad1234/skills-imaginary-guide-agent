# MCP OSQuery Server - Interaction Diagrams

## Sequence Diagrams

### 1. Tool Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant MCP_Client
    participant MCP_Server
    participant OSQuery_Tools
    participant OSQuery_Binary
    participant System

    User->>Claude: "Show me top 5 processes by memory"
    Claude->>Claude: Parse intent & select tool
    Claude->>MCP_Client: Generate MCP request
    
    MCP_Client->>MCP_Server: call_tool("processes", {"limit": 5})
    activate MCP_Server
    
    MCP_Server->>MCP_Server: Validate input parameters
    MCP_Server->>OSQuery_Tools: query_processes(limit=5)
    activate OSQuery_Tools
    
    OSQuery_Tools->>OSQuery_Tools: Generate SQL query
    OSQuery_Tools->>OSQuery_Binary: Execute osqueryi
    activate OSQuery_Binary
    
    OSQuery_Binary->>System: Query system tables
    System-->>OSQuery_Binary: System data
    OSQuery_Binary-->>OSQuery_Tools: JSON response
    deactivate OSQuery_Binary
    
    OSQuery_Tools->>OSQuery_Tools: Parse & validate JSON
    OSQuery_Tools-->>MCP_Server: Structured result
    deactivate OSQuery_Tools
    
    MCP_Server->>MCP_Server: Format MCP response
    MCP_Server-->>MCP_Client: CallToolResult
    deactivate MCP_Server
    
    MCP_Client-->>Claude: Tool result data
    Claude->>Claude: Process & format response
    Claude-->>User: "Here are the top 5 processes..."
```

### 2. Error Handling Flow

```mermaid
sequenceDiagram
    participant MCP_Client
    participant MCP_Server
    participant OSQuery_Tools
    participant OSQuery_Binary

    MCP_Client->>MCP_Server: call_tool("processes", {})
    activate MCP_Server
    
    MCP_Server->>OSQuery_Tools: query_processes()
    activate OSQuery_Tools
    
    OSQuery_Tools->>OSQuery_Binary: Execute osqueryi
    OSQuery_Binary-->>OSQuery_Tools: Error: osqueryi not found
    
    OSQuery_Tools->>OSQuery_Tools: Handle subprocess error
    OSQuery_Tools-->>MCP_Server: {"success": false, "error": "osqueryi not found"}
    deactivate OSQuery_Tools
    
    MCP_Server->>MCP_Server: Create error response
    MCP_Server-->>MCP_Client: CallToolResult(isError=true)
    deactivate MCP_Server
    
    Note over MCP_Client: Client receives structured error
```

### 3. Server Initialization Flow

```mermaid
sequenceDiagram
    participant Process
    participant Server
    participant OSQuery_Client
    participant System

    Process->>Server: Start MCP Server
    activate Server
    
    Server->>Server: Initialize logging
    Server->>Server: Register tools
    
    Note over Server: Server ready for requests
    
    Server->>Process: Listen on STDIO
    
    loop Request Processing
        Process->>Server: JSON-RPC request
        Server->>OSQuery_Client: Initialize if needed
        activate OSQuery_Client
        
        OSQuery_Client->>System: Check osqueryi availability
        System-->>OSQuery_Client: Path or error
        OSQuery_Client-->>Server: Client ready
        deactivate OSQuery_Client
        
        Server->>Server: Process request
        Server-->>Process: JSON-RPC response
    end
```

## Component Interaction Diagrams

### 1. System Overview

```mermaid
graph TB
    subgraph "AI Layer"
        A[Claude AI Model]
        B[Natural Language Processing]
    end
    
    subgraph "Protocol Layer"
        C[MCP Client]
        D[JSON-RPC over STDIO]
        E[MCP Server]
    end
    
    subgraph "Application Layer"
        F[Tool Registry]
        G[Request Handler]
        H[OSQuery Tools]
    end
    
    subgraph "System Layer"
        I[OSQuery Binary]
        J[System Tables]
        K[Operating System]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    G --> H
    H --> I
    I --> J
    J --> K
    
    K --> J
    J --> I
    I --> H
    H --> G
    G --> E
    E --> D
    D --> C
    C --> B
    B --> A
```

### 2. Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Processing"
        A[User Query] --> B[AI Intent Recognition]
        B --> C[Tool Selection]
        C --> D[Parameter Extraction]
    end
    
    subgraph "MCP Layer"
        D --> E[MCP Request]
        E --> F[Tool Dispatcher]
        F --> G[Input Validation]
    end
    
    subgraph "Query Layer"
        G --> H[SQL Generation]
        H --> I[Process Execution]
        I --> J[Result Processing]
    end
    
    subgraph "System Layer"
        J --> K[OSQuery Binary]
        K --> L[System Tables]
        L --> M[Raw Data]
    end
    
    subgraph "Response Processing"
        M --> N[JSON Parsing]
        N --> O[Data Validation]
        O --> P[Response Formatting]
        P --> Q[User Response]
    end
```

### 3. Error Handling Architecture

```mermaid
graph TB
    subgraph "Error Sources"
        A[Input Validation Error]
        B[Process Execution Error]
        C[OSQuery Error]
        D[System Error]
    end
    
    subgraph "Error Processing"
        E[Error Detector]
        F[Error Classifier]
        G[Error Logger]
        H[Recovery Handler]
    end
    
    subgraph "Error Response"
        I[Error Formatter]
        J[Client Notification]
        K[User Feedback]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    F --> G
    F --> H
    
    G --> I
    H --> I
    I --> J
    J --> K
```

## Tool Interaction Matrix

### Available Tools and Their Dependencies

| Tool | OSQuery Tables | System Requirements | Permissions |
|------|---------------|-------------------|-------------|
| **system_info** | `system_info` | None | User |
| **processes** | `processes` | None | User |
| **users** | `users` | None | User |
| **network_interfaces** | `interface_details` | None | User |
| **network_connections** | `process_open_sockets` | None | User |
| **open_files** | `process_open_files` | None | User/Root* |
| **disk_usage** | `mounts` | None | User |
| **installed_packages** | `programs`, `packages` | Platform specific | User |
| **running_services** | `launchd`, `systemd_units` | Platform specific | User/Root* |
| **custom_query** | Any valid table | Varies | User/Root* |

*\* Some queries may require elevated privileges*

### Tool Execution Patterns

```mermaid
graph TD
    subgraph "Quick Response Tools (< 1s)"
        A[system_info]
        B[users]
        C[network_interfaces]
    end
    
    subgraph "Medium Response Tools (1-5s)"
        D[processes]
        E[disk_usage]
        F[network_connections]
    end
    
    subgraph "Variable Response Tools (1-30s)"
        G[open_files]
        H[installed_packages]
        I[running_services]
        J[custom_query]
    end
    
    subgraph "Optimization Strategies"
        K[LIMIT clauses]
        L[Indexed columns]
        M[Efficient filters]
    end
    
    D --> K
    E --> L
    F --> K
    G --> M
    H --> L
    I --> L
    J --> K
    J --> M
```

## Communication Protocol Details

### MCP Request Structure

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "processes",
    "arguments": {
      "limit": 5
    }
  },
  "id": 1
}
```

### MCP Response Structure

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  {\n    \"pid\": \"250011\",\n    \"name\": \"node\",\n    \"uid\": \"1000\",\n    \"resident_size\": \"1198477312\"\n  }\n]"
      }
    ],
    "isError": false
  },
  "id": 1
}
```

### Error Response Structure

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: osqueryi not found"
      }
    ],
    "isError": true
  },
  "id": 1
}
```

## State Management

### Server State Diagram

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Ready: Setup complete
    Initializing --> Failed: Setup error
    
    Ready --> Processing: Request received
    Processing --> Ready: Request completed
    Processing --> Error: Request failed
    
    Error --> Ready: Error handled
    Error --> Failed: Critical error
    
    Failed --> [*]: Server shutdown
    Ready --> [*]: Graceful shutdown
```

### Client Connection State

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: Start server
    Connecting --> Connected: Handshake complete
    Connecting --> Failed: Connection error
    
    Connected --> Active: Tool call
    Active --> Connected: Response sent
    Active --> Error: Tool error
    
    Error --> Connected: Error recovered
    Error --> Disconnected: Connection lost
    
    Connected --> Disconnected: Shutdown
    Failed --> [*]: Terminal error
    Disconnected --> [*]: Clean exit
```

## Performance Characteristics

### Response Time Distribution

| Tool Category | Typical Response Time | 95th Percentile | Timeout |
|---------------|----------------------|-----------------|---------|
| **System Info** | 50-200ms | 500ms | 30s |
| **Process Queries** | 100-500ms | 2s | 30s |
| **Network Queries** | 200-1000ms | 3s | 30s |
| **File System** | 500-2000ms | 10s | 30s |
| **Custom Queries** | Variable | Variable | 30s |

### Concurrency Model

```mermaid
graph TB
    subgraph "Request Processing"
        A[Incoming Request]
        B[Async Handler]
        C[Tool Dispatcher]
    end
    
    subgraph "Concurrent Execution"
        D[Tool 1]
        E[Tool 2]
        F[Tool N]
    end
    
    subgraph "Response Management"
        G[Result Aggregator]
        H[Response Builder]
        I[Client Response]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    
    D --> G
    E --> G
    F --> G
    
    G --> H
    H --> I
```

---

**Interaction Design Version**: 1.0  
**Last Updated**: November 9, 2025  
**Mermaid Version**: Compatible with latest renderers