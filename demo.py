#!/usr/bin/env python3
"""
Whisper Transcription Demo
=========================

This script demonstrates how to use the Whisper transcription tool programmatically
and provides examples of different usage patterns.

Run this script to see example commands and usage patterns.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and display it with description."""
    print(f"\n{'='*60}")
    print(f"DEMO: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    # Ask user if they want to run this command
    response = input("Run this command? (y/n/skip remaining): ").lower()
    
    if response == 'skip remaining' or response == 's':
        return False
    elif response == 'y' or response == 'yes':
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout:
                print("Output:")
                print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            if result.returncode != 0:
                print(f"Command failed with return code {result.returncode}")
        except Exception as e:
            print(f"Error running command: {e}")
    else:
        print("Skipped.")
    
    return True


def check_requirements():
    """Check if basic requirements are met."""
    print("Checking Requirements...")
    print("-" * 30)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if whisper_transcriber.py exists
    whisper_path = Path("whisper_transcriber.py")
    if whisper_path.exists():
        print("✓ whisper_transcriber.py found")
    else:
        print("✗ whisper_transcriber.py not found in current directory")
        return False
    
    # Check if requirements.txt exists
    req_path = Path("requirements.txt")
    if req_path.exists():
        print("✓ requirements.txt found")
    else:
        print("✗ requirements.txt not found")
    
    # Try to import required modules
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} installed")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  - GPU: {torch.cuda.get_device_name()}")
    except ImportError:
        print("✗ PyTorch not installed")
    
    try:
        import whisper
        print("✓ OpenAI Whisper installed")
    except ImportError:
        print("✗ OpenAI Whisper not installed")
        print("  Run: pip install openai-whisper")
    
    return True


def create_sample_commands():
    """Generate sample commands for demonstration."""
    
    commands = [
        {
            "command": "python whisper_transcriber.py --info",
            "description": "Show system information and capabilities",
            "note": "This shows your GPU status, supported languages, and system info"
        },
        {
            "command": "python whisper_transcriber.py --help",
            "description": "Show help and all available options",
            "note": "Complete reference of all command-line options"
        }
    ]
    
    # Add file-based commands if we have sample files
    sample_files = [
        "sample_audio.mp3",
        "sample_audio.wav", 
        "test_audio.m4a",
        "demo.flac"
    ]
    
    # Check if any sample audio files exist
    existing_files = [f for f in sample_files if Path(f).exists()]
    
    if existing_files:
        sample_file = existing_files[0]
        commands.extend([
            {
                "command": f"python whisper_transcriber.py {sample_file}",
                "description": f"Basic transcription of {sample_file}",
                "note": "Auto-detects language and uses default settings"
            },
            {
                "command": f"python whisper_transcriber.py {sample_file} --language en",
                "description": f"Transcribe {sample_file} as English",
                "note": "Explicitly set language for better accuracy"
            },
            {
                "command": f"python whisper_transcriber.py {sample_file} --language tl",
                "description": f"Transcribe {sample_file} as Tagalog",
                "note": "Specify Tagalog language"
            },
            {
                "command": f"python whisper_transcriber.py {sample_file} --task translate",
                "description": f"Translate {sample_file} to English",
                "note": "Translate any language to English"
            },
            {
                "command": f"python whisper_transcriber.py {sample_file} --model medium",
                "description": "Use medium model for faster processing",
                "note": "Trade accuracy for speed"
            },
            {
                "command": f"python whisper_transcriber.py {sample_file} --output-formats txt json srt vtt",
                "description": "Save in multiple formats",
                "note": "Creates text, JSON, SRT subtitle, and VTT files"
            },
            {
                "command": f"python whisper_transcriber.py {sample_file} --device cpu",
                "description": "Force CPU usage",
                "note": "Useful if GPU has issues or insufficient memory"
            }
        ])
    else:
        print("\nNo sample audio files found. To test with actual audio:")
        print("1. Add an audio file (MP3, WAV, M4A, etc.) to this directory")
        print("2. Replace 'sample_audio.mp3' in the commands below with your file name")
        print("\nExample commands with your audio file:")
        commands.extend([
            {
                "command": "python whisper_transcriber.py YOUR_AUDIO.mp3",
                "description": "Basic transcription (replace YOUR_AUDIO.mp3 with your file)",
                "note": "Auto-detects language and uses default settings"
            },
            {
                "command": "python whisper_transcriber.py YOUR_AUDIO.mp3 --language en",
                "description": "Transcribe as English",
                "note": "Explicitly set language for better accuracy"
            },
            {
                "command": "python whisper_transcriber.py YOUR_AUDIO.mp3 --language tl",
                "description": "Transcribe as Tagalog",
                "note": "Specify Tagalog language"
            }
        ])
    
    return commands


