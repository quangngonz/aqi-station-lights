"""
Remote control functionality for Pico W
Polls cloud backend for commands and reports status
"""

import requests
import time


def poll_backend_command(backend_url, token):
    """
    Poll the backend for pending commands.
    Returns the action string or None if error.
    """
    try:
        url = f"{backend_url}/command?token={token}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get('action', 'none')
        else:
            print(f"Backend returned status {response.status_code}")
            return None

    except Exception as e:
        print(f"Error polling backend: {e}")
        return None


def clear_backend_command(backend_url, token):
    """
    Clear the backend command by setting it to 'none'.
    """
    try:
        url = f"{backend_url}/command?token={token}"
        response = requests.post(
            url,
            json={"action": "none"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error clearing backend command: {e}")
        return False


def report_status_to_backend(backend_url, token, aqi, timestamp):
    """
    Report device status to backend.
    """
    try:
        url = f"{backend_url}/status?token={token}"
        response = requests.post(
            url,
            json={"aqi": aqi, "timestamp": timestamp},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error reporting status: {e}")
        return False
