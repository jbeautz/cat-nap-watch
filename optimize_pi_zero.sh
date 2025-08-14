#!/bin/bash

# Pi Zero Memory Optimization Script for CatNap Watch
# This script configures your Pi Zero to better handle camera operations

echo "🐱 Pi Zero Memory Optimization for CatNap Watch"
echo "================================================="

# Check if running on Pi Zero
PI_MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "Unknown")
echo "Detected Pi Model: $PI_MODEL"

# GPU Memory Split optimization
echo ""
echo "🔧 Optimizing GPU memory split..."
CURRENT_GPU_MEM=$(vcgencmd get_mem gpu | cut -d= -f2 | cut -d M -f1)
echo "Current GPU memory: ${CURRENT_GPU_MEM}M"

if [ "$CURRENT_GPU_MEM" -lt "128" ]; then
    echo "📈 Increasing GPU memory to 128M for camera operations..."
    sudo raspi-config nonint do_memory_split 128
    echo "✅ GPU memory split updated (requires reboot)"
else
    echo "✅ GPU memory split is adequate"
fi

# Camera-specific optimizations
echo ""
echo "📸 Applying camera optimizations..."

# Create camera optimization config
sudo tee /etc/modprobe.d/camera-optimization.conf > /dev/null << EOF
# Camera optimization for Pi Zero
options bcm2835-v4l2 max_video_width=320 max_video_height=240
EOF

echo "✅ Camera resolution limits applied"

# System optimizations for low memory
echo ""
echo "🚀 Applying system memory optimizations..."

# Disable unnecessary services to free memory
SERVICES_TO_DISABLE=(
    "bluetooth.service"
    "hciuart.service" 
    "ModemManager.service"
)

for service in "${SERVICES_TO_DISABLE[@]}"; do
    if systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo "⏹️  Disabling $service..."
        sudo systemctl disable "$service"
        sudo systemctl stop "$service"
    fi
done

# Configure swap for emergency memory
echo ""
echo "💾 Configuring emergency swap..."
if [ ! -f /var/swap ]; then
    echo "Creating 256MB swap file..."
    sudo fallocate -l 256M /var/swap
    sudo chmod 600 /var/swap
    sudo mkswap /var/swap
    echo '/var/swap swap swap defaults 0 0' | sudo tee -a /etc/fstab
    sudo swapon /var/swap
    echo "✅ Swap file created and enabled"
else
    echo "✅ Swap file already exists"
fi

# Configure kernel parameters for camera
echo ""
echo "⚙️  Configuring kernel parameters..."

# Add camera-friendly kernel parameters
sudo tee -a /boot/config.txt > /dev/null << EOF

# CatNap Watch Camera Optimizations
gpu_mem=128
disable_overscan=1
camera_auto_detect=1
dtoverlay=vc4-kms-v3d
max_framebuffers=2

# Memory optimizations
gpu_mem_256=128
gpu_mem_512=128
EOF

echo "✅ Boot configuration updated"

# Set environment variables for GStreamer
echo ""
echo "🎥 Configuring GStreamer for low memory..."

sudo tee /etc/environment > /dev/null << EOF
# GStreamer optimizations for Pi Zero
GST_DEBUG=1
GST_REGISTRY_DISABLE=1
GST_REGISTRY_FORK=no
OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0
OPENCV_VIDEOIO_DEBUG=1
EOF

# Add to user's profile as well
tee -a ~/.bashrc > /dev/null << 'EOF'

# CatNap Watch environment optimizations
export GST_DEBUG=1
export GST_REGISTRY_DISABLE=1
export GST_REGISTRY_FORK=no
export OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0
EOF

echo "✅ GStreamer environment configured"

# Create memory monitoring script
echo ""
echo "📊 Creating memory monitoring script..."

tee monitor_memory.sh > /dev/null << 'EOF'
#!/bin/bash
# Memory monitoring for CatNap Watch

echo "🐱 CatNap Watch Memory Monitor"
echo "=============================="
echo ""

while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo "Memory Usage:"
    free -h | grep -E "Mem:|Swap:"
    
    echo ""
    echo "GPU Memory:"
    vcgencmd get_mem arm
    vcgencmd get_mem gpu
    
    echo ""
    echo "Temperature:"
    vcgencmd measure_temp
    
    echo "=============================="
    sleep 30
done
EOF

chmod +x monitor_memory.sh

echo "✅ Memory monitor created (run ./monitor_memory.sh)"

# Summary
echo ""
echo "🎉 Pi Zero optimization complete!"
echo ""
echo "Applied optimizations:"
echo "✓ GPU memory split set to 128M"
echo "✓ Camera resolution limits configured"
echo "✓ Unnecessary services disabled"
echo "✓ Emergency swap file created"
echo "✓ GStreamer optimizations applied"
echo "✓ Memory monitor script created"
echo ""
echo "⚠️  IMPORTANT: Reboot required for all changes to take effect!"
echo ""
echo "After reboot:"
echo "1. Test camera: python test_camera_email.py"
echo "2. Monitor memory: ./monitor_memory.sh"
echo "3. Run CatNap Watch: python catnap_watch.py"
echo ""
echo "🔄 Run 'sudo reboot' now to apply changes"
