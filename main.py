
import time
import machine
import requests
import wifi
import _thread
import socket
import remote_control

# TODO: Update config_example.py with new AQI thresholds and URL and rename to config.py
from config import (
    AQI_GOOD_MAX, AQI_CAUTION_MAX, UPDATE_INTERVAL, STATION_URL, WEB_SERVER_PORT,
    BACKEND_URL, BACKEND_TOKEN, BACKEND_POLL_INTERVAL, ENABLE_REMOTE_CONTROL
)

# Global state for caching and control
last_aqi = None
last_successful_fetch = None
restart_requested = False
last_backend_poll = 0

# GPIO pin configuration for relays
RELAY_PINS = [4, 3, 2]  # [Red, Yellow, Green]


class TrafficLight:
    """Controls a traffic light using three relay pins."""

    def __init__(self, red_pin, yellow_pin, green_pin):
        self.red_light = machine.Pin(red_pin, machine.Pin.OUT)
        self.yellow_light = machine.Pin(yellow_pin, machine.Pin.OUT)
        self.green_light = machine.Pin(green_pin, machine.Pin.OUT)
        self.off()  # Initialize with all lights off

    def red(self):
        """Turn on red light only."""
        self.red_light.value(1)
        self.yellow_light.value(0)
        self.green_light.value(0)

    def yellow(self):
        """Turn on yellow light only."""
        self.red_light.value(0)
        self.yellow_light.value(1)
        self.green_light.value(0)

    def green(self):
        """Turn on green light only."""
        self.red_light.value(0)
        self.yellow_light.value(0)
        self.green_light.value(1)

    def off(self):
        """Turn off all lights."""
        self.red_light.value(0)
        self.yellow_light.value(0)
        self.green_light.value(0)


def fetch_hanoi_aqi(report_to_backend=False):
    """Fetch current AQI data for Hanoi."""
    global last_aqi, last_successful_fetch

    print("Fetching Hanoi AQI data...")
    try:
        response = requests.get(STATION_URL, timeout=10)
        data = response.json()
        aqi = data.get('current', {}).get('aqius')

        if aqi is not None:
            print(f"AQI data received: {aqi}")
            # Cache successful response
            last_aqi = aqi
            last_successful_fetch = time.time()

            # Report to backend if enabled and requested
            if report_to_backend and ENABLE_REMOTE_CONTROL:
                try:
                    remote_control.report_status_to_backend(
                        BACKEND_URL, BACKEND_TOKEN, aqi, int(
                            last_successful_fetch)
                    )
                    print("Status reported to backend")
                except Exception as e:
                    print(f"Failed to report status: {e}")

            return aqi
        else:
            print("AQI data incomplete, using cached value")
            return last_aqi

    except Exception as e:
        print(f"AQI fetch error: {e}")
        if last_aqi is not None:
            age = time.time() - last_successful_fetch if last_successful_fetch else 0
            print(f"Using cached AQI: {last_aqi} (age: {age:.0f}s)")
        return last_aqi


def set_traffic_light_by_aqi(aqi, traffic_light):
    """Set traffic light color based on AQI value."""
    if aqi is None:
        print("No AQI data available. Turning off traffic light.")
        traffic_light.off()
        return

    print(f"Current AQI: {aqi}")
    if aqi <= AQI_GOOD_MAX:
        print("AQI Level: GOOD (Green)")
        traffic_light.green()
    elif aqi <= AQI_CAUTION_MAX:
        print("AQI Level: CAUTION (Yellow)")
        traffic_light.yellow()
    else:
        print("AQI Level: UNHEALTHY (Red)")
        traffic_light.red()


def web_server(traffic_light):
    """Simple web server for remote control and status."""
    global restart_requested, last_aqi, last_successful_fetch

    addr = socket.getaddrinfo('0.0.0.0', WEB_SERVER_PORT)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print(f"Web server listening on port {WEB_SERVER_PORT}")

    while True:
        try:
            cl, addr = s.accept()
            print(f"Client connected from {addr}")

            request = cl.recv(1024).decode('utf-8')

            if 'GET /refresh' in request:
                response = "HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n"
                response += "<html><body><h1>Refreshing AQI data...</h1><p><a href='/status'>Back to Status</a></p></body></html>"
                cl.send(response.encode())
                cl.close()
                print("AQI refresh requested via web")
                # Trigger immediate refresh
                aqi = fetch_hanoi_aqi(report_to_backend=True)
                set_traffic_light_by_aqi(aqi, traffic_light)

            elif 'GET /restart' in request:
                response = "HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n"
                response += "<html><body><h1>Restarting device...</h1></body></html>"
                cl.send(response.encode())
                cl.close()
                print("Restart requested via web")
                restart_requested = True
                time.sleep(1)
                machine.reset()

            elif 'GET /status' in request:
                age = time.time() - last_successful_fetch if last_successful_fetch else 0
                uptime = time.time()
                remote_status = "Enabled" if ENABLE_REMOTE_CONTROL else "Disabled"
                status = f"""HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n
<html><body>
<h1>Pico W AQI Monitor Status</h1>
<p><b>Current AQI:</b> {last_aqi if last_aqi else 'No data yet'}</p>
<p><b>Last Update:</b> {age:.0f} seconds ago</p>
<p><b>Uptime:</b> {uptime:.0f} seconds</p>
<p><b>Remote Control:</b> {remote_status}</p>
<p><a href='/refresh'>Refresh AQI Now</a> | <a href='/restart'>Restart Device</a></p>
</body></html>"""
                cl.send(status.encode())
            else:
                # Default page
                response = """HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n
<html><body>
<h1>Pico W AQI Monitor</h1>
<p><a href='/status'>View Status</a></p>
<p><a href='/refresh'>Refresh AQI</a></p>
<p><a href='/restart'>Restart Device</a></p>
</body></html>"""
                cl.send(response.encode())
                cl.close()
                cl.send(response.encode())
                cl.close()

        except Exception as e:
            print(f"Web server error: {e}")
            try:
                cl.close()
            except:
                pass


