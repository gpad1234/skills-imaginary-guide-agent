# Test Results Report

**Generated:** 2025-11-30T22:15:28.539688
**Overall Status:** FAILED
**Duration:** 11.25s

## Summary

| Metric | Count |
|--------|-------|
| Total Passed | 27 |
| Total Failed | 3 |
| Total Skipped | 18 |
| Total Errors | 0 |

## Test Suite Results

| Test Suite | Status | Duration | P/F/S/E |
|------------|--------|----------|---------|
| MCP Server Core | PASSED | 2.35s | 12/0/0/0 |
| Security Components | FAILED | 1.34s | 3/1/0/0 |
| Workflow Builder | FAILED | 1.33s | 6/1/0/0 |
| LangGraph Workflows | PASSED | 1.72s | 3/0/7/0 |
| LangChain Agent | PASSED | 2.63s | 1/0/10/0 |
| Integration Tests | FAILED | 1.87s | 2/1/1/0 |

## Dependencies

| Package | Available |
|---------|-----------|
| pytest | ✅ |
| mcp | ✅ |
| anthropic | ✅ |
| langchain | ✅ |
| langgraph | ✅ |

## Notes

- Tests were run with Python 3.12.7
- Project root: /Users/gp/python/agentic/agentic-python-getting-started-main
- Some tests may be skipped due to missing optional dependencies
- For full functionality, install: `pip install langchain langgraph anthropic`

## Test Coverage

The test suite covers:

- ✅ MCP Server core functionality
- ✅ OSQuery tool integration  
- ✅ Security components (RBAC, audit, rate limiting)
- ✅ Workflow builder and visual design
- ✅ LangChain/LangGraph integration (when available)
- ✅ Error handling and edge cases
- ✅ Integration and performance testing
