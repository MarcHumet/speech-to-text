"""Audio capture module for recording microphone input."""

import logging
import numpy as np
from typing import Optional, Callable
import threading
import queue

logger = logging.getLogger(__name__)


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
        except ImportError:
            logger.warning("sounddevice not available, audio capture disabled")
            self.available = False
    
    def start_recording(self) -> None:
        """Start recording audio."""
        if not self.available:
            raise RuntimeError("Audio capture not available - install sounddevice")
        
        if self._recording:
            logger.warning("Already recording")
            return
        
        self._recording = True
        self._audio_data = []
        
        logger.info(f"Starting audio recording (max {self.max_duration}s)")
        
        # Start recording in separate thread
        self._record_thread = threading.Thread(target=self._record)
        self._record_thread.start()
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data.
        
        Returns:
            NumPy array containing audio samples
        """
        if not self._recording:
            logger.warning("Not currently recording")
            return np.array([], dtype=np.float32)
        
        self._recording = False
        
        if self._record_thread:
            self._record_thread.join(timeout=1.0)
        
        logger.info(f"Stopped recording, captured {len(self._audio_data)} samples")
        
        if self._audio_data:
            return np.concatenate(self._audio_data)
        else:
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
