# Speech-to-Text Service

Self-hosted speech-to-text service for Pop!_OS (Linux) that replaces typing with speech input. Target languages: Spanish, English, and Catalan.

## Overview

This service allows you to dictate text instead of typing by pressing a configurable hotkey. The transcribed text can be automatically typed or copied to your clipboard, making it seamless to use across all applications.

## Features

- 🎤 **Hotkey-triggered recording**: Press a customizable hotkey to start/stop recording
- 🌍 **Multi-language support**: English, Spanish, and Catalan
- ⌨️ **Flexible output**: Type text directly or copy to clipboard
- 🔌 **Modular architecture**: Easy to extend with new models and features
- 🐧 **Linux-native**: Designed specifically for Pop!_OS and Ubuntu-based systems
- 🔧 **Model-agnostic**: Plug in your own STT models (Whisper, Vosk, custom)

## Architecture

The service uses a **hybrid modular architecture** (see [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design):

```
stt_service/
├── core/           # Core functionality (audio, config, engine)
├── input/          # Input handlers (hotkey detection)
├── output/         # Output handlers (keyboard, clipboard)
├── models/         # STT model interfaces
└── service.py      # Main service orchestrator
```

### Key Components

- **Audio Capture**: Records microphone input with configurable quality
- **STT Engine**: Abstract interface for speech-to-text models
- **Input Handler**: Detects hotkey presses to trigger recording
- **Output Handler**: Types text or copies to clipboard
- **Configuration**: YAML-based configuration with sensible defaults

## Installation

### Prerequisites

#### System Dependencies (Ubuntu/Debian)

```bash
# Update system packages
sudo apt update

# Install Python 3 and development tools (if not already installed)
sudo apt install python3 python3-pip python3-venv python3-dev

# Audio system dependencies
sudo apt install portaudio19-dev libasound2-dev

# GUI/X11 dependencies for keyboard automation
sudo apt install python3-tk python3-dev libx11-dev libxext-dev libxtst-dev libxss-dev

# Optional: FFmpeg for Whisper audio processing
sudo apt install ffmpeg

# Optional: Build tools for compiling Python packages
sudo apt install build-essential pkg-config

# For some audio processing packages
sudo apt install libjack-jackd2-dev

# GPU Acceleration (Optional but Recommended)
# For NVIDIA GPU support with faster-whisper:
sudo apt install nvidia-driver-580  # or latest available
# Verify GPU: nvidia-smi
```

#### Additional Requirements by Distribution

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install portaudio-devel python3-devel alsa-lib-devel
sudo dnf install libX11-devel libXext-devel libXtst-devel libXScrnSaver-devel
sudo dnf install ffmpeg  # may need RPM Fusion repository

# GPU acceleration (optional)
sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda
```

**Arch Linux:**
```bash
sudo pacman -S portaudio python python-pip alsa-lib
sudo pacman -S libx11 libxext libxtst libxss
sudo pacman -S ffmpeg

# GPU acceleration (optional)
sudo pacman -S nvidia nvidia-utils cuda
```

**macOS:**
```bash
# Install Homebrew first: https://brew.sh
brew install portaudio python
# XQuartz may be needed for GUI automation: https://xquartz.org
```

### Install uv (if not already installed)

uv is a fast Python package installer and resolver. If you don't have uv installed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on macOS with Homebrew
brew install uv

# Or on Windows with PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the Service

```bash
# Clone the repository
git clone https://github.com/MarcHumet/speech-to-text.git
cd speech-to-text

# Create virtual environment with uv (recommended)
uv venv
source .venv/bin/activate

# Install dependencies with uv
uv pip install -r requirements.txt

# Install the service
uv pip install -e .
```

### Install STT Models

#### Option 1: GPU-Accelerated (Recommended for NVIDIA GPUs)
For fast, memory-efficient transcription with GPU support:

```bash
# Install faster-whisper (GPU-optimized)
uv add faster-whisper

# Verify GPU is detected
nvidia-smi
```

#### Option 2: CPU-Only Whisper
For systems without NVIDIA GPU:

```bash
# Install standard OpenAI Whisper
uv add openai-whisper
```

#### Option 3: Custom Models
Implement your own STT model interface in `stt_service/core/engine.py`

### GPU Acceleration Setup

If you have an NVIDIA GPU with CUDA support:

1. **Check GPU availability:**
   ```bash
   nvidia-smi  # Should show your GPU
   ```

2. **Verify CUDA installation:**
   ```bash
   nvcc --version  # Should show CUDA version
   ```

3. **Configure for GPU in `config.yaml`:**
   ```yaml
   model:
     type: faster-whisper  # GPU-optimized engine
     path: tiny           # or base, small, medium, large
   ```

**GPU Benefits:**
- 🚀 **10-50x faster** transcription
- 🧠 **Lower RAM usage** (uses GPU VRAM instead)
- ⚡ **Real-time capable** for short clips
- 🎯 **Better accuracy** with faster processing

## Quick Start

### 1. Create Configuration

```bash
# Create example configuration
uv run cli.py config --create -o config.yaml

# Edit the configuration
nano config.yaml
```

### 2. Test Components

```bash
# Quick system check (recommended first)
uv run python -c "
import sys
print('🔍 System Dependency Check')
print('-' * 30)

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
    print('✅ STT: faster-whisper available (GPU-optimized)')
except ImportError:
    try:
        import whisper
        print('✅ STT: whisper available (CPU-only)')
    except ImportError:
        print('⚠️ STT: No whisper engine installed')

# Check GPU
try:
    import subprocess
    gpu_check = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    if gpu_check.returncode == 0:
        print('✅ GPU: NVIDIA GPU detected')
    else:
        print('ℹ️ GPU: No NVIDIA GPU (CPU-only mode)')
except:
    print('ℹ️ GPU: No NVIDIA drivers (CPU-only mode)')
    
print('\n🧪 Use \"uv run python cli.py test all\" for detailed tests')
"

# Test all components
uv run python cli.py test all

# Test specific components
uv run python cli.py test audio
uv run python cli.py test keyboard
uv run python cli.py test clipboard
```

### 3. Run the Service

```bash
# Run with default configuration
uv run python cli.py run

# Run with custom configuration
uv run python cli.py run -c config.yaml

# Run with command-line overrides
uv run python cli.py run -l es -o clipboard 
# uv run python cli.py run -l en  # English
# uv run python cli.py run -l es  # Spanish
# uv run python cli.py run -l ca  # Catalan
```

### 4. Use the Service

1. Start the service (it runs in the foreground)
2. Press the configured hotkey (default: `Ctrl+Shift+Space`)
3. Start speaking
4. Press the hotkey again to stop recording
5. The transcribed text will be typed or copied to clipboard

## Configuration

Configuration is managed via YAML files. See `config.yaml.example` for all options.

### Key Settings

```yaml
service:
  language: en  # en, es, ca
  audio_device: default

input:
  hotkey: ctrl+shift+space

output:
  method: keyboard  # keyboard, clipboard, both

model:
  type: faster-whisper  # dummy, whisper, faster-whisper (GPU-optimized)
  path: tiny            # Model size: tiny, base, small, medium, large

audio:
  max_duration: 5       # Maximum recording time (seconds)
  sample_rate: 16000    # Audio sample rate
```

### Model Options

| Model Type | Best For | GPU Support | Memory Usage | Speed |
|------------|----------|-------------|--------------|-------|
| `dummy` | Testing | N/A | Very Low | Instant |
| `whisper` | CPU-only systems | No | High | Slow |
| `faster-whisper` | NVIDIA GPUs | Yes | Low (uses VRAM) | Very Fast |

### Configuration Priority

1. Command-line arguments (highest)
2. Custom config file (`-c config.yaml`)
3. `./config.yaml` (current directory)
4. `~/.config/stt-service/config.yaml` (user config)
5. `/etc/stt-service/config.yaml` (system config)
6. Default values (lowest)

## Usage Examples

### Basic Usage

```bash
# Run with dummy model (for testing)
uv run python cli.py run

# Run with Whisper
uv run python cli.py run -m small

# Spanish transcription to clipboard
uv run python cli.py run -l es -o clipboard
```

### Advanced Usage

```bash
# Create custom config
uv run python cli.py config --create -o my-config.yaml

# Edit configuration
nano my-config.yaml

# Run with custom config
uv run python cli.py run -c my-config.yaml
```

### Running as a Systemd Service

To run as a systemd service (autostart on boot):

```bash
# Create systemd service file
sudo nano /etc/systemd/system/stt-service.service
```

Add the following content (adjust paths):

```ini
[Unit]
Description=Speech-to-Text Service
After=sound.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/speech-to-text
ExecStart=/home/your-username/speech-to-text/.venv/bin/python cli.py run -c /home/your-username/.config/stt-service/config.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable stt-service
sudo systemctl start stt-service
sudo systemctl status stt-service
```

## Development

### Project Structure

```
speech-to-text/
├── stt_service/              # Main package
│   ├── core/                 # Core components
│   │   ├── audio_capture.py  # Audio recording
│   │   ├── config.py         # Configuration management
│   │   └── engine.py         # STT engine interface
│   ├── input/                # Input handlers
│   │   ├── base.py           # Base class
│   │   └── hotkey.py         # Hotkey detection
│   ├── output/               # Output handlers
│   │   ├── base.py           # Base class
│   │   └── keyboard.py       # Keyboard & clipboard
│   ├── models/               # STT model implementations
│   └── service.py            # Main service
├── cli.py                    # Command-line interface
├── config.yaml.example       # Example configuration
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── ARCHITECTURE.md           # Architecture documentation
└── README.md                 # This file
```

### Adding a New STT Model

1. Create a new class in `stt_service/models/` that inherits from `STTEngine`
2. Implement required methods: `transcribe()`, `load_model()`, `is_ready()`
3. Add factory method in `stt_service/core/engine.py`

Example:

```python
from stt_service.core.engine import STTEngine

class MyCustomEngine(STTEngine):
    def load_model(self, model_path: str) -> None:
        # Load your model
        pass
    
    def transcribe(self, audio: np.ndarray, language: str = None) -> str:
        # Transcribe audio
        return "transcribed text"
    
    def is_ready(self) -> bool:
        return self.model is not None
```

### Testing

```bash
# Test all components
uv run python cli.py test

# Test with verbose output
uv run python cli.py test -v
```

## Troubleshooting

### System Dependencies

**PortAudio Issues:**
```bash
# If sounddevice fails to import
sudo apt install portaudio19-dev libasound2-dev
# Then reinstall sounddevice
uv pip uninstall sounddevice
uv pip install sounddevice
```

**X11/GUI Issues:**
```bash
# If pyautogui/pynput don't work
sudo apt install libx11-dev libxtst-dev python3-tk
# For Wayland users, you may need X11 session
# Or install additional Wayland support packages
```

**Audio Permission Issues:**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in, then test:
python -m sounddevice
```

### Audio Issues

```bash
# Check available audio devices
uv run python -c "import sounddevice as sd; print(sd.query_devices())"

# Test audio recording
uv run python cli.py test audio
```

### Keyboard/Input Issues

```bash
# Test keyboard output
uv run python cli.py test keyboard

# Test clipboard functionality  
uv run python cli.py test clipboard

# For global hotkeys, ensure X11 session (not Wayland)
echo $XDG_SESSION_TYPE  # should show 'x11'
```

### Permission Issues

Some features may require additional permissions:

```bash
# For keyboard emulation, you may need to add your user to input group
sudo usermod -a -G input $USER
# Log out and log back in for changes to take effect
```

### Model Not Loading

```bash
# For Whisper models
uv pip install openai-whisper

# Download specific model
python -c "import whisper; whisper.load_model('base')"
```

## Roadmap

- [ ] Voice activity detection (auto-start/stop)
- [ ] GUI configuration interface
- [ ] Support for more STT models (Vosk, Coqui)
- [ ] Cloud model API support
- [ ] macOS and Windows support
- [ ] Browser extension integration
- [ ] Custom commands and text replacements

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- Built for Pop!_OS and Ubuntu-based Linux distributions
- Designed with modularity and extensibility in mind
- Architecture optimized for local, privacy-focused speech-to-text
