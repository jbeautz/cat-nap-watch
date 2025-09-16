#!/usr/bin/env python3
"""
PIR Sensitivity Tuner for BISS0001 (e.g., HC-SR501)

Helps you adjust the potentiometers (sensitivity and time) while seeing live events.
- Prints rising events with timestamps
- Shows simple rolling counts to gauge noise
- Optional: blinks onboard ACT LED via sysfs (if available)

Usage:
  python pir_sensitivity_tuner.py  # uses default GPIO from config
  PIR_GPIO_PIN=27 python pir_sensitivity_tuner.py

Tips:
- Sensitivity pot controls detection range; time pot controls output high duration.
- Start with sensitivity mid, time short. Adjust sensitivity until you see reliable motion events without noise.
"""
import os
import sys
import time
from datetime import datetime

try:
    import RPi.GPIO as GPIO
except Exception:
    class _DummyGPIO:
        BCM = 'BCM'
        IN = 'IN'
        PUD_DOWN = 'PUD_DOWN'
        RISING = 'RISING'
        def setmode(self, *_): pass
        def setup(self, *_ , **__): pass
        def input(self, *_ , **__): return 0
        def add_event_detect(self, *_, **__): pass
        def cleanup(self): pass
    GPIO = _DummyGPIO()

from config import PIR_GPIO_PIN

LED_SYSFS = "/sys/class/leds/led0/trigger"

def blink_led_once():
    try:
        # This toggles the activity LED on many Pis by setting trigger to 'timer' briefly
        if os.path.exists(LED_SYSFS):
            with open(LED_SYSFS, 'w') as f:
                f.write('timer')
            time.sleep(0.1)
            with open(LED_SYSFS, 'w') as f:
                f.write('mmc0')
    except Exception:
        pass


def main():
    pin = PIR_GPIO_PIN
    if len(sys.argv) > 1:
        try:
            pin = int(sys.argv[1])
        except ValueError:
            pass

    print(f"PIR Sensitivity Tuner on GPIO{pin} (BCM). Press Ctrl+C to stop.")
    print("- Adjust sensitivity pot; you should see events when moving at desired range")
    print("- Adjust time pot to set how long the output stays HIGH (event duration)")

    try:
        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        except TypeError:
            GPIO.setup(pin, GPIO.IN)

        events = 0
        last_event = 0
        window = []  # timestamps of last N events
        N = 10

        def on_event(_):
            nonlocal events, last_event, window
            now = time.time()
            events += 1
            last_event = now
            window.append(now)
            if len(window) > N:
                window.pop(0)
            ts = datetime.fromtimestamp(now).strftime('%H:%M:%S')
            print(f"[{ts}] Motion event! count={events} rate(last {N})={len(window)}")
            blink_led_once()

        try:
            GPIO.add_event_detect(pin, GPIO.RISING, callback=on_event, bouncetime=150)
            while True:
                time.sleep(0.5)
        except Exception:
            prev = 0
            while True:
                cur = GPIO.input(pin)
                if cur == 1 and prev == 0:
                    on_event(None)
                prev = cur
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping tuner.")
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
