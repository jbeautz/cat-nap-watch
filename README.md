# CatNap Watch – Automated Cat Perch Monitoring 🐱📸
Overview

CatNap Watch is a Raspberry Pi project that monitors your cat’s favorite perch or bed. It captures photos at regular intervals, detects when something interesting happens, identifies the cat, and triggers AI-generated updates.

The CatNap Diaries component generates funny, personalized emails written from your cat’s perspective whenever activity is detected. Perfect for keeping up with your furry friend while you’re away—or just enjoying their daily antics!
Features

    Captures 1 photo per minute

    Detects significant changes compared to the last image

    Identifies if a cat is present

    Determines cat color: light or dark

    Saves photos with timestamps

    Sends AI-generated email updates (CatNap Diaries)

    Modular, easy to expand with better detection or 360° camera rotation

Setup

## Quick Setup for Raspberry Pi Zero

1. **Clone or download this project** to your Raspberry Pi:
```bash
cd /home/pi
git clone https://github.com/jbeautz/cat-nap-watch.git
cd cat-nap-watch
```

2. **Run the automated setup script**:
```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

3. **Configure your API key**:
```bash
cp .env.example .env
nano .env  # Add your OpenAI API key
```

4. **Test the installation**:
```bash
source catnap_env/bin/activate
python test_catnap.py
```

5. **Test camera and email** (recommended):
```bash
python test_camera_email.py
```

6. **Run CatNap Watch**:
```bash
python catnap_watch.py
```

## Manual Setup Steps

If you prefer manual installation:

1. **Install Python dependencies**:
```bash
pip install opencv-python openai python-dotenv
```

2. **Connect your Raspberry Pi camera** and enable it via raspi-config:
```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
```

3. **Set your OpenAI API key** in a `.env` file:
```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_actual_api_key_here
```

4. **Run the main CatNap Watch script**:
```bash
python catnap_watch.py
```

## Running as a Service (Optional)

To run CatNap Watch automatically on boot:

```bash
sudo cp catnap-watch.service /etc/systemd/system/
sudo systemctl enable catnap-watch
sudo systemctl start catnap-watch

# Check status
sudo systemctl status catnap-watch
```

How It Works

    Capture Image – The Pi takes a photo every minute.

    Detect Change – Compares the new frame with the last frame to see if it’s “interesting.”

    Cat Detection – Determines if a cat is present using simple heuristics or blob detection.

    Identify Cat Color – Light or dark, to personalize AI updates.

    Generate CatNap Diaries Email – Uses OpenAI API to create a funny, cat-perspective message.

    Save & Notify – Saves the photo and sends the AI-generated email.

Folder Structure

```
CatNapWatch/
├── README.md             # This overview
├── catnap_watch.py       # Main Pi loop: capture, detect, save, trigger
├── catnap_diaries.py     # AI email generation logic
├── config.py             # Thresholds, timing, API keys configuration
├── requirements.txt      # Python dependencies
├── setup_pi.sh           # Automated setup script for Raspberry Pi
├── test_catnap.py        # Test script to verify installation
├── test_camera_email.py  # Camera and email test with photo capture
├── catnap-watch.service  # Systemd service file for auto-start
├── .env.example          # Environment variables template
├── .env                  # Your actual environment variables (create this)
├── photos/               # Saved cat photos with timestamps
├── catnap_watch.log      # Application logs
└── docs/                 # Optional diagrams or guides
```

## Configuration

The `config.py` file contains all the adjustable settings:

- `CAPTURE_INTERVAL`: Time between captures (default: 60 seconds)
- `DIFF_THRESHOLD`: Motion sensitivity (default: 5000)
- `CAT_BRIGHTNESS_THRESHOLD`: Minimum brightness to detect cat presence
- `LIGHT_CAT_THRESHOLD`: Threshold to distinguish light vs dark cats

## Email Setup (Optional)

To receive actual emails instead of console output:

1. Add email credentials to your `.env` file:
```
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@gmail.com
```

2. For Gmail, create an App Password:
   - Enable 2FA on your Google account
   - Generate an App Password: https://support.google.com/accounts/answer/185833

## Testing

Run the comprehensive test suite to verify everything is working:

```bash
python test_catnap.py
```

This will test:
- Camera functionality
- Motion detection
- OpenAI API connection

**For a quick camera and email test:**

```bash
python test_camera_email.py
```

This focused test will:
- Take a test photo with your Pi camera
- Save it with timestamp
- Email the photo to you (if email is configured)
- Verify both camera and email functionality

This is perfect for quickly testing your hardware setup!

## Troubleshooting

**Camera Issues:**
- Ensure camera is properly connected and enabled: `sudo raspi-config`
- Check if camera is detected: `vcgencmd get_camera`
- Verify camera permissions for the pi user

**OpenAI API Issues:**
- Verify your API key in the `.env` file
- Check your OpenAI account has available credits
- Test API connection with `python test_catnap.py`

**Performance on Pi Zero:**
- The default settings are optimized for Pi Zero's limited resources
- Consider increasing `CAPTURE_INTERVAL` if the system is struggling
- Monitor system resources with `htop`

**False Detections:**
- Adjust `DIFF_THRESHOLD` in `config.py` for motion sensitivity
- Modify `CAT_BRIGHTNESS_THRESHOLD` for detection sensitivity
- Position camera to minimize lighting changes and moving shadows

## Future Improvements

    Upgrade cat detection with ML for higher accuracy

    Add 360° camera rotation with servo motors

    Track multiple cats individually

    Generate more personalized and frequent CatNap Diaries

Notes

    Adjust thresholds for motion detection to match lighting and environment

    OpenAI usage may incur costs beyond the free tier

    Email sending requires an SMTP or similar email service
