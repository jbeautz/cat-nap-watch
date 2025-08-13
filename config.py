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

# Email settings (placeholder for future implementation)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# Ensure photos directory exists
os.makedirs(PHOTOS_DIR, exist_ok=True)
