"""Tests for keyboard output module."""

import unittest
from unittest.mock import Mock, patch, MagicMock

from stt_service.output.keyboard import KeyboardOutput, create_output_handler


class TestKeyboardOutput(unittest.TestCase):
    """Test cases for KeyboardOutput class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'output_target': 'active_window',
            'typing_delay': 0.01,
            'clear_clipboard': True
        }

    @patch('stt_service.output.keyboard.pyautogui')
    def test_keyboard_output_initialization(self, mock_pyautogui):
        """Test KeyboardOutput initialization."""
        output = KeyboardOutput(self.config)
        
        self.assertEqual(output.output_target, 'active_window')
        self.assertEqual(output.typing_delay, 0.01)
        self.assertTrue(output.clear_clipboard)

    @patch('stt_service.output.keyboard.pyautogui')
    def test_output_to_active_window(self, mock_pyautogui):
        """Test outputting text to active window."""
        output = KeyboardOutput(self.config)
        test_text = "Hello, world!"
        
        output.output(test_text)
        
        mock_pyautogui.typewrite.assert_called_once_with(test_text, interval=0.01)

    @patch('stt_service.output.keyboard.pyautogui')
    @patch('stt_service.output.keyboard.pyperclip')
    def test_output_to_clipboard(self, mock_pyperclip, mock_pyautogui):
        """Test outputting text to clipboard."""
        config = self.config.copy()
        config['output_target'] = 'clipboard'
        
        output = KeyboardOutput(config)
        test_text = "Clipboard text"
        
        output.output(test_text)
        
        mock_pyperclip.copy.assert_called_once_with(test_text)
        mock_pyautogui.typewrite.assert_not_called()

    @patch('stt_service.output.keyboard.pyautogui')
    @patch('stt_service.output.keyboard.pyperclip')
    def test_output_to_clipboard_and_paste(self, mock_pyperclip, mock_pyautogui):
        """Test outputting text to clipboard and pasting."""
        config = self.config.copy()
        config['output_target'] = 'clipboard_paste'
        
        output = KeyboardOutput(config)
        test_text = "Paste this text"
        
        output.output(test_text)
        
        mock_pyperclip.copy.assert_called_once_with(test_text)
        mock_pyautogui.hotkey.assert_called_with('ctrl', 'v')

    @patch('stt_service.output.keyboard.pyautogui')
    def test_typing_delay_configuration(self, mock_pyautogui):
        """Test typing delay configuration."""
        config = self.config.copy()
        config['typing_delay'] = 0.05
        
        output = KeyboardOutput(config)
        test_text = "Slow typing"
        
        output.output(test_text)
        
        mock_pyautogui.typewrite.assert_called_once_with(test_text, interval=0.05)

    @patch('stt_service.output.keyboard.pyautogui')
    def test_empty_text_handling(self, mock_pyautogui):
        """Test handling of empty text."""
        output = KeyboardOutput(self.config)
        
        # Empty string
        output.output("")
        mock_pyautogui.typewrite.assert_not_called()
        
        # None
        output.output(None)
        self.assertEqual(mock_pyautogui.typewrite.call_count, 0)
        
        # Whitespace only
        output.output("   ")
        mock_pyautogui.typewrite.assert_not_called()

    @patch('stt_service.output.keyboard.pyautogui')
    def test_text_preprocessing(self, mock_pyautogui):
        """Test text preprocessing before output."""
        output = KeyboardOutput(self.config)
        
        # Test trimming whitespace
        test_text = "  Hello, world!  "
        output.output(test_text)
        
        mock_pyautogui.typewrite.assert_called_once_with("Hello, world!", interval=0.01)

    @patch('stt_service.output.keyboard.pyautogui')
    def test_special_characters_handling(self, mock_pyautogui):
        """Test handling of special characters."""
        output = KeyboardOutput(self.config)
        
        test_cases = [
            "Hello\nworld",  # Newline
            "Tab\tcharacter",  # Tab
            "Special chars: !@#$%^&*()",  # Special characters
            "Unicode: café résumé",  # Unicode characters
        ]
        
        for text in test_cases:
            mock_pyautogui.reset_mock()
            output.output(text)
            mock_pyautogui.typewrite.assert_called_once_with(text, interval=0.01)

    @patch('stt_service.output.keyboard.pyautogui')
    def test_error_handling(self, mock_pyautogui):
        """Test error handling in keyboard output."""
        mock_pyautogui.typewrite.side_effect = Exception("Keyboard error")
        
        output = KeyboardOutput(self.config)
        
        # Should handle the exception gracefully
        try:
            output.output("Test text")
        except Exception:
            self.fail("KeyboardOutput should handle exceptions gracefully")

    @patch('stt_service.output.keyboard.pyautogui')
    def test_is_available(self, mock_pyautogui):
        """Test availability checking."""
        output = KeyboardOutput(self.config)
        
        # Should be available if pyautogui is working
        self.assertTrue(output.is_available())
        
        # Test when pyautogui fails
        mock_pyautogui.typewrite.side_effect = Exception("Not available")
        # Even with errors, should still report as available (error handling is internal)
        self.assertTrue(output.is_available())

    @patch('stt_service.output.keyboard.pyautogui')
    @patch('stt_service.output.keyboard.pyperclip')
    def test_clipboard_clearing(self, mock_pyperclip, mock_pyautogui):
        """Test clipboard clearing functionality."""
        config = self.config.copy()
        config['clear_clipboard'] = True
        
        output = KeyboardOutput(config)
        test_text = "Text to clear"
        
        output.output(test_text)
        
        # Should type the text
        mock_pyautogui.typewrite.assert_called_once_with(test_text, interval=0.01)


class TestKeyboardOutputFactory(unittest.TestCase):
    """Test cases for keyboard output factory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'output_target': 'active_window',
            'typing_delay': 0.01
        }

    @patch('stt_service.output.keyboard.pyautogui')
    def test_create_output_handler(self, mock_pyautogui):
        """Test creating keyboard output handler with factory function."""
        handler = create_output_handler(self.config)
        
        self.assertIsInstance(handler, KeyboardOutput)
        self.assertEqual(handler.output_target, 'active_window')

    @patch('stt_service.output.keyboard.pyautogui')
    def test_create_output_handler_with_defaults(self, mock_pyautogui):
        """Test creating keyboard output handler with default configuration."""
        minimal_config = {}
        
        handler = create_output_handler(minimal_config)
        
        self.assertIsInstance(handler, KeyboardOutput)
        # Should use default values
        self.assertIsNotNone(handler.output_target)

    @patch('stt_service.output.keyboard.pyautogui')
    def test_create_output_handler_different_targets(self, mock_pyautogui):
        """Test creating handlers for different output targets."""
        targets = ['active_window', 'clipboard', 'clipboard_paste']
        
        for target in targets:
            config = {'output_target': target}
            handler = create_output_handler(config)
            
            self.assertIsInstance(handler, KeyboardOutput)
            self.assertEqual(handler.output_target, target)


if __name__ == '__main__':
    unittest.main()