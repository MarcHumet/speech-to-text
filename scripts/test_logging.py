#!/usr/bin/env python3
"""
Logging test script for STT Service.

This script tests the loguru logging functionality and demonstrates
how to detect malfunctions and track operations.
"""

import sys
import os
import time

# Add parent directory to path to import stt_service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stt_service.core.logger import (
    setup_logging, get_logger, 
    log_operation_start, log_operation_success, log_operation_error,
    log_malfunction, log_performance, log_audio_event, log_stt_event,
    log_config_change
)


def test_logging_system():
    """Test the comprehensive logging system."""
    print("🧪 Testing STT Service Logging System")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Test basic logging levels
    print("\n1. Testing basic log levels...")
    logger.debug("🔍 Debug message - detailed information")
    logger.info("ℹ️ Info message - general information")
    logger.warning("⚠️ Warning message - something unexpected")
    logger.error("🚨 Error message - something went wrong")
    logger.success("✅ Success message - operation completed")
    
    # Test operation logging
    print("\n2. Testing operation logging...")
    log_operation_start("Test Operation", component="TestModule", version="1.0")
    time.sleep(0.5)  # Simulate work
    log_operation_success("Test Operation", duration=0.5, component="TestModule")
    
    # Test malfunction logging
    print("\n3. Testing malfunction detection...")
    log_malfunction("AudioCapture", "Microphone not found", "ERROR", device_id="default")
    log_malfunction("STTEngine", "Model loading timeout", "CRITICAL", model="whisper-base")
    log_malfunction("NetworkManager", "Connection unstable", "WARNING", retry_count=3)
    
    # Test performance logging
    print("\n4. Testing performance tracking...")
    log_performance("Audio Recording", 2.3, threshold=2.0, samples=36800)
    log_performance("STT Processing", 1.8, threshold=3.0, text_length=45)
    log_performance("Text Output", 0.1, threshold=0.5)
    
    # Test audio events
    print("\n5. Testing audio event logging...")
    log_audio_event("Recording started", {
        "device": "default", 
        "sample_rate": 16000,
        "max_duration": 30
    })
    log_audio_event("Recording completed", {
        "duration": "3.2s",
        "samples": 51200,
        "quality": "good"
    })
    
    # Test STT events
    print("\n6. Testing STT event logging...")
    log_stt_event("Transcription request", confidence=0.92, language="en")
    log_stt_event("Transcription completed", 
                  text="Hello, this is a test transcription", 
                  confidence=0.95,
                  processing_time=1.2)
    
    # Test configuration changes
    print("\n7. Testing configuration change logging...")
    log_config_change("service.language", "en", "es", user="admin")
    log_config_change("audio.sample_rate", 16000, 22050, reason="quality_improvement")
    
    # Test error scenarios
    print("\n8. Testing error logging...")
    try:
        # Simulate an error
        raise ValueError("This is a test error for logging demonstration")
    except Exception as e:
        log_operation_error("Test Error Handling", e, 
                           context="demonstration", 
                           user_action="test_logging")
    
    # Test different log contexts
    print("\n9. Testing contextual logging...")
    component_logger = get_logger("STTService.AudioCapture")
    component_logger.info("Component-specific logging message")
    
    engine_logger = get_logger("STTService.WhisperEngine")
    engine_logger.info("STT Engine status update", extra={
        "model": "whisper-base",
        "language": "en",
        "ready": True
    })
    
    print("\n✅ Logging test completed!")
    print("\n📁 Check the following for log files:")
    print("   - logs/stt_service.log (main log with rotation)")
    print("   - logs/stt_service_size.log (size-based rotation)")
    print("   - logs/stt_service_errors.log (warnings and errors only)")
    
    # Test log rotation information
    logger.info("🔄 Log rotation configured:")
    logger.info("   - Time rotation: 1 week")
    logger.info("   - Size rotation: 10 MB")
    logger.info("   - Retention: 4 weeks")
    logger.info("   - Compression: ZIP")


def demonstrate_malfunction_detection():
    """Demonstrate how logging helps detect malfunctions."""
    print("\n" + "=" * 60)
    print("🔍 MALFUNCTION DETECTION DEMONSTRATION")
    print("=" * 60)
    
    logger = get_logger("MalfunctionDemo")
    
    # Simulate various malfunction scenarios
    scenarios = [
        {
            "component": "AudioCapture",
            "issue": "Device not found: 'professional-mic-1'",
            "severity": "ERROR",
            "context": {"requested_device": "professional-mic-1", "available_devices": ["default", "built-in"]}
        },
        {
            "component": "STTEngine",
            "issue": "Model loading failed - insufficient memory",
            "severity": "CRITICAL",
            "context": {"required_memory": "2GB", "available_memory": "1.2GB", "model": "whisper-large"}
        },
        {
            "component": "HotkeyManager",
            "issue": "Hotkey registration conflict with system",
            "severity": "WARNING",
            "context": {"requested_key": "ctrl+shift+space", "conflicting_app": "screenshot-tool"}
        },
        {
            "component": "OutputHandler",
            "issue": "Text input blocked by security policy",
            "severity": "ERROR", 
            "context": {"target_app": "secure-terminal", "policy": "input_restricted"}
        },
        {
            "component": "NetworkManager",
            "issue": "High latency detected in STT service",
            "severity": "WARNING",
            "context": {"latency": "250ms", "threshold": "100ms", "endpoint": "stt-api.example.com"}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Simulating malfunction scenario...")
        log_malfunction(
            scenario["component"],
            scenario["issue"], 
            scenario["severity"],
            **scenario["context"]
        )
        time.sleep(0.2)
    
    print("\n🎯 These malfunctions are now logged with full context for easy debugging!")


if __name__ == "__main__":
    test_logging_system()
    demonstrate_malfunction_detection()
    
    print(f"\n🎉 All tests completed! Check the logs directory for detailed output.")
    print("💡 In production, these logs will help you:")
    print("   - Quickly identify performance bottlenecks")
    print("   - Track down hardware/software compatibility issues")  
    print("   - Monitor transcription accuracy and quality")
    print("   - Debug hotkey and input handling problems")
    print("   - Analyze usage patterns and optimize accordingly")