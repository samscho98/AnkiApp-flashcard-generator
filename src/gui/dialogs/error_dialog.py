"""
Error Dialog
User-friendly error handling and display
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import traceback
from typing import Optional
import logging

from ..utils import GUIHelpers

logger = logging.getLogger(__name__)


class ErrorDialog:
    """Enhanced error dialog with details and logging"""
    
    @staticmethod
    def show_error(parent, title: str, message: str, details: Optional[str] = None):
        """Show error dialog with optional details"""
        dialog = ErrorDialog._create_dialog(parent, title, message, details, "error")
        dialog.focus_set()
    
    @staticmethod
    def show_warning(parent, title: str, message: str, details: Optional[str] = None):
        """Show warning dialog with optional details"""
        dialog = ErrorDialog._create_dialog(parent, title, message, details, "warning")
        dialog.focus_set()
    
    @staticmethod
    def show_info(parent, title: str, message: str, details: Optional[str] = None):
        """Show info dialog with optional details"""
        dialog = ErrorDialog._create_dialog(parent, title, message, details, "info")
        dialog.focus_set()
    
    @staticmethod
    def show_exception(parent, title: str, exception: Exception, context: str = None):
        """Show error dialog for an exception with full traceback"""
        message = f"{type(exception).__name__}: {str(exception)}"
        if context:
            message = f"{context}\n\n{message}"
        
        details = traceback.format_exc()
        
        # Log the exception
        logger.error(f"Exception in {context or 'application'}: {exception}", exc_info=True)
        
        dialog = ErrorDialog._create_dialog(parent, title, message, details, "error")
        dialog.focus_set()
    
    @staticmethod
    def _create_dialog(parent, title: str, message: str, details: Optional[str], 
                      dialog_type: str) -> tk.Toplevel:
        """Create the error dialog window"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("450x300" if details else "400x150")
        dialog.resizable(True, True)
        dialog.minsize(350, 120)
        
        # Make modal
        dialog.transient(parent)
        dialog.grab_set()
        
        # Configure grid
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Icon and message area
        icon_frame = ttk.Frame(main_frame)
        icon_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        icon_frame.columnconfigure(1, weight=1)
        
        # Icon (simple text representation)
        icon_text = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
        icon_label = ttk.Label(
            icon_frame, 
            text=icon_text.get(dialog_type, "❌"),
            font=('Arial', 16)
        )
        icon_label.grid(row=0, column=0, padx=(0, 15), sticky=tk.W)
        
        # Message
        message_label = ttk.Label(
            icon_frame,
            text=message,
            wraplength=350,
            justify=tk.LEFT,
            font=('Arial', 10)
        )
        message_label.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        
        # Details section (if provided)
        if details:
            # Separator
            separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
            separator.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
            
            # Details label
            details_label = ttk.Label(main_frame, text="Details:", font=('Arial', 9, 'bold'))
            details_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
            
            # Details text area
            details_frame = ttk.Frame(main_frame)
            details_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
            details_frame.columnconfigure(0, weight=1)
            details_frame.rowconfigure(0, weight=1)
            
            # Make main frame expandable when details are shown
            main_frame.rowconfigure(3, weight=1)
            
            details_text = scrolledtext.ScrolledText(
                details_frame,
                height=8,
                wrap=tk.WORD,
                font=('Consolas', 9),
                state=tk.DISABLED
            )
            details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Insert details
            details_text.config(state=tk.NORMAL)
            details_text.insert(tk.END, details)
            details_text.config(state=tk.DISABLED)
            
            # Copy button for details
            copy_button = ttk.Button(
                details_frame,
                text="Copy Details",
                command=lambda: ErrorDialog._copy_to_clipboard(dialog, details)
            )
            copy_button.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4 if details else 1, column=0, columnspan=2, sticky=tk.E)
        
        # OK button
        ok_button = ttk.Button(
            button_frame,
            text="OK",
            command=dialog.destroy,
            width=10,
            default='active'
        )
        ok_button.pack(side=tk.RIGHT)
        
        # Bind Enter and Escape keys
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Center on parent
        GUIHelpers.center_window(dialog, parent)
        
        return dialog
    
    @staticmethod
    def _copy_to_clipboard(dialog, text: str):
        """Copy text to clipboard"""
        try:
            dialog.clipboard_clear()
            dialog.clipboard_append(text)
            # Brief feedback - change button text temporarily
            # This is a simple way to give feedback without additional dialogs
        except Exception as e:
            logger.warning(f"Failed to copy to clipboard: {e}")


