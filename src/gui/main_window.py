"""
Main Window for Language Learning Flashcard Generator
Simplified window layout and coordination - delegates to specialized components
Modified to support single-day selection and editable CSV preview
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Import core modules
from core.csv_generator import GenericLanguageCSVGenerator
from core.history_manager import HistoryManager
from config.settings import SettingsManager

# Import GUI components
from .components import (
    FileSelector, ContentSelector, CSVPreviewEditor, 
    ExportPanel, ProgressDisplay, StatusBar
)
from .dialogs import SettingsDialog, ErrorDialog
from .utils import GUIHelpers

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window - coordinates all components and handles high-level logic"""
    
    def __init__(self, root):
        """Initialize the main window"""
        self.root = root
        
        # Initialize core components
        self.settings_manager = SettingsManager()
        self.history_manager = HistoryManager()
        self.csv_generator = GenericLanguageCSVGenerator(
            output_dir=self.settings_manager.get_output_directory(),
            config=self._get_csv_generator_config()
        )
        
        # Application state
        self.current_data = None
        self.current_file_path = None
        self.current_csv_content = ""
        self.available_languages = {}
        self.available_content_types = ["vocabulary", "grammar"]
        
        # GUI state
        self._window_configured = False
        
        # Setup UI
        self._create_layout()
        self._setup_event_handlers()
        self._scan_data_directory()
        self._apply_saved_settings()
    
    def _create_layout(self):
        """Create the main window layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)  # Preview column
        main_frame.rowconfigure(1, weight=1)     # Content row
        
        # Create layout sections
        self._create_toolbar(main_frame)
        self._create_content_area(main_frame)
        self._create_bottom_panel(main_frame)
        self._create_status_bar(main_frame)
    
    def _create_toolbar(self, parent):
        """Create the top toolbar with file selection and settings"""
        toolbar_frame = ttk.Frame(parent, padding="5")
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar_frame.columnconfigure(1, weight=1)
        
        # Settings button
        ttk.Button(
            toolbar_frame, 
            text="Settings", 
            command=self._open_settings
        ).grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        # File selector component
        self.file_selector = FileSelector(
            toolbar_frame, 
            selection_callback=self._on_file_selection_changed
        )
        self.file_selector.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
    
    def _create_content_area(self, parent):
        """Create the main content area with selection panel and CSV preview"""
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        content_frame.columnconfigure(0, weight=0, minsize=300)  # Selection panel - fixed width
        content_frame.columnconfigure(1, weight=1)              # CSV preview - expandable
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Content selection (SINGLE selection only)
        self.content_selector = ContentSelector(
            content_frame, 
            selection_callback=self._on_content_selection_changed,
            selection_mode='single'  # NEW: Only allow single day/section selection
        )
        self.content_selector.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Right panel - CSV Preview Editor (NEW: Editable CSV preview)
        self.csv_preview = CSVPreviewEditor(
            content_frame,
            on_csv_changed=self._on_csv_content_changed
        )
        self.csv_preview.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
    
    def _create_bottom_panel(self, parent):
        """Create the bottom panel with export controls and progress"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Export panel
        self.export_panel = ExportPanel(
            bottom_frame, 
            export_callback=self._export_csv
        )
        self.export_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress display
        self.progress_display = ProgressDisplay(bottom_frame, self.history_manager)
        self.progress_display.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def _create_status_bar(self, parent):
        """Create the status bar at the bottom"""
        self.status_bar = StatusBar(parent)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def _setup_event_handlers(self):
        """Setup event handlers for component interactions"""
        # Window events
        self.root.bind('<Control-s>', lambda e: self._save_csv_content())
        self.root.bind('<Control-o>', lambda e: self.file_selector.open_file_dialog())
        self.root.bind('<F5>', lambda e: self._refresh_data())
    
    def _get_csv_generator_config(self) -> Dict[str, Any]:
        """Get CSV generator configuration from settings"""
        export_settings = self.settings_manager.get_export_settings()
        study_settings = self.settings_manager.get_study_settings()
        
        return {
            'tag_prefix': 'Language_Learning',
            'include_html_formatting': export_settings.html_formatting,
            'show_connections': study_settings.include_native_connections,
            'target_language': self.settings_manager.get_setting('language_learning.target_language', ''),
            'native_language': self.settings_manager.get_setting('language_learning.native_language', 'english'),
            'field_mappings': {
                'target': ['german', 'target', 'word', 'term'],
                'native': ['english', 'native', 'translation'],
                'example': ['example', 'example_sentence'],
                'pronunciation': ['pronunciation', 'phonetic'],
                'notes': ['notes', 'note', 'memory_tip']
            }
        }
    
    def _scan_data_directory(self):
        """Scan the data directory for available languages and content"""
        data_path = self.settings_manager.get_data_directory()
        
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
            self.status_bar.set_message(f"Created data directory at {data_path}")
            return
        
        # Scan for languages and content types
        for content_type in self.available_content_types:
            content_path = data_path / content_type
            if content_path.exists():
                for lang_dir in content_path.iterdir():
                    if lang_dir.is_dir():
                        lang_name = lang_dir.name
                        if lang_name not in self.available_languages:
                            self.available_languages[lang_name] = {}
                        
                        # Find JSON files in this language directory
                        json_files = list(lang_dir.glob("*.json"))
                        if json_files:
                            self.available_languages[lang_name][content_type] = json_files
        
        # Update file selector with available options
        self.file_selector.update_available_options(
            self.available_languages, 
            self.available_content_types
        )
        
        if self.available_languages:
            self.status_bar.set_message(f"Found {len(self.available_languages)} languages")
        else:
            self.status_bar.set_message("No data files found - add JSON files to data directory")
    
    def _on_file_selection_changed(self, file_path: Optional[Path], language: str, content_type: str):
        """Handle file selection change - load file and update components"""
        if file_path is None:
            self._clear_content()
            self.status_bar.set_message(f"No {content_type} files available for {language}")
            return
        
        try:
            # Load the selected file
            with open(file_path, 'r', encoding='utf-8') as f:
                import json
                self.current_data = json.load(f)
            
            self.current_file_path = file_path
            
            # Update content selector with the new data
            self.content_selector.load_data(self.current_data, content_type)
            
            # Clear CSV preview until a day is selected
            self.csv_preview.clear()
            self.current_csv_content = ""
            
            # Update export panel
            self.export_panel.set_data_loaded(True, str(file_path.name))
            
            # Add to recent files
            self.settings_manager.add_recent_file(str(file_path))
            
            self.status_bar.set_message(f"Loaded: {file_path.name}")
            logger.info(f"Loaded file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            ErrorDialog.show_error(self.root, "Load Error", f"Failed to load file: {e}")
            self._clear_content()
    
    def _on_content_selection_changed(self, selected_section: Optional[str], item_count: int):
        """Handle content selection change - generate and show CSV preview"""
        if not self.current_data or not selected_section:
            self.csv_preview.clear()
            self.current_csv_content = ""
            self.export_panel.set_selection(0, 0)
            return
        
        try:
            # Extract entries for the selected section/day
            entries = self._extract_entries_for_section(selected_section)
            
            if not entries:
                self.status_bar.set_message(f"No entries found in {selected_section}")
                return
            
            # Generate CSV content for preview
            self._generate_csv_preview(entries, selected_section)
            
            # Update export panel
            self.export_panel.set_selection(1, len(entries))  # 1 section, N items
            
            self.status_bar.set_message(f"Previewing {len(entries)} items from {selected_section}")
            
        except Exception as e:
            logger.error(f"Error generating CSV preview: {e}")
            ErrorDialog.show_error(self.root, "Preview Error", f"Failed to generate preview: {e}")
    
    def _extract_entries_for_section(self, section_key: str) -> List[Dict[str, Any]]:
        """Extract entries for a specific section/day"""
        if not self.current_data:
            return []
        
        # Handle different JSON structures
        if 'days' in self.current_data:
            day_data = self.current_data['days'].get(section_key, {})
            return day_data.get('words', [])
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_data = self.current_data[container_key].get(section_key, {})
            return section_data.get('entries', section_data.get('words', section_data.get('items', [])))
        
        elif section_key == 'main':  # Direct entries structure
            return self.current_data.get('entries', self.current_data.get('words', []))
        
        return []
    
    def _generate_csv_preview(self, entries: List[Dict[str, Any]], section_name: str):
        """Generate CSV content and show in preview editor"""
        try:
            # Prepare metadata
            language = self.file_selector.get_selected_language()
            content_type = self.file_selector.get_selected_content_type()
            
            metadata = {
                'target_language': language.lower().replace(' ', '_'),
                'content_type': content_type,
                'source_file': str(self.current_file_path.name) if self.current_file_path else '',
                'section': section_name,
                'week': self._extract_week_from_filename(str(self.current_file_path.name)) if self.current_file_path else 1,
                'topic': self._get_section_topic(section_name)
            }
            
            # Generate CSV content using the CSV generator
            formatter_config = self._get_csv_generator_config()
            from core.card_formatter import AnkiAppFormatter
            
            formatter = AnkiAppFormatter(formatter_config)
            
            # Build CSV content
            csv_lines = []
            
            # Add headers (AnkiApp format doesn't need headers, but we'll show them for editing)
            headers = formatter.get_headers()
            csv_lines.append(','.join(f'"{header}"' for header in headers))
            
            # Add data rows
            for entry in entries:
                try:
                    row = formatter.format_entry(entry, metadata)
                    # Properly escape CSV fields
                    escaped_row = []
                    for field in row:
                        field_str = str(field).replace('"', '""')  # Escape quotes
                        if ',' in field_str or '"' in field_str or '\n' in field_str:
                            escaped_row.append(f'"{field_str}"')
                        else:
                            escaped_row.append(field_str)
                    csv_lines.append(','.join(escaped_row))
                except Exception as e:
                    logger.warning(f"Failed to format entry: {e}")
                    continue
            
            self.current_csv_content = '\n'.join(csv_lines)
            
            # Show in CSV preview editor
            self.csv_preview.set_csv_content(self.current_csv_content)
            
        except Exception as e:
            logger.error(f"Error generating CSV preview: {e}")
            raise
    
    def _get_section_topic(self, section_key: str) -> str:
        """Get the topic for a section"""
        if not self.current_data:
            return ""
        
        if 'days' in self.current_data:
            return self.current_data['days'].get(section_key, {}).get('topic', '')
        
        # Add other structure handlers as needed
        return ""
    
    def _extract_week_from_filename(self, filename: str) -> int:
        """Extract week number from filename like 'week1.json'"""
        import re
        match = re.search(r'week(\d+)', filename.lower())
        return int(match.group(1)) if match else 1
    
    def _on_csv_content_changed(self, new_csv_content: str):
        """Handle CSV content changes in the preview editor"""
        self.current_csv_content = new_csv_content
        # Update export button state
        self.export_panel.set_csv_ready(bool(new_csv_content.strip()))
    
    def _export_csv(self):
        """Export the current CSV content to a file"""
        if not self.current_csv_content:
            messagebox.showwarning("Warning", "No CSV content to export")
            return
        
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            # Generate default filename
            language = self.file_selector.get_selected_language()
            content_type = self.file_selector.get_selected_content_type()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            default_filename = f"{language.replace(' ', '_')}_{content_type}_{timestamp}.csv"
            
            # Ask user for save location
            output_dir = self.settings_manager.get_output_directory()
            output_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=default_filename,
                initialdir=str(output_dir)
            )
            
            if not file_path:
                return
            
            # Save the CSV content
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(self.current_csv_content)
            
            # Count items (subtract 1 for header)
            item_count = len(self.current_csv_content.split('\n')) - 1
            
            # Update history
            session_id = self.history_manager.start_study_session(
                target_language=language,
                content_type=content_type,
                source_file=str(self.current_file_path) if self.current_file_path else ""
            )
            
            self.history_manager.end_study_session(
                session_id, 
                items_studied=item_count, 
                items_learned=item_count
            )
            
            self.history_manager.add_generated_file(
                str(file_path), 
                str(self.current_file_path) if self.current_file_path else "", 
                content_type, 
                item_count
            )
            
            # Update progress display
            self.progress_display.refresh()
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"CSV exported successfully!\n\nFile: {Path(file_path).name}\nItems: {item_count}"
            )
            
            self.status_bar.set_message(f"Exported {item_count} items to {Path(file_path).name}")
            logger.info(f"Exported CSV: {file_path}")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            ErrorDialog.show_error(self.root, "Export Error", f"Failed to export CSV: {e}")
    
    def _save_csv_content(self):
        """Save current CSV content (Ctrl+S handler)"""
        if self.current_csv_content:
            self._export_csv()
    
    def _refresh_data(self):
        """Refresh data directory scan (F5 handler)"""
        self._scan_data_directory()
        self.status_bar.set_message("Data refreshed")
    
    def _clear_content(self):
        """Clear all content displays"""
        self.current_data = None
        self.current_file_path = None
        self.current_csv_content = ""
        self.content_selector.clear()
        self.csv_preview.clear()
        self.export_panel.set_data_loaded(False)
    
    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.root, self.settings_manager)
        dialog.show()
        
        # Apply any changed settings
        self._apply_saved_settings()
    
    def _apply_saved_settings(self):
        """Apply current settings to the interface"""
        # Update appearance
        appearance_settings = self.settings_manager.get_appearance_settings()
        
        # Update window size if remember_window_position is enabled
        if appearance_settings.remember_window_position and not self._window_configured:
            geometry = f"{appearance_settings.window_width}x{appearance_settings.window_height}"
            self.root.geometry(geometry)
            self._window_configured = True
        
        # Update CSV generator config
        self.csv_generator = GenericLanguageCSVGenerator(
            output_dir=self.settings_manager.get_output_directory(),
            config=self._get_csv_generator_config()
        )
    
    def can_close(self) -> bool:
        """Check if the window can be closed (for unsaved changes)"""
        # Could check for unsaved CSV changes here
        return True
    
    def save_state(self):
        """Save current application state"""
        try:
            # Save window geometry
            geometry = self.root.geometry()
            # Could save to settings if needed
            
            logger.info("Application state saved")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def on_window_configure(self, event):
        """Handle window configuration changes"""
        # Could save window size/position here
        pass
    
    def refresh_theme(self):
        """Refresh theme after theme change"""
        # Refresh all components that need theme updates
        if hasattr(self, 'csv_preview'):
            self.csv_preview.refresh_theme()