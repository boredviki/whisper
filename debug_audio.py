#!/usr/bin/env python3
"""
Debug script to test problematic audio file
"""

import subprocess
import sys
import time
import signal
import os

def test_file(audio_file):
    """Test transcription of a specific file with timeout and debugging."""
    print(f"Testing file: {audio_file}")
    
    if not os.path.exists(audio_file):
        print(f"File does not exist: {audio_file}")
        return False
    
    # Get file size
    file_size = os.path.getsize(audio_file)
    print(f"File size: {file_size:,} bytes")
    
    # Build command
    python_exe = sys.executable
    cmd = [
        python_exe, "whisper_transcriber.py",
        audio_file,
        "--language", "en",
        "--model", "tiny",
        "--output-dir", "debug_output",
        "--output-formats", "txt",
        "--device", "cpu",
        "--verbose"
    ]
    
    print("Command:", ' '.join(cmd))
    print("\nStarting transcription...")
    print("=" * 50)
    
    try:
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor output with timeout
        start_time = time.time()
        output_lines = []
        
        while True:
            # Check if process is done
            return_code = process.poll()
            if return_code is not None:
                print(f"\nProcess completed with return code: {return_code}")
                break
            
            # Check timeout (30 seconds)
            if time.time() - start_time > 30:
                print("\n⚠️ TIMEOUT: Process taking too long, terminating...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                return False
            
            # Read output
            try:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        print(f"OUTPUT: {line}")
                        output_lines.append(line)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        print("=" * 50)
        print(f"Total output lines: {len(output_lines)}")
        
        if return_code == 0:
            print("✅ SUCCESS: Transcription completed")
            return True
        else:
            print(f"❌ FAILED: Exit code {return_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    # Test the problematic file
    problematic_file = "/Users/victoriakintanar/Python Projects/whispers/temp_recordings/recording_20250922_222926.wav"
    
    print("Debug Audio File Transcription")
    print("=" * 50)
    
    success = test_file(problematic_file)
    
    if not success:
        print("\n" + "=" * 50)
        print("DEBUGGING SUGGESTIONS:")
        print("1. Try with a different model (base, small)")
        print("2. Try without language specification")
        print("3. Check if the audio file is corrupted")
        print("4. Try re-recording the audio")