"""
Progress Display Component
Shows learning progress and statistics
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)


class ProgressDisplay(ttk.LabelFrame):
    """Widget for displaying learning progress and statistics"""
    
    def __init__(self, parent, history_manager):
        super().__init__(parent, text="Progress", padding="5")
        
        self.history_manager = history_manager
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Setup the progress display UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Progress text
        self.progress_text = tk.StringVar(value="Loading progress...")
        self.progress_label = ttk.Label(
            self, 
            textvariable=self.progress_text, 
            font=('Arial', 9)
        )
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
    
    def refresh(self):
        """Refresh progress display"""
        try:
            if not self.history_manager:
                self.progress_text.set("Progress tracking unavailable")
                return
            
            summary = self.history_manager.get_progress_summary()
            today_progress = self.history_manager.get_today_progress()
            
            # Format progress text
            progress_parts = []
            
            # Total learning stats
            total_items = summary.get('total_items_learned', 0)
            total_hours = summary.get('total_study_time_hours', 0)
            progress_parts.append(f"Total learned: {total_items} items")
            
            if total_hours > 0:
                progress_parts.append(f"Study time: {total_hours:.1f}h")
            
            # Today's progress
            today_items = today_progress.get('items_learned', 0)
            if today_items > 0:
                progress_parts.append(f"Today: {today_items} items")
            
            # Study streak
            streak = summary.get('study_streak', 0)
            if streak > 0:
                progress_parts.append(f"Streak: {streak} days")
            
            progress_text = " | ".join(progress_parts) if progress_parts else "No progress yet"
            self.progress_text.set(progress_text)
            
        except Exception as e:
            logger.error(f"Error refreshing progress display: {e}")
            self.progress_text.set("Progress unavailable")