#!/usr/bin/env python3
"""
GUI Debug Test - Simulate exactly what the GUI does
"""

import subprocess
import sys
import os
import threading
import queue
import time

def test_gui_approach():
    """Test the exact same approach the GUI uses."""
    
    # Simulate GUI variables
    audio_file = "/Users/victoriakintanar/Python Projects/whispers/temp_recordings/recording_20250922_222926.wav"
    output_dir = "gui_test_output"
    
    print(f"Testing GUI approach with:")
    print(f"Audio file: {audio_file}")
    print(f"Output dir: {output_dir}")
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Build command exactly like GUI does
    python_exe = sys.executable
    cmd = [
        python_exe, "whisper_transcriber.py",
        audio_file,
        "--language", "en",
        "--model", "tiny", 
        "--device", "cpu",
        "--output-dir", output_dir,
        "--output-formats", "txt",
        "--verbose"
    ]
    
    print(f"\nCommand: {' '.join(cmd)}")
    print("\n" + "="*60)
    print("STARTING SUBPROCESS (GUI METHOD)")
    print("="*60)
    
    try:
        # Exactly what the GUI does
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        print("✓ Process started successfully")
        print("✓ Waiting for communicate()...")
        
        # Time the communicate() call
        start_time = time.time()
        stdout, _ = process.communicate()
        end_time = time.time()
        
        print(f"✓ communicate() finished in {end_time - start_time:.2f} seconds")
        print(f"✓ Return code: {process.returncode}")
        print(f"✓ stdout length: {len(stdout) if stdout else 0} characters")
        
        print("\n" + "="*60)
        print("SUBPROCESS OUTPUT:")
        print("="*60)
        
        if stdout:
            lines = stdout.split('\n')
            print(f"Total lines: {len(lines)}")
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"{i:3d}: {line}")
        else:
            print("❌ No stdout received!")
        
        print("\n" + "="*60)
        print("CHECKING OUTPUT FILES:")
        print("="*60)
        
        # Check if output files were created
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            if files:
                print(f"✓ Output files created: {files}")
                for file in files:
                    file_path = os.path.join(output_dir, file)
                    size = os.path.getsize(file_path)
                    print(f"  - {file}: {size} bytes")
            else:
                print("❌ No output files found in directory")
        else:
            print("❌ Output directory was not created")
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"❌ Exception during subprocess: {e}")
        return False

def test_gui_in_thread():
    """Test the GUI approach with threading like the actual GUI."""
    
    progress_queue = queue.Queue()
    
    def run_in_thread():
        """Run transcription in thread like GUI does."""
        try:
            # Same setup as above
            audio_file = "/Users/victoriakintanar/Python Projects/whispers/temp_recordings/recording_20250922_222926.wav"
            output_dir = "gui_thread_test_output"
            os.makedirs(output_dir, exist_ok=True)
            
            python_exe = sys.executable
            cmd = [
                python_exe, "whisper_transcriber.py",
                audio_file,
                "--language", "en",
                "--model", "tiny", 
                "--device", "cpu",
                "--output-dir", output_dir,
                "--output-formats", "txt",
                "--verbose"
            ]
            
            progress_queue.put(("output", f"Starting: {' '.join(cmd)}"))
            progress_queue.put(("progress", 10))
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            progress_queue.put(("status", "Process started, waiting for output..."))
            progress_queue.put(("progress", 20))
            
            stdout, _ = process.communicate()
            
            progress_queue.put(("status", f"Process finished with code: {process.returncode}"))
            
            if stdout:
                for line in stdout.split('\n'):
                    if line.strip():
                        progress_queue.put(("output", line.strip()))
                        if "loading" in line.lower():
                            progress_queue.put(("progress", 40))
                        elif "transcribing" in line.lower():
                            progress_queue.put(("progress", 70))
                        elif "saving" in line.lower():
                            progress_queue.put(("progress", 90))
                        elif "completed successfully" in line.lower():
                            progress_queue.put(("progress", 100))
            
            if process.returncode == 0:
                progress_queue.put(("status", "✅ Success!"))
            else:
                progress_queue.put(("status", f"❌ Failed with code {process.returncode}"))
                
        except Exception as e:
            progress_queue.put(("status", f"❌ Error: {e}"))
        finally:
            progress_queue.put(("done", None))
    
    print("\n" + "="*60)
    print("TESTING THREADED APPROACH (LIKE GUI)")
    print("="*60)
    
    # Start thread
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()
    
    # Monitor progress queue like GUI does
    start_time = time.time()
    while True:
        try:
            item = progress_queue.get(timeout=1)
            msg_type, data = item
            
            current_time = time.time() - start_time
            print(f"[{current_time:6.2f}s] {msg_type.upper()}: {data}")
            
            if msg_type == "done":
                break
                
        except queue.Empty:
            current_time = time.time() - start_time
            if current_time > 60:  # 60 second timeout
                print(f"[{current_time:6.2f}s] ❌ TIMEOUT: No progress for too long")
                break
            print(f"[{current_time:6.2f}s] QUEUE: Empty, waiting...")
    
    # Wait for thread to finish
    thread.join(timeout=5)
    
    print("\nThread test completed.")

if __name__ == "__main__":
    print("GUI Debugging Test")
    print("="*60)
    print("This script tests the exact same approach used by the GUI")
    print("to identify why progress monitoring isn't working.")
    print()
    
    # Test 1: Direct subprocess approach
    print("TEST 1: Direct subprocess (no threading)")
    success1 = test_gui_approach()
    
    # Test 2: Threaded approach like GUI
    print("\nTEST 2: Threaded approach (like GUI)")
    test_gui_in_thread()
    
    print("\n" + "="*60)
    print("DEBUGGING COMPLETE")
    print("="*60)
    if success1:
        print("✅ Basic subprocess works - issue might be in GUI threading/queue")
    else:
        print("❌ Basic subprocess fails - issue is in command or environment")