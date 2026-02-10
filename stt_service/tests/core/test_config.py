"""Tests for config module."""

import unittest
import tempfile
import os
import shutil
from pathlib import Path

from stt_service.core.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.yaml')

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        # Test default values
        self.assertEqual(config.get('service.language'), 'en')
        self.assertEqual(config.get('input.method'), 'hotkey')
        self.assertEqual(config.get('output.method'), 'keyboard')
        self.assertEqual(config.get('audio.sample_rate'), 16000)

    def test_config_file_loading(self):
        """Test loading configuration from file."""
        # Create a test config file
        test_config = """
service:
  language: es
  audio_device: "microphone_1"
input:
  method: "hotkey"
  hotkey: "ctrl+space"
output:
  method: "clipboard"
"""
        with open(self.config_file, 'w') as f:
            f.write(test_config)

        config = Config(self.config_file)
        
        self.assertEqual(config.get('service.language'), 'es')
        self.assertEqual(config.get('service.audio_device'), 'microphone_1')
        self.assertEqual(config.get('input.hotkey'), 'ctrl+space')
        self.assertEqual(config.get('output.method'), 'clipboard')

    def test_config_get_with_default(self):
        """Test getting configuration values with defaults."""
        config = Config()
        
        # Test existing key
        self.assertEqual(config.get('service.language'), 'en')
        
        # Test non-existing key with default
        self.assertEqual(config.get('non.existing.key', 'default_value'), 'default_value')
        
        # Test non-existing key without default
        self.assertIsNone(config.get('non.existing.key'))

    def test_config_set(self):
        """Test setting configuration values."""
        config = Config()
        
        # Set existing key
        config.set('service.language', 'ca')
        self.assertEqual(config.get('service.language'), 'ca')
        
        # Set new nested key
        config.set('new.nested.key', 'test_value')
        self.assertEqual(config.get('new.nested.key'), 'test_value')

    def test_config_save_and_load(self):
        """Test saving and loading configuration."""
        config = Config()
        
        # Modify configuration
        config.set('service.language', 'es')
        config.set('custom.setting', 'test_value')
        
        # Save to file
        config.save(self.config_file)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load new config from saved file
        new_config = Config(self.config_file)
        self.assertEqual(new_config.get('service.language'), 'es')
        self.assertEqual(new_config.get('custom.setting'), 'test_value')

    def test_deep_config_update(self):
        """Test deep updating of nested configuration."""
        config = Config()
        
        # Create a test config file with nested updates
        test_config = """
service:
  language: es
audio:
  sample_rate: 22050
  new_setting: true
"""
        with open(self.config_file, 'w') as f:
            f.write(test_config)

        config.load_config(self.config_file)
        
        # Should update existing values
        self.assertEqual(config.get('service.language'), 'es')
        self.assertEqual(config.get('audio.sample_rate'), 22050)
        
        # Should preserve existing values not in update
        self.assertEqual(config.get('audio.channels'), 1)
        
        # Should add new values
        self.assertTrue(config.get('audio.new_setting'))

    def test_config_with_missing_file(self):
        """Test configuration initialization with missing file."""
        non_existent_file = os.path.join(self.temp_dir, 'missing.yaml')
        
        # Should not raise error and use defaults
        config = Config(non_existent_file)
        self.assertEqual(config.get('service.language'), 'en')

    def test_config_directory_creation(self):
        """Test automatic directory creation when saving config."""
        nested_path = os.path.join(self.temp_dir, 'nested', 'directory', 'config.yaml')
        config = Config()
        
        config.save(nested_path)
        
        self.assertTrue(os.path.exists(nested_path))
        self.assertTrue(os.path.isfile(nested_path))

    def test_config_malformed_yaml(self):
        """Test handling of malformed YAML files."""
        # Create malformed YAML
        malformed_yaml = """
service:
  language: en
    invalid_indentation: value
"""
        with open(self.config_file, 'w') as f:
            f.write(malformed_yaml)
        
        # Should handle malformed YAML gracefully
        with self.assertRaises(Exception):
            Config(self.config_file)


if __name__ == '__main__':
    unittest.main()