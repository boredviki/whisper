#!/usr/bin/env python3
"""
Whisper Transcription GUI
=========================

A user-friendly graphical interface for the Whisper audio transcription tool.
Features file browsing, drag-and-drop support, output customization, and real-time progress tracking.

Usage:
    python whisper_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.dnd as dnd
import os
import sys
import threading
import queue
import subprocess
import json
from pathlib import Path
import time
import io
from contextlib import redirect_stdout

# Import audio recorder
try:
    from audio_recorder import AudioRecorder
    RECORDING_AVAILABLE = True
except ImportError:
    RECORDING_AVAILABLE = False
    print("Warning: Audio recording not available. Install pyaudio to enable recording features.")

# Import system info functions from whisper_transcriber
try:
    from whisper_transcriber import print_system_info, print_language_info
    SYSTEM_INFO_AVAILABLE = True
except ImportError:
    SYSTEM_INFO_AVAILABLE = False
    print("Warning: System info functions not available.")

# Constants
def get_whisper_script_path():
    """Get the correct path to whisper_transcriber.py for both dev and packaged environments."""
    if getattr(sys, 'frozen', False):
        # Running as packaged app
        bundle_dir = sys._MEIPASS
        script_path = os.path.join(bundle_dir, "whisper_transcriber.py")
    else:
        # Running as development script
        script_path = "whisper_transcriber.py"
    return script_path

WHISPER_SCRIPT = get_whisper_script_path()


class WhisperGUI:
    """Main GUI application for Whisper transcription."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Whisper Audio Transcription Tool")
        self.root.geometry("950x850")
        self.root.minsize(900, 750)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.audio_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd() / "output"))
        self.language_var = tk.StringVar(value="auto")
        self.model_var = tk.StringVar(value="base")  # Fast and good quality
        self.task_var = tk.StringVar(value="transcribe")
        self.device_var = tk.StringVar(value="cpu")  # Safe default, can be changed to mps if desired
        self.formats_var = tk.StringVar(value="txt")  # Only TXT by default
        self.verbose_var = tk.BooleanVar(value=False)
        
        # Recording variables
        self.is_recording = False
        self.recorder = None
        self.recording_file = None
        self.audio_level_var = tk.DoubleVar(value=0.0)
        self.recording_status_var = tk.StringVar(value="Ready to record")
        self.recording_duration_var = tk.StringVar(value="00:00")
        
        # Progress tracking
        self.is_transcribing = False
        self.progress_queue = queue.Queue()
        self.progress_monitoring = False
        self.progress_thread = None
        
        # Create GUI
        self.create_widgets()
        self.setup_drag_drop()
        
        # Start progress monitoring
        self.root.after(100, self.check_progress)
    
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="🎤 Whisper Audio Transcription", 
                               font=("Helvetica", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="📁 Audio File Selection", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Audio file selection
        ttk.Label(file_frame, text="Audio File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_entry = ttk.Entry(file_frame, textvariable=self.audio_file_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2)
        
        # Drag and drop label
        self.drop_label = ttk.Label(file_frame, text="💡 Tip: You can also drag and drop audio files here!", 
                                   foreground="gray")
        self.drop_label.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        # Audio recording section (if available)
        if RECORDING_AVAILABLE:
            self.create_recording_section(main_frame, row)
            row += 1
        
        # Output settings section
        output_frame = ttk.LabelFrame(main_frame, text="📤 Output Settings", padding="10")
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Output directory
        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2)
        
        # Output formats
        ttk.Label(output_frame, text="Output Formats:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        formats_frame = ttk.Frame(output_frame)
        formats_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.format_vars = {}
        formats = [("TXT (Text)", "txt"), ("JSON (Detailed)", "json"), ("SRT (Subtitles)", "srt"), 
                  ("VTT (Web Subtitles)", "vtt"), ("TSV (Table)", "tsv")]
        for i, (label, value) in enumerate(formats):
            var = tk.BooleanVar(value=value in ["txt"])
            self.format_vars[value] = var
            ttk.Checkbutton(formats_frame, text=label, variable=var).grid(row=0, column=i, padx=(0, 15), sticky=tk.W)
        
        # Transcription settings section
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Transcription Settings", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        row += 1
        
        # Language selection
        ttk.Label(settings_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, width=15)
        language_combo['values'] = ['auto', 'en', 'tl', 'es', 'fr', 'de', 'ja', 'zh', 'ko', 'pt', 'ru', 'it', 'nl']
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Model selection (ordered by speed: fastest to slowest)
        ttk.Label(settings_frame, text="Model:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, width=15)
        model_combo['values'] = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
        model_combo.grid(row=0, column=3, sticky=tk.W)
        
        # Task selection
        ttk.Label(settings_frame, text="Task:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        task_combo = ttk.Combobox(settings_frame, textvariable=self.task_var, width=15)
        task_combo['values'] = ['transcribe', 'translate']
        task_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Device selection - choose based on your system capabilities
        ttk.Label(settings_frame, text="Device:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        device_combo = ttk.Combobox(settings_frame, textvariable=self.device_var, width=15)
        device_combo['values'] = ['cpu', 'mps', 'cuda']
        device_combo.grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # Options
        options_frame = ttk.Frame(settings_frame)
        options_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(options_frame, text="Verbose output", variable=self.verbose_var).grid(row=0, column=0, sticky=tk.W)
        
        # Action buttons section
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))
        row += 1
        
        # Transcribe button
        self.transcribe_btn = ttk.Button(action_frame, text="🎤 Start Transcription", 
                                        command=self.start_transcription, style="Accent.TButton")
        self.transcribe_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(action_frame, text="⏹ Stop", 
                                  command=self.stop_transcription, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Open output button
        self.open_output_btn = ttk.Button(action_frame, text="📁 Open Output Folder", 
                                         command=self.open_output_folder)
        self.open_output_btn.grid(row=0, column=2, padx=(0, 10))
        
        # System info button
        ttk.Button(action_frame, text="ℹ️ System Info", command=self.show_system_info).grid(row=0, column=3)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progress & Output", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(2, weight=1)
        row += 1
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to transcribe")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Configure main grid weights
        main_frame.rowconfigure(row-1, weight=1)
        
        # Copyright footer
        copyright_frame = ttk.Frame(self.root)
        copyright_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 10))
        copyright_frame.columnconfigure(0, weight=1)
        
        copyright_label = ttk.Label(copyright_frame, 
                                   text="© 2025 ORIX IT Group, Enterprise System Development Division. All rights reserved.",
                                   font=("Arial", 9),
                                   foreground="gray")
        copyright_label.grid(row=0, column=0)
    
    def create_recording_section(self, parent, row):
        """Create the audio recording section."""
        recording_frame = ttk.LabelFrame(parent, text="🎙️ Audio Recording", padding="10")
        recording_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        recording_frame.columnconfigure(1, weight=1)
        
        # Recording controls
        controls_frame = ttk.Frame(recording_frame)
        controls_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Record button
        self.record_btn = ttk.Button(controls_frame, text="🔴 Start Recording", 
                                    command=self.toggle_recording, style="Accent.TButton")
        self.record_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Recording status
        self.recording_status_label = ttk.Label(controls_frame, textvariable=self.recording_status_var)
        self.recording_status_label.grid(row=0, column=1, padx=(10, 10))
        
        # Recording duration
        self.recording_duration_label = ttk.Label(controls_frame, textvariable=self.recording_duration_var, 
                                                 font=("Courier", 12))
        self.recording_duration_label.grid(row=0, column=2, padx=(10, 0))
        
        # Audio level visualization
        level_frame = ttk.Frame(recording_frame)
        level_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        level_frame.columnconfigure(1, weight=1)
        
        ttk.Label(level_frame, text="Level:").grid(row=0, column=0, padx=(0, 10))
        
        # Audio level meter
        self.level_progress = ttk.Progressbar(level_frame, variable=self.audio_level_var, 
                                            maximum=1.0, mode='determinate')
        self.level_progress.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Level percentage
        self.level_label = ttk.Label(level_frame, text="0%")
        self.level_label.grid(row=0, column=2)
        
        # Recording options
        options_frame = ttk.Frame(recording_frame)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(options_frame, text="Save to:").grid(row=0, column=0, padx=(0, 10))
        
        # Recording output options
        self.record_to_temp = tk.BooleanVar(value=True)
        self.record_to_output = tk.BooleanVar(value=False)
        
        ttk.Radiobutton(options_frame, text="Temporary folder (auto-use for transcription)", 
                       variable=self.record_to_temp, value=True).grid(row=0, column=1, padx=(0, 15))
        ttk.Radiobutton(options_frame, text="Output folder", 
                       variable=self.record_to_temp, value=False).grid(row=0, column=2)
        
        # Initialize recorder
        self.setup_recorder()
    
    def setup_drag_drop(self):
        """Set up drag and drop functionality."""
        # Note: tkinter.dnd is limited, so we'll use a simpler approach
        # Users can still use the Browse button or copy-paste file paths
        self.file_entry.bind("<Button-3>", self.show_file_context_menu)
    
    def show_file_context_menu(self, event):
        """Show context menu for file entry."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Paste", command=lambda: self.file_entry.event_generate('<<Paste>>'))
        context_menu.add_command(label="Clear", command=lambda: self.audio_file_var.set(""))
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def browse_file(self):
        """Open file dialog to select audio file."""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.m4a *.flac *.ogg *.wma *.aac"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("M4A files", "*.m4a"),
            ("FLAC files", "*.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filename:
            self.audio_file_var.set(filename)
    
    def browse_output_dir(self):
        """Open dialog to select output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        
        if directory:
            self.output_dir_var.set(directory)
    
    def setup_recorder(self):
        """Initialize the audio recorder."""
        if not RECORDING_AVAILABLE:
            return
            
        try:
            self.recorder = AudioRecorder()
            self.recorder.set_level_callback(self.update_audio_level)
            self.recorder.set_status_callback(self.update_recording_status)
            self.start_recording_timer()
        except Exception as e:
            print(f"Failed to initialize recorder: {e}")
            self.recorder = None
    
    def start_recording_timer(self):
        """Start the recording duration timer."""
        if self.is_recording and self.recorder:
            duration = self.recorder.get_recording_duration()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.recording_duration_var.set(f"{minutes:02d}:{seconds:02d}")
        
        # Schedule next update
        self.root.after(100, self.start_recording_timer)
    
    def update_audio_level(self, level):
        """Update the audio level visualization."""
        self.audio_level_var.set(level)
        percentage = int(level * 100)
        self.level_label.config(text=f"{percentage}%")
        
        # Change color based on level
        if level > 0.8:
            self.level_progress.config(style="Red.Horizontal.TProgressbar")
        elif level > 0.6:
            self.level_progress.config(style="Yellow.Horizontal.TProgressbar") 
        else:
            self.level_progress.config(style="Green.Horizontal.TProgressbar")
    
    def update_recording_status(self, status):
        """Update the recording status."""
        self.recording_status_var.set(status)
    
    def toggle_recording(self):
        """Start or stop audio recording."""
        if not RECORDING_AVAILABLE or not self.recorder:
            messagebox.showerror("Error", "Audio recording not available. Please install pyaudio.")
            return
        
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start audio recording."""
        if self.is_recording:
            return
        
        try:
            # Start recording
            if self.recorder.start_recording():
                self.is_recording = True
                self.record_btn.config(text="⏹ Stop Recording", style="")
                self.recording_status_var.set("Recording...")
                self.recording_duration_var.set("00:00")
                
                # Generate recording filename
                if self.record_to_temp.get():
                    # Save to temp directory for immediate transcription
                    temp_dir = Path.cwd() / "temp_recordings"
                    temp_dir.mkdir(exist_ok=True)
                    self.recording_file = self.recorder.generate_filename(str(temp_dir))
                else:
                    # Save to output directory
                    output_dir = self.output_dir_var.get()
                    self.recording_file = self.recorder.generate_filename(output_dir)
                
        except Exception as e:
            messagebox.showerror("Recording Error", f"Failed to start recording: {str(e)}")
            self.is_recording = False
    
    def stop_recording(self):
        """Stop audio recording."""
        if not self.is_recording:
            return
        
        try:
            self.recorder.stop_recording()
            self.is_recording = False
            self.record_btn.config(text="🔴 Start Recording", style="Accent.TButton")
            
            # Save recording
            if self.recording_file and self.recorder.save_recording(self.recording_file):
                duration = self.recorder.get_recording_duration()
                self.recording_status_var.set(f"Recording saved ({duration:.1f}s)")
                
                # Auto-select the recorded file for transcription
                if self.record_to_temp.get():
                    self.audio_file_var.set(self.recording_file)
                    messagebox.showinfo("Recording Complete", 
                                      f"Recording saved and ready for transcription!\n"
                                      f"Duration: {duration:.1f} seconds\n"
                                      f"File: {os.path.basename(self.recording_file)}")
                else:
                    messagebox.showinfo("Recording Complete", 
                                      f"Recording saved to output folder!\n"
                                      f"Duration: {duration:.1f} seconds\n"
                                      f"File: {self.recording_file}")
            else:
                self.recording_status_var.set("Failed to save recording")
                messagebox.showerror("Error", "Failed to save recording.")
                
        except Exception as e:
            messagebox.showerror("Recording Error", f"Failed to stop recording: {str(e)}")
            self.is_recording = False
    
    def get_selected_formats(self):
        """Get list of selected output formats."""
        return [fmt for fmt, var in self.format_vars.items() if var.get()]
    
    def validate_inputs(self):
        """Validate user inputs before starting transcription."""
        # Check audio file
        audio_file = self.audio_file_var.get()
        if not audio_file:
            messagebox.showerror("Error", "Please select an audio file.")
            return False
        
        if not os.path.exists(audio_file):
            messagebox.showerror("Error", f"Audio file not found: {audio_file}")
            return False
        
        # Check output formats
        if not self.get_selected_formats():
            messagebox.showerror("Error", "Please select at least one output format.")
            return False
        
        # Create output directory if it doesn't exist
        output_dir = self.output_dir_var.get()
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create output directory: {e}")
            return False
        
        return True
    
    def build_command(self):
        """Build the command line for whisper_transcriber.py."""
        # Use the current Python executable (virtual environment aware)
        python_exe = sys.executable
        cmd = [python_exe, WHISPER_SCRIPT]
        
        # Audio file
        cmd.append(self.audio_file_var.get())
        
        # Language
        if self.language_var.get() != "auto":
            cmd.extend(["--language", self.language_var.get()])
        
        # Model
        cmd.extend(["--model", self.model_var.get()])
        
        # Device
        if self.device_var.get() != "auto":
            cmd.extend(["--device", self.device_var.get()])
        
        # Task
        if self.task_var.get() != "transcribe":
            cmd.extend(["--task", self.task_var.get()])
        
        # Output directory
        cmd.extend(["--output-dir", self.output_dir_var.get()])
        
        # Output formats
        formats = self.get_selected_formats()
        cmd.extend(["--output-formats"] + formats)
        
        # Always use verbose in GUI to get better progress tracking
        cmd.append("--verbose")
        
        return cmd
    
    def start_transcription(self):
        """Start the transcription process in a separate thread."""
        if not self.validate_inputs():
            return
        
        # Update UI state
        self.is_transcribing = True
        self.transcribe_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_var.set(0)
        self.status_var.set("Starting transcription...")
        
        # Start transcription thread
        self.transcription_thread = threading.Thread(target=self.run_transcription, daemon=True)
        self.transcription_thread.start()
    
    def run_transcription(self):
        """Run the transcription process."""
        print("GUI DEBUG: Starting transcription thread")
        try:
            cmd = self.build_command()
            print(f"GUI DEBUG: Built command: {cmd}")
            
            self.progress_queue.put(("status", "Starting transcription..."))
            self.progress_queue.put(("progress", 10))
            print("GUI DEBUG: Added initial queue items")
            
            # Run the transcription with simple, reliable subprocess handling
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            self.current_process = process
            self.progress_queue.put(("status", "Transcription in progress..."))
            self.progress_queue.put(("progress", 20))
            print("GUI DEBUG: Process started, added progress items")
            
            # Start progress monitoring thread
            self.start_progress_monitoring()
            
            # Use communicate() for reliable output capture
            print("GUI DEBUG: Calling communicate()...")
            stdout, _ = process.communicate()
            print(f"GUI DEBUG: communicate() finished, stdout length: {len(stdout) if stdout else 0}")
            
            # Stop progress monitoring
            self.stop_progress_monitoring()
            
            # Process is done, check results
            return_code = process.returncode
            print(f"GUI DEBUG: Process return code: {return_code}")
            
            # Show all output at once
            if stdout:
                lines = stdout.split('\n')
                print(f"GUI DEBUG: Processing {len(lines)} output lines")
                
                # Look for specific progress indicators in the output
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    line_lower = line.lower()
                    
                    # Check for specific Whisper progress indicators
                    if "loading whisper" in line_lower or "loading model" in line_lower:
                        self.progress_queue.put(("progress", 25))
                    elif "100%" in line and ("decode" in line_lower or "transcrib" in line_lower):
                        self.progress_queue.put(("progress", 90))
                    elif any(keyword in line_lower for keyword in ["detected language", "processing", "transcribing"]):
                        self.progress_queue.put(("progress", 60))
            
            # Final status update based on return code
            if return_code == 0:
                self.progress_queue.put(("progress", 100))
                self.progress_queue.put(("status", "✅ Transcription completed successfully!"))
                print("GUI DEBUG: Added success messages to queue")
            else:
                self.progress_queue.put(("status", f"❌ Transcription failed (exit code: {return_code})"))
                print("GUI DEBUG: Added failure messages to queue")
            
        except FileNotFoundError:
            self.progress_queue.put(("status", f"❌ Error: {WHISPER_SCRIPT} not found"))
            print("GUI DEBUG: Added FileNotFoundError to queue")
        except Exception as e:
            self.progress_queue.put(("status", f"❌ Error: {str(e)}"))
            print(f"GUI DEBUG: Added exception to queue: {e}")
        finally:
            self.progress_queue.put(("done", None))
            print("GUI DEBUG: Added 'done' to queue, thread finishing")
    
    def start_progress_monitoring(self):
        """Start a background thread to simulate progress during transcription."""
        self.progress_monitoring = True
        self.progress_thread = threading.Thread(target=self._progress_monitor, daemon=True)
        self.progress_thread.start()
    
    def stop_progress_monitoring(self):
        """Stop the progress monitoring."""
        self.progress_monitoring = False
    
    def _progress_monitor(self):
        """Monitor progress and update the progress bar gradually."""
        import time
        progress = 20  # Start at 20% after process starts
        
        while self.progress_monitoring and progress < 95:
            time.sleep(2)  # Update every 2 seconds
            if self.progress_monitoring:
                progress += 5  # Increment by 5% each time
                self.progress_queue.put(("progress", min(progress, 95)))
                print(f"GUI DEBUG: Progress monitor updated to {min(progress, 95)}%")
    
    def stop_transcription(self):
        """Stop the current transcription."""
        self.is_transcribing = False
        self.stop_progress_monitoring()  # Stop progress monitoring
        if hasattr(self, 'current_process'):
            try:
                self.current_process.terminate()
            except Exception:
                pass
        
        self.status_var.set("Stopping transcription...")
    
    def check_progress(self):
        """Check for progress updates from the transcription thread."""
        try:
            items_processed = 0
            max_items_per_cycle = 5  # Limit items processed per cycle for better UI responsiveness
            
            while items_processed < max_items_per_cycle:
                item = self.progress_queue.get_nowait()
                items_processed += 1
                msg_type, data = item
                
                # Debug: Print to console what we're processing
                print(f"GUI DEBUG: Processing {msg_type}: {data}")
                
                if msg_type == "status":
                    self.status_var.set(data)
                    self.root.update_idletasks()  # Force UI update
                elif msg_type == "progress":
                    self.progress_var.set(data)
                    print(f"GUI DEBUG: Progress set to {data}")
                    self.root.update_idletasks()  # Force UI update
                elif msg_type == "done":
                    self.is_transcribing = False
                    self.transcribe_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    self.root.update_idletasks()  # Force UI update
                    print("GUI DEBUG: Transcription done, buttons reset")
            
            if items_processed > 0:
                print(f"GUI DEBUG: Processed {items_processed} queue items")
                    
        except queue.Empty:
            pass
        
        # Schedule next check - more frequent for better responsiveness
        self.root.after(50, self.check_progress)
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", output_dir])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
        else:
            messagebox.showwarning("Warning", f"Output directory does not exist: {output_dir}")
    
    def show_system_info(self):
        """Show system information dialog."""
        try:
            if not SYSTEM_INFO_AVAILABLE:
                messagebox.showerror("Error", "System info functions are not available.")
                return
            
            # Create info window
            info_window = tk.Toplevel(self.root)
            info_window.title("System Information")
            info_window.geometry("600x400")
            
            # Add text widget with system info
            text_widget = tk.Text(info_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Capture the output from the print functions
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                print_system_info()
                print_language_info()
            
            # Insert the captured output into the text widget
            system_info_text = output_buffer.getvalue()
            text_widget.insert(tk.END, system_info_text)
            text_widget.config(state=tk.DISABLED)
            
            # Add close button
            ttk.Button(info_window, text="Close", 
                      command=info_window.destroy).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system info: {str(e)}")
    
    def cleanup(self):
        """Clean up resources before closing."""
        # Stop recording if active
        if self.is_recording and self.recorder:
            self.stop_recording()
        
        # Clean up recorder
        if self.recorder:
            self.recorder.cleanup()


def main():
    """Main function to run the GUI application."""
    # Check if whisper_transcriber.py exists
    if not os.path.exists(WHISPER_SCRIPT):
        if getattr(sys, 'frozen', False):
            # In packaged mode, show a user-friendly error
            import tkinter.messagebox as msgbox
            msgbox.showerror("Missing Component", 
                           "The transcriber component is missing from the application bundle.\n"
                           "Please reinstall the application.")
        else:
            print(f"Error: {WHISPER_SCRIPT} not found in current directory.")
            print(f"Please run this GUI from the same directory as {WHISPER_SCRIPT}")
        return
    
    # Create and run the GUI
    root = tk.Tk()
    app = WhisperGUI(root)
    
    # Setup cleanup on window close
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nGUI closed by user")
        app.cleanup()


if __name__ == "__main__":
    main()