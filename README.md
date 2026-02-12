# AQI Traffic Light System

A Raspberry Pi Pico 2W-based air quality indicator that displays real-time Air Quality Index (AQI) data using a traffic light system. Perfect for schools, offices, and public spaces to provide instant visual feedback about outdoor air quality conditions.

## 🚦 Overview

This project fetches real-time AQI data from monitoring stations and displays air quality levels using a three-color traffic light system:

- 🟢 **Green Light**: Good air quality (AQI ≤ 50) - Safe to play outside
- 🟡 **Yellow Light**: Moderate air quality (AQI 51-150) - Outside activity with caution
- 🔴 **Red Light**: Unhealthy air quality (AQI > 150) - Stay indoors

The traffic lights also provide **WiFi connection status feedback**:
- 🟡🔴 **Flashing Yellow/Red**: Attempting to connect to WiFi
- 🟢 **Flashing Green (3x)**: Successfully connected to WiFi

The system is designed to help schools and institutions make informed decisions about outdoor activities based on current air quality conditions.

## 🔧 Hardware Requirements

- **Raspberry Pi Zero 2W** (or any Raspberry Pi model)
- **3-Channel Relay Module** (5V or 3.3V compatible)
- **Traffic Light** or individual LEDs (Red, Yellow, Green)
- **Micro SD Card** (8GB+ with Raspberry Pi OS)
- **Power Supply** (5V micro USB)
- **Jumper Wires**

## 📋 Wiring Diagram

| Pico Pin | Component | Description |
|----------|-----------|-------------|
| GPIO 4   | Relay 1   | Red Light   |
| GPIO 3   | Relay 2   | Yellow Light|
| GPIO 2   | Relay 3   | Green Light |
| GND      | Relay GND | Ground      |
| 3V3/VBUS | Relay VCC | Power (check your relay voltage)|

## 🚀 Getting Started

### 1. Prerequisites

- Raspberry Pi Zero 2W with Raspberry Pi OS (Legacy or Bookworm)
- Internet connection configured on the Pi (via `raspi-config` or `wpa_supplicant`)

### 2. Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd aqi-lights
    git checkout feature/pi-zero-migration
    ```

2.  **Run Setup Script**
    This script installs dependencies, creates a virtual environment, and sets up the systemd service.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

3.  **Configure Config File**
    Edit `config.py` with your specific AQI Station URL and thresholds.
    ```bash
    nano config.py
    ```
    *Note: Wi-Fi credentials are NOT required in `config.py` as networking is handled by the OS.*

4.  **Restart Service**
    After editing the config, restart the service to apply changes.
    ```bash
    sudo systemctl restart aqi-lights
    ```

### 3. Verification

1.  **Check Service Status**
    ```bash
    sudo systemctl status aqi-lights
    ```
    You should see `Active: active (running)`.

2.  **View Logs**
    ```bash
    journalctl -u aqi-lights -f
    ```

3.  **Network Failure Behavior**
    If the network disconnects, the light will **stay on** (displaying the last known AQI state) instead of turning off. The system will automatically retry fetching data in the background.

## 🌐 AQI Data Sources

This project supports any AQI data source that provides JSON responses with AQI values. Popular options include:

### IQAir API
1. Register for a free API key at [IQAir](https://www.iqair.com/air-pollution-data-api)
2. Use the endpoint format:
   ```
   https://api.airvisual.com/v2/nearest_city?key=YOUR_API_KEY
   ```
3. Update `STATION_URL` in `config.py`

### Custom API
The code expects a JSON response with the following structure:
```json
{
  "current": {
    "aqius": 85
  }
}
```

Modify the `fetch_hanoi_aqi()` function in `main.py` if your API uses a different format.

## 💡 Status Indication

- **Startup**: The Green light will flash 3 times when the service starts successfully.
- **Normal Operation**: Lights display AQI status.
- **Network Failure**: If the network fails, the system keeps the **last known light state** active until connection is restored.

## 🧪 Testing

To test the relay connections without fetching AQI data, uncomment the following line at the end of `main.py`:

```python
if __name__ == "__main__":
    # main()
    cycle_relays()  # Uncomment this line for testing
```

This will cycle through all three lights (Red → Yellow → Green → Off) to verify your wiring.

## ⚙️ Customization

### Adjusting AQI Thresholds

Modify the thresholds in `config.py` based on your local air quality standards or organizational policies:

```python
AQI_GOOD_MAX = 50         # Adjust for your "safe" threshold
AQI_CAUTION_MAX = 150     # Adjust for your "caution" threshold
```

### Changing Update Frequency

Update the `UPDATE_INTERVAL` value in `config.py` (in seconds):

```python
UPDATE_INTERVAL = 60 * 10  # Update every 10 minutes
```

### Modifying GPIO Pins

If you need to use different GPIO pins, update the `RELAY_PINS` list in `main.py`:

```python
RELAY_PINS = [4, 3, 2]  # [Red, Yellow, Green]
```

## 📁 Project Structure

```
aqi-lights/
├── main.py              # Main application logic
├── setup.sh             # Setup script for dependencies and service
├── aqi-lights.service   # Systemd service file
├── requirements.txt     # Python dependencies
├── config.py            # Configuration file (gitignored)
├── config_example.py    # Configuration template
└── README.md            # This file
```

## 🐛 Troubleshooting

### Service Not Starting
- Check status: `sudo systemctl status aqi-lights`
- Check logs: `journalctl -u aqi-lights -f`
- Ensure `config.py` exists and has valid values.
- Verify `setup.sh` ran successfully.

### Relays Not Switching
- Verify wiring connections (GPIO 4, 3, 2).
- Check if your relay module requires 5V.
- Test relays manually using python to toggle GPIOs.

### AQI Data Not Updating
- Verify `STATION_URL` is correct and accessible.
- Check logs for "AQI fetch error".
- Ensure internet connectivity (`ping google.com`).

### Lights Stay Off
- Check that AQI data is being fetched successfully (monitor serial output)
- Verify relay connections and power supply
- Test relays using `cycle_relays()` function

## 📝 License

This project is open source and available for educational and non-commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Share your customizations

## 🌟 Use Cases

- **Schools**: Help administrators decide when it's safe for outdoor activities
- **Offices**: Inform employees about air quality conditions
- **Public Spaces**: Provide real-time air quality awareness
- **Smart Homes**: Integrate with home automation systems

## 📧 Support

For questions or issues, please open an issue on the project repository.

---

**Built with ❤️ for cleaner air and healthier communities**
