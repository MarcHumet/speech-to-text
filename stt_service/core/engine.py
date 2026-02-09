"""STT Engine interface for model abstraction."""

import logging
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class STTEngine(ABC):
    """Abstract base class for STT engines."""
    
    @abstractmethod
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio to text.
        
        Args:
            audio: Audio data as numpy array
            language: Language code (e.g., 'en', 'es', 'ca')
            
        Returns:
            Transcribed text
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Load the STT model.
        
        Args:
            model_path: Path to model files
        """
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if engine is ready to transcribe.
        
        Returns:
            True if model is loaded and ready
        """
        pass


class DummyEngine(STTEngine):
    """Dummy STT engine for testing and development."""
    
    def __init__(self):
        self.ready = False
        logger.info("Initialized Dummy STT Engine")
    
    def load_model(self, model_path: str) -> None:
        """Simulate model loading.
        
        Args:
            model_path: Path to model (ignored for dummy)
        """
        logger.info(f"Dummy engine: pretending to load model from {model_path}")
        self.ready = True
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Return dummy transcription.
        
        Args:
            audio: Audio data (analyzed for dummy response)
            language: Language code (used in dummy response)
            
        Returns:
            Dummy transcription text
        """
        if not self.ready:
            raise RuntimeError("Model not loaded")
        
        duration = len(audio) / 16000.0  # Assume 16kHz
        lang_text = language or 'unknown'
        
        # Return a dummy transcription based on audio length
        if duration < 1.0:
            return f"[Dummy {lang_text}]: Short utterance"
        elif duration < 3.0:
            return f"[Dummy {lang_text}]: Medium length speech detected"
        else:
            return f"[Dummy {lang_text}]: Long speech detected, duration: {duration:.1f}s"
    
    def is_ready(self) -> bool:
        """Check if ready.
        
        Returns:
            True if ready
        """
        return self.ready


class WhisperEngine(STTEngine):
    """OpenAI Whisper STT engine (requires openai-whisper package)."""
    
    def __init__(self):
        self.model = None
        self.ready = False
        logger.info("Initialized Whisper STT Engine")
    
    def load_model(self, model_path: str) -> None:
        """Load Whisper model.
        
        Args:
            model_path: Model name or path (e.g., 'base', 'small', 'medium')
        """
        try:
            import whisper
            logger.info(f"Loading Whisper model: {model_path}")
            self.model = whisper.load_model(model_path)
            self.ready = True
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error("openai-whisper package not installed")
            raise RuntimeError("Install openai-whisper: pip install openai-whisper")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio using Whisper.
        
        Args:
            audio: Audio data as float32 numpy array
            language: Language code ('en', 'es', 'ca')
            
        Returns:
            Transcribed text
        """
        if not self.ready or self.model is None:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Whisper expects float32 audio
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize audio
            if audio.max() > 1.0 or audio.min() < -1.0:
                audio = audio / max(abs(audio.max()), abs(audio.min()))
            
            # Transcribe
            options = {}
            if language:
                options['language'] = language
            
            result = self.model.transcribe(audio, **options)
            return result['text'].strip()
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    def is_ready(self) -> bool:
        """Check if ready.
        
        Returns:
            True if model loaded
        """
        return self.ready


def create_engine(engine_type: str = 'dummy', model_path: str = '') -> STTEngine:
    """Factory function to create STT engines.
    
    Args:
        engine_type: Type of engine ('dummy', 'whisper')
        model_path: Path to model files
        
    Returns:
        Initialized STT engine
    """
    if engine_type.lower() == 'whisper':
        engine = WhisperEngine()
    else:
        engine = DummyEngine()
    
    if model_path:
        engine.load_model(model_path)
    
    return engine
