# Installation Guide

This guide will walk you through installing and setting up the Speech-to-Text service on Pop!_OS or Ubuntu.

## System Requirements

- Pop!_OS 20.04+ or Ubuntu 20.04+
- Python 3.8 or higher
- Microphone/audio input device
- At least 2GB free disk space (for models)
- Internet connection (for initial setup)

## Step-by-Step Installation

### 1. Install System Dependencies

```bash
# Update package lists
sudo apt update

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv

# Install audio libraries
sudo apt install -y portaudio19-dev python3-pyaudio

# Install FFmpeg (required for Whisper)
sudo apt install -y ffmpeg

# Install additional dependencies for keyboard/clipboard
sudo apt install -y xclip  # For X11 clipboard support
```

### 2. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/MarcHumet/speech-to-text.git
cd speech-to-text
```

### 3. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4. Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install the service in development mode
pip install -e .
```

### 5. Install STT Model

Choose one of the following options:

#### Option A: Dummy Model (Testing Only)

No additional installation needed. The dummy model is included for testing.

#### Option B: OpenAI Whisper (Recommended)

```bash
# Install Whisper
pip install openai-whisper

# Pre-download a model (optional but recommended)
# Available models: tiny, base, small, medium, large
python3 -c "import whisper; whisper.load_model('base')"
```

Model sizes and requirements:
- `tiny`: ~75 MB, fastest, lowest quality
- `base`: ~150 MB, good balance (recommended for testing)
- `small`: ~500 MB, better quality
- `medium`: ~1.5 GB, high quality
- `large`: ~3 GB, best quality

## Configuration

### 1. Create Configuration File

```bash
# Create example config
python cli.py config --create

# This creates config.yaml in the current directory
```

### 2. Edit Configuration

Open `config.yaml` in your preferred editor:

```bash
nano config.yaml
```

Key settings to configure:

```yaml
service:
  language: en  # Change to: es (Spanish) or ca (Catalan)

input:
  hotkey: ctrl+shift+space  # Change to your preferred hotkey

output:
  method: keyboard  # Options: keyboard, clipboard, both

model:
  type: whisper  # Change to: whisper (from dummy)
  path: base     # Change to: tiny, small, medium, or large
```

## First Run

### 1. Test Components

Before running the service, test that all components work:

```bash
# Test all components
python cli.py test

# You should see:
# ✓ Audio capture available
# ✓ Keyboard output available
# ✓ Clipboard output available
```

If any component shows ✗, install the missing dependency:

```bash
# For audio:
pip install sounddevice

# For keyboard:
pip install pynput

# For clipboard:
pip install pyperclip
```

### 2. Run the Service

```bash
# Run with dummy model (quick test)
python cli.py run

# Run with Whisper
python cli.py run -m base

# Run with Spanish
python cli.py run -l es
```

### 3. Test Speech Recognition

1. The service is now running
2. Press your hotkey (default: `Ctrl+Shift+Space`)
3. Speak into your microphone
4. Press the hotkey again to stop
5. The transcribed text should be typed automatically

Press `Ctrl+C` to stop the service.

## Troubleshooting

### Audio Not Working

```bash
# List audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
python3 -c "import sounddevice; print(sounddevice.rec(16000, samplerate=16000, channels=1))"
```

### Keyboard Output Not Working

```bash
# Add user to input group (may be required)
sudo usermod -a -G input $USER

# Log out and log back in for changes to take effect
```

### Hotkey Not Detected

```bash
# Try alternative backend
python cli.py run  # Uses 'keyboard' library by default
# If issues, edit config to use 'pynput' backend
```

### Permission Denied Errors

```bash
# Some operations may require additional permissions
# Run without sudo first; only escalate if necessary
```

## Running as System Service

To run the service automatically on startup:

### 1. Create systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/stt-service.service
```

Add this content (adjust paths to match your setup):

```ini
[Unit]
Description=Speech-to-Text Service
After=sound.target graphical.target

[Service]
Type=simple
User=YOUR_USERNAME
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/YOUR_USERNAME/.Xauthority"
WorkingDirectory=/home/YOUR_USERNAME/speech-to-text
ExecStart=/home/YOUR_USERNAME/speech-to-text/venv/bin/python /home/YOUR_USERNAME/speech-to-text/cli.py run
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
```

### 2. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable stt-service

# Start service now
sudo systemctl start stt-service

# Check status
sudo systemctl status stt-service

# View logs
journalctl -u stt-service -f
```

### 3. Manage Service

```bash
# Stop service
sudo systemctl stop stt-service

# Restart service
sudo systemctl restart stt-service

# Disable service (don't start on boot)
sudo systemctl disable stt-service
```

## Next Steps

- Read the [README.md](README.md) for usage examples
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
- Customize your configuration in `config.yaml`
- Try different models and languages
- Explore integrating custom STT models

## Getting Help

If you encounter issues:

1. Check the logs for error messages
2. Run component tests: `python cli.py test`
3. Try with the dummy model first to isolate issues
4. Check GitHub issues for similar problems
5. Open a new issue with detailed error information

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment and files
cd ..
rm -rf speech-to-text

# Remove system service (if installed)
sudo systemctl stop stt-service
sudo systemctl disable stt-service
sudo rm /etc/systemd/system/stt-service.service
sudo systemctl daemon-reload
```
