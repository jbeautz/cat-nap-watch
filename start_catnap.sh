#!/bin/bash

# Quick Start Script for CatNap Watch (PIR + USB Camera)

echo "🐱 Starting CatNap Watch (PIR + USB Camera)..."

# Check if virtual environment exists
if [ ! -d "catnap_env" ]; then
    echo "❌ Virtual environment not found. Please run ./setup_pi.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your API key."
    exit 1
fi

# Activate virtual environment
source catnap_env/bin/activate

# Start the PIR + USB watcher
echo "🚀 Launching CatNap Watch (motion-triggered)..."
python catnap_watch_pir_usb.py
