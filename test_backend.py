"""
Test script to verify backend is working correctly
Run this BEFORE deploying to your Pico to ensure backend is operational
"""

import requests
import json
import sys

# Configuration - Update these
BACKEND_URL = "https://yourusername.pythonanywhere.com"
TOKEN = "your-secret-token-change-me"


def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test a single endpoint."""
    url = f"{BACKEND_URL}{endpoint}"

    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method}")
    print(f"URL: {url}")

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        else:
            print(f"❌ Unknown method: {method}")
            return False

        print(f"Status Code: {response.status_code}")

        if response.status_code == expected_status:
            print("✅ Status code matches expected")
        else:
            print(f"❌ Expected {expected_status}, got {response.status_code}")
            return False

        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        except:
            print(f"Response (text): {response.text}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot reach backend")
        print("   - Check backend URL is correct")
        print("   - Verify backend is deployed and running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Backend not responding")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run comprehensive backend tests."""
    print("="*60)
    print("Backend API Test Suite")
    print("="*60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Token: {TOKEN[:10]}..." if len(TOKEN) > 10 else f"Token: {TOKEN}")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Index endpoint
    if test_endpoint("Index / Landing Page", "GET", "/"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Command endpoint without token (should fail)
    if test_endpoint(
        "Command without token (should fail)",
        "GET",
        "/command",
        expected_status=401
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Command endpoint with token
    if test_endpoint(
        "Get command with token",
        "GET",
        f"/command?token={TOKEN}"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 4: Set command to refresh
    if test_endpoint(
        "Set command to 'refresh'",
        "POST",
        f"/command?token={TOKEN}",
        data={"action": "refresh"}
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 5: Verify command was set
    if test_endpoint(
        "Verify command is 'refresh'",
        "GET",
        f"/command?token={TOKEN}"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 6: Clear command
    if test_endpoint(
        "Clear command (set to 'none')",
        "POST",
        f"/command?token={TOKEN}",
        data={"action": "none"}
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 7: Report status
    if test_endpoint(
        "Report device status",
        "POST",
        f"/status?token={TOKEN}",
        data={"aqi": 42, "timestamp": 1702123456}
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 8: Get status
    if test_endpoint(
        "Get device status",
        "GET",
        f"/status?token={TOKEN}"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 9: Invalid action (should fail)
    if test_endpoint(
        "Invalid action (should fail)",
        "POST",
        f"/command?token={TOKEN}",
        data={"action": "invalid"},
        expected_status=400
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 10: Health check
    if test_endpoint("Health check", "GET", "/health"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    print("="*60)

    if tests_failed == 0:
        print("\n🎉 All tests passed! Backend is ready for use.")
        print("\nNext steps:")
        print("1. Update config.py on your Pico with:")
        print(f"   BACKEND_URL = \"{BACKEND_URL}\"")
        print(f"   BACKEND_TOKEN = \"{TOKEN}\"")
        print("2. Upload files to your Pico")
        print("3. Monitor serial output to verify connection")
        return True
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying to Pico.")
        print("\nCommon issues:")
        print("- Check BACKEND_URL and TOKEN are correct in this script")
        print("- Verify backend is deployed and running")
        print("- Check environment variable PICO_API_TOKEN matches TOKEN")
        return False


def interactive_test():
    """Interactive mode for manual testing."""
    print("\n" + "="*60)
    print("Interactive Mode")
    print("="*60)
    print("Commands:")
    print("  refresh  - Send refresh command")
    print("  restart  - Send restart command")
    print("  clear    - Clear command")
    print("  status   - Get device status")
    print("  check    - Check pending command")
    print("  quit     - Exit")
    print("="*60)

    while True:
        try:
            cmd = input("\nEnter command: ").strip().lower()

            if cmd == "quit":
                break
            elif cmd == "refresh":
                test_endpoint("Send refresh", "POST", f"/command?token={TOKEN}",
                              data={"action": "refresh"})
            elif cmd == "restart":
                test_endpoint("Send restart", "POST", f"/command?token={TOKEN}",
                              data={"action": "restart"})
            elif cmd == "clear":
                test_endpoint("Clear command", "POST", f"/command?token={TOKEN}",
                              data={"action": "none"})
            elif cmd == "status":
                test_endpoint("Get status", "GET", f"/status?token={TOKEN}")
            elif cmd == "check":
                test_endpoint("Check command", "GET",
                              f"/command?token={TOKEN}")
            else:
                print(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break


def main():
    """Main entry point."""
    if BACKEND_URL == "https://yourusername.pythonanywhere.com":
        print("⚠️  Please update BACKEND_URL in this script first!")
        sys.exit(1)

    if TOKEN == "your-secret-token-change-me":
        print("⚠️  Please update TOKEN in this script first!")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
