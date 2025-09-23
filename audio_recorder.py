#!/usr/bin/env python3
"""
Audio Recorder for Whisper Transcription App
Provides audio recording functionality with real-time level monitoring
"""

import pyaudio
import wave
import threading
import time
import numpy as np
from typing import Optional, Callable
import os
from datetime import datetime


class AudioRecorder:
    """Audio recorder with real-time level monitoring"""
    
    def __init__(self, sample_rate: int = 44100, channels: int = 1, chunk_size: int = 1024):
        """
        Initialize audio recorder
        
        Args:
            sample_rate: Audio sample rate (Hz)
            channels: Number of audio channels (1=mono, 2=stereo)
            chunk_size: Audio buffer size
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        
        # Recording state
        self.is_recording = False
        self.audio_data = []
        self.audio_stream = None
        self.pyaudio_instance = None
        self.recording_thread = None
        
        # Callbacks
        self.level_callback: Optional[Callable[[float], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        
    def set_level_callback(self, callback: Callable[[float], None]):
        """Set callback for audio level updates (0.0 to 1.0)"""
        self.level_callback = callback
        
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates"""
        self.status_callback = callback
        
    def _update_status(self, status: str):
        """Update status via callback"""
        if self.status_callback:
            self.status_callback(status)
            
    def _update_level(self, level: float):
        """Update audio level via callback"""
        if self.level_callback:
            self.level_callback(min(1.0, max(0.0, level)))
    
    def get_audio_devices(self):
        """Get list of available audio input devices"""
        devices = []
        try:
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
            p.terminate()
        except Exception as e:
            print(f"Error getting audio devices: {e}")
        return devices
    
    def start_recording(self, device_index: Optional[int] = None):
        """Start audio recording"""
        if self.is_recording:
            return False
            
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Open audio stream
            self.audio_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_recording = True
            self.audio_data = []
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            self._update_status("Recording...")
            return True
            
        except Exception as e:
            self._update_status(f"Recording error: {str(e)}")
            self.cleanup()
            return False
    
    def _record_audio(self):
        """Recording thread function"""
        try:
            while self.is_recording and self.audio_stream:
                # Read audio data
                data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
                
                # Calculate audio level for visualization
                audio_np = np.frombuffer(data, dtype=np.int16)
                if len(audio_np) > 0:
                    level = np.abs(audio_np).mean() / 32768.0  # Normalize to 0-1
                    self._update_level(level)
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except Exception as e:
            self._update_status(f"Recording error: {str(e)}")
            self.is_recording = False
    
    def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
        
        self.cleanup()
        self._update_status("Recording stopped")
        self._update_level(0.0)
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception:
                pass
            self.audio_stream = None
            
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception:
                pass
            self.pyaudio_instance = None
    
    def save_recording(self, filename: str) -> bool:
        """
        Save recorded audio to file
        
        Args:
            filename: Output filename (should end with .wav)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.audio_data:
            self._update_status("No audio data to save")
            return False
        
        try:
            # Ensure filename ends with .wav
            if not filename.lower().endswith('.wav'):
                filename += '.wav'
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save audio to WAV file
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.pyaudio_instance.get_sample_size(self.format) if self.pyaudio_instance else 2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(b''.join(self.audio_data))
            
            self._update_status(f"Recording saved: {filename}")
            return True
            
        except Exception as e:
            self._update_status(f"Save error: {str(e)}")
            return False
    
    def get_recording_duration(self) -> float:
        """Get current recording duration in seconds"""
        if not self.audio_data:
            return 0.0
        
        frames = len(self.audio_data) * self.chunk_size
        return frames / self.sample_rate
    
    def generate_filename(self, output_dir: str = "recordings") -> str:
        """Generate a unique filename for recording"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        return os.path.join(output_dir, filename)


def test_audio_recorder():
    """Test the audio recorder functionality"""
    import time
    
    print("Testing Audio Recorder...")
    
    recorder = AudioRecorder()
    
    # Set up callbacks
    def level_callback(level):
        bar_length = int(level * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"\rLevel: [{bar}] {level:.2f}", end="", flush=True)
    
    def status_callback(status):
        print(f"\nStatus: {status}")
    
    recorder.set_level_callback(level_callback)
    recorder.set_status_callback(status_callback)
    
    # List audio devices
    devices = recorder.get_audio_devices()
    print("\nAvailable audio devices:")
    for device in devices:
        print(f"  {device['index']}: {device['name']}")
    
    # Start recording
    print("\nStarting 5-second recording test...")
    if recorder.start_recording():
        time.sleep(5)
        recorder.stop_recording()
        
        # Save recording
        filename = recorder.generate_filename()
        if recorder.save_recording(filename):
            print(f"\nRecording saved successfully: {filename}")
            print(f"Duration: {recorder.get_recording_duration():.2f} seconds")
        else:
            print("\nFailed to save recording")
    else:
        print("Failed to start recording")


if __name__ == "__main__":
    test_audio_recorder()