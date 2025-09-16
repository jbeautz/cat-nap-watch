#!/usr/bin/env python3
"""
Test which camera commands are available on the system
"""
import subprocess
import sys

def test_command(command, description):
    """Test if a command is available"""
    print(f"\nTesting {description}...")
    try:
        result = subprocess.run([command, '--help'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0 or 'usage' in result.stdout.lower() or 'usage' in result.stderr.lower():
            print(f"✅ {command} is available")
            return True
        else:
            print(f"❌ {command} not available (return code: {result.returncode})")
            return False
    except FileNotFoundError:
        print(f"❌ {command} not found")
        return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  {command} timed out (might be available but hanging)")
        return False
    except Exception as e:
        print(f"❌ Error testing {command}: {e}")
        return False

def main():
    print("=== Camera Command Detection ===")
    
    commands_to_test = [
        ('raspistill', 'Legacy Raspberry Pi camera tool'),
        ('libcamera-still', 'Modern libcamera still capture'),
        ('libcamera-vid', 'Modern libcamera video capture'),
        ('rpicam-still', 'Newer rpicam still capture'),
        ('rpicam-vid', 'Newer rpicam video capture'),
    ]
    
    available_commands = []
    
    for command, description in commands_to_test:
        if test_command(command, description):
            available_commands.append(command)
    
    print(f"\n=== Summary ===")
    print(f"Available commands: {available_commands}")
    
    if 'libcamera-still' in available_commands:
        print("✅ Recommended: Use libcamera-still for photo capture")
    elif 'rpicam-still' in available_commands:
        print("✅ Recommended: Use rpicam-still for photo capture")
    elif 'raspistill' in available_commands:
        print("✅ Recommended: Use raspistill for photo capture (legacy)")
    else:
        print("❌ No camera commands found!")
        print("Try installing camera tools:")
        print("  sudo apt update")
        print("  sudo apt install libcamera-apps")
        print("  # OR for older systems:")
        print("  sudo apt install libraspberrypi-bin")
    
    return len(available_commands) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
