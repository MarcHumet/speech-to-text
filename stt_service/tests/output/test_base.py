"""Tests for base output module."""

import unittest
from unittest.mock import Mock

from stt_service.output.base import OutputHandler


class TestOutputHandler(unittest.TestCase):
    """Test cases for OutputHandler base class."""

    def test_output_handler_abstract_methods(self):
        """Test that OutputHandler is abstract and requires implementation."""
        with self.assertRaises(TypeError):
            OutputHandler()

    def test_output_handler_interface(self):
        """Test OutputHandler interface definition."""
        # Create a concrete implementation for testing
        class TestOutputHandler(OutputHandler):
            def __init__(self, config):
                super().__init__(config)
                self.output_history = []
            
            def output(self, text):
                if text and text.strip():
                    self.output_history.append(text.strip())
            
            def is_available(self):
                return True
            
            def cleanup(self):
                self.output_history.clear()
        
        handler = TestOutputHandler({})
        
        self.assertTrue(hasattr(handler, 'output'))
        self.assertTrue(hasattr(handler, 'is_available'))
        self.assertTrue(hasattr(handler, 'cleanup'))

    def test_output_handler_config_storage(self):
        """Test that config is properly stored."""
        class TestOutputHandler(OutputHandler):
            def __init__(self, config):
                super().__init__(config)
            
            def output(self, text):
                pass
            
            def is_available(self):
                return True
            
            def cleanup(self):
                pass
        
        config = {'test_option': 'test_value', 'output_target': 'test'}
        handler = TestOutputHandler(config)
        
        self.assertEqual(handler.config, config)

    def test_output_handler_functionality(self):
        """Test basic output handler functionality."""
        class TestOutputHandler(OutputHandler):
            def __init__(self, config):
                super().__init__(config)
                self.last_output = None
            
            def output(self, text):
                self.last_output = text
            
            def is_available(self):
                return True
            
            def cleanup(self):
                self.last_output = None
        
        handler = TestOutputHandler({})
        
        # Test output
        test_text = "Hello, world!"
        handler.output(test_text)
        self.assertEqual(handler.last_output, test_text)
        
        # Test availability
        self.assertTrue(handler.is_available())
        
        # Test cleanup
        handler.cleanup()
        self.assertIsNone(handler.last_output)

    def test_output_handler_context_manager(self):
        """Test OutputHandler context manager protocol if implemented."""
        class TestOutputHandler(OutputHandler):
            def __init__(self, config):
                super().__init__(config)
                self.initialized = False
                self.cleaned_up = False
            
            def output(self, text):
                pass
            
            def is_available(self):
                return True
            
            def cleanup(self):
                self.cleaned_up = True
            
            def __enter__(self):
                self.initialized = True
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.cleanup()
        
        handler = TestOutputHandler({})
        
        with handler as ctx_handler:
            self.assertIs(ctx_handler, handler)
            self.assertTrue(handler.initialized)
        
        self.assertTrue(handler.cleaned_up)

    def test_output_handler_error_handling(self):
        """Test error handling in output handler."""
        class TestOutputHandler(OutputHandler):
            def __init__(self, config):
                super().__init__(config)
                self.should_fail = False
            
            def output(self, text):
                if self.should_fail:
                    raise Exception("Output failed")
                return text
            
            def is_available(self):
                return not self.should_fail
            
            def cleanup(self):
                pass
        
        handler = TestOutputHandler({})
        
        # Test normal operation
        self.assertTrue(handler.is_available())
        
        # Test with failures
        handler.should_fail = True
        self.assertFalse(handler.is_available())
        
        with self.assertRaises(Exception):
            handler.output("test")


if __name__ == '__main__':
    unittest.main()