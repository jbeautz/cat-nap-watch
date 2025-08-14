#!/usr/bin/env python3
"""
Camera Test Script for CatNap Watch
Takes a test photo and emails it to verify camera and email functionality
"""

import cv2
import time
import os
import sys
from datetime import datetime
from config import WARMUP_TIME, PHOTOS_DIR, PHOTO_CAPTURE_WIDTH, PHOTO_CAPTURE_HEIGHT, CAMERA_FPS, CAMERA_BUFFER_SIZE
from catnap_diaries import CatNapDiaries

def test_camera_and_email():
    """Test camera capture and email functionality."""
    print("🎥 CatNap Watch Camera & Email Test")
    print("=" * 40)
    
    # Initialize camera
    print("📸 Initializing camera with Pi Zero optimizations...")
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if not camera.isOpened():
        print("⚠️  V4L2 backend failed, trying default backend...")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print("❌ ERROR: Could not open camera!")
            print("Make sure:")
            print("  - Camera is properly connected")
            print("  - Camera is enabled: sudo raspi-config")
            print("  - No other processes are using the camera")
            return False
    
    # Configure camera for Pi Zero
    print("🔧 Configuring camera settings for Pi Zero...")
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, PHOTO_CAPTURE_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, PHOTO_CAPTURE_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    
    # Camera warmup
    print(f"⏳ Camera warming up for {WARMUP_TIME} seconds...")
    time.sleep(WARMUP_TIME)
    
    # Take countdown photos
    print("\n📷 Taking test photos...")
    for i in range(3, 0, -1):
        print(f"   Photo in {i}...")
        time.sleep(1)
    
    print("   📸 SNAP!")
    
    # Capture the photo
    ret, frame = camera.read()
    camera.release()
    
    if not ret:
        print("❌ ERROR: Failed to capture image from camera!")
        return False
    
    # Save the test photo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"camera_test_{timestamp}.jpg"
    filepath = os.path.join(PHOTOS_DIR, filename)
    
    success = cv2.imwrite(filepath, frame)
    if not success:
        print("❌ ERROR: Failed to save image!")
        return False
    
    print(f"✅ Photo saved: {filepath}")
    print(f"   Image size: {frame.shape[1]}x{frame.shape[0]} pixels")
    
    # Test email functionality
    print("\n📧 Testing email functionality...")
    try:
        diaries = CatNapDiaries()
        
        # Create a test email
        test_email = f"""Subject: 📸 CatNap Watch Camera Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}

Hello from your CatNap Watch system! 📱

This is a test message to verify that your camera and email system are working correctly.

Test Details:
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📸 Photo: {filename}
📏 Resolution: {frame.shape[1]}x{frame.shape[0]} pixels
🎯 Purpose: Camera and email functionality test

If you're reading this, both your Raspberry Pi camera and email system are working perfectly! 🎉

Your cat monitoring system is ready to capture all those precious moments when your feline friend decides to grace their favorite perch with their presence.

Next steps:
1. Position your camera to monitor your cat's favorite spot
2. Run the main CatNap Watch application: python catnap_watch.py
3. Enjoy funny updates from your cat's perspective!

Happy cat watching! 🐱

---
CatNap Watch System
Automated Cat Perch Monitoring"""

        # Send the test email with photo attachment
        success = diaries.send_email(test_email, filepath)
        
        if success:
            print("✅ Test email sent successfully!")
            print("   Check your email inbox for the test message with photo attachment.")
        else:
            print("⚠️  Email sending failed, but this might be normal if email isn't configured.")
            print("   The photo was still saved locally for testing.")
        
    except Exception as e:
        print(f"⚠️  Email test encountered an error: {e}")
        print("   This is normal if email credentials aren't configured yet.")
        print("   The camera test was still successful!")
    
    print("\n🎯 Test Summary:")
    print(f"   📸 Camera: ✅ Working (photo saved: {filename})")
    print(f"   💾 Storage: ✅ Working (saved to: {PHOTOS_DIR}/)")
    
    # Display next steps
    print("\n🚀 Next Steps:")
    print("   1. Check the saved photo to verify image quality")
    print("   2. If email didn't work, configure your .env file with email credentials")
    print("   3. Run the full test suite: python test_catnap.py")
    print("   4. Start monitoring: python catnap_watch.py")
    
    return True

def show_camera_info():
    """Display camera information and settings."""
    print("\n🔍 Camera Information:")
    try:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = camera.get(cv2.CAP_PROP_FPS)
            print(f"   Resolution: {int(width)}x{int(height)}")
            print(f"   FPS: {fps}")
            camera.release()
        else:
            print("   ❌ Camera not accessible")
    except Exception as e:
        print(f"   ⚠️  Could not get camera info: {e}")

def main():
    """Main function to run camera and email test."""
    print("🐱 Welcome to CatNap Watch Camera Test!")
    print("This script will test your camera and email setup.\n")
    
    # Check if photos directory exists
    if not os.path.exists(PHOTOS_DIR):
        print(f"📁 Creating photos directory: {PHOTOS_DIR}")
        os.makedirs(PHOTOS_DIR)
    
    # Show camera info
    show_camera_info()
    
    # Ask user if they're ready
    try:
        input("\n📸 Press ENTER when you're ready to take a test photo (or Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\n👋 Test cancelled. Goodbye!")
        sys.exit(0)
    
    # Run the test
    success = test_camera_and_email()
    
    if success:
        print("\n🎉 Camera test completed successfully!")
        print("Your CatNap Watch hardware is ready to monitor cats! 🐱")
    else:
        print("\n❌ Camera test failed. Please check the error messages above.")
        print("Make sure your camera is connected and enabled.")
    
    print("\n📚 For more help, check the troubleshooting section in README.md")

if __name__ == "__main__":
    main()