class ConfirmDialog:
    """Confirmation dialog with customizable options"""
    
    @staticmethod
    def ask_yes_no(parent, title: str, message: str, 
                   yes_text: str = "Yes", no_text: str = "No") -> bool:
        """Show yes/no confirmation dialog"""
        return ConfirmDialog._show_confirm(parent, title, message, 
                                         [(yes_text, True), (no_text, False)])
    
    @staticmethod
    def ask_yes_no_cancel(parent, title: str, message: str,
                         yes_text: str = "Yes", no_text: str = "No", 
                         cancel_text: str = "Cancel") -> Optional[bool]:
        """Show yes/no/cancel confirmation dialog"""
        return ConfirmDialog._show_confirm(parent, title, message,
                                         [(yes_text, True), (no_text, False), (cancel_text, None)])
    
    @staticmethod
    def ask_custom(parent, title: str, message: str, 
                  options: list) -> Optional[str]:
        """Show confirmation dialog with custom options"""
        return ConfirmDialog._show_confirm(parent, title, message, 
                                         [(opt, opt) for opt in options])
    
    @staticmethod
    def _show_confirm(parent, title: str, message: str, options: list):
        """Show confirmation dialog with custom options"""
        result = [None]  # Use list to modify from nested function
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Make modal
        dialog.transient(parent)
        dialog.grab_set()
        
        # Configure grid
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # Message
        message_label = ttk.Label(
            main_frame,
            text=message,
            wraplength=350,
            justify=tk.CENTER,
            font=('Arial', 10)
        )
        message_label.grid(row=0, column=0, pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0)
        
        def on_choice(value):
            result[0] = value
            dialog.destroy()
        
        # Create buttons
        for i, (text, value) in enumerate(options):
            btn = ttk.Button(
                button_frame,
                text=text,
                command=lambda v=value: on_choice(v),
                width=10
            )
            btn.grid(row=0, column=i, padx=5)
            
            # Set first button as default
            if i == 0:
                btn.configure(default='active')
        
        # Handle window close as cancel
        dialog.protocol("WM_DELETE_WINDOW", lambda: on_choice(None))
        
        # Bind keys
        if len(options) >= 2:
            dialog.bind('<Return>', lambda e: on_choice(options[0][1]))
            dialog.bind('<Escape>', lambda e: on_choice(options[-1][1]))
        
        # Center and show
        GUIHelpers.center_window(dialog, parent)
        dialog.focus_set()
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result[0]


class ProgressDialog:
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent, title: str = "Progress", message: str = "Please wait..."):
        self.parent = parent
        self.dialog = None
        self.progress_var = None
        self.message_var = None
        self.cancelled = False
        
        self._create_dialog(title, message)
    
    def _create_dialog(self, title: str, message: str):
        """Create the progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("350x120")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Prevent closing
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # Message
        self.message_var = tk.StringVar(value=message)
        message_label = ttk.Label(
            main_frame,
            textvariable=self.message_var,
            font=('Arial', 10)
        )
        message_label.grid(row=0, column=0, pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            main_frame,
            text="Cancel",
            command=self._on_cancel,
            width=10
        )
        self.cancel_button.grid(row=2, column=0)
        
        # Center on parent
        GUIHelpers.center_window(self.dialog, self.parent)
        
        # Update display
        self.dialog.update()
    
    def set_progress(self, value: float, message: str = None):
        """Update progress (0-100) and optional message"""
        if self.dialog and not self.cancelled:
            self.progress_var.set(value)
            if message:
                self.message_var.set(message)
            self.dialog.update()
    
    def set_message(self, message: str):
        """Update progress message"""
        if self.dialog and not self.cancelled:
            self.message_var.set(message)
            self.dialog.update()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self.cancelled
    
    def close(self):
        """Close the progress dialog"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.cancelled = True
        # Don't close immediately - let the calling code handle it
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()