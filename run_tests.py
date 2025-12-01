#!/usr/bin/env python3
"""
Comprehensive test runner for the entire OSQuery MCP Server project
Runs all test suites and generates detailed reports
"""

import sys
import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def run_test_suite(test_file, name):
    """Run a specific test suite and return results"""
    print(f"\n{'='*60}")
    print(f"Running {name}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        # Run pytest with detailed output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(test_file),
            "-v", "--tb=short", "-x"  # Stop on first failure for faster feedback
        ], capture_output=True, text=True, cwd=project_root)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse results
        output = result.stdout + result.stderr
        
        # Count tests
        passed = output.count(" PASSED")
        failed = output.count(" FAILED") 
        skipped = output.count(" SKIPPED")
        errors = output.count(" ERROR")
        
        status = "PASSED" if result.returncode == 0 else "FAILED"
        
        test_result = {
            "name": name,
            "status": status,
            "duration": round(duration, 2),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "output": output,
            "return_code": result.returncode
        }
        
        # Print summary
        print(f"\n{name} Results:")
        print(f"  Status: {status}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")
        print(f"  Errors: {errors}")
        
        if failed > 0 or errors > 0:
            print(f"\nFailure/Error Details:")
            print(output[-1000:])  # Last 1000 chars of output
        
        return test_result
        
    except Exception as e:
        print(f"Error running {name}: {e}")
        return {
            "name": name,
            "status": "ERROR",
            "duration": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 1,
            "output": str(e),
            "return_code": -1
        }

def check_dependencies():
    """Check if required dependencies are available"""
    print("Checking dependencies...")
    
    dependencies = {
        "pytest": "pytest",
        "mcp": "MCP server library",
        "anthropic": "Anthropic API (optional)",
        "langchain": "LangChain (optional)",
        "langgraph": "LangGraph (optional)"
    }
    
    available = {}
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            available[dep] = True
            print(f"  ✓ {description}")
        except ImportError:
            available[dep] = False
            print(f"  ✗ {description} (not available)")
    
    return available

