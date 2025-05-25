"""
Status Bar Component
Bottom status bar for application messages
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StatusBar(ttk.Frame):
    """Status bar widget for showing application status and messages"""
    
    def __init__(self, parent):
        super().__init__(parent, relief=tk.SUNKEN, borderwidth=1, padding="2")
        
        self._setup_ui()
        self.set_message("Ready")
    
    def _setup_ui(self):
        """Setup the status bar UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Status message (left side)
        self.message_var = tk.StringVar(value="Ready")
        self.message_label = ttk.Label(
            self, 
            textvariable=self.message_var,
            font=('Arial', 9)
        )
        self.message_label.grid(row=0, column=0, sticky=tk.W, padx=(5, 0))
        
        # Spacer
        spacer = ttk.Frame(self)
        spacer.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Time/info (right side)
        self.info_var = tk.StringVar(value="")
        self.info_label = ttk.Label(
            self, 
            textvariable=self.info_var,
            font=('Arial', 8),
            foreground='gray'
        )
        self.info_label.grid(row=0, column=2, sticky=tk.E, padx=(0, 5))
        
        # Update time periodically
        self._update_time()
    
    def set_message(self, message: str):
        """Set the main status message"""
        self.message_var.set(message)
        logger.debug(f"Status: {message}")
    
    def set_info(self, info: str):
        """Set the info text (right side)"""
        self.info_var.set(info)
    
    def show_temporary_message(self, message: str, duration: int = 3000):
        """Show a temporary message that reverts after duration (ms)"""
        original_message = self.message_var.get()
        self.set_message(message)
        
        # Revert after duration
        self.after(duration, lambda: self.set_message(original_message))
    
    def _update_time(self):
        """Update the time display"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            self.set_info(current_time)
        except Exception as e:
            logger.debug(f"Error updating time: {e}")
        
        # Schedule next update (every minute)
        self.after(60000, self._update_time)
    
    def clear(self):
        """Clear status bar"""
        self.set_message("Ready")
        self.set_info("")