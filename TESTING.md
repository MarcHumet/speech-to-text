# Test Execution Guide

This document explains how to run tests for the STT Service project.

## Project Structure

```
/home/marc/project/speech-to-text/
├── cli.py                          # Main CLI interface (kept in root)
├── setup.py                        # Package setup (kept in root)  
├── scripts/
│   └── demo.py                     # Demo script (moved from root)
├── stt_service/
│   ├── __init__.py
│   ├── service.py                  # Main service
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── audio_capture.py
│   │   └── engine.py
│   ├── input/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── hotkey.py
│   ├── output/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── keyboard.py
│   └── tests/                      # NEW: Comprehensive test suite
│       ├── __init__.py
│       ├── run_tests.py            # Test runner
│       ├── test_service.py         # Main service tests
│       ├── test_integration.py     # Integration tests
│       ├── core/
│       │   ├── __init__.py
│       │   ├── test_config.py
│       │   ├── test_audio_capture.py
│       │   └── test_engine.py
│       ├── input/
│       │   ├── __init__.py
│       │   ├── test_base.py
│       │   └── test_hotkey.py
│       └── output/
│           ├── __init__.py
│           ├── test_base.py
│           └── test_keyboard.py
└── pytest.ini                     # Pytest configuration
```

## Running Tests

### Prerequisites

Make sure pytest is installed:
```bash
uv add pytest pytest-cov --group dev
```

### Run All Tests

```bash
# Run all tests with pytest
uv run python -m pytest stt_service/tests/ -v

# Run with coverage
uv run python -m pytest stt_service/tests/ --cov=stt_service --cov-report=html

# Run specific test modules
uv run python -m pytest stt_service/tests/core/test_config.py -v
```

### Run Tests with Custom Runner

```bash
# Run all tests
uv run python stt_service/tests/run_tests.py

# Run specific module tests
uv run python stt_service/tests/run_tests.py core.test_config
```

### Run Demo Script

```bash
# Test component functionality
uv run python scripts/demo.py
```

### Run CLI

```bash
# Test CLI interface
uv run python cli.py --help
uv run python cli.py config --create
```

## Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component workflow testing
- **Mock Tests**: Tests using mocked dependencies for components requiring hardware

## File Organization Changes Made

1. ✅ **demo.py** moved to `scripts/` directory
2. ✅ **cli.py** and **setup.py** kept in root (standard practice)
3. ✅ Created comprehensive test structure under `stt_service/tests/`
4. ✅ Added pytest configuration
5. ✅ Updated demo.py with proper import paths
6. ✅ Enhanced setup.py with test dependencies

## Verification

All changes maintain backward compatibility:
- ✅ CLI still works: `uv run python cli.py --help`
- ✅ Demo script still works: `uv run python scripts/demo.py`
- ✅ Service imports work correctly
- ✅ Tests pass: 9/9 config tests passing
- ✅ Module structure is clean and organized