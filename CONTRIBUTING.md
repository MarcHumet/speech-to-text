# Contributing Guide

Thank you for your interest in contributing to the Speech-to-Text service! This guide will help you extend and customize the system.

## Development Setup

```bash
# Clone and setup
git clone https://github.com/MarcHumet/speech-to-text.git
cd speech-to-text

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements.txt
```

## Architecture Overview

The service uses a modular architecture with clear separation of concerns:

```
stt_service/
├── core/           # Core functionality
│   ├── config.py           # Configuration management
│   ├── audio_capture.py    # Audio recording
│   └── engine.py           # STT engine interface
├── input/          # Input handlers
│   ├── base.py            # Base input handler
│   └── hotkey.py          # Hotkey detection
├── output/         # Output handlers
│   ├── base.py            # Base output handler
│   └── keyboard.py        # Keyboard/clipboard output
├── models/         # Model implementations
└── service.py      # Main service orchestrator
```

## Adding a New STT Model

### Step 1: Create Model Class

Create a new file in `stt_service/models/` or add to `core/engine.py`:

```python
from stt_service.core.engine import STTEngine
import numpy as np

class MyCustomEngine(STTEngine):
    """Custom STT engine."""
    
    def __init__(self):
        self.model = None
        self.ready = False
    
    def load_model(self, model_path: str) -> None:
        """Load your model."""
        # Load model from path
        # self.model = load_your_model(model_path)
        self.ready = True
    
    def transcribe(self, audio: np.ndarray, language: str = None) -> str:
        """Transcribe audio to text."""
        if not self.ready:
            raise RuntimeError("Model not loaded")
        
        # Process audio with your model
        # text = self.model.transcribe(audio)
        # return text
        return "Transcribed text"
    
    def is_ready(self) -> bool:
        """Check if model is ready."""
        return self.ready
```

### Step 2: Register in Factory

Edit `stt_service/core/engine.py`, add to `create_engine()`:

```python
def create_engine(engine_type: str = 'dummy', model_path: str = '') -> STTEngine:
    """Factory function to create STT engines."""
    if engine_type.lower() == 'whisper':
        engine = WhisperEngine()
    elif engine_type.lower() == 'mycustom':  # Add this
        engine = MyCustomEngine()
    else:
        engine = DummyEngine()
    
    if model_path:
        engine.load_model(model_path)
    
    return engine
```

### Step 3: Use in Configuration

```yaml
model:
  type: mycustom
  path: /path/to/your/model
```

## Adding a New Input Method

### Step 1: Create Input Handler

Create `stt_service/input/custom_input.py`:

```python
from .base import InputHandler
from typing import Callable

class CustomInputHandler(InputHandler):
    """Custom input handler."""
    
    def __init__(self, config: dict):
        self.config = config
        self._active = False
        self._callback = None
    
    def start(self, callback: Callable[[], None]) -> None:
        """Start listening for input."""
        self._callback = callback
        self._active = True
        # Setup your input listener
    
    def stop(self) -> None:
        """Stop listening."""
        self._active = False
        # Cleanup
    
    def is_active(self) -> bool:
        """Check if active."""
        return self._active
```

### Step 2: Integrate in Service

Edit `stt_service/service.py` to use your handler:

```python
from .input.custom_input import CustomInputHandler

# In _initialize_components():
if input_method == 'custom':
    self.input_handler = CustomInputHandler(config)
```

## Adding a New Output Method

### Step 1: Create Output Handler

Create `stt_service/output/custom_output.py`:

```python
from .base import OutputHandler

class CustomOutputHandler(OutputHandler):
    """Custom output handler."""
    
    def __init__(self):
        self.available = True
    
    def send_text(self, text: str) -> bool:
        """Send text to your custom output."""
        try:
            # Implement your output logic
            # e.g., send to API, websocket, file, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if output is available."""
        return self.available
```

### Step 2: Register in Factory

Edit `stt_service/output/keyboard.py`, add to `create_output_handler()`:

```python
def create_output_handler(method: str = 'keyboard') -> OutputHandler:
    """Factory function to create output handlers."""
    method = method.lower()
    
    if method == 'keyboard':
        return KeyboardHandler()
    elif method == 'clipboard':
        return ClipboardHandler()
    elif method == 'custom':  # Add this
        from .custom_output import CustomOutputHandler
        return CustomOutputHandler()
    elif method == 'both':
        return CompositeHandler(KeyboardHandler(), ClipboardHandler())
    else:
        return KeyboardHandler()
```

## Extending Configuration

### Adding New Config Options

Edit `stt_service/core/config.py`, update `DEFAULT_CONFIG`:

