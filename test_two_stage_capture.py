#!/usr/bin/env python3
"""
Two-Stage Capture Test for CatNap Watch
Tests the memory-efficient two-stage capture system
"""

import cv2
import time
import os
import gc
from datetime import datetime
from config import (
    MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT,
    PHOTO_CAPTURE_WIDTH, PHOTO_CAPTURE_HEIGHT,
    PHOTOS_DIR
)

def set_camera_resolution(camera, width, height):
    """Change camera resolution."""
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    time.sleep(0.1)  # Allow camera to adjust

def test_two_stage_capture():
    """Test the two-stage capture system."""
    print("🐱 Two-Stage Capture Test")
    print("=" * 30)
    print("This test demonstrates memory-efficient capture:")
    print(f"  Stage 1: Motion detection at {MOTION_DETECTION_WIDTH}x{MOTION_DETECTION_HEIGHT}")
    print(f"  Stage 2: High-res photos at {PHOTO_CAPTURE_WIDTH}x{PHOTO_CAPTURE_HEIGHT}")
    print()
    
    # Initialize camera
    print("📸 Initializing camera...")
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if not camera.isOpened():
        print("V4L2 failed, trying default backend...")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("❌ Camera failed to open")
            return False
    
    try:
        # Start with low resolution
        print(f"🔧 Setting motion detection resolution: {MOTION_DETECTION_WIDTH}x{MOTION_DETECTION_HEIGHT}")
        set_camera_resolution(camera, MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT)
        
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        
        # Camera warmup
        print("⏳ Camera warmup...")
        time.sleep(2)
        
        # Clear buffer
        for _ in range(3):
            ret, frame = camera.read()
            if ret:
                del frame
        
        # Stage 1: Capture low-res frame for motion detection
        print("\n📷 Stage 1: Low-res motion detection frame")
        ret, low_res_frame = camera.read()
        
        if not ret:
            print("❌ Failed to capture low-res frame")
            return False
        
        print(f"✅ Low-res frame: {low_res_frame.shape[1]}x{low_res_frame.shape[0]}")
        
        # Convert to grayscale for motion detection (saves memory)
        gray_frame = cv2.cvtColor(low_res_frame, cv2.COLOR_BGR2GRAY)
        del low_res_frame  # Immediate cleanup
        
        # Calculate memory usage
        gray_memory_mb = (gray_frame.nbytes) / (1024 * 1024)
        print(f"   Memory usage: {gray_memory_mb:.2f} MB (grayscale)")
        
        # Simulate motion detection
        print("🔍 Simulating motion detection...")
        time.sleep(1)
        print("✅ Motion detected! Switching to high resolution...")
        
        # Stage 2: Switch to high resolution for cat photo
        print(f"\n📸 Stage 2: High-res photo capture")
        print(f"🔄 Switching to {PHOTO_CAPTURE_WIDTH}x{PHOTO_CAPTURE_HEIGHT}...")
        
        set_camera_resolution(camera, PHOTO_CAPTURE_WIDTH, PHOTO_CAPTURE_HEIGHT)
        time.sleep(0.5)  # Give camera time to adjust
        
        # Capture high-res frame
        high_res_frame = None
        for i in range(3):  # Try a few times for stability
            ret, frame = camera.read()
            if ret:
                high_res_frame = frame
            time.sleep(0.1)
        
        if high_res_frame is None:
            print("❌ Failed to capture high-res frame")
            return False
        
        print(f"✅ High-res frame: {high_res_frame.shape[1]}x{high_res_frame.shape[0]}")
        
        # Calculate memory usage difference
        color_memory_mb = (high_res_frame.nbytes) / (1024 * 1024)
        print(f"   Memory usage: {color_memory_mb:.2f} MB (full color)")
        
        memory_savings = ((color_memory_mb - gray_memory_mb) / color_memory_mb) * 100
        print(f"   Memory savings: {memory_savings:.1f}% during motion detection")
        
        # Save the high-res photo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"two_stage_test_{timestamp}.jpg"
        filepath = os.path.join(PHOTOS_DIR, filename)
        
        success = cv2.imwrite(filepath, high_res_frame)
        if success:
            print(f"✅ High-res photo saved: {filename}")
        else:
            print("❌ Failed to save photo")
        
        # Clean up
        del gray_frame
        del high_res_frame
        
        # Switch back to low resolution
        print(f"\n🔄 Switching back to low-res for next cycle...")
        set_camera_resolution(camera, MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT)
        
        print("\n🎉 Two-stage capture test successful!")
        print(f"   💾 Memory efficient motion detection")
        print(f"   📸 High quality photos when needed")
        print(f"   🔄 Automatic resolution switching")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        camera.release()
        gc.collect()

def compare_memory_usage():
    """Compare memory usage between approaches."""
    print("\n📊 Memory Usage Comparison")
    print("=" * 30)
    
    # Calculate theoretical memory usage
    low_res_pixels = MOTION_DETECTION_WIDTH * MOTION_DETECTION_HEIGHT
    high_res_pixels = PHOTO_CAPTURE_WIDTH * PHOTO_CAPTURE_HEIGHT
    
    # Grayscale (1 byte per pixel) vs Color (3 bytes per pixel)
    low_res_gray_mb = (low_res_pixels * 1) / (1024 * 1024)
    low_res_color_mb = (low_res_pixels * 3) / (1024 * 1024)
    high_res_color_mb = (high_res_pixels * 3) / (1024 * 1024)
    
    print(f"Low-res grayscale:  {low_res_gray_mb:.2f} MB")
    print(f"Low-res color:      {low_res_color_mb:.2f} MB")  
    print(f"High-res color:     {high_res_color_mb:.2f} MB")
    
    savings_vs_high = ((high_res_color_mb - low_res_gray_mb) / high_res_color_mb) * 100
    savings_vs_low_color = ((low_res_color_mb - low_res_gray_mb) / low_res_color_mb) * 100
    
    print(f"\nMemory savings vs high-res color: {savings_vs_high:.1f}%")
    print(f"Memory savings vs low-res color:  {savings_vs_low_color:.1f}%")

def main():
    """Run two-stage capture test."""
    print("🎯 CatNap Watch Two-Stage Capture Test")
    print("This tests the memory-efficient capture system")
    print()
    
    compare_memory_usage()
    
    try:
        input("\nPress ENTER to test camera capture (Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return
    
    success = test_two_stage_capture()
    
    if success:
        print("\n✅ Two-stage capture is working perfectly!")
        print("Your Pi Zero can efficiently handle cat monitoring!")
    else:
        print("\n❌ Two-stage capture test failed")
        print("Check camera connection and try the minimal test instead")

if __name__ == "__main__":
    main()
