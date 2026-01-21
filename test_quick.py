"""
Quick test to run all WebSocket tests.
"""

import subprocess
import sys

def run_test(test_file):
    """Run a test file and return success."""
    print(f"\n▶️  Running {test_file}...")
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    
    return result.returncode == 0

def main():
    """Run all WebSocket tests."""
    print("🧪 WebSocket System Tests")
    print("=" * 50)
    
    tests = [
        "test_websocket_server.py",
        "test_eventbus_websocket.py", 
        "test_streamlit_client.py",
        "test_integration.py"
    ]
    
    passed = 0
    failed = 0
    
    for test_file in tests:
        if run_test(test_file):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! WebSocket system is ready.")
    else:
        print(f"💥 {failed} tests failed. Check issues above.")
    
    exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()