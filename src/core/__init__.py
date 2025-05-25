"""
Core Package for Language Learning Flashcard Generator
Contains data management, CSV generation, and content processing systems
"""

# Import existing modules
from .history_manager import HistoryManager

# Import CSV generation system
try:
    from .csv_generator import (
        GenericLanguageCSVGenerator, 
        AnkiAppFormatter,
        GenericContentEntry
    )
    CSV_GENERATOR_AVAILABLE = True
except ImportError:
    GenericLanguageCSVGenerator = None
    AnkiAppFormatter = None
    GenericContentEntry = None
    CSV_GENERATOR_AVAILABLE = False

# Import data management
try:
    from .data_manager import DataManager, ContentLoader
    DATA_MANAGER_AVAILABLE = True
except ImportError:
    DataManager = None
    ContentLoader = None
    DATA_MANAGER_AVAILABLE = False

# Import card formatting
try:
    from .card_formatter import CardFormatter, HTMLCardFormatter
    CARD_FORMATTER_AVAILABLE = True
except ImportError:
    CardFormatter = None
    HTMLCardFormatter = None
    CARD_FORMATTER_AVAILABLE = False

__all__ = [
    'HistoryManager',
    'GenericLanguageCSVGenerator', 
    'AnkiAppFormatter',
    'GenericContentEntry',
    'DataManager',
    'ContentLoader',
    'CardFormatter',
    'HTMLCardFormatter',
    'CSV_GENERATOR_AVAILABLE',
    'DATA_MANAGER_AVAILABLE',
    'CARD_FORMATTER_AVAILABLE'
]