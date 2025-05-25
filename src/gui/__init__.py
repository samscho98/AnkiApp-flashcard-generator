"""
GUI Package for Language Learning Flashcard Generator
Contains tkinter-based user interface components
"""

# Import main window and components
try:
    from .main_window import MainWindow, LanguageLearningApp
    MAIN_WINDOW_AVAILABLE = True
except ImportError:
    MainWindow = None
    LanguageLearningApp = None
    MAIN_WINDOW_AVAILABLE = False

# Import custom widgets
try:
    from .widgets import (
        FileSelector,
        ContentPreview,
        ExportPanel,
        ProgressDisplay,
        SettingsPanel
    )
    WIDGETS_AVAILABLE = True
except ImportError:
    FileSelector = None
    ContentPreview = None
    ExportPanel = None
    ProgressDisplay = None
    SettingsPanel = None
    WIDGETS_AVAILABLE = False

# Import settings window
try:
    from .settings_window import SettingsWindow, PreferencesDialog
    SETTINGS_WINDOW_AVAILABLE = True
except ImportError:
    SettingsWindow = None
    PreferencesDialog = None
    SETTINGS_WINDOW_AVAILABLE = False

__all__ = [
    'MainWindow',
    'LanguageLearningApp',
    'FileSelector',
    'ContentPreview',
    'ExportPanel',
    'ProgressDisplay',
    'SettingsPanel',
    'SettingsWindow',
    'PreferencesDialog',
    'MAIN_WINDOW_AVAILABLE',
    'WIDGETS_AVAILABLE',
    'SETTINGS_WINDOW_AVAILABLE'
]
