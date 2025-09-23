#!/usr/bin/env python3
"""
Test all Whisper models to verify they work correctly.
This script tests each model with a sample audio file and measures performance.
"""

import os
import sys
import time
import traceback
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whisper_transcriber import WhisperTranscriber

def test_model(model_name, audio_file, output_dir):
    """Test a specific Whisper model."""
    print(f"\n{'='*60}")
    print(f"Testing {model_name} model...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Initialize transcriber
        transcriber = WhisperTranscriber(
            model_size=model_name,
            device='cpu'  # Force CPU to avoid MPS issues
        )
        
        init_time = time.time() - start_time
        print(f"✓ Model initialized in {init_time:.2f} seconds")
        
        # Test transcription
        transcribe_start = time.time()
        result = transcriber.transcribe_audio(
            audio_path=audio_file, 
            language='auto',
            task='transcribe',
            verbose=False  # Reduce output for cleaner test results
        )
        transcribe_time = time.time() - transcribe_start
        
        # Save results to output directory
        if result:
            transcriber.save_results(
                result=result,
                output_dir=output_dir,
                formats=['txt']  # Just save as text file
            )
        
        total_time = time.time() - start_time
        
        if result and 'text' in result:
            print("✓ Transcription completed successfully!")
            print(f"  - Initialization time: {init_time:.2f}s")
            print(f"  - Transcription time: {transcribe_time:.2f}s")
            print(f"  - Total time: {total_time:.2f}s")
            print(f"  - Detected language: {result.get('language', 'N/A')}")
            
            # Show a preview of the transcription
            text = result['text']
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"  - Preview: {preview}")
            
            return {
                'success': True,
                'init_time': init_time,
                'transcribe_time': transcribe_time,
                'total_time': total_time,
                'text_length': len(text),
                'detected_language': result.get('language', 'unknown'),
                'text_preview': preview
            }
        else:
            print("✗ Transcription failed: No text result returned")
            return {
                'success': False,
                'error': 'No text result returned',
                'total_time': total_time
            }
            
    except Exception as e:
        error_time = time.time() - start_time
        print(f"✗ Exception occurred: {str(e)}")
        print(f"  - Time before error: {error_time:.2f}s")
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'total_time': error_time
        }

def main():
    """Run tests for all Whisper models."""
    print("Whisper Models Test Suite")
    print("=" * 60)
    
    # Setup paths
    script_dir = Path(__file__).parent
    audio_file = script_dir / "recordings" / "recording_20250922_221823.wav"
    output_dir = script_dir / "model_test_output"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Check if audio file exists
    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    print(f"📁 Audio file: {audio_file}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Audio file size: {audio_file.stat().st_size / 1024:.1f} KB")
    
    # Models to test (ordered by size)
    models = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
    
    # Store results
    results = {}
    
    # Test each model
    for model in models:
        results[model] = test_model(model, str(audio_file), str(output_dir))
        
        # Small delay between tests to prevent memory issues
        time.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_models = []
    failed_models = []
    
    for model, result in results.items():
        if result['success']:
            successful_models.append(model)
            print(f"✓ {model:12s} - {result['total_time']:6.2f}s total, {result.get('text_length', 0):4d} chars")
        else:
            failed_models.append(model)
            print(f"✗ {model:12s} - FAILED ({result.get('error', 'Unknown error')[:50]}...)")
    
    print(f"\n📊 Results:")
    print(f"  - Successful: {len(successful_models)}/{len(models)} models")
    print(f"  - Failed: {len(failed_models)}/{len(models)} models")
    
    if successful_models:
        print(f"  - Working models: {', '.join(successful_models)}")
        
        # Find fastest and slowest
        successful_results = {k: v for k, v in results.items() if v['success']}
        if successful_results:
            fastest = min(successful_results.items(), key=lambda x: x[1]['total_time'])
            slowest = max(successful_results.items(), key=lambda x: x[1]['total_time'])
            print(f"  - Fastest: {fastest[0]} ({fastest[1]['total_time']:.2f}s)")
            print(f"  - Slowest: {slowest[0]} ({slowest[1]['total_time']:.2f}s)")
    
    if failed_models:
        print(f"  - Failed models: {', '.join(failed_models)}")
    
    print(f"\n📁 Output files saved to: {output_dir}")
    
    # List output files
    output_files = list(output_dir.glob("*.txt"))
    if output_files:
        print(f"📄 Generated files:")
        for file in sorted(output_files):
            print(f"  - {file.name}")

if __name__ == "__main__":
    main()