#!/usr/bin/env python3
"""
Test script to find working video devices for OpenCV camera access.
This will test different video device numbers to find one that works.
"""

import cv2
import sys
import time

def test_video_device(device_id):
    """Test a specific video device ID"""
    print(f"\n=== Testing /dev/video{device_id} ===")
    
    try:
        # Try to open the camera
        cap = cv2.VideoCapture(device_id)
        
        if not cap.isOpened():
            print(f"❌ Could not open /dev/video{device_id}")
            return False
        
        # Try to read a frame
        print(f"✅ Successfully opened /dev/video{device_id}")
        
        # Set a reasonable resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Try to capture a frame with timeout
        print("Attempting to capture frame...")
        start_time = time.time()
        
        ret, frame = cap.read()
        
        if ret and frame is not None:
            print(f"✅ Successfully captured frame from /dev/video{device_id}")
            print(f"   Frame shape: {frame.shape}")
            print(f"   Capture took: {time.time() - start_time:.2f} seconds")
            
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {fps}")
            
            cap.release()
            return True
        else:
            print(f"❌ Failed to capture frame from /dev/video{device_id}")
            print(f"   Return value: {ret}")
            print(f"   Frame: {frame}")
            cap.release()
            return False
            
    except Exception as e:
        print(f"❌ Exception testing /dev/video{device_id}: {e}")
        return False

def main():
    print("🔍 Testing video devices for OpenCV camera access...")
    print("This will help identify which video device works with your camera.")
    
    working_devices = []
    
    # Test video devices 0-15 (should cover most cases)
    for device_id in range(16):
        if test_video_device(device_id):
            working_devices.append(device_id)
    
    print("\n" + "="*50)
    print("📊 RESULTS SUMMARY:")
    
    if working_devices:
        print(f"✅ Working video devices: {working_devices}")
        print(f"\n🎯 RECOMMENDATION:")
        print(f"   Use device {working_devices[0]} in your CatNap Watch configuration")
        print(f"   Update config.py with: CAMERA_DEVICE_ID = {working_devices[0]}")
    else:
        print("❌ No working video devices found")
        print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
        print("   1. Check camera hardware: vcgencmd get_camera")
        print("   2. Verify camera module is properly connected")
        print("   3. Try rebooting: sudo reboot")
        print("   4. Check dmesg for camera errors: dmesg | grep -i camera")

if __name__ == "__main__":
    main()
