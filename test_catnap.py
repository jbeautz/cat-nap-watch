#!/usr/bin/env python3
"""
CatNap Watch Test Script
Tests basic camera functionality and detection algorithms
"""

import cv2
import time
import os
from datetime import datetime

def test_camera():
    """Test basic camera functionality."""
    print("🎥 Testing camera...")
    
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Camera failed to open")
        return False
    
    print("✅ Camera opened successfully")
    
    # Set camera properties
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Test capture
    ret, frame = camera.read()
    if not ret:
        print("❌ Failed to capture frame")
        camera.release()
        return False
    
    print(f"✅ Captured frame: {frame.shape}")
    
    # Save test image
    test_filename = f"test_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(test_filename, frame)
    print(f"✅ Test image saved: {test_filename}")
    
    camera.release()
    return True

def test_motion_detection():
    """Test motion detection with sample images."""
    print("🔍 Testing motion detection...")
    
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("❌ Camera not available for motion test")
        return False
    
    print("Taking baseline image in 3 seconds...")
    time.sleep(3)
    ret1, frame1 = camera.read()
    
    print("Move something in front of the camera!")
    print("Taking comparison image in 5 seconds...")
    time.sleep(5)
    ret2, frame2 = camera.read()
    
    if ret1 and ret2:
        # Simple motion detection
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
        changed_pixels = cv2.countNonZero(thresh)
        
        print(f"Changed pixels: {changed_pixels}")
        if changed_pixels > 1000:
            print("✅ Motion detected!")
        else:
            print("ℹ️  No significant motion detected")
    
    camera.release()
    return True

def test_openai_connection():
    """Test OpenAI API connection."""
    print("🤖 Testing OpenAI connection...")
    
    try:
        from config import OPENAI_API_KEY
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            print("❌ OpenAI API key not configured")
            print("Please set your API key in the .env file")
            return False
        
        import openai
        openai.api_key = OPENAI_API_KEY
        
        # Test API call
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello from a cat!"}],
            max_tokens=50
        )
        
        print("✅ OpenAI API connection successful!")
        print(f"Test response: {response.choices[0].message.content}")
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed")
        return False
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

def main():
    """Run all tests."""
    print("🐱 CatNap Watch Test Suite")
    print("=" * 40)
    
    tests = [
        ("Camera Test", test_camera),
        ("Motion Detection Test", test_motion_detection),
        ("OpenAI API Test", test_openai_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    print(f"\nPassed: {passed}/{len(results)} tests")

if __name__ == "__main__":
    main()
