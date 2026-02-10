"""Main STT service orchestrator."""

import time
from typing import Optional
import threading
import numpy as np

from .core.config import Config
from .core.audio_capture import AudioCapture
from .core.engine import create_engine, STTEngine
from .input.hotkey import create_hotkey_handler
from .output.keyboard import create_output_handler
from .core.logger import get_logger, log_operation_start, log_operation_success, log_operation_error, log_malfunction, log_stt_event, log_audio_event, log_performance

logger = get_logger(__name__)


class STTService:
    """Main service class that orchestrates all components."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize STT service.
        
        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or Config()
        self.service_start_time = time.time()
        
        log_operation_start("STT Service Initialization", 
                           language=self.config.get('service.language'),
                           audio_device=self.config.get('service.audio_device'))
        
        # Initialize components
        self.audio_capture = None
        self.engine = None
        self.input_handler = None
        self.output_handler = None
        
        self._running = False
        self._processing = False
        self._transcription_count = 0
        self._error_count = 0
        
        try:
            self._initialize_components()
            init_duration = time.time() - self.service_start_time
            log_operation_success("STT Service Initialization", duration=init_duration)
        except Exception as e:
            log_operation_error("STT Service Initialization", e)
            raise
    
    def _initialize_components(self) -> None:
        """Initialize all service components."""
        log_operation_start("Component Initialization")
        
        try:
            # Audio capture
            logger.info("🎤 Initializing audio capture...")
            self.audio_capture = AudioCapture(
                sample_rate=self.config.get('audio.sample_rate', 16000),
                channels=self.config.get('audio.channels', 1),
                max_duration=self.config.get('audio.max_duration', 30),
                device=self.config.get('service.audio_device', 'default')
            )
            
            # STT Engine
            engine_type = self.config.get('model.type', 'dummy')
            model_path = self.config.get('model.path', '')
            logger.info(f"🤖 Initializing STT engine: {engine_type}")
            self.engine = create_engine(engine_type, model_path)
            
            # Input handler
            logger.info("⌨️ Initializing input handler...")
            self.input_handler = create_hotkey_handler(
                self.config.get('input.hotkey', 'ctrl+shift+space'),
                backend='pynput'  # Use pynput to avoid requiring root
            )
            
            # Output handler
            logger.info("🖨 Initializing output handler...")
            self.output_handler = create_output_handler(
                method=self.config.get('output.method', 'keyboard')
            )
            
            logger.success("✅ All components initialized successfully")
            
        except Exception as e:
            log_malfunction("STTService", f"Component initialization failed: {e}", "CRITICAL")
            raise
    
    def start(self) -> None:
        """Start the STT service."""
        if self._running:
            logger.warning("Service already running")
            return
        
        logger.info("Starting STT Service...")
        
        # Check if engine is ready
        if not self.engine.is_ready():
            logger.warning("STT engine not ready, attempting to load model...")
            model_path = self.config.get('model.path', 'base')
            try:
                self.engine.load_model(model_path)
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
        
        # Start input handler
        try:
            self.input_handler.start(self._on_trigger)
            self._running = True
            logger.info("STT Service started successfully")
            logger.info(f"Press {self.config.get('input.hotkey')} to start recording")
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the STT service."""
        if not self._running:
            logger.warning("Service not running")
            return
        
        logger.info("Stopping STT Service...")
        
        # Stop input handler
        if self.input_handler:
            self.input_handler.stop()
        
        # Stop any ongoing recording
        if self.audio_capture and self.audio_capture.is_recording():
            self.audio_capture.stop_recording()
        
        self._running = False
        logger.info("STT Service stopped")
    
    def _on_trigger(self) -> None:
        """Handle trigger event (hotkey press)."""
        if self._processing:
            log_malfunction("STTService", "Trigger activated while already processing", "WARNING")
            return
        
        self._processing = True
        operation_start = time.time()
        
        try:
            # Toggle recording
            if self.audio_capture.is_recording():
                log_audio_event("Recording stop triggered")
                audio_data = self.audio_capture.stop_recording()
                
                if len(audio_data) > 0:
                    self._process_audio(audio_data)
                else:
                    log_malfunction("STTService", "No audio data captured during recording session", "WARNING")
            else:
                log_audio_event("Recording start triggered")
                self.audio_capture.start_recording()
        
        except Exception as e:
            operation_duration = time.time() - operation_start
            log_operation_error("Trigger Handling", e, duration=operation_duration)
        
        finally:
            self._processing = False
    
    def _process_audio(self, audio_data) -> None:
        """Process captured audio.
        
        Args:
            audio_data: Audio data to process
        """
        start_time = time.time()
        self._transcription_count += 1
        
        log_operation_start("Audio Processing", 
                           samples=len(audio_data), 
                           transcription_id=self._transcription_count)
        
        try:
            # Transcribe
            language = self.config.get('service.language', 'en')
            text = self.engine.transcribe(audio_data, language)
            
            if text and text.strip():
                # Log the detected text for proper visibility
                logger.info(f"🎯 DETECTED TEXT: \"{text}\"")
                log_stt_event("Transcription success", text=text, transcription_id=self._transcription_count)
                
                # Send to output
                output_start = time.time()
                if self.output_handler.send_text(text):
                    output_duration = time.time() - output_start
                    logger.success(f"✅ Text output successful: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                    log_performance("Text output", output_duration, threshold=1.0)
                else:
                    log_malfunction("STTService", "Failed to send text to output", "ERROR")
                    self._error_count += 1
            else:
                log_malfunction("STTService", "Empty transcription result", "WARNING")
                self._error_count += 1
            
            processing_duration = time.time() - start_time
            log_operation_success("Audio Processing", 
                                duration=processing_duration,
                                transcription_id=self._transcription_count)
        
        except Exception as e:
            processing_duration = time.time() - start_time  
            self._error_count += 1
            log_operation_error("Audio Processing", e, 
                              duration=processing_duration,
                              transcription_id=self._transcription_count)
    
    def _on_speech_input(self, audio_data: np.ndarray) -> None:
        """Handle speech input from audio capture.
        
        Args:
            audio_data: Captured audio data
        """
        try:
            # Process the audio data
            self._process_audio(audio_data)
        except Exception as e:
            logger.error(f"Speech input processing failed: {e}")
            log_malfunction("STTService", f"Speech input failed: {e}", "ERROR")
    
    def run(self) -> None:
        """Run the service (blocking call)."""
        self.start()
        
        try:
            logger.info("Service running. Press Ctrl+C to stop.")
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def is_running(self) -> bool:
        """Check if service is running.
        
        Returns:
            True if running
        """
        return self._running
