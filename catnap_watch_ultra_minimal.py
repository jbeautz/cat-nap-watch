#!/usr/bin/env python3
"""
Ultra-Minimal CatNap Watch for Pi Zero
Uses raspistill command instead of OpenCV to bypass GStreamer issues
"""

import subprocess
import time
import os
import logging
from datetime import datetime
from config import CAPTURE_INTERVAL, PHOTOS_DIR
from catnap_diaries import CatNapDiaries

# Minimal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraMinimalCatWatch:
    def __init__(self):
        self.diaries = CatNapDiaries()
        self.running = False
        self.last_photo_path = None
        
    def test_raspistill(self):
        """Test if raspistill command works."""
        try:
            # Test raspistill with minimal settings
            test_cmd = [
                'raspistill',
                '-o', '/tmp/test_camera.jpg',
                '-w', '320',
                '-h', '240',
                '-q', '50',
                '-t', '1000',  # 1 second timeout
                '--nopreview'
            ]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Clean up test file
                if os.path.exists('/tmp/test_camera.jpg'):
                    os.remove('/tmp/test_camera.jpg')
                return True
            else:
                logger.error(f"raspistill failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("raspistill command timed out")
            return False
        except Exception as e:
            logger.error(f"Error testing raspistill: {e}")
            return False
    
    def capture_photo(self, width=320, height=240, quality=50):
        """Capture photo using raspistill command."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ultra_minimal_{timestamp}.jpg"
            filepath = os.path.join(PHOTOS_DIR, filename)
            
            cmd = [
                'raspistill',
                '-o', filepath,
                '-w', str(width),
                '-h', str(height),
                '-q', str(quality),
                '-t', '2000',  # 2 second capture
                '--nopreview'
            ]
            
            logger.info(f"Capturing photo: {width}x{height} quality={quality}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(filepath):
                file_size = os.path.getsize(filepath) / 1024  # KB
                logger.info(f"Photo captured: {filename} ({file_size:.1f} KB)")
                return filepath
            else:
                logger.error(f"Failed to capture photo: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Photo capture timed out")
            return None
        except Exception as e:
            logger.error(f"Error capturing photo: {e}")
            return None
    
    def detect_movement_simple(self):
        """
        Ultra-simple movement detection using timestamp comparison.
        For Pi Zero, we'll just take photos at intervals and assume movement.
        """
        # For ultra-minimal mode, assume there's always potential for cats
        # This bypasses complex image comparison that uses too much memory
        return True
    
    def run_ultra_minimal(self):
        """Run in ultra-minimal mode using raspistill."""
        logger.info("🚨 Starting ULTRA-MINIMAL mode")
        logger.info("Using raspistill command instead of OpenCV")
        logger.info("This bypasses all GStreamer memory issues")
        
        if not self.test_raspistill():
            logger.error("raspistill command not working")
            logger.error("Make sure camera is enabled: sudo raspi-config")
            return False
        
        logger.info("✅ raspistill working - starting monitoring")
        
        self.running = True
        photo_count = 0
        
        try:
            while self.running:
                logger.info(f"📸 Capture cycle {photo_count + 1}")
                
                # Capture a photo (no video stream, no memory issues)
                photo_path = self.capture_photo()
                
                if photo_path:
                    photo_count += 1
                    
                    # For ultra-minimal mode, assume every photo might have a cat
                    # This eliminates complex image processing that uses memory
                    logger.info("Assuming potential cat presence (ultra-minimal mode)")
                    
                    try:
                        # Generate and send email (simplified)
                        logger.info("Generating cat diary email...")
                        email_content = f"""Subject: 📸 CatNap Watch Update #{photo_count}

Hello from your CatNap Watch system!

I've captured photo #{photo_count} from your cat's monitoring area.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Mode: Ultra-Minimal (Pi Zero optimized)
Photo: {os.path.basename(photo_path)}

Since we're running in ultra-minimal mode to work around memory constraints, 
I'm sending you every photo I take. This ensures you don't miss any cat activity!

Your faithful Pi Zero,
CatNap Watch 🐱

P.S. - Thanks for being patient with my memory limitations!"""

                        success = self.diaries.send_email(email_content, photo_path)
                        if success:
                            logger.info("📧 Email sent successfully")
                        else:
                            logger.info("📧 Email printed to console")
                            
                    except Exception as e:
                        logger.error(f"Error with email: {e}")
                
                else:
                    logger.warning("Failed to capture photo")
                
                # Wait before next capture
                logger.info(f"⏳ Waiting {CAPTURE_INTERVAL} seconds...")
                time.sleep(CAPTURE_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Stopping ultra-minimal mode")
            self.running = False
        except Exception as e:
            logger.error(f"Error in ultra-minimal mode: {e}")
        
        logger.info(f"Ultra-minimal mode stopped. Captured {photo_count} photos.")

def main():
    """Run ultra-minimal cat watch."""
    print("🚨 CatNap Watch - ULTRA-MINIMAL MODE")
    print("=" * 40)
    print("This mode completely bypasses OpenCV and GStreamer:")
    print("  ✓ Uses raspistill command directly")
    print("  ✓ No video stream (no memory pressure)")
    print("  ✓ No complex image processing")
    print("  ✓ Takes photos at intervals")
    print("  ✓ Sends all photos (assumes cats)")
    print("")
    print("This is the absolute minimal approach for Pi Zero!")
    print("")
    
    try:
        input("Press ENTER to start ultra-minimal mode (Ctrl+C to exit)...")
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    watch = UltraMinimalCatWatch()
    watch.run_ultra_minimal()

if __name__ == "__main__":
    main()
