"""
Centralized logging configuration with loguru for STT Service.

This module provides a configured logger with proper rotation settings
and custom formatting for easy debugging and malfunction detection.
"""

import sys
import os
from pathlib import Path
from loguru import logger
from typing import Optional


class LoggerConfig:
    """Configuration class for STT Service logging."""
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize logging configuration.
        
        Args:
            log_dir: Directory for log files. Defaults to logs/ in project root.
        """
        if log_dir is None:
            # Default to logs directory in project root
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Remove default handler
        logger.remove()
        
        # Configure logging
        self._setup_console_logging()
        self._setup_file_logging()
        self._setup_error_logging()
    
    def _setup_console_logging(self):
        """Configure console logging with colored output."""
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True,
            enqueue=True,
        )
    
    def _setup_file_logging(self):
        """Configure main log file with rotation."""
        log_file = self.log_dir / "stt_service.log"
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="1 week",      # Rotate weekly
            retention="4 weeks",    # Keep 4 weeks of logs
            compression="zip",      # Compress old logs
            enqueue=True,
            serialize=False,
        )
        
        # Additional rotation by size (10MB)
        logger.add(
            self.log_dir / "stt_service_size.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",       # Rotate at 10MB
            retention=10,           # Keep max 10 files
            compression="zip",
            enqueue=True,
            serialize=False,
        )
    
    def _setup_error_logging(self):
        """Configure separate error log file."""
        error_log = self.log_dir / "stt_service_errors.log"
        
        logger.add(
            error_log,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="WARNING",
            rotation="1 week",
            retention="4 weeks", 
            compression="zip",
            enqueue=True,
            serialize=False,
        )
    
    @staticmethod
    def get_logger(name: str):
        """
        Get a logger instance with context.
        
        Args:
            name: Name/context for the logger (usually __name__)
            
        Returns:
            Configured logger instance
        """
        return logger.bind(context=name)


# Global logger configuration
_logger_config = None


def setup_logging(log_dir: Optional[str] = None) -> None:
    """
    Setup logging configuration for the entire application.
    
    Args:
        log_dir: Directory for log files. Defaults to logs/ in project root.
    """
    global _logger_config
    if _logger_config is None:
        _logger_config = LoggerConfig(log_dir)


def get_logger(name: str = __name__):
    """
    Get a logger instance.
    
    Args:
        name: Logger name/context (usually __name__)
        
    Returns:
        Configured logger instance
    """
    # Ensure logging is setup
    if _logger_config is None:
        setup_logging()
    
    return logger.bind(context=name)


# Additional convenience functions for specific log types
def log_operation_start(operation: str, **kwargs):
    """Log the start of an operation with context."""
    logger.info("🚀 Starting operation: {}", operation, extra={"operation": operation, **kwargs})


def log_operation_success(operation: str, duration: float = None, **kwargs):
    """Log successful completion of an operation."""
    if duration is not None:
        logger.info("✅ Operation completed successfully: {} in {:.2f}s", operation, duration,
                    extra={"operation": operation, "duration": duration, **kwargs})
    else:
        logger.info("✅ Operation completed successfully: {}", operation,
                    extra={"operation": operation, **kwargs})


def log_operation_error(operation: str, error: Exception, **kwargs):
    """Log operation error with full context."""
    logger.error("❌ Operation failed: {} - {}: {}", operation, type(error).__name__, str(error), 
                 extra={"operation": operation, "error_type": type(error).__name__, 
                        "error_message": str(error), **kwargs})


def log_malfunction(component: str, issue: str, severity: str = "ERROR", **kwargs):
    """Log system malfunctions with detailed context for easy debugging."""
    severity_emoji = {"DEBUG": "🔍", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "🚨", "CRITICAL": "💥"}
    emoji = severity_emoji.get(severity.upper(), "🔍")
    
    log_func = getattr(logger, severity.lower())
    log_func("{} MALFUNCTION DETECTED in {}: {}", emoji, component, issue,
             extra={"component": component, "malfunction": issue, "severity": severity, **kwargs})


def log_performance(operation: str, duration: float, threshold: float = None, **kwargs):
    """Log performance metrics."""
    if threshold and duration > threshold:
        logger.warning("⏱️ Performance warning: {} took {:.2f}s (threshold: {:.2f}s)", 
                      operation, duration, threshold,
                      extra={"operation": operation, "duration": duration, "threshold": threshold, **kwargs})
    else:
        logger.debug("⏱️ Performance: {} took {:.2f}s", operation, duration,
                    extra={"operation": operation, "duration": duration, **kwargs})


def log_config_change(key: str, old_value, new_value, **kwargs):
    """Log configuration changes."""
    logger.info("🔧 Configuration changed: {} = {} → {}", key, old_value, new_value,
                extra={"config_key": key, "old_value": old_value, "new_value": new_value, **kwargs})


def log_audio_event(event: str, details: dict = None):
    """Log audio-related events."""
    if details:
        logger.info("🎤 Audio event: {} - {}", event, details, extra={"audio_event": event, "details": details})
    else:
        logger.info("🎤 Audio event: {}", event, extra={"audio_event": event})


def log_stt_event(event: str, text: str = None, confidence: float = None, **kwargs):
    """Log speech-to-text events."""
    text_preview = text[:50] + "..." if text and len(text) > 50 else text if text else ""
    
    if confidence is not None:
        logger.info("🗣️ STT event: {} (confidence: {:.2f}) - '{}'", event, confidence, text_preview,
                    extra={"stt_event": event, "text": text, "confidence": confidence, **kwargs})
    else:
        logger.info("🗣️ STT event: {} - '{}'", event, text_preview,
                    extra={"stt_event": event, "text": text, **kwargs})