#!/usr/bin/env python3
"""
Test script to verify transcription progress monitoring
"""

import sys
import subprocess
import os
from pathlib import Path

def test_transcription():
    """Test transcription with a recording file."""
    # Find a test audio file
    test_files = [
        "recordings/recording_20250922_221823.wav",
        "temp_recordings/recording_20250922_222128.wav"
    ]
    
    test_file = None
    for file in test_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if not test_file:
        print("No test audio files found. Please record some audio first.")
        return False
    
    print(f"Testing transcription with: {test_file}")
    print("This will test if progress output is working correctly.\n")
    
    # Build command using current Python executable
    python_exe = sys.executable
    cmd = [
        python_exe, "whisper_transcriber.py",
        test_file,
        "--language", "en",
        "--model", "tiny",  # Use tiny model for faster testing
        "--output-dir", "test_output",
        "--output-formats", "txt",
        "--verbose"
    ]
    
    print("Command:", ' '.join(cmd))
    print("\n" + "="*50)
    print("TRANSCRIPTION OUTPUT:")
    print("="*50)
    
    try:
        # Run the command and capture output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            universal_newlines=True
        )
        
        # Read output line by line to test progress monitoring
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"OUTPUT: {line.strip()}")
        
        return_code = process.wait()
        
        print("="*50)
        print(f"Process completed with exit code: {return_code}")
        
        if return_code == 0:
            print("✅ Transcription completed successfully!")
            print(f"Check the 'test_output' folder for results.")
            return True
        else:
            print("❌ Transcription failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running transcription: {e}")
        return False

if __name__ == "__main__":
    print("Testing Whisper Transcription Progress Monitoring")
    print("="*50)
    
    # Check if whisper_transcriber.py exists
    if not os.path.exists("whisper_transcriber.py"):
        print("❌ whisper_transcriber.py not found!")
        sys.exit(1)
    
    success = test_transcription()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("If you saw OUTPUT lines above, the progress monitoring is working.")
    else:
        print("\n❌ Test failed!")
        print("Check the error messages above for troubleshooting.")