"""Base class for input handlers."""

from abc import ABC, abstractmethod
from typing import Callable


class InputHandler(ABC):
    """Abstract base class for input handlers."""
    
    @abstractmethod
    def start(self, callback: Callable[[], None]) -> None:
        """Start listening for input events.
        
        Args:
            callback: Function to call when input is detected
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop listening for input events."""
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Check if handler is actively listening.
        
        Returns:
            True if listening for input
        """
        pass
