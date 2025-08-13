CatNap Watch – Automated Cat Perch Monitoring 🐱📸
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

    Install Python dependencies:

pip install opencv-python openai

    Connect your Raspberry Pi camera and enable it via raspi-config.

    Set your OpenAI API key in the environment:

export OPENAI_API_KEY="your_api_key_here"

    Run the main CatNap Watch script:

python catnap_watch.py

How It Works

    Capture Image – The Pi takes a photo every minute.

    Detect Change – Compares the new frame with the last frame to see if it’s “interesting.”

    Cat Detection – Determines if a cat is present using simple heuristics or blob detection.

    Identify Cat Color – Light or dark, to personalize AI updates.

    Generate CatNap Diaries Email – Uses OpenAI API to create a funny, cat-perspective message.

    Save & Notify – Saves the photo and sends the AI-generated email.

Folder Structure (Suggested)

CatNapWatch/
├── README.md             # This overview
├── catnap_watch.py       # Main Pi loop: capture, detect, save, trigger
├── catnap_diaries.py     # AI email generation logic
├── photos/               # Saved cat photos with timestamps
├── config.py             # Thresholds, timing, API keys
├── requirements.txt      # Python dependencies
└── docs/                 # Optional diagrams or guides

Future Improvements

    Upgrade cat detection with ML for higher accuracy

    Add 360° camera rotation with servo motors

    Track multiple cats individually

    Generate more personalized and frequent CatNap Diaries

Notes

    Adjust thresholds for motion detection to match lighting and environment

    OpenAI usage may incur costs beyond the free tier

    Email sending requires an SMTP or similar email service
