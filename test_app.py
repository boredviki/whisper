#!/usr/bin/env python3
"""
Quick Test Script for Whisper Transcriber
==========================================

This script performs a quick test to verify that the Whisper transcription
environment is set up correctly.
"""

import subprocess
import sys


def test_application():
    """Test the main application functionality."""
    print("Testing Whisper Transcriber Application")
    print("=" * 40)
    
    # Test 1: Info command
    print("\n1. Testing system info command...")
    try:
        result = subprocess.run(
            ["python", "whisper_transcriber.py", "--info"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✓ Info command works correctly")
            print("Sample output:")
            print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"✗ Info command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error running info command: {e}")
        return False
    
    # Test 2: Help command
    print("\n2. Testing help command...")
    try:
        result = subprocess.run(
            ["python", "whisper_transcriber.py", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✓ Help command works correctly")
        else:
            print(f"✗ Help command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error running help command: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print("Your Whisper transcription application is ready to use!")
    print("\nTo transcribe an audio file:")
    print("  python whisper_transcriber.py your_audio_file.mp3")
    print("\nFor more options:")
    print("  python whisper_transcriber.py --help")
    print("\nTo run examples:")
    print("  python demo.py")
    
    return True


if __name__ == "__main__":
    if test_application():
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the setup.")
        sys.exit(1)