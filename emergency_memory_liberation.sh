#!/bin/bash

# Emergency Pi Zero Memory Liberation Script
# Frees up maximum memory for camera operations

echo "🚨 EMERGENCY Pi Zero Memory Liberation"
echo "======================================"
echo "This script will free up maximum memory for camera operations"
echo "⚠️  This will disable many services - only use if camera fails!"
echo ""

read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🛑 Stopping unnecessary services..."

# Stop and disable memory-heavy services
SERVICES_TO_STOP=(
    "bluetooth.service"
    "hciuart.service"
    "dphys-swapfile.service"  # We'll recreate swap optimally
    "ModemManager.service"
    "wpa_supplicant.service"  # Only if using ethernet
    "avahi-daemon.service"
    "triggerhappy.service"
    "alsa-state.service"
    "keyboard-setup.service"
    "plymouth.service"
)

for service in "${SERVICES_TO_STOP[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "⏹️  Stopping $service..."
        sudo systemctl stop "$service" 2>/dev/null
        sudo systemctl disable "$service" 2>/dev/null
    fi
done

echo ""
echo "🧹 Cleaning up temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
sudo journalctl --vacuum-size=10M

echo ""
echo "💾 Optimizing swap..."
# Stop existing swap
sudo swapoff -a

# Create smaller, optimized swap
if [ -f /var/swap ]; then
    sudo rm /var/swap
fi

# Create 128MB swap (smaller but present)
echo "Creating optimized 128MB swap file..."
sudo fallocate -l 128M /var/swap
sudo chmod 600 /var/swap
sudo mkswap /var/swap
sudo swapon /var/swap

# Update fstab
sudo cp /etc/fstab /etc/fstab.backup
grep -v swap /etc/fstab.backup | sudo tee /etc/fstab > /dev/null
echo '/var/swap swap swap defaults,pri=100 0 0' | sudo tee -a /etc/fstab

echo ""
echo "🎛️  Applying emergency kernel parameters..."

# Reduce memory allocations
sudo tee -a /boot/config.txt > /dev/null << 'EOF'

# EMERGENCY Pi Zero Memory Settings
gpu_mem=64
disable_splash=1
boot_delay=0
disable_overscan=1

# Camera optimizations
camera_auto_detect=1
dtoverlay=vc4-kms-v3d,composite

# Memory optimizations
gpu_mem_256=64
gpu_mem_512=64
arm_freq=700
core_freq=250
EOF

echo ""
echo "🔧 Setting emergency environment variables..."

# Create emergency environment
sudo tee /etc/environment > /dev/null << 'EOF'
# Emergency Pi Zero environment
MALLOC_ARENA_MAX=1
MALLOC_MMAP_THRESHOLD_=32768
GST_REGISTRY_DISABLE=1
GST_DEBUG=0
OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0
OPENCV_VIDEOIO_PRIORITY_V4L2=1
EOF

# Add to user profile
tee -a ~/.bashrc > /dev/null << 'EOF'

# Emergency memory settings
export MALLOC_ARENA_MAX=1
export MALLOC_MMAP_THRESHOLD_=32768
export GST_REGISTRY_DISABLE=1
export GST_DEBUG=0
export OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0
export OPENCV_VIDEOIO_PRIORITY_V4L2=1
EOF

echo ""
echo "📊 Current memory status:"
free -h

echo ""
echo "🎉 Emergency memory liberation complete!"
echo ""
echo "Changes made:"
echo "✓ Disabled unnecessary services"
echo "✓ Cleaned temporary files"
echo "✓ Optimized swap (128MB)"
echo "✓ Reduced GPU memory to 64MB"
echo "✓ Set emergency environment variables"
echo ""
echo "⚠️  IMPORTANT: Reboot required!"
echo ""
echo "After reboot, try:"
echo "1. python catnap_watch_ultra_minimal.py"
echo "2. This uses raspistill instead of OpenCV"
echo "3. No video stream = no memory pressure"
echo ""
echo "🔄 Run 'sudo reboot' now to apply changes"
