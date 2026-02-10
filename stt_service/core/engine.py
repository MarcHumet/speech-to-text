"""STT Engine interface for model abstraction."""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import time
import random

from .logger import get_logger, log_operation_start, log_operation_success, log_stt_event, log_malfunction

logger = get_logger(__name__)


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
        self.transcription_count = 0
        log_operation_start("DummyEngine Init")
        logger.info("🤖 Dummy STT Engine initialized for testing")
    
    def load_model(self, model_path: str) -> None:
        """Simulate model loading.
        
        Args:
            model_path: Path to model (ignored for dummy)
        """
        start_time = time.time()
        log_operation_start("Load Dummy Model", model_path=model_path)
        
        # Simulate loading time
        time.sleep(0.1)
        
        self.ready = True
        duration = time.time() - start_time
        
        logger.info(f"📁 Dummy model 'loaded' from {model_path}")
        log_operation_success("Load Dummy Model", duration=duration, model_path=model_path)
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Return dummy transcription.
        
        Args:
            audio: Audio data (analyzed for dummy response)
            language: Language code (used in dummy response)
            
        Returns:
            Dummy transcription text
        """
        start_time = time.time()
        self.transcription_count += 1
        
        if not self.ready:
            log_malfunction("DummyEngine", "Transcription attempted before model loading", "ERROR")
            raise RuntimeError("Model not loaded")
        
        # Analyze audio for realistic dummy response
        audio_length = len(audio) if audio is not None else 0
        duration = audio_length / 16000.0  # Assume 16kHz
        lang_text = language or 'unknown'
        
        log_audio_event("Transcription request", {
            "audio_samples": audio_length,
            "duration": f"{duration:.2f}s",
            "language": lang_text,
            "attempt": self.transcription_count
        })
        
        # Generate realistic dummy response based on audio length
        if duration < 1.0:
            result = f"[Dummy {lang_text}]: Short utterance"
        elif duration < 3.0:
            result = f"[Dummy {lang_text}]: Medium length speech detected"
        else:
            result = f"[Dummy {lang_text}]: Long speech detected, duration: {duration:.1f}s"
        
        # Simulate processing time
        processing_time = min(0.5, duration * 0.2)  # Realistic processing time
        time.sleep(processing_time)
        
        total_time = time.time() - start_time
        confidence = random.uniform(0.8, 0.95)  # Fake confidence score
        
        log_stt_event("Transcription completed", 
                      text=result, 
                      confidence=confidence,
                      processing_time=total_time,
                      audio_duration=duration)
        
        log_performance("STT Transcription", total_time, threshold=2.0)
        
        return result
    
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
