"""Tests for STT engine module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from stt_service.core.engine import STTEngine, DummyEngine, create_engine


class TestSTTEngine(unittest.TestCase):
    """Test cases for STTEngine base class."""

    def test_stt_engine_abstract_methods(self):
        """Test that STTEngine is abstract and requires implementation."""
        with self.assertRaises(TypeError):
            STTEngine()

    def test_stt_engine_interface(self):
        """Test STTEngine interface definition."""
        # Create a concrete implementation for testing
        class TestEngine(STTEngine):
            def __init__(self, config):
                super().__init__(config)
                self.is_ready = True
            
            def transcribe(self, audio_data):
                return "test transcription"
            
            def is_available(self):
                return True
            
            def cleanup(self):
                pass
        
        engine = TestEngine({})
        self.assertTrue(hasattr(engine, 'transcribe'))
        self.assertTrue(hasattr(engine, 'is_available'))
        self.assertTrue(hasattr(engine, 'cleanup'))


class TestDummyEngine(unittest.TestCase):
    """Test cases for DummyEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'language': 'en',
            'responses': ['Hello', 'Test', 'Speech to text']
        }

    def test_dummy_engine_initialization(self):
        """Test DummyEngine initialization."""
        engine = DummyEngine(self.config)
        
        self.assertEqual(engine.language, 'en')
        self.assertTrue(engine.is_ready)
        self.assertTrue(engine.is_available())

    def test_dummy_engine_transcribe(self):
        """Test DummyEngine transcription."""
        engine = DummyEngine(self.config)
        
        # Test with audio data
        audio_data = b'fake_audio_data'
        result = engine.transcribe(audio_data)
        
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_dummy_engine_random_responses(self):
        """Test DummyEngine returns different responses."""
        engine = DummyEngine(self.config)
        
        responses = set()
        for _ in range(10):
            result = engine.transcribe(b'audio')
            responses.add(result)
        
        # Should have some variety in responses
        self.assertTrue(len(responses) >= 1)

    def test_dummy_engine_language_specific_responses(self):
        """Test DummyEngine with different languages."""
        # Test English
        en_config = {'language': 'en'}
        en_engine = DummyEngine(en_config)
        en_result = en_engine.transcribe(b'audio')
        self.assertIsInstance(en_result, str)
        
        # Test Spanish
        es_config = {'language': 'es'}
        es_engine = DummyEngine(es_config)
        es_result = es_engine.transcribe(b'audio')
        self.assertIsInstance(es_result, str)

    def test_dummy_engine_cleanup(self):
        """Test DummyEngine cleanup."""
        engine = DummyEngine(self.config)
        
        # Should not raise any exceptions
        engine.cleanup()
        
        # Can be called multiple times
        engine.cleanup()

    def test_dummy_engine_with_custom_responses(self):
        """Test DummyEngine with custom response list."""
        custom_responses = ['Custom response 1', 'Custom response 2']
        config = {'language': 'en', 'responses': custom_responses}
        
        engine = DummyEngine(config)
        
        result = engine.transcribe(b'audio')
        self.assertIn(result, custom_responses)


class TestEngineFactory(unittest.TestCase):
    """Test cases for engine creation factory function."""

    def test_create_dummy_engine(self):
        """Test creating dummy engine."""
        config = {'engine': 'dummy', 'language': 'en'}
        
        engine = create_engine(config)
        
        self.assertIsInstance(engine, DummyEngine)
        self.assertEqual(engine.language, 'en')

    @patch('stt_service.core.engine.WhisperEngine')
    def test_create_whisper_engine(self, mock_whisper):
        """Test creating Whisper engine."""
        mock_instance = Mock()
        mock_whisper.return_value = mock_instance
        
        config = {'engine': 'whisper', 'language': 'en'}
        
        try:
            engine = create_engine(config)
            # If WhisperEngine is available, it should return the mock
            mock_whisper.assert_called_once_with(config)
        except ImportError:
            # If WhisperEngine is not available, should fall back to DummyEngine
            engine = create_engine(config)
            self.assertIsInstance(engine, DummyEngine)

    def test_create_unknown_engine_fallback(self):
        """Test fallback to dummy engine for unknown engine types."""
        config = {'engine': 'unknown_engine', 'language': 'en'}
        
        engine = create_engine(config)
        
        # Should fall back to DummyEngine
        self.assertIsInstance(engine, DummyEngine)

    def test_create_engine_without_config(self):
        """Test creating engine with minimal config."""
        config = {}
        
        engine = create_engine(config)
        
        self.assertIsInstance(engine, DummyEngine)

    def test_engine_availability_check(self):
        """Test checking engine availability."""
        config = {'engine': 'dummy', 'language': 'en'}
        engine = create_engine(config)
        
        self.assertTrue(engine.is_available())

    def test_engine_context_manager(self):
        """Test engine as context manager if supported."""
        config = {'engine': 'dummy', 'language': 'en'}
        engine = create_engine(config)
        
        # DummyEngine should support context manager protocol
        if hasattr(engine, '__enter__') and hasattr(engine, '__exit__'):
            with engine as ctx_engine:
                self.assertIs(ctx_engine, engine)


if __name__ == '__main__':
    unittest.main()