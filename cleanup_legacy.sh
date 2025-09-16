#!/bin/bash
set -e

# Cleanup legacy files not needed for PIR + USB camera configuration

echo "🧹 Cleaning up legacy files..."

files=(
  "catnap_watch.py"
  "catnap_watch_lowmem.py"
  "catnap_watch_ultra_minimal.py"
  "test_two_stage_capture.py"
  "test_minimal_camera.py"
  "test_raspistill.py"
  "test_catnap.py"
  "test_camera_commands.py"
  "test_video_devices.py"
  "emergency_memory_liberation.sh"
  "optimize_pi_zero.sh"
)

for f in "${files[@]}"; do
  if [ -e "$f" ]; then
    rm -f "$f"
    echo "  Removed $f"
  else
    echo "  Skipped $f (not found)"
  fi
done

echo "✅ Cleanup complete. Remaining files are focused on PIR + USB workflow."
