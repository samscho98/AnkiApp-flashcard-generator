"""
GUI Helper Functions
Common utility functions for GUI operations
"""

import tkinter as tk
from tkinter import ttk
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GUIHelpers:
    """Collection of GUI utility functions"""
    
    @staticmethod
    def center_window(window: tk.Toplevel, parent: Optional[tk.Tk] = None):
        """Center a window on screen or on parent window"""
        window.update_idletasks()
        
        if parent:
            # Center on parent
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            x = parent_x + (parent_width // 2) - (window.winfo_width() // 2)
            y = parent_y + (parent_height // 2) - (window.winfo_height() // 2)
        else:
            # Center on screen
            x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
            y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        
        window.geometry(f"+{x}+{y}")
    
    @staticmethod
    def create_tooltip(widget, text: str):
        """Create a simple tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip, 
                text=text, 
                background='#ffffe0',
                borderwidth=1, 
                relief='solid', 
                font=('Arial', 8),
                padx=5,
                pady=2
            )
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    @staticmethod
    def validate_number_entry(char: str) -> bool:
        """Validation function for number-only entries"""
        return char.isdigit() or char in '.-'
    
    @staticmethod
    def get_text_dimensions(text: str, font: tuple = ('Arial', 10)) -> Tuple[int, int]:
        """Get approximate text dimensions in pixels"""
        # Create temporary widget to measure text
        temp_label = tk.Label(font=font, text=text)
        temp_label.update_idletasks()
        width = temp_label.winfo_reqwidth()
        height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        return width, height
    
    @staticmethod
    def bind_mousewheel(widget, canvas):
        """Bind mousewheel scrolling to a canvas"""
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        widget.bind("<MouseWheel>", on_mousewheel)  # Windows
        widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
    
    @staticmethod
    def create_separator(parent, orientation='horizontal', **kwargs):
        """Create a visual separator"""
        if orientation == 'horizontal':
            sep = ttk.Separator(parent, orient=tk.HORIZONTAL, **kwargs)
        else:
            sep = ttk.Separator(parent, orient=tk.VERTICAL, **kwargs)
        return sep
    
    @staticmethod
    def ask_yes_no(parent, title: str, message: str) -> bool:
        """Show a yes/no dialog and return result"""
        import tkinter.messagebox as messagebox
        return messagebox.askyesno(title, message, parent=parent)
    
    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show an info dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo(title, message, parent=parent)
    
    @staticmethod
    def show_warning(parent, title: str, message: str):
        """Show a warning dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showwarning(title, message, parent=parent)
    
    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show an error dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showerror(title, message, parent=parent)
    
    @staticmethod
    def configure_grid_weights(widget, rows=None, columns=None):
        """Configure grid row and column weights"""
        if rows:
            for row, weight in rows.items():
                widget.grid_rowconfigure(row, weight=weight)
        
        if columns:
            for col, weight in columns.items():
                widget.grid_columnconfigure(col, weight=weight)
    
    @staticmethod
    def create_labeled_frame(parent, title: str, **kwargs):
        """Create a labeled frame with consistent styling"""
        frame = ttk.LabelFrame(parent, text=title, padding="10", **kwargs)
        return frame
    
    @staticmethod
    def safe_destroy(widget):
        """Safely destroy a widget"""
        try:
            if widget and widget.winfo_exists():
                widget.destroy()
        except tk.TclError:
            pass  # Widget already destroyed