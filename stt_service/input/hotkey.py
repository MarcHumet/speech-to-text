"""Hotkey input handler for triggering speech recognition."""

import logging
from typing import Callable, Optional
from .base import InputHandler

logger = logging.getLogger(__name__)


class HotkeyHandler(InputHandler):
    """Handle hotkey detection for triggering STT."""
    
    def __init__(self, hotkey: str = 'ctrl+shift+space'):
        """Initialize hotkey handler.
        
        Args:
            hotkey: Hotkey combination (e.g., 'ctrl+shift+space')
        """
        self.hotkey = hotkey
        self._active = False
        self._callback = None
        self._keyboard = None
        
        # Try to import keyboard library
        try:
            import keyboard
            self.keyboard_lib = keyboard
            self.available = True
        except ImportError:
            logger.warning("keyboard library not available")
            self.available = False
    
    def start(self, callback: Callable[[], None]) -> None:
        """Start listening for hotkey.
        
        Args:
            callback: Function to call when hotkey is pressed
        """
        if not self.available:
            raise RuntimeError("keyboard library not installed - install with: pip install keyboard")
        
        if self._active:
            logger.warning("Hotkey handler already active")
            return
        
        self._callback = callback
        self._active = True
        
        # Register hotkey
        try:
            self.keyboard_lib.add_hotkey(self.hotkey, self._on_hotkey_pressed)
            logger.info(f"Hotkey handler started: {self.hotkey}")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
            self._active = False
            raise
    
    def stop(self) -> None:
        """Stop listening for hotkey."""
        if not self._active:
            return
        
        try:
            self.keyboard_lib.remove_hotkey(self.hotkey)
            logger.info("Hotkey handler stopped")
        except Exception as e:
            logger.error(f"Error stopping hotkey handler: {e}")
        
        self._active = False
        self._callback = None
    
    def is_active(self) -> bool:
        """Check if handler is active.
        
        Returns:
            True if listening for hotkeys
        """
        return self._active
    
    def _on_hotkey_pressed(self) -> None:
        """Internal callback for hotkey press."""
        logger.debug(f"Hotkey pressed: {self.hotkey}")
        if self._callback:
            try:
                self._callback()
            except Exception as e:
                logger.error(f"Error in hotkey callback: {e}")


class PynputHotkeyHandler(InputHandler):
    """Alternative hotkey handler using pynput (may work better on some systems)."""
    
    def __init__(self, hotkey: str = 'ctrl+shift+space'):
        """Initialize pynput hotkey handler.
        
        Args:
            hotkey: Hotkey combination
        """
        self.hotkey = hotkey
        self._active = False
        self._callback = None
        self._listener = None
        
        # Try to import pynput
        try:
            from pynput import keyboard
            self.pynput_keyboard = keyboard
            self.available = True
        except ImportError:
            logger.warning("pynput library not available")
            self.available = False
    
    def start(self, callback: Callable[[], None]) -> None:
        """Start listening for hotkey.
        
        Args:
            callback: Function to call when hotkey is pressed
        """
        if not self.available:
            raise RuntimeError("pynput library not installed - install with: pip install pynput")
        
        if self._active:
            logger.warning("Hotkey handler already active")
            return
        
        self._callback = callback
        self._active = True
        
        # Parse hotkey string
        keys = self._parse_hotkey(self.hotkey)
        
        # Create global hotkey
        try:
            hotkey_obj = self.pynput_keyboard.HotKey(
                keys,
                self._on_hotkey_pressed
            )
            
            # Create listener
            self._listener = self.pynput_keyboard.Listener(
                on_press=lambda k: hotkey_obj.press(self._listener.canonical(k)),
                on_release=lambda k: hotkey_obj.release(self._listener.canonical(k))
            )
            
            self._listener.start()
            logger.info(f"Pynput hotkey handler started: {self.hotkey}")
            
        except Exception as e:
            logger.error(f"Failed to start pynput listener: {e}")
            self._active = False
            raise
    
    def stop(self) -> None:
        """Stop listening for hotkey."""
        if not self._active:
            return
        
        if self._listener:
            self._listener.stop()
            self._listener = None
        
        self._active = False
        self._callback = None
        logger.info("Pynput hotkey handler stopped")
    
    def is_active(self) -> bool:
        """Check if handler is active.
        
        Returns:
            True if listening
        """
        return self._active
    
    def _parse_hotkey(self, hotkey_str: str):
        """Parse hotkey string into pynput key objects.
        
        Args:
            hotkey_str: Hotkey string like 'ctrl+shift+space'
            
        Returns:
            Set of pynput Key objects
        """
        Key = self.pynput_keyboard.Key
        KeyCode = self.pynput_keyboard.KeyCode
        
        parts = hotkey_str.lower().split('+')
        keys = set()
        
        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                keys.add(Key.ctrl_l)
            elif part == 'shift':
                keys.add(Key.shift_l)
            elif part == 'alt':
                keys.add(Key.alt_l)
            elif part == 'space':
                keys.add(Key.space)
            else:
                # Try as character key
                keys.add(KeyCode.from_char(part))
        
        return keys
    
    def _on_hotkey_pressed(self) -> None:
        """Internal callback for hotkey press."""
        logger.debug(f"Hotkey pressed: {self.hotkey}")
        if self._callback:
            try:
                self._callback()
            except Exception as e:
                logger.error(f"Error in hotkey callback: {e}")


def create_hotkey_handler(hotkey: str = 'ctrl+shift+space', 
                         backend: str = 'keyboard') -> InputHandler:
    """Factory function to create hotkey handlers.
    
    Args:
        hotkey: Hotkey combination
        backend: Backend to use ('keyboard' or 'pynput')
        
    Returns:
        Hotkey handler instance
    """
    if backend.lower() == 'pynput':
        return PynputHotkeyHandler(hotkey)
    else:
        return HotkeyHandler(hotkey)
