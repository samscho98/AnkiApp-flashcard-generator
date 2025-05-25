"""
Test Package for Language Learning Flashcard Generator
Contains unit tests, integration tests, and test utilities
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test discovery helpers
def discover_tests(test_directory=None):
    """
    Discover and return all tests in the test directory
    
    Args:
        test_directory: Directory to search for tests (default: current directory)
        
    Returns:
        TestSuite containing all discovered tests
    """
    if test_directory is None:
        test_directory = Path(__file__).parent
    
    loader = unittest.TestLoader()
    return loader.discover(str(test_directory), pattern='test_*.py')

def run_all_tests(verbosity=2):
    """
    Run all tests with specified verbosity
    
    Args:
        verbosity: Test output verbosity level (0-2)
        
    Returns:
        TestResult object
    """
    suite = discover_tests()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)

# Test categories
UNIT_TESTS = [
    'test_csv_generator',
    'test_history_manager', 
    'test_data_manager',
    'test_file_utils',
    'test_validation'
]

INTEGRATION_TESTS = [
    'test_full_workflow',
    'test_gui_integration'
]

__all__ = [
    'discover_tests',
    'run_all_tests',
    'UNIT_TESTS',
    'INTEGRATION_TESTS'
]