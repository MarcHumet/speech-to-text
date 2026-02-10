# Logging System Documentation

## Overview

The STT Service now includes a comprehensive logging system using Loguru that provides:
- **Malfunction Detection**: Easily identify and debug system issues
- **Performance Monitoring**: Track operation timing and bottlenecks
- **Log Rotation**: Automatic log management (1 week + 10MB rotation)
- **Structured Logging**: Rich context for debugging and analysis

## Log Files

The system creates three main log files in the `logs/` directory:

- **`stt_service.log`** - Main log with all levels (rotated weekly)
- **`stt_service_size.log`** - Size-based rotation (10MB limit)
- **`stt_service_errors.log`** - Warnings and errors only

## Key Features

### 🚨 Malfunction Detection

Automatically logs system malfunctions with full context:

```python
log_malfunction("AudioCapture", "Microphone not found", "ERROR", device_id="default")
log_malfunction("STTEngine", "Model loading timeout", "CRITICAL", model="whisper-base") 
```

### ⚡ Performance Monitoring

Track operation performance with threshold warnings:

```python
log_performance("STT Transcription", 2.5, threshold=2.0)  # Warns if over threshold
```

### 🎤 Audio Event Tracking

Monitor audio capture and processing:

```python
log_audio_event("Recording started", {"device": "default", "sample_rate": 16000})
log_stt_event("Transcription completed", text="Hello world", confidence=0.95)
```

### 📊 Operation Tracking

Track the lifecycle of operations:

```python
log_operation_start("Audio Processing", samples=16000)
# ... do work ...
log_operation_success("Audio Processing", duration=1.2)
```

## Console Output Examples

The system provides colorized, emoji-enhanced console output:

```
2026-02-10 09:23:40.132 | INFO     | stt_service.service:start:85 | 🚀 Starting STT Service
2026-02-10 09:23:40.635 | ERROR    | stt_service.core.audio:init:43 | 🚨 MALFUNCTION: Microphone not found
2026-02-10 09:23:40.911 | WARNING  | stt_service.core.engine:transcribe:95 | ⏱️ Performance warning: STT took 2.30s
2026-02-10 09:23:40.912 | SUCCESS  | stt_service.service:process:120 | ✅ Transcription successful: "Hello world"
```

## Testing the System

Run the logging test script to see all features:

```bash
uv run python scripts/test_logging.py
```

This demonstrates:
- Basic logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Malfunction detection scenarios
- Performance monitoring
- Audio and STT event logging
- Configuration change tracking
- Error handling with full context

## Production Usage

### Quick Malfunction Debugging

When issues occur, check the logs for malfunction indicators:

```bash
# Find recent malfunctions
grep "MALFUNCTION DETECTED" logs/stt_service.log | tail -10

# Check performance warnings  
grep "Performance warning" logs/stt_service.log

# Review recent errors
tail -20 logs/stt_service_errors.log
```

### Common Malfunction Patterns

The system automatically detects and logs:

- **Audio Issues**: Device not found, buffer overflow, no input detected
- **STT Engine Issues**: Model loading failures, transcription timeouts
- **Input Issues**: Hotkey conflicts, permission problems  
- **Output Issues**: Text input blocked, clipboard access denied
- **Performance Issues**: Processing taking too long, memory issues

### Log Rotation

Logs automatically rotate to prevent disk space issues:
- **Time-based**: Weekly rotation with 4 weeks retention
- **Size-based**: 10MB rotation with 10 file retention  
- **Compression**: Old logs are ZIP compressed

## Integration

The logging system is automatically initialized when importing any STT service module. 

For manual setup:

```python
from stt_service.core.logger import setup_logging, get_logger

setup_logging()  # Initialize logging system
logger = get_logger(__name__)  # Get contextual logger

logger.info("Your message here")
```

## Benefits

✅ **Quick Debugging**: Malfunction detection points directly to issues  
✅ **Performance Insights**: Identify bottlenecks and optimization opportunities  
✅ **Production Ready**: Automatic rotation prevents disk space problems  
✅ **Rich Context**: Structured logging with metadata for analysis  
✅ **Visual Clarity**: Emojis and colors make console output easy to scan