#!/usr/bin/env python3
"""
Quick test to verify the fixes work
"""

import subprocess
import sys

print("🧪 Testing fixes for the 4 failing tests...\n")

# Test 1: MCP Server Core - test_list_tools
print("1️⃣  Testing MCP Server Core (test_list_tools)...")
result = subprocess.run(
    ["python", "-m", "pytest", "tests/test_mcp_server.py::TestMCPServer::test_list_tools", "-v"],
    capture_output=True,
    text=True
)
if "PASSED" in result.stdout:
    print("   ✅ PASSED\n")
else:
    print(f"   ❌ FAILED\n{result.stdout}\n")

# Test 2: Security Components - test_log_security_violation
print("2️⃣  Testing Security Components (test_log_security_violation)...")
result = subprocess.run(
    ["python", "-m", "pytest", "tests/test_security.py::TestAuditLogger::test_log_security_violation", "-v"],
    capture_output=True,
    text=True
)
if "PASSED" in result.stdout:
    print("   ✅ PASSED\n")
else:
    print(f"   ❌ FAILED\n{result.stdout}\n")

# Test 3: Workflow Builder - test_workflow_validation
print("3️⃣  Testing Workflow Builder (test_workflow_validation)...")
result = subprocess.run(
    ["python", "-m", "pytest", "tests/test_workflow_builder.py::TestWorkflowBuilder::test_workflow_validation", "-v"],
    capture_output=True,
    text=True
)
if "PASSED" in result.stdout:
    print("   ✅ PASSED\n")
else:
    print(f"   ❌ FAILED\n{result.stdout}\n")

# Test 4: Integration Tests - test_full_mcp_request_flow
print("4️⃣  Testing Integration (test_full_mcp_request_flow)...")
result = subprocess.run(
    ["python", "-m", "pytest", "tests/test_integration.py::TestSystemIntegration::test_full_mcp_request_flow", "-v"],
    capture_output=True,
    text=True
)
if "PASSED" in result.stdout:
    print("   ✅ PASSED\n")
else:
    print(f"   ❌ FAILED\n{result.stdout}\n")

print("✨ Test verification complete!")