def cycle_relays(delay=0.5):
    """Cycle through traffic lights for testing purposes."""
    traffic_light = TrafficLight(RELAY_PINS[0], RELAY_PINS[1], RELAY_PINS[2])
    print("Starting traffic light test cycle...")

    try:
        while True:
            print("RED")
            traffic_light.red()
            time.sleep(delay)

            print("YELLOW")
            traffic_light.yellow()
            time.sleep(delay)

            print("GREEN")
            traffic_light.green()
            time.sleep(delay)

            print("OFF")
            traffic_light.off()
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nStopping test cycle.")
        traffic_light.off()


def main():
    """Main application loop for AQI monitoring."""
    global restart_requested, last_backend_poll

    # Setup watchdog timer (8 seconds)
    wdt = machine.WDT(timeout=8000)

    # Initialize traffic light first
    traffic_light = TrafficLight(RELAY_PINS[0], RELAY_PINS[1], RELAY_PINS[2])

    # Connect to Wi-Fi - keep trying until successful
    print("Connecting to Wi-Fi...")
    while not wifi.connect_wifi():
        print("Failed to connect. Retrying...")
        traffic_light.yellow()
        time.sleep(0.5)
        traffic_light.red()
        time.sleep(0.5)
        wdt.feed()  # Feed watchdog during connection attempts

    # Flash green light to indicate successful connection
    print("Wi-Fi connected.")
    for _ in range(3):
        traffic_light.green()
        time.sleep(0.2)
        traffic_light.off()
        time.sleep(0.2)

    # Start web server in separate thread
    try:
        _thread.start_new_thread(web_server, (traffic_light,))
        print("Web server started in background")
    except Exception as e:
        print(f"Failed to start web server: {e}")

    last_update = time.time() - UPDATE_INTERVAL

    print(f"Starting AQI monitoring (update interval: {UPDATE_INTERVAL}s)")
    if ENABLE_REMOTE_CONTROL:
        print(
            f"Remote control enabled (poll interval: {BACKEND_POLL_INTERVAL}s)")

    try:
        while True:
            # Feed watchdog to prevent reset
            wdt.feed()

            if restart_requested:
                print("Restart requested, rebooting...")
                machine.reset()

            current_time = time.time()

            # Check backend for remote commands
            if ENABLE_REMOTE_CONTROL and (current_time - last_backend_poll >= BACKEND_POLL_INTERVAL):
                last_backend_poll = current_time

                try:
                    action = remote_control.poll_backend_command(
                        BACKEND_URL, BACKEND_TOKEN)

                    if action == "refresh":
                        print("Remote refresh command received")
                        aqi = fetch_hanoi_aqi(report_to_backend=True)
                        set_traffic_light_by_aqi(aqi, traffic_light)
                        # Clear the command
                        remote_control.clear_backend_command(
                            BACKEND_URL, BACKEND_TOKEN)

                    elif action == "restart":
                        print("Remote restart command received")
                        # Clear command before restart
                        remote_control.clear_backend_command(
                            BACKEND_URL, BACKEND_TOKEN)
                        time.sleep(1)
                        machine.reset()

                except Exception as e:
                    print(f"Remote control error: {e}")

            # Regular AQI update
            if current_time - last_update >= UPDATE_INTERVAL:
                last_update = current_time

                aqi = fetch_hanoi_aqi(report_to_backend=ENABLE_REMOTE_CONTROL)
                set_traffic_light_by_aqi(aqi, traffic_light)

            time.sleep(1)  # Small delay to prevent busy waiting

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Restarting in 5 seconds...")
        time.sleep(5)
        machine.reset()
    finally:
        traffic_light.off()
        print("Traffic light turned off.")


if __name__ == "__main__":
    main()
    # Uncomment below to test traffic light cycling instead
    # cycle_relays()
