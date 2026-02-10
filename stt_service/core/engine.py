"""STT Engine interface for model abstraction."""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import time
import random

from .logger import get_logger, log_operation_start, log_operation_success, log_stt_event, log_malfunction, log_performance, log_audio_event

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
            # Add safety checks and debugging
            logger.info(f"Audio data: shape={audio.shape}, dtype={audio.dtype}, duration={len(audio)/16000:.2f}s")
            
            # Safety check: limit audio length to prevent memory issues
            max_samples = 16000 * 10  # 10 seconds max
            if len(audio) > max_samples:
                logger.warning(f"Audio too long ({len(audio)} samples), truncating to 10 seconds")
                audio = audio[:max_samples]
            
            # Whisper expects float32 audio
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize audio to [-1, 1] range
            if audio.max() > 1.0 or audio.min() < -1.0:
                max_val = max(abs(audio.max()), abs(audio.min()))
                audio = audio / max_val
                logger.info(f"Audio normalized by factor: {max_val}")
            
            # Additional safety: ensure audio is 1D
            if len(audio.shape) > 1:
                audio = audio.flatten()
                logger.info("Audio flattened to 1D")
            
            # Transcribe with minimal options to reduce memory usage
            options = {
                'fp16': False,  # Use fp32 to avoid potential issues
                'verbose': False,  # Reduce memory overhead
            }
            if language:
                options['language'] = language
            
            logger.info(f"Starting Whisper transcription with {len(audio)} samples...")
            result = self.model.transcribe(audio, **options)
            return result['text'].strip()
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            # Check if it's a memory error
            if "allocate memory" in str(e) or "out of memory" in str(e).lower():
                logger.warning("Whisper memory error - consider using a lighter model or shorter audio clips")
                return "[Memory Error: Audio too long or system low on RAM]"
            return ""
    
    def is_ready(self) -> bool:
        """Check if ready.
        
        Returns:
            True if model loaded
        """
        return self.ready


