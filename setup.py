#!/usr/bin/env python3
"""
Whisper Transcription Setup Script
=================================

This script helps set up the Whisper transcription environment and
verifies that everythi    print("Next steps:")
    print("1. Test the installation:")
    print("   python whisper_transcriber.py --info")
    print("2. Run the demo:")
    print("   python demo.py")
    print("3. Transcribe your first audio file:")
    print("   python whisper_transcriber.py your_audio.mp3")
    print("\nFor help: python whisper_transcriber.py --help")rking correctly.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description="", check=True):
    """Run a command and return the result."""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is too old")
        print("Please upgrade to Python 3.8 or higher")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\nChecking FFmpeg...")
    if run_command("ffmpeg -version", "Checking FFmpeg installation", check=False):
        print("✓ FFmpeg is installed")
        return True
    else:
        print("✗ FFmpeg not found")
        print("Please install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return False


def install_requirements():
    """Install Python requirements."""
    print("\nInstalling Python requirements...")
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("✗ requirements.txt not found")
        return False
    
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements"
    )
    
    if success:
        print("✓ Requirements installed successfully")
    else:
        print("✗ Failed to install requirements")
    
    return success


def test_imports():
    """Test if all required modules can be imported."""
    print("\nTesting module imports...")
    
    modules = [
        ("torch", "PyTorch"),
        ("whisper", "OpenAI Whisper"),
        ("librosa", "Librosa"),
        ("soundfile", "SoundFile"),
        ("numpy", "NumPy")
    ]
    
    all_good = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✓ {name} imported successfully")
        except ImportError:
            print(f"✗ {name} import failed")
            all_good = False
    
    return all_good


def test_gpu():
    """Test GPU availability."""
    print("\nTesting GPU availability...")
    try:
        import torch
        
        # Test CUDA
        if torch.cuda.is_available():
            print(f"✓ CUDA GPU available: {torch.cuda.get_device_name()}")
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("- CUDA GPU not available")
        
        # Test MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✓ Apple Silicon GPU (MPS) available")
        else:
            print("- Apple Silicon GPU (MPS) not available")
        
        if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
            print("- Using CPU (transcription will be slower)")
        
        return True
    except ImportError:
        print("✗ Cannot test GPU - PyTorch not installed")
        return False


def test_whisper():
    """Test if Whisper can load a model."""
    print("\nTesting Whisper model loading...")
    try:
        import whisper
        print("Loading tiny model for testing...")
        _ = whisper.load_model("tiny")  # Just test loading, don't need to store
        print("✓ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to load Whisper model: {e}")
        return False


def main():
    """Main setup function."""
    print("Whisper Transcription Setup")
    print("=" * 30)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_ffmpeg():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Test imports
    if not test_imports():
        print("\nSome modules failed to import. Try:")
        print("pip install --upgrade -r requirements.txt")
        return False
    
    # Test GPU
    test_gpu()
    
    # Test Whisper
    if not test_whisper():
        return False
    
    # Final success message
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Your Whisper transcription environment is ready!")
    print("\nNext steps:")
    print("1. Test the installation:")
    print("   python whisper.py --info")
    print("2. Run the demo:")
    print("   python demo.py")
    print("3. Transcribe your first audio file:")
    print("   python whisper.py your_audio.mp3")
    print("\nFor help: python whisper.py --help")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)