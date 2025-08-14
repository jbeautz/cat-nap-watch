#!/usr/bin/env python3
"""
CatNap Watch - Ultra Low Memory Mode
Emergency version for Pi Zero with severe memory constraints
"""

import cv2
import time
import logging
import gc
import os
from datetime import datetime
from config import (
    CAPTURE_INTERVAL, WARMUP_TIME, DIFF_THRESHOLD, 
    EMERGENCY_CAMERA_WIDTH, EMERGENCY_CAMERA_HEIGHT, JPEG_QUALITY, PHOTOS_DIR
)

# Minimal logging to save memory
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraLowMemoryCatWatch:
    def __init__(self):
        self.camera = None
        self.last_frame_gray = None  # Store only grayscale to save memory
        
    def init_camera(self):
        """Initialize camera with emergency low-memory settings."""
        try:
            logger.warning("Starting ULTRA LOW MEMORY mode")
            
            # Force memory cleanup before starting
            gc.collect()
            
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            
            # Emergency ultra-low settings
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, EMERGENCY_CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, EMERGENCY_CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            time.sleep(WARMUP_TIME)
            
            # Get baseline - store only grayscale to save memory
            ret, frame = self.camera.read()
            if ret:
                self.last_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                del frame  # Immediate cleanup
                gc.collect()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Camera init failed: {e}")
            return False
    
    def detect_change(self, current_gray):
        """Ultra-simple change detection."""
        if self.last_frame_gray is None:
            return False
        
        # Simple pixel difference count
        diff = cv2.absdiff(self.last_frame_gray, current_gray)
        changed_pixels = cv2.countNonZero(cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)[1])
        
        return changed_pixels > 500  # Lower threshold for emergency mode
    
    def save_photo(self, frame):
        """Save photo with maximum compression."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lowmem_cat_{timestamp}.jpg"
        filepath = os.path.join(PHOTOS_DIR, filename)
        
        # Save with high compression to reduce memory usage
        success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        return filepath if success else None
    
    def run_emergency_mode(self):
        """Run in emergency low-memory mode with proper image lifecycle."""
        if not self.init_camera():
            logger.error("Failed to initialize camera in emergency mode")
            return
        
        logger.warning("CatNap Watch running in EMERGENCY LOW MEMORY MODE")
        logger.warning(f"Resolution: {EMERGENCY_CAMERA_WIDTH}x{EMERGENCY_CAMERA_HEIGHT}")
        
        try:
            frame_count = 0
            while True:
                # Force cleanup every 10 frames
                if frame_count % 10 == 0:
                    gc.collect()
                
                ret, current_frame = self.camera.read()
                if not ret:
                    time.sleep(1)
                    continue
                
                # Convert to grayscale immediately to save memory
                current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
                
                # Check for changes
                if self.detect_change(current_gray):
                    logger.warning("Change detected - saving photo")
                    
                    # Save the color frame (only if change detected)
                    photo_path = self.save_photo(current_frame)
                    if photo_path:
                        print(f"📸 Photo saved: {photo_path}")
                    
                    # Update baseline to current grayscale frame
                    if self.last_frame_gray is not None:
                        del self.last_frame_gray  # Clean up old baseline
                    self.last_frame_gray = current_gray.copy()
                    
                else:
                    # No change detected - discard frame immediately
                    del current_gray
                
                # Always clean up the current color frame
                del current_frame
                
                frame_count += 1
                time.sleep(CAPTURE_INTERVAL)
                
        except KeyboardInterrupt:
            logger.warning("Stopping emergency mode")
        except Exception as e:
            logger.error(f"Emergency mode error: {e}")
        finally:
            if self.camera:
                self.camera.release()
            # Clean up any remaining frames
            if self.last_frame_gray is not None:
                del self.last_frame_gray
            gc.collect()

def main():
    """Run ultra low memory cat watch."""
    print("🚨 CatNap Watch - ULTRA LOW MEMORY MODE")
    print("=====================================")
    print("⚠️  This mode uses minimal memory but reduced functionality:")
    print("   - Very low resolution photos")
    print("   - No AI email generation") 
    print("   - Basic motion detection only")
    print("   - Photos saved locally only")
    print("")
    
    try:
        input("Press ENTER to start emergency mode (Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    watch = UltraLowMemoryCatWatch()
    watch.run_emergency_mode()

if __name__ == "__main__":
    main()
