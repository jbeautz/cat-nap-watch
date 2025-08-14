import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------
# Configuration Settings
# ---------------------------

# Camera settings
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

# Motion detection thresholds
DIFF_THRESHOLD = 5000  # adjust for motion sensitivity
MOTION_THRESHOLD = 50  # threshold for binary conversion in motion detection

# Cat detection settings
CAT_BRIGHTNESS_THRESHOLD = 50  # minimum brightness to assume cat presence
LIGHT_CAT_THRESHOLD = 100  # threshold to distinguish light vs dark cat

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# File paths
PHOTOS_DIR = "photos"
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
