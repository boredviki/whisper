#!/usr/bin/env python3
"""
Quick test script to verify the GUI device selection fix
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from whisper_mini import WhisperMini

def test_device_selection():
    """Test the device selection logic."""
    print("Testing device selection logic...")
    
    # Create a GUI instance (but don't show it)
    app = WhisperMini()
    
    # Test different device settings
    test_cases = ["auto", "cpu", "cuda", "mps"]
    
    for device in test_cases:
        app.device_var.set(device)
        resolved_device = app.get_optimal_device()
        print(f"Device '{device}' resolves to: '{resolved_device}'")
    
    # Test command building
    app.audio_file_var.set("test.wav")
    app.device_var.set("auto")
    
    try:
        cmd = app.build_command()
        print(f"\nSample command: {' '.join(cmd)}")
        
        # Check that 'auto' is not in the command
        if "auto" in cmd:
            print("❌ ERROR: 'auto' found in command - this will cause the error!")
        else:
            print("✅ SUCCESS: 'auto' properly resolved to specific device")
            
    except Exception as e:
        print(f"❌ ERROR building command: {e}")
    
    # Don't actually show the GUI
    app.root.destroy()

if __name__ == "__main__":
    test_device_selection()