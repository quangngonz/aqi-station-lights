#!/bin/bash
set -e

echo "Starting AQI Lights Setup for Pi Zero 2W..."

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-lgpio

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create config.py if it doesn't exist
if [ ! -f config.py ]; then
    echo "Creating config.py from config_example.py..."
    cp config_example.py config.py
    echo "PLEASE EDIT config.py with your specific settings!"
fi

# Setup Systemd Service
echo "Setting up systemd service..."
# Assuming script is run from project root, and we want to install it
# We need to make sure the paths in the service file are correct
# This script assumes the project is checked out to /home/pi/aqi-lights
# If not, we should probably sed the service file or copy it to the right place.
# For simplicity, we'll assume the user might need to adjust paths if not in /home/pi/aqi-lights.
# But let's try to be smart and verify the current directory.

CURRENT_DIR=$(pwd)
SERVICE_FILE="aqi-lights.service"

# Update WorkingDirectory and ExecStart in service file to match current location
sed -i "s|WorkingDirectory=/home/pi/aqi-lights|WorkingDirectory=$CURRENT_DIR|g" $SERVICE_FILE
sed -i "s|ExecStart=/home/pi/aqi-lights/venv/bin/python3 /home/pi/aqi-lights/main.py|ExecStart=$CURRENT_DIR/venv/bin/python3 $CURRENT_DIR/main.py|g" $SERVICE_FILE
sed -i "s|User=pi|User=$USER|g" $SERVICE_FILE

sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aqi-lights
sudo systemctl start aqi-lights

echo "Setup complete! Service started."
echo "Check status with: sudo systemctl status aqi-lights"
