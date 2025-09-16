#!/bin/bash

# Fix OpenCV ImportError: libGL.so.1 not found

echo "🔧 Fixing OpenCV OpenGL dependency issue..."

# Install missing OpenGL libraries
sudo apt update
sudo apt install -y libgl1-mesa-glx libglib2.0-0

# Install additional OpenCV dependencies that might be missing
sudo apt install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0

echo "✅ OpenCV dependencies installed!"
echo ""
echo "Now try running your USB camera test again:"
echo "source catnap_env/bin/activate"
echo "python test_camera_email.py"
echo "# Or start motion-triggered watcher:"
echo "python catnap_watch_pir_usb.py"
