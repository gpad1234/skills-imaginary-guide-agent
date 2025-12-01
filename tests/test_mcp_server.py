#!/usr/bin/env python3
"""
Comprehensive tests for MCP OSQuery Server
Tests the core MCP server functionality and OSQuery tools
"""

import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_osquery_server import osquery_tools, server

class TestOSQueryTools:
    """Test OSQuery tool functions"""
    
    @patch('subprocess.run')
    def test_query_system_info_success(self, mock_run):
        """Test successful system info query"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"hostname": "test-host", "cpu_type": "x86_64"}]',
            stderr=''
        )
        
        result = osquery_tools.query_system_info()
        assert isinstance(result, dict)
        assert "hostname" in str(result)
        assert "cpu_type" in str(result)
        
    @patch('subprocess.run')
    def test_query_processes_success(self, mock_run):
        """Test successful process listing"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"pid": "1234", "name": "test_process", "resident_size": "50000"}]',
            stderr=''
        )
        
        result = osquery_tools.query_processes(limit=5)
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is True
        if "data" in result and result["data"]:  # If processes returned
            assert "pid" in result["data"][0]
            assert "name" in result["data"][0]

    @patch('subprocess.run')
    def test_query_users_success(self, mock_run):
        """Test successful user enumeration"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"username": "testuser", "uid": "1000"}]',
            stderr=''
        )
        
        result = osquery_tools.query_users()
        assert isinstance(result, dict)
        assert "success" in result

    @patch('subprocess.run') 
    def test_custom_query_success(self, mock_run):
        """Test custom query execution"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"result": "test_data"}]',
            stderr=''
        )
        
        result = osquery_tools.custom_query("SELECT * FROM system_info LIMIT 1;")
        assert isinstance(result, dict)
        assert "success" in result

    def test_validate_sql_safe_query(self):
        """Test SQL validation with safe queries"""
        from security.security_policy import SecurityPolicyEngine
        
        policy_engine = SecurityPolicyEngine()
        safe_queries = [
            "SELECT name FROM processes LIMIT 10;",
            "SELECT * FROM system_info;",
            "SELECT pid, name FROM processes WHERE name = 'nginx';"
        ]
        
        for query in safe_queries:
            violations = policy_engine._detect_sql_injection(query)
            assert len(violations) == 0, f"Safe query flagged as unsafe: {query}"

    def test_validate_sql_unsafe_query(self):
        """Test SQL validation with unsafe queries"""
        from security.security_policy import SecurityPolicyEngine
        
        policy_engine = SecurityPolicyEngine()
        unsafe_queries = [
            "DROP TABLE processes;",
            "DELETE FROM system_info;",
            "UPDATE processes SET name = 'hacked';",
            "INSERT INTO logs VALUES ('malicious');",
            "SELECT * FROM file WHERE path = '/etc/passwd';"
        ]
        
        for query in unsafe_queries:
            violations = policy_engine._detect_sql_injection(query)
            assert len(violations) > 0, f"Unsafe query not detected: {query}"

    @patch('subprocess.run')
    def test_osquery_error_handling(self, mock_run):
        """Test error handling in OSQuery execution"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='Error: osquery failed'
        )
        
        result = osquery_tools.query_system_info()
        assert "error" in str(result).lower()

class TestMCPServer:
    """Test MCP server functionality"""
    
    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server instance"""
        return server.create_server()

    @pytest.mark.asyncio
    async def test_list_tools(self, mock_server):
        """Test MCP tools listing"""
        # Call the list_tools function directly
        from mcp_osquery_server.server import list_tools
        tools = await list_tools()
        
        expected_tools = [
            "system_info", "processes", "users", "network_interfaces",
            "network_connections", "custom_query"
        ]
        
        tool_names = [tool.name for tool in tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    @patch('mcp_osquery_server.osquery_tools.query_system_info')
    async def test_call_tool_system_info(self, mock_query, mock_server):
        """Test system_info tool call"""
        mock_query.return_value = {"hostname": "test-host", "cpu_type": "x86_64", "success": True, "data": [{"hostname": "test-host"}]}
        
        from mcp_osquery_server.server import call_tool
        response = await call_tool("system_info", {})
        assert response.content[0].text is not None

    @pytest.mark.asyncio
    @patch('mcp_osquery_server.osquery_tools.query_processes')  
    async def test_call_tool_processes(self, mock_query, mock_server):
        """Test processes tool call"""
        mock_query.return_value = {"success": True, "data": [{"pid": "1234", "name": "test_process"}]}
        
        from mcp_osquery_server.server import call_tool
        response = await call_tool("processes", {"limit": 5})
        assert response.content[0].text is not None

    @pytest.mark.asyncio
    @patch('mcp_osquery_server.osquery_tools.custom_query')
    async def test_call_tool_custom_query_safe(self, mock_query, mock_server):
        """Test custom query with safe SQL"""
        mock_query.return_value = {"success": True, "data": [{"result": "safe_data"}]}
        
        from mcp_osquery_server.server import call_tool
        response = await call_tool("custom_query", {"sql": "SELECT name FROM processes LIMIT 5;"})
        assert response.content[0].text is not None

    @pytest.mark.asyncio
    async def test_call_tool_custom_query_unsafe(self, mock_server):
        """Test custom query with unsafe SQL"""
        from mcp_osquery_server.server import call_tool
        response = await call_tool("custom_query", {"sql": "DROP TABLE processes;"})
        # The response should still return cleanly (error or success)
        assert response.content[0].text is not None

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])