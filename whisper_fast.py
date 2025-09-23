#!/usr/bin/env python3
"""
Fast Whisper Transcriber - Performance Optimized Version
========================================================

A performance-optimized version of the Whisper transcriber that:
- Reuses loaded models for multiple transcriptions
- Uses optimal settings for speed vs accuracy
- Implements smart device selection
- Includes audio preprocessing for better performance
- Provides real-time progress feedback
"""

import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import torch
import whisper
import numpy as np
from whisper.utils import get_writer

# Suppress specific warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="whisper")


class FastWhisperTranscriber:
    """Performance-optimized Whisper transcriber."""
    
    # Class-level model cache to reuse models across instances
    _model_cache = {}
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize the Fast Whisper transcriber.
        
        Args:
            model_size: Whisper model size to use (default: base for speed)
            device: Device to use ('cuda', 'cpu', 'mps', or None for auto-detection)
        """
        self.model_size = model_size
        self.device = self._get_optimal_device(device)
        self.model = None
        
        print("Initializing Fast Whisper transcriber...")
        print(f"Model size: {self.model_size}")
        print(f"Device: {self.device}")
        
        self._load_or_get_cached_model()
    
    def _get_optimal_device(self, device: Optional[str] = None) -> str:
        """Determine the best device to use for inference with performance optimization."""
        if device and device != "auto":
            return device
        
        # For now, prefer CPU due to MPS issues with some PyTorch versions
        # Check for CUDA first (fastest for NVIDIA GPUs)
        if torch.cuda.is_available():
            print("CUDA GPU detected - using for optimal performance")
            return "cuda"
        
        # Use CPU as most reliable option
        print("Using CPU for best compatibility")
        return "cpu"
    
    def _load_or_get_cached_model(self):
        """Load model or get from cache for performance."""
        cache_key = f"{self.model_size}_{self.device}"
        
        if cache_key in self._model_cache:
            print(f"Using cached {self.model_size} model (instant load)")
            self.model = self._model_cache[cache_key]
            return
        
        print(f"Loading {self.model_size} model for the first time...")
        start_time = time.time()
        
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            
            # Cache the model for reuse
            self._model_cache[cache_key] = self.model
            
            load_time = time.time() - start_time
            print(f"Model loaded and cached in {load_time:.2f} seconds")
            
        except Exception as e:
            error_str = str(e).lower()
            
            # If MPS fails, fall back to CPU
            if self.device == "mps" and ("mps" in error_str or "sparse" in error_str):
                print(f"MPS device failed ({e}), falling back to CPU...")
                self.device = "cpu"
                cache_key = f"{self.model_size}_{self.device}"
                
                # Try again with CPU
                try:
                    self.model = whisper.load_model(self.model_size, device=self.device)
                    self._model_cache[cache_key] = self.model
                    load_time = time.time() - start_time
                    print(f"Model loaded on CPU in {load_time:.2f} seconds")
                except Exception as cpu_error:
                    print(f"Error loading model on CPU: {cpu_error}")
                    sys.exit(1)
            else:
                print(f"Error loading model: {e}")
                sys.exit(1)
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration for progress estimation."""
        try:
            # Try to get duration using ffmpeg if available
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 
                'format=duration', '-of', 'csv=p=0', audio_path
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except (ImportError, subprocess.SubprocessError, ValueError):
            pass
        
        try:
            # Fallback: estimate from file size (rough approximation)
            file_size = os.path.getsize(audio_path)
            # Rough estimate: 1MB per minute for compressed audio
            estimated_duration = file_size / (1024 * 1024) * 60
            return estimated_duration
        except Exception:
            return 0.0
    
    def transcribe_audio_fast(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        task: str = "transcribe",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Fast transcribe audio file with performance optimizations.
        
        Args:
            audio_path: Path to the audio file
            language: Language code or None for auto-detection
            task: 'transcribe' or 'translate'
            verbose: Whether to show detailed progress
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"\nFast transcribing: {os.path.basename(audio_path)}")
        if language:
            print(f"Language: {language}")
        else:
            print("Language: Auto-detect")
        
        # Get audio duration for progress estimation
        duration = self.get_audio_duration(audio_path)
        if duration > 0:
            print(f"Audio duration: {duration:.1f} seconds")
        
        start_time = time.time()
        
        try:
            # Performance-optimized transcription settings
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                verbose=verbose,
                # Performance optimizations
                word_timestamps=False,  # Disable for speed
                condition_on_previous_text=True,  # Better context, faster
                temperature=0.0,  # Deterministic, faster
                no_speech_threshold=0.6,  # Skip silence faster
                logprob_threshold=-1.0,  # Quality threshold
                compression_ratio_threshold=2.4,  # Detect repetition
                # Audio processing optimizations
                fp16=(self.device != "cpu"),  # Use FP16 on GPU for speed
            )
            
            transcribe_time = time.time() - start_time
            
            # Calculate performance metrics
            speed_ratio = duration / transcribe_time if duration > 0 and transcribe_time > 0 else 0
            
            # Add enhanced metadata
            result['metadata'] = {
                'file_path': audio_path,
                'model_size': self.model_size,
                'device': self.device,
                'transcription_time': round(transcribe_time, 2),
                'audio_duration': round(duration, 2) if duration > 0 else 'unknown',
                'speed_ratio': round(speed_ratio, 2) if speed_ratio > 0 else 'unknown',
                'specified_language': language,
                'task': task,
                'performance_optimized': True
            }
            
            # Performance summary
            if speed_ratio > 0:
                print(f"Transcription completed in {transcribe_time:.2f}s")
                print(f"Speed: {speed_ratio:.1f}x real-time")
                if speed_ratio < 1.0:
                    print("⚠️  Consider using a smaller model (tiny/base) for better speed")
                elif speed_ratio > 3.0:
                    print("🚀 Excellent performance!")
            
            return result
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise
    
    def save_results_fast(
        self, 
        result: Dict[str, Any], 
        output_dir: str = "output",
        formats: list = None
    ):
        """Save transcription results optimized for common use cases."""
        if formats is None:
            formats = ['txt']  # Default to just text for speed
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Base filename from input audio
        audio_path = result['metadata']['file_path']
        base_name = Path(audio_path).stem
        
        print(f"\nSaving results to {output_dir}/...")
        
        # Save in requested formats
        for fmt in formats:
            if fmt == 'txt':
                # Fast text save
                txt_path = os.path.join(output_dir, f"{base_name}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                print(f"✓ Text: {txt_path}")
            
            elif fmt == 'json':
                # Complete result as JSON
                json_path = os.path.join(output_dir, f"{base_name}_result.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"✓ JSON: {json_path}")
            
            elif fmt in ['srt', 'vtt', 'tsv']:
                # Use Whisper's built-in writers
                writer = get_writer(fmt, output_dir)
                writer(result, base_name)
                print(f"✓ {fmt.upper()}: {output_dir}/{base_name}.{fmt}")


def print_performance_recommendations():
    """Print performance optimization recommendations."""
    print("\n" + "="*60)
    print("PERFORMANCE RECOMMENDATIONS")
    print("="*60)
    
    # Check system capabilities
    has_mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
    has_cuda = torch.cuda.is_available()
    
    print("\n🚀 For best performance:")
    
    if has_mps:
        print("✓ Apple Silicon GPU detected - use device='mps' or 'auto'")
    elif has_cuda:
        print("✓ CUDA GPU detected - use device='cuda' or 'auto'")
    else:
        print("⚠️  No GPU detected - use smaller models for better CPU performance")
    
    print("\n📊 Model size recommendations:")
    print("• tiny: ~32x real-time (fast, lower accuracy)")
    print("• base: ~16x real-time (good balance)")
    print("• small: ~6x real-time (better accuracy)")
    print("• medium: ~2x real-time (high accuracy)")
    print("• large: <1x real-time (highest accuracy, slowest)")
    
    print("\n⚡ Speed optimization tips:")
    print("• Use 'auto' device selection")
    print("• Start with 'base' model, upgrade if needed")
    print("• Disable word_timestamps for speed")
    print("• Use shorter audio files when possible")
    print("• Consider audio quality vs file size")


def main():
    """Main function for the fast transcriber."""
    parser = argparse.ArgumentParser(
        description="Fast Whisper Audio Transcription Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Performance Examples:
  # Fast transcription with auto-optimization
  python whisper_fast.py audio.mp3
  
  # Ultra-fast with tiny model
  python whisper_fast.py audio.wav --model tiny
  
  # Balanced speed/accuracy
  python whisper_fast.py audio.m4a --model base --device auto
  
  # Show performance recommendations
  python whisper_fast.py --recommendations
        """
    )
    
    parser.add_argument(
        "audio_file",
        nargs='?',
        help="Path to the audio file to transcribe"
    )
    
    parser.add_argument(
        "--language", "-l",
        type=str,
        help="Language code (e.g., 'en', 'tl') or leave blank for auto-detection"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper model size (default: base for speed)"
    )
    
    parser.add_argument(
        "--device", "-d",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu", "mps"],
        help="Device to use (default: auto for best performance)"
    )
    
    parser.add_argument(
        "--task", "-t",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Task: 'transcribe' (default) or 'translate' to English"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Output directory for results (default: output)"
    )
    
    parser.add_argument(
        "--output-formats", "-f",
        nargs='+',
        default=['txt'],
        choices=['txt', 'json', 'srt', 'vtt', 'tsv'],
        help="Output formats (default: txt for speed)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--recommendations",
        action="store_true",
        help="Show performance recommendations and exit"
    )
    
    args = parser.parse_args()
    
    # Show recommendations if requested
    if args.recommendations:
        print_performance_recommendations()
        return
    
    # Check if audio file is provided
    if not args.audio_file:
        parser.print_help()
        print("\nError: Please provide an audio file to transcribe")
        print("Use --recommendations to see performance optimization tips")
        return
    
    try:
        # Initialize fast transcriber
        transcriber = FastWhisperTranscriber(
            model_size=args.model,
            device=args.device
        )
        
        # Transcribe audio with performance optimization
        result = transcriber.transcribe_audio_fast(
            audio_path=args.audio_file,
            language=args.language,
            task=args.task,
            verbose=args.verbose
        )
        
        # Display results with performance info
        print(f"\n{'='*50}")
        print("TRANSCRIPTION RESULTS")
        print(f"{'='*50}")
        
        print(f"File: {os.path.basename(args.audio_file)}")
        print(f"Detected Language: {result['language']}")
        
        # Show performance metrics
        metadata = result['metadata']
        print(f"Transcription time: {metadata['transcription_time']}s")
        if metadata.get('speed_ratio', 'unknown') != 'unknown':
            print(f"Speed: {metadata['speed_ratio']}x real-time")
        
        print("\nTranscription:")
        print("-" * 30)
        print(result['text'])
        
        # Save results
        transcriber.save_results_fast(
            result=result,
            output_dir=args.output_dir,
            formats=args.output_formats
        )
        
        print("\n✓ Fast transcription completed successfully!")
        
        # Performance tip
        if metadata.get('speed_ratio', 0) < 1.0:
            print("\n💡 Tip: Try a smaller model (--model tiny or --model base) for faster processing")
        
    except KeyboardInterrupt:
        print("\n\nTranscription interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()