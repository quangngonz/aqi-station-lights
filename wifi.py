import network
import time
from config import SSID, PASSWORD

# Connection settings
MAX_WAIT = 20
RETRY_INTERVAL = 0.5


def scan_networks():
    """Scan for available Wi-Fi networks and return list of SSIDs."""
    print("Scanning for Wi-Fi networks...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()

    ssids = []
    for net in networks:
        ssid = net[0].decode('utf-8')
        ssids.append(ssid)
        print(f"Found network: {ssid}")

    return ssids, wlan


def connect_wifi(ssid=SSID, password=PASSWORD, max_wait=MAX_WAIT):
    """Connect to Wi-Fi network and return connection status."""
    ssids, wlan = scan_networks()

    if ssid not in ssids:
        print(f"Network '{ssid}' not found.")
        return False

    print(f"Connecting to '{ssid}'...")
    wlan.connect(ssid, password)

    # Wait for connection
    for _ in range(max_wait):
        if wlan.isconnected():
            print("Connected!")
            print(f"IP address: {wlan.ifconfig()[0]}")
            return True
        time.sleep(RETRY_INTERVAL)

    print("Failed to connect to Wi-Fi.")
    return False


if __name__ == "__main__":
    connect_wifi()
