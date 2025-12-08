SSID = "Replace_with_your_SSID"
PASSWORD = "Replace_with_your_PASSWORD"

# AQI thresholds for traffic light levels
# Adjust these values as needed
AQI_GOOD_MAX = 50         # Good to play outside
AQI_CAUTION_MAX = 150     # Outside with caution
# AQI > AQI_CAUTION_MAX: Get inside

UPDATE_INTERVAL = 60 * 5  # Update every 5 minutes
STATION_URL = "Replace_with_your_AQI_station_URL"

# Web server configuration
WEB_SERVER_PORT = 80  # Port for remote control web interface

# Remote control backend configuration
ENABLE_REMOTE_CONTROL = False  # Set to True to enable cloud control
BACKEND_URL = "https://your-username.pythonanywhere.com"  # Your deployed backend URL
BACKEND_TOKEN = "your-secret-token-change-me"  # Must match backend SECRET_TOKEN
BACKEND_POLL_INTERVAL = 30  # Poll backend every 30 seconds
