#!/usr/bin/env python3
"""Command-line interface for STT service."""

import argparse
import sys
import logging
from pathlib import Path

from stt_service.core.config import Config
from stt_service.service import STTService

logger = logging.getLogger(__name__)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Self-hosted Speech-to-Text Service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                        # Run with default config
  %(prog)s run -c config.yaml         # Run with custom config
  %(prog)s config                     # Show current configuration
  %(prog)s config --create            # Create example config file
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the STT service')
    run_parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file'
    )
    run_parser.add_argument(
        '-l', '--language',
        type=str,
        choices=['en', 'es', 'ca'],
        help='Override language setting (en, es, ca)'
    )
    run_parser.add_argument(
        '-m', '--model',
        type=str,
        help='Override model path/name'
    )
    run_parser.add_argument(
        '-o', '--output',
        type=str,
        choices=['keyboard', 'clipboard', 'both'],
        help='Override output method'
    )
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument(
        '--create',
        action='store_true',
        help='Create example configuration file'
    )
    config_parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    config_parser.add_argument(
        '-o', '--output',
        type=str,
        default='config.yaml',
        help='Output file for created config (default: config.yaml)'
    )
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test components')
    test_parser.add_argument(
        'component',
        nargs='?',
        choices=['audio', 'keyboard', 'clipboard', 'all'],
        default='all',
        help='Component to test'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Execute command
    if args.command == 'run':
        run_service(args)
    elif args.command == 'config':
        manage_config(args)
    elif args.command == 'test':
        test_components(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_service(args):
    """Run the STT service.
    
    Args:
        args: Parsed command-line arguments
    """
    try:
        # Load configuration
        config = Config(args.config if hasattr(args, 'config') else None)
        
        # Apply command-line overrides
        if hasattr(args, 'language') and args.language:
            config.set('service.language', args.language)
        
        if hasattr(args, 'model') and args.model:
            config.set('model.path', args.model)
        
        if hasattr(args, 'output') and args.output:
            config.set('output.method', args.output)
        
        # Create and run service
        service = STTService(config)
        service.run()
        
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to run service: {e}")
        sys.exit(1)


def manage_config(args):
    """Manage configuration.
    
    Args:
        args: Parsed command-line arguments
    """
    if args.create:
        create_example_config(args.output)
    elif args.show:
        show_config()
    else:
        create_example_config(args.output)


def create_example_config(output_path: str):
    """Create example configuration file.
    
    Args:
        output_path: Path to save configuration file
    """
    config = Config()
    
    try:
        config.save(output_path)
        print(f"Example configuration created: {output_path}")
        print("\nEdit this file and run: stt-service run -c {output_path}")
    except Exception as e:
        logger.error(f"Failed to create config file: {e}")
        sys.exit(1)


def show_config():
    """Show current configuration."""
    config = Config()
    
    print("Current Configuration:")
    print("=" * 50)
    
    import yaml
    print(yaml.dump(config.config, default_flow_style=False))


def test_components(args):
    """Test service components.
    
    Args:
        args: Parsed command-line arguments
    """
    component = args.component
    
    print(f"Testing {component}...")
    print("=" * 50)
    
    if component in ['audio', 'all']:
        test_audio()
    
    if component in ['keyboard', 'all']:
        test_keyboard()
    
    if component in ['clipboard', 'all']:
        test_clipboard()


def test_audio():
    """Test audio capture."""
    print("\n[Audio Test]")
    try:
        from stt_service.core.audio_capture import AudioCapture
        
        capture = AudioCapture()
        if capture.available:
            print("✓ Audio capture available")
            print("  - sounddevice library is installed")
        else:
            print("✗ Audio capture NOT available")
            print("  - Install with: pip install sounddevice")
    except Exception as e:
        print(f"✗ Audio test failed: {e}")


def test_keyboard():
    """Test keyboard output."""
    print("\n[Keyboard Test]")
    try:
        from stt_service.output.keyboard import KeyboardHandler
        
        handler = KeyboardHandler()
        if handler.is_available():
            print("✓ Keyboard output available")
            print("  - pynput library is installed")
        else:
            print("✗ Keyboard output NOT available")
            print("  - Install with: pip install pynput")
    except Exception as e:
        print(f"✗ Keyboard test failed: {e}")


def test_clipboard():
    """Test clipboard output."""
    print("\n[Clipboard Test]")
    try:
        from stt_service.output.keyboard import ClipboardHandler
        
        handler = ClipboardHandler()
        if handler.is_available():
            print("✓ Clipboard output available")
            print("  - pyperclip library is installed")
        else:
            print("✗ Clipboard output NOT available")
            print("  - Install with: pip install pyperclip")
    except Exception as e:
        print(f"✗ Clipboard test failed: {e}")


if __name__ == '__main__':
    main()
