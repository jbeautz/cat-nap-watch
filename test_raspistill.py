#!/usr/bin/env python3
"""
Test raspistill camera command for Pi Zero
Bypasses all OpenCV/GStreamer issues
"""

import subprocess
import os
import time
from datetime import datetime

def test_raspistill_basic():
    """Test basic raspistill functionality."""
    print("🐱 Testing raspistill camera command")
    print("=" * 35)
    
    # Check if raspistill is available
    try:
        result = subprocess.run(['which', 'raspistill'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ raspistill command not found")
            print("Make sure you're on a Raspberry Pi with camera support")
            return False
        else:
            print("✅ raspistill command found")
    except Exception as e:
        print(f"❌ Error checking raspistill: {e}")
        return False
    
    # Test camera detection
    print("\n🔍 Testing camera detection...")
    try:
        # Very simple test - just try to capture a tiny image
        test_file = "/tmp/camera_test.jpg"
        
        cmd = [
            'raspistill',
            '-o', test_file,
            '-w', '64',      # Tiny resolution
            '-h', '64',
            '-q', '10',      # Low quality
            '-t', '1000',    # 1 second
            '--nopreview'
        ]
        
        print("📸 Attempting minimal photo capture...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if os.path.exists(test_file):
                size = os.path.getsize(test_file)
                print(f"✅ Camera test successful! Photo: {size} bytes")
                os.remove(test_file)  # Cleanup
                return True
            else:
                print("❌ Command succeeded but no file created")
                return False
        else:
            print(f"❌ Camera test failed: {result.stderr}")
            print("\nTroubleshooting:")
            print("1. Enable camera: sudo raspi-config -> Interface Options -> Camera")
            print("2. Reboot after enabling camera")
            print("3. Check camera connection")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Camera test timed out")
        print("Camera might be stuck or not responding")
        return False
    except Exception as e:
        print(f"❌ Error during camera test: {e}")
        return False

def test_different_settings():
    """Test various raspistill settings to find what works."""
    print("\n🔬 Testing different camera settings...")
    
    settings_to_try = [
        {"w": "160", "h": "120", "q": "20", "desc": "Ultra-minimal"},
        {"w": "320", "h": "240", "q": "30", "desc": "Low resolution"},
        {"w": "640", "h": "480", "q": "50", "desc": "Medium resolution"}
    ]
    
    working_settings = []
    
    for i, settings in enumerate(settings_to_try):
        print(f"\n📷 Test {i+1}: {settings['desc']} ({settings['w']}x{settings['h']})")
        
        test_file = f"/tmp/test_{i}.jpg"
        
        cmd = [
            'raspistill',
            '-o', test_file,
            '-w', settings['w'],
            '-h', settings['h'],
            '-q', settings['q'],
            '-t', '2000',
            '--nopreview'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(test_file):
                size = os.path.getsize(test_file) / 1024  # KB
                print(f"   ✅ Success! File size: {size:.1f} KB")
                working_settings.append(settings)
                os.remove(test_file)
            else:
                print(f"   ❌ Failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Results: {len(working_settings)}/3 settings worked")
    return len(working_settings) > 0

def show_memory_usage():
    """Show current memory usage."""
    print("\n💾 Current memory usage:")
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print("Could not get memory info")

def main():
    """Main test function."""
    print("🚨 Pi Zero Camera Test - Bypassing OpenCV")
    print("This uses raspistill command directly")
    print()
    
    show_memory_usage()
    
    # Basic test
    if not test_raspistill_basic():
        print("\n❌ Basic camera test failed!")
        print("\nNext steps:")
        print("1. sudo raspi-config -> Interface Options -> Camera -> Enable")
        print("2. sudo reboot")
        print("3. Check camera cable connection")
        return False
    
    # Extended tests
    if test_different_settings():
        print("\n🎉 Camera is working with raspistill!")
        print("\nYou can now try:")
        print("python catnap_watch_ultra_minimal.py")
        print("\nThis will:")
        print("- Use no video streaming (no memory pressure)")
        print("- Take photos at intervals using raspistill")
        print("- Send all photos via email")
        print("- Completely bypass OpenCV/GStreamer issues")
    else:
        print("\n⚠️  Camera partially working but may have issues")
        print("Try running the emergency memory liberation script:")
        print("./emergency_memory_liberation.sh")

if __name__ == "__main__":
    main()
