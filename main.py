
import time
import machine
import requests
import wifi

# TODO: Update config_example.py with new AQI thresholds and URL and rename to config.py
from config import AQI_GOOD_MAX, AQI_CAUTION_MAX, UPDATE_INTERVAL, STATION_URL

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


def fetch_hanoi_aqi():
    """Fetch current AQI data for Hanoi."""
    print("Fetching Hanoi AQI data...")
    try:
        response = requests.get(STATION_URL, timeout=10)
        data = response.json()
        aqi = data.get('current', {}).get('aqius')
        print(f"AQI data received: {aqi}")
        return aqi
    except Exception as e:
        print(f"AQI fetch error: {e}")
        return None


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

    # Flash green light to indicate successful connection
    print("Wi-Fi connected.")
    for _ in range(3):
        traffic_light.green()
        time.sleep(0.2)
        traffic_light.off()
        time.sleep(0.2)

    last_update = time.time() - UPDATE_INTERVAL

    print(f"Starting AQI monitoring (update interval: {UPDATE_INTERVAL}s)")

    try:
        while True:
            current_time = time.time()

            if current_time - last_update >= UPDATE_INTERVAL:
                last_update = current_time

                aqi = fetch_hanoi_aqi()
                set_traffic_light_by_aqi(aqi, traffic_light)

            time.sleep(1)  # Small delay to prevent busy waiting

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        traffic_light.off()
        print("Traffic light turned off.")


if __name__ == "__main__":
    main()
    # Uncomment below to test traffic light cycling instead
    # cycle_relays()
