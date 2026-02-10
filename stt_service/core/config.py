"""Configuration management for STT service."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for the STT service."""
    
    DEFAULT_CONFIG = {
        'service': {
            'language': 'en',
            'audio_device': 'default',
        },
        'input': {
            'method': 'hotkey',
            'hotkey': 'ctrl+shift+space',
        },
        'output': {
            'method': 'keyboard',  # keyboard, clipboard, both
        },
        'model': {
            'type': 'whisper',
            'path': 'models/whisper-base',
        },
        'audio': {
            'sample_rate': 16000,
            'channels': 1,
            'max_duration': 30,
            'format': 'int16',
        },
        'logging': {
            'level': 'INFO',
            'file': None,
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses defaults.
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            # Try to load from default locations
            default_paths = [
                'config.yaml',
                os.path.expanduser('~/.config/stt-service/config.yaml'),
                '/etc/stt-service/config.yaml',
            ]
            for path in default_paths:
                if os.path.exists(path):
                    self.load_config(path)
                    break
    
    def load_config(self, path: str) -> None:
        """Load configuration from YAML file.
        
        Args:
            path: Path to YAML configuration file
        """
        with open(path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                self._deep_update(self.config, user_config)
    
    def _deep_update(self, base: Dict, update: Dict) -> None:
        """Recursively update nested dictionaries.
        
        Args:
            base: Base dictionary to update
            update: Dictionary with updates
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'service.language')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'service.language')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: str) -> None:
        """Save current configuration to file.
        
        Args:
            path: Path to save configuration file
        """
        dir_path = os.path.dirname(path)
        if dir_path:  # Only create directory if path is not empty
            os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
