"""
About Dialog
Information about the application, version, and credits
"""

import os
import tkinter as tk
from tkinter import ttk
import webbrowser
from typing import Optional
import logging

from ..utils import GUIHelpers

logger = logging.getLogger(__name__)


class AboutDialog:
    """About application dialog"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
    
    def show(self):
        """Show the about dialog"""
        if self.dialog is not None:
            self.dialog.lift()
            self.dialog.focus_force()
            return
        
        self._create_dialog()
        GUIHelpers.center_window(self.dialog, self.parent)
        self.dialog.focus_set()
    
    def _create_dialog(self):
        """Create the about dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("About")
        self.dialog.geometry("450x500")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # App icon/logo (text-based)
        icon_frame = ttk.Frame(main_frame)
        icon_frame.grid(row=0, column=0, pady=(0, 20))
        
        icon_label = ttk.Label(
            icon_frame,
            text="📚",
            font=('Arial', 48)
        )
        icon_label.pack()
        
        # App name and version
        app_label = ttk.Label(
            main_frame,
            text="Language Learning Flashcard Generator",
            font=('Arial', 14, 'bold')
        )
        app_label.grid(row=1, column=0, pady=(0, 5))
        
        # Version
        try:
            from __version__ import __version__
            version_text = f"Version {__version__}"
        except ImportError:
            version_text = "Version 1.0.0"
        
        version_label = ttk.Label(
            main_frame,
            text=version_text,
            font=('Arial', 11)
        )
        version_label.grid(row=2, column=0, pady=(0, 20))
        
        # Description
        description = """A powerful tool for converting JSON vocabulary data into 
AnkiApp-compatible CSV files for language learning.

Perfect for creating flashcards with:
• Rich HTML formatting
• Language connections
• Example sentences
• Progress tracking"""
        
        desc_label = ttk.Label(
            main_frame,
            text=description,
            font=('Arial', 10),
            justify=tk.CENTER,
            wraplength=350
        )
        desc_label.grid(row=3, column=0, pady=(0, 25))
        
        # Features section
        features_frame = ttk.LabelFrame(main_frame, text="Key Features", padding="15")
        features_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        features_frame.columnconfigure(0, weight=1)
        
        features = [
            "✅ Universal language support",
            "✅ Multiple export formats (AnkiApp, Anki, Quizlet)",
            "✅ Editable CSV preview",
            "✅ Language connections (Dutch → German)",
            "✅ Progress tracking and statistics",
            "✅ Customizable themes and settings"
        ]
        
        for i, feature in enumerate(features):
            feature_label = ttk.Label(
                features_frame,
                text=feature,
                font=('Arial', 9),
                anchor=tk.W
            )
            feature_label.grid(row=i, column=0, sticky=tk.W, pady=1)
        
        # Credits section
        credits_frame = ttk.LabelFrame(main_frame, text="Credits", padding="10")
        credits_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        credits_text = """Created for language learners worldwide
        
Special thanks to:
• AnkiApp team for excellent spaced repetition
• Python tkinter community
• Language learning enthusiasts"""
        
        credits_label = ttk.Label(
            credits_frame,
            text=credits_text,
            font=('Arial', 9),
            justify=tk.CENTER,
            foreground='gray'
        )
        credits_label.pack()
        
        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.grid(row=6, column=0, pady=(0, 20))
        
        # GitHub link (if you have one)
        github_button = ttk.Button(
            links_frame,
            text="🔗 GitHub Repository",
            command=self._open_github,
            width=20
        )
        github_button.pack(side=tk.LEFT, padx=5)
        
        # Documentation link
        docs_button = ttk.Button(
            links_frame,
            text="📖 Documentation",
            command=self._open_docs,
            width=20
        )
        docs_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self._close_dialog,
            width=15,
            default='active'
        )
        close_button.grid(row=7, column=0, pady=(10, 0))
        
        # Bind Enter and Escape
        self.dialog.bind('<Return>', lambda e: self._close_dialog())
        self.dialog.bind('<Escape>', lambda e: self._close_dialog())
    
    def _open_github(self):
        """Open GitHub repository in browser"""
        try:
            webbrowser.open("https://github.com/samscho98/AnkiApp-flashcard-generator")
        except Exception as e:
            logger.warning(f"Failed to open GitHub link: {e}")
    
    def _open_docs(self):
        """Open documentation in browser"""
        try:
            webbrowser.open("https://github.com/samscho98/AnkiApp-flashcard-generator#readme")
        except Exception as e:
            logger.warning(f"Failed to open documentation link: {e}")
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None


