#!/usr/bin/env python3
"""
Whisper Mini - Minimalist Transcription GUI
==========================================
...
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import subprocess
import time
from pathlib import Path

# --- Model auto-download logic ---
MODEL_URLS = {
    "tiny":     "https://huggingface.co/openai/whisper-tiny/resolve/main/tiny.bin",
    "base":     "https://huggingface.co/openai/whisper-base/resolve/main/base.bin",
    "small":    "https://huggingface.co/openai/whisper-small/resolve/main/small.bin",
    "medium":   "https://huggingface.co/openai/whisper-medium/resolve/main/medium.bin",
    "large":    "https://huggingface.co/openai/whisper-large/resolve/main/large.bin",
    "large-v2": "https://huggingface.co/openai/whisper-large-v2/resolve/main/large-v2.bin",
    "large-v3": "https://huggingface.co/openai/whisper-large-v3/resolve/main/large-v3.bin",
}
def ensure_model(model_name):
    if model_name not in MODEL_URLS:
        raise ValueError(f"Unknown model: {model_name}")
    models_dir = os.path.join(os.getcwd(), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f"{model_name}.bin")
    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model...")
        url = MODEL_URLS[model_name]
        try:
            import urllib.request
            urllib.request.urlretrieve(url, model_path)
            print(f"{model_name} model downloaded.")
        except Exception as e:
            print(f"Failed to download model: {e}")
            raise
    return model_path
# -----------------------------------

# Import audio recorder
try:
    from audio_recorder import AudioRecorder
    RECORDING_AVAILABLE = True
except ImportError:
    RECORDING_AVAILABLE = False

# Constants
def get_whisper_script_path():
    ...
WHISPER_SCRIPT = get_whisper_script_path()

class WhisperMini:
    ...
    def build_command(self):
        """Build the command line for whisper_transcriber.py."""
        python_exe = sys.executable
        cmd = [python_exe, WHISPER_SCRIPT]

        # Audio file
        cmd.append(self.audio_file_var.get())

        # Language
        if self.language_var.get() != "auto":
            cmd.extend(["--language", self.language_var.get()])

        # Model - ensure it's downloaded first
        model_name = self.model_var.get()
        model_path = ensure_model(model_name)  # <--- Ensure model is present
        cmd.extend(["--model", model_path])    # Pass the file path to the model

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
    ...
def main():
    ...
if __name__ == "__main__":
    main()
