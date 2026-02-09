"""Main STT service orchestrator."""

import logging
import time
from typing import Optional

from .core.config import Config
from .core.audio_capture import AudioCapture
from .core.engine import create_engine, STTEngine
from .input.hotkey import create_hotkey_handler
from .output.keyboard import create_output_handler

logger = logging.getLogger(__name__)


class STTService:
    """Main service class that orchestrates all components."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize STT service.
        
        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or Config()
        self._setup_logging()
        
        logger.info("Initializing STT Service...")
        
        # Initialize components
        self.audio_capture = None
        self.engine = None
        self.input_handler = None
        self.output_handler = None
        
        self._running = False
        self._processing = False
        
        self._initialize_components()
    
    def _setup_logging(self) -> None:
        """Configure logging based on config."""
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get('logging.file')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
            ] + ([logging.FileHandler(log_file)] if log_file else [])
        )
    
    def _initialize_components(self) -> None:
        """Initialize all service components."""
        # Audio capture
        self.audio_capture = AudioCapture(
            sample_rate=self.config.get('audio.sample_rate', 16000),
            channels=self.config.get('audio.channels', 1),
            max_duration=self.config.get('audio.max_duration', 30),
            device=self.config.get('service.audio_device', 'default')
        )
        
        # STT Engine
        engine_type = self.config.get('model.type', 'dummy')
        model_path = self.config.get('model.path', '')
        self.engine = create_engine(engine_type, model_path)
        
        # Input handler
        hotkey = self.config.get('input.hotkey', 'ctrl+shift+space')
        self.input_handler = create_hotkey_handler(hotkey)
        
        # Output handler
        output_method = self.config.get('output.method', 'keyboard')
        self.output_handler = create_output_handler(output_method)
        
        logger.info("All components initialized")
    
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
            logger.info("Already processing, ignoring trigger")
            return
        
        self._processing = True
        
        try:
            # Toggle recording
            if self.audio_capture.is_recording():
                logger.info("Stopping recording...")
                audio_data = self.audio_capture.stop_recording()
                
                if len(audio_data) > 0:
                    self._process_audio(audio_data)
                else:
                    logger.warning("No audio data captured")
            else:
                logger.info("Starting recording...")
                self.audio_capture.start_recording()
        
        except Exception as e:
            logger.error(f"Error handling trigger: {e}")
        
        finally:
            self._processing = False
    
    def _process_audio(self, audio_data) -> None:
        """Process captured audio.
        
        Args:
            audio_data: Audio data to process
        """
        logger.info(f"Processing audio ({len(audio_data)} samples)...")
        
        try:
            # Transcribe
            language = self.config.get('service.language', 'en')
            text = self.engine.transcribe(audio_data, language)
            
            if text:
                logger.info(f"Transcription: {text}")
                
                # Send to output
                if self.output_handler.send_text(text):
                    logger.info("Text sent successfully")
                else:
                    logger.error("Failed to send text")
            else:
                logger.warning("No transcription result")
        
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
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
