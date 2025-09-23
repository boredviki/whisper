#!/usr/bin/env python3
"""
Whisper Performance Test
========================

Test script to measure and compare transcription performance
with different models and settings.
"""

import time
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from whisper_fast import FastWhisperTranscriber
    fast_available = True
except ImportError:
    fast_available = False

try:
    from whisper_transcriber import WhisperTranscriber
    standard_available = True
except ImportError:
    standard_available = False


def test_audio_file():
    """Find a test audio file or create instructions."""
    test_files = []
    
    # Look for existing audio files
    for pattern in ["*.wav", "*.mp3", "*.m4a", "*.flac"]:
        test_files.extend(Path(".").glob(pattern))
        test_files.extend(Path("recordings").glob(pattern) if Path("recordings").exists() else [])
        test_files.extend(Path("temp_recordings").glob(pattern) if Path("temp_recordings").exists() else [])
    
    if test_files:
        return str(test_files[0])
    
    print("No audio files found for testing.")
    print("Please place a test audio file in the current directory or:")
    print("1. Use the GUI to record a short test audio")
    print("2. Copy an audio file to this directory")
    print("3. Specify a file path as an argument")
    return None


def run_performance_test(audio_file, models=None):
    """Run performance tests with different models."""
    if models is None:
        models = ["tiny", "base", "small"]
    
    print(f"Testing with audio file: {audio_file}")
    print(f"File size: {os.path.getsize(audio_file) / 1024 / 1024:.2f} MB")
    print("="*60)
    
    results = []
    
    for model in models:
        print(f"\nTesting {model} model...")
        print("-" * 30)
        
        try:
            if fast_available:
                # Test with optimized version
                print(f"🚀 Fast Transcriber ({model}):")
                transcriber = FastWhisperTranscriber(model_size=model, device="auto")
                
                start_time = time.time()
                result = transcriber.transcribe_audio_fast(audio_file, verbose=False)
                end_time = time.time()
                
                duration = end_time - start_time
                speed = result['metadata'].get('speed_ratio', 'unknown')
                
                print(f"   Time: {duration:.2f}s")
                print(f"   Speed: {speed}x real-time" if speed != 'unknown' else "   Speed: unknown")
                print(f"   Text length: {len(result['text'])} characters")
                
                results.append({
                    'model': model,
                    'type': 'fast',
                    'duration': duration,
                    'speed_ratio': speed,
                    'text_length': len(result['text'])
                })
        
        except Exception as e:
            print(f"   ❌ Error with fast transcriber: {e}")
        
        try:
            if standard_available:
                # Test with standard version
                print(f"📝 Standard Transcriber ({model}):")
                transcriber = WhisperTranscriber(model_size=model, device="auto")
                
                start_time = time.time()
                result = transcriber.transcribe_audio(audio_file, verbose=False)
                end_time = time.time()
                
                duration = end_time - start_time
                speed = result['metadata'].get('speed_ratio', 'unknown')
                
                print(f"   Time: {duration:.2f}s")
                print(f"   Speed: {speed}x real-time" if speed != 'unknown' else "   Speed: unknown")
                print(f"   Text length: {len(result['text'])} characters")
                
                results.append({
                    'model': model,
                    'type': 'standard',
                    'duration': duration,
                    'speed_ratio': speed,
                    'text_length': len(result['text'])
                })
        
        except Exception as e:
            print(f"   ❌ Error with standard transcriber: {e}")
    
    return results


def print_summary(results):
    """Print a summary of test results."""
    if not results:
        print("\nNo successful tests to summarize.")
        return
    
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    print(f"{'Model':<10} {'Type':<10} {'Time':<8} {'Speed':<10} {'Text Len':<10}")
    print("-" * 60)
    
    for result in results:
        speed_str = f"{result['speed_ratio']:.1f}x" if result['speed_ratio'] != 'unknown' else 'unknown'
        print(f"{result['model']:<10} {result['type']:<10} {result['duration']:<8.2f} {speed_str:<10} {result['text_length']:<10}")
    
    # Find fastest
    fastest = min(results, key=lambda x: x['duration'])
    print(f"\n🏆 Fastest: {fastest['model']} ({fastest['type']}) - {fastest['duration']:.2f}s")
    
    # Performance recommendations
    print("\n💡 RECOMMENDATIONS:")
    fast_models = [r for r in results if r['duration'] < 10]
    if fast_models:
        best_model = min(fast_models, key=lambda x: x['duration'])
        print(f"• Use '{best_model['model']}' model for best speed")
    else:
        print("• Consider using 'tiny' or 'base' model for better speed")
    
    if any(r['type'] == 'fast' for r in results):
        print("• Use whisper_fast.py for optimized performance")
    
    print("• Ensure you're using GPU acceleration (MPS/CUDA) if available")


def main():
    """Main test function."""
    print("Whisper Performance Test")
    print("="*60)
    
    # Check system
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if hasattr(torch.backends, 'mps'):
        print(f"MPS available: {torch.backends.mps.is_available()}")
    
    # Get test audio file
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = test_audio_file()
    
    if not audio_file or not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Run tests
    models_to_test = ["tiny", "base"]  # Start with fast models
    if len(sys.argv) > 2:
        models_to_test = sys.argv[2].split(",")
    
    print(f"\nTesting models: {', '.join(models_to_test)}")
    
    results = run_performance_test(audio_file, models_to_test)
    print_summary(results)
    
    print("\n✅ Performance test completed!")
    print(f"💡 Run with different models: python {sys.argv[0]} {audio_file} tiny,base,small")


if __name__ == "__main__":
    main()