import time
import requests
import logging
from gpiozero import LED
from signal import pause

# TODO: Update config_example.py with new AQI thresholds and URL and rename to config.py
try:
    from config import AQI_GOOD_MAX, AQI_CAUTION_MAX, UPDATE_INTERVAL, STATION_URL
except ImportError:
    # Default fallback values if config is missing
    AQI_GOOD_MAX = 50
    AQI_CAUTION_MAX = 100
    UPDATE_INTERVAL = 900 # 15 minutes
    STATION_URL = "https://api.waqi.info/feed/hanoi/?token=YOUR_TOKEN_HERE"

# GPIO pin configuration for relays (BCM numbering)
# Adjust these pins if you wired them differently on the Pi Zero 2W
RED_PIN = 4
YELLOW_PIN = 3
GREEN_PIN = 2

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TrafficLight:
    """Controls a traffic light using three relay pins (via gpiozero)."""

    def __init__(self, red_pin, yellow_pin, green_pin):
        # active_high=False might be needed for some relay modules.
        # Check your relay module specs. Assuming active HIGH for now as per previous code.
        # If relays are active LOW, set active_high=False.
        self.red_light = LED(red_pin)
        self.yellow_light = LED(yellow_pin)
        self.green_light = LED(green_pin)
        self.off()  # Initialize with all lights off

    def red(self):
        """Turn on red light only."""
        self.red_light.on()
        self.yellow_light.off()
        self.green_light.off()

    def yellow(self):
        """Turn on yellow light only."""
        self.red_light.off()
        self.yellow_light.on()
        self.green_light.off()

    def green(self):
        """Turn on green light only."""
        self.red_light.off()
        self.yellow_light.off()
        self.green_light.on()

    def off(self):
        """Turn off all lights."""
        self.red_light.off()
        self.yellow_light.off()
        self.green_light.off()


def fetch_hanoi_aqi():
    """Fetch current AQI data for Hanoi."""
    logging.info("Fetching Hanoi AQI data...")
    try:
        response = requests.get(STATION_URL, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx, 5xx)
        data = response.json()
        
        # WAQI API structure check
        if data.get('status') != 'ok':
            logging.error(f"API returned status: {data.get('status')}")
            return None

        aqi = data.get('data', {}).get('aqi') # Standard WAQI structure: data -> aqi
        
        # Fallback for the Structure in original code if using a different API wrapper
        if aqi is None:
             aqi = data.get('current', {}).get('aqius')

        logging.info(f"AQI data received: {aqi}")
        return aqi
    except requests.exceptions.RequestException as e:
        logging.error(f"AQI fetch error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None


def set_traffic_light_by_aqi(aqi, traffic_light):
    """Set traffic light color based on AQI value."""
    if aqi is None:
        logging.warning("No AQI data available. Keeping previous state.")
        return

    logging.info(f"Current AQI: {aqi}")
    
    # Ensure aqi is an integer/float
    try:
        aqi_val = float(aqi)
    except (ValueError, TypeError):
        logging.error(f"Invalid AQI value: {aqi}")
        return

    if aqi_val <= AQI_GOOD_MAX:
        logging.info("AQI Level: GOOD (Green)")
        traffic_light.green()
    elif aqi_val <= AQI_CAUTION_MAX:
        logging.info("AQI Level: CAUTION (Yellow)")
        traffic_light.yellow()
    else:
        logging.info("AQI Level: UNHEALTHY (Red)")
        traffic_light.red()


def cycle_relays(traffic_light, delay=0.5):
    """Cycle through traffic lights for testing purposes."""
    logging.info("Starting traffic light test cycle...")
    try:
        while True:
            logging.info("RED")
            traffic_light.red()
            time.sleep(delay)

            logging.info("YELLOW")
            traffic_light.yellow()
            time.sleep(delay)

            logging.info("GREEN")
            traffic_light.green()
            time.sleep(delay)

            logging.info("OFF")
            traffic_light.off()
            time.sleep(delay)
    except KeyboardInterrupt:
        logging.info("Stopping test cycle.")
        traffic_light.off()


def main():
    """Main application loop for AQI monitoring."""
    # Initialize traffic light
    traffic_light = TrafficLight(RED_PIN, YELLOW_PIN, GREEN_PIN)

    # Initial test cycle to show system is starting
    logging.info("System starting...")
    for _ in range(3):
        traffic_light.green()
        time.sleep(0.2)
        traffic_light.off()
        time.sleep(0.2)

    logging.info(f"Starting AQI monitoring (update interval: {UPDATE_INTERVAL}s)")

    while True:
        try:
            aqi = fetch_hanoi_aqi()
            
            # If fetch fails (aqi is None), set_traffic_light_by_aqi handles it 
            # by doing nothing (preserving state), which meets the requirement:
            # "if you can't fetch just keep the current light on alwaysss keep 1 light on (the latest one)"
            set_traffic_light_by_aqi(aqi, traffic_light)

            # Wait for next update
            time.sleep(UPDATE_INTERVAL)

        except KeyboardInterrupt:
            logging.info("Shutting down...")
            traffic_light.off()
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in main loop: {e}")
            # Wait a bit before retrying to avoid spamming if there's a persistent error
            time.sleep(60) 


if __name__ == "__main__":
    main()
