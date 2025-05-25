"""
Settings Window for Language Learning Flashcard Generator
Provides interface for configuring application settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings configuration window"""
    
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        self.window = None
    
    def show(self):
        """Show the settings window"""
        if self.window is not None:
            # Window already exists, just bring it to front
            self.window.lift()
            self.window.focus_force()
            return
        
        # Create new settings window
        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("400x300")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Setup UI
        self.setup_ui()
        
        # Center window on parent
        self.center_window()
    
    def setup_ui(self):
        """Setup the settings UI"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Placeholder content
        placeholder_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        placeholder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        ttk.Label(placeholder_frame, text="Settings will be implemented here.", 
                 font=('Arial', 10)).pack(pady=20)
        
        ttk.Label(placeholder_frame, text="Future settings may include:", 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(10, 5))
        
        settings_list = [
            "• Default export directory",
            "• Language preferences", 
            "• Card formatting options",
            "• Connection language settings",
            "• Study progress targets",
            "• Interface appearance"
        ]
        
        for item in settings_list:
            ttk.Label(placeholder_frame, text=item, font=('Arial', 8)).pack(anchor=tk.W, padx=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        # Close button
        ttk.Button(button_frame, text="Close", command=self.on_close).pack(side=tk.RIGHT)
    
    def center_window(self):
        """Center the settings window on the parent window"""
        self.window.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get settings window size
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        
        # Calculate center position
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        
        # Set window position
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def on_close(self):
        """Handle window close"""
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None


class PreferencesDialog:
    """Simple preferences dialog - placeholder for future use"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def show(self):
        """Show preferences dialog"""
        messagebox.showinfo("Preferences", "Preferences dialog will be implemented in a future version.")