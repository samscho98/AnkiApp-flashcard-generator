"""
GUI Package for Language Learning Flashcard Generator
Refactored into focused, maintainable components
"""

# Import main application class
from .app import LanguageLearningApp

# Import main window
from .main_window import MainWindow

# Import components
from .components import (
    FileSelector,
    ContentSelector, 
    CSVPreviewEditor,
    ExportPanel,
    ProgressDisplay,
    StatusBar
)

# Import dialogs
from .dialogs import (
    SettingsDialog,
    ErrorDialog,
    ExportDialog,
    AboutDialog
)

# Import utilities
from .utils import (
    GUIHelpers,
    ThemeManager,
    LayoutHelpers
)

# Main entry point
def main():
    """Main entry point for the GUI application"""
    app = LanguageLearningApp()
    app.run()

__all__ = [
    # Main classes
    'LanguageLearningApp',
    'MainWindow',
    
    # Components
    'FileSelector',
    'ContentSelector', 
    'CSVPreviewEditor',
    'ExportPanel',
    'ProgressDisplay',
    'StatusBar',
    
    # Dialogs
    'SettingsDialog',
    'ErrorDialog',
    'ExportDialog',
    'AboutDialog',
    
    # Utilities
    'GUIHelpers',
    'ThemeManager',
    'LayoutHelpers',
    
    # Entry point
    'main'
]