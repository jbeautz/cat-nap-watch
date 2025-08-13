#!/bin/bash

# Quick Start Script for CatNap Watch
# This script activates the virtual environment and starts the application

echo "🐱 Starting CatNap Watch..."

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

# Start the application
echo "🚀 Launching CatNap Watch..."
python catnap_watch.py
