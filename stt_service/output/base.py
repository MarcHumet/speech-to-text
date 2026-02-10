"""Base class for output handlers."""

from abc import ABC, abstractmethod


class OutputHandler(ABC):
    """Abstract base class for output handlers."""
    
    @abstractmethod
    def send_text(self, text: str) -> bool:
        """Send transcribed text to output.
        
        Args:
            text: Text to send
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if output method is available.
        
        Returns:
            True if output can be used
        """
        pass
