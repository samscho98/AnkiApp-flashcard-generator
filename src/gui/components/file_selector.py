"""
Enhanced File Selector Component - FIXED to preserve language selection
Shows days/sections in a list where only one can be selected at a time
Fixed: When switching content types, preserve the current language selection
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging
import re

logger = logging.getLogger(__name__)


class FileSelector(ttk.Frame):
    """Enhanced widget for selecting language, content type, and specific files with better organization"""
    
    def __init__(self, parent, selection_callback: Callable):
        super().__init__(parent)
        
        self.selection_callback = selection_callback
        self.available_languages = {}
        self.available_content_types = []
        
        # Store current selections to preserve them
        self._current_language = ""
        self._current_content_type = ""
        self._current_week = ""
        
        self._setup_ui()
        # Don't scan immediately - wait for explicit call
        self._initial_scan_done = False
    
    def _setup_ui(self):
        """Setup the enhanced file selector UI with improved layout"""
        # Configure grid
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(5, weight=1)
        
        # Row 1: Content Type, Language, Week
        row = 0
        
        # Content Type selection (dropdown)
        ttk.Label(self, text="Content Type:").grid(row=row, column=0, sticky=tk.W, padx=(0, 5))
        self.content_type_var = tk.StringVar()
        self.content_type_combo = ttk.Combobox(
            self, 
            textvariable=self.content_type_var, 
            state="readonly", 
            width=15
        )
        self.content_type_combo.grid(row=row, column=1, padx=(0, 15), sticky=tk.W)
        self.content_type_combo.bind('<<ComboboxSelected>>', self._on_content_type_changed)
        
        # Language selection
        ttk.Label(self, text="Language:").grid(row=row, column=2, sticky=tk.W, padx=(0, 5))
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(
            self, 
            textvariable=self.language_var, 
            state="readonly", 
            width=18
        )
        self.language_combo.grid(row=row, column=3, padx=(0, 15), sticky=tk.W)
        self.language_combo.bind('<<ComboboxSelected>>', self._on_language_changed)
        
        # Week selection
        ttk.Label(self, text="Week:").grid(row=row, column=4, sticky=tk.W, padx=(0, 5))
        self.week_var = tk.StringVar()
        self.week_combo = ttk.Combobox(
            self, 
            textvariable=self.week_var, 
            state="readonly", 
            width=12
        )
        self.week_combo.grid(row=row, column=5, padx=(0, 15), sticky=tk.W)
        self.week_combo.bind('<<ComboboxSelected>>', self._on_week_changed)
        
        # Row 2: Browse button (spanning multiple columns)
        row = 1
        browse_frame = ttk.Frame(self)
        browse_frame.grid(row=row, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(8, 0))
        
        ttk.Button(
            browse_frame, 
            text="Browse for File...", 
            command=self._browse_for_file,
            width=20
        ).pack(side=tk.LEFT)
        
        # Status label for current selection
        self.status_var = tk.StringVar(value="Select content type and language to begin")
        self.status_label = ttk.Label(
            browse_frame, 
            textvariable=self.status_var,
            font=('Arial', 9),
            foreground='gray'
        )
        self.status_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Perform initial scan after UI is set up
        self.after_idle(self._perform_initial_scan)
    
    def _perform_initial_scan(self):
        """Perform initial directory scan after UI is fully set up"""
        if not self._initial_scan_done:
            self._scan_data_directory()
            self._initial_scan_done = True
    
    def _scan_data_directory(self):
        """Scan the data directory and populate dropdowns"""
        data_path = Path("data")
        
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created data directory at {data_path}")
            return
        
        # Scan for content types (directories in data/)
        content_types = []
        languages_by_content = {}
        
        for content_dir in data_path.iterdir():
            if content_dir.is_dir():
                # Format content type name
                content_type_display = self._format_content_type_name(content_dir.name)
                content_types.append(content_type_display)
                
                # Scan for languages in this content type
                languages = []
                for lang_dir in content_dir.iterdir():
                    if lang_dir.is_dir():
                        language_display = self._format_language_name(lang_dir.name)
                        languages.append(language_display)
                        
                        # Scan for week files
                        week_files = self._scan_week_files(lang_dir)
                        
                        # Store the mapping
                        if content_type_display not in languages_by_content:
                            languages_by_content[content_type_display] = {}
                        languages_by_content[content_type_display][language_display] = {
                            'raw_name': lang_dir.name,
                            'weeks': week_files
                        }
                
                if languages:
                    languages_by_content[content_type_display] = languages_by_content.get(content_type_display, {})
        
        self.available_content_types = sorted(content_types)
        self.available_languages = languages_by_content
        
        # Update content type dropdown
        self.content_type_combo['values'] = self.available_content_types
        if self.available_content_types:
            self.content_type_combo.set(self.available_content_types[0])
            self._current_content_type = self.available_content_types[0]
            self._on_content_type_changed()
        
        self._update_status()
    
    def _format_content_type_name(self, dir_name: str) -> str:
        """Format directory name for display"""
        # Replace underscores with spaces and capitalize first letter of each word
        formatted = dir_name.replace('_', ' ')
        return ' '.join(word.capitalize() for word in formatted.split())
    
    def _format_language_name(self, dir_name: str) -> str:
        """Format language directory name for display"""
        # For now, just return as-is, but could be enhanced for specific formatting
        return dir_name
    
    def _scan_week_files(self, lang_dir: Path) -> List[Dict[str, Any]]:
        """Scan for week files in a language directory"""
        week_files = []
        
        # Look for week{number}.json files
        for file_path in lang_dir.glob("week*.json"):
            # Extract week number from filename
            match = re.search(r'week(\d+)\.json', file_path.name, re.IGNORECASE)
            if match:
                week_number = int(match.group(1))
                week_files.append({
                    'number': week_number,
                    'display_name': f"Week {week_number}",
                    'filename': file_path.name,
                    'path': file_path
                })
        
        # Sort by week number
        week_files.sort(key=lambda x: x['number'])
        return week_files
    
    def _on_content_type_changed(self, event=None):
        """Handle content type selection change - FIXED to preserve language selection"""
        new_content_type = self.content_type_var.get()
        
        # Update current content type
        self._current_content_type = new_content_type
        
        # Get available languages for this content type
        if new_content_type in self.available_languages:
            available_languages = list(self.available_languages[new_content_type].keys())
            self.language_combo['values'] = available_languages
            
            # FIXED: Try to preserve the current language selection
            if self._current_language and self._current_language in available_languages:
                # Language is available in new content type - keep it
                self.language_combo.set(self._current_language)
                logger.info(f"Preserved language selection: {self._current_language}")
                self._on_language_changed()
            elif available_languages:
                # Language not available or not set - select first available
                self.language_combo.set(available_languages[0])
                self._current_language = available_languages[0]
                logger.info(f"Selected first available language: {self._current_language}")
                self._on_language_changed()
            else:
                # No languages available
                self.language_combo.set("")
                self._current_language = ""
                self.week_combo['values'] = []
                self.week_combo.set("")
                self._current_week = ""
        else:
            # Content type not found - reset all
            self.language_combo['values'] = []
            self.language_combo.set("")
            self._current_language = ""
            self.week_combo['values'] = []
            self.week_combo.set("")
            self._current_week = ""
        
        self._update_status()
    
    def _on_language_changed(self, event=None):
        """Handle language selection change"""
        new_language = self.language_var.get()
        content_type = self.content_type_var.get()
        
        # Update current language
        self._current_language = new_language
        
        # Update week dropdown
        if (content_type in self.available_languages and 
            new_language in self.available_languages[content_type]):
            
            lang_data = self.available_languages[content_type][new_language]
            weeks = lang_data['weeks']
            
            week_options = [week['display_name'] for week in weeks]
            self.week_combo['values'] = week_options
            
            # FIXED: Try to preserve the current week selection
            if self._current_week and self._current_week in week_options:
                # Week is available - keep it
                self.week_combo.set(self._current_week)
                logger.info(f"Preserved week selection: {self._current_week}")
                self._on_week_changed()
            elif week_options:
                # Week not available or not set - select first available
                self.week_combo.set(week_options[0])
                self._current_week = week_options[0]
                logger.info(f"Selected first available week: {self._current_week}")
                self._on_week_changed()
            else:
                # No weeks available
                self.week_combo.set("")
                self._current_week = ""
        else:
            self.week_combo['values'] = []
            self.week_combo.set("")
            self._current_week = ""
        
        self._update_status()
    
    def _on_week_changed(self, event=None):
        """Handle week selection change"""
        content_type = self.content_type_var.get()
        language = self.language_var.get()
        new_week_display = self.week_var.get()
        
        # Update current week
        self._current_week = new_week_display
        
        if (content_type and language and new_week_display and
            content_type in self.available_languages and
            language in self.available_languages[content_type]):
            
            lang_data = self.available_languages[content_type][language]
            
            # Find the selected week
            selected_week = None
            for week in lang_data['weeks']:
                if week['display_name'] == new_week_display:
                    selected_week = week
                    break
            
            if selected_week:
                file_path = selected_week['path']
                raw_content_type = self._get_raw_content_type_name(content_type)
                self.selection_callback(file_path, language, raw_content_type)
                self._update_status(f"Selected: {new_week_display} - {language} {content_type}")
                return
        
        # No valid selection
        self.selection_callback(None, "", "")
        self._update_status()
    
    def _get_raw_content_type_name(self, display_name: str) -> str:
        """Convert display name back to raw directory name"""
        # Convert "Common Phrases" back to "common_phrases"
        return display_name.lower().replace(' ', '_')
    
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
            
            # Try to determine content type and language from path
            content_type = "vocabulary"  # default
            language = "Custom"
            
            # If file is in our data structure, extract info
            try:
                parts = file_path.parts
                data_index = parts.index("data")
                if len(parts) > data_index + 2:
                    raw_content_type = parts[data_index + 1]
                    raw_language = parts[data_index + 2]
                    
                    content_type = self._format_content_type_name(raw_content_type)
                    language = self._format_language_name(raw_language)
                    
                    # Update dropdowns to match
                    if content_type in self.available_content_types:
                        self.content_type_combo.set(content_type)
                        self._current_content_type = content_type
                        self._on_content_type_changed()
                        
                        if language in self.language_combo['values']:
                            self.language_combo.set(language)
                            self._current_language = language
                            self._on_language_changed()
                            
                            # Try to select the right week
                            filename = file_path.name
                            match = re.search(r'week(\d+)\.json', filename, re.IGNORECASE)
                            if match:
                                week_num = int(match.group(1))
                                week_display = f"Week {week_num}"
                                if week_display in self.week_combo['values']:
                                    self.week_combo.set(week_display)
                                    self._current_week = week_display
            except (ValueError, IndexError):
                pass
            
            # Trigger selection
            self.selection_callback(file_path, language, self._get_raw_content_type_name(content_type))
            self._update_status(f"Custom file: {file_path.name}")
    
    def _update_status(self, message: str = None):
        """Update the status label"""
        if message:
            self.status_var.set(message)
        else:
            content_type = self.content_type_var.get()
            language = self.language_var.get()
            week = self.week_var.get()
            
            if content_type and language and week:
                self.status_var.set(f"Selected: {week} - {language} {content_type}")
            elif content_type and language:
                self.status_var.set(f"Select a week for {language} {content_type}")
            elif content_type:
                self.status_var.set(f"Select language for {content_type}")
            else:
                self.status_var.set("Select content type to begin")
    
    def get_selected_content_type(self) -> str:
        """Get currently selected content type (raw format)"""
        display_name = self.content_type_var.get()
        return self._get_raw_content_type_name(display_name) if display_name else ""
    
    def get_selected_language(self) -> str:
        """Get currently selected language"""
        return self.language_var.get()
    
    def get_selected_week(self) -> str:
        """Get currently selected week display name"""
        return self.week_var.get()
    
    def get_selected_file_path(self) -> Optional[Path]:
        """Get currently selected file path"""
        content_type = self.content_type_var.get()
        language = self.language_var.get()
        week_display = self.week_var.get()
        
        if (content_type and language and week_display and
            content_type in self.available_languages and
            language in self.available_languages[content_type]):
            
            lang_data = self.available_languages[content_type][language]
            for week in lang_data['weeks']:
                if week['display_name'] == week_display:
                    return week['path']
        
        return None
    
    def set_selection(self, content_type: str, language: str, week_number: int = None):
        """Programmatically set selection"""
        # Format content type for display
        content_type_display = self._format_content_type_name(content_type)
        
        if content_type_display in self.available_content_types:
            self.content_type_combo.set(content_type_display)
            self._current_content_type = content_type_display
            self._on_content_type_changed()
            
            if language in self.language_combo['values']:
                self.language_combo.set(language)
                self._current_language = language
                self._on_language_changed()
                
                if week_number:
                    week_display = f"Week {week_number}"
                    if week_display in self.week_combo['values']:
                        self.week_combo.set(week_display)
                        self._current_week = week_display
                        self._on_week_changed()
    
    def refresh_files(self):
        """Refresh file list by rescanning data directory"""
        # Store current selections before refresh
        current_content_type = self._current_content_type
        current_language = self._current_language
        current_week = self._current_week
        
        # Rescan directory
        self._scan_data_directory()
        
        # Try to restore previous selections
        if current_content_type and current_content_type in self.available_content_types:
            self.content_type_combo.set(current_content_type)
            self._current_content_type = current_content_type
            self._on_content_type_changed()
            
            # Language will be handled by _on_content_type_changed which preserves it
            
        logger.info("File list refreshed, selections preserved where possible")
    
    def get_available_content_types(self) -> List[str]:
        """Get list of available content types"""
        return self.available_content_types.copy()
    
    def get_available_languages(self, content_type: str = None) -> List[str]:
        """Get list of available languages for a content type"""
        if content_type and content_type in self.available_languages:
            return list(self.available_languages[content_type].keys())
        return []
    
    def get_available_weeks(self, content_type: str = None, language: str = None) -> List[str]:
        """Get list of available weeks for a content type and language"""
        if (content_type and language and 
            content_type in self.available_languages and
            language in self.available_languages[content_type]):
            
            lang_data = self.available_languages[content_type][language]
            return [week['display_name'] for week in lang_data['weeks']]
        return []
    
    # Legacy methods for compatibility with existing code
    def update_available_options(self, languages: Dict[str, Dict[str, List[Path]]], 
                                content_types: List[str]):
        """Legacy method - now handled by _scan_data_directory"""
        # This method is kept for compatibility but functionality moved to _scan_data_directory
        self._scan_data_directory()
    
    def open_file_dialog(self):
        """Public method to open file dialog"""
        self._browse_for_file()


# Example usage and testing
if __name__ == "__main__":
    def test_selection_callback(file_path, language, content_type):
        if file_path:
            print(f"Selected: {file_path}")
            print(f"Language: {language}")
            print(f"Content Type: {content_type}")
        else:
            print("No selection")
    
    # Create test window
    root = tk.Tk()
    root.title("Enhanced File Selector Test - Fixed Language Preservation")
    root.geometry("800x200")
    
    # Create selector
    selector = FileSelector(root, test_selection_callback)
    selector.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Test methods
    print("Available content types:", selector.get_available_content_types())
    print("Available languages for Vocabulary:", selector.get_available_languages("Vocabulary"))
    
    root.mainloop()