```python
DEFAULT_CONFIG = {
    # ... existing config ...
    'mycustom': {
        'option1': 'value1',
        'option2': 'value2',
    }
}
```

Access in your code:

```python
config = Config()
value = config.get('mycustom.option1')
```

## Adding CLI Commands

Edit `cli.py` to add new subcommands:

```python
# Add new subparser
custom_parser = subparsers.add_parser('custom', help='Custom command')
custom_parser.add_argument('--option', type=str, help='Custom option')

# Handle in main()
if args.command == 'custom':
    custom_command(args)

# Implement handler
def custom_command(args):
    """Handle custom command."""
    print(f"Custom command with option: {args.option}")
```

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to all public functions/classes
- Keep functions focused and single-purpose

Example:

```python
def process_audio(audio: np.ndarray, language: str = 'en') -> str:
    """Process audio and return transcription.
    
    Args:
        audio: Audio data as numpy array
        language: Language code (default: 'en')
        
    Returns:
        Transcribed text
        
    Raises:
        ValueError: If audio is empty
    """
    if len(audio) == 0:
        raise ValueError("Audio data is empty")
    
    # Process...
    return text
```

### Logging

Use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Error Handling

```python
try:
    # Operation
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}")
    # Handle gracefully
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Fallback behavior
finally:
    # Cleanup
    pass
```

## Testing

### Manual Testing

```bash
# Test specific component
python cli.py test audio

# Run with verbose logging
python cli.py run -v

# Test with dummy model first
python cli.py run -m dummy
```

### Adding Unit Tests

Create test files in a `tests/` directory:

```python
import unittest
from stt_service.core.config import Config

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        config = Config()
        self.assertEqual(config.get('service.language'), 'en')
    
    def test_set_value(self):
        config = Config()
        config.set('service.language', 'es')
        self.assertEqual(config.get('service.language'), 'es')

if __name__ == '__main__':
    unittest.main()
```

## Example: Adding Vosk Model Support

Here's a complete example of adding Vosk STT model:

### 1. Create VoskEngine

```python
# In stt_service/core/engine.py

class VoskEngine(STTEngine):
    """Vosk STT engine."""
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.ready = False
    
    def load_model(self, model_path: str) -> None:
        """Load Vosk model."""
        try:
            from vosk import Model, KaldiRecognizer
            import json
            
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.ready = True
            logger.info("Vosk model loaded successfully")
        except ImportError:
            raise RuntimeError("Install vosk: pip install vosk")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise
    
    def transcribe(self, audio: np.ndarray, language: str = None) -> str:
        """Transcribe using Vosk."""
        if not self.ready:
            raise RuntimeError("Vosk model not loaded")
        
        try:
            import json
            
            # Convert to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Process audio
            self.recognizer.AcceptWaveform(audio_int16.tobytes())
            result = json.loads(self.recognizer.FinalResult())
            
            return result.get('text', '')
        except Exception as e:
            logger.error(f"Vosk transcription failed: {e}")
            return ""
    
    def is_ready(self) -> bool:
        return self.ready
```

### 2. Update Factory

```python
def create_engine(engine_type: str = 'dummy', model_path: str = '') -> STTEngine:
    if engine_type.lower() == 'whisper':
        engine = WhisperEngine()
    elif engine_type.lower() == 'vosk':
        engine = VoskEngine()
    else:
        engine = DummyEngine()
    
    if model_path:
        engine.load_model(model_path)
    
    return engine
```

### 3. Update Config

```yaml
model:
  type: vosk
  path: /path/to/vosk-model-en
```

### 4. Update Requirements

Add to `requirements.txt`:
```
# Optional: Vosk for STT
# vosk>=0.3.45
```

## Debugging Tips

### Enable Verbose Logging

```bash
python cli.py run -v
```

### Check Component Status

```bash
python cli.py test
```

### Test Audio Capture

```python
from stt_service.core.audio_capture import AudioCapture

capture = AudioCapture()
capture.start_recording()
# Speak for a few seconds
audio = capture.stop_recording()
print(f"Captured {len(audio)} samples")
```

### Test Engine

```python
from stt_service.core.engine import create_engine
import numpy as np

engine = create_engine('dummy')
audio = np.random.randn(16000)  # 1 second of random audio
text = engine.transcribe(audio)
print(f"Result: {text}")
```

## Best Practices

1. **Modularity**: Keep components independent
2. **Configuration**: Make behavior configurable
3. **Logging**: Add logging for debugging
4. **Error Handling**: Handle errors gracefully
5. **Documentation**: Document your code
6. **Testing**: Test before committing

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Questions?

- Check the [ARCHITECTURE.md](ARCHITECTURE.md) for design details
- See [README.md](README.md) for general information
- Open an issue on GitHub for questions

Happy coding! 🚀
