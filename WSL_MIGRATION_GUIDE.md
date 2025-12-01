# WSL Migration Guide
**MCP OSQuery Server - Windows Subsystem for Linux Setup**

## Pre-Migration Checklist

- [ ] WSL2 installed on Windows
- [ ] Ubuntu 20.04+ distribution selected
- [ ] Git available in WSL
- [ ] Administrator access for package installation

## System Requirements for WSL

### Minimum
- Windows 10/11 with WSL2 enabled
- 4GB RAM allocated to WSL
- 5GB free disk space
- Python 3.10+

### Recommended
- Windows 11
- 8GB+ RAM allocated
- 10GB+ free disk space
- Python 3.12+

## Installation Steps

### Step 1: Enable WSL2 (Windows PowerShell - Admin)
```powershell
wsl --install
# Or if already installed:
wsl --set-default-version 2
```

### Step 2: Install Ubuntu Distribution
```powershell
wsl --install -d Ubuntu-22.04
```

### Step 3: Initial WSL Setup
```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install build essentials
sudo apt-get install -y build-essential curl wget git
```

### Step 4: Install Python and Dependencies
```bash
# Install Python 3.12 (or latest available)
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
```

### Step 5: Install osquery
```bash
# Add osquery repository
curl -L https://pkg.osquery.io/linux_signing_key.asc | sudo apt-key add -
sudo add-apt-repository 'deb [arch=amd64] https://pkg.osquery.io/deb deb main'

# Install osquery
sudo apt-get update
sudo apt-get install -y osquery

# Verify installation
osqueryi --version
```

### Step 6: Clone and Setup Project
```bash
# Navigate to desired directory
cd /home/username/projects  # or your preferred location

# Clone repository
git clone https://github.com/gpad1234/agentic-python-getting-started.git
cd agentic-python-getting-started

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install optional packages
pip install langchain langgraph langchain-anthropic pytest pytest-asyncio
```

### Step 7: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
# Add: ANTHROPIC_API_KEY=your_key_here
# Add: OPENAI_API_KEY=your_key_here (optional)
```

### Step 8: Verify Installation
```bash
# Run critical tests
python -m pytest \
  tests/test_mcp_server.py::TestMCPServer::test_list_tools \
  tests/test_security.py::TestAuditLogger::test_log_security_violation \
  tests/test_workflow_builder.py::TestWorkflowBuilder::test_workflow_validation \
  tests/test_integration.py::TestSystemIntegration::test_full_mcp_request_flow \
  -v

# Should see: 4 passed in ~0.7s
```

## WSL-Specific Configuration

### File System Access
```bash
# Windows files accessible at /mnt/c/
/mnt/c/Users/YourUsername/Documents

# Linux home directory
/home/username/

# Project location (recommended)
/home/username/projects/agentic-python-getting-started
```

### Network Configuration
```bash
# WSL2 uses Hyper-V virtual network
# To access services from Windows:
# - Use localhost from Windows for WSL services
# - Use WSL's IP for Windows-to-WSL (run: hostname -I)

# Check WSL IP
hostname -I

# Example: If WSL IP is 172.31.x.x
# Windows can access MCP server at: http://172.31.x.x:port
```

### Performance Tips
```bash
# Store project on WSL filesystem (not /mnt)
# WSL filesystem: /home/username/
# Windows filesystem: /mnt/c/Users/...
# (WSL filesystem is ~5x faster)

# Create .wslconfig in Windows home for optimization
# C:\Users\YourUsername\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=4GB
```

## Troubleshooting

### Issue: osquery not found
```bash
# Reinstall
sudo apt-get install --reinstall osquery

# Verify path
which osqueryi
```

### Issue: Python package installation fails
```bash
# Install build dependencies
sudo apt-get install -y python3-dev python3-distutils

# Retry pip install
pip install -r requirements.txt
```

### Issue: Permission denied on scripts
```bash
# Add execute permission
chmod +x *.py

# Or run directly
python3 script.py
```

### Issue: Port conflicts (if running server)
```bash
# Check listening ports
sudo netstat -tlnp

# WSL2 ports should be accessible via localhost from Windows
```

## Usage After Migration

### Daily Development
```bash
# Open WSL terminal (or from VS Code)
# cd /home/username/projects/agentic-python-getting-started
cd ~/projects/agentic-python-getting-started

# Activate environment
source venv/bin/activate

# Run tests
python run_tests.py

# Start MCP server
python -m mcp_osquery_server.server

# Demo mode
python demo_osquery_server.py
```

### Accessing from Windows
```bash
# VS Code Remote - WSL extension
# From VS Code: Ctrl+Shift+P > Remote-WSL: Open Folder in WSL

# Command line from PowerShell
wsl python ~/projects/agentic-python-getting-started/main.py

# Direct WSL command
wsl python -m mcp_osquery_server.server
```

## IDE Integration

### VS Code (Recommended)
```
1. Install "Remote - WSL" extension
2. Open folder in WSL
3. Select Python interpreter from WSL venv
4. Terminal automatically uses WSL
```

### PyCharm
```
1. Settings > Project > Python Interpreter
2. Add New Interpreter > WSL
3. Select Ubuntu distribution
4. Select venv path: /home/username/projects/.../venv
```

### Cursor
```
1. Same as VS Code (shares Remote extensions)
```

## File Synchronization

### One-way sync from Windows to WSL
```bash
# In WSL terminal
rsync -av /mnt/c/Users/YourUsername/source/ ~/destination/

# Or use git
git clone https://github.com/your-repo.git
```

### Two-way sync
```bash
# Install syncthing or use git for version control
# (Recommended approach)
```

## Performance Metrics

### Expected Performance (WSL2)
- Project setup: 2-5 minutes
- First test run: 30-60 seconds
- osquery queries: 0.5-2 seconds
- API calls: Depends on network

### Optimization Checklist
- [ ] Project on /home filesystem (not /mnt)
- [ ] 8GB+ RAM allocated
- [ ] SSD storage
- [ ] Windows Defender excluded from WSL folders
- [ ] .wslconfig optimized

## Migration Complete Checklist

- [ ] WSL2 installed and Ubuntu selected
- [ ] Python 3.12+ installed
- [ ] osquery installed and verified
- [ ] Project cloned to /home directory
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API keys configured in .env
- [ ] Critical tests passing (4/4)
- [ ] IDE configured (VS Code/PyCharm)
- [ ] Project accessible from IDE

## Quick Start Command (All-in-one for WSL)

```bash
# Run this after opening new WSL terminal
cd ~/projects/agentic-python-getting-started && \
source venv/bin/activate && \
python -m pytest tests/test_mcp_server.py::TestMCPServer::test_list_tools -v
```

## Support

For issues:
1. Check WSL logs: `wsl --update`
2. Verify osquery: `osqueryi --version`
3. Check Python: `python3 --version`
4. Review .env configuration
5. Run tests: `python run_tests.py`

---

**Last Updated**: November 30, 2025  
**Status**: ✅ WSL2 Ready  
**Tested On**: Windows 11 + Ubuntu 22.04 LTS
