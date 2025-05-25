"""
Export Panel Component
Controls for CSV export with status information
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class ExportPanel(ttk.LabelFrame):
    """Widget for export controls and status display"""
    
    def __init__(self, parent, export_callback: Callable):
        super().__init__(parent, text="Export to AnkiApp", padding="10")
        
        self.export_callback = export_callback
        self._data_loaded = False
        self._csv_ready = False
        self._selection_count = 0
        self._item_count = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the export panel UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Export button
        self.export_button = ttk.Button(
            self, 
            text="Export CSV File", 
            command=self._on_export_clicked,
            state=tk.DISABLED,
            width=15
        )
        self.export_button.grid(row=0, column=0, padx=(0, 15), sticky=tk.W)
        
        # Status information
        status_frame = ttk.Frame(self)
        status_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        # Main status label
        self.status_var = tk.StringVar(value="Select a day/section to begin")
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            font=('Arial', 10)
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Secondary info label
        self.info_var = tk.StringVar(value="")
        self.info_label = ttk.Label(
            status_frame, 
            textvariable=self.info_var,
            font=('Arial', 9),
            foreground='gray'
        )
        self.info_label.grid(row=1, column=0, sticky=tk.W)
        
        # Export format info (small)
        format_info = ttk.Label(
            status_frame,
            text="Exports in AnkiApp CSV format",
            font=('Arial', 8),
            foreground='gray'
        )
        format_info.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
    
    def _on_export_clicked(self):
        """Handle export button click"""
        try:
            logger.info("Export button clicked")
            self.export_callback()
        except Exception as e:
            logger.error(f"Error in export callback: {e}")
    
    def set_data_loaded(self, loaded: bool, filename: str = ""):
        """Update status when data file is loaded"""
        self._data_loaded = loaded
        
        if loaded:
            self.status_var.set(f"File loaded: {filename}")
            self.info_var.set("Select a day/section to preview CSV")
        else:
            self.status_var.set("No file loaded")
            self.info_var.set("Choose language and file above")
            self._csv_ready = False
        
        self._update_button_state()
    
    def set_selection(self, section_count: int, item_count: int):
        """Update status when selection changes"""
        self._selection_count = section_count
        self._item_count = item_count
        
        if section_count > 0 and item_count > 0:
            if section_count == 1:
                self.status_var.set(f"Selected: 1 section with {item_count} items")
            else:
                self.status_var.set(f"Selected: {section_count} sections with {item_count} items")
            self.info_var.set("CSV preview generated - edit if needed")
        else:
            self.status_var.set("No content selected")
            self.info_var.set("Select a day/section to preview CSV")
            self._csv_ready = False
        
        self._update_button_state()
    
    def set_csv_ready(self, ready: bool):
        """Update status when CSV content is ready for export"""
        self._csv_ready = ready
        
        if ready:
            self.info_var.set("CSV ready for export")
        else:
            if self._selection_count > 0:
                self.info_var.set("Generating CSV preview...")
            else:
                self.info_var.set("No CSV content available")
        
        self._update_button_state()
    
    def _update_button_state(self):
        """Update export button enabled/disabled state"""
        # Button is enabled if we have data loaded and CSV is ready
        if self._data_loaded and self._csv_ready and self._item_count > 0:
            self.export_button.config(state=tk.NORMAL)
        else:
            self.export_button.config(state=tk.DISABLED)
    
    def set_exporting(self, is_exporting: bool):
        """Update UI during export process"""
        if is_exporting:
            self.export_button.config(state=tk.DISABLED, text="Exporting...")
            self.status_var.set("Exporting CSV file...")
            self.info_var.set("Please wait...")
        else:
            self.export_button.config(text="Export CSV File")
            self._update_button_state()
    
    def set_export_complete(self, success: bool, message: str = ""):
        """Update UI when export is complete"""
        self.set_exporting(False)
        
        if success:
            self.status_var.set("Export successful!")
            self.info_var.set(message or "CSV file saved")
        else:
            self.status_var.set("Export failed")
            self.info_var.set(message or "See error dialog for details")
    
    def get_status(self) -> dict:
        """Get current export panel status"""
        return {
            'data_loaded': self._data_loaded,
            'csv_ready': self._csv_ready,
            'selection_count': self._selection_count,
            'item_count': self._item_count,
            'export_enabled': self.export_button['state'] == tk.NORMAL
        }