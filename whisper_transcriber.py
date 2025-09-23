#!/usr/bin/env python3
"""
Whisper Audio Transcription Tool
================================

A Python application that transcribes audio files to text using OpenAI's Whisper model.
Supports multiple languages including Tagalog and English with GPU acceleration for offline use.

Features:
- Uses Whisper large-v3 model for high accuracy
- GPU acceleration when available
- Language detection and specification
- Supports multiple audio formats
- Offline operation
- Detailed transcription results with timestamps
"""

import argparse
import json
import os
import ssl
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

import torch
import whisper
from whisper.utils import get_writer


class WhisperTranscriber:
    """Audio transcription class using OpenAI Whisper model."""
    
    def __init__(self, model_size: str = "large-v3", device: Optional[str] = None):
        """
        Initialize the Whisper transcriber.
        
        Args:
            model_size: Whisper model size to use (default: large-v3)
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
        """
        self.model_size = model_size
        self.device = self._get_device(device)
        self.model = None
        
        print("Initializing Whisper transcriber...")
        print(f"Model size: {self.model_size}")
        print(f"Device: {self.device}")
        
        self._load_model()
    
    def _get_device(self, device: Optional[str] = None) -> str:
        """Determine the best device to use for inference."""
        if device:
            return device
        
        if torch.cuda.is_available():
            print("CUDA GPU detected and available")
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("Apple Silicon GPU (MPS) detected and available")
            return "mps"
        else:
            print("GPU not available, using CPU")
            return "cpu"
    
    def _load_model(self):
        """Load the Whisper model with SSL certificate handling and download retry."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Loading Whisper {self.model_size} model... (attempt {attempt + 1}/{max_retries})")
                start_time = time.time()
                
                # Try to load model normally first
                try:
                    self.model = whisper.load_model(self.model_size, device=self.device)
                    break  # Success, exit retry loop
                    
                except Exception as ssl_error:
                    error_str = str(ssl_error).lower()
                    
                    if "ssl" in error_str or "certificate" in error_str:
                        print("SSL certificate error detected. Attempting to fix...")
                        
                        # Create unverified SSL context
                        old_context = ssl._create_default_https_context
                        ssl._create_default_https_context = ssl._create_unverified_context
                        
                        try:
                            # Try loading model with unverified SSL context
                            self.model = whisper.load_model(self.model_size, device=self.device)
                            print("Model loaded successfully with SSL workaround")
                            break  # Success, exit retry loop
                        finally:
                            # Restore original SSL context
                            ssl._create_default_https_context = old_context
                            
                    elif "sha256" in error_str or "checksum" in error_str:
                        print(f"Checksum error detected. Clearing cache and retrying... (attempt {attempt + 1})")
                        # Clear cache for this model and retry
                        import os
                        import pathlib
                        cache_dir = pathlib.Path.home() / ".cache" / "whisper"
                        model_file = cache_dir / f"{self.model_size}.pt"
                        if model_file.exists():
                            os.remove(model_file)
                            print(f"Removed corrupted model file: {model_file}")
                        
                        if attempt < max_retries - 1:  # Don't sleep on last attempt
                            import time as time_module
                            time_module.sleep(2)  # Wait before retry
                        continue  # Retry the download
                    else:
                        raise ssl_error
                        
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"Error loading model after {max_retries} attempts: {e}")
                    sys.exit(1)
                else:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print("Retrying...")
                    continue
            
        load_time = time.time() - start_time
        print(f"Model loaded successfully in {load_time:.2f} seconds")
    
    def transcribe_audio(
        self, 
        audio_path: str, 
        language: Optional[str] = None,
        task: str = "transcribe",
        verbose: bool = True,
        no_speech_threshold: float = 0.6,
        logprob_threshold: float = -1.0,
        compression_ratio_threshold: float = 2.4
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'tl') or None for auto-detection
            task: 'transcribe' or 'translate' (translate to English)
            verbose: Whether to show progress
            
        Returns:
            Dictionary containing transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"\nTranscribing: {audio_path}")
        if language:
            print(f"Language: {language}")
        else:
            print("Language: Auto-detect")
        print(f"Task: {task}")
        
        start_time = time.time()
        
        try:
            # Transcribe with Whisper - optimized settings for performance
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                verbose=verbose,
                word_timestamps=False,  # Disable word timestamps for speed
                no_speech_threshold=no_speech_threshold,
                logprob_threshold=logprob_threshold,
                compression_ratio_threshold=compression_ratio_threshold,
                condition_on_previous_text=True,  # Better context
                temperature=0.0  # Deterministic output for speed
            )
            
            transcribe_time = time.time() - start_time
            
            # Add metadata
            result['metadata'] = {
                'file_path': audio_path,
                'model_size': self.model_size,
                'device': self.device,
                'transcription_time': round(transcribe_time, 2),
                'specified_language': language,
                'task': task
            }
            
            return result
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            raise
    
    def save_results(
        self, 
        result: Dict[str, Any], 
        output_dir: str = "output",
        formats: list = None
    ):
        """
        Save transcription results in multiple formats.
        
        Args:
            result: Transcription result from whisper
            output_dir: Directory to save output files
            formats: List of formats to save ('txt', 'json', 'srt', 'vtt')
        """
        if formats is None:
            formats = ['txt', 'json', 'srt']
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Base filename from input audio
        audio_path = result['metadata']['file_path']
        base_name = Path(audio_path).stem
        
        print(f"\nSaving results to {output_dir}/...")
        
        # Save in requested formats
        for fmt in formats:
            if fmt == 'json':
                # Save complete result as JSON
                json_path = os.path.join(output_dir, f"{base_name}_result.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"✓ JSON: {json_path}")
            
            elif fmt in ['txt', 'srt', 'vtt', 'tsv']:
                # Use Whisper's built-in writers
                writer = get_writer(fmt, output_dir)
                writer(result, base_name)
                print(f"✓ {fmt.upper()}: {output_dir}/{base_name}.{fmt}")


def print_language_info():
    """Print information about supported languages."""
    print("\nSupported Languages:")
    print("- English (en)")
    print("- Tagalog/Filipino (tl)")
    print("- And 97+ other languages supported by Whisper")
    print("\nNote: Use language codes (e.g., 'en', 'tl') or leave blank for auto-detection")


def print_system_info():
    """Print system and GPU information."""
    print("System Information:")
    print(f"- Python version: {sys.version}")
    print(f"- PyTorch version: {torch.__version__}")
    print(f"- CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"- CUDA version: {torch.version.cuda}")
        print(f"- GPU device: {torch.cuda.get_device_name()}")
        print(f"- GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print("- Apple Silicon GPU (MPS) available")


def main():
    """Main function to handle command line interface."""
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription with auto-language detection
  python whisper_transcriber.py audio.mp3
  
  # Transcribe in English
  python whisper_transcriber.py audio.wav --language en
  
  # Transcribe in Tagalog
  python whisper_transcriber.py audio.m4a --language tl
  
  # Translate to English
  python whisper_transcriber.py audio.mp3 --task translate
  
  # Use different model size
  python whisper_transcriber.py audio.wav --model medium
  
  # Force CPU usage
  python whisper_transcriber.py audio.mp3 --device cpu
  
  # Save multiple output formats
  python whisper_transcriber.py audio.wav --output-formats txt json srt vtt
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
        help="Language code (e.g., 'en' for English, 'tl' for Tagalog) or leave blank for auto-detection"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="large-v3",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper model size (default: large-v3)"
    )
    
    parser.add_argument(
        "--device", "-d",
        type=str,
        choices=["cuda", "cpu", "mps"],
        help="Device to use for inference (auto-detected if not specified)"
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
        default=['txt', 'json', 'srt'],
        choices=['txt', 'json', 'srt', 'vtt', 'tsv'],
        help="Output formats (default: txt json srt)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show system and language information"
    )
    
    args = parser.parse_args()
    
    # Show info if requested
    if args.info:
        print_system_info()
        print_language_info()
        return
    
    # Check if audio file is provided
    if not args.audio_file:
        parser.print_help()
        print("\nError: Please provide an audio file to transcribe")
        print("Use --info to see system information and supported languages")
        return
    
    try:
        # Initialize transcriber
        transcriber = WhisperTranscriber(
            model_size=args.model,
            device=args.device
        )
        
        # Transcribe audio
        result = transcriber.transcribe_audio(
            audio_path=args.audio_file,
            language=args.language,
            task=args.task,
            verbose=args.verbose
        )
        
        # Display results
        print(f"\n{'='*50}")
        print("TRANSCRIPTION RESULTS")
        print(f"{'='*50}")
        
        print(f"File: {args.audio_file}")
        print(f"Detected Language: {result['language']}")
        print(f"Duration: {result['metadata']['transcription_time']} seconds")
        
        print("\nTranscription:")
        print("-" * 30)
        print(result['text'])
        
        # Save results
        transcriber.save_results(
            result=result,
            output_dir=args.output_dir,
            formats=args.output_formats
        )
        
        print("\n✓ Transcription completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nTranscription interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()