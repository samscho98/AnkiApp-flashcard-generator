"""
File Selector Component
Handles language, content type, and file selection
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class FileSelector(ttk.Frame):
    """Widget for selecting language, content type, and specific files"""
    
    def __init__(self, parent, selection_callback: Callable):
        super().__init__(parent)
        
        self.selection_callback = selection_callback
        self.available_languages = {}
        self.available_content_types = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the file selector UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        
        # Language selection
        ttk.Label(self, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(
            self, 
            textvariable=self.language_var, 
            state="readonly", 
            width=20
        )
        self.language_combo.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)
        self.language_combo.bind('<<ComboboxSelected>>', self._on_language_changed)
        
        # Content type selection (radio buttons)
        self.content_type_var = tk.StringVar(value="vocabulary")
        content_type_frame = ttk.Frame(self)
        content_type_frame.grid(row=0, column=2, padx=(15, 15), sticky=tk.W)
        
        ttk.Radiobutton(
            content_type_frame, 
            text="Vocabulary", 
            variable=self.content_type_var, 
            value="vocabulary",
            command=self._on_content_type_changed
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            content_type_frame, 
            text="Grammar", 
            variable=self.content_type_var, 
            value="grammar",
            command=self._on_content_type_changed
        ).pack(side=tk.LEFT)
        
        # File selection
        ttk.Label(self, text="File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(8, 0))
        
        file_frame = ttk.Frame(self)
        file_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(8, 0), padx=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(
            file_frame, 
            textvariable=self.file_var, 
            state="readonly"
        )
        self.file_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.file_combo.bind('<<ComboboxSelected>>', self._on_file_changed)
        
        # Browse button
        ttk.Button(
            file_frame, 
            text="Browse...", 
            command=self._browse_for_file,
            width=10
        ).grid(row=0, column=1)
    
    def update_available_options(self, languages: Dict[str, Dict[str, List[Path]]], 
                                content_types: List[str]):
        """Update available languages and content types"""
        self.available_languages = languages
        self.available_content_types = content_types
        
        # Update language dropdown
        language_names = list(languages.keys()) if languages else []
        self.language_combo['values'] = language_names
        
        if language_names:
            # Set first language as default if none selected
            if not self.language_var.get():
                self.language_combo.set(language_names[0])
            self._on_language_changed()
        else:
            self.language_combo.set("")
            self.file_combo['values'] = []
            self.file_combo.set("")
    
    def _on_language_changed(self, event=None):
        """Handle language selection change"""
        self._update_file_dropdown()
    
    def _on_content_type_changed(self):
        """Handle content type change"""
        self._update_file_dropdown()
    
    def _update_file_dropdown(self):
        """Update file dropdown based on selected language and content type"""
        selected_lang = self.language_var.get()
        content_type = self.content_type_var.get()
        
        self.file_combo['values'] = []
        self.file_combo.set("")
        
        if selected_lang in self.available_languages:
            lang_data = self.available_languages[selected_lang]
            if content_type in lang_data:
                files = [f.name for f in lang_data[content_type]]
                self.file_combo['values'] = files
                if files:
                    self.file_combo.set(files[0])
                    self._on_file_changed()
                else:
                    # No files available for this combination
                    self.selection_callback(None, selected_lang, content_type)
            else:
                # No content of this type for this language
                self.selection_callback(None, selected_lang, content_type)
    
    def _on_file_changed(self, event=None):
        """Handle file selection change"""
        selected_file = self.file_var.get()
        selected_lang = self.language_var.get()
        content_type = self.content_type_var.get()
        
        if selected_file and selected_lang:
            # Construct file path
            file_path = Path("data") / content_type / selected_lang / selected_file
            if file_path.exists():
                self.selection_callback(file_path, selected_lang, content_type)
            else:
                logger.warning(f"Selected file does not exist: {file_path}")
                self.selection_callback(None, selected_lang, content_type)
        else:
            self.selection_callback(None, selected_lang, content_type)
    
    def _browse_for_file(self):
        """Open file browser dialog"""
        filetypes = [
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        # Start from data directory if it exists
        initial_dir = Path("data")
        if not initial_dir.exists():
            initial_dir = Path.cwd()
        
        file_path = filedialog.askopenfilename(
            title="Select learning content file",
            filetypes=filetypes,
            initialdir=str(initial_dir)
        )
        
        if file_path:
            file_path = Path(file_path)
            
            # Try to determine language and content type from path
            language = "Custom"
            content_type = "vocabulary"
            
            # If file is in our data structure, extract info
            try:
                parts = file_path.parts
                data_index = parts.index("data")
                if len(parts) > data_index + 2:
                    content_type = parts[data_index + 1]
                    language = parts[data_index + 2]
            except (ValueError, IndexError):
                pass
            
            # Update dropdowns
            self.content_type_var.set(content_type)
            
            # Add language if not in list
            current_languages = list(self.language_combo['values'])
            if language not in current_languages:
                current_languages.append(language)
                self.language_combo['values'] = current_languages
            
            self.language_var.set(language)
            
            # Add file to list
            current_files = list(self.file_combo['values'])
            filename = file_path.name
            if filename not in current_files:
                current_files.append(filename)
                self.file_combo['values'] = current_files
            
            self.file_var.set(filename)
            
            # Trigger selection
            self.selection_callback(file_path, language, content_type)
    
    def get_selected_language(self) -> str:
        """Get currently selected language"""
        return self.language_var.get()
    
    def get_selected_content_type(self) -> str:
        """Get currently selected content type"""
        return self.content_type_var.get()
    
    def get_selected_file_path(self) -> Optional[Path]:
        """Get currently selected file path"""
        selected_file = self.file_var.get()
        selected_lang = self.language_var.get()
        content_type = self.content_type_var.get()
        
        if selected_file and selected_lang:
            return Path("data") / content_type / selected_lang / selected_file
        return None
    
    def set_selection(self, language: str, content_type: str, filename: str):
        """Programmatically set selection"""
        self.language_var.set(language)
        self.content_type_var.set(content_type)
        self._update_file_dropdown()
        self.file_var.set(filename)
        self._on_file_changed()
    
    def refresh_files(self):
        """Refresh file list for current selection"""
        self._update_file_dropdown()
    
    def open_file_dialog(self):
        """Public method to open file dialog"""
        self._browse_for_file()