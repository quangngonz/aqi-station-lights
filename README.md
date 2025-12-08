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

- **Raspberry Pi Pico 2W** (or Pico W with MicroPython support)
- **3-Channel Relay Module** (5V or 3.3V compatible)
- **Traffic Light** or individual LEDs (Red, Yellow, Green)
- **Power Supply** (appropriate for your relay and lights)
- **Jumper Wires**

## 📋 Wiring Diagram

| Pico Pin | Component | Description                      |
| -------- | --------- | -------------------------------- |
| GPIO 4   | Relay 1   | Red Light                        |
| GPIO 3   | Relay 2   | Yellow Light                     |
| GPIO 2   | Relay 3   | Green Light                      |
| GND      | Relay GND | Ground                           |
| 3V3/VBUS | Relay VCC | Power (check your relay voltage) |

## 🚀 Getting Started

### 1. Install MicroPython on Pico 2W

1. Download the latest MicroPython firmware for Pico 2W from [micropython.org](https://micropython.org/download/rp2-pico-w/)
2. Hold the BOOTSEL button while connecting the Pico to your computer
3. Drag and drop the `.uf2` file to the RPI-RP2 drive that appears

### 2. Configure the Project

1. Clone this repository or download the files
2. Copy `config_example.py` to `config.py`:
   ```bash
   cp config_example.py config.py
   ```
3. Edit `config.py` with your settings:

   ```python
   # WiFi credentials
   SSID = "Your_WiFi_SSID"
   PASSWORD = "Your_WiFi_Password"

   # AQI thresholds (adjust based on your needs)
   AQI_GOOD_MAX = 50         # Good to play outside
   AQI_CAUTION_MAX = 150     # Outside with caution

   # Update interval (in seconds)
   UPDATE_INTERVAL = 60 * 5  # Update every 5 minutes

   # AQI data source URL (e.g., IQAir API endpoint)
   STATION_URL = "Your_AQI_station_URL"
   ```

### 3. Upload Files to Pico

Upload the following files to your Pico using a tool like [Thonny](https://thonny.org/) or [rshell](https://github.com/dhylands/rshell):

- `main.py` - Main application logic
- `wifi.py` - WiFi connection handler
- `config.py` - Your configuration file

### 4. Run the Application

The application will start automatically on boot if `main.py` is present. You can also run it manually in Thonny or via REPL:

```python
import main
main.main()
```

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

## 💡 WiFi Status Indication

The system uses the traffic lights to indicate WiFi connection status during startup:

1. **Connecting**: Yellow and Red lights will alternate rapidly while attempting to connect
2. **Connected**: Green light will flash 3 times to confirm successful WiFi connection
3. **Normal Operation**: After successful connection, lights will display AQI status

This visual feedback eliminates the need for a separate WiFi status LED, making the system more compact and informative.

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

## 🌐 Remote Control (NEW!)

Control your Pico W device from anywhere on the internet! The system now includes a cloud backend that allows you to:

- **Trigger AQI refresh** remotely (no waiting for the next update)
- **Restart the device** from anywhere
- **Monitor device status** and view current AQI

### Quick Start

1. **Deploy the backend** (free hosting on PythonAnywhere):

   ```bash
   # See REMOTE_CONTROL_GUIDE.md for detailed instructions
   ```

2. **Enable remote control** in `config.py`:

   ```python
   ENABLE_REMOTE_CONTROL = True
   BACKEND_URL = "https://yourusername.pythonanywhere.com"
   BACKEND_TOKEN = "your-secret-token"
   ```

3. **Control from anywhere**:

   ```bash
   # Trigger AQI refresh
   python control_pico.py refresh

   # Check device status
   python control_pico.py status
   ```

**📖 For complete setup and deployment instructions, see [REMOTE_CONTROL_GUIDE.md](REMOTE_CONTROL_GUIDE.md)**

## 📁 Project Structure

```
aqi-lights/
├── main.py                    # Main application logic
├── wifi.py                    # WiFi connection handler
├── remote_control.py          # Remote control integration (NEW!)
├── config.py                  # Configuration file (gitignored)
├── config_example.py          # Configuration template
├── backend.py                 # Flask backend server (NEW!)
├── control_pico.py            # CLI control script (NEW!)
├── requirements.txt           # Backend dependencies (NEW!)
├── REMOTE_CONTROL_GUIDE.md    # Remote control setup guide (NEW!)
└── README.md                  # This file
```

## 🐛 Troubleshooting

### WiFi Connection Issues

- **Symptom**: Yellow and Red lights keep flashing indefinitely
- **Solutions**:
  - Verify SSID and password in `config.py`
  - Check if your WiFi network is 2.4GHz (Pico W doesn't support 5GHz)
  - Ensure the Pico is within range of your WiFi router
  - Check serial output for specific error messages

### Relays Not Switching

- Verify wiring connections
- Check if your relay module requires 5V (use VBUS pin instead of 3V3)
- Run `cycle_relays()` to test relay functionality

### AQI Data Not Updating

- Verify `STATION_URL` is correct and accessible
- Check API key validity (if using IQAir or similar)
- Monitor serial output for error messages
- Ensure internet connectivity

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
