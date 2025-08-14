# CatNap Watch – Automated Cat Perch Monitoring 🐱📸
Overview

CatNap Watch is a Raspberry Pi projecHow It Works

CatNap Watch uses a **memory-efficient two-stage capture system** optimized for Pi Zero:

**Stage 1 - Motion Detection (Low Memory):**
- Captures at 160x120 resolution in grayscale (~0.02 MB per frame)
- Compares with previous frame to detect interesting activity
- Uses minimal RAM for continuous monitoring

**Stage 2 - Cat Photography (High Quality):**
- Only when motion detected, switches to 640x480 full color
- Analyzes for cat presence and characteristics  
- Saves high-quality photos and sends AI-generated emails
- Switches back to low-resolution for next cycle

This approach uses **~95% less memory** during normal monitoring while still capturing high-quality cat photos when needed!rs your cat’s favorite perch or bed. It captures photos at regular intervals, detects when something interesting happens, identifies the cat, and triggers AI-generated updates.

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
├── optimize_pi_zero.sh   # Pi Zero memory optimization script
├── test_catnap.py        # Test script to verify installation
├── test_camera_email.py  # Camera and email test with photo capture
├── test_minimal_camera.py # Minimal memory camera test
├── test_two_stage_capture.py # Two-stage capture system test
├── test_raspistill.py    # Direct camera command test (bypasses OpenCV)
├── catnap_watch_lowmem.py # Emergency low-memory version
├── catnap_watch_ultra_minimal.py # Ultra-minimal using raspistill command
├── photo_manager.py      # Photo storage management utility
├── emergency_memory_liberation.sh # Maximum memory freeing script
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
- `MAX_STORED_PHOTOS`: Maximum number of cat photos to keep (default: 50)
- `CLEANUP_INTERVAL_HOURS`: How often to clean up old photos (default: 24 hours)

## Memory Optimization for Pi Zero

The Raspberry Pi Zero has only 512MB of RAM, requiring special memory management:

1. **Two-Stage Capture System**: The main application uses 160x120 grayscale for motion detection and 640x480 color only for cat photos (95% memory reduction)
2. **Emergency Fallback Versions**: Multiple fallback versions for different memory constraints
3. **System Optimization**: Scripts to disable unnecessary services and maximize available memory

### If Standard Version Fails with Memory Errors

If you get GStreamer allocation errors, try these solutions in order:

1. **First try the ultra-minimal version** (bypasses OpenCV entirely):
```bash
python test_raspistill.py  # Test if camera works with raspistill
python catnap_watch_ultra_minimal.py  # Run ultra-minimal version
```

2. **If still failing, run emergency memory liberation**:
```bash
chmod +x emergency_memory_liberation.sh
./emergency_memory_liberation.sh
sudo reboot
```

3. **After reboot, try ultra-minimal version again**:
```bash
python catnap_watch_ultra_minimal.py
```

The ultra-minimal version:
- Uses `raspistill` command instead of OpenCV
- Takes photos at regular intervals (assumes all photos contain cats)
- Much lower memory usage but no real-time motion detection

## Photo Management

CatNap Watch automatically manages photo storage to prevent filling up your Pi's storage:

- **Only saves photos when cats are detected** (not every frame)
- **Automatic cleanup**: Removes old photos when limit is reached
- **Smart comparison**: Each new frame is compared to the most recent interesting frame
- **Email attachments**: Cat photos are included in email notifications

**Manual photo management:**
```bash
# View storage information
python photo_manager.py --info

# Clean up old photos (keeps newest 50)
python photo_manager.py --cleanup

# Preview what would be deleted
python photo_manager.py --cleanup --dry-run

# Custom photo limit
python photo_manager.py --cleanup --max-photos 25
```

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

**For minimal memory testing:**

```bash
python test_minimal_camera.py
```

**For two-stage capture testing:**

```bash
python test_two_stage_capture.py
```

The tests will:
- **test_catnap.py**: Complete system test (camera, AI, email)
- **test_camera_email.py**: Camera + email test with normal resolution  
- **test_minimal_camera.py**: Ultra-low memory camera test (160x120)
- **test_two_stage_capture.py**: Memory-efficient two-stage system test

Start with `test_two_stage_capture.py` to see the memory savings in action!

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

**GStreamer Memory Issues:**
If you get "GStreamer warning - failed to allocate enough memory":

⚠️  **IMPORTANT**: Pi Zero has only 512MB RAM. Success isn't guaranteed.

**Step 1 - Try optimizations:**
1. Run the Pi Zero optimization script: `./optimize_pi_zero.sh`
2. Reboot your Pi: `sudo reboot`
3. Test with minimal settings: `python test_minimal_camera.py`

**Step 2 - If still failing:**
1. Use emergency low-memory mode: `python catnap_watch_lowmem.py`
2. This uses 160x120 resolution and minimal features
3. Monitor memory: `./monitor_memory.sh`

**Step 3 - If nothing works:**
- Consider Pi Zero 2W (4x more RAM) 
- Use USB camera instead of CSI camera
- Run without AI features (photos only)

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
