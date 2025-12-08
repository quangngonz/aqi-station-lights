"""
Example control script for Pico W device
Use this to control your device from your computer
"""

import requests
import sys

# Configuration - Update these with your values
BACKEND_URL = "https://yourusername.pythonanywhere.com"
TOKEN = "your-secret-token-change-me"


def send_command(action):
    """Send a command to the Pico device."""
    if action not in ['refresh', 'restart', 'none']:
        print(f"Error: Invalid action '{action}'")
        print("Valid actions: refresh, restart, none")
        return False

    url = f"{BACKEND_URL}/command?token={TOKEN}"

    try:
        response = requests.post(
            url,
            json={"action": action},
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Command sent successfully: {data['message']}")
            return True
        elif response.status_code == 401:
            print("✗ Error: Unauthorized. Check your token.")
            return False
        else:
            print(f"✗ Error: Server returned status {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False


def get_status():
    """Get the current device status."""
    url = f"{BACKEND_URL}/status?token={TOKEN}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get('aqi') is None:
                print("No status reported yet.")
            else:
                print(f"\n{'='*50}")
                print("Device Status")
                print(f"{'='*50}")
                print(f"Current AQI: {data['aqi']}")
                print(f"Timestamp: {data.get('readable_time', 'N/A')}")
                print(f"Data age: {data.get('age_seconds', 0):.0f} seconds")
                print(f"{'='*50}\n")
            return True

        elif response.status_code == 401:
            print("✗ Error: Unauthorized. Check your token.")
            return False
        else:
            print(f"✗ Error: Server returned status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False


def check_command():
    """Check what command is currently pending."""
    url = f"{BACKEND_URL}/command?token={TOKEN}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"Pending command: {data['action']}")
            return True
        else:
            print(f"✗ Error: Server returned status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return False


def main():
    """Main command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: python control_pico.py <command>")
        print("\nCommands:")
        print("  refresh  - Trigger AQI data refresh")
        print("  restart  - Restart the device")
        print("  clear    - Clear pending command")
        print("  status   - Get current device status")
        print("  check    - Check pending command")
        print("\nExample:")
        print("  python control_pico.py refresh")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "refresh":
        send_command("refresh")
    elif command == "restart":
        send_command("restart")
    elif command == "clear":
        send_command("none")
    elif command == "status":
        get_status()
    elif command == "check":
        check_command()
    else:
        print(f"Unknown command: {command}")
        print("Use: refresh, restart, clear, status, or check")
        sys.exit(1)


if __name__ == "__main__":
    main()
