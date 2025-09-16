import os
import time
import logging
from datetime import datetime

import cv2

try:
    import RPi.GPIO as GPIO
except Exception:
    # Allow development on non-Pi environments
    class _DummyGPIO:
        BCM = 'BCM'
        IN = 'IN'
        PUD_DOWN = 'PUD_DOWN'
        RISING = 'RISING'
        BOTH = 'BOTH'
        def setmode(self, *_): pass
        def setup(self, *_ , **__): pass
        def input(self, *_ , **__): return 0
        def add_event_detect(self, *_, **__): pass
        def remove_event_detect(self, *_, **__): pass
        def cleanup(self): pass
    GPIO = _DummyGPIO()

from config import (
    PIR_GPIO_PIN,
    CAMERA_DEVICE_ID,
    FRAME_WIDTH, FRAME_HEIGHT,
    USE_MJPG,
    CAPTURE_DELAY_AFTER_MOTION,
    MOTION_COOLDOWN_SECONDS,
    SAVE_ALL_MOTION_SHOTS,
    LIGHT_CAT_THRESHOLD,
    CAT_BRIGHTNESS_THRESHOLD,
    PHOTOS_DIR,
    LOG_FILE,
    MAX_STORED_PHOTOS,
    CLEANUP_INTERVAL_HOURS,
    # New baseline comparison settings
    BASELINE_IMAGE_PATH,
    BASELINE_DIFF_THRESHOLD,
    BASELINE_BINARY_THRESHOLD,
    BASELINE_BLUR_KERNEL,
    WARMUP_TIME,
)
from catnap_diaries import CatNapDiaries
from photo_manager import cleanup_old_photos

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PIRUSBCameraWatcher:
    def __init__(self):
        self.diaries = CatNapDiaries()
        self.cap = None
        self.last_motion_time = 0
        self.last_cleanup_time = time.time()
        self.baseline_gray = None

    def _try_configure_cap(self, cap, try_mjpg=True):
        if try_mjpg:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        else:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(0.3)
        # toss a couple frames
        for _ in range(2):
            cap.read()
        ret, frame = cap.read()
        return ret, frame

    def _open_camera(self):
        indices = range(0, 6) if CAMERA_DEVICE_ID < 0 else [CAMERA_DEVICE_ID]
        for idx in indices:
            logger.info(f"Trying to open camera /dev/video{idx}...")
            cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
            if not cap.isOpened():
                cap.release()
                continue
            # First try MJPG (fast), then fallback to YUYV if needed
            ret, frame = self._try_configure_cap(cap, try_mjpg=USE_MJPG)
            if not (ret and frame is not None):
                logger.info("MJPG failed to yield frames; trying YUYV...")
                ret, frame = self._try_configure_cap(cap, try_mjpg=False)
            if ret and frame is not None:
                logger.info(f"Camera opened: {frame.shape[1]}x{frame.shape[0]} on /dev/video{idx}")
                self.cap = cap
                return True
            cap.release()
        logger.error("Failed to open any usable USB camera")
        return False

    def _close_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def _capture_frame(self):
        if not self.cap:
            if not self._open_camera():
                return None
        # small warm-up each capture to refresh frame
        for _ in range(2):
            self.cap.read()
        ret, frame = self.cap.read()
        if ret:
            return frame
        # attempt reopen if stale
        logger.info("Read failed; reopening camera...")
        self._close_camera()
        if self._open_camera():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def _ensure_baseline(self):
        """Load baseline gray image from disk or capture and save if missing."""
        os.makedirs(os.path.dirname(BASELINE_IMAGE_PATH), exist_ok=True)
        if os.path.exists(BASELINE_IMAGE_PATH):
            img = cv2.imread(BASELINE_IMAGE_PATH)
            if img is not None:
                self.baseline_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                logger.info(f"Loaded baseline image: {BASELINE_IMAGE_PATH}")
                return True
            else:
                logger.warning("Baseline image exists but could not be read; recapturing...")
        # Capture new baseline
        logger.info("Capturing baseline 'no cat' image in current scene...")
        if not self.cap and not self._open_camera():
            logger.error("Cannot open camera to capture baseline")
            return False
        time.sleep(max(0.2, WARMUP_TIME))
        # discard a couple frames
        for _ in range(3):
            self.cap.read()
        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.error("Failed to capture baseline frame")
            return False
        if not cv2.imwrite(BASELINE_IMAGE_PATH, frame):
            logger.error("Failed to save baseline image")
            return False
        self.baseline_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        logger.info(f"Baseline saved to {BASELINE_IMAGE_PATH}")
        return True

    def _compare_to_baseline(self, frame):
        """Return count of changed pixels vs baseline using configured thresholds."""
        if self.baseline_gray is None:
            if not self._ensure_baseline():
                return 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if BASELINE_BLUR_KERNEL and BASELINE_BLUR_KERNEL % 2 == 1:
            gray = cv2.GaussianBlur(gray, (BASELINE_BLUR_KERNEL, BASELINE_BLUR_KERNEL), 0)
            base = cv2.GaussianBlur(self.baseline_gray, (BASELINE_BLUR_KERNEL, BASELINE_BLUR_KERNEL), 0)
        else:
            base = self.baseline_gray
        diff = cv2.absdiff(base, gray)
        _, thresh = cv2.threshold(diff, BASELINE_BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)
        changed = cv2.countNonZero(thresh)
        logger.info(f"Baseline diff changed pixels: {changed} (threshold: {BASELINE_DIFF_THRESHOLD})")
        return changed

    def _detect_cat(self, frame):
        # Kept for reference; not used when baseline comparison is enabled
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = gray.mean()
            if mean_brightness < CAT_BRIGHTNESS_THRESHOLD:
                return False
            blur = cv2.GaussianBlur(gray, (15, 15), 0)
            _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            min_area = 2000
            max_area = frame.shape[0] * frame.shape[1] * 0.6
            for c in contours:
                area = cv2.contourArea(c)
                if min_area < area < max_area:
                    return True
            return False
        except Exception as e:
            logger.error(f"Cat detection error: {e}")
            return False

    def _cat_color(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return 'light' if gray.mean() > LIGHT_CAT_THRESHOLD else 'dark'
        except Exception:
            return 'mysterious'

    def _save_photo(self, frame):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(PHOTOS_DIR, f'cat_{ts}.jpg')
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        if cv2.imwrite(path, frame):
            logger.info(f"Saved photo: {path}")
            return path
        logger.error("Failed to save photo")
        return None

    def _periodic_cleanup(self):
        now = time.time()
        if (now - self.last_cleanup_time) / 3600 >= CLEANUP_INTERVAL_HOURS:
            deleted = cleanup_old_photos(MAX_STORED_PHOTOS)
            if deleted:
                logger.info(f"Cleaned up {deleted} old photos")
            self.last_cleanup_time = now

    def _on_motion(self, channel=None):
        now = time.time()
        if now - self.last_motion_time < MOTION_COOLDOWN_SECONDS:
            return
        self.last_motion_time = now
        logger.info("Motion detected by PIR — capturing in a moment...")
        time.sleep(CAPTURE_DELAY_AFTER_MOTION)
        frame = self._capture_frame()
        if frame is None:
            logger.error("Capture failed")
            return
        # Compare against baseline image
        changed = self._compare_to_baseline(frame)
        is_cat = changed > BASELINE_DIFF_THRESHOLD
        if is_cat or SAVE_ALL_MOTION_SHOTS:
            path = self._save_photo(frame)
            color = self._cat_color(frame)
            self.diaries.create_and_send_update(color, path)
        else:
            logger.info("Change below threshold; not saving photo")
        self._periodic_cleanup()

    def run(self):
        try:
            logger.info("Setting up PIR sensor...")
            GPIO.setmode(GPIO.BCM)
            # Some BISS0001 modules idle LOW and pulse HIGH on motion; use pull-down to keep stable
            try:
                GPIO.setup(PIR_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            except TypeError:
                # Fallback for dummy or older RPi.GPIO
                GPIO.setup(PIR_GPIO_PIN, GPIO.IN)

            # Prime camera once and capture/load baseline
            if not self._open_camera():
                logger.error("Camera not available")
                return
            if not self._ensure_baseline():
                logger.error("Failed to initialize baseline image")
                return

            logger.info("Waiting for motion... (press Ctrl+C to stop)")
            # If add_event_detect isn't reliable in your environment, poll in a loop instead
            try:
                GPIO.add_event_detect(PIR_GPIO_PIN, GPIO.RISING, callback=self._on_motion, bouncetime=200)
                while True:
                    time.sleep(1)
            except Exception:
                # Polling fallback
                prev = 0
                while True:
                    cur = GPIO.input(PIR_GPIO_PIN)
                    if cur == 1 and prev == 0:
                        self._on_motion()
                    prev = cur
                    time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            self._close_camera()
            GPIO.cleanup()
            logger.info("Stopped.")

if __name__ == '__main__':
    PIRUSBCameraWatcher().run()
