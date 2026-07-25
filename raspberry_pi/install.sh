#!/bin/bash
# VNPR Raspberry Pi Installation Script

echo "Installing VNPR Edge Device..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv libcamera-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install picamera2 RPi.GPIO pyserial requests Pillow numpy
pip install google-cloud-vision

# Install OpenCV (optional, for local fallback OCR)
pip install opencv-python-headless

# Create directories
mkdir -p violation_backups
mkdir -p logs

# Copy config
cp .env.example .env

echo "Installation complete!"
echo "Edit .env with your API credentials, then run: python main.py"
