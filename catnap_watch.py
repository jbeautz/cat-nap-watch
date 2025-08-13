import cv2
import time
import logging
from datetime import datetime
import os
from config import (
    CAPTURE_INTERVAL, WARMUP_TIME, DIFF_THRESHOLD, MOTION_THRESHOLD,
    CAT_BRIGHTNESS_THRESHOLD, LIGHT_CAT_THRESHOLD, PHOTOS_DIR, LOG_FILE
)
from catnap_diaries import CatNapDiaries

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
        self.last_frame = None
        self.diaries = CatNapDiaries()
        self.running = False
        
    def initialize_camera(self):
        """Initialize and configure the camera."""
        try:
            logger.info("Initializing camera...")
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                raise Exception("Failed to open camera")
            
            # Set camera properties for Pi Zero optimization
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 1)  # Low FPS for Pi Zero
            
            # Camera warmup
            logger.info(f"Camera warming up for {WARMUP_TIME} seconds...")
            time.sleep(WARMUP_TIME)
            
            # Capture baseline frame
            ret, self.last_frame = self.camera.read()
            if not ret:
                raise Exception("Failed to capture baseline image")
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False
    
    def is_interesting_frame(self, frame, threshold=DIFF_THRESHOLD):
        """
        Determine if the current frame is significantly different from the last frame.
        Returns True if frame shows interesting activity.
        """
        try:
            # Convert both frames to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_last = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate absolute difference
            diff = cv2.absdiff(gray_last, gray_frame)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)
            
            # Count non-zero pixels (changed pixels)
            changed_pixels = cv2.countNonZero(thresh)
            
            logger.debug(f"Changed pixels: {changed_pixels}, Threshold: {threshold}")
            return changed_pixels > threshold
            
        except Exception as e:
            logger.error(f"Error in motion detection: {e}")
            return False
    
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
    
    def process_cat_detection(self, frame):
        """Process a frame where a cat has been detected."""
        try:
            logger.info("Cat detected! Processing...")
            
            # Save the photo
            photo_path = self.save_cat_photo(frame)
            
            # Identify cat characteristics
            cat_color = self.identify_cat_color(frame)
            
            # Generate and send cat diary email
            logger.info(f"Generating CatNap Diaries email for {cat_color} cat...")
            success = self.diaries.create_and_send_update(cat_color, photo_path)
            
            if success:
                logger.info("CatNap Diaries email sent successfully!")
            else:
                logger.warning("Failed to send CatNap Diaries email")
                
        except Exception as e:
            logger.error(f"Error processing cat detection: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.camera:
            self.camera.release()
            logger.info("Camera released")
    
    def run(self):
        """Main monitoring loop."""
        try:
            logger.info("Starting CatNap Watch...")
            
            if not self.initialize_camera():
                logger.error("Failed to initialize camera. Exiting.")
                return False
            
            self.running = True
            logger.info(f"Monitoring started. Capturing every {CAPTURE_INTERVAL} seconds.")
            
            while self.running:
                try:
                    # Capture new frame
                    ret, frame = self.camera.read()
                    if not ret:
                        logger.warning("Failed to capture frame")
                        continue
                    
                    # Check if this frame shows interesting activity
                    if self.is_interesting_frame(frame):
                        logger.info("Interesting activity detected!")
                        
                        # Update our baseline
                        self.last_frame = frame.copy()
                        
                        # Check if a cat is present
                        if self.detect_cat_presence(frame):
                            self.process_cat_detection(frame)
                        else:
                            logger.info("Activity detected but no cat identified")
                    
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
