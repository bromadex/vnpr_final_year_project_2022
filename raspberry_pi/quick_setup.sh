#!/bin/bash
# Raspberry Pi Edge Device Quick Setup

echo "============================================"
echo "  VNPR Edge Device Setup"
echo "============================================"

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3-pip \
    python3-venv \
    libcamera-dev \
    libcap-dev \
    python3-libcamera \
    python3-kms++ \
    python3-picamera2

# Create virtual environment
python3 -m venv ~/vnpr_env
source ~/vnpr_env/bin/activate

# Install Python packages
pip install --upgrade pip
pip install picamera2 RPi.GPIO pyserial requests Pillow numpy
pip install google-cloud-vision opencv-python-headless

# Create project directory
mkdir -p ~/vnpr_device
cd ~/vnpr_device

# Copy device files (run this from your main project)
# cp /path/to/vnpr_project/raspberry_pi/* .

# Create config
cat > .env << 'EOF'
API_BASE_URL=http://your-server-ip:8000/api
DEVICE_API_KEY=your-device-api-key
SPEED_LIMIT=60
GOOGLE_CLOUD_VISION_API_KEY=your-google-cloud-api-key
EOF

echo ""
echo "Edit .env with your credentials, then run:"
echo "  source ~/vnpr_env/bin/activate"
echo "  python main.py"
