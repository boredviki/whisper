#!/usr/bin/env python3
"""
Whisper GUI Launcher
===================

Simple launcher script for the Whisper transcription GUI.
Run this to start the graphical interface.
"""

import os
import sys
import subprocess


def main():
    """Launch the Whisper GUI."""
    print("🎤 Starting Whisper Transcription GUI...")
    
    # Check if we're in the right directory
    if not os.path.exists("whisper_gui.py"):
        print("❌ Error: whisper_gui.py not found in current directory.")
        print("Please run this launcher from the whispers project directory.")
        return 1
    
    if not os.path.exists("whisper_transcriber.py"):
        print("❌ Error: whisper_transcriber.py not found in current directory.")
        print("Please ensure you're in the whispers project directory.")
        return 1
    
    try:
        # Launch the GUI
        subprocess.run([sys.executable, "whisper_gui.py"], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching GUI: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 GUI launcher interrupted by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())