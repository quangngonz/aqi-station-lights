"""
Flask Backend for Remote Pico W Control
========================================
Simple REST API for commanding Raspberry Pi Pico W devices remotely.
Designed for free hosting on PythonAnywhere, Render, or Vercel.

Endpoints:
- GET  /command?token=SECRET → Returns pending action
- POST /command?token=SECRET → Sets action (JSON: {"action": "refresh"|"restart"|"none"})
- GET  /status?token=SECRET  → Returns last reported device status
- POST /status?token=SECRET  → Device reports its status (JSON: {"aqi": 123, "timestamp": 1234567890})

Security: Shared secret token via query parameter
Storage: In-memory (resets on server restart - good for free tier)
"""

from flask import Flask, request, jsonify
import os
import time
from datetime import datetime

app = Flask(__name__)

# Security: Load token from environment variable or use default for testing
SECRET_TOKEN = os.environ.get('PICO_API_TOKEN', 'your-secret-token-change-me')

# In-memory storage (resets on server restart)
current_command = {
    "action": "none",  # Can be: "none", "refresh", "restart"
    "timestamp": time.time()
}

device_status = {
    "aqi": None,
    "timestamp": None,
    "last_update": None
}


def verify_token():
    """Verify the secret token from query parameters."""
    token = request.args.get('token', '')
    if token != SECRET_TOKEN:
        return False
    return True


@app.route('/')
def index():
    """Simple landing page."""
    return jsonify({
        "service": "Pico W Remote Control API",
        "status": "running",
        "endpoints": ["/command", "/status"],
        "note": "All endpoints require ?token=SECRET"
    })


@app.route('/command', methods=['GET', 'POST'])
def command():
    """
    GET: Device polls for pending command
    POST: User/admin sets new command
    """
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        # Device is polling for command
        return jsonify({
            "action": current_command["action"],
            "timestamp": current_command["timestamp"]
        })

    elif request.method == 'POST':
        # User is setting a new command
        data = request.get_json()

        if not data or 'action' not in data:
            return jsonify({"error": "Missing 'action' in request body"}), 400

        action = data['action']

        # Validate action
        if action not in ['none', 'refresh', 'restart']:
            return jsonify({"error": "Invalid action. Must be: none, refresh, or restart"}), 400

        # Set the command
        current_command['action'] = action
        current_command['timestamp'] = time.time()

        return jsonify({
            "message": f"Command set to '{action}'",
            "command": current_command
        })


@app.route('/status', methods=['GET', 'POST'])
def status():
    """
    GET: Query current device status
    POST: Device reports its status
    """
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        # User is querying device status
        if device_status['aqi'] is None:
            return jsonify({
                "message": "No status reported yet",
                "status": device_status
            })

        # Calculate age of status
        age_seconds = None
        if device_status['last_update']:
            age_seconds = time.time() - device_status['last_update']

        return jsonify({
            "aqi": device_status['aqi'],
            "timestamp": device_status['timestamp'],
            "last_update": device_status['last_update'],
            "age_seconds": age_seconds,
            "readable_time": datetime.fromtimestamp(device_status['timestamp']).isoformat() if device_status['timestamp'] else None
        })

    elif request.method == 'POST':
        # Device is reporting status
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing status data"}), 400

        # Update device status
        device_status['aqi'] = data.get('aqi')
        device_status['timestamp'] = data.get('timestamp', time.time())
        device_status['last_update'] = time.time()

        return jsonify({
            "message": "Status updated",
            "status": device_status
        })


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    })


# For local testing
if __name__ == '__main__':
    print("=" * 50)
    print("Pico W Remote Control Backend")
    print("=" * 50)
    print(f"SECRET_TOKEN: {SECRET_TOKEN}")
    print("Change token via environment variable: PICO_API_TOKEN")
    print("=" * 50)

    # Run on all interfaces for local testing
    app.run(host='0.0.0.0', port=5000, debug=True)
