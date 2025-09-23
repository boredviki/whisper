# 🖥️ GUI User Guide

Welcome to the Whisper Transcription GUI! This user-friendly interface makes audio transcription easy without needing to use command lines.

## 🚀 Quick Start

### Launch the GUI
```bash
python whisper_gui.py
```

Or use the launcher:
```bash
python launch_gui.py
```

## 📖 Interface Guide

### 1. 📁 File Selection
- **Browse Button**: Click to select your audio file
- **Supported Formats**: MP3, WAV, M4A, FLAC, OGG, WMA, AAC
- **Tip**: You can also right-click in the file field to paste a file path

### 2. 🎙️ Audio Recording (NEW!)
- **Record Button**: Click "🔴 Start Recording" to begin recording
- **Live Audio Level**: Real-time visualization of recording volume
- **Recording Timer**: Shows current recording duration (MM:SS)
- **Recording Status**: Displays current recording state
- **Save Options**:
  - **Temporary folder**: Auto-selects recorded file for immediate transcription
  - **Output folder**: Saves to your chosen output directory
- **One-Click Workflow**: Record → Auto-select → Transcribe seamlessly

### 3. 📤 Output Settings
- **Output Folder**: Choose where to save your transcriptions
- **Output Formats**: Select multiple formats:
  - **TXT**: Plain text transcription
  - **JSON**: Detailed results with timestamps
  - **SRT**: Subtitle files for videos
  - **VTT**: Web subtitle format
  - **TSV**: Spreadsheet-compatible format

### 4. ⚙️ Transcription Settings

#### Language Selection
- **Auto**: Let Whisper detect the language automatically
- **English (en)**: Force English transcription
- **Tagalog (tl)**: Force Tagalog/Filipino transcription
- **Others**: Spanish (es), French (fr), Japanese (ja), etc.

#### Model Selection
| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|---------|----------|
| tiny | ⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Quick tests |
| small | ⚡⚡⚡ | ⭐⭐⭐ | ~2GB | Fast processing |
| medium | ⚡⚡ | ⭐⭐⭐⭐ | ~5GB | **Balanced** |
| large-v3 | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | **Best quality** |

#### Task Selection
- **Transcribe**: Convert speech to text in original language
- **Translate**: Convert speech to English text

#### Device Selection
- **Auto**: Automatically choose the best device
- **CPU**: Use processor (slower but reliable)
- **MPS**: Use Apple Silicon GPU (if available)
- **CUDA**: Use NVIDIA GPU (if available)

### 5. 🎬 Running Transcription

1. **Select Audio File**: Click "Browse..." and choose your audio OR record new audio
2. **Configure Settings**: Adjust language, model, and output options
3. **Click "Start Transcription"**: Begin the process
4. **Monitor Progress**: Watch the progress bar and live output
5. **Stop if Needed**: Click "Stop" to cancel transcription

### 6. 📊 Progress Monitoring

- **Progress Bar**: Shows overall completion percentage
- **Status**: Current transcription step
- **Live Output**: Real-time transcription messages
- **Completion**: Success message with output location

### 7. 📁 Accessing Results

- **"Open Output Folder"**: Opens the results folder automatically
- **Multiple Files**: Find your transcriptions in different formats
- **File Names**: Based on original audio filename

## 🎙️ Recording Workflow

### Quick Recording & Transcription
1. **Click "🔴 Start Recording"**: Begin recording immediately
2. **Monitor Audio Level**: Watch the green/yellow/red level meter
3. **Speak Clearly**: Ensure good audio levels (avoid red zone)
4. **Click "⏹ Stop Recording"**: Finish recording
5. **Auto-Selection**: File is automatically selected for transcription
6. **Start Transcription**: Click "🎤 Start Transcription"
7. **Get Results**: Transcription appears in your output folder

### Recording Tips
- **Good Audio Levels**: Keep levels in green/yellow range (avoid red)
- **Clear Speech**: Speak clearly and at normal pace
- **Quiet Environment**: Minimize background noise
- **Microphone Distance**: Stay 6-12 inches from microphone
- **Recording Length**: No limit, but longer recordings take more time to transcribe

### Recording Options
- **Temporary Folder**: Records to temp folder and auto-selects for transcription
- **Output Folder**: Saves recording to your chosen output directory for keeping
- **Format**: All recordings are saved as high-quality WAV files (44.1kHz, 16-bit)

## 💡 Tips for Best Results

### Audio Quality
- Use clear, high-quality recordings
- Minimize background noise
- Ensure good microphone placement

### Language Settings
- Specify language when known for better accuracy
- Use "auto" for mixed-language content
- Try "translate" to convert to English

### Model Selection
- Start with "medium" for good balance
- Use "large-v3" for best quality
- Try "small" if processing is slow

### Performance
- Check "System Info" to see GPU availability
- Use GPU when available for faster processing
- Close other applications for better performance

## 🆘 Troubleshooting

### Common Issues

**"Audio file not found"**
- Check file path is correct
- Ensure file exists and isn't corrupted

**"No output formats selected"**
- Select at least one output format (TXT, JSON, SRT, etc.)

**"Transcription failed"**
- Check the live output for error details
- Try a different model size
- Verify audio file format is supported

**Slow transcription**
- Check "System Info" for GPU status
- Try smaller model (medium → small → tiny)
- Ensure sufficient RAM available

**GUI won't start**
- Ensure you're in the correct directory
- Verify whisper_transcriber.py exists
- Check Python and tkinter installation

**Recording not working**
- Verify microphone permissions in System Preferences
- Check that pyaudio is installed: `pip install pyaudio`
- Try different microphone if multiple are available
- Ensure microphone is not being used by other applications

**No audio level detected**
- Check microphone permissions
- Verify microphone is working in other applications
- Try adjusting microphone volume in system settings
- Check if microphone is muted

### Getting Help

1. **System Info**: Click "ℹ️ System Info" for system status
2. **Live Output**: Check the output area for error messages
3. **Command Line**: Use `python whisper_transcriber.py --help` for options
4. **Documentation**: Read README.md for detailed information

## 🎯 Workflow Examples

### Basic Transcription
1. Launch GUI: `python whisper_gui.py`
2. Browse and select audio file
3. Keep default settings (auto language, large-v3 model)
4. Click "Start Transcription"
5. Wait for completion
6. Click "Open Output Folder" to see results

### Creating Subtitles
1. Select your audio/video file's audio OR record directly in the app
2. Choose output formats: SRT and VTT
3. Set language to match content
4. Use medium or large-v3 model for accuracy
5. Start transcription
6. Use .srt file with video players

### Multi-language Content
1. Set language to "auto"
2. Use large-v3 model for best detection
3. Select multiple output formats
4. Review JSON output for language confidence

### Record & Transcribe Workflow
1. Click "🔴 Start Recording"
2. Speak your content clearly
3. Monitor audio levels (stay in green/yellow)
4. Click "⏹ Stop Recording" when done
5. File is auto-selected for transcription
6. Choose your preferred settings
7. Click "🎤 Start Transcription"
8. Get instant results!

### Quick Testing
1. Use "tiny" or "small" model
2. Select only TXT format
3. Start transcription for quick results

## 🎉 Success!

You're now ready to transcribe audio with the user-friendly GUI! The interface makes it easy to:

- Select files visually
- Configure options with dropdowns
- Monitor progress in real-time
- Access results with one click

Happy transcribing! 🎤✨