"""Audio capture module for recording microphone input."""

import numpy as np
from typing import Optional, Callable
import threading
import queue
import time

from .logger import get_logger, log_malfunction, log_audio_event, log_performance

logger = get_logger(__name__)


class AudioCapture:
    """Handle audio recording from microphone."""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 max_duration: int = 30,
                 device: str = 'default'):
        """Initialize audio capture.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            max_duration: Maximum recording duration in seconds
            device: Audio device name or index
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration = max_duration
        self.device = device
        
        self._recording = False
        self._audio_data = []
        self._stream = None
        
        # Try to import audio library (will be installed later)
        try:
            import sounddevice as sd
            self.sd = sd
            self.available = True
            log_audio_event("Audio capture initialized", {
                "device": device, 
                "sample_rate": sample_rate, 
                "channels": channels,
                "max_duration": max_duration
            })
        except ImportError as e:
            log_malfunction("AudioCapture", f"sounddevice not available: {e}", "ERROR")
            logger.error("🚨 Audio capture disabled - sounddevice not installed")
            self.available = False
    
    def start_recording(self) -> None:
        """Start recording audio."""
        if not self.available:
            log_malfunction("AudioCapture", "Attempted to record without available audio system", "ERROR")
            raise RuntimeError("Audio capture not available - install sounddevice")
        
        if self._recording:
            log_malfunction("AudioCapture", "Attempted to start recording while already recording", "WARNING")
            return
        
        self._recording = True
        self._audio_data = []
        self._start_time = time.time()
        
        log_audio_event("Recording started", {
            "max_duration": self.max_duration,
            "sample_rate": self.sample_rate,
            "device": self.device
        })
        
        # Start recording in separate thread
        self._record_thread = threading.Thread(target=self._record)
        self._record_thread.start()
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data.
        
        Returns:
            NumPy array containing audio samples
        """
        if not self._recording:
            log_malfunction("AudioCapture", "Attempted to stop recording when not recording", "WARNING")
            return np.array([], dtype=np.float32)
        
        self._recording = False
        
        if self._record_thread:
            self._record_thread.join(timeout=1.0)
        
        # Calculate metrics
        duration = time.time() - self._start_time if hasattr(self, '_start_time') else 0
        samples_count = len(self._audio_data)
        
        log_audio_event("Recording stopped", {
            "duration": f"{duration:.2f}s",
            "data_chunks": samples_count,
            "audio_quality": "good" if samples_count > 10 else "poor"
        })
        
        log_performance("Audio recording", duration, threshold=self.max_duration * 0.8)
        
        if self._audio_data:
            audio_array = np.concatenate(self._audio_data)
            logger.info(f"✅ Audio capture successful: {len(audio_array)} samples in {duration:.2f}s")
            return audio_array
        else:
            log_malfunction("AudioCapture", "No audio data captured during session", "WARNING")
            return np.array([], dtype=np.float32)
    
    def _record(self) -> None:
        """Internal recording loop."""
        try:
            max_samples = int(self.sample_rate * self.max_duration)
            samples_recorded = 0
            
            with self.sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                device=self.device if self.device != 'default' else None
            ) as stream:
                while self._recording and samples_recorded < max_samples:
                    data, overflowed = stream.read(self.sample_rate // 10)  # 100ms chunks
                    
                    if overflowed:
                        logger.warning("Audio buffer overflow")
                    
                    self._audio_data.append(data.copy())
                    samples_recorded += len(data)
                    
            if samples_recorded >= max_samples:
                logger.info("Maximum recording duration reached")
                self._recording = False
                
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            self._recording = False
    
    def is_recording(self) -> bool:
        """Check if currently recording.
        
        Returns:
            True if recording is in progress
        """
        return self._recording
    
    def record_until_silence(self, 
                            silence_threshold: float = 0.01,
                            silence_duration: float = 1.0) -> np.ndarray:
        """Record until silence is detected.
        
        Args:
            silence_threshold: RMS threshold below which is considered silence
            silence_duration: Duration of silence required to stop (seconds)
            
        Returns:
            NumPy array containing audio samples
        """
        if not self.available:
            raise RuntimeError("Audio capture not available - install sounddevice")
        
        logger.info("Recording until silence detected...")
        
        audio_data = []
        silence_samples = int(self.sample_rate * silence_duration)
        consecutive_silence = 0
        
        try:
            with self.sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                device=self.device if self.device != 'default' else None
            ) as stream:
                
                while consecutive_silence < silence_samples:
                    data, _ = stream.read(self.sample_rate // 10)  # 100ms chunks
                    audio_data.append(data.copy())
                    
                    # Calculate RMS
                    rms = np.sqrt(np.mean(data**2))
                    
                    if rms < silence_threshold:
                        consecutive_silence += len(data)
                    else:
                        consecutive_silence = 0
                    
                    # Safety check for max duration
                    if len(audio_data) * len(data) >= self.sample_rate * self.max_duration:
                        logger.info("Maximum duration reached")
                        break
        
        except Exception as e:
            logger.error(f"Error during silence detection: {e}")
        
        logger.info(f"Silence detected, captured {len(audio_data)} chunks")
        
        if audio_data:
            return np.concatenate(audio_data)
        else:
            return np.array([], dtype=np.float32)
