"""
Settings Dialog
Configuration interface for application settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from ..utils import GUIHelpers, LayoutHelpers

logger = logging.getLogger(__name__)


class SettingsDialog:
    """Settings configuration dialog window"""
    
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        self.dialog = None
        self.widgets = {}
        self.original_settings = None
        
    def show(self):
        """Show the settings dialog"""
        if self.dialog is not None:
            # Dialog already exists, bring it to front
            self.dialog.lift()
            self.dialog.focus_force()
            return
        
        # Create new settings dialog
        self._create_dialog()
        self._create_content()
        self._load_current_settings()
        
        # Center and show
        GUIHelpers.center_window(self.dialog, self.parent)
        self.dialog.focus_set()
    
    def _create_dialog(self):
        """Create the dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x600")
        self.dialog.resizable(True, True)
        self.dialog.minsize(400, 500)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Configure main grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def _create_content(self):
        """Create the dialog content"""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for different settings categories
        notebook, tabs = LayoutHelpers.create_notebook_with_tabs(main_frame, {
            'general': {'text': 'General'},
            'export': {'text': 'Export'},
            'appearance': {'text': 'Appearance'},
            'advanced': {'text': 'Advanced'}
        })
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Create content for each tab
        self._create_general_tab(tabs['general'])
        self._create_export_tab(tabs['export'])
        self._create_appearance_tab(tabs['appearance'])
        self._create_advanced_tab(tabs['advanced'])
        
        # Create button row
        self._create_buttons(main_frame)
    
    def _create_general_tab(self, parent):
        """Create general settings tab"""
        # Configure grid
        parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # Daily target items
        ttk.Label(parent, text="Daily Target Items:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['daily_target'] = ttk.Spinbox(
            parent, from_=1, to=100, width=10
        )
        self.widgets['daily_target'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Target language
        ttk.Label(parent, text="Target Language:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['target_language'] = ttk.Entry(parent, width=20)
        self.widgets['target_language'].grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Native language
        ttk.Label(parent, text="Native Language:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['native_language'] = ttk.Combobox(
            parent, 
            values=['english', 'spanish', 'french', 'german', 'italian', 'portuguese'],
            state='readonly',
            width=18
        )
        self.widgets['native_language'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Include native connections
        self.widgets['include_connections'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Include language connections (e.g., Dutch connections for German)",
            variable=self.widgets['include_connections']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Study reminder
        self.widgets['study_reminder'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Enable study reminders",
            variable=self.widgets['study_reminder']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Reminder time
        ttk.Label(parent, text="Reminder Time:").grid(
            row=row, column=0, sticky=tk.W, padx=(20, 10), pady=5
        )
        self.widgets['reminder_time'] = ttk.Entry(parent, width=10)
        self.widgets['reminder_time'].grid(row=row, column=1, sticky=tk.W, pady=5)
        
        # Add helper text
        ttk.Label(parent, text="(Format: HH:MM, e.g., 09:00)", font=('Arial', 8), foreground='gray').grid(
            row=row+1, column=1, sticky=tk.W, pady=(0, 5)
        )
    
    def _create_export_tab(self, parent):
        """Create export settings tab"""
        parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # Output directory
        ttk.Label(parent, text="Output Directory:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        self.widgets['output_directory'] = ttk.Entry(dir_frame)
        self.widgets['output_directory'].grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(
            dir_frame, 
            text="Browse...", 
            command=self._browse_output_directory,
            width=10
        ).grid(row=0, column=1)
        row += 1
        
        # Export format
        ttk.Label(parent, text="Export Format:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['export_format'] = ttk.Combobox(
            parent,
            values=['ankiapp', 'anki', 'quizlet', 'generic'],
            state='readonly',
            width=18
        )
        self.widgets['export_format'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Filename template
        ttk.Label(parent, text="Filename Template:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['filename_template'] = ttk.Entry(parent)
        self.widgets['filename_template'].grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Add helper text
        ttk.Label(
            parent, 
            text="Use {category}, {subcategory}, {date} as placeholders", 
            font=('Arial', 8), 
            foreground='gray'
        ).grid(row=row+1, column=1, sticky=tk.W, pady=(0, 5))
        row += 2
        
        # Include date in filename
        self.widgets['include_date'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Include date in filename",
            variable=self.widgets['include_date']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # HTML formatting
        self.widgets['html_formatting'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Enable HTML formatting (bold, italic, line breaks)",
            variable=self.widgets['html_formatting']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Include headers
        self.widgets['include_headers'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Include headers in CSV files",
            variable=self.widgets['include_headers']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _create_appearance_tab(self, parent):
        """Create appearance settings tab"""
        parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # Theme
        ttk.Label(parent, text="Theme:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['theme'] = ttk.Combobox(
            parent,
            values=['system', 'light', 'dark', 'blue'],
            state='readonly',
            width=18
        )
        self.widgets['theme'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Font family
        ttk.Label(parent, text="Font Family:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['font_family'] = ttk.Combobox(
            parent,
            values=['Segoe UI', 'Arial', 'Calibri', 'Consolas', 'Times New Roman'],
            width=18
        )
        self.widgets['font_family'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Font size
        ttk.Label(parent, text="Font Size:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['font_size'] = ttk.Spinbox(
            parent, from_=8, to=16, width=10
        )
        self.widgets['font_size'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Window size
        ttk.Label(parent, text="Default Window Size:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        
        size_frame = ttk.Frame(parent)
        size_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        self.widgets['window_width'] = ttk.Entry(size_frame, width=8)
        self.widgets['window_width'].pack(side=tk.LEFT)
        
        ttk.Label(size_frame, text=" x ").pack(side=tk.LEFT)
        
        self.widgets['window_height'] = ttk.Entry(size_frame, width=8)
        self.widgets['window_height'].pack(side=tk.LEFT)
        row += 1
        
        # Remember window position
        self.widgets['remember_position'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Remember window position and size",
            variable=self.widgets['remember_position']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Show progress indicators
        self.widgets['show_progress'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Show progress indicators",
            variable=self.widgets['show_progress']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _create_advanced_tab(self, parent):
        """Create advanced settings tab"""
        parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # Data directory
        ttk.Label(parent, text="Data Directory:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        
        data_frame = ttk.Frame(parent)
        data_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        data_frame.columnconfigure(0, weight=1)
        
        self.widgets['data_directory'] = ttk.Entry(data_frame)
        self.widgets['data_directory'].grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(
            data_frame, 
            text="Browse...", 
            command=self._browse_data_directory,
            width=10
        ).grid(row=0, column=1)
        row += 1
        
        # Log level
        ttk.Label(parent, text="Log Level:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.widgets['log_level'] = ttk.Combobox(
            parent,
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            state='readonly',
            width=18
        )
        self.widgets['log_level'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Backup settings
        self.widgets['backup_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Enable automatic backups",
            variable=self.widgets['backup_enabled']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Backup frequency
        ttk.Label(parent, text="Backup Frequency (days):").grid(
            row=row, column=0, sticky=tk.W, padx=(20, 10), pady=5
        )
        self.widgets['backup_frequency'] = ttk.Spinbox(
            parent, from_=1, to=30, width=10
        )
        self.widgets['backup_frequency'].grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Performance mode
        self.widgets['performance_mode'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Performance mode (reduce visual effects)",
            variable=self.widgets['performance_mode']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        row += 1
        
        # Auto-update check
        self.widgets['auto_update'] = tk.BooleanVar()
        ttk.Checkbutton(
            parent,
            text="Check for updates automatically",
            variable=self.widgets['auto_update']
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def _create_buttons(self, parent):
        """Create dialog buttons"""
        button_config = {
            'ok': {'text': 'OK', 'command': self._on_ok, 'width': 10},
            'cancel': {'text': 'Cancel', 'command': self._on_cancel, 'width': 10},
            'apply': {'text': 'Apply', 'command': self._on_apply, 'width': 10},
            'reset': {'text': 'Reset to Defaults', 'command': self._on_reset, 'width': 15}
        }
        
        button_frame, buttons = LayoutHelpers.create_button_row(parent, button_config)
        button_frame.grid(row=1, column=0, sticky=tk.E, pady=(20, 0))
        
        # Set default button
        buttons['ok'].configure(default='active')
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self._on_ok())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.widgets['output_directory'].get() or str(Path.cwd())
        )
        if directory:
            self.widgets['output_directory'].delete(0, tk.END)
            self.widgets['output_directory'].insert(0, directory)
    
    def _browse_data_directory(self):
        """Browse for data directory"""
        directory = filedialog.askdirectory(
            title="Select Data Directory",
            initialdir=self.widgets['data_directory'].get() or str(Path.cwd() / "data")
        )
        if directory:
            self.widgets['data_directory'].delete(0, tk.END)
            self.widgets['data_directory'].insert(0, directory)
    
    def _load_current_settings(self):
        """Load current settings into the form"""
        try:
            # Store original settings for comparison
            self.original_settings = {
                'study': self.settings_manager.get_study_settings(),
                'export': self.settings_manager.get_export_settings(),
                'appearance': self.settings_manager.get_appearance_settings(),
                'advanced': self.settings_manager.get_advanced_settings()
            }
            
            # Load study settings
            study = self.original_settings['study']
            self.widgets['daily_target'].set(study.daily_target_items)
            self.widgets['target_language'].insert(0, 
                self.settings_manager.get_setting('language_learning.target_language', ''))
            self.widgets['native_language'].set(
                self.settings_manager.get_setting('language_learning.native_language', 'english'))
            self.widgets['include_connections'].set(study.include_native_connections)
            self.widgets['study_reminder'].set(study.study_reminder_enabled)
            self.widgets['reminder_time'].insert(0, study.reminder_time)
            
            # Load export settings
            export = self.original_settings['export']
            self.widgets['output_directory'].insert(0, export.output_directory)
            self.widgets['export_format'].set(export.export_format)
            self.widgets['filename_template'].insert(0, export.filename_template)
            self.widgets['include_date'].set(export.include_date_in_filename)
            self.widgets['html_formatting'].set(export.html_formatting)
            self.widgets['include_headers'].set(export.include_headers)
            
            # Load appearance settings
            appearance = self.original_settings['appearance']
            self.widgets['theme'].set(appearance.theme)
            self.widgets['font_family'].set(appearance.font_family)
            self.widgets['font_size'].set(appearance.font_size)
            self.widgets['window_width'].insert(0, str(appearance.window_width))
            self.widgets['window_height'].insert(0, str(appearance.window_height))
            self.widgets['remember_position'].set(appearance.remember_window_position)
            self.widgets['show_progress'].set(appearance.show_progress_indicators)
            
            # Load advanced settings
            advanced = self.original_settings['advanced']
            self.widgets['data_directory'].insert(0, advanced.data_directory)
            self.widgets['log_level'].set(advanced.log_level)
            self.widgets['backup_enabled'].set(advanced.backup_enabled)
            self.widgets['backup_frequency'].set(advanced.backup_frequency)
            self.widgets['performance_mode'].set(advanced.performance_mode)
            self.widgets['auto_update'].set(advanced.auto_update_check)
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            messagebox.showerror("Error", f"Failed to load current settings: {e}")
    
    def _save_settings(self) -> bool:
        """Save settings from the form"""
        try:
            # Validate and save study settings
            study_settings = self.settings_manager.get_study_settings()
            study_settings.daily_target_items = int(self.widgets['daily_target'].get())
            study_settings.include_native_connections = self.widgets['include_connections'].get()
            study_settings.study_reminder_enabled = self.widgets['study_reminder'].get()
            study_settings.reminder_time = self.widgets['reminder_time'].get()
            
            # Validate time format
            try:
                from datetime import time
                time.fromisoformat(study_settings.reminder_time)
            except ValueError:
                messagebox.showerror("Error", "Invalid time format. Use HH:MM (e.g., 09:00)")
                return False
            
            self.settings_manager.set_study_settings(study_settings)
            
            # Save export settings
            export_settings = self.settings_manager.get_export_settings()
            export_settings.output_directory = self.widgets['output_directory'].get()
            export_settings.export_format = self.widgets['export_format'].get()
            export_settings.filename_template = self.widgets['filename_template'].get()
            export_settings.include_date_in_filename = self.widgets['include_date'].get()
            export_settings.html_formatting = self.widgets['html_formatting'].get()
            export_settings.include_headers = self.widgets['include_headers'].get()
            
            self.settings_manager.set_export_settings(export_settings)
            
            # Save appearance settings
            appearance_settings = self.settings_manager.get_appearance_settings()
            appearance_settings.theme = self.widgets['theme'].get()
            appearance_settings.font_family = self.widgets['font_family'].get()
            appearance_settings.font_size = int(self.widgets['font_size'].get())
            appearance_settings.window_width = int(self.widgets['window_width'].get())
            appearance_settings.window_height = int(self.widgets['window_height'].get())
            appearance_settings.remember_window_position = self.widgets['remember_position'].get()
            appearance_settings.show_progress_indicators = self.widgets['show_progress'].get()
            
            self.settings_manager.set_appearance_settings(appearance_settings)
            
            # Save advanced settings
            advanced_settings = self.settings_manager.get_advanced_settings()
            advanced_settings.data_directory = self.widgets['data_directory'].get()
            advanced_settings.log_level = self.widgets['log_level'].get()
            advanced_settings.backup_enabled = self.widgets['backup_enabled'].get()
            advanced_settings.backup_frequency = int(self.widgets['backup_frequency'].get())
            advanced_settings.performance_mode = self.widgets['performance_mode'].get()
            advanced_settings.auto_update_check = self.widgets['auto_update'].get()
            
            self.settings_manager.set_advanced_settings(advanced_settings)
            
            # Save language settings
            self.settings_manager.set_language_settings(
                self.widgets['target_language'].get(),
                self.widgets['native_language'].get()
            )
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False
    
    def _on_ok(self):
        """Handle OK button"""
        if self._save_settings():
            self._close_dialog()
    
    def _on_cancel(self):
        """Handle Cancel button"""
        self._close_dialog()
    
    def _on_apply(self):
        """Handle Apply button"""
        if self._save_settings():
            messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def _on_reset(self):
        """Handle Reset to Defaults button"""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?\n\n"
                              "This action cannot be undone."):
            try:
                self.settings_manager.reset_to_defaults()
                self._close_dialog()
                messagebox.showinfo("Settings", "Settings have been reset to defaults.")
            except Exception as e:
                logger.error(f"Error resetting settings: {e}")
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None