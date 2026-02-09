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

```bash
# Update system packages
sudo apt update

# Install Python 3 and pip (if not already installed)
sudo apt install python3 python3-pip python3-venv

# Install system dependencies for audio
sudo apt install portaudio19-dev python3-pyaudio

# For Whisper support (optional)
sudo apt install ffmpeg
```

### Install the Service

```bash
# Clone the repository
git clone https://github.com/MarcHumet/speech-to-text.git
cd speech-to-text

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the service
pip install -e .
```

### Install STT Model (Optional)

For production use, install OpenAI Whisper:

```bash
pip install openai-whisper
```

Or use another STT model of your choice and implement the interface in `stt_service/models/`.

## Quick Start

### 1. Create Configuration

```bash
# Create example configuration
python cli.py config --create -o config.yaml

# Edit the configuration
nano config.yaml
```

### 2. Test Components

```bash
# Test all components
python cli.py test

# Test specific component
python cli.py test audio
python cli.py test keyboard
python cli.py test clipboard
```

### 3. Run the Service

```bash
# Run with default configuration
python cli.py run

# Run with custom configuration
python cli.py run -c config.yaml

# Run with command-line overrides
python cli.py run -l es -o clipboard
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
  type: whisper  # dummy, whisper, or custom
  path: base     # Model size: tiny, base, small, medium, large
```

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
python cli.py run

# Run with Whisper
python cli.py run -m small

# Spanish transcription to clipboard
python cli.py run -l es -o clipboard
```

### Advanced Usage

```bash
# Create custom config
python cli.py config --create -o my-config.yaml

# Edit configuration
nano my-config.yaml

# Run with custom config
python cli.py run -c my-config.yaml
```

### Running as a Service

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
ExecStart=/home/your-username/speech-to-text/venv/bin/python cli.py run -c /home/your-username/.config/stt-service/config.yaml
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
python cli.py test

# Test with verbose output
python cli.py test -v
```

## Troubleshooting

### Audio Issues

```bash
# Check audio devices
python -m sounddevice

# Test audio recording
python cli.py test audio
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
pip install openai-whisper

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
