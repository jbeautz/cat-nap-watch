Legacy files (kept for reference)

These files were used for the original CSI camera + Pi Zero, two-stage capture, or ultra-minimal modes. They are not needed for the new PIR (BISS0001) + U20CAM-720P USB camera configuration and can be safely deleted if you no longer need them.

- catnap_watch.py (interval-based two-stage capture)
- catnap_watch_lowmem.py (ultra-low memory mode)
- catnap_watch_ultra_minimal.py (raspistill-based)
- test_two_stage_capture.py
- test_minimal_camera.py
- test_raspistill.py
- test_catnap.py (mixed tests; superseded by test_camera_email.py for basic check)
- test_camera_commands.py
- test_video_devices.py (was useful for debugging V4L2 indices)
- emergency_memory_liberation.sh
- optimize_pi_zero.sh

If you want this repository to only contain the PIR + USB workflow, you may delete the above files. The core files you need are:

- README.md
- config.py
- catnap_diaries.py
- catnap_watch_pir_usb.py
- requirements.txt
- setup_pi.sh
- start_catnap.sh
- catnap-watch.service
- photo_manager.py
- monitor_logs.sh
- .env.example
- photos/ (created at runtime)
- catnap_watch.log (created at runtime)
