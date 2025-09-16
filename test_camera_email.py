#!/usr/bin/env python3
"""
Camera + Email Test for PIR + USB Camera setup
Captures a single frame from the configured USB camera and emails it.
"""

import cv2
import time
import os
import sys
from datetime import datetime
from config import (
    CAMERA_DEVICE_ID,
    FRAME_WIDTH, FRAME_HEIGHT,
    WARMUP_TIME,
    PHOTOS_DIR,
    USE_MJPG,
)
from catnap_diaries import CatNapDiaries


def _try_configure_cap(cap, try_mjpg=True):
    if try_mjpg:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    else:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    time.sleep(0.3)
    for _ in range(2):
        cap.read()
    return cap.read()


def open_usb_camera():
    indices = range(0, 6) if CAMERA_DEVICE_ID < 0 else [CAMERA_DEVICE_ID]
    for idx in indices:
        print(f"Trying /dev/video{idx}...")
        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap.release()
            continue
        ret, frame = _try_configure_cap(cap, try_mjpg=USE_MJPG)
        if not (ret and frame is not None):
            print("  MJPG failed; trying YUYV...")
            ret, frame = _try_configure_cap(cap, try_mjpg=False)
        if ret and frame is not None:
            print(f"Opened camera at {frame.shape[1]}x{frame.shape[0]} on index {idx}")
            return cap
        cap.release()
    return None


def test_camera_and_email():
    print("🎥 USB Camera & Email Test")
    print("=" * 40)

    os.makedirs(PHOTOS_DIR, exist_ok=True)

    cap = open_usb_camera()
    if not cap:
        print("❌ Could not open any USB camera. Check connections and permissions.")
        return False

    print(f"⏳ Warming up for {WARMUP_TIME} seconds...")
    time.sleep(WARMUP_TIME)

    print("📸 Capturing...")
    for _ in range(2):
        cap.read()
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("❌ Failed to capture frame")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"camera_test_{timestamp}.jpg"
    filepath = os.path.join(PHOTOS_DIR, filename)

    if not cv2.imwrite(filepath, frame):
        print("❌ Failed to save image")
        return False

    print(f"✅ Photo saved: {filepath}")

    print("\n📧 Sending test email...")
    try:
        diaries = CatNapDiaries()
        email = f"""Subject: 📸 CatNap Watch USB Camera Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}

Hello from your CatNap Watch (PIR + USB) setup! 📱

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
        ok = diaries.send_email(email, filepath)
        if ok:
            print("✅ Email sent (or printed if email not configured)")
        else:
            print("⚠️ Email send failed; check .env settings")
    except Exception as e:
        print(f"⚠️ Email test error: {e}")

    return True


def main():
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
    try:
        input("Press ENTER to capture a test image...")
    except KeyboardInterrupt:
        print("Cancelled")
        sys.exit(0)
    ok = test_camera_and_email()
    print("\nDone." if ok else "\nFailed.")


if __name__ == "__main__":
    main()
