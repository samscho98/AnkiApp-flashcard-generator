"""
Updated Main Window for Language Learning Flashcard Generator
Uses the enhanced file selector with improved dropdown organization
Fixed for proper phrases support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import re
import secrets

# Import core modules
from core.csv_generator import GenericLanguageCSVGenerator
from core.history_manager import HistoryManager
from config.settings import SettingsManager

# Import GUI components - using enhanced file selector
from .components import (
    ContentSelector, CSVPreviewEditor, 
    ExportPanel, ProgressDisplay, StatusBar, FileSelector
)
from .dialogs import SettingsDialog, ErrorDialog
from .utils import GUIHelpers

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window with enhanced file selection"""
    
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
        
        # GUI state
        self._window_configured = False
        
        # Setup UI
        self._create_layout()
        self._setup_event_handlers()
        self._apply_saved_settings()
        
        # Initialize file selector after all components are created
        if hasattr(self, 'file_selector'):
            self.file_selector._perform_initial_scan()
    
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
        """Create the top toolbar with enhanced file selection and settings"""
        toolbar_frame = ttk.Frame(parent, padding="5")
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar_frame.columnconfigure(1, weight=1)
        
        # Settings button
        ttk.Button(
            toolbar_frame, 
            text="Settings", 
            command=self._open_settings
        ).grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        # Enhanced file selector component
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
            selection_mode='single'
        )
        self.content_selector.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Right panel - CSV Preview Editor
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
        self.root.bind('<Control-o>', lambda e: self.file_selector._browse_for_file())
        self.root.bind('<F5>', lambda e: self._refresh_data())
    
    def _get_csv_generator_config(self) -> Dict[str, Any]:
        """Get CSV generator configuration from settings"""
        export_settings = self.settings_manager.get_export_settings()
        study_settings = self.settings_manager.get_study_settings()
        
        return {
            'tag_prefix': 'Language_Learning',
            'include_html_formatting': export_settings.html_formatting,
            'show_connections': study_settings.include_native_connections,
            'show_context_indicators': True,
            'phrase_category_prefix': '💬',
            'target_language': self.settings_manager.get_setting('language_learning.target_language', ''),
            'native_language': self.settings_manager.get_setting('language_learning.native_language', 'english'),
            'field_mappings': {
                'target': ['german', 'German', 'target', 'word', 'term', 'phrase'],
                'native': ['english', 'English', 'native', 'translation'],
                'example': ['example', 'example_sentence'],
                'pronunciation': ['pronunciation', 'phonetic'],
                'notes': ['notes', 'Notes', 'note', 'memory_tip'],
                'tags': ['tags', 'Tags', 'categories', 'tag']
            }
        }
    
    def _on_file_selection_changed(self, file_path: Optional[Path], language: str, content_type: str):
        """Handle file selection change - load file and update components"""
        if file_path is None:
            self._clear_content()
            if language and content_type:
                self.status_bar.set_message(f"No files available for {language} {content_type}")
            else:
                self.status_bar.set_message("Make a selection to begin")
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
            
            # Show selection info
            week = self.file_selector.get_selected_week()
            display_name = f"{week} - {language} {self._format_content_type_display(content_type)}"
            self.status_bar.set_message(f"Loaded: {display_name}")
            logger.info(f"Loaded file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            ErrorDialog.show_error(self.root, "Load Error", f"Failed to load file: {e}")
            self._clear_content()
    
    def _format_content_type_display(self, content_type: str) -> str:
        """Format content type for display"""
        return content_type.replace('_', ' ').title()
    
    def _on_content_selection_changed(self, selected_section: Optional[str], item_count: int):
        """Handle content selection change - generate and show CSV preview"""
        if not self.current_data or not selected_section:
            self.csv_preview.clear()
            self.current_csv_content = ""
            self.export_panel.set_selection(0, 0)
            self.export_panel.set_csv_ready(False)  # ADD THIS LINE
            return
        
        try:
            # Extract entries for the selected section/day
            entries = self._extract_entries_for_section(selected_section)
            
            if not entries:
                self.status_bar.set_message(f"No entries found in {selected_section}")
                self.export_panel.set_selection(0, 0)
                self.export_panel.set_csv_ready(False)  # ADD THIS LINE
                return
            
            # Generate CSV content for preview FIRST
            self._generate_csv_preview(entries, selected_section)
            
            # THEN update export panel with the correct sequence:
            self.export_panel.set_selection(1, len(entries))  # 1 section, N items
            self.export_panel.set_csv_ready(True)  # ADD THIS LINE (moved from _generate_csv_preview)
            
            # Update status with current selection info
            week = self.file_selector.get_selected_week()
            language = self.file_selector.get_selected_language()
            content_type_display = self._format_content_type_display(self.file_selector.get_selected_content_type())
            
            self.status_bar.set_message(
                f"Previewing {len(entries)} items from {selected_section} ({week} - {language} {content_type_display})"
            )
            
        except Exception as e:
            logger.error(f"Error generating CSV preview: {e}")
            self.export_panel.set_csv_ready(False)  # ADD THIS LINE
            ErrorDialog.show_error(self.root, "Preview Error", f"Failed to generate preview: {e}")


    def _extract_entries_for_section(self, section_key: str) -> List[Dict[str, Any]]:
        """Extract entries for a specific section/day - FIXED for phrases support"""
        if not self.current_data:
            return []
        
        # Handle different JSON structures
        if 'days' in self.current_data:
            day_data = self.current_data['days'].get(section_key, {})
            # FIXED: Check phrases first, then other fields
            return day_data.get('phrases', day_data.get('words', day_data.get('entries', day_data.get('items', []))))
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_data = self.current_data[container_key].get(section_key, {})
            # FIXED: Check phrases first, then other fields
            return section_data.get('phrases', section_data.get('entries', section_data.get('words', section_data.get('items', []))))
        
        elif section_key == 'main':  # Direct entries structure
            return self.current_data.get('phrases', self.current_data.get('entries', self.current_data.get('words', [])))
        
        return []
    
    def _generate_csv_preview(self, entries: List[Dict[str, Any]], section_name: str):
        """Generate CSV content and show in preview editor - REWRITTEN for better reliability"""
        try:
            # Clear any existing content first
            self.current_csv_content = ""
            
            # Validate inputs
            if not entries:
                logger.warning("No entries provided for CSV generation")
                self.csv_preview.clear()
                return
            
            # Get basic info for metadata
            language = self.file_selector.get_selected_language()
            content_type = self.file_selector.get_selected_content_type()
            
            # Auto-detect if this is phrases content
            is_phrases = self._detect_phrases_content()
            
            # Build comprehensive metadata
            metadata = {
                'target_language': language.lower().replace(' ', '_'),
                'content_type': 'phrases' if is_phrases else content_type,
                'source_file': str(self.current_file_path.name) if self.current_file_path else '',
                'section': section_name,
                'section_topic': self._get_section_topic(section_name),
                'week': self._extract_week_from_selection(),
                'topic': self.current_data.get('topic', ''),
                'unit': self._extract_week_from_selection()
            }
            
            logger.info(f"Generating CSV preview for {len(entries)} entries, content_type: {metadata['content_type']}")
            
            # Generate CSV content
            csv_content = self._build_csv_content(entries, metadata, is_phrases)
            
            # Validate generated content
            if not csv_content or csv_content.strip() == "":
                logger.error("Generated CSV content is empty")
                self.csv_preview.clear()
                return
            
            # Store and display the content
            self.current_csv_content = csv_content
            self.csv_preview.set_csv_content(self.current_csv_content)
            
            logger.info(f"CSV preview generated successfully: {len(csv_content)} characters, {len(entries)} entries")
            
        except Exception as e:
            logger.error(f"Error generating CSV preview: {e}", exc_info=True)
            self.current_csv_content = ""
            self.csv_preview.clear()
            raise

    def _detect_phrases_content(self) -> bool:
        """Detect if the current content is phrases-based"""
        if not self.current_data:
            return False
        
        # Check multiple indicators
        indicators = [
            'phrase' in self.file_selector.get_selected_content_type().lower(),
            'phrases' in str(self.current_data).lower(),
            'total_phrases' in self.current_data,
            any('phrases' in str(day_data) for day_data in self.current_data.get('days', {}).values()),
            'common_phrase' in str(self.current_file_path).lower() if self.current_file_path else False
        ]
        
        return any(indicators)

    def _build_csv_content(self, entries: List[Dict[str, Any]], metadata: Dict[str, Any], is_phrases: bool) -> str:
        """Build CSV content using the appropriate formatter"""
        
        # Get the correct formatter
        from core.card_formatter import FormatterFactory
        formatter_type = 'phrases' if is_phrases else 'ankiapp'
        formatter_config = self._get_csv_generator_config()
        
        try:
            formatter = FormatterFactory.create_formatter(formatter_type, formatter_config)
        except Exception as e:
            logger.error(f"Failed to create formatter '{formatter_type}': {e}")
            # Fallback to basic formatter
            formatter = FormatterFactory.create_formatter('ankiapp', formatter_config)
        
        # Build CSV line by line
        csv_lines = []
        
        # Add headers
        try:
            headers = formatter.get_headers()
            if headers:
                header_line = ','.join(f'"{header}"' for header in headers)
                csv_lines.append(header_line)
        except Exception as e:
            logger.warning(f"Error getting headers: {e}")
            # Use default headers
            csv_lines.append('"Front","Back","Tag","",""')
        
        # Process each entry
        successful_entries = 0
        for i, entry in enumerate(entries):
            try:
                # Format the entry
                row = formatter.format_entry(entry, metadata)
                
                # Escape and build CSV row
                csv_row = self._escape_csv_row(row)
                csv_lines.append(csv_row)
                successful_entries += 1
                
            except Exception as e:
                logger.warning(f"Failed to format entry {i+1}: {e}")
                logger.debug(f"Problematic entry: {entry}")
                continue
        
        if successful_entries == 0:
            raise ValueError("No entries could be successfully formatted")
        
        logger.info(f"Successfully formatted {successful_entries}/{len(entries)} entries")
        return '\n'.join(csv_lines)

    def _escape_csv_row(self, row: List[str]) -> str:
        """Properly escape a CSV row"""
        escaped_fields = []
        
        for field in row:
            # Convert to string and handle None values
            field_str = str(field) if field is not None else ""
            
            # Escape quotes by doubling them
            field_str = field_str.replace('"', '""')
            
            # Wrap in quotes if needed (contains comma, quote, newline, or HTML)
            needs_quotes = any(char in field_str for char in [',', '"', '\n', '\r', '<', '>'])
            
            if needs_quotes:
                escaped_fields.append(f'"{field_str}"')
            else:
                escaped_fields.append(field_str)
        
        return ','.join(escaped_fields)
    
    def _generate_csv_with_generator(self, entries: List[Dict[str, Any]], metadata: Dict[str, Any], is_phrases: bool = False) -> str:
        """Generate CSV using the same logic as the CSV generator"""
        
        # Get the appropriate formatter
        from core.card_formatter import FormatterFactory
        formatter_type = 'phrases' if is_phrases else 'ankiapp'
        formatter_config = self._get_csv_generator_config()
        formatter = FormatterFactory.create_formatter(formatter_type, formatter_config)
        
        # Build CSV content
        csv_lines = []
        
        # Add headers (for preview purposes)
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
                    if ',' in field_str or '"' in field_str or '\n' in field_str or '<' in field_str:
                        escaped_row.append(f'"{field_str}"')
                    else:
                        escaped_row.append(field_str)
                csv_lines.append(','.join(escaped_row))
            except Exception as e:
                logger.warning(f"Failed to format entry: {e}")
                continue
        
        return '\n'.join(csv_lines)
    
    def _extract_week_from_selection(self) -> int:
        """Extract week number from current selection"""
        try:
            week_display = self.file_selector.get_selected_week()
            # Extract number from "Week 5" format
            import re
            match = re.search(r'week\s+(\d+)', week_display, re.IGNORECASE)
            if match:
                return int(match.group(1))
            
            # Fallback to data
            if self.current_data and 'week' in self.current_data:
                return int(self.current_data['week'])
            
            # Default fallback
            return 1
        except (ValueError, AttributeError, TypeError):
            # If anything goes wrong, return 1
            return 1
    
    def _get_section_topic(self, section_key: str) -> str:
        """Get the topic for a section"""
        if not self.current_data:
            return ""
        
        if 'days' in self.current_data:
            return self.current_data['days'].get(section_key, {}).get('topic', '')
        
        # Add other structure handlers as needed
        return ""
    
    def _on_csv_content_changed(self, new_csv_content: str):
        """Handle CSV content changes in the preview editor"""
        self.current_csv_content = new_csv_content
        # Update export button state
        self.export_panel.set_csv_ready(bool(new_csv_content.strip()))
    
    def _export_csv(self):
        """Export the current CSV content to a file - FIXED to remove headers"""
        if not self.current_csv_content:
            messagebox.showwarning("Warning", "No CSV content to export")
            return
        
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            # Generate enhanced filename format
            language = self.file_selector.get_selected_language()
            content_type_display = self._format_content_type_display(self.file_selector.get_selected_content_type())
            week = self.file_selector.get_selected_week()
            section_key = self.content_selector.get_selected_section()  # Get selected day/section
            
            # Generate new filename format: Language_Week_Day_Category_ID.csv
            default_filename = self._generate_new_filename(language, content_type_display, week, section_key)
            
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
            
            # FIXED: Remove header row before saving
            csv_lines = self.current_csv_content.split('\n')
            
            # Skip the first line (headers) and keep only data rows
            data_lines = [line for line in csv_lines[1:] if line.strip()]  # Also remove empty lines
            
            # Join back without headers
            csv_content_no_headers = '\n'.join(data_lines)
            
            # Save the CSV content WITHOUT headers
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_content_no_headers)
            
            # Count items (no need to subtract 1 for header since we removed it)
            item_count = len(data_lines)
            
            # Update history
            session_id = self.history_manager.start_study_session(
                target_language=language,
                content_type=self.file_selector.get_selected_content_type(),
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
                self.file_selector.get_selected_content_type(), 
                item_count
            )
            
            # Update progress display
            self.progress_display.refresh()
            
            # Show success message with better info
            week = self.file_selector.get_selected_week()
            content_type_display = self._format_content_type_display(self.file_selector.get_selected_content_type())
            
            messagebox.showinfo(
                "Success", 
                f"CSV exported successfully!\n\n"
                f"Content: {week} - {language} {content_type_display}\n"
                f"Items: {item_count} flashcards\n"
                f"File: {Path(file_path).name}\n\n"
                f"✅ Ready for AnkiApp import!"
            )
            
            self.status_bar.set_message(f"Exported {item_count} flashcards to {Path(file_path).name}")
            logger.info(f"Exported CSV without headers: {file_path} ({item_count} cards)")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            ErrorDialog.show_error(self.root, "Export Error", f"Failed to export CSV: {e}")

    # OPTIONAL: Add a method to preview what will be exported (without headers)

    def _generate_new_filename(self, language, content_type, week, section_key=""):
        """Generate filename: Language_Week_Day_Category_ID.csv"""
        
        # Clean language name
        language_clean = language.replace(' ', '_').replace('-', '_')
        
        # Extract week number (from "Week 1" -> "Week1")
        week_match = re.search(r'week\s*(\d+)', week, re.IGNORECASE)
        week_num = week_match.group(1) if week_match else "1"
        week_clean = f"Week{week_num}"
        
        # Extract day number from section (from "day_1" -> "Day1")
        day_clean = "Day1"  # Default
        if section_key:
            day_match = re.search(r'day[_\s]*(\d+)', section_key, re.IGNORECASE)
            if day_match:
                day_clean = f"Day{day_match.group(1)}"
        
        # Standardize content type
        if 'phrase' in content_type.lower():
            content_clean = 'Phrases'
        elif 'grammar' in content_type.lower():
            content_clean = 'Grammar'
        else:
            content_clean = 'Vocabulary'
        
        # Generate random 6-character ID
        random_id = secrets.token_hex(3)  # Creates abc123 format
        
        # Build final filename
        filename = f"{language_clean}_{week_clean}_{day_clean}_{content_clean}_{random_id}.csv"
        
        return filename

    def _preview_export_content(self):
        """Preview what will actually be exported (without headers)"""
        if not self.current_csv_content:
            return ""
        
        csv_lines = self.current_csv_content.split('\n')
        data_lines = [line for line in csv_lines[1:] if line.strip()]
        return '\n'.join(data_lines)
    
    def _save_csv_content(self):
        """Save current CSV content (Ctrl+S handler)"""
        if self.current_csv_content:
            self._export_csv()
    
    def _refresh_data(self):
        """Refresh data directory scan (F5 handler)"""
        self.file_selector.refresh_files()
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
