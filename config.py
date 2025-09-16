import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------
# Configuration Settings
# ---------------------------

# Camera settings (legacy interval-based capture)
CAPTURE_INTERVAL = 60  # seconds between captures
WARMUP_TIME = 2  # seconds for camera warmup

# Pi Zero specific camera optimizations
# Two-stage capture: low-res for motion detection, high-res for cat photos
MOTION_DETECTION_WIDTH = 160   # Very small for motion detection (75% less memory)
MOTION_DETECTION_HEIGHT = 120  # Very small for motion detection
PHOTO_CAPTURE_WIDTH = 640      # Higher resolution for saved cat photos
PHOTO_CAPTURE_HEIGHT = 480     # Higher resolution for saved cat photos
CAMERA_FPS = 1                 # Very low FPS for Pi Zero
CAMERA_BUFFER_SIZE = 1         # Minimal buffer to reduce memory usage

# Emergency low-memory settings (use if standard settings fail)
EMERGENCY_CAMERA_WIDTH = 160   # Ultra-low resolution
EMERGENCY_CAMERA_HEIGHT = 120  # Ultra-low resolution
JPEG_QUALITY = 70              # Compressed image quality to save memory

# Motion detection thresholds (legacy frame-diff)
DIFF_THRESHOLD = 5000  # adjust for motion sensitivity
MOTION_THRESHOLD = 50  # threshold for binary conversion in motion detection

# Cat detection settings
CAT_BRIGHTNESS_THRESHOLD = 50  # minimum brightness to assume cat presence
LIGHT_CAT_THRESHOLD = 100  # threshold to distinguish light vs dark cat

# ---------------------------
# New: PIR + USB camera configuration
# ---------------------------
# PIR motion sensor (BISS0001 module, e.g., HC-SR501)
# BCM pin number for PIR output (default GPIO17)
PIR_GPIO_PIN = int(os.getenv("PIR_GPIO_PIN", 17))

# USB camera device selection for OpenCV
# Set to specific index (e.g., 0 for /dev/video0); set to -1 to auto-scan 0-5
CAMERA_DEVICE_ID = int(os.getenv("CAMERA_DEVICE_ID", 0))

# Preferred capture resolution for USB cam (e.g., U20CAM-720P supports 1280x720)
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", 1280))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", 720))

# Try MJPG for better USB cam performance
USE_MJPG = os.getenv("USE_MJPG", "1") == "1"

# Delay after PIR triggers before capturing (let subject settle)
CAPTURE_DELAY_AFTER_MOTION = float(os.getenv("CAPTURE_DELAY_AFTER_MOTION", 0.6))

# Cooldown to avoid spamming captures when motion is continuous
MOTION_COOLDOWN_SECONDS = float(os.getenv("MOTION_COOLDOWN_SECONDS", 5.0))

# Save every motion shot even if no cat detected
SAVE_ALL_MOTION_SHOTS = os.getenv("SAVE_ALL_MOTION_SHOTS", "0") == "1"

# ---------------------------
# Baseline (no-cat) reference image comparison
# ---------------------------
# Path to the baseline "no cat" image used for comparisons
PHOTOS_DIR = "photos"
BASELINE_IMAGE_PATH = os.getenv("BASELINE_IMAGE_PATH", os.path.join(PHOTOS_DIR, "baseline_nocat.jpg"))

# Thresholds for baseline comparison
# Number of changed pixels (after diff+threshold) required to call it a cat/event
BASELINE_DIFF_THRESHOLD = int(os.getenv("BASELINE_DIFF_THRESHOLD", 30000))
# Binary threshold applied to absdiff; lower detects smaller changes
BASELINE_BINARY_THRESHOLD = int(os.getenv("BASELINE_BINARY_THRESHOLD", 30))
# Optional Gaussian blur kernel size (odd integer); 0 disables
BASELINE_BLUR_KERNEL = int(os.getenv("BASELINE_BLUR_KERNEL", 5))

# ---------------------------
# OpenAI settings
# ---------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# File paths
LOG_FILE = "catnap_watch.log"

# Photo management
MAX_STORED_PHOTOS = 50  # Maximum number of cat photos to keep
CLEANUP_INTERVAL_HOURS = 24  # How often to clean up old photos (hours)

# Email settings (placeholder for future implementation)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Ensure photos directory exists
os.makedirs(PHOTOS_DIR, exist_ok=True)
