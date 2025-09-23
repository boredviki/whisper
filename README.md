# Wh## Features

- 🎯 **High Accuracy**: Uses Whisper large-v3 model for superior transcription quality
- 🌍 **Multi-Language**: Supports 99+ languages including English and Tagalog
- ⚡ **GPU Acceleration**: Automatic GPU detection and utilization (CUDA/Apple Silicon)
- 📱 **Offline Operation**: Works completely offline once models are downloaded
- 🎙️ **Built-in Recording**: Record audio directly in the app with real-time level monitoring
- 🎵 **Multiple Formats**: Supports MP3, WAV, M4A, FLAC, and many other audio formats
- 📝 **Multiple Outputs**: Export as TXT, JSON, SRT, VTT, and TSV formats
- ⏱️ **Timestamps**: Includes word-level timestamps for precise alignment
- 🖥️ **Dual Interface**: Both command-line and user-friendly GUI
- 🔧 **Easy to Use**: Drag-and-drop file selection and output folder browsing Transcription Tool

A powerful Python application that transcribes audio files to text using OpenAI's Whisper model with support for multiple languages including Tagalog and English. Features GPU acceleration for fast offline transcription and includes both command-line and graphical user interfaces.

## Features

- 🎯 **High Accuracy**: Uses Whisper large-v3 model for superior transcription quality
- 🌍 **Multi-Language**: Supports 99+ languages including English and Tagalog
- ⚡ **GPU Acceleration**: Automatic GPU detection and utilization (CUDA/Apple Silicon)
- 📱 **Offline Operation**: Works completely offline once models are downloaded
- 🎵 **Multiple Formats**: Supports MP3, WAV, M4A, FLAC, and many other audio formats
- 📝 **Multiple Outputs**: Export as TXT, JSON, SRT, VTT, and TSV formats
- ⏱️ **Timestamps**: Includes word-level timestamps for precise alignment
- �️ **Dual Interface**: Both command-line and user-friendly GUI
- 🔧 **Easy to Use**: Drag-and-drop file selection and output folder browsing

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **FFmpeg** (required for audio processing)

#### Install FFmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html) or use Chocolatey:
```bash
choco install ffmpeg
```

### Install Dependencies

1. **Clone or download this repository**
2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

### GPU Setup (Optional but Recommended)

#### For NVIDIA GPUs (CUDA)

1. **Install CUDA Toolkit** (version 11.8 or 12.1 recommended)
   - Download from [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads)

2. **Install PyTorch with CUDA support:**

For CUDA 11.8:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

For CUDA 12.1:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### For Apple Silicon Macs (M1/M2/M3)

PyTorch with Metal Performance Shaders (MPS) is automatically supported:
```bash
pip install torch torchvision torchaudio
```

## Usage

### 🖥️ Graphical Interface (Recommended for Beginners)

The easiest way to use the transcription tool is through the graphical interface:

```bash
# Launch the GUI
python whisper_gui.py

# Or use the launcher
python launch_gui.py
```

**GUI Features:**
- 📁 **File Browser**: Click "Browse..." to select audio files
- 🎙️ **Built-in Recording**: Record audio directly with real-time level monitoring
- 📂 **Output Folder**: Choose where to save transcriptions
- ⚙️ **Settings Panel**: Configure language, model, and options
- 📊 **Progress Tracking**: Real-time status and progress bar
- 📄 **Live Output**: See transcription progress in real-time
- 🎛️ **Format Selection**: Choose multiple output formats

### 🎙️ Recording & Transcription Workflow

1. **Launch GUI**: `python whisper_gui.py`
2. **Click "🔴 Start Recording"**: Begin recording audio
3. **Monitor Audio Levels**: Watch the real-time level meter
4. **Click "⏹ Stop Recording"**: Finish recording (auto-selects file)
5. **Configure Settings**: Choose language, model, output formats
6. **Click "🎤 Start Transcription"**: Process the recorded audio
7. **Get Results**: Open the output folder to access transcriptions

### ⌨️ Command Line Interface

```bash
# Basic transcription with auto-language detection
python whisper_transcriber.py audio.mp3

# Transcribe with specific language
python whisper_transcriber.py audio.wav --language en

# Transcribe Tagalog audio
python whisper_transcriber.py audio.m4a --language tl
```

### Advanced Usage

```bash
# Translate to English
python whisper_transcriber.py audio.mp3 --task translate

# Use different model size for faster processing
python whisper_transcriber.py audio.wav --model medium

# Force CPU usage (if GPU issues)
python whisper_transcriber.py audio.mp3 --device cpu

# Save multiple output formats
python whisper_transcriber.py audio.wav --output-formats txt json srt vtt

# Custom output directory
python whisper_transcriber.py audio.mp3 --output-dir my_transcriptions

# Verbose output for debugging
python whisper_transcriber.py audio.wav --verbose
```

### System Information

```bash
# Check system capabilities and supported languages
python whisper_transcriber.py --info
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--language` | `-l` | Language code (e.g., 'en', 'tl') | Auto-detect |
| `--model` | `-m` | Model size (tiny, base, small, medium, large, large-v2, large-v3) | large-v3 |
| `--device` | `-d` | Device (cuda, cpu, mps) | Auto-detect |
| `--task` | `-t` | Task (transcribe, translate) | transcribe |
| `--output-dir` | `-o` | Output directory | output |
| `--output-formats` | `-f` | Output formats (txt, json, srt, vtt, tsv) | txt json srt |
| `--verbose` | `-v` | Enable verbose output | False |
| `--info` | | Show system information | |

## Supported Languages

