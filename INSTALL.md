# Installation Guide

This guide will walk you through installing and setting up the Speech-to-Text service on Pop!_OS or Ubuntu.

## System Requirements

- Pop!_OS 20.04+ or Ubuntu 20.04+
- Python 3.8 or higher
- Microphone/audio input device
- At least 4GB free disk space (for models and GPU libraries)
- Internet connection (for initial setup)
- **Optional but Recommended**: NVIDIA GPU with 4GB+ VRAM for GPU acceleration

## GPU Acceleration (Optional but Recommended)

For 10-50x faster transcription, install NVIDIA GPU support:

```bash
# Check if you have NVIDIA GPU
nvidia-smi

# Install NVIDIA drivers (if needed)
sudo apt install nvidia-driver-580  # or latest available

# Verify GPU is detected
nvidia-smi
```

## Step-by-Step Installation

### 1. Install System Dependencies

```bash
# Update package lists
sudo apt update

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Audio system dependencies
sudo apt install -y portaudio19-dev libasound2-dev

# GUI/X11 dependencies for keyboard automation
sudo apt install -y python3-tk libx11-dev libxext-dev libxtst-dev libxss-dev

# Install FFmpeg (required for Whisper)
sudo apt install -y ffmpeg

# Build tools for compiling packages
sudo apt install -y build-essential pkg-config

# Additional audio processing libraries
sudo apt install -y libjack-jackd2-dev

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart terminal or run: source ~/.profile
```

### 2. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/MarcHumet/speech-to-text.git
cd speech-to-text
```

### 3. Set Up Python Environment with uv

```bash
# Create virtual environment with uv (recommended)
uv venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip (uv handles this automatically)
# pip install --upgrade pip  # Not needed with uv
```

### 4. Install Python Dependencies

```bash
# Install core dependencies with uv (faster)
uv pip install -r requirements.txt

# Install the service in development mode
uv pip install -e .
```

### 5. Install STT Engine

Choose the best option for your hardware:

#### Option A: GPU-Accelerated (Recommended for NVIDIA GPUs)

```bash
# Install faster-whisper (GPU-optimized)
uv add faster-whisper

# Verify GPU is available
nvidia-smi

# Test GPU acceleration
uv run python -c "from faster_whisper import WhisperModel; print('GPU support available!')"
```

#### Option B: CPU-Only Whisper

```bash
# Install standard OpenAI Whisper
uv add openai-whisper

# Pre-download a model (recommended)
python3 -c "import whisper; whisper.load_model('base')"
```

#### Option C: Testing Only (Not Recommended)

```bash
# Dummy model is already included
# Only use for initial testing - produces random text
```

**Model Performance Comparison:**

| Model Type | GPU Support | Speed | Memory | Quality |
|------------|-------------|-------|--------|---------|
| `faster-whisper` | ✅ NVIDIA | Very Fast | Low (VRAM) | Excellent |
| `whisper` | ❌ CPU-only | Slow | High (RAM) | Good |
| `dummy` | ❌ Testing | Instant | Very Low | Random text |

**Recommended Model Sizes:**
- `tiny`: ~75 MB, fastest, good for short phrases
- `base`: ~150 MB, **recommended balance** of speed/quality
- `small`: ~500 MB, better quality, slower
- `medium`: ~1.5 GB, high quality
- `large`: ~3 GB, best quality, requires more VRAM

## Configuration

### 1. Create Configuration File

```bash
# Create example config using uv
uv run python cli.py config --create

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
  type: faster-whisper  # GPU-optimized (recommended)
  path: base           # Good balance of speed/quality

audio:
  sample_rate: 16000    # Standard for Whisper
  max_duration: 20      # Maximum recording time (seconds)
```

**Engine Options:**
- `faster-whisper`: GPU-accelerated, **recommended**
- `whisper`: CPU-only fallback
- `dummy`: Testing only (produces random text)

## First Run

### 1. Test Components

Before running the service, test that all components work:

```bash
# Quick system check with GPU detection
uv run python -c "
import sys
print('🔍 System Check')
print('-' * 20)

try:
    import sounddevice
    print('✅ Audio: sounddevice available')
except Exception as e:
    print(f'❌ Audio: {e}')

try:
    import pyautogui
    print('✅ GUI: pyautogui available')
except Exception as e:
    print(f'❌ GUI: {e}')

try:
    import pynput
    print('✅ Input: pynput available')
except Exception as e:
    print(f'❌ Input: {e}')

# Check STT engines
try:
    import faster_whisper
    print('✅ STT: faster-whisper (GPU-optimized) available')
except ImportError:
    try:
        import whisper
        print('✅ STT: whisper (CPU-only) available')
    except ImportError:
        print('❌ STT: No whisper engine installed')

# Check GPU
try:
    import subprocess
    gpu = subprocess.run(['nvidia-smi'], capture_output=True)
    if gpu.returncode == 0:
        print('✅ GPU: NVIDIA GPU detected')
    else:
        print('ℹ️ GPU: No NVIDIA GPU (CPU-only mode)')
except:
    print('ℹ️ GPU: No NVIDIA drivers')
"

# Comprehensive component tests
uv run python cli.py test all

# Test specific components
uv run python cli.py test audio
uv run python cli.py test keyboard
uv run python cli.py test clipboard
```

If any component shows ❌, install the missing dependency:

```bash
# For audio:
uv pip install sounddevice

# For GUI automation:
uv pip install pyautogui

# For input detection:
uv pip install pynput

# For clipboard:
uv pip install pyperclip

# For GPU acceleration:
uv add faster-whisper

# For CPU-only STT:
uv add openai-whisper
```

### 2. Run the Service

```bash
# Run with default configuration (faster-whisper + base model)
uv run python cli.py run

# Run with custom configuration
uv run python cli.py run -c config.yaml

# Language-specific runs
uv run python cli.py run -l en  # English
uv run python cli.py run -l es  # Spanish
uv run python cli.py run -l ca  # Catalan

# Output to clipboard instead of typing
uv run python cli.py run -o clipboard
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
