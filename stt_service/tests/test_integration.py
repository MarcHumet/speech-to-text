"""Integration tests for the complete STT service workflow."""

import unittest
import tempfile
import os
import time
from unittest.mock import patch

from stt_service.service import STTService
from stt_service.core.config import Config


class TestSTTServiceIntegration(unittest.TestCase):
    """Integration tests for STT service components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yaml')
        
        # Create a test config file
        test_config = """
language: en
engine: dummy
input_device: default
output_target: active_window
hotkey:
  keys: ["ctrl", "space"]
  hold_duration: 0.1
  trigger_on_release: true
"""
        with open(self.config_file, 'w') as f:
            f.write(test_config)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)

    def test_service_initialization_with_config_file(self):
        """Test complete service initialization with config file."""
        service = STTService(self.config_file)
        
        self.assertIsNotNone(service.config)
        self.assertIsNotNone(service.engine)
        self.assertIsNotNone(service.audio_capture)
        self.assertIsNotNone(service.input_handler)
        self.assertIsNotNone(service.output_handler)
        
        # Test that config was loaded correctly
        self.assertEqual(service.config.language, 'en')
        self.assertEqual(service.config.engine, 'dummy')

    def test_service_lifecycle(self):
        """Test complete service lifecycle."""
        service = STTService(self.config_file)
        
        # Test initial state
        self.assertFalse(service.is_running)
        
        # Test starting
        service.start()
        self.assertTrue(service.is_running)
        
        # Test status reporting
        status = service.get_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(status['is_running'])
        
        # Test stopping
        service.stop()
        self.assertFalse(service.is_running)

    def test_service_context_manager(self):
        """Test service as context manager."""
        with STTService(self.config_file) as service:
            self.assertTrue(service.is_running)
            
            status = service.get_status()
            self.assertTrue(status['is_running'])
        
        # Should be stopped after context exit
        self.assertFalse(service.is_running)

    @patch('stt_service.output.keyboard.pyautogui')
    @patch('stt_service.core.audio_capture.pyaudio')
    def test_simulated_speech_workflow(self, mock_pyaudio, mock_pyautogui):
        """Test simulated speech-to-text workflow."""
        # Setup audio mocks
        mock_audio = Mock()
        mock_stream = Mock()
        mock_stream.read.return_value = b'fake_audio_data'
        mock_audio.open.return_value = mock_stream
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        service = STTService(self.config_file)
        
        # Simulate the speech input process
        service._handle_speech_input()
        
        # Verify audio was captured
        mock_audio.open.assert_called()
        
        # Verify output was attempted (with dummy engine)
        mock_pyautogui.typewrite.assert_called()

    def test_config_validation_integration(self):
        """Test configuration validation in full context."""
        # Test with invalid config
        invalid_config = """
language: invalid_lang
engine: dummy
"""
        invalid_config_file = os.path.join(self.temp_dir, 'invalid.yaml')
        with open(invalid_config_file, 'w') as f:
            f.write(invalid_config)
        
        # Should handle invalid config gracefully
        service = STTService(invalid_config_file)
        self.assertIsNotNone(service.config)
        
        # Clean up
        os.remove(invalid_config_file)

    def test_engine_fallback_integration(self):
        """Test engine fallback behavior."""
        # Config with non-existent engine should fall back to dummy
        fallback_config = """
language: en
engine: non_existent_engine
"""
        fallback_config_file = os.path.join(self.temp_dir, 'fallback.yaml')
        with open(fallback_config_file, 'w') as f:
            f.write(fallback_config)
        
        service = STTService(fallback_config_file)
        
        # Should have created service with fallback engine
        self.assertIsNotNone(service.engine)
        self.assertTrue(service.engine.is_available())
        
        # Clean up
        os.remove(fallback_config_file)

    def test_multiple_service_instances(self):
        """Test multiple service instances don't conflict."""
        service1 = STTService(self.config_file)
        service2 = STTService(self.config_file)
        
        # Both should initialize successfully
        self.assertIsNotNone(service1.engine)
        self.assertIsNotNone(service2.engine)
        
        # Both should be able to start (though hotkeys might conflict in real usage)
        service1.start()
        service2.start()
        
        self.assertTrue(service1.is_running)
        self.assertTrue(service2.is_running)
        
        service1.stop()
        service2.stop()


if __name__ == '__main__':
    # Import Mock here to avoid issues if unittest.mock is not available
    from unittest.mock import Mock
    unittest.main()