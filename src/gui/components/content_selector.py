"""
Content Selector Component - Modified for single selection only
Shows days/sections in a list where only one can be selected at a time
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ContentSelector(ttk.LabelFrame):
    """Widget for selecting a single content section from loaded data"""
    
    def __init__(self, parent, selection_callback: Callable, selection_mode: str = 'single'):
        super().__init__(parent, text="Select Day/Section", padding="10")
        
        self.selection_callback = selection_callback
        self.selection_mode = selection_mode  # 'single' or 'multiple' (future use)
        self.current_data = None
        self.content_type = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the content selector UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create listbox with scrollbar for single selection
        list_frame = ttk.Frame(self)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Single selection listbox
        self.listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.SINGLE,  # Only allow single selection
            height=10
        )
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.listbox.bind('<<ListboxSelect>>', self._on_selection_changed)
        
        # Add info label
        info_frame = ttk.Frame(self)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.info_label = ttk.Label(
            info_frame, 
            text="Select one day/section to preview",
            font=('Arial', 9),
            foreground='gray'
        )
        self.info_label.pack()
    
    def load_data(self, data: Dict[str, Any], content_type: str):
        """Load data and populate the list"""
        self.current_data = data
        self.content_type = content_type
        self.listbox.delete(0, tk.END)
        
        if not data:
            self.info_label.config(text="No data loaded")
            self._trigger_selection_callback(None, 0)
            return
        
        # Handle different JSON structures
        sections_added = 0
        
        if 'days' in data:
            # Week-based structure with days
            days = data['days']
            for day_key in sorted(days.keys()):  # Sort to ensure consistent order
                day_data = days[day_key]
                topic = day_data.get('topic', 'No topic')
                word_count = len(day_data.get('words', []))
                
                display_text = f"{day_key.replace('_', ' ').title()} - {topic} ({word_count} items)"
                self.listbox.insert(tk.END, display_text)
                sections_added += 1
        
        elif any(key in data for key in ['lessons', 'chapters', 'sections']):
            # Handle lessons/chapters/sections structure
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in data)
            container = data[container_key]
            
            for section_key in sorted(container.keys()):
                section_data = container[section_key]
                topic = section_data.get('topic', section_data.get('title', 'No topic'))
                items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                
                display_text = f"{section_key.replace('_', ' ').title()} - {topic} ({len(items)} items)"
                self.listbox.insert(tk.END, display_text)
                sections_added += 1
        
        elif 'entries' in data or 'words' in data:
            # Direct entries structure - single item
            items = data.get('entries', data.get('words', []))
            display_text = f"All items ({len(items)} total)"
            self.listbox.insert(tk.END, display_text)
            sections_added += 1
        
        # Update info label
        if sections_added == 0:
            self.info_label.config(text="No sections found in data")
        else:
            self.info_label.config(text=f"{sections_added} sections available - select one")
        
        # Auto-select first item if only one section
        if sections_added == 1:
            self.listbox.selection_set(0)
            self._on_selection_changed()
    
    def _on_selection_changed(self, event=None):
        """Handle selection change"""
        selection = self.listbox.curselection()
        
        if not selection or not self.current_data:
            self._trigger_selection_callback(None, 0)
            return
        
        selected_index = selection[0]
        selected_section_key = None
        item_count = 0
        
        # Map selection back to section key
        if 'days' in self.current_data:
            day_keys = sorted(self.current_data['days'].keys())
            if selected_index < len(day_keys):
                selected_section_key = day_keys[selected_index]
                item_count = len(self.current_data['days'][selected_section_key].get('words', []))
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_keys = sorted(self.current_data[container_key].keys())
            if selected_index < len(section_keys):
                selected_section_key = section_keys[selected_index]
                section_data = self.current_data[container_key][selected_section_key]
                items = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                item_count = len(items)
        
        elif selected_index == 0:  # Direct entries structure
            selected_section_key = 'main'
            item_count = len(self.current_data.get('entries', self.current_data.get('words', [])))
        
        self._trigger_selection_callback(selected_section_key, item_count)
    
    def _trigger_selection_callback(self, section_key: Optional[str], item_count: int):
        """Trigger the selection callback"""
        try:
            self.selection_callback(section_key, item_count)
        except Exception as e:
            logger.error(f"Error in selection callback: {e}")
    
    def get_selected_section(self) -> Optional[str]:
        """Get currently selected section key"""
        selection = self.listbox.curselection()
        if not selection or not self.current_data:
            return None
        
        selected_index = selection[0]
        
        if 'days' in self.current_data:
            day_keys = sorted(self.current_data['days'].keys())
            return day_keys[selected_index] if selected_index < len(day_keys) else None
        
        elif any(key in self.current_data for key in ['lessons', 'chapters', 'sections']):
            container_key = next(key for key in ['lessons', 'chapters', 'sections'] if key in self.current_data)
            section_keys = sorted(self.current_data[container_key].keys())
            return section_keys[selected_index] if selected_index < len(section_keys) else None
        
        elif selected_index == 0:
            return 'main'
        
        return None
    
    def clear(self):
        """Clear the content list"""
        self.listbox.delete(0, tk.END)
        self.current_data = None
        self.content_type = None
        self.info_label.config(text="No data loaded")
        self._trigger_selection_callback(None, 0)
    
    def select_first(self):
        """Select the first item in the list"""
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self._on_selection_changed()
    
    def get_selection_count(self) -> int:
        """Get number of items in current selection"""
        return len(self.listbox.curselection())
    
    def is_selection_valid(self) -> bool:
        """Check if current selection is valid"""
        return self.get_selection_count() > 0 and self.current_data is not None