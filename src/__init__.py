"""
Generic Language Learning Flashcard Generator
Main package for creating AnkiApp-compatible flashcards from JSON data
"""

__version__ = "0.1.0"
__author__ = "Sam Schonenberg"
__description__ = "Generic flashcard generator for language learning with AnkiApp"

# Import main components for easy access
from .core import (
    HistoryManager,
    GenericLanguageCSVGenerator, 
    AnkiAppFormatter,
    GenericContentEntry
)

from .config import SettingsManager
from .utils import FileManager, JSONFileManager, ValidationRunner

__all__ = [
    'HistoryManager',
    'GenericLanguageCSVGenerator', 
    'AnkiAppFormatter',
    'GenericContentEntry',
    'SettingsManager',
    'FileManager',
    'JSONFileManager',
    'ValidationRunner'
]