class FasterWhisperEngine(STTEngine):
    """Faster Whisper STT engine with GPU support (uses ctranslate2)."""
    
    def __init__(self):
        self.model = None
        self.ready = False
        self.model_path = None
        self.device = None
        self.compute_type = None
        logger.info("Initialized Faster Whisper STT Engine (GPU-optimized)")
    
    def load_model(self, model_path: str) -> None:
        """Load Faster Whisper model.
        
        Args:
            model_path: Model name or path (e.g., 'tiny', 'base', 'small', 'medium', 'large')
        """
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Faster Whisper model: {model_path}")
            
            # Store model configuration for lazy loading
            self.model_path = model_path
            
            # Try GPU first, fallback to CPU
            try:
                # Use GPU with CUDA
                self.device = "cuda"
                self.compute_type = "float16"
                self.model = WhisperModel(model_path, device=self.device, compute_type=self.compute_type)
                logger.info("✅ Faster Whisper model loaded on GPU with CUDA!")
            except Exception as gpu_error:
                logger.warning(f"GPU loading failed: {gpu_error}")
                # Fallback to CPU
                self.device = "cpu"
                self.compute_type = "int8"
                self.model = WhisperModel(model_path, device=self.device, compute_type=self.compute_type)
                logger.info("✅ Faster Whisper model loaded on CPU (fallback)")
            
            self.ready = True
            
        except ImportError:
            logger.error("faster-whisper package not installed")
            raise RuntimeError("Install faster-whisper: uv add faster-whisper")
        except Exception as e:
            logger.error(f"Failed to load Faster Whisper model: {e}")
            raise
    
    def transcribe(self, audio: np.ndarray, language: Optional[str] = None) -> str:
        """Transcribe audio using Faster Whisper.
        
        Args:
            audio: Audio data as float32 numpy array
            language: Language code ('en', 'es', 'ca')
            
        Returns:
            Transcribed text
        """
        # Ensure model is loaded (supports lazy loading)
        self._ensure_model_loaded()
        
        if not self.ready or self.model is None:
            raise RuntimeError("Faster Whisper model not loaded")
        
        try:
            # Add safety checks (use 16000 as fallback sample rate for duration estimation)
            estimated_sample_rate = 16000  # Default assumption for duration calculation
            logger.info(f"Audio data: shape={audio.shape}, dtype={audio.dtype}, duration={len(audio)/estimated_sample_rate:.2f}s")
            
            # Convert 2D audio to 1D if needed (faster-whisper expects 1D)
            if len(audio.shape) == 2:
                if audio.shape[1] == 1:
                    # Mono audio: (samples, 1) -> (samples,)
                    audio = audio.flatten()
                    logger.info(f"Flattened mono audio to 1D: shape={audio.shape}")
                else:
                    # Stereo audio: (samples, 2) -> (samples,) by averaging channels
                    audio = np.mean(audio, axis=1)
                    logger.info(f"Converted stereo to mono: shape={audio.shape}")
            
            # Safety check: limit audio length to prevent memory issues
            # Use estimated sample rate for max samples (assume 8-16kHz range)
            max_samples = estimated_sample_rate * 10  # 10 seconds max
            if len(audio) > max_samples:
                logger.warning(f"Audio too long ({len(audio)} samples), truncating to 10 seconds")
                audio = audio[:max_samples]
            
            # Faster-whisper expects float32 audio
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Additional safety: check memory usage
            audio_size_mb = audio.nbytes / (1024 * 1024)
            if audio_size_mb > 50:  # Limit to 50MB
                logger.error(f"Audio data too large: {audio_size_mb:.1f}MB, max allowed: 50MB")
                return ""
            
            # Validate audio is not empty
            if len(audio) == 0:
                logger.warning("Empty audio array received")
                return ""
            
            # Normalize audio to [-1, 1] range if needed
            audio_max = np.abs(audio).max()
            if audio_max > 1.0:
                audio = audio / audio_max
                logger.info(f"Audio normalized by factor: {audio_max}")
            elif audio_max == 0.0:
                logger.warning("Silent audio detected (all zeros)")
                return ""
            
            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                audio,
                language=language,
                beam_size=1,  # Faster inference
                best_of=1,    # Faster inference
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine segments into text
            text = " ".join([segment.text for segment in segments]).strip()
            logger.info(f"Faster Whisper transcription completed: '{text}'")
            
            # Note: Model stays loaded in GPU memory for better performance
            # Use unload_model() manually if you need to free GPU memory
            
            return text
            
        except MemoryError as e:
            logger.error(f"Faster Whisper ran out of memory: {e}")
            logger.error("Try reducing max_duration in config or use smaller model (tiny/base)")
            return ""
        except RuntimeError as e:
            if "can't allocate memory" in str(e).lower():
                logger.error(f"Memory allocation failed: {e}")
                logger.error("Try reducing max_duration or switching to CPU-only whisper engine")
            else:
                logger.error(f"Faster Whisper runtime error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Faster Whisper transcription failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return ""
    
    def is_ready(self) -> bool:
        """Check if ready.
        
        Returns:
            True if model loaded
        """
        return self.ready


def create_engine(engine_type: str = 'faster-whisper', model_path: str = '') -> STTEngine:
    """Factory function to create STT engines.
    
    Args:
        engine_type: Type of engine ('faster-whisper', 'whisper', 'dummy')
        model_path: Path to model files
        
    Returns:
        Initialized STT engine
    """
    if engine_type.lower() == 'faster-whisper':
        engine = FasterWhisperEngine()
    elif engine_type.lower() == 'whisper':
        engine = WhisperEngine()
    elif engine_type.lower() == 'dummy':
        engine = DummyEngine()
    else:
        # Default to faster-whisper for unknown types (avoid dummy)
        logger.warning(f"Unknown engine type '{engine_type}', defaulting to faster-whisper")
        engine = FasterWhisperEngine()
    
    if model_path:
        engine.load_model(model_path)
    
    return engine
