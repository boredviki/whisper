#!/usr/bin/env python3
"""
Whisper Mini - Minimalist Transcription GUI
==========================================

A compact, minimalist version of the Whisper transcription tool with only essential features:
- Audio file selection
- Audio recording
- Output folder selection
- Text format output only
- Language selection
- Task selection (transcribe/translate)
- Model and device selection
- Progress bar and status indicator

Usage:
    python whisper_mini.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import subprocess
import time
from pathlib import Path

# Import audio recorder
try:
    from audio_recorder import AudioRecorder
    RECORDING_AVAILABLE = True
except ImportError:
    RECORDING_AVAILABLE = False

# Constants
def get_whisper_script_path():
    """Get the correct path to whisper_transcriber.py for both dev and packaged environments."""
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        script_path = os.path.join(bundle_dir, "whisper_transcriber.py")
    else:
        # Check if fast transcriber exists and use it for better performance
        fast_script = "whisper_fast.py"
        standard_script = "whisper_transcriber.py"
        
        if os.path.exists(fast_script):
            return fast_script
        else:
            return standard_script
    return script_path

WHISPER_SCRIPT = get_whisper_script_path()


class WhisperMini:
    """Minimalist Whisper transcription GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Whisper Mini")
        self.root.geometry("480x400")
        self.root.resizable(False, False)
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.audio_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Desktop"))
        self.recordings_dir_var = tk.StringVar(value=str(Path.home() / "Desktop" / "Recordings"))
        self.language_var = tk.StringVar(value="auto")
        self.task_var = tk.StringVar(value="transcribe")
        self.model_var = tk.StringVar(value="base")
        self.device_var = tk.StringVar(value="auto")  # Use auto-detection for best performance
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Recording state
        self.is_recording = False
        self.recorder = None
        self.current_process = None
        self.current_recording_file = None
        
        # Create recordings directory if it doesn't exist
        try:
            recordings_dir = Path(self.recordings_dir_var.get())
            recordings_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass  # If we can't create it now, we'll try again when recording
        
        self.setup_ui()
    
    def setup_styles(self):
        """Setup custom styles for the interface."""
        style = ttk.Style()
        
        # Configure button styles
        style.configure("Primary.TButton", 
                       font=("SF Pro Display", 11),
                       padding=(10, 8))
        
        style.configure("Record.TButton",
                       font=("SF Pro Display", 11),
                       padding=(15, 10))
        
        style.configure("Browse.TButton",
                       font=("SF Pro Display", 9),
                       padding=(8, 6))
        
        # Configure label styles
        style.configure("Title.TLabel",
                       font=("SF Pro Display", 12, "bold"))
        
        style.configure("Status.TLabel",
                       font=("SF Pro Display", 10))
        
        # Configure entry styles
        style.configure("Path.TEntry",
                       font=("SF Pro Text", 10),
                       fieldbackground="white")
        
    def setup_ui(self):
        """Setup the compact user interface."""
        # Main container with minimal padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Audio file selection
        ttk.Label(main_frame, text="Audio File:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.audio_file_var, style="Path.TEntry").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(main_frame, text="Browse", command=self.browse_audio_file, style="Browse.TButton").grid(row=row, column=2, padx=(5, 0), pady=2)
        row += 1
        
        # Recording section (if available)
        if RECORDING_AVAILABLE:
            self.record_button = ttk.Button(main_frame, text="Record Audio", 
                                          command=self.toggle_recording, style="Record.TButton")
            self.record_button.grid(row=row, column=1, pady=5)
            row += 1
            
            # Recordings save folder
            ttk.Label(main_frame, text="Save To:").grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(main_frame, textvariable=self.recordings_dir_var, style="Path.TEntry").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
            ttk.Button(main_frame, text="Browse", command=self.browse_recordings_dir, style="Browse.TButton").grid(row=row, column=2, padx=(5, 0), pady=2)
            row += 1
        
        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.output_dir_var, style="Path.TEntry").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_dir, style="Browse.TButton").grid(row=row, column=2, padx=(5, 0), pady=2)
        row += 1
        
        # Settings in a compact 2x2 grid
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Language and Task (first row)
        ttk.Label(settings_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, width=12, state="readonly")
        language_combo['values'] = ['auto', 'en', 'tl', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        
        ttk.Label(settings_frame, text="Task:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        task_combo = ttk.Combobox(settings_frame, textvariable=self.task_var, width=12, state="readonly")
        task_combo['values'] = ['transcribe', 'translate']
        task_combo.grid(row=0, column=3, sticky=tk.W)
        
        # Model and Device (second row)
        ttk.Label(settings_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, width=12, state="readonly")
        model_combo['values'] = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
        model_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 15), pady=(5, 0))
        
        ttk.Label(settings_frame, text="Device:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        device_combo = ttk.Combobox(settings_frame, textvariable=self.device_var, width=12, state="readonly")
        device_combo['values'] = ['auto', 'cpu', 'cuda', 'mps']
        device_combo.grid(row=1, column=3, sticky=tk.W, pady=(5, 0))
        
        row += 1
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        
        row += 1
        
        # Start button
        self.transcribe_button = ttk.Button(main_frame, text="Start Transcription", 
                                          command=self.start_transcription, style="Primary.TButton")
        self.transcribe_button.grid(row=row, column=0, columnspan=3, pady=(0, 5))
        
        row += 1
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=row, column=0, columnspan=3, pady=(5, 0))
        
        ttk.Label(status_frame, text="Status:", style="Status.TLabel").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                     foreground="green", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def browse_audio_file(self):
        """Browse for an audio file."""
        filetypes = [
            ("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg *.aac *.wma"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        if filename:
            self.audio_file_var.set(filename)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)
    
    def browse_recordings_dir(self):
        """Browse for recordings save directory."""
        directory = filedialog.askdirectory(
            title="Select Recordings Save Directory",
            initialdir=self.recordings_dir_var.get()
        )
        if directory:
            self.recordings_dir_var.set(directory)
    
    def toggle_recording(self):
        """Toggle audio recording."""
        if not RECORDING_AVAILABLE:
            messagebox.showerror("Error", "Audio recording not available. Install pyaudio.")
            return
            
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start audio recording."""
        try:
            # Create recordings directory if it doesn't exist
            recordings_dir = Path(self.recordings_dir_var.get())
            recordings_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.current_recording_file = recordings_dir / f"recording_{timestamp}.wav"
            
            # Initialize and start recorder
            self.recorder = AudioRecorder()
            success = self.recorder.start_recording()
            
            if success:
                self.is_recording = True
                self.record_button.config(text="⏹️ Stop Recording")
                self.status_var.set("Recording...")
            else:
                messagebox.showerror("Recording Error", "Failed to start recording")
            
        except Exception as e:
            messagebox.showerror("Recording Error", f"Failed to start recording: {str(e)}")
    
    def stop_recording(self):
        """Stop audio recording."""
        if self.recorder and self.is_recording:
            try:
                # Stop recording
                self.recorder.stop_recording()
                
                # Save the recording to file
                if self.current_recording_file:
                    success = self.recorder.save_recording(str(self.current_recording_file))
                    
                    if success and os.path.exists(self.current_recording_file):
                        self.audio_file_var.set(str(self.current_recording_file))
                        messagebox.showinfo("Recording Complete", 
                                          f"Recording saved: {self.current_recording_file.name}")
                    else:
                        messagebox.showerror("Save Error", "Failed to save recording")
                
                self.is_recording = False
                self.record_button.config(text="🎙️ Record Audio")
                self.status_var.set("Ready")
                self.current_recording_file = None
                
            except Exception as e:
                messagebox.showerror("Recording Error", f"Failed to stop recording: {str(e)}")
                self.is_recording = False
                self.record_button.config(text="🎙️ Record Audio")
                self.status_var.set("Ready")
    
    def validate_inputs(self):
        """Validate user inputs."""
        if not self.audio_file_var.get():
            messagebox.showerror("Error", "Please select an audio file or record audio.")
            return False
        
        if not os.path.exists(self.audio_file_var.get()):
            messagebox.showerror("Error", "Selected audio file does not exist.")
            return False
        
        if not os.path.exists(self.output_dir_var.get()):
            messagebox.showerror("Error", "Output directory does not exist.")
            return False
        
        return True
    
    def get_optimal_device(self):
        """Get the optimal device for transcription, resolving 'auto' selection."""
        device = self.device_var.get()
        
        if device != "auto":
            return device
        
        # Auto-detect best device with conservative approach
        import torch
        
        # Prefer CPU for stability, unless user specifically requests GPU
        # This avoids the MPS sparse tensor issues we encountered
        if torch.cuda.is_available():
            return "cuda"
        else:
            # Use CPU as the most reliable option
            return "cpu"
    
    def build_command(self):
        """Build the command line for whisper_transcriber.py."""
        python_exe = sys.executable
        cmd = [python_exe, WHISPER_SCRIPT]
        
        # Audio file
        cmd.append(self.audio_file_var.get())
        
        # Language
        if self.language_var.get() != "auto":
            cmd.extend(["--language", self.language_var.get()])
        
        # Model
        cmd.extend(["--model", self.model_var.get()])
        
        # Device - resolve 'auto' to specific device
        device = self.get_optimal_device()
        cmd.extend(["--device", device])
        
        # Task
        if self.task_var.get() != "transcribe":
            cmd.extend(["--task", self.task_var.get()])
        
        # Output directory
        cmd.extend(["--output-dir", self.output_dir_var.get()])
        
        # Output format (text only)
        cmd.extend(["--output-formats", "txt"])
        
        # Add verbose flag for debugging
        cmd.append("--verbose")
        
        return cmd
    
    def start_transcription(self):
        """Start the transcription process."""
        if not self.validate_inputs():
            return
        
        # Reset progress
        self.progress_var.set(0)
        
        # Show device information in status
        selected_device = self.device_var.get()
        actual_device = self.get_optimal_device()
        
        if selected_device == "auto":
            status_msg = f"Auto-selected {actual_device.upper()} device"
        else:
            status_msg = f"Using {actual_device.upper()} device"
        
        # Disable the transcribe button
        self.transcribe_button.config(state="disabled", text="🔄 Transcribing...")
        self.status_var.set(status_msg)
        
        # Start transcription in a separate thread
        thread = threading.Thread(target=self.run_transcription, daemon=True)
        thread.start()
    
    def update_progress(self, value, status=""):
        """Update progress bar and status safely from any thread."""
        def update():
            self.progress_var.set(value)
            if status:
                self.status_var.set(status)
        self.root.after(0, update)
    
    def run_transcription(self):
        """Run the transcription process in a separate thread."""
        try:
            cmd = self.build_command()
            
            # Debug: Print the command being executed
            print("DEBUG: Executing command:", ' '.join(cmd))
            
            # Update progress
            self.update_progress(10, "Starting transcription...")
            
            # Run the transcription
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            self.update_progress(25, "Model loading...")
            
            # Monitor process output for progress
            output_lines = []
            while True:
                line = self.current_process.stdout.readline()
                if line:
                    output_lines.append(line)
                    print(f"DEBUG: {line.strip()}")
                    
                    # Update progress based on output
                    if "Loading model" in line:
                        self.update_progress(40, "Loading Whisper model...")
                    elif "Processing" in line or "Transcribing" in line:
                        self.update_progress(60, "Processing audio...")
                    elif "Writing" in line or "Saving" in line:
                        self.update_progress(85, "Saving results...")
                
                # Check if process is done
                if self.current_process.poll() is not None:
                    break
            
            # Get any remaining output
            remaining_output, _ = self.current_process.communicate()
            if remaining_output:
                output_lines.append(remaining_output)
            
            stdout = ''.join(output_lines)
            
            # Debug: Print the output
            print("DEBUG: Process return code:", self.current_process.returncode)
            print("DEBUG: Process output:", stdout[:500] if stdout else "No output")
            
            if self.current_process.returncode == 0:
                # Success
                self.update_progress(100, "Transcription completed!")
                self.root.after(0, lambda: messagebox.showinfo("✅ Success", "Transcription completed successfully!"))
            else:
                # Error
                self.update_progress(0, "Transcription failed")
                self.root.after(0, lambda: messagebox.showerror("❌ Error", f"Transcription failed:\n{stdout}"))
        
        except subprocess.TimeoutExpired:
            self.current_process.kill()
            stdout, _ = self.current_process.communicate()
            print("DEBUG: Process timed out")
            self.update_progress(0, "Transcription timed out")
            self.root.after(0, lambda: messagebox.showerror("⏰ Timeout", "Transcription timed out after 5 minutes"))
            
        except Exception as e:
            print("DEBUG: Exception occurred:", str(e))
            self.update_progress(0, "Error occurred")
            self.root.after(0, lambda: messagebox.showerror("❌ Error", f"An error occurred:\n{str(e)}"))
        
        finally:
            # Re-enable the transcribe button and reset progress if failed
            def reset_ui():
                self.transcribe_button.config(state="normal", text="🚀 Start Transcription")
                if self.progress_var.get() != 100:
                    self.progress_var.set(0)
            
            self.root.after(0, reset_ui)
            self.current_process = None
    
    def cleanup(self):
        """Clean up resources before closing."""
        # Stop recording if active
        if self.is_recording and self.recorder:
            self.stop_recording()
        
        # Terminate any running process
        if self.current_process:
            self.current_process.terminate()
    
    def run(self):
        """Run the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing."""
        self.cleanup()
        self.root.destroy()


def main():
    """Main function."""
    app = WhisperMini()
    app.run()


if __name__ == "__main__":
    main()