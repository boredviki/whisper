#!/usr/bin/env python3
"""
Test script to verify the system info functionality works correctly.
"""

import sys
import io
from contextlib import redirect_stdout

# Import the functions directly
try:
    from whisper_transcriber import print_system_info, print_language_info
    
    print("Testing system info functionality...")
    print("=" * 50)
    
    # Capture the output
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        print_system_info()
        print_language_info()
    
    # Get the captured output
    system_info_text = output_buffer.getvalue()
    
    print("System info captured successfully!")
    print("Output length:", len(system_info_text), "characters")
    print("\nFirst few lines of output:")
    print("-" * 30)
    print('\n'.join(system_info_text.split('\n')[:10]))
    print("-" * 30)
    print("✓ System info functionality is working correctly!")
    
except ImportError as e:
    print(f"❌ Failed to import system info functions: {e}")
except Exception as e:
    print(f"❌ Error testing system info: {e}")