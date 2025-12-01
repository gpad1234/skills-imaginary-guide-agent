# MCP OSQuery Server - Technical Specifications

## System Requirements

### Minimum Requirements

| Component | Specification | Notes |
|-----------|---------------|-------|
| **Operating System** | macOS 10.15+ / Linux (Ubuntu 18.04+) | Windows support via WSL |
| **Python** | 3.8+ | Recommended: 3.11+ |
| **Memory** | 512 MB RAM | Additional 256 MB for osquery |
| **Storage** | 100 MB | Includes dependencies |
| **OSQuery** | 5.0+ | Optional for demo mode |
| **Network** | None | Communicates via STDIO |

### Recommended Requirements

| Component | Specification | Benefits |
|-----------|---------------|---------|
| **Operating System** | macOS 12+ / Linux (Ubuntu 20.04+) | Latest osquery features |
| **Python** | 3.12+ | Performance optimizations |
| **Memory** | 2 GB RAM | Better performance for large queries |
| **Storage** | 1 GB | Room for logs and caching |
| **CPU** | 2+ cores | Concurrent query processing |

## API Specifications

### MCP Tool Interface

#### Tool: `system_info`

**Description**: Get general system information including OS, hostname, CPU, and memory details.

```typescript
interface SystemInfoTool {
  name: "system_info";
  description: "Get general system information (OS, hostname, CPU count, etc.)";
  inputSchema: {
    type: "object";
    properties: {};
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "hostname": {"type": "string"},
      "computer_name": {"type": "string"},
      "cpu_brand": {"type": "string"},
      "cpu_logical_cores": {"type": "string"},
      "cpu_physical_cores": {"type": "string"},
      "physical_memory": {"type": "string"},
      "hardware_model": {"type": "string"},
      "uuid": {"type": "string"}
    }
  }
}
```

#### Tool: `processes`

**Description**: Get running processes sorted by memory usage.

```typescript
interface ProcessesTool {
  name: "processes";
  description: "Get top memory-consuming processes";
  inputSchema: {
    type: "object";
    properties: {
      limit: {
        type: "integer";
        description: "Number of processes to return (default: 10)";
        default: 10;
        minimum: 1;
        maximum: 1000;
      };
    };
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "pid": {"type": "string"},
      "name": {"type": "string"},
      "uid": {"type": "string"},
      "resident_size": {"type": "string"}
    },
    "required": ["pid", "name", "uid", "resident_size"]
  }
}
```

#### Tool: `users`

**Description**: Get system user accounts.

```typescript
interface UsersTool {
  name: "users";
  description: "Get system users";
  inputSchema: {
    type: "object";
    properties: {};
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "uid": {"type": "string"},
      "gid": {"type": "string"},
      "username": {"type": "string"},
      "description": {"type": "string"},
      "directory": {"type": "string"},
      "shell": {"type": "string"}
    },
    "required": ["uid", "username"]
  }
}
```

#### Tool: `network_interfaces`

**Description**: Get network interface details.

```typescript
interface NetworkInterfacesTool {
  name: "network_interfaces";
  description: "Get network interfaces and their details";
  inputSchema: {
    type: "object";
    properties: {};
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "interface": {"type": "string"},
      "mac": {"type": "string"},
      "mtu": {"type": "string"},
      "metric": {"type": "string"}
    },
    "required": ["interface", "mac"]
  }
}
```

#### Tool: `network_connections`

**Description**: Get active network connections.

```typescript
interface NetworkConnectionsTool {
  name: "network_connections";
  description: "Get active network connections";
  inputSchema: {
    type: "object";
    properties: {
      limit: {
        type: "integer";
        description: "Number of connections to return (default: 20)";
        default: 20;
        minimum: 1;
        maximum: 1000;
      };
    };
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "protocol": {"type": "string"},
      "local_address": {"type": "string"},
      "local_port": {"type": "string"},
      "remote_address": {"type": "string"},
      "remote_port": {"type": "string"},
      "state": {"type": "string"}
    }
  }
}
```

#### Tool: `open_files`

**Description**: Get files opened by processes.

```typescript
interface OpenFilesTool {
  name: "open_files";
  description: "Get open files by processes";
  inputSchema: {
    type: "object";
    properties: {
      pid: {
        type: "integer";
        description: "Process ID (optional, gets all if not specified)";
        minimum: 1;
      };
    };
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "pid": {"type": "string"},
      "path": {"type": "string"}
    },
    "required": ["pid", "path"]
  }
}
```

#### Tool: `disk_usage`

**Description**: Get disk usage and mount information.

```typescript
interface DiskUsageTool {
  name: "disk_usage";
  description: "Get disk usage and mount information";
  inputSchema: {
    type: "object";
    properties: {};
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "path": {"type": "string"},
      "blocks_size": {"type": "string"},
      "blocks_available": {"type": "string"}
    },
    "required": ["path"]
  }
}
```

