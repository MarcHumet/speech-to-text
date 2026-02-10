"""Tests for audio capture module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from stt_service.core.audio_capture import AudioCapture


class TestAudioCapture(unittest.TestCase):
    """Test cases for AudioCapture class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'input_device': 'default',
            'sample_rate': 16000,
            'chunk_size': 1024,
            'channels': 1
        }

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_audio_capture_initialization(self, mock_pyaudio):
        """Test AudioCapture initialization."""
        mock_audio = Mock()
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        capture = AudioCapture(self.config)
        
        self.assertEqual(capture.sample_rate, 16000)
        self.assertEqual(capture.chunk_size, 1024)
        self.assertEqual(capture.channels, 1)
        mock_pyaudio.PyAudio.assert_called_once()

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_start_recording(self, mock_pyaudio):
        """Test starting audio recording."""
        mock_audio = Mock()
        mock_stream = Mock()
        mock_pyaudio.PyAudio.return_value = mock_audio
        mock_audio.open.return_value = mock_stream
        
        capture = AudioCapture(self.config)
        capture.start_recording()
        
        self.assertTrue(capture.is_recording)
        mock_audio.open.assert_called_once()

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_stop_recording(self, mock_pyaudio):
        """Test stopping audio recording."""
        mock_audio = Mock()
        mock_stream = Mock()
        mock_pyaudio.PyAudio.return_value = mock_audio
        mock_audio.open.return_value = mock_stream
        
        capture = AudioCapture(self.config)
        capture.start_recording()
        audio_data = capture.stop_recording()
        
        self.assertFalse(capture.is_recording)
        self.assertIsInstance(audio_data, bytes)
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_get_audio_data(self, mock_pyaudio):
        """Test getting audio data during recording."""
        mock_audio = Mock()
        mock_stream = Mock()
        mock_stream.read.return_value = b'test_audio_data'
        mock_pyaudio.PyAudio.return_value = mock_audio
        mock_audio.open.return_value = mock_stream
        
        capture = AudioCapture(self.config)
        capture.start_recording()
        
        # Mock the stream to return some data
        data = capture._read_audio_chunk()
        
        self.assertEqual(data, b'test_audio_data')
        mock_stream.read.assert_called_with(1024)

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_audio_capture_context_manager(self, mock_pyaudio):
        """Test AudioCapture as context manager."""
        mock_audio = Mock()
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        with AudioCapture(self.config) as capture:
            self.assertIsNotNone(capture)
        
        mock_audio.terminate.assert_called_once()

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_device_listing(self, mock_pyaudio):
        """Test listing available audio devices."""
        mock_audio = Mock()
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info_by_index.side_effect = [
            {'name': 'Device 1', 'maxInputChannels': 2, 'defaultSampleRate': 44100},
            {'name': 'Device 2', 'maxInputChannels': 1, 'defaultSampleRate': 16000}
        ]
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        devices = AudioCapture.list_input_devices()
        
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]['name'], 'Device 1')
        self.assertEqual(devices[1]['name'], 'Device 2')

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_sample_rate_validation(self, mock_pyaudio):
        """Test sample rate validation."""
        mock_audio = Mock()
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        # Test valid sample rates
        for rate in [8000, 16000, 22050, 44100]:
            config = self.config.copy()
            config['sample_rate'] = rate
            capture = AudioCapture(config)
            self.assertEqual(capture.sample_rate, rate)

    @patch('stt_service.core.audio_capture.pyaudio')
    def test_error_handling(self, mock_pyaudio):
        """Test error handling in audio capture."""
        mock_audio = Mock()
        mock_audio.open.side_effect = Exception("Device not found")
        mock_pyaudio.PyAudio.return_value = mock_audio
        
        capture = AudioCapture(self.config)
        
        with self.assertRaises(Exception):
            capture.start_recording()


if __name__ == '__main__':
    unittest.main()