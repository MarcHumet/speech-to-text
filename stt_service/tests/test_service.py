"""Tests for the main STT service."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import threading
import time

from stt_service.service import STTService


class TestSTTService(unittest.TestCase):
    """Test cases for STTService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_dict = {
            'language': 'en',
            'engine': 'dummy',
            'input_device': 'default',
            'output_target': 'active_window',
            'hotkey': {
                'keys': ['ctrl', 'space'],
                'hold_duration': 0.1,
                'trigger_on_release': True
            }
        }

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_initialization(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test STTService initialization."""
        # Setup mocks
        mock_config.return_value = self.config_dict
        mock_engine.return_value = Mock()
        mock_audio.return_value = Mock()
        mock_hotkey.return_value = Mock()
        mock_output.return_value = Mock()
        
        service = STTService()
        
        self.assertIsNotNone(service.config)
        self.assertIsNotNone(service.engine)
        self.assertIsNotNone(service.audio_capture)
        self.assertIsNotNone(service.input_handler)
        self.assertIsNotNone(service.output_handler)

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_with_config_file(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test STTService initialization with config file."""
        config_file = '/tmp/test_config.yaml'
        
        mock_config.return_value = self.config_dict
        mock_engine.return_value = Mock()
        mock_audio.return_value = Mock()
        mock_hotkey.return_value = Mock()
        mock_output.return_value = Mock()
        
        service = STTService(config_file)
        
        mock_config.assert_called_once_with(config_file)

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_start(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test starting the STT service."""
        # Setup mocks
        mock_config.return_value = self.config_dict
        mock_engine.return_value = Mock()
        mock_audio.return_value = Mock()
        mock_hotkey_instance = Mock()
        mock_hotkey.return_value = mock_hotkey_instance
        mock_output.return_value = Mock()
        
        service = STTService()
        service.start()
        
        self.assertTrue(service.is_running)
        mock_hotkey_instance.start.assert_called_once()

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_stop(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test stopping the STT service."""
        # Setup mocks
        mock_config.return_value = self.config_dict
        mock_engine.return_value = Mock()
        mock_audio.return_value = Mock()
        mock_hotkey_instance = Mock()
        mock_hotkey.return_value = mock_hotkey_instance
        mock_output.return_value = Mock()
        
        service = STTService()
        service.start()
        service.stop()
        
        self.assertFalse(service.is_running)
        mock_hotkey_instance.stop.assert_called_once()

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_transcription_process(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test the transcription process."""
        # Setup mocks
        mock_config.return_value = self.config_dict
        mock_engine_instance = Mock()
        mock_engine_instance.transcribe.return_value = "Hello world"
        mock_engine.return_value = mock_engine_instance
        
        mock_audio_instance = Mock()
        mock_audio_instance.start_recording.return_value = None
        mock_audio_instance.stop_recording.return_value = b'fake_audio_data'
        mock_audio.return_value = mock_audio_instance
        
        mock_hotkey.return_value = Mock()
        mock_output_instance = Mock()
        mock_output.return_value = mock_output_instance
        
        service = STTService()
        
        # Simulate the transcription process
        service._handle_speech_input()
        
        mock_audio_instance.start_recording.assert_called_once()
        mock_audio_instance.stop_recording.assert_called_once()
        mock_engine_instance.transcribe.assert_called_once_with(b'fake_audio_data')
        mock_output_instance.output.assert_called_once_with("Hello world")

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_context_manager(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test STTService as context manager."""
        # Setup mocks
        mock_config.return_value = self.config_dict
        mock_engine.return_value = Mock()
        mock_audio.return_value = Mock()
        mock_hotkey_instance = Mock()
        mock_hotkey.return_value = mock_hotkey_instance
        mock_output.return_value = Mock()
        
        with STTService() as service:
            self.assertIsNotNone(service)
            self.assertTrue(service.is_running)
        
        self.assertFalse(service.is_running)
        mock_hotkey_instance.stop.assert_called_once()

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_error_handling(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test error handling in STT service."""
        # Setup mocks with some failures
        mock_config.return_value = self.config_dict
        mock_engine_instance = Mock()
        mock_engine_instance.transcribe.side_effect = Exception("Transcription failed")
        mock_engine.return_value = mock_engine_instance
        
        mock_audio_instance = Mock()
        mock_audio_instance.stop_recording.return_value = b'fake_audio_data'
        mock_audio.return_value = mock_audio_instance
        
        mock_hotkey.return_value = Mock()
        mock_output.return_value = Mock()
        
        service = STTService()
        
        # Should handle transcription errors gracefully
        try:
            service._handle_speech_input()
        except Exception:
            self.fail("STTService should handle transcription errors gracefully")

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_configuration_updates(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test configuration updates."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.language = 'en'
        mock_config_instance.engine = 'dummy'
        mock_config_instance.update = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_engine.return_value = Mock()
        mock_audio.return_value = Mock()
        mock_hotkey.return_value = Mock()
        mock_output.return_value = Mock()
        
        service = STTService()
        
        # Test config updates
        new_config = {'language': 'es', 'engine': 'whisper'}
        service.update_config(new_config)
        
        mock_config_instance.update.assert_called_once_with(new_config)

    @patch('stt_service.service.Config')
    @patch('stt_service.service.create_engine')
    @patch('stt_service.service.AudioCapture')
    @patch('stt_service.service.create_hotkey_handler')
    @patch('stt_service.service.create_output_handler')
    def test_stt_service_status_reporting(self, mock_output, mock_hotkey, mock_audio, mock_engine, mock_config):
        """Test service status reporting."""
        # Setup mocks
        mock_config.return_value = self.config_dict
        mock_engine_instance = Mock()
        mock_engine_instance.is_available.return_value = True
        mock_engine.return_value = mock_engine_instance
        
        mock_audio_instance = Mock()
        mock_audio.return_value = mock_audio_instance
        
        mock_hotkey_instance = Mock()
        mock_hotkey.return_value = mock_hotkey_instance
        
        mock_output_instance = Mock()
        mock_output_instance.is_available.return_value = True
        mock_output.return_value = mock_output_instance
        
        service = STTService()
        status = service.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('is_running', status)
        self.assertIn('engine_available', status)
        self.assertIn('output_available', status)


if __name__ == '__main__':
    unittest.main()