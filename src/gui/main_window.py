"""
Main Window for Language Learning Flashcard Generator
Integrates with existing core modules and configuration system
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Import from existing core modules
from core.csv_generator import GenericLanguageCSVGenerator
from core.history_manager import HistoryManager
from config.settings import SettingsManager
from .widgets import FileSelector, ContentSelector, ContentPreview, ExportPanel, ProgressDisplay
from .settings_window import SettingsWindow

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window using existing modular structure"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Language Learning Flashcard Generator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
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
        self.available_languages = {}
        self.available_content_types = ["vocabulary", "grammar"]
        
        # Setup UI
        self.setup_ui()
        self.scan_data_directory()
        
        # Apply saved settings
        self.apply_settings()
    
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
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create top control panel
        self.create_control_panel(main_frame)
        
        # Create content area with custom widgets
        self.create_content_area(main_frame)
        
        # Create bottom panels
        self.create_bottom_panels(main_frame)
    
    def create_control_panel(self, parent):
        """Create the top control panel with dropdowns and settings"""
        control_frame = ttk.Frame(parent, padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Settings button
        ttk.Button(control_frame, text="Settings", command=self.open_settings).grid(
            row=0, column=0, padx=(0, 10), sticky=tk.W
        )
        
        # File selector widget
        self.file_selector = FileSelector(control_frame, self.on_file_selection_changed)
        self.file_selector.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
    
    def create_content_area(self, parent):
        """Create the main content area with selection panel and preview"""
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Content selection (using custom widget)
        self.content_selector = ContentSelector(content_frame, self.on_content_selection_changed)
        self.content_selector.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Right panel - Preview (using custom widget)
        self.content_preview = ContentPreview(content_frame)
        self.content_preview.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
    
    def create_bottom_panels(self, parent):
        """Create the bottom panels for export and progress"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Export panel (using custom widget)
        self.export_panel = ExportPanel(bottom_frame, self.export_to_csv)
        self.export_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress display (using custom widget)
        self.progress_display = ProgressDisplay(bottom_frame, self.history_manager)
        self.progress_display.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def scan_data_directory(self):
        """Scan the data directory for available languages and content"""
        data_path = self.settings_manager.get_data_directory()
        
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
            messagebox.showinfo("Info", f"Created data directory at {data_path}. Please add your JSON files.")
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
        self.file_selector.update_available_options(self.available_languages, self.available_content_types)
    
    def on_file_selection_changed(self, file_path: Path, language: str, content_type: str):
        """Handle file selection change from FileSelector widget"""
        if file_path is None:
            # No file available for this language/content type combination
            logger.info(f"No {content_type} files available for {language}")
            self.clear_content_display()
            # Explicitly load empty data to ensure content selector is cleared
            self.content_selector.load_data(None, content_type)
            return
            
        try:
            # Load the selected file
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_data = json.load(f)
            
            self.current_file_path = file_path
            
            # Update content selector with the new data and content type
            self.content_selector.load_data(self.current_data, content_type)
            
            # Update export panel
            self.export_panel.set_data_loaded(True, str(file_path.name))
            
            # Add to recent files
            self.settings_manager.add_recent_file(str(file_path))
            
            logger.info(f"Loaded file: {file_path} (content type: {content_type})")
            
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to load file: {e}")
            self.clear_content_display()
    
    def on_content_selection_changed(self, selected_sections: List[str], total_items: int):
        """Handle content selection change from ContentSelector widget"""
        if self.current_data and selected_sections:
            # Update preview
            self.content_preview.update_preview(self.current_data, selected_sections)
            
            # Update export panel
            self.export_panel.set_selection(len(selected_sections), total_items)
        else:
            self.content_preview.clear_preview()
            self.export_panel.set_selection(0, 0)
    
    def export_to_csv(self):
        """Export selected content to AnkiApp CSV format"""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        selected_sections = self.content_selector.get_selected_sections()
        if not selected_sections:
            messagebox.showwarning("Warning", "No content selected")
            return
        
        try:
            # Generate filename based on settings
            export_settings = self.settings_manager.get_export_settings()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            language = self.file_selector.get_selected_language()
            content_type = self.file_selector.get_selected_content_type()
            
            if export_settings.include_date_in_filename:
                filename = export_settings.filename_template.format(
                    category=language.replace(" ", "_"),
                    subcategory=content_type,
                    date=timestamp
                ) + ".csv"
            else:
                filename = f"{language.replace(' ', '_')}_{content_type}.csv"
            
            # Ensure output directory exists and get proper path
            output_dir = self.settings_manager.get_output_directory()
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename,
                initialdir=str(output_dir)
            )
            
            if not file_path:
                return
            
            # Debug information
            logger.info(f"Current data keys: {list(self.current_data.keys())}")
            logger.info(f"Selected sections: {selected_sections}")
            
            # Extract entries from selected sections - IMPROVED LOGIC
            entries_to_export = []
            
            if 'days' in self.current_data:
                # Week-based structure with days
                logger.info("Processing days structure")
                days_data = self.current_data['days']
                
                # Map selected sections to actual day keys
                for section in selected_sections:
                    # Try direct match first
                    if section in days_data:
                        day_data = days_data[section]
                        words = day_data.get('words', [])
                        entries_to_export.extend(words)
                        logger.info(f"Found {len(words)} words in {section}")
                    else:
                        # Try to find matching day by looking for day number
                        # section might be "day_1" but displayed as "Day 1 - Topic"
                        for day_key, day_data in days_data.items():
                            if section.lower().replace(' ', '_').startswith(day_key.lower()) or \
                            day_key.lower().replace('_', ' ') in section.lower():
                                words = day_data.get('words', [])
                                entries_to_export.extend(words)
                                logger.info(f"Found {len(words)} words in {day_key} (matched from {section})")
                                break
            
            elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
                # Handle lessons/chapters/sections structure
                container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
                logger.info(f"Processing {container_key} structure")
                container = self.current_data[container_key]
                
                for section in selected_sections:
                    if section in container:
                        section_data = container[section]
                        items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                        entries_to_export.extend(items)
                        logger.info(f"Found {len(items)} items in {section}")
            
            elif 'entries' in self.current_data:
                # Direct entries structure
                logger.info("Processing direct entries structure")
                entries_to_export = self.current_data['entries']
                logger.info(f"Found {len(entries_to_export)} entries")
            
            elif 'words' in self.current_data:
                # Direct words structure
                logger.info("Processing direct words structure")
                entries_to_export = self.current_data['words']
                logger.info(f"Found {len(entries_to_export)} words")
            
            logger.info(f"Total entries to export: {len(entries_to_export)}")
            
            # If still no entries, try a more aggressive search
            if not entries_to_export:
                logger.warning("No entries found with normal logic, trying comprehensive search...")
                entries_to_export = self._find_all_entries_in_data(self.current_data)
                logger.info(f"Comprehensive search found: {len(entries_to_export)} entries")
            
            if not entries_to_export:
                error_msg = f"No entries found to export.\n\nData structure: {list(self.current_data.keys())}\nSelected sections: {selected_sections}"
                messagebox.showwarning("Warning", error_msg)
                logger.error(error_msg)
                return
            
            # Start progress tracking
            session_id = self.history_manager.start_study_session(
                target_language=language,
                content_type=content_type,
                source_file=str(self.current_file_path)
            )
            
            # Prepare metadata
            metadata = {
                'target_language': language.lower().replace(' ', '_'),
                'content_type': content_type,
                'source_file': str(self.current_file_path.name),
                'week': self._extract_week_from_filename(str(self.current_file_path.name)),
                'topic': self.current_data.get('topic', '')
            }
            
            # Generate CSV using existing core module
            csv_path = self.csv_generator.generate_from_entries(
                entries_to_export,
                metadata=metadata,
                output_filename=Path(file_path).name,
                custom_config=self._get_csv_generator_config()
            )
            
            if csv_path:
                # Move to user-selected location if different
                if str(csv_path) != file_path:
                    Path(csv_path).replace(file_path)
                    csv_path = file_path
                
                # Count exported items
                item_count = len(entries_to_export)
                
                # Update history
                self.history_manager.end_study_session(session_id, items_studied=item_count, items_learned=item_count)
                self.history_manager.add_generated_file(str(csv_path), str(self.current_file_path), content_type, item_count)
                
                # Update progress display
                self.progress_display.refresh()
                
                # Show success message
                messagebox.showinfo("Success", f"CSV exported successfully!\n\nFile: {Path(csv_path).name}\nItems: {item_count}")
                
                logger.info(f"Exported {item_count} items to {csv_path}")
            else:
                messagebox.showerror("Error", "Failed to generate CSV")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Error", f"Failed to export CSV: {e}")

    def _find_all_entries_in_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recursively find all entries in the data structure"""
        entries = []
        
        def extract_entries(obj, path=""):
            if isinstance(obj, dict):
                # Check for direct entry collections
                for key in ['entries', 'words', 'items']:
                    if key in obj and isinstance(obj[key], list):
                        logger.info(f"Found {len(obj[key])} {key} at {path}.{key}")
                        entries.extend(obj[key])
                
                # Recurse into nested objects
                for key, value in obj.items():
                    if key not in ['entries', 'words', 'items']:
                        extract_entries(value, f"{path}.{key}" if path else key)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_entries(item, f"{path}[{i}]")
        
        extract_entries(data)
        return entries

    def _extract_week_from_filename(self, filename: str) -> int:
        """Extract week number from filename like 'week1.json'"""
        import re
        match = re.search(r'week(\d+)', filename.lower())
        return int(match.group(1)) if match else 1  
    
    def clear_content_display(self):
        """Clear all content displays"""
        self.current_data = None
        self.current_file_path = None
        self.content_selector.clear()
        self.content_preview.clear_preview()
        self.export_panel.set_data_loaded(False)
    
    def open_settings(self):
        """Open settings window"""
        settings_window = SettingsWindow(self.root, self.settings_manager)
        settings_window.show()
        
        # Apply any changed settings
        self.apply_settings()
    
    def apply_settings(self):
        """Apply current settings to the interface"""
        # Update appearance
        appearance_settings = self.settings_manager.get_appearance_settings()
        
        # Update window size if remember_window_position is enabled
        if appearance_settings.remember_window_position:
            geometry = f"{appearance_settings.window_width}x{appearance_settings.window_height}"
            self.root.geometry(geometry)
        
        # Update CSV generator config
        self.csv_generator = GenericLanguageCSVGenerator(
            output_dir=self.settings_manager.get_output_directory(),
            config=self._get_csv_generator_config()
        )
        
        # Refresh data directory scan in case paths changed
        self.scan_data_directory()


class LanguageLearningApp:
    """Main application class - wrapper for backwards compatibility"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root)
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")


def main():
    """Main entry point"""
    app = LanguageLearningApp()
    app.run()


if __name__ == "__main__":
    main()