def show_advanced_examples():
    """Show advanced usage patterns."""
    print(f"\n{'='*60}")
    print("ADVANCED USAGE EXAMPLES")
    print(f"{'='*60}")
    
    examples = [
        {
            "title": "Batch Processing with Shell Script",
            "code": """#!/bin/bash
# Process all MP3 files in current directory
for file in *.mp3; do
    echo "Processing: $file"
    python whisper_transcriber.py "$file" --language en --output-dir batch_results
done""",
            "description": "Process multiple files automatically"
        },
        {
            "title": "Python Integration",
            "code": """import subprocess
import json

# Transcribe and get JSON output
result = subprocess.run([
    'python', 'whisper_transcriber.py', 'audio.mp3', 
    '--output-formats', 'json', 
    '--output-dir', 'temp'
], capture_output=True)

# Load the results
with open('temp/audio_result.json') as f:
    transcription = json.load(f)
    
print(f"Detected language: {transcription['language']}")
print(f"Text: {transcription['text']}")""",
            "description": "Use from another Python script"
        },
        {
            "title": "Performance Optimization",
            "code": """# For large files, use smaller model first to check content
python whisper_transcriber.py large_file.mp3 --model small --output-formats txt

# Then use large model only if needed
python whisper_transcriber.py large_file.mp3 --model large-v3 --output-formats json srt""",
            "description": "Two-stage processing for efficiency"
        },
        {
            "title": "Subtitle Creation Workflow",
            "code": """# Create subtitles with precise timing
python whisper_transcriber.py video_audio.wav --output-formats srt vtt --language en

# The .srt file can be used with video players
# The .vtt file can be used for web video""",
            "description": "Generate subtitles for video content"
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print("-" * len(example['title']))
        print(f"Description: {example['description']}")
        print("Code:")
        print(example['code'])


def show_troubleshooting():
    """Show common troubleshooting steps."""
    print(f"\n{'='*60}")
    print("TROUBLESHOOTING GUIDE")
    print(f"{'='*60}")
    
    issues = [
        {
            "problem": "ModuleNotFoundError: No module named 'whisper'",
            "solution": "pip install openai-whisper"
        },
        {
            "problem": "CUDA out of memory",
            "solutions": [
                "Use smaller model: --model medium or --model small",
                "Use CPU: --device cpu",
                "Close other GPU applications"
            ]
        },
        {
            "problem": "FFmpeg not found",
            "solutions": [
                "macOS: brew install ffmpeg",
                "Ubuntu: sudo apt install ffmpeg", 
                "Windows: Download from ffmpeg.org"
            ]
        },
        {
            "problem": "Slow transcription",
            "solutions": [
                "Check GPU usage: python whisper_transcriber.py --info",
                "Use smaller model: --model medium",
                "Ensure CUDA/PyTorch GPU support is installed"
            ]
        },
        {
            "problem": "Poor accuracy",
            "solutions": [
                "Specify language: --language en or --language tl",
                "Use larger model: --model large-v3",
                "Ensure good audio quality",
                "Check if audio has background noise"
            ]
        }
    ]
    
    for issue in issues:
        print(f"\nProblem: {issue['problem']}")
        if 'solution' in issue:
            print(f"Solution: {issue['solution']}")
        elif 'solutions' in issue:
            print("Solutions:")
            for solution in issue['solutions']:
                print(f"  - {solution}")


def main():
    """Main demo function."""
    print("Whisper Transcription Tool - Demo & Examples")
    print("=" * 50)
    
    # Check requirements first
    if not check_requirements():
        print("\nPlease install missing requirements before proceeding.")
        print("Run: pip install -r requirements.txt")
        return
    
    # Show sample commands
    print(f"\n{'='*60}")
    print("INTERACTIVE DEMO")
    print(f"{'='*60}")
    print("This demo will show you various ways to use the Whisper transcription tool.")
    print("You can choose to run each command or skip it.")
    
    commands = create_sample_commands()
    
    continue_demo = True
    for cmd_info in commands:
        if not continue_demo:
            break
            
        print(f"\nNote: {cmd_info['note']}")
        continue_demo = run_command(cmd_info['command'], cmd_info['description'])
    
    # Show advanced examples
    show_advanced_examples()
    
    # Show troubleshooting
    show_troubleshooting()
    
    print(f"\n{'='*60}")
    print("DEMO COMPLETE")
    print(f"{'='*60}")
    print("For more information:")
    print("- Read README.md for detailed documentation")
    print("- Run: python whisper_transcriber.py --help")
    print("- Run: python whisper_transcriber.py --info")


if __name__ == "__main__":
    main()