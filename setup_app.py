#!/usr/bin/env python3
"""
Setup script for creating a macOS .app bundle for Whisper GUI
"""

from setuptools import setup

# App configuration
APP = ['whisper_gui.py']

# Data files to include
DATA_FILES = [
    ('', ['whisper_transcriber.py']),  # Include the transcriber script
]

# Options for py2app
OPTIONS = {
    'argv_emulation': False,  # Don't emulate command line arguments
    'plist': {
        'CFBundleName': 'Whisper Transcriber',
        'CFBundleDisplayName': 'Whisper Transcriber',
        'CFBundleGetInfoString': 'Audio transcription using OpenAI Whisper',
        'CFBundleIdentifier': 'com.victoriakintanar.whispertranscriber',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 Victoria Kintanar',
        'NSHighResolutionCapable': True,  # Support retina displays
        'LSMinimumSystemVersion': '10.15',  # Minimum macOS version
    },
    'packages': [
        'whisper',
        'torch',
        'torchaudio', 
        'tiktoken',
        'numpy',
        'pyaudio',
        'tkinter',
        'pathlib',
        'queue',
        'threading',
        'subprocess',
        'ssl',
        'urllib',
        'certifi',
    ],
    'includes': [
        'whisper',
        'torch',
        'torchaudio',
        'tiktoken',
        'ssl',
        'certifi',
    ],
    'excludes': [
        'matplotlib',
        'scipy',
        'PIL',
        'IPython',
        'jupyter',
    ],
    'resources': [],
    'iconfile': None,  # You can add an .icns file here if you have one
    'strip': False,  # Don't strip debug symbols
}

setup(
    name='Whisper Transcriber',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    python_requires='>=3.8',
)