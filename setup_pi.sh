#!/bin/bash

# CatNap Watch Setup Script for Raspberry Pi Zero

echo "🐱 Setting up CatNap Watch on Raspberry Pi Zero..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python3 and pip if not already installed
echo "🐍 Installing Python3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install system dependencies for OpenCV
echo "📸 Installing OpenCV system dependencies..."
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    python3-pyqt5 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper1 \
    libilmbase23 \
    libopenexr23 \
    libgstreamer1.0-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgtk2.0-0

# Enable camera interface
echo "📷 Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv catnap_env
source catnap_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and add your OpenAI API key"
echo "2. Activate the virtual environment: source catnap_env/bin/activate"
echo "3. Run the application: python catnap_watch.py"
echo ""
echo "🐱 Happy cat watching!"
