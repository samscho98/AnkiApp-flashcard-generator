"""
Custom GUI Widgets for Language Learning Flashcard Generator
Contains reusable UI components for the main application
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
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
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the file selector UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        
        # Language selection
        ttk.Label(self, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(self, textvariable=self.language_var, 
                                          state="readonly", width=15)
        self.language_combo.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_changed)
        
        # Content type selection (radio buttons)
        self.content_type_var = tk.StringVar(value="vocabulary")
        content_type_frame = ttk.Frame(self)
        content_type_frame.grid(row=0, column=2, padx=(10, 10), sticky=tk.W)
        
        ttk.Radiobutton(content_type_frame, text="Vocabulary", variable=self.content_type_var, 
                       value="vocabulary", command=self.on_content_type_changed).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(content_type_frame, text="Grammar", variable=self.content_type_var, 
                       value="grammar", command=self.on_content_type_changed).pack(side=tk.LEFT)
        
        # File selection
        ttk.Label(self, text="File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(self, textvariable=self.file_var, 
                                      state="readonly", width=25)
        self.file_combo.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=(5, 0), sticky=(tk.W, tk.E))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_changed)
    
    def update_available_options(self, languages: Dict[str, Dict[str, List[Path]]], 
                                content_types: List[str]):
        """Update available languages and content types"""
        self.available_languages = languages
        self.available_content_types = content_types
        
        # Update language dropdown
        language_names = list(languages.keys()) if languages else []
        self.language_combo['values'] = language_names
        
        if language_names:
            self.language_combo.set(language_names[0])
            self.on_language_changed()
    
    def on_language_changed(self, event=None):
        """Handle language selection change"""
        self.update_file_dropdown()
    
    def on_content_type_changed(self):
        """Handle content type change"""
        self.update_file_dropdown()
    
    def update_file_dropdown(self):
        """Update file dropdown based on selected language and content type"""
        selected_lang = self.language_var.get()
        content_type = self.content_type_var.get()
        
        if selected_lang in self.available_languages:
            lang_data = self.available_languages[selected_lang]
            if content_type in lang_data:
                files = [f.name for f in lang_data[content_type]]
                self.file_combo['values'] = files
                if files:
                    self.file_combo.set(files[0])
                    self.on_file_changed()  # This will trigger content loading
                else:
                    self.file_combo.set("")
                    # Trigger callback with None to clear content
                    self.selection_callback(None, selected_lang, content_type)
            else:
                self.file_combo['values'] = []
                self.file_combo.set("")
                # Trigger callback with None to clear content
                self.selection_callback(None, selected_lang, content_type)
    
    def on_file_changed(self, event=None):
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
                # Clear selection if file doesn't exist
                self.selection_callback(None, selected_lang, content_type)
    
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


class ContentSelector(ttk.LabelFrame):
    """Widget for selecting specific content sections from loaded data - SINGLE SELECTION ONLY"""
    
    def __init__(self, parent, selection_callback: Callable):
        super().__init__(parent, text="Content Selection", padding="10")
        self.selection_callback = selection_callback
        self.current_data = None
        self.content_type = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the content selector UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create listbox with scrollbar - CHANGED TO SINGLE SELECTION
        list_frame = ttk.Frame(self)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Changed from tk.EXTENDED to tk.SINGLE for single selection only
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.listbox.bind('<<ListboxSelect>>', self.on_selection_changed)
        
        # Remove select all/none buttons since we only allow single selection
        # button_frame = ttk.Frame(self)
        # button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        # 
        # ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        # ttk.Button(button_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT)
        
        # Add instruction label instead
        instruction_frame = ttk.Frame(self)
        instruction_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(instruction_frame, text="Select one day to export", 
                 font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)
    
    def load_data(self, data: Dict[str, Any], content_type: str):
        """Load data and populate the list"""
        self.current_data = data
        self.content_type = content_type
        self.listbox.delete(0, tk.END)  # Always clear first
        
        if not data:
            # No data - trigger callback with empty selection
            self.selection_callback([], 0)
            return
        
        # Handle different JSON structures
        if 'days' in data:
            # Week-based structure with days
            for day_key, day_data in data['days'].items():
                topic = day_data.get('topic', 'No topic')
                word_count = len(day_data.get('words', []))
                display_text = f"{day_key.replace('_', ' ').title()} - {topic} ({word_count} items)"
                self.listbox.insert(tk.END, display_text)
        
        elif any(key in data for key in ['lessons', 'chapters', 'sections']):
            # Handle lessons/chapters/sections structure
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in data)
            container = data[container_key]
            
            for section_key, section_data in container.items():
                topic = section_data.get('topic', section_data.get('title', 'No topic'))
                items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                display_text = f"{section_key.replace('_', ' ').title()} - {topic} ({len(items)} items)"
                self.listbox.insert(tk.END, display_text)
        
        elif 'entries' in data:
            # Direct entries structure
            entries = data['entries']
            display_text = f"All entries ({len(entries)} items)"
            self.listbox.insert(tk.END, display_text)
        
        elif 'words' in data:
            # Direct words structure
            words = data['words']
            display_text = f"All words ({len(words)} items)"
            self.listbox.insert(tk.END, display_text)
        
        # Auto-select first item if available
        if self.listbox.size() > 0:
            self.listbox.select_set(0)
            self.on_selection_changed()
    
    def on_selection_changed(self, event=None):
        """Handle selection change - UPDATED FOR SINGLE SELECTION"""
        if not self.current_data:
            return
        
        # Get single selected index (curselection returns tuple, but only one item for SINGLE mode)
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            # No selection
            self.selection_callback([], 0)
            return
        
        # Only one index since we use SINGLE selection mode
        selected_idx = selected_indices[0]
        selected_sections = []
        total_items = 0
        
        if 'days' in self.current_data:
            day_keys = list(self.current_data['days'].keys())
            if selected_idx < len(day_keys):
                day_key = day_keys[selected_idx]
                selected_sections.append(day_key)
                total_items = len(self.current_data['days'][day_key].get('words', []))
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_keys = list(self.current_data[container_key].keys())
            if selected_idx < len(section_keys):
                section_key = section_keys[selected_idx]
                selected_sections.append(section_key)
                items = self.current_data[container_key][section_key].get('entries', 
                         self.current_data[container_key][section_key].get('words', 
                         self.current_data[container_key][section_key].get('items', [])))
                total_items = len(items)
        
        else:
            # For direct entries/words
            selected_sections = ['main']
            total_items = len(self.current_data.get('entries', self.current_data.get('words', [])))
        
        self.selection_callback(selected_sections, total_items)
    
    def get_selected_sections(self) -> List[str]:
        """Get currently selected section names - UPDATED FOR SINGLE SELECTION"""
        if not self.current_data:
            return []
        
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            return []
        
        # Only one selection allowed
        selected_idx = selected_indices[0]
        selected_sections = []
        
        if 'days' in self.current_data:
            day_keys = list(self.current_data['days'].keys())
            if selected_idx < len(day_keys):
                selected_sections.append(day_keys[selected_idx])
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_keys = list(self.current_data[container_key].keys())
            if selected_idx < len(section_keys):
                selected_sections.append(section_keys[selected_idx])
        
        elif selected_indices:
            selected_sections = ['main']
        
        return selected_sections
    
    def clear(self):
        """Clear the content list"""
        self.listbox.delete(0, tk.END)  # Clear all items from listbox
        self.current_data = None
        self.content_type = None
        # Trigger callback to update other components
        self.selection_callback([], 0)


class ContentPreview(ttk.LabelFrame):
    """Widget for previewing selected content"""
    
    def __init__(self, parent):
        super().__init__(parent, text="Preview", padding="10")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preview UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create scrolled text widget
        self.preview_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=('Consolas', 10), state=tk.DISABLED
        )
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def update_preview(self, data: Dict[str, Any], selected_sections: List[str]):
        """Update preview with selected content"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        if not data or not selected_sections:
            self.preview_text.config(state=tk.DISABLED)
            return
        
        preview_content = []
        
        if 'days' in data:
            for section in selected_sections:
                if section in data['days']:
                    day_data = data['days'][section]
                    preview_content.append(f"=== {section.replace('_', ' ').title()} ===")
                    preview_content.append(f"Topic: {day_data.get('topic', 'No topic')}")
                    preview_content.append("")
                    
                    words = day_data.get('words', [])
                    for i, word in enumerate(words[:5]):  # Show first 5 words
                        target = word.get('german', word.get('target', 'N/A'))
                        native = word.get('english', word.get('native', 'N/A'))
                        preview_content.append(f"{i+1}. {target} → {native}")
                        
                        # Show example if available
                        example = word.get('example')
                        if example:
                            preview_content.append(f"   Example: {example}")
                    
                    if len(words) > 5:
                        preview_content.append(f"... and {len(words) - 5} more items")
                    
                    preview_content.append("")
        
        elif any(key in data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in data)
            container = data[container_key]
            
            for section in selected_sections:
                if section in container:
                    section_data = container[section]
                    preview_content.append(f"=== {section.replace('_', ' ').title()} ===")
                    preview_content.append(f"Topic: {section_data.get('topic', section_data.get('title', 'No topic'))}")
                    preview_content.append("")
                    
                    items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                    for i, item in enumerate(items[:5]):
                        target = item.get('german', item.get('target', 'N/A'))
                        native = item.get('english', item.get('native', 'N/A'))
                        preview_content.append(f"{i+1}. {target} → {native}")
                    
                    if len(items) > 5:
                        preview_content.append(f"... and {len(items) - 5} more items")
                    
                    preview_content.append("")
        
        else:
            # Handle direct entries/words
            items = data.get('entries', data.get('words', []))
            preview_content.append(f"=== All Items ({len(items)} total) ===")
            preview_content.append("")
            
            for i, item in enumerate(items[:10]):  # Show first 10 items
                target = item.get('german', item.get('target', 'N/A'))
                native = item.get('english', item.get('native', 'N/A'))
                preview_content.append(f"{i+1}. {target} → {native}")
                
                # Show example if available
                example = item.get('example')
                if example:
                    preview_content.append(f"   Example: {example}")
            
            if len(items) > 10:
                preview_content.append(f"... and {len(items) - 10} more items")
        
        self.preview_text.insert(1.0, "\n".join(preview_content))
        self.preview_text.config(state=tk.DISABLED)
    
    def clear_preview(self):
        """Clear the preview"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)


class ExportPanel(ttk.LabelFrame):
    """Widget for export controls and status - UPDATED FOR SINGLE DAY SELECTION"""
    
    def __init__(self, parent, export_callback: Callable):
        super().__init__(parent, text="Export to AnkiApp", padding="10")
        self.export_callback = export_callback
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the export panel UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Export button
        self.export_button = ttk.Button(self, text="Export to CSV", 
                                       command=self.export_callback, state=tk.DISABLED)
        self.export_button.grid(row=0, column=0, padx=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Select a day to export")
        ttk.Label(self, textvariable=self.status_var).grid(row=0, column=1, sticky=tk.W)
    
    def set_data_loaded(self, loaded: bool, filename: str = ""):
        """Update status when data is loaded"""
        if loaded:
            self.status_var.set(f"Loaded: {filename} - Select a day to export")
        else:
            self.status_var.set("Select a day to export")
            self.export_button.config(state=tk.DISABLED)
    
    def set_selection(self, section_count: int, item_count: int):
        """Update status when selection changes - UPDATED FOR SINGLE DAY"""
        if section_count == 1 and item_count > 0:
            # Single day selected (which is what we want)
            self.status_var.set(f"Selected day with {item_count} items - Ready to export")
            self.export_button.config(state=tk.NORMAL)
        elif section_count > 1:
            # This shouldn't happen anymore with single selection, but just in case
            self.status_var.set("Multiple selections detected - Please select only one day")
            self.export_button.config(state=tk.DISABLED)
        else:
            # No selection
            self.status_var.set("No day selected")
            self.export_button.config(state=tk.DISABLED)


class ProgressDisplay(ttk.LabelFrame):
    """Widget for displaying learning progress and statistics"""
    
    def __init__(self, parent, history_manager):
        super().__init__(parent, text="Progress", padding="5")
        self.history_manager = history_manager
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup the progress display UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Progress labels
        self.progress_text = tk.StringVar()
        ttk.Label(self, textvariable=self.progress_text, font=('Arial', 9)).grid(
            row=0, column=0, sticky=tk.W
        )
    
    def refresh(self):
        """Refresh progress display"""
        try:
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


class FileSelector(ttk.Frame):
    """Widget for selecting language, content type, and specific files"""
    
    def __init__(self, parent, selection_callback: Callable):
        super().__init__(parent)
        self.selection_callback = selection_callback
        self.available_languages = {}
        self.available_content_types = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the file selector UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        
        # Language selection
        ttk.Label(self, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(self, textvariable=self.language_var, 
                                          state="readonly", width=15)
        self.language_combo.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_changed)
        
        # Content type selection (radio buttons)
        self.content_type_var = tk.StringVar(value="vocabulary")
        content_type_frame = ttk.Frame(self)
        content_type_frame.grid(row=0, column=2, padx=(10, 10), sticky=tk.W)
        
        ttk.Radiobutton(content_type_frame, text="Vocabulary", variable=self.content_type_var, 
                       value="vocabulary", command=self.on_content_type_changed).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(content_type_frame, text="Grammar", variable=self.content_type_var, 
                       value="grammar", command=self.on_content_type_changed).pack(side=tk.LEFT)
        
        # File selection
        ttk.Label(self, text="File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(self, textvariable=self.file_var, 
                                      state="readonly", width=25)
        self.file_combo.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=(5, 0), sticky=(tk.W, tk.E))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_changed)
    
    def update_available_options(self, languages: Dict[str, Dict[str, List[Path]]], 
                                content_types: List[str]):
        """Update available languages and content types"""
        self.available_languages = languages
        self.available_content_types = content_types
        
        # Update language dropdown
        language_names = list(languages.keys()) if languages else []
        self.language_combo['values'] = language_names
        
        if language_names:
            self.language_combo.set(language_names[0])
            self.on_language_changed()
    
    def on_language_changed(self, event=None):
        """Handle language selection change"""
        self.update_file_dropdown()
    
    def on_content_type_changed(self):
        """Handle content type change"""
        self.update_file_dropdown()
    
    def update_file_dropdown(self):
        """Update file dropdown based on selected language and content type"""
        selected_lang = self.language_var.get()
        content_type = self.content_type_var.get()
        
        if selected_lang in self.available_languages:
            lang_data = self.available_languages[selected_lang]
            if content_type in lang_data:
                files = [f.name for f in lang_data[content_type]]
                self.file_combo['values'] = files
                if files:
                    self.file_combo.set(files[0])
                    self.on_file_changed()
            else:
                self.file_combo['values'] = []
                self.file_combo.set("")
    
    def on_file_changed(self, event=None):
        """Handle file selection change"""
        selected_file = self.file_var.get()
        selected_lang = self.language_var.get()
        content_type = self.content_type_var.get()
        
        if selected_file and selected_lang:
            # Construct file path
            file_path = Path("data") / content_type / selected_lang / selected_file
            if file_path.exists():
                self.selection_callback(file_path, selected_lang, content_type)
    
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


class ContentSelector(ttk.LabelFrame):
    """Widget for selecting specific content sections from loaded data"""
    
    def __init__(self, parent, selection_callback: Callable):
        super().__init__(parent, text="Content Selection", padding="10")
        self.selection_callback = selection_callback
        self.current_data = None
        self.content_type = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the content selector UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create listbox with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.listbox.bind('<<ListboxSelect>>', self.on_selection_changed)
        
        # Add select all/none buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT)
    
    def load_data(self, data: Dict[str, Any], content_type: str):
        """Load data and populate the list"""
        self.current_data = data
        self.content_type = content_type
        self.listbox.delete(0, tk.END)
        
        if not data:
            return
        
        # Handle different JSON structures
        if 'days' in data:
            # Week-based structure with days
            for day_key, day_data in data['days'].items():
                topic = day_data.get('topic', 'No topic')
                word_count = len(day_data.get('words', []))
                display_text = f"{day_key.replace('_', ' ').title()} - {topic} ({word_count} items)"
                self.listbox.insert(tk.END, display_text)
        
        elif any(key in data for key in ['lessons', 'chapters', 'sections']):
            # Handle lessons/chapters/sections structure
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in data)
            container = data[container_key]
            
            for section_key, section_data in container.items():
                topic = section_data.get('topic', section_data.get('title', 'No topic'))
                items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                display_text = f"{section_key.replace('_', ' ').title()} - {topic} ({len(items)} items)"
                self.listbox.insert(tk.END, display_text)
        
        elif 'entries' in data:
            # Direct entries structure
            entries = data['entries']
            display_text = f"All entries ({len(entries)} items)"
            self.listbox.insert(tk.END, display_text)
        
        elif 'words' in data:
            # Direct words structure
            words = data['words']
            display_text = f"All words ({len(words)} items)"
            self.listbox.insert(tk.END, display_text)
        
        # Select all items by default
        self.select_all()
    
    def on_selection_changed(self, event=None):
        """Handle selection change"""
        if not self.current_data:
            return
        
        selected_indices = self.listbox.curselection()
        selected_sections = []
        total_items = 0
        
        if 'days' in self.current_data:
            day_keys = list(self.current_data['days'].keys())
            for idx in selected_indices:
                if idx < len(day_keys):
                    day_key = day_keys[idx]
                    selected_sections.append(day_key)
                    total_items += len(self.current_data['days'][day_key].get('words', []))
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_keys = list(self.current_data[container_key].keys())
            for idx in selected_indices:
                if idx < len(section_keys):
                    section_key = section_keys[idx]
                    selected_sections.append(section_key)
                    items = self.current_data[container_key][section_key].get('entries', 
                             self.current_data[container_key][section_key].get('words', 
                             self.current_data[container_key][section_key].get('items', [])))
                    total_items += len(items)
        
        else:
            # For direct entries/words
            if selected_indices:
                selected_sections = ['main']
                total_items = len(self.current_data.get('entries', self.current_data.get('words', [])))
        
        self.selection_callback(selected_sections, total_items)
    
    def get_selected_sections(self) -> List[str]:
        """Get currently selected section names"""
        if not self.current_data:
            return []
        
        selected_indices = self.listbox.curselection()
        selected_sections = []
        
        if 'days' in self.current_data:
            day_keys = list(self.current_data['days'].keys())
            for idx in selected_indices:
                if idx < len(day_keys):
                    selected_sections.append(day_keys[idx])
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_keys = list(self.current_data[container_key].keys())
            for idx in selected_indices:
                if idx < len(section_keys):
                    selected_sections.append(section_keys[idx])
        
        elif selected_indices:
            selected_sections = ['main']
        
        return selected_sections
    
    def select_all(self):
        """Select all items in the list"""
        self.listbox.select_set(0, tk.END)
        self.on_selection_changed()
    
    def select_none(self):
        """Deselect all items"""
        self.listbox.select_clear(0, tk.END)
        self.on_selection_changed()
    
    def clear(self):
        """Clear the content list"""
        self.listbox.delete(0, tk.END)
        self.current_data = None
        self.content_type = None


class ContentPreview(ttk.LabelFrame):
    """Widget for previewing selected content"""
    
    def __init__(self, parent):
        super().__init__(parent, text="Preview", padding="10")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preview UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create scrolled text widget
        self.preview_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=('Consolas', 10), state=tk.DISABLED
        )
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def update_preview(self, data: Dict[str, Any], selected_sections: List[str]):
        """Update preview with selected content"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        if not data or not selected_sections:
            self.preview_text.config(state=tk.DISABLED)
            return
        
        preview_content = []
        
        if 'days' in data:
            for section in selected_sections:
                if section in data['days']:
                    day_data = data['days'][section]
                    preview_content.append(f"=== {section.replace('_', ' ').title()} ===")
                    preview_content.append(f"Topic: {day_data.get('topic', 'No topic')}")
                    preview_content.append("")
                    
                    words = day_data.get('words', [])
                    for i, word in enumerate(words[:5]):  # Show first 5 words
                        target = word.get('german', word.get('target', 'N/A'))
                        native = word.get('english', word.get('native', 'N/A'))
                        preview_content.append(f"{i+1}. {target} → {native}")
                        
                        # Show example if available
                        example = word.get('example')
                        if example:
                            preview_content.append(f"   Example: {example}")
                    
                    if len(words) > 5:
                        preview_content.append(f"... and {len(words) - 5} more items")
                    
                    preview_content.append("")
        
        elif any(key in data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in data)
            container = data[container_key]
            
            for section in selected_sections:
                if section in container:
                    section_data = container[section]
                    preview_content.append(f"=== {section.replace('_', ' ').title()} ===")
                    preview_content.append(f"Topic: {section_data.get('topic', section_data.get('title', 'No topic'))}")
                    preview_content.append("")
                    
                    items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                    for i, item in enumerate(items[:5]):
                        target = item.get('german', item.get('target', 'N/A'))
                        native = item.get('english', item.get('native', 'N/A'))
                        preview_content.append(f"{i+1}. {target} → {native}")
                    
                    if len(items) > 5:
                        preview_content.append(f"... and {len(items) - 5} more items")
                    
                    preview_content.append("")
        
        else:
            # Handle direct entries/words
            items = data.get('entries', data.get('words', []))
            preview_content.append(f"=== All Items ({len(items)} total) ===")
            preview_content.append("")
            
            for i, item in enumerate(items[:10]):  # Show first 10 items
                target = item.get('german', item.get('target', 'N/A'))
                native = item.get('english', item.get('native', 'N/A'))
                preview_content.append(f"{i+1}. {target} → {native}")
                
                # Show example if available
                example = item.get('example')
                if example:
                    preview_content.append(f"   Example: {example}")
            
            if len(items) > 10:
                preview_content.append(f"... and {len(items) - 10} more items")
        
        self.preview_text.insert(1.0, "\n".join(preview_content))
        self.preview_text.config(state=tk.DISABLED)
    
    def clear_preview(self):
        """Clear the preview"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)


class ExportPanel(ttk.LabelFrame):
    """Widget for export controls and status"""
    
    def __init__(self, parent, export_callback: Callable):
        super().__init__(parent, text="Export to AnkiApp", padding="10")
        self.export_callback = export_callback
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the export panel UI"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Export button
        self.export_button = ttk.Button(self, text="Export to CSV", 
                                       command=self.export_callback, state=tk.DISABLED)
        self.export_button.grid(row=0, column=0, padx=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Select content to export")
        ttk.Label(self, textvariable=self.status_var).grid(row=0, column=1, sticky=tk.W)
    
    def set_data_loaded(self, loaded: bool, filename: str = ""):
        """Update status when data is loaded"""
        if loaded:
            self.status_var.set(f"Loaded: {filename}")
        else:
            self.status_var.set("Select content to export")
            self.export_button.config(state=tk.DISABLED)
    
    def set_selection(self, section_count: int, item_count: int):
        """Update status when selection changes"""
        if section_count > 0 and item_count > 0:
            self.status_var.set(f"Selected {section_count} sections with {item_count} items")
            self.export_button.config(state=tk.NORMAL)
        else:
            self.status_var.set("No content selected")
            self.export_button.config(state=tk.DISABLED)


class ProgressDisplay(ttk.LabelFrame):
    """Widget for displaying learning progress and statistics"""
    
    def __init__(self, parent, history_manager):
        super().__init__(parent, text="Progress", padding="5")
        self.history_manager = history_manager
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup the progress display UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Progress labels
        self.progress_text = tk.StringVar()
        ttk.Label(self, textvariable=self.progress_text, font=('Arial', 9)).grid(
            row=0, column=0, sticky=tk.W
        )
    
    def refresh(self):
        """Refresh progress display"""
        try:
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