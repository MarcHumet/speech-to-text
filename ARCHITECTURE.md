# Speech-to-Text Service Architecture Options

## Overview
Self-hosted speech-to-text service for Pop!_OS (Linux) that replaces typed text with speech input. Target languages: Spanish, English, and Catalan.

## Architectural Options

### Option 1: Daemon Service with D-Bus Integration
**Description**: A background daemon that listens for a hotkey, captures audio, processes it, and injects text using D-Bus and input device emulation.

**Components**:
- System daemon (systemd service)
- D-Bus interface for IPC
- Audio capture via PulseAudio/PipeWire
- Input device emulation (evdev/uinput)
- Hotkey detection (X11/Wayland)

**Pros**:
- Native Linux integration
- Low latency
- System-wide availability
- Works across all applications
- Efficient resource usage (runs in background)
- Proper Linux service management

**Cons**:
- More complex setup (systemd service)
- Requires root/privileged access for input device creation
- More complex to debug
- Display server dependencies (X11/Wayland differences)

### Option 2: Clipboard-Based Service
**Description**: A lightweight service that captures audio on hotkey, processes speech, and copies result to clipboard. User manually pastes.

**Components**:
- Background process
- Audio capture via ALSA/PulseAudio
- Clipboard integration (xclip/wl-clipboard)
- Hotkey listener

**Pros**:
- Simpler implementation
- No privileged access required
- Cross-platform compatible
- Easy to debug
- Works with any text input method

**Cons**:
- Requires manual paste action
- Less seamless user experience
- Limited to applications that support paste
- Extra step in workflow

### Option 3: Web Service + Browser Extension
**Description**: Local web server with API endpoints, browser extension for integration in web apps.

**Components**:
- Flask/FastAPI web service
- REST API
- Browser extension (Chrome/Firefox)
- Web interface for configuration

**Pros**:
- Web-based UI for configuration
- Easy to extend with additional features
- No system-level integration required
- Cross-browser support
- Easy remote access potential

**Cons**:
- Limited to browser applications only
- Won't work in native apps
- Higher resource usage
- Browser dependency
- Not system-wide solution

### Option 4: Hybrid Modular Service
**Description**: Modular Python service with pluggable backends for different integration methods.

**Components**:
- Core STT engine (model interface)
- Pluggable input modules (hotkey detection)
- Pluggable output modules (keyboard emulation, clipboard, API)
- Configuration system
- CLI and optional GUI

**Pros**:
- Maximum flexibility
- Can support multiple use cases
- Easy to extend and maintain
- User can choose integration method
- Clean separation of concerns
- Easier testing and development

**Cons**:
- More initial development time
- Requires good architecture design
- Potentially more configuration needed

## Recommendation: Option 4 - Hybrid Modular Service

**Rationale**:
1. **Flexibility**: Supports multiple integration methods (keyboard, clipboard, API)
2. **Maintainability**: Clean modular design makes it easy to extend
3. **Development**: Model development happens separately, architecture must accommodate this
4. **User Choice**: Users can choose their preferred integration method
5. **Linux Compatibility**: Can adapt to different Linux environments (X11/Wayland)
6. **Future-Proof**: Easy to add new features and integration methods

## Detailed Architecture Design

### Core Components

```
speech-to-text/
├── stt_service/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── audio_capture.py      # Audio recording
│   │   ├── engine.py              # STT model interface
│   │   └── config.py              # Configuration management
│   ├── input/
│   │   ├── __init__.py
│   │   ├── hotkey.py              # Hotkey detection
│   │   └── base.py                # Input handler base class
│   ├── output/
│   │   ├── __init__.py
│   │   ├── keyboard.py            # Keyboard emulation
│   │   ├── clipboard.py           # Clipboard integration
│   │   └── base.py                # Output handler base class
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py                # Model interface (plug models here)
│   └── service.py                 # Main service orchestrator
├── cli.py                          # Command-line interface
├── setup.py                        # Installation script
├── requirements.txt                # Python dependencies
├── config.yaml.example             # Example configuration
└── README.md                       # Documentation
```

### Data Flow

1. **Input Detection**: Hotkey pressed → Input handler detects
2. **Audio Capture**: Record audio from microphone
3. **Processing**: Send audio to STT model
4. **Output**: Send transcribed text to output handler (keyboard/clipboard)
5. **Feedback**: Optional visual/audio feedback to user

### Key Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Plugin Architecture**: Easy to add new input/output methods
3. **Configuration-Driven**: Behavior controlled via config files
4. **Model Agnostic**: Core doesn't care about model implementation
5. **Async-First**: Use asyncio for non-blocking operations
6. **Error Handling**: Graceful degradation and clear error messages

### Technology Stack

**Core**:
- Python 3.9+
- asyncio for async operations
- PyYAML for configuration

**Audio**:
- pyaudio or sounddevice for audio capture
- numpy for audio processing

**Input**:
- pynput or keyboard for hotkey detection
- evdev for low-level input (optional)

**Output**:
- pynput for keyboard emulation
- pyperclip or xerox for clipboard
- python-uinput for advanced keyboard simulation (optional)

**Models**:
- Interface for plugging in Whisper, Vosk, or custom models
- Support for local and remote model loading

### Configuration Example

```yaml
service:
  language: es  # es, en, ca
  audio_device: default
  
input:
  method: hotkey
  hotkey: ctrl+shift+space
  
output:
  method: keyboard  # keyboard, clipboard, both
  
model:
  type: whisper  # whisper, vosk, custom
  path: models/whisper-small-es
  
audio:
  sample_rate: 16000
  channels: 1
  max_duration: 30  # seconds
```

## Implementation Phases

### Phase 1: Core Framework ✓
- Project structure
- Configuration management
- Base classes and interfaces

### Phase 2: Audio Capture
- Microphone access
- Audio recording
- Audio preprocessing

### Phase 3: Model Interface
- Abstract model interface
- Example/stub implementation
- Model loading and inference

### Phase 4: Input Handler
- Hotkey detection
- Start/stop recording logic

### Phase 5: Output Handler
- Keyboard emulation
- Clipboard integration

### Phase 6: Service Integration
- Main service loop
- Error handling
- Logging

### Phase 7: CLI and Documentation
- Command-line interface
- Installation instructions
- Usage documentation

## Questions for Consideration

1. **Permissions**: Will users be comfortable running with required permissions?
2. **Display Server**: Should we support both X11 and Wayland from the start?
3. **Model Loading**: Should models be loaded on startup or on-demand?
4. **Feedback**: What kind of user feedback (visual, audio, notification)?
5. **Multi-language**: Should language switching be dynamic or config-based?
