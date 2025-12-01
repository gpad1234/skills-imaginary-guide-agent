# OSQuery MCP Server with LangChain/LangGraph Integration

A comprehensive Model Context Protocol (MCP) server that provides system information querying capabilities through OSQuery, with advanced LangChain and LangGraph integration for intelligent automation and visual workflow design.

## 🚀 Key Features

- **MCP Server**: Direct OSQuery tool access via JSON-RPC over STDIO
- **LangGraph Workflows**: Visual workflow orchestration with graph-based design
- **LangChain Agents**: Intelligent LLM-driven tool selection and chaining
- **Interactive Builder**: Web interface for designing and testing workflows
- **Enterprise Security**: Audit logging, rate limiting, and role-based access control
- **Production Ready**: Docker, Kubernetes, and monitoring support

## 🏗️ Three Integration Approaches

### 1. MCP Server (Original)
Direct tool access for AI models and IDEs:
```bash
python -m mcp_osquery_server.server
```

### 2. LangGraph Workflows
Visual graph-based orchestration:
```bash
python examples/langgraph_example.py
```

### 3. LangChain Agents  
Intelligent LLM-driven automation:
```bash
python examples/langchain_agent.py --interactive
```

## 📊 Quick Start

```bash
# Clone and setup
git clone https://github.com/gpad1234/agentic-python-getting-started.git
cd agentic-python-getting-started

# Install all dependencies (includes LangChain/LangGraph)
source venv/bin/activate
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your Anthropic API key

# Test the interactive workflow builder
python web_interface/workflow_builder.py --sample

# Run a comprehensive security analysis
python examples/langchain_agent.py
```

## 🎯 Use Cases

| Approach | Best For | Example |
|----------|----------|---------|
| **MCP Server** | IDE integration, direct AI tool access | Claude Desktop, Cursor IDE |
| **LangGraph** | Complex workflows, visual design | Multi-step security analysis |
| **LangChain Agent** | Intelligent automation, natural language | "Check for performance issues" |

## 🛠️ Available Tools

- `system_info`: Get comprehensive system information
- `processes`: List running processes with memory usage
- `users`: Enumerate system users and properties
- `network_interfaces`: Show network interface details
- `network_connections`: Display active network connections
- `custom_query`: Execute custom OSQuery SQL with validation

## 🔐 Enterprise Security

- **Role-Based Access Control**: Guest, User, Analyst, Admin roles
- **Audit Logging**: JSON-structured logging with compliance reporting
- **Rate Limiting**: Token bucket and sliding window algorithms
- **SQL Injection Protection**: Pattern detection and query validation
- **Policy Engine**: Customizable security policies and violations

## 🐳 Deployment Options

### Docker (Recommended)
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

### Kubernetes
```bash
kubectl apply -f deployment/k8s/
```

### Local Development
```bash
# MCP Server
python -m mcp_osquery_server.server

# LangGraph Service
python examples/langgraph_example.py --interactive

# Interactive Workflow Builder
python web_interface/workflow_builder.py
```

## 📈 Advanced Features

### Visual Workflow Design
Create complex analysis workflows with the interactive builder:
```bash
python web_interface/workflow_builder.py
# Commands: add, connect, show, diagram, export, test
```

### Security Monitoring
```python
from security.audit_logger import get_audit_logger
from security.rate_limiter import check_rate_limit
from security.security_policy import validate_user_request

# Comprehensive security validation
violations = validate_user_request("analyst1", "custom_query", 
                                  {"sql": "SELECT * FROM processes LIMIT 10"})
```

### Intelligent Analysis
```python
from examples.langchain_agent import OSQueryAgent

agent = OSQueryAgent()
result = await agent.analyze("Show me any security concerns")
# Agent automatically selects and chains appropriate tools
```

## 📚 Documentation

- **[LangChain Integration Guide](LANGCHAIN_INTEGRATION_GUIDE.md)**: Comprehensive guide to all features
- **[Architecture Documentation](docs/ARCHITECTURE.md)**: System design and components
- **[Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)**: Production deployment
- **[Security Documentation](security/README.md)**: Security features and configuration
- **[API Reference](docs/TECHNICAL_SPECS.md)**: Complete API documentation

## 🔄 Migration from MCP-Only

Existing MCP server users can incrementally adopt new features:

1. **Keep existing MCP functionality** - All original features remain unchanged
2. **Add LangGraph workflows** - Create visual workflows for complex analysis
3. **Integrate LangChain agents** - Add intelligent automation layer
4. **Enable security features** - Add audit logging and access control

## 🔒 Security Setup

**IMPORTANT**: This project uses environment variables for API keys:

- ✅ **`.env`** - Contains your actual API keys (git ignored)
- ✅ **`.env.example`** - Safe template (can be committed)
- ✅ **`.gitignore`** - Protects all secrets from git

**Get your API key:**
- Visit [Anthropic Console](https://console.anthropic.com/)
- Create an account and generate an API key
- Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

## 🛡️ Security Features

- ✅ **Environment files protected** (`.env*` git ignored)
- ✅ **API keys secured** (never in source code)  
- ✅ **Virtual environment ignored** (`venv/` excluded)
- ✅ **Comprehensive gitignore** (secrets, credentials, keys)
- ✅ **Enterprise security** (RBAC, audit logging, rate limiting)
- ✅ **Ready for production** (secure by default)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Update documentation
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`) 
7. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/gpad1234/agentic-python-getting-started/issues)
- **Documentation**: See `docs/` directory for comprehensive guides
- **Examples**: Check `examples/` directory for usage patterns
- **Security**: Report security issues privately

## ⚠️ Security Reminder

**Never commit these files:**
- `.env` (contains real API keys)
- Any `*.key`, `*.pem`, or credential files
- Virtual environment directories

The `.gitignore` is configured to prevent this automatically.

---

**Ready for production use with comprehensive testing, enterprise security, and multiple deployment options.**