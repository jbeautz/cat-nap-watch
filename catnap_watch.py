import cv2
import time
import logging
from datetime import datetime
import os
from config import (
    CAPTURE_INTERVAL, WARMUP_TIME, DIFF_THRESHOLD, MOTION_THRESHOLD,
    CAT_BRIGHTNESS_THRESHOLD, LIGHT_CAT_THRESHOLD, PHOTOS_DIR, LOG_FILE,
    MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT, 
    PHOTO_CAPTURE_WIDTH, PHOTO_CAPTURE_HEIGHT,
    CAMERA_FPS, CAMERA_BUFFER_SIZE,
    MAX_STORED_PHOTOS, CLEANUP_INTERVAL_HOURS
)
from catnap_diaries import CatNapDiaries
from photo_manager import cleanup_old_photos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CatNapWatch:
    def __init__(self):
        """Initialize the CatNap Watch system."""
        self.camera = None
        self.last_frame_gray = None  # Store grayscale for motion detection
        self.diaries = CatNapDiaries()
        self.running = False
        self.last_cleanup_time = time.time()  # Track when we last cleaned up photos
        
    def set_camera_resolution(self, width, height):
        """Change camera resolution dynamically."""
        if self.camera and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            # Small delay to allow camera to adjust
            time.sleep(0.1)
        
    def initialize_camera(self):
        """Initialize and configure the camera with Pi Zero optimizations."""
        try:
            logger.info("Initializing camera with two-stage capture optimization...")
            
            # Use CAP_V4L2 backend for better Pi compatibility
            self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
            
            if not self.camera.isOpened():
                # Fallback to default backend
                logger.warning("V4L2 backend failed, trying default...")
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    raise Exception("Failed to open camera with any backend")
            
            # Start with low resolution for motion detection (saves RAM)
            self.set_camera_resolution(MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)
            
            # Additional Pi Zero optimizations
            self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            # Verify settings
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.info(f"Motion detection resolution: {int(actual_width)}x{int(actual_height)}")
            
            # Camera warmup
            logger.info(f"Camera warming up for {WARMUP_TIME} seconds...")
            time.sleep(WARMUP_TIME)
            
            # Capture and discard a few frames to stabilize
            for i in range(3):
                ret, _ = self.camera.read()
                if ret:
                    time.sleep(0.1)
            
            # Capture baseline frame in grayscale (saves memory)
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Failed to capture baseline image")
            
            self.last_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            del frame  # Immediate cleanup of color frame
            
            logger.info(f"Camera initialized - baseline: {self.last_frame_gray.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False
    
    def is_interesting_frame(self, frame_gray, threshold=DIFF_THRESHOLD):
        """
        Determine if the current frame is significantly different from the last frame.
        Uses grayscale images for memory efficiency.
        Returns True if frame shows interesting activity.
        """
        try:
            if self.last_frame_gray is None:
                return False
            
            # Calculate absolute difference between grayscale frames
            diff = cv2.absdiff(self.last_frame_gray, frame_gray)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)
            
            # Count non-zero pixels (changed pixels)
            changed_pixels = cv2.countNonZero(thresh)
            
            logger.debug(f"Changed pixels: {changed_pixels}, Threshold: {threshold}")
            return changed_pixels > threshold
            
        except Exception as e:
            logger.error(f"Error in motion detection: {e}")
            return False
    
    def capture_high_res_photo(self):
        """
        Switch to high resolution and capture a photo for saving/analysis.
        Returns the high-res frame or None if failed.
        """
        try:
            logger.info("Switching to high resolution for cat photo...")
            
            # Switch to high resolution
            self.set_camera_resolution(PHOTO_CAPTURE_WIDTH, PHOTO_CAPTURE_HEIGHT)
            
            # Give camera time to adjust and stabilize
            time.sleep(0.5)
            
            # Capture a few frames to ensure we get a stable high-res image
            high_res_frame = None
            for i in range(3):
                ret, frame = self.camera.read()
                if ret:
                    high_res_frame = frame
                time.sleep(0.1)
            
            # Switch back to low resolution for next motion detection cycle
            self.set_camera_resolution(MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT)
            
            if high_res_frame is not None:
                actual_width = high_res_frame.shape[1]
                actual_height = high_res_frame.shape[0]
                logger.info(f"Captured high-res photo: {actual_width}x{actual_height}")
                return high_res_frame
            else:
                logger.error("Failed to capture high-res photo")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing high-res photo: {e}")
            # Ensure we switch back to low res even on error
            try:
                self.set_camera_resolution(MOTION_DETECTION_WIDTH, MOTION_DETECTION_HEIGHT)
            except:
                pass
            return None
    
    def detect_cat_presence(self, frame):
        """
        Simple cat detection based on image characteristics.
        Returns True if a cat is likely present.
        TODO: Replace with ML-based detection for better accuracy.
        """
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Simple heuristic: cats often change the overall brightness
            # and add organic shapes to the frame
            mean_brightness = gray.mean()
            
            # Check if brightness suggests presence of an object
            if mean_brightness > CAT_BRIGHTNESS_THRESHOLD:
                # Additional check: look for areas of consistent color/texture
                # that might indicate fur
                blur = cv2.GaussianBlur(gray, (15, 15), 0)
                _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Find contours (potential cat shapes)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Look for reasonably sized contours that could be a cat
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 1000 < area < 50000:  # Reasonable size range for a cat
                        logger.debug(f"Potential cat detected - area: {area}, brightness: {mean_brightness}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in cat detection: {e}")
            return False
    
    def identify_cat_color(self, frame):
        """
        Determine if the cat appears to be light or dark colored.
        Returns 'light' or 'dark'.
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = gray.mean()
            
            color = "light" if mean_brightness > LIGHT_CAT_THRESHOLD else "dark"
            logger.debug(f"Cat color identified as: {color} (brightness: {mean_brightness})")
            return color
            
        except Exception as e:
            logger.error(f"Error identifying cat color: {e}")
            return "mysterious"  # Fallback
    
    def save_cat_photo(self, frame):
        """Save the current frame as a timestamped photo."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cat_{timestamp}.jpg"
            filepath = os.path.join(PHOTOS_DIR, filename)
            
            success = cv2.imwrite(filepath, frame)
            if success:
                logger.info(f"Cat photo saved: {filepath}")
                return filepath
            else:
                logger.error("Failed to save photo")
                return None
                
        except Exception as e:
            logger.error(f"Error saving photo: {e}")
            return None
    
    def periodic_cleanup(self):
        """Perform periodic cleanup of old photos if needed."""
        current_time = time.time()
        hours_since_cleanup = (current_time - self.last_cleanup_time) / 3600
        
        if hours_since_cleanup >= CLEANUP_INTERVAL_HOURS:
            logger.info("Performing periodic photo cleanup...")
            deleted_count = cleanup_old_photos(MAX_STORED_PHOTOS)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old photos")
            self.last_cleanup_time = current_time
    
    def cleanup(self):
        """Clean up resources."""
        if self.camera:
            self.camera.release()
            logger.info("Camera released")
    
    def run(self):
        """Main monitoring loop with two-stage capture for memory efficiency."""
        try:
            logger.info("Starting CatNap Watch with two-stage capture...")
            
            if not self.initialize_camera():
                logger.error("Failed to initialize camera. Exiting.")
                return False
            
            self.running = True
            logger.info(f"Monitoring started. Low-res motion detection every {CAPTURE_INTERVAL} seconds.")
            logger.info(f"Motion detection: {MOTION_DETECTION_WIDTH}x{MOTION_DETECTION_HEIGHT}")
            logger.info(f"Cat photos: {PHOTO_CAPTURE_WIDTH}x{PHOTO_CAPTURE_HEIGHT}")
            
            while self.running:
                try:
                    # Stage 1: Capture low-resolution frame for motion detection (saves RAM)
                    ret, low_res_frame = self.camera.read()
                    if not ret:
                        logger.warning("Failed to capture motion detection frame")
                        continue
                    
                    # Convert to grayscale immediately to save memory
                    current_gray = cv2.cvtColor(low_res_frame, cv2.COLOR_BGR2GRAY)
                    del low_res_frame  # Immediate cleanup of color frame
                    
                    # Check if this frame shows interesting activity
                    is_interesting = self.is_interesting_frame(current_gray)
                    
                    if is_interesting:
                        logger.info("Interesting activity detected!")
                        
                        # Stage 2: Switch to high resolution for detailed analysis
                        high_res_frame = self.capture_high_res_photo()
                        
                        if high_res_frame is not None:
                            # Check if a cat is present in the high-res frame
                            cat_detected = self.detect_cat_presence(high_res_frame)
                            
                            if cat_detected:
                                logger.info("Cat detected in high-res frame!")
                                
                                # Save the high-res photo and send email
                                photo_path = self.save_cat_photo(high_res_frame)
                                cat_color = self.identify_cat_color(high_res_frame)
                                
                                logger.info(f"Generating CatNap Diaries email for {cat_color} cat...")
                                success = self.diaries.create_and_send_update(cat_color, photo_path)
                                
                                if success:
                                    logger.info("CatNap Diaries email sent successfully!")
                                else:
                                    logger.warning("Failed to send CatNap Diaries email")
                            else:
                                logger.info("Activity detected but no cat identified in high-res frame")
                            
                            # Clean up high-res frame
                            del high_res_frame
                        
                        # Update baseline to current low-res grayscale frame
                        if self.last_frame_gray is not None:
                            del self.last_frame_gray
                        self.last_frame_gray = current_gray.copy()
                        logger.debug("Updated motion detection baseline")
                        
                    else:
                        # No interesting activity - discard current frame
                        logger.debug("No significant changes detected - frame discarded")
                    
                    # Clean up current grayscale frame if not used as baseline
                    if not is_interesting:
                        del current_gray
                    
                    # Perform periodic cleanup of old photos
                    self.periodic_cleanup()
                    
                    # Wait before next capture
                    time.sleep(CAPTURE_INTERVAL)
                    
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal. Stopping...")
                    self.running = False
                    break
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(5)  # Brief pause before continuing
            
        except Exception as e:
            logger.error(f"Critical error in run loop: {e}")
            
        finally:
            self.cleanup()
            logger.info("CatNap Watch stopped")

def main():
    """Entry point for the CatNap Watch application."""
    watch = CatNapWatch()
    
    try:
        watch.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        watch.cleanup()

if __name__ == "__main__":
    main()
