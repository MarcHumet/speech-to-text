"""STT Service - Self-hosted Speech-to-Text Service."""

__version__ = '0.1.0'
__author__ = 'Marc Humet'

from .core.config import Config
from .service import STTService

__all__ = ['Config', 'STTService']