The tool supports 99+ languages. Here are some common ones:

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | `en` | Tagalog/Filipino | `tl` |
| Spanish | `es` | French | `fr` |
| German | `de` | Japanese | `ja` |
| Chinese | `zh` | Korean | `ko` |
| Portuguese | `pt` | Russian | `ru` |
| Italian | `it` | Dutch | `nl` |

*Use `python whisper_transcriber.py --info` to see system information and language support.*

## Supported Audio Formats

- **MP3** (.mp3)
- **WAV** (.wav)
- **M4A** (.m4a)
- **FLAC** (.flac)
- **OGG** (.ogg)
- **WMA** (.wma)
- **AAC** (.aac)
- And many others supported by FFmpeg

## Output Formats

### TXT Format
Plain text transcription:
```
Hello, this is a sample transcription of the audio file.
```

### JSON Format
Complete results with metadata and timestamps:
```json
{
  "text": "Hello, this is a sample transcription...",
  "segments": [...],
  "language": "en",
  "metadata": {
    "file_path": "audio.mp3",
    "model_size": "large-v3",
    "device": "cuda",
    "transcription_time": 15.2
  }
}
```

### SRT Format (Subtitles)
```
1
00:00:00,000 --> 00:00:03,000
Hello, this is a sample transcription

2
00:00:03,000 --> 00:00:06,000
of the audio file.
```

### VTT Format (Web subtitles)
```
WEBVTT

00:00:00.000 --> 00:00:03.000
Hello, this is a sample transcription

00:00:03.000 --> 00:00:06.000
of the audio file.
```

## Performance Guide

### Model Sizes and Performance

| Model | Size | Speed | Accuracy | VRAM Usage |
|-------|------|-------|----------|------------|
| tiny | 39 MB | ~32x | Good | ~1 GB |
| base | 74 MB | ~16x | Better | ~1 GB |
| small | 244 MB | ~6x | Good | ~2 GB |
| medium | 769 MB | ~2x | Better | ~5 GB |
| large-v3 | 1550 MB | 1x | Best | ~10 GB |

### Optimization Tips

1. **Use GPU**: GPU acceleration is 10-50x faster than CPU
2. **Model Selection**: Use `medium` for balance of speed/accuracy, `large-v3` for best quality
3. **Audio Quality**: Higher quality audio = better transcription accuracy
4. **Language Specification**: Specifying language improves accuracy and speed

## Troubleshooting

### Common Issues

#### "CUDA out of memory"
```bash
# Use smaller model or CPU
python whisper_transcriber.py audio.mp3 --model medium
python whisper_transcriber.py audio.mp3 --device cpu
```

#### "FFmpeg not found"
```bash
# Install FFmpeg (see installation section above)
# Or check if it's in your PATH
ffmpeg -version
```

#### "No module named 'whisper'"
```bash
# Install or reinstall whisper
pip install --upgrade openai-whisper
```

#### Slow transcription
```bash
# Check if GPU is being used
python whisper_transcriber.py --info

# Try different model sizes
python whisper_transcriber.py audio.mp3 --model medium  # Faster
python whisper_transcriber.py audio.mp3 --model small   # Even faster
```

### Getting Help

1. **Check system info**: `python whisper_transcriber.py --info`
2. **Use verbose mode**: `python whisper_transcriber.py audio.mp3 --verbose`
3. **Check GPU usage**: Monitor GPU usage during transcription
4. **Verify audio file**: Ensure audio file is not corrupted

### Recording Troubleshooting

**Recording not working:**
- **Microphone permissions**: Check System Preferences > Security & Privacy > Microphone
- **PyAudio installation**: Run `pip install pyaudio` (may need PortAudio: `brew install portaudio`)
- **Microphone conflict**: Close other apps using the microphone
- **Device selection**: Try different microphones if multiple are available

**No audio level detected:**
- **Check microphone**: Test in other applications (System Preferences > Sound > Input)
- **Volume settings**: Ensure microphone volume is not muted or too low
- **Permission**: Grant microphone access to Terminal/Python applications

**Recording quality issues:**
- **Distance**: Stay 6-12 inches from microphone
- **Environment**: Record in quiet environment
- **Levels**: Keep audio in green/yellow range, avoid red zone
- **Format**: Recordings are saved as high-quality WAV (44.1kHz, 16-bit)

## Examples

### Transcribing English Audio
```bash
python whisper_transcriber.py meeting_recording.mp3 --language en --output-formats txt srt
```

### Transcribing Tagalog Audio
```bash
python whisper_transcriber.py tagalog_speech.wav --language tl --output-dir tagalog_results
```

### Translating Non-English to English
```bash
python whisper_transcriber.py foreign_audio.m4a --task translate --output-formats txt json
```

### Batch Processing (using shell)
```bash
# Process all MP3 files in a directory
for file in *.mp3; do
    python whisper_transcriber.py "$file" --language en --output-dir batch_results
done
```

## Technical Details

### Model Information
- **Architecture**: Transformer-based encoder-decoder
- **Training Data**: 680,000 hours of multilingual audio
- **Capabilities**: Speech recognition, language identification, translation
- **Offline**: Models downloaded once, used offline thereafter

### Hardware Requirements
- **Minimum**: 4GB RAM, any CPU
- **Recommended**: 8GB+ RAM, NVIDIA GPU with 6GB+ VRAM
- **Optimal**: 16GB+ RAM, NVIDIA GPU with 12GB+ VRAM

## License

This project uses OpenAI's Whisper model, which is licensed under MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## Changelog

### v1.0.0
- Initial release
- Whisper large-v3 support
- GPU acceleration
- Multi-language support
- Multiple output formats
- Command-line interface