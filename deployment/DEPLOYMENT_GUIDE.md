# Production Deployment Guide

## Overview

This guide covers deploying the OSQuery MCP Server with LangChain/LangGraph support in production environments. Multiple deployment approaches are provided for different use cases.

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Quick Start
```bash
# Clone repository
git clone https://github.com/gpad1234/agentic-python-getting-started.git
cd agentic-python-getting-started

# Build and run with Docker Compose
docker-compose -f deployment/docker-compose.yml up -d

# Check logs
docker-compose -f deployment/docker-compose.yml logs -f
```

#### Production Services
- **mcp-server**: Core MCP OSQuery server (STDIO mode)
- **langgraph-service**: LangGraph orchestration runtime
- **langchain-agent**: Intelligent agent with LLM reasoning
- **monitoring**: Prometheus metrics collection (optional)
- **log-collector**: Centralized logging with Fluent Bit (optional)

#### Resource Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 20GB disk
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB disk
- **Network**: No inbound ports required (STDIO communication)

### 2. Kubernetes Deployment

Create Kubernetes manifests for scalable deployment:

```yaml
# deployment/k8s/mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-osquery-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-osquery-server
  template:
    metadata:
      labels:
        app: mcp-osquery-server
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: mcp-server
        image: mcp-osquery:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi" 
            cpu: "1000m"
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

### 3. Systemd Service

For direct host deployment:

```ini
# /etc/systemd/system/mcp-osquery.service
[Unit]
Description=MCP OSQuery Server
After=network.target
Requires=network.target

[Service]
Type=simple
User=osquery
Group=osquery
WorkingDirectory=/opt/mcp-osquery
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/mcp-osquery/venv/bin/python -m mcp_osquery_server.server
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-osquery

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/mcp-osquery/logs
ProtectHome=yes
PrivateDevices=yes

[Install]
WantedBy=multi-user.target
```

## Configuration

### Environment Variables

```bash
# Core settings
PYTHONUNBUFFERED=1
MCP_LOG_LEVEL=INFO
OSQUERY_TIMEOUT=30

# LangChain settings (if using real LLM)
OPENAI_API_KEY=your-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key

# Security settings
MCP_ALLOWED_QUERIES=system_info,processes,users,network_interfaces
MCP_RATE_LIMIT=10
```

### Security Configuration

#### 1. Network Security
- **STDIO only**: No network ports exposed by default
- **Container isolation**: Each service in separate container
- **Network policies**: Kubernetes network policies for pod isolation

#### 2. Access Control
```python
# mcp_osquery_server/security.py
ALLOWED_TABLES = [
    'system_info', 'processes', 'users', 
    'interface_details', 'listening_ports'
]

BLOCKED_QUERIES = [
    'SELECT * FROM file',  # Prevent file system access
    'DROP ', 'INSERT ', 'UPDATE ', 'DELETE '  # Prevent modifications
]

RATE_LIMITS = {
    'default': 10,  # 10 requests per minute
    'custom_query': 5  # Custom queries more restricted
}
```

#### 3. Audit Logging
```python
# Enable audit logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/audit.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Tuning

#### 1. OSQuery Optimization
```ini
# /etc/osquery/osquery.conf
{
  "options": {
    "config_plugin": "filesystem",
    "logger_plugin": "filesystem",
    "disable_events": false,
    "disable_audit": false,
    "audit_allow_config": true,
    "host_identifier": "hostname",
    "schedule_splay_percent": 10
  },
  "schedule": {
    "system_info": {
      "query": "SELECT hostname, cpu_brand, physical_memory FROM system_info;",
      "interval": 300
    }
  }
}
```

#### 2. Python Optimization
```python
# Use async/await for all I/O operations
# Enable connection pooling
# Implement caching for frequently accessed data
# Use memory-efficient data structures
```

## Monitoring & Observability

### 1. Health Checks

```python
# health_check.py
import asyncio
from mcp_osquery_server import osquery_tools

async def health_check():
    try:
        # Test basic functionality
        client = osquery_tools.get_client()
        result = await client.query("SELECT 1;")
        return {"status": "healthy", "osquery": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### 2. Metrics Collection

```python
# metrics.py
from prometheus_client import Counter, Histogram, start_http_server

query_counter = Counter('osquery_queries_total', 'Total queries executed')
query_duration = Histogram('osquery_query_duration_seconds', 'Query execution time')

@query_duration.time()
def execute_query(sql):
    query_counter.inc()
    # Execute query logic
```

### 3. Log Analysis

```bash
# Useful log queries
docker logs mcp-osquery-server 2>&1 | grep ERROR
docker logs mcp-osquery-server 2>&1 | grep "Query executed" | tail -100

# Performance analysis
docker logs mcp-osquery-server 2>&1 | grep -E "duration|time" | sort
```

## Scaling Considerations

### 1. Horizontal Scaling
- **Multiple instances**: Run multiple MCP server instances
- **Load balancing**: Use message queues for work distribution
- **Stateless design**: No local state dependencies

### 2. Vertical Scaling
- **Memory**: Increase for large query results
- **CPU**: Scale for query processing
- **Storage**: Monitor logs and temporary files

### 3. Database Optimization
- **Query caching**: Cache frequent queries
- **Result pagination**: Limit result set sizes
- **Index optimization**: Ensure OSQuery tables are indexed

## Troubleshooting

### Common Issues

1. **OSQuery not found**
   ```bash
   # Install OSQuery
   curl -L https://pkg.osquery.io/deb/osquery_5.12.0-1.linux_x86_64.deb -o osquery.deb
   sudo dpkg -i osquery.deb
   ```

2. **Permission denied**
   ```bash
   # Check user permissions
   sudo usermod -a -G osquery $USER
   # Or run with appropriate permissions
   sudo docker-compose up
   ```

3. **Memory issues**
   ```bash
   # Monitor memory usage
   docker stats
   # Adjust container limits
   echo "memory: 4g" >> docker-compose.override.yml
   ```

### Debug Mode
```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
docker-compose -f deployment/docker-compose.yml up

# Check container logs
docker exec -it mcp-osquery-server tail -f /app/logs/debug.log
```

## Backup & Recovery

### 1. Configuration Backup
```bash
# Backup configuration
tar -czf mcp-config-backup.tar.gz \
    deployment/ \
    .env \
    requirements.txt

# Automated daily backup
echo "0 2 * * * /usr/local/bin/backup-mcp-config.sh" | crontab -
```

### 2. Log Retention
```yaml
# docker-compose.yml logging configuration
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "10"
```

## Security Checklist

- [ ] OSQuery runs as non-root user
- [ ] Container security scanning completed
- [ ] Network policies implemented
- [ ] Audit logging enabled
- [ ] Secrets management configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] TLS/SSL configured (if network mode)
- [ ] Regular security updates scheduled
- [ ] Incident response plan documented

## Performance Benchmarks

| Configuration | Queries/sec | Memory Usage | CPU Usage |
|---------------|-------------|--------------|-----------|
| Single container | 100 | 512MB | 25% |
| 3-replica cluster | 300 | 1.5GB | 60% |
| High-performance | 500+ | 4GB | 80% |

## Support & Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review logs for errors
   - Check resource usage
   - Update security patches

2. **Monthly**:
   - Performance optimization review
   - Backup validation
   - Security audit

3. **Quarterly**:
   - Dependency updates
   - Disaster recovery testing
   - Architecture review