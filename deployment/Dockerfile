# MCP OSQuery Server
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install OSQuery
RUN curl -L https://pkg.osquery.io/deb/osquery_5.12.0-1.linux_x86_64.deb -o osquery.deb \
    && dpkg -i osquery.deb \
    && rm osquery.deb

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional LangChain dependencies
RUN pip install --no-cache-dir langchain langgraph

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -s /bin/bash osquery && \
    chown -R osquery:osquery /app

USER osquery

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from mcp_osquery_server import osquery_tools; osquery_tools.get_client()" || exit 1

# Default command - MCP Server
CMD ["python", "-m", "mcp_osquery_server.server"]

# Metadata
LABEL maintainer="OSQuery MCP Team" \
      version="1.0.0" \
      description="MCP OSQuery Server with LangChain/LangGraph support"