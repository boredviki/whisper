#!/usr/bin/env python3
"""
Simple test script to check if Whisper transcription works
"""

import whisper
import sys
import os

def test_whisper():
    print("Loading Whisper tiny model...")
    model = whisper.load_model("tiny")
    
    audio_file = "recordings/recording_20250922_221823.wav"
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return False
    
    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)
    
    print("Transcription completed!")
    print("Text:", result["text"])
    
    return True

if __name__ == "__main__":
    try:
        success = test_whisper()
        print("Test result:", "SUCCESS" if success else "FAILED")
    except Exception as e:
        print("Test FAILED with error:", str(e))