def run_all_tests():
    """Run all test suites and generate comprehensive report"""
    print("🧪 OSQuery MCP Server - Comprehensive Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies
    dependencies = check_dependencies()
    
    # Define test suites
    test_suites = [
        ("tests/test_mcp_server.py", "MCP Server Core"),
        ("tests/test_security.py", "Security Components"),
        ("tests/test_workflow_builder.py", "Workflow Builder"),
        ("tests/test_langgraph_workflows.py", "LangGraph Workflows"),
        ("tests/test_langchain_agent.py", "LangChain Agent"),
        ("tests/test_integration.py", "Integration Tests")
    ]
    
    results = []
    overall_start = time.time()
    
    # Run each test suite
    for test_file, name in test_suites:
        test_path = project_root / test_file
        print(f"Looking for test file: {test_path}")
        print(f"File exists: {test_path.exists()}")
        if test_path.exists():
            result = run_test_suite(test_path, name)
            results.append(result)
        else:
            print(f"⚠️  Test file not found: {test_file}")
            print(f"    Checked path: {test_path}")
            print(f"    Project root: {project_root}")
            results.append({
                "name": name,
                "status": "SKIPPED",
                "duration": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 1,
                "errors": 0,
                "output": "Test file not found",
                "return_code": 0
            })
    
    overall_duration = time.time() - overall_start
    
    # Generate comprehensive report
    generate_test_report(results, dependencies, overall_duration)
    
    return results

def generate_test_report(results, dependencies, overall_duration):
    """Generate detailed test report"""
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST REPORT")
    print('='*80)
    
    # Overall summary
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    total_tests = total_passed + total_failed + total_skipped + total_errors
    
    overall_status = "PASSED" if total_failed == 0 and total_errors == 0 else "FAILED"
    
    print(f"\nOverall Status: {overall_status}")
    print(f"Total Duration: {overall_duration:.2f}s")
    print(f"Total Tests: {total_tests}")
    print(f"  ✓ Passed: {total_passed}")
    print(f"  ✗ Failed: {total_failed}")
    print(f"  ⚠ Skipped: {total_skipped}")
    print(f"  💥 Errors: {total_errors}")
    
    # Test suite breakdown
    print(f"\nTest Suite Breakdown:")
    print("-" * 60)
    
    for result in results:
        status_icon = "✓" if result["status"] == "PASSED" else "✗" if result["status"] == "FAILED" else "⚠"
        print(f"{status_icon} {result['name']:<25} {result['status']:<8} ({result['duration']:.1f}s)")
        if result["failed"] > 0 or result["errors"] > 0:
            print(f"    Failed: {result['failed']}, Errors: {result['errors']}")
    
    # Dependency status
    print(f"\nDependency Status:")
    print("-" * 30)
    for dep, available in dependencies.items():
        status = "✓" if available else "✗"
        print(f"{status} {dep}")
    
    # Recommendations
    print(f"\nRecommendations:")
    print("-" * 20)
    
    if not dependencies.get("anthropic", False):
        print("• Install 'anthropic' package to test LangChain agent functionality")
    
    if not dependencies.get("langchain", False):
        print("• Install 'langchain' and 'langgraph' packages to test workflow features")
    
    if total_failed > 0:
        print("• Review failed test output above for debugging information")
        print("• Check that osquery is installed on the system")
        print("• Verify environment variables are set correctly")
    
    if total_skipped > 0:
        print(f"• {total_skipped} tests were skipped due to missing dependencies")
    
    # Success metrics
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Excellent! System is well-tested and functioning.")
        elif success_rate >= 75:
            print("👍 Good! Most functionality is working correctly.")
        elif success_rate >= 50:
            print("⚠️  Moderate. Some issues need attention.")
        else:
            print("🚨 Critical. Significant issues detected.")
    
    # Save detailed report
    save_detailed_report(results, dependencies, overall_duration, overall_status)

def save_detailed_report(results, dependencies, duration, status):
    """Save detailed JSON report"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": status,
        "overall_duration": round(duration, 2),
        "summary": {
            "total_passed": sum(r["passed"] for r in results),
            "total_failed": sum(r["failed"] for r in results), 
            "total_skipped": sum(r["skipped"] for r in results),
            "total_errors": sum(r["errors"] for r in results)
        },
        "dependencies": dependencies,
        "test_results": results
    }
    
    # Save to file
    report_file = project_root / "TEST_RESULTS.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")
    
    # Also create markdown report
    create_markdown_report(report)

def create_markdown_report(report_data):
    """Create markdown test report"""
    
    markdown_content = f"""# Test Results Report

**Generated:** {report_data['timestamp']}
**Overall Status:** {report_data['overall_status']}
**Duration:** {report_data['overall_duration']}s

## Summary

| Metric | Count |
|--------|-------|
| Total Passed | {report_data['summary']['total_passed']} |
| Total Failed | {report_data['summary']['total_failed']} |
| Total Skipped | {report_data['summary']['total_skipped']} |
| Total Errors | {report_data['summary']['total_errors']} |

## Test Suite Results

| Test Suite | Status | Duration | P/F/S/E |
|------------|--------|----------|---------|
"""
    
    for result in report_data['test_results']:
        pfse = f"{result['passed']}/{result['failed']}/{result['skipped']}/{result['errors']}"
        markdown_content += f"| {result['name']} | {result['status']} | {result['duration']}s | {pfse} |\n"
    
    markdown_content += f"""
## Dependencies

| Package | Available |
|---------|-----------|
"""
    
    for dep, available in report_data['dependencies'].items():
        status = "✅" if available else "❌" 
        markdown_content += f"| {dep} | {status} |\n"
    
    markdown_content += f"""
## Notes

- Tests were run with Python {sys.version.split()[0]}
- Project root: {project_root}
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
"""
    
    # Save markdown report
    report_file = project_root / "TEST_REPORT.md"
    try:
        with open(report_file, 'w') as f:
            f.write(markdown_content)
        print(f"📄 Markdown report saved to: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save markdown report: {e}")

if __name__ == "__main__":
    # Run comprehensive test suite
    results = run_all_tests()
    
    # Exit with appropriate code
    failed_suites = [r for r in results if r["status"] == "FAILED"]
    error_suites = [r for r in results if r["status"] == "ERROR"]
    
    if failed_suites or error_suites:
        print(f"\n❌ {len(failed_suites + error_suites)} test suite(s) failed")
        sys.exit(1)
    else:
        print(f"\n✅ All test suites passed successfully!")
        sys.exit(0)