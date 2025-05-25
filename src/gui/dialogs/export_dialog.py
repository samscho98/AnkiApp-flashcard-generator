"""
Export Dialog
Progress and options dialog for CSV export operations
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import logging

from ..utils import GUIHelpers

logger = logging.getLogger(__name__)


class ExportDialog:
    """Export progress and options dialog"""
    
    def __init__(self, parent, title: str = "Exporting..."):
        self.parent = parent
        self.dialog = None
        self.progress_var = None
        self.message_var = None
        self.detail_var = None
        self.cancelled = False
        self.on_cancel_callback = None
        
        self._create_dialog(title)
    
    def _create_dialog(self, title: str):
        """Create the export dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("400x180")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # Icon and main message
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(1, weight=1)
        
        # Export icon
        icon_label = ttk.Label(header_frame, text="📊", font=('Arial', 16))
        icon_label.grid(row=0, column=0, padx=(0, 10))
        
        # Main message
        self.message_var = tk.StringVar(value="Preparing export...")
        message_label = ttk.Label(
            header_frame,
            textvariable=self.message_var,
            font=('Arial', 11, 'bold')
        )
        message_label.grid(row=0, column=1, sticky=tk.W)
        
        # Detail message
        self.detail_var = tk.StringVar(value="")
        detail_label = ttk.Label(
            main_frame,
            textvariable=self.detail_var,
            font=('Arial', 9),
            foreground='gray'
        )
        detail_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=350
        )
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=tk.E)
        
        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=10
        )
        self.cancel_button.pack(side=tk.RIGHT)
        
        # Center on parent
        GUIHelpers.center_window(self.dialog, self.parent)
        
        # Start with indeterminate progress
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        
        # Update display
        self.dialog.update()
    
    def set_progress(self, value: Optional[float] = None, message: str = None, detail: str = None):
        """Update progress and messages"""
        if not self.dialog or self.cancelled:
            return
        
        try:
            if value is not None:
                # Switch to determinate mode if needed
                if self.progress_bar.cget('mode') == 'indeterminate':
                    self.progress_bar.stop()
                    self.progress_bar.configure(mode='determinate')
                
                self.progress_var.set(max(0, min(100, value)))
            
            if message:
                self.message_var.set(message)
            
            if detail:
                self.detail_var.set(detail)
            
            self.dialog.update()
            
        except tk.TclError:
            # Dialog was destroyed
            pass
    
    def set_indeterminate(self, message: str = None):
        """Set progress to indeterminate mode"""
        if not self.dialog or self.cancelled:
            return
        
        try:
            if self.progress_bar.cget('mode') == 'determinate':
                self.progress_bar.configure(mode='indeterminate')
                self.progress_bar.start()
            
            if message:
                self.message_var.set(message)
            
            self.dialog.update()
            
        except tk.TclError:
            pass
    
    def set_complete(self, message: str = "Export completed!", detail: str = ""):
        """Mark export as complete"""
        if not self.dialog or self.cancelled:
            return
        
        try:
            # Stop progress animation
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
            self.progress_var.set(100)
            
            self.message_var.set(message)
            self.detail_var.set(detail)
            
            # Change cancel button to close
            self.cancel_button.configure(text="Close", command=self.close)
            
            self.dialog.update()
            
        except tk.TclError:
            pass
    
    def set_error(self, message: str = "Export failed!", detail: str = ""):
        """Mark export as failed"""
        if not self.dialog or self.cancelled:
            return
        
        try:
            # Stop progress animation
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
            self.progress_var.set(0)
            
            self.message_var.set(message)
            self.detail_var.set(detail)
            
            # Change cancel button to close
            self.cancel_button.configure(text="Close", command=self.close)
            
            self.dialog.update()
            
        except tk.TclError:
            pass
    
    def is_cancelled(self) -> bool:
        """Check if export was cancelled"""
        return self.cancelled
    
    def set_cancel_callback(self, callback: Callable):
        """Set callback to call when cancel is pressed"""
        self.on_cancel_callback = callback
    
    def close(self):
        """Close the dialog"""
        if self.dialog:
            try:
                self.progress_bar.stop()
                self.dialog.grab_release()
                self.dialog.destroy()
                self.dialog = None
            except tk.TclError:
                pass
    
    def _on_cancel(self):
        """Handle cancel button press"""
        if not self.cancelled:
            self.cancelled = True
            
            if self.on_cancel_callback:
                self.on_cancel_callback()
            
            # Update UI to show cancelling
            if self.dialog:
                try:
                    self.message_var.set("Cancelling...")
                    self.detail_var.set("Please wait...")
                    self.cancel_button.configure(state=tk.DISABLED)
                    self.dialog.update()
                except tk.TclError:
                    pass
    
    def show_progress(self, message: str = "Exporting..."):
        """Show the dialog with a progress message"""
        if self.dialog:
            self.set_progress(message=message)
            self.dialog.deiconify()
            self.dialog.lift()
    
    def hide(self):
        """Hide the dialog without closing it"""
        if self.dialog:
            self.dialog.withdraw()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


class ExportOptionsDialog:
    """Dialog for choosing export options before exporting"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.result = None
        
    def show(self, default_filename: str = "", available_formats: list = None) -> Optional[dict]:
        """
        Show export options dialog
        
        Returns:
            Dict with export options or None if cancelled
        """
        if available_formats is None:
            available_formats = ['ankiapp', 'anki', 'quizlet', 'generic']
        
        self.result = None
        self._create_dialog(default_filename, available_formats)
        
        # Center and show
        GUIHelpers.center_window(self.dialog, self.parent)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.result
    
    def _create_dialog(self, default_filename: str, available_formats: list):
        """Create the export options dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Export Options")
        self.dialog.geometry("450x300")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Export Options", 
            font=('Arial', 12, 'bold')
        )
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1
        
        # Filename
        ttk.Label(main_frame, text="Filename:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.filename_entry = ttk.Entry(main_frame, width=30)
        self.filename_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.filename_entry.insert(0, default_filename)
        row += 1
        
        # Export format
        ttk.Label(main_frame, text="Format:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.format_var = tk.StringVar(value=available_formats[0])
        format_combo = ttk.Combobox(
            main_frame,
            textvariable=self.format_var,
            values=available_formats,
            state='readonly',
            width=15
        )
        format_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 15))
        row += 1
        
        # Export options
        self.include_headers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Include column headers",
            variable=self.include_headers_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.html_formatting_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Enable HTML formatting (bold, italic, etc.)",
            variable=self.html_formatting_var
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.open_after_export_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Open file after export",
            variable=self.open_after_export_var
        ).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, sticky=tk.E)
        
        ttk.Button(
            button_frame,
            text="Export",
            command=self._on_export,
            width=10,
            default='active'
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=10
        ).pack(side=tk.RIGHT)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self._on_export())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
        # Focus filename entry
        self.filename_entry.focus_set()
        self.filename_entry.select_range(0, tk.END)
    
    def _on_export(self):
        """Handle export button"""
        filename = self.filename_entry.get().strip()
        if not filename:
            from tkinter import messagebox
            messagebox.showwarning("Export Options", "Please enter a filename.")
            return
        
        self.result = {
            'filename': filename,
            'format': self.format_var.get(),
            'include_headers': self.include_headers_var.get(),
            'html_formatting': self.html_formatting_var.get(),
            'open_after_export': self.open_after_export_var.get()
        }
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.result = None
        self.dialog.destroy()