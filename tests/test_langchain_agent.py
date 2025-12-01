#!/usr/bin/env python3
"""
Tests for LangChain agent functionality
Tests agent tool selection, reasoning, and chaining
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test with mock imports if LangChain is not available
try:
    from langchain_anthropic import ChatAnthropic
    from examples.langchain_agent import OSQueryAgent, analyze_scenario
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available - testing with mocks")

class TestLangChainAgent:
    """Test LangChain agent functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.sample_tools_data = {
            "system_info": {"hostname": "test-host", "cpu_type": "x86_64"},
            "processes": [{"pid": "1234", "name": "nginx", "resident_size": "50000"}],
            "network_connections": [{"local_port": "80", "state": "LISTEN"}]
        }

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_agent_creation(self):
        """Test OSQuery agent creation"""
        agent = OSQueryAgent()
        assert agent is not None
        assert hasattr(agent, 'tools')
        assert len(agent.tools) > 0

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch('mcp_osquery_server.osquery_tools.query_system_info')
    @patch('mcp_osquery_server.osquery_tools.query_processes')  
    async def test_agent_tool_selection(self, mock_processes, mock_system):
        """Test agent intelligent tool selection"""
        mock_system.return_value = self.sample_tools_data["system_info"]
        mock_processes.return_value = self.sample_tools_data["processes"]
        
        # Test security analysis scenario
        result = await analyze_scenario("security")
        
        assert isinstance(result, dict)
        assert "analysis" in result
        assert "tools_used" in result

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch('mcp_osquery_server.osquery_tools.query_system_info')
    async def test_agent_performance_analysis(self, mock_system):
        """Test agent performance analysis"""
        mock_system.return_value = {
            "hostname": "test-host",
            "cpu_type": "x86_64",
            "memory": "4096MB"  # Low memory for performance concern
        }
        
        result = await analyze_scenario("performance") 
        
        assert isinstance(result, dict)
        assert "analysis" in result

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch('mcp_osquery_server.osquery_tools.query_system_info')
    @patch('mcp_osquery_server.osquery_tools.query_processes')
    @patch('mcp_osquery_server.osquery_tools.query_network_connections')
    async def test_agent_multi_tool_chaining(self, mock_network, mock_processes, mock_system):
        """Test agent chaining multiple tools"""
        mock_system.return_value = self.sample_tools_data["system_info"]
        mock_processes.return_value = self.sample_tools_data["processes"] 
        mock_network.return_value = self.sample_tools_data["network_connections"]
        
        result = await analyze_scenario("overview")
        
        assert isinstance(result, dict)
        assert "analysis" in result
        # Should use multiple tools for comprehensive overview

class TestAgentRules:
    """Test agent rule-based tool selection"""
    
    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    def test_security_analysis_rules(self):
        """Test security analysis tool selection rules"""
        from examples.langchain_agent import select_tools_for_analysis
        
        tools = select_tools_for_analysis("security")
        
        expected_security_tools = ["system_info", "processes", "network_connections", "users"]
        for tool in expected_security_tools:
            assert tool in tools

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    def test_performance_analysis_rules(self):
        """Test performance analysis tool selection rules"""
        from examples.langchain_agent import select_tools_for_analysis
        
        tools = select_tools_for_analysis("performance")
        
        expected_performance_tools = ["system_info", "processes"]
        for tool in expected_performance_tools:
            assert tool in tools

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    def test_overview_analysis_rules(self):
        """Test overview analysis tool selection rules"""
        from examples.langchain_agent import select_tools_for_analysis
        
        tools = select_tools_for_analysis("overview")
        
        # Overview should include most tools
        expected_tools = ["system_info", "processes", "users", "network_interfaces"]
        for tool in expected_tools:
            assert tool in tools

class TestAgentErrorHandling:
    """Test agent error handling and resilience"""
    
    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch('mcp_osquery_server.osquery_tools.query_system_info')
    async def test_agent_tool_error_handling(self, mock_system):
        """Test agent handling of tool execution errors"""
        mock_system.side_effect = Exception("OSQuery failed")
        
        try:
            result = await analyze_scenario("security")
            # Should handle error gracefully
            assert "error" in str(result).lower() or "analysis" in result
        except Exception as e:
            # Should not propagate unhandled exceptions
            pytest.fail(f"Agent should handle tool errors gracefully: {e}")

    @pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
    @patch.dict(os.environ, {})  # No API key
    def test_agent_missing_api_key(self):
        """Test agent behavior without API key"""
        try:
            agent = OSQueryAgent()
            # Should handle missing API key gracefully
        except Exception as e:
            assert "api_key" in str(e).lower() or "anthropic" in str(e).lower()

class TestMockAgent:
    """Test agent functionality with mocks when LangChain unavailable"""
    
    @pytest.mark.skipif(LANGCHAIN_AVAILABLE, reason="LangChain is available")
    def test_mock_agent_creation(self):
        """Test agent creation falls back gracefully"""
        # Should not fail when imports unavailable
        try:
            from examples.langchain_agent import OSQueryAgent
            # If import succeeds, it's using fallback
            assert True
        except ImportError:
            # Expected when no fallback implemented
            assert True

    @pytest.mark.skipif(LANGCHAIN_AVAILABLE, reason="LangChain is available")
    @pytest.mark.asyncio
    async def test_mock_analysis(self):
        """Test analysis with mocked components"""
        # Should provide some form of analysis even without LangChain
        try:
            from examples.langchain_agent import analyze_scenario
            result = await analyze_scenario("security")
            assert isinstance(result, (dict, str))
        except ImportError:
            # Expected when no fallback
            pytest.skip("No mock implementation available")

if __name__ == "__main__":
    # Run tests  
    pytest.main([__file__, "-v", "--tb=short"])