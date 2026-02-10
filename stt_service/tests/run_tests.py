"""Test runner for STT Service tests."""

import unittest
import sys
import os

# Add the parent directory to the path so we can import stt_service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all tests in the tests directory."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_module_tests(module_name):
    """Run tests for a specific module."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Import and add specific test module
    test_module = __import__(f'stt_service.tests.{module_name}', fromlist=[''])
    suite.addTests(loader.loadTestsFromModule(test_module))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific module tests
        module = sys.argv[1]
        print(f"Running tests for {module}...")
        success = run_specific_module_tests(module)
    else:
        # Run all tests
        print("Running all STT Service tests...")
        success = run_all_tests()
    
    sys.exit(0 if success else 1)