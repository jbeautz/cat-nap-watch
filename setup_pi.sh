#!/bin/bash

# CatNap Watch Setup Script (PIR + USB Camera)

echo "🐱 Setting up CatNap Watch (PIR + USB Camera)..."

set -e

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python3 and pip if not already installed
echo "🐍 Installing Python3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install system packages needed for GPIO and V4L2
echo "🔌 Installing GPIO and V4L2 tooling..."
sudo apt install -y python3-rpi.gpio v4l-utils

# Optional: common OpenCV runtime deps (avoid dev headers for speed)
echo "📸 Installing common OpenCV runtime libraries..."
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libgtk-3-0 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0

# Ensure user in video group for camera access
if id -nG "$USER" | grep -qw video; then
  echo "✅ User $USER already in video group"
else
  echo "➕ Adding $USER to video group (re-login required to take effect)"
  sudo usermod -a -G video "$USER"
fi

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv catnap_env
source catnap_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "📝 Created .env from example. Update it with your settings."
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1) Review and edit .env as needed (CAMERA_DEVICE_ID, FRAME_WIDTH/HEIGHT, EMAIL_*, OPENAI_API_KEY)"
echo "2) Activate the venv: source catnap_env/bin/activate"
echo "3) Run motion-triggered watcher: python catnap_watch_pir_usb.py"
echo ""
echo "🐱 Happy cat watching!"