#### Tool: `installed_packages`

**Description**: Get installed packages/applications.

```typescript
interface InstalledPackagesTool {
  name: "installed_packages";
  description: "Get installed packages/applications";
  inputSchema: {
    type: "object";
    properties: {};
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "version": {"type": "string"},
      "source": {"type": "string"}
    },
    "required": ["name"]
  }
}
```

#### Tool: `running_services`

**Description**: Get running services.

```typescript
interface RunningServicesTool {
  name: "running_services";
  description: "Get running services (launchd on macOS)";
  inputSchema: {
    type: "object";
    properties: {};
    required: [];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "state": {"type": "string"},
      "pid": {"type": "string"}
    },
    "required": ["name"]
  }
}
```

#### Tool: `custom_query`

**Description**: Execute custom osquery SQL.

```typescript
interface CustomQueryTool {
  name: "custom_query";
  description: "Execute a custom osquery SQL query";
  inputSchema: {
    type: "object";
    properties: {
      sql: {
        type: "string";
        description: "osquery SQL query to execute";
        pattern: "^SELECT\\s+.*";
        maxLength: 10000;
      };
    };
    required: ["sql"];
  };
}
```

**Response Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": true
  }
}
```

## Error Response Specifications

### Standard Error Response

```typescript
interface ErrorResponse {
  content: Array<{
    type: "text";
    text: string;
  }>;
  isError: true;
}
```

### Error Categories

| Error Type | HTTP Equivalent | Description | Example |
|------------|----------------|-------------|---------|
| **ValidationError** | 400 | Invalid input parameters | `"limit must be between 1 and 1000"` |
| **ToolNotFoundError** | 404 | Unknown tool name | `"Unknown tool: invalid_tool"` |
| **ExecutionError** | 500 | OSQuery execution failed | `"osqueryi execution failed: timeout"` |
| **SystemError** | 503 | System unavailable | `"osqueryi not found"` |
| **TimeoutError** | 504 | Query timeout | `"Query timed out after 30 seconds"` |

### Error Response Examples

```json
// Validation Error
{
  "content": [{"type": "text", "text": "Error: limit must be a positive integer"}],
  "isError": true
}

// System Error
{
  "content": [{"type": "text", "text": "Error: osqueryi not found"}],
  "isError": true
}

// Timeout Error
{
  "content": [{"type": "text", "text": "Error: Query timed out after 30 seconds"}],
  "isError": true
}
```

## Performance Specifications

### Query Performance Targets

| Query Type | Target Response Time | Maximum Response Time | Typical Data Size |
|------------|---------------------|----------------------|------------------|
| **system_info** | < 100ms | 1s | < 1KB |
| **processes** | < 500ms | 5s | < 50KB |
| **users** | < 200ms | 2s | < 10KB |
| **network_interfaces** | < 300ms | 3s | < 5KB |
| **network_connections** | < 1s | 10s | < 100KB |
| **open_files** | < 2s | 15s | < 200KB |
| **disk_usage** | < 500ms | 5s | < 20KB |
| **installed_packages** | < 3s | 20s | < 500KB |
| **running_services** | < 1s | 10s | < 50KB |
| **custom_query** | Variable | 30s | Variable |

### Resource Utilization

| Resource | Normal Usage | Peak Usage | Limits |
|----------|-------------|------------|--------|
| **CPU** | < 5% | < 20% | N/A |
| **Memory** | < 100MB | < 500MB | 1GB |
| **Disk I/O** | < 1MB/s | < 10MB/s | N/A |
| **Subprocess** | 1-2 | 5 | 10 |

### Concurrency Specifications

```python
# Maximum concurrent tool executions
MAX_CONCURRENT_TOOLS = 5

# Query timeout (seconds)
QUERY_TIMEOUT = 30

# Maximum response size (bytes)
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB

# Rate limiting (queries per minute)
RATE_LIMIT = 60
```

## Security Specifications

### Input Validation

| Input Type | Validation Rules | Sanitization |
|------------|------------------|--------------|
| **limit** | 1 ≤ limit ≤ 1000 | Integer coercion |
| **pid** | pid > 0 | Integer validation |
| **sql** | Must start with SELECT | SQL injection prevention |
| **string** | Length < 10000 chars | Escape special chars |

### SQL Query Restrictions

```sql
-- Allowed patterns
SELECT ... FROM table_name WHERE conditions LIMIT number;
SELECT ... FROM table_name ORDER BY column LIMIT number;

-- Forbidden patterns
INSERT INTO ...;
UPDATE ... SET ...;
DELETE FROM ...;
DROP TABLE ...;
CREATE TABLE ...;
ALTER TABLE ...;

