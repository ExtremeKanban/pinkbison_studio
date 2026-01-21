"""
Test runner for REAL-TIME WORKFLOW & FEEDBACK verification.

Runs all automated tests and generates a summary report.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text):
    """Print a formatted section."""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80 + "\n")


def run_tests(test_path, description):
    """Run pytest on a specific test file or directory."""
    print_section(description)
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        "-v",
        "--tb=short",
        "-W", "ignore::DeprecationWarning"
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Run all real-time feature tests."""
    print_header("REAL-TIME WORKFLOW & FEEDBACK Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track results
    results = {}
    
    # Layer 1: Unit Tests
    print_header("Layer 1: Unit Tests")
    
    results["WebSocketManager"] = run_tests(
        "tests/realtime_features/test_websocket_manager.py",
        "WebSocketManager Unit Tests"
    )
    
    results["EventBus WebSocket"] = run_tests(
        "tests/realtime_features/test_eventbus_websocket.py",
        "EventBus WebSocket Integration Tests"
    )
    
    # Layer 2: Integration Tests
    print_header("Layer 2: Integration Tests")
    
    results["WebSocket Integration"] = run_tests(
        "tests/realtime_features/test_websocket_integration.py",
        "WebSocket + EventBus Integration Tests"
    )
    
    # Summary
    print_header("Test Results Summary")
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    print("Test Suites:")
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {len(results)} test suites")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ All automated tests passed!")
        print("\nNext Steps:")
        print("1. Run manual UI tests using: tests/manual_testing/manual_test_checklist.md")
        print("2. Start Streamlit and verify real-time features in browser")
        print("3. Document any issues found")
    else:
        print("\n✗ Some tests failed. Review output above for details.")
        print("\nFix failing tests before proceeding to manual testing.")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())