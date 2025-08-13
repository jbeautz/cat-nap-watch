#!/bin/bash

# CatNap Watch Log Monitor
# Displays real-time logs from the application

LOG_FILE="catnap_watch.log"

echo "🐱 CatNap Watch Log Monitor"
echo "Press Ctrl+C to exit"
echo "=========================="

if [ -f "$LOG_FILE" ]; then
    tail -f "$LOG_FILE"
else
    echo "Log file not found. Make sure CatNap Watch is running."
    echo "Looking for: $LOG_FILE"
fi