-- Forbidden functions
LOAD_EXTENSION();
system();
shell();
```

### Permission Model

| Operation | User Permissions | Root Permissions | Notes |
|-----------|-----------------|------------------|-------|
| **system_info** | ✅ Read | ✅ Read | Always accessible |
| **processes** | ✅ User processes | ✅ All processes | Limited to user context |
| **network_*** | ✅ Basic info | ✅ Full details | Some details require root |
| **open_files** | ✅ User files | ✅ All files | Limited by file permissions |
| **services** | ✅ Read | ✅ Read/Control | Some services require root |

## Configuration Specifications

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional
OSQUERY_TIMEOUT=30
OSQUERY_PATH=/usr/local/bin/osqueryi
LOG_LEVEL=INFO
MAX_RESPONSE_SIZE=10485760
```

### MCP Server Configuration

```json
{
  "mcpServers": {
    "osquery": {
      "command": "python",
      "args": ["-m", "mcp_osquery_server.server"],
      "cwd": "/path/to/project",
      "env": {
        "OSQUERY_TIMEOUT": "30",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Logging Configuration

```python
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "mcp_osquery_server": {
            "handlers": ["default"],
            "level": "INFO"
        }
    }
}
```

## Deployment Specifications

### Package Dependencies

```python
# requirements.txt
mcp>=1.21.0,<2.0.0
pydantic>=2.12.0,<3.0.0
python-dotenv>=1.2.0,<2.0.0
anthropic>=0.72.0,<1.0.0

# Development dependencies
pytest>=7.0.0
black>=23.0.0
mypy>=1.0.0
```

### File Structure Requirements

```
project_root/
├── mcp_osquery_server/
│   ├── __init__.py
│   ├── server.py
│   └── osquery_tools.py
├── .env                    # Required: API keys
├── .gitignore             # Required: Security
├── requirements.txt       # Required: Dependencies
├── README.md              # Recommended
├── docs/                  # Optional
└── tests/                 # Recommended
```

### Installation Verification

```bash
# 1. Verify Python version
python --version  # Should be 3.8+

# 2. Verify virtual environment
which python      # Should point to venv

# 3. Verify dependencies
pip list | grep -E "(mcp|pydantic|anthropic|python-dotenv)"

# 4. Verify osquery (optional)
osqueryi --version

# 5. Verify server startup
timeout 5 python -m mcp_osquery_server.server || echo "Server starts"

# 6. Verify tools
python -c "from mcp_osquery_server import osquery_tools; print('Import OK')"
```

## Testing Specifications

### Unit Test Coverage

| Component | Coverage Target | Test Types |
|-----------|-----------------|------------|
| **osquery_tools.py** | 90%+ | Unit, Integration |
| **server.py** | 85%+ | Unit, E2E |
| **Tool functions** | 95%+ | Unit, Mock |
| **Error handling** | 100% | Unit |

### Test Categories

```python
# Unit Tests
class TestOSQueryTools:
    def test_client_initialization()
    def test_query_execution()
    def test_error_handling()
    def test_timeout_handling()

# Integration Tests
class TestMCPIntegration:
    def test_tool_registration()
    def test_tool_execution()
    def test_response_formatting()

# End-to-End Tests
class TestE2E:
    def test_full_workflow()
    def test_error_scenarios()
    def test_performance()
```

### Performance Benchmarks

```python
# Performance test thresholds
PERFORMANCE_THRESHOLDS = {
    "system_info": 1.0,      # seconds
    "processes": 5.0,
    "users": 2.0,
    "network_interfaces": 3.0,
    "network_connections": 10.0,
    "open_files": 15.0,
    "disk_usage": 5.0,
    "installed_packages": 20.0,
    "running_services": 10.0
}
```

## Monitoring and Observability

### Metrics Collection

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|----------------|
| **request_count** | Counter | Total requests processed | N/A |
| **request_duration** | Histogram | Request processing time | > 30s |
| **error_rate** | Rate | Errors per minute | > 10% |
| **tool_usage** | Counter | Per-tool usage statistics | N/A |
| **query_timeout** | Counter | Timed out queries | > 5% |
| **memory_usage** | Gauge | Process memory usage | > 500MB |

### Health Check Endpoint

```python
# Health check implementation
async def health_check():
    """Check system health."""
    checks = {
        "osquery_available": check_osquery(),
        "memory_usage": get_memory_usage(),
        "response_time": measure_response_time()
    }
    
    return {
        "status": "healthy" if all(checks.values()) else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Log Format Specification

```json
{
  "timestamp": "2025-11-09T12:30:45.123Z",
  "level": "INFO",
  "logger": "mcp_osquery_server.server",
  "message": "Tool executed successfully",
  "tool": "processes",
  "duration_ms": 245,
  "response_size": 1024,
  "user_id": "anonymous"
}
```

---

**Technical Specification Version**: 1.0  
**Last Updated**: November 9, 2025  
**API Version**: 1.0  
**Compatibility**: MCP 1.21.0, Python 3.8+, OSQuery 5.0+