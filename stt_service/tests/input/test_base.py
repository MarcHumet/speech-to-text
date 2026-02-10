"""Tests for base input module."""

import unittest
from unittest.mock import Mock, patch

from stt_service.input.base import InputHandler


class TestInputHandler(unittest.TestCase):
    """Test cases for InputHandler base class."""

    def test_input_handler_abstract_methods(self):
        """Test that InputHandler is abstract and requires implementation."""
        with self.assertRaises(TypeError):
            InputHandler()

    def test_input_handler_interface(self):
        """Test InputHandler interface definition."""
        # Create a concrete implementation for testing
        class TestInputHandler(InputHandler):
            def __init__(self, config, callback):
                super().__init__(config, callback)
            
            def start(self):
                self.is_active = True
            
            def stop(self):
                self.is_active = False
            
            def is_available(self):
                return True
        
        callback = Mock()
        handler = TestInputHandler({}, callback)
        
        self.assertTrue(hasattr(handler, 'start'))
        self.assertTrue(hasattr(handler, 'stop'))
        self.assertTrue(hasattr(handler, 'is_available'))
        self.assertEqual(handler.callback, callback)

    def test_input_handler_context_manager(self):
        """Test InputHandler context manager protocol."""
        class TestInputHandler(InputHandler):
            def __init__(self, config, callback):
                super().__init__(config, callback)
                self.started = False
                self.stopped = False
            
            def start(self):
                self.started = True
            
            def stop(self):
                self.stopped = True
            
            def is_available(self):
                return True
        
        callback = Mock()
        handler = TestInputHandler({}, callback)
        
        with handler as ctx_handler:
            self.assertIs(ctx_handler, handler)
            self.assertTrue(handler.started)
        
        self.assertTrue(handler.stopped)

    def test_input_handler_callback_storage(self):
        """Test that callback is properly stored."""
        class TestInputHandler(InputHandler):
            def __init__(self, config, callback):
                super().__init__(config, callback)
            
            def start(self):
                pass
            
            def stop(self):
                pass
            
            def is_available(self):
                return True
        
        callback = Mock()
        handler = TestInputHandler({}, callback)
        
        self.assertEqual(handler.callback, callback)

    def test_input_handler_config_storage(self):
        """Test that config is properly stored."""
        class TestInputHandler(InputHandler):
            def __init__(self, config, callback):
                super().__init__(config, callback)
            
            def start(self):
                pass
            
            def stop(self):
                pass
            
            def is_available(self):
                return True
        
        config = {'test_option': 'test_value'}
        callback = Mock()
        handler = TestInputHandler(config, callback)
        
        self.assertEqual(handler.config, config)


if __name__ == '__main__':
    unittest.main()