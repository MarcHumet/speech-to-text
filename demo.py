#!/usr/bin/env python3
"""
Demo script to test the STT service components.

This script demonstrates the basic functionality without requiring
all dependencies to be installed.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that core modules can be imported."""
    print("\n" + "="*60)
    print("Testing Module Imports")
    print("="*60)
    
    try:
        from stt_service.core.config import Config
        print("✓ Config module imported")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from stt_service.core.audio_capture import AudioCapture
        print("✓ AudioCapture module imported")
    except Exception as e:
        print(f"✗ AudioCapture import failed: {e}")
        return False
    
    try:
        from stt_service.core.engine import STTEngine, DummyEngine, create_engine
        print("✓ Engine module imported")
    except Exception as e:
        print(f"✗ Engine import failed: {e}")
        return False
    
    try:
        from stt_service.input.hotkey import create_hotkey_handler
        print("✓ Input module imported")
    except Exception as e:
        print(f"✗ Input import failed: {e}")
        return False
    
    try:
        from stt_service.output.keyboard import create_output_handler
        print("✓ Output module imported")
    except Exception as e:
        print(f"✗ Output import failed: {e}")
        return False
    
    try:
        from stt_service.service import STTService
        print("✓ Service module imported")
    except Exception as e:
        print(f"✗ Service import failed: {e}")
        return False
    
    return True


def test_config():
    """Test configuration system."""
    print("\n" + "="*60)
    print("Testing Configuration")
    print("="*60)
    
    from stt_service.core.config import Config
    
    # Create default config
    config = Config()
    print(f"✓ Default config created")
    
    # Test get
    lang = config.get('service.language')
    print(f"✓ Language: {lang}")
    
    # Test set
    config.set('service.language', 'es')
    new_lang = config.get('service.language')
    assert new_lang == 'es', "Config set failed"
    print(f"✓ Language changed to: {new_lang}")
    
    # Test nested get
    sample_rate = config.get('audio.sample_rate')
    print(f"✓ Sample rate: {sample_rate}")
    
    return True


def test_engine():
    """Test STT engine."""
    print("\n" + "="*60)
    print("Testing STT Engine")
    print("="*60)
    
    from stt_service.core.engine import create_engine
    import numpy as np
    
    # Create dummy engine
    engine = create_engine('dummy')
    print("✓ Dummy engine created")
    
    # Load model
    engine.load_model('dummy-model')
    print("✓ Model loaded")
    
    # Check ready
    assert engine.is_ready(), "Engine not ready"
    print("✓ Engine is ready")
    
    # Create dummy audio
    audio = np.random.randn(16000).astype(np.float32)
    print(f"✓ Created test audio: {len(audio)} samples")
    
    # Transcribe
    text = engine.transcribe(audio, language='en')
    print(f"✓ Transcription: '{text}'")
    
    return True


def test_service_creation():
    """Test service creation."""
    print("\n" + "="*60)
    print("Testing Service Creation")
    print("="*60)
    
    from stt_service.core.config import Config
    from stt_service.service import STTService
    
    # Create config with dummy model
    config = Config()
    config.set('model.type', 'dummy')
    print("✓ Config created")
    
    # Create service
    service = STTService(config)
    print("✓ Service created")
    
    # Check components
    assert service.audio_capture is not None, "Audio capture not initialized"
    print("✓ Audio capture initialized")
    
    assert service.engine is not None, "Engine not initialized"
    print("✓ Engine initialized")
    
    assert service.input_handler is not None, "Input handler not initialized"
    print("✓ Input handler initialized")
    
    assert service.output_handler is not None, "Output handler not initialized"
    print("✓ Output handler initialized")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("STT Service Component Demo")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("STT Engine", test_engine),
        ("Service Creation", test_service_creation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("All tests passed! ✓")
        print("\nThe service architecture is working correctly.")
        print("Next steps:")
        print("  1. Install optional dependencies: pip install -r requirements.txt")
        print("  2. Run component tests: python cli.py test")
        print("  3. Try the service: python cli.py run")
    else:
        print("Some tests failed! ✗")
        print("\nPlease check the error messages above.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
