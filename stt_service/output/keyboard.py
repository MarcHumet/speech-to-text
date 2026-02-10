"""Keyboard output handler for typing text."""

import time
from typing import Optional
from .base import OutputHandler
from ..core.logger import get_logger, log_operation_start, log_operation_success, log_malfunction, log_performance

logger = get_logger(__name__)


class KeyboardHandler(OutputHandler):
    """Handle keyboard output for typing transcribed text."""
    
    def __init__(self, delay: float = 0.01):
        """Initialize keyboard handler.
        
        Args:
            delay: Delay between keystrokes (seconds)
        """
        self.delay = delay
        
        # Try to import keyboard library
        try:
            import pynput.keyboard as keyboard
            self.keyboard = keyboard
            self.controller = keyboard.Controller()
            self.available = True
        except ImportError:
            logger.warning("pynput library not available for keyboard output")
            self.available = False
    
    def send_text(self, text: str) -> bool:
        """Type the text using keyboard emulation.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful
        """
        if not self.available:
            logger.error("Keyboard output not available - install pynput")
            return False
        
        if not text:
            logger.warning("Empty text, nothing to type")
            return True
        
        try:
            # Small delay to allow user to position cursor
            time.sleep(0.1)
            
            # Type the text
            logger.info(f"Typing text: {text[:50]}...")
            self.controller.type(text)
            
            # Optional: add newline
            # self.controller.press(self.keyboard.Key.enter)
            # self.controller.release(self.keyboard.Key.enter)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if keyboard output is available.
        
        Returns:
            True if available
        """
        return self.available


class ClipboardHandler(OutputHandler):
    """Handle clipboard output for copying text."""
    
    def __init__(self):
        """Initialize clipboard handler."""
        # Try to import clipboard library
        try:
            import pyperclip
            self.pyperclip = pyperclip
            self.available = True
        except ImportError:
            logger.warning("pyperclip library not available for clipboard output")
            self.available = False
    
    def send_text(self, text: str) -> bool:
        """Copy text to clipboard.
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful
        """
        if not self.available:
            logger.error("Clipboard output not available - install pyperclip")
            return False
        
        if not text:
            logger.warning("Empty text, nothing to copy")
            return True
        
        try:
            self.pyperclip.copy(text)
            logger.info(f"Copied to clipboard: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if clipboard output is available.
        
        Returns:
            True if available
        """
        return self.available


class CompositeHandler(OutputHandler):
    """Composite handler that uses multiple output methods."""
    
    def __init__(self, *handlers: OutputHandler):
        """Initialize composite handler.
        
        Args:
            handlers: Output handlers to use
        """
        self.handlers = list(handlers)
    
    def send_text(self, text: str) -> bool:
        """Send text using all handlers.
        
        Args:
            text: Text to send
            
        Returns:
            True if at least one handler succeeded
        """
        if not self.handlers:
            logger.error("No output handlers configured")
            return False
        
        success = False
        for handler in self.handlers:
            if handler.is_available():
                if handler.send_text(text):
                    success = True
        
        return success
    
    def is_available(self) -> bool:
        """Check if at least one handler is available.
        
        Returns:
            True if available
        """
        return any(h.is_available() for h in self.handlers)


def create_output_handler(method: str = 'keyboard') -> OutputHandler:
    """Factory function to create output handlers.
    
    Args:
        method: Output method ('keyboard', 'clipboard', or 'both')
        
    Returns:
        Output handler instance
    """
    method = method.lower()
    
    if method == 'keyboard':
        return KeyboardHandler()
    elif method == 'clipboard':
        return ClipboardHandler()
    elif method == 'both':
        return CompositeHandler(KeyboardHandler(), ClipboardHandler())
    else:
        logger.warning(f"Unknown output method '{method}', using keyboard")
        return KeyboardHandler()