class SystemInfoDialog:
    """System information dialog for troubleshooting"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
    
    def show(self):
        """Show system information dialog"""
        if self.dialog is not None:
            self.dialog.lift()
            self.dialog.focus_force()
            return
        
        self._create_dialog()
        GUIHelpers.center_window(self.dialog, self.parent)
        self.dialog.focus_set()
    
    def _create_dialog(self):
        """Create system info dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("System Information")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="System Information",
            font=('Arial', 12, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 15))
        
        # Info text area
        from tkinter import scrolledtext
        
        self.info_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            height=20,
            state=tk.DISABLED
        )
        self.info_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Load system information
        self._load_system_info()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=tk.E)
        
        copy_button = ttk.Button(
            button_frame,
            text="Copy to Clipboard",
            command=self._copy_info,
            width=15
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self._close_dialog,
            width=10,
            default='active'
        )
        close_button.pack(side=tk.LEFT)
        
        # Bind keys
        self.dialog.bind('<Escape>', lambda e: self._close_dialog())
    
    def _load_system_info(self):
        """Load and display system information"""
        import sys
        import platform
        from pathlib import Path
        
        info_lines = []
        
        # Application info
        info_lines.append("=== APPLICATION INFORMATION ===")
        try:
            from __version__ import __version__, APP_NAME
            info_lines.append(f"Application: {APP_NAME}")
            info_lines.append(f"Version: {__version__}")
        except ImportError:
            info_lines.append("Application: Language Learning Flashcard Generator")
            info_lines.append("Version: 1.0.0")
        
        info_lines.append("")
        
        # Python info
        info_lines.append("=== PYTHON INFORMATION ===")
        info_lines.append(f"Python Version: {sys.version}")
        info_lines.append(f"Python Executable: {sys.executable}")
        info_lines.append(f"Platform: {platform.platform()}")
        info_lines.append(f"Architecture: {platform.machine()}")
        info_lines.append("")
        
        # System info
        info_lines.append("=== SYSTEM INFORMATION ===")
        info_lines.append(f"Operating System: {platform.system()} {platform.release()}")
        info_lines.append(f"Processor: {platform.processor()}")
        info_lines.append("")
        
        # Tkinter info
        info_lines.append("=== TKINTER INFORMATION ===")
        info_lines.append(f"Tkinter Version: {tk.TkVersion}")
        info_lines.append(f"Tcl Version: {tk.TclVersion}")
        info_lines.append("")
        
        # Path info
        info_lines.append("=== PATH INFORMATION ===")
        info_lines.append(f"Current Working Directory: {Path.cwd()}")
        info_lines.append(f"Script Directory: {Path(__file__).parent.parent.parent}")
        info_lines.append("")
        
        # Module info
        info_lines.append("=== IMPORTED MODULES ===")
        relevant_modules = ['tkinter', 'json', 'csv', 'pathlib', 'logging']
        for module_name in relevant_modules:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, '__file__'):
                    info_lines.append(f"{module_name}: {module.__file__}")
                else:
                    info_lines.append(f"{module_name}: (built-in)")
            else:
                info_lines.append(f"{module_name}: Not imported")
        
        info_lines.append("")
        
        # Environment variables (selected)
        info_lines.append("=== RELEVANT ENVIRONMENT VARIABLES ===")
        env_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER', 'USERPROFILE']
        for var in env_vars:
            value = os.environ.get(var, 'Not set')
            if len(value) > 100:
                value = value[:97] + "..."
            info_lines.append(f"{var}: {value}")
        
        # Display in text widget
        info_text = "\n".join(info_lines)
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state=tk.DISABLED)
    
    def _copy_info(self):
        """Copy system info to clipboard"""
        try:
            info_text = self.info_text.get(1.0, tk.END)
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(info_text)
            
            # Show brief confirmation
            original_text = self.info_text.get(1.0, "1.end")
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, "1.end")
            self.info_text.insert(1.0, "✅ Copied to clipboard!")
            self.info_text.config(state=tk.DISABLED)
            
            # Restore original text after 2 seconds
            self.dialog.after(2000, lambda: self._restore_first_line(original_text))
            
        except Exception as e:
            logger.warning(f"Failed to copy to clipboard: {e}")
    
    def _restore_first_line(self, original_text: str):
        """Restore the first line after copy confirmation"""
        try:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, "1.end")
            self.info_text.insert(1.0, original_text)
            self.info_text.config(state=tk.DISABLED)
        except tk.TclError:
            pass  # Dialog was closed
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None


class KeyboardShortcutsDialog:
    """Dialog showing keyboard shortcuts"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
    
    def show(self):
        """Show keyboard shortcuts dialog"""
        if self.dialog is not None:
            self.dialog.lift()
            self.dialog.focus_force()
            return
        
        self._create_dialog()
        GUIHelpers.center_window(self.dialog, self.parent)
        self.dialog.focus_set()
    
    def _create_dialog(self):
        """Create keyboard shortcuts dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Keyboard Shortcuts")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Keyboard Shortcuts",
            font=('Arial', 12, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 15))
        
        # Shortcuts frame
        shortcuts_frame = ttk.Frame(main_frame)
        shortcuts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        shortcuts_frame.columnconfigure(1, weight=1)
        
        shortcuts = [
            ("Ctrl+S", "Save/Export current CSV"),
            ("Ctrl+O", "Open file browser"),
            ("F5", "Refresh data directory"),
            ("Ctrl+,", "Open Settings (future)"),
            ("F1", "Show Help (future)"),
            ("Escape", "Close dialogs"),
            ("Enter", "Confirm dialogs"),
            ("Tab", "Navigate between fields"),
            ("Ctrl+A", "Select all (in text areas)"),
            ("Ctrl+Z", "Undo (in CSV editor)"),
            ("Ctrl+Y", "Redo (in CSV editor)")
        ]
        
        for i, (shortcut, description) in enumerate(shortcuts):
            # Shortcut key
            shortcut_label = ttk.Label(
                shortcuts_frame,
                text=shortcut,
                font=('Consolas', 9, 'bold'),
                width=12,
                anchor=tk.W
            )
            shortcut_label.grid(row=i, column=0, sticky=tk.W, pady=2, padx=(0, 15))
            
            # Description
            desc_label = ttk.Label(
                shortcuts_frame,
                text=description,
                font=('Arial', 9),
                anchor=tk.W
            )
            desc_label.grid(row=i, column=1, sticky=tk.W, pady=2)
        
        # Close button
        close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self._close_dialog,
            width=10,
            default='active'
        )
        close_button.grid(row=2, column=0)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self._close_dialog())
        self.dialog.bind('<Escape>', lambda e: self._close_dialog())
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None