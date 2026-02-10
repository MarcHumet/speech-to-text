"""Tests for hotkey input module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time

from stt_service.input.hotkey import HotkeyHandler, create_hotkey_handler


class TestHotkeyHandler(unittest.TestCase):
    """Test cases for HotkeyHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'keys': ['ctrl', 'space'],
            'hold_duration': 0.1,
            'trigger_on_release': True
        }
        self.callback = Mock()

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_handler_initialization(self, mock_keyboard):
        """Test HotkeyHandler initialization."""
        handler = HotkeyHandler(self.config, self.callback)
        
        self.assertEqual(handler.keys, ['ctrl', 'space'])
        self.assertEqual(handler.hold_duration, 0.1)
        self.assertEqual(handler.trigger_on_release, True)
        self.assertEqual(handler.callback, self.callback)

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_registration(self, mock_keyboard):
        """Test hotkey registration with keyboard library."""
        handler = HotkeyHandler(self.config, self.callback)
        handler.start()
        
        mock_keyboard.add_hotkey.assert_called()
        call_args = mock_keyboard.add_hotkey.call_args
        self.assertIn('ctrl+space', str(call_args))

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_callback_execution(self, mock_keyboard):
        """Test hotkey callback execution."""
        handler = HotkeyHandler(self.config, self.callback)
        
        # Simulate hotkey press
        handler._on_hotkey_press()
        
        # Should not call callback immediately for hold-type hotkeys
        self.callback.assert_not_called()

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_hold_duration(self, mock_keyboard):
        """Test hotkey hold duration functionality."""
        handler = HotkeyHandler(self.config, self.callback)
        
        # Start press
        handler._on_hotkey_press()
        
        # Wait less than hold duration
        time.sleep(0.05)
        
        # Release
        handler._on_hotkey_release()
        
        # Should not trigger callback (held for less than required duration)
        self.callback.assert_not_called()

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_successful_hold(self, mock_keyboard):
        """Test successful hotkey hold and release."""
        config = self.config.copy()
        config['hold_duration'] = 0.05  # Very short for testing
        
        handler = HotkeyHandler(config, self.callback)
        
        # Start press
        handler._on_hotkey_press()
        
        # Wait longer than hold duration
        time.sleep(0.1)
        
        # Release
        handler._on_hotkey_release()
        
        # Should trigger callback
        self.callback.assert_called_once()

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_stop(self, mock_keyboard):
        """Test stopping hotkey handler."""
        handler = HotkeyHandler(self.config, self.callback)
        handler.start()
        handler.stop()
        
        mock_keyboard.remove_hotkey.assert_called()

    @patch('stt_service.input.hotkey.keyboard')
    def test_hotkey_context_manager(self, mock_keyboard):
        """Test HotkeyHandler as context manager."""
        with HotkeyHandler(self.config, self.callback) as handler:
            self.assertIsNotNone(handler)
            mock_keyboard.add_hotkey.assert_called()
        
        mock_keyboard.remove_hotkey.assert_called()

    @patch('stt_service.input.hotkey.keyboard')
    def test_different_key_combinations(self, mock_keyboard):
        """Test different hotkey combinations."""
        test_cases = [
            ['ctrl', 'alt', 'space'],
            ['shift', 'f1'],
            ['ctrl', 'shift', 'r'],
            ['alt', 'tab']
        ]
        
        for keys in test_cases:
            config = self.config.copy()
            config['keys'] = keys
            
            handler = HotkeyHandler(config, self.callback)
            handler.start()
            
            mock_keyboard.add_hotkey.assert_called()
            handler.stop()

    @patch('stt_service.input.hotkey.keyboard')
    def test_immediate_trigger_mode(self, mock_keyboard):
        """Test immediate trigger mode (no hold required)."""
        config = {
            'keys': ['f1'],
            'trigger_on_release': False,
            'hold_duration': 0
        }
        
        handler = HotkeyHandler(config, self.callback)
        
        # Simulate press
        handler._on_hotkey_press()
        
        # Should trigger callback immediately
        self.callback.assert_called_once()

    @patch('stt_service.input.hotkey.keyboard')
    def test_error_handling(self, mock_keyboard):
        """Test error handling in hotkey registration."""
        mock_keyboard.add_hotkey.side_effect = Exception("Hotkey registration failed")
        
        handler = HotkeyHandler(self.config, self.callback)
        
        # Should handle the exception gracefully
        with self.assertRaises(Exception):
            handler.start()


class TestHotkeyFactory(unittest.TestCase):
    """Test cases for hotkey handler factory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'hotkey': {
                'keys': ['ctrl', 'space'],
                'hold_duration': 0.1,
                'trigger_on_release': True
            }
        }
        self.callback = Mock()

    @patch('stt_service.input.hotkey.keyboard')
    def test_create_hotkey_handler(self, mock_keyboard):
        """Test creating hotkey handler with factory function."""
        handler = create_hotkey_handler(self.config, self.callback)
        
        self.assertIsInstance(handler, HotkeyHandler)
        self.assertEqual(handler.keys, ['ctrl', 'space'])

    @patch('stt_service.input.hotkey.keyboard')
    def test_create_hotkey_handler_with_defaults(self, mock_keyboard):
        """Test creating hotkey handler with default configuration."""
        minimal_config = {}
        
        handler = create_hotkey_handler(minimal_config, self.callback)
        
        self.assertIsInstance(handler, HotkeyHandler)
        # Should use default keys
        self.assertIsNotNone(handler.keys)

    @patch('stt_service.input.hotkey.keyboard')
    def test_create_hotkey_handler_invalid_config(self, mock_keyboard):
        """Test creating hotkey handler with invalid configuration."""
        invalid_config = {
            'hotkey': {
                'keys': [],  # Empty keys list
                'hold_duration': -1  # Invalid duration
            }
        }
        
        # Should handle invalid config gracefully
        handler = create_hotkey_handler(invalid_config, self.callback)
        self.assertIsInstance(handler, HotkeyHandler)


if __name__ == '__main__':
    unittest.main()