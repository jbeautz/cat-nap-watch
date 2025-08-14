#!/usr/bin/env python3
"""
Minimal Camera Test for Pi Zero
Tests camera functionality with absolute minimum memory usage
"""

import cv2
import time
import os
import gc
from datetime import datetime

def minimal_camera_test():
    """Test camera with minimal memory footprint."""
    print("🐱 Minimal Pi Zero Camera Test")
    print("==============================")
    print("This test uses the absolute minimum memory possible.")
    
    # Force garbage collection
    gc.collect()
    
    try:
        print("📸 Opening camera with minimal settings...")
        
        # Use the most basic camera initialization
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("❌ Camera failed to open")
            return False
        
        # Set to absolute minimum resolution
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 160)  # Very small
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)  # Very small
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print("⏳ Brief warmup...")
        time.sleep(1)
        
        # Clear buffer
        for _ in range(2):
            ret, frame = camera.read()
            if ret:
                del frame  # Explicit cleanup
        
        # Take actual photo
        print("📷 Taking minimal test photo...")
        ret, frame = camera.read()
        
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"minimal_test_{timestamp}.jpg"
            
            # Save with minimal quality to reduce memory
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            
            print(f"✅ Photo saved: {filename}")
            print(f"   Size: {frame.shape[1]}x{frame.shape[0]} pixels")
            
            # Immediate cleanup
            del frame
            
        camera.release()
        
        # Force cleanup
        gc.collect()
        
        print("✅ Minimal camera test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Ensure cleanup
        gc.collect()

if __name__ == "__main__":
    success = minimal_camera_test()
    if success:
        print("\n🎉 Your Pi Zero can handle basic camera operations!")
        print("You can now try the full CatNap Watch system.")
    else:
        print("\n⚠️  Your Pi Zero is struggling with camera operations.")
        print("Consider using an external camera or upgrading hardware.")
