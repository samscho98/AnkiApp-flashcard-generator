"""
CSV Preview Editor Component
Shows editable CSV content that will be exported
Replaces the old content preview with actual CSV editing
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Callable, Optional
import logging
import csv
import io

logger = logging.getLogger(__name__)


class CSVPreviewEditor(ttk.LabelFrame):
    """Widget for previewing and editing CSV content before export"""
    
    def __init__(self, parent, on_csv_changed: Optional[Callable] = None):
        super().__init__(parent, text="CSV Preview & Editor", padding="10")
        
        self.on_csv_changed = on_csv_changed
        self.current_csv_content = ""
        self._text_modified = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the CSV preview editor UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # Text area gets the space
        
        # Create toolbar
        self._create_toolbar()
        
        # Create main text editor
        self._create_text_editor()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_toolbar(self):
        """Create toolbar with CSV editing tools"""
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        toolbar_frame.columnconfigure(3, weight=1)  # Spacer
        
        # Validate CSV button
        ttk.Button(
            toolbar_frame, 
            text="Validate CSV", 
            command=self._validate_csv,
            width=12
        ).grid(row=0, column=0, padx=(0, 5))
        
        # Format CSV button
        ttk.Button(
            toolbar_frame, 
            text="Format CSV", 
            command=self._format_csv,
            width=12
        ).grid(row=0, column=1, padx=(0, 5))
        
        # Clear button
        ttk.Button(
            toolbar_frame, 
            text="Clear", 
            command=self._clear_content,
            width=8
        ).grid(row=0, column=2, padx=(0, 5))
        
        # Spacer
        ttk.Frame(toolbar_frame).grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # Info label
        self.csv_info_label = ttk.Label(
            toolbar_frame, 
            text="No CSV loaded",
            font=('Arial', 9),
            foreground='gray'
        )
        self.csv_info_label.grid(row=0, column=4, sticky=tk.E)
    
    def _create_text_editor(self):
        """Create the main CSV text editor"""
        # Create frame for text editor with scrollbars
        editor_frame = ttk.Frame(self)
        editor_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbars
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,  # Don't wrap lines for CSV
            font=('Consolas', 10),  # Monospace font for CSV
            height=15,
            undo=True,  # Enable undo/redo
            maxundo=20
        )
        self.text_editor.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add horizontal scrollbar
        h_scroll = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.text_editor.xview)
        self.text_editor.configure(xscrollcommand=h_scroll.set)
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind events
        self.text_editor.bind('<KeyRelease>', self._on_text_changed)
        self.text_editor.bind('<Button-1>', self._on_text_changed)
        self.text_editor.bind('<Control-a>', self._select_all)
        self.text_editor.bind('<Control-z>', lambda e: self.text_editor.edit_undo())
        self.text_editor.bind('<Control-y>', lambda e: self.text_editor.edit_redo())
        
        # Configure text styling
        self._setup_text_styling()
    
    def _setup_text_styling(self):
        """Setup text styling for better CSV visualization"""
        # Configure tags for different types of content
        self.text_editor.tag_configure('header', background='#e6f3ff', font=('Consolas', 10, 'bold'))
        self.text_editor.tag_configure('error', background='#ffe6e6', foreground='red')
        self.text_editor.tag_configure('warning', background='#fff2e6', foreground='orange')
    
    def _create_status_bar(self):
        """Create status bar for CSV information"""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Line/column info
        self.position_label = ttk.Label(
            status_frame, 
            text="Line 1, Column 1",
            font=('Arial', 8)
        )
        self.position_label.grid(row=0, column=0, sticky=tk.W)
        
        # CSV stats
        self.stats_label = ttk.Label(
            status_frame, 
            text="0 rows, 0 columns",
            font=('Arial', 8)
        )
        self.stats_label.grid(row=0, column=2, sticky=tk.E)
        
        # Update position on cursor move
        self.text_editor.bind('<KeyRelease>', self._update_cursor_position)
        self.text_editor.bind('<Button-1>', self._update_cursor_position)
    
    def set_csv_content(self, csv_content: str):
        """Set CSV content in the editor"""
        self.current_csv_content = csv_content
        self._text_modified = False
        
        # Clear and set content
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, csv_content)
        
        # Apply styling
        self._apply_csv_styling()
        
        # Update info
        self._update_csv_info()
        
        # Mark as unmodified
        self.text_editor.edit_modified(False)
    
    def get_csv_content(self) -> str:
        """Get current CSV content from editor"""
        return self.text_editor.get(1.0, tk.END).rstrip('\n')
    
    def clear(self):
        """Clear the CSV editor"""
        self.text_editor.delete(1.0, tk.END)
        self.current_csv_content = ""
        self._text_modified = False
        self.csv_info_label.config(text="No CSV loaded")
        self.stats_label.config(text="0 rows, 0 columns")
        self.position_label.config(text="Line 1, Column 1")
    
    def _on_text_changed(self, event=None):
        """Handle text content changes"""
        if self.text_editor.edit_modified():
            self._text_modified = True
            new_content = self.get_csv_content()
            
            # Update info
            self._update_csv_info()
            
            # Trigger callback
            if self.on_csv_changed:
                self.on_csv_changed(new_content)
            
            # Reset modified flag
            self.text_editor.edit_modified(False)
    
    def _update_cursor_position(self, event=None):
        """Update cursor position display"""
        try:
            cursor_pos = self.text_editor.index(tk.INSERT)
            line, column = cursor_pos.split('.')
            self.position_label.config(text=f"Line {line}, Column {int(column) + 1}")
        except:
            pass
    
    def _update_csv_info(self):
        """Update CSV information display"""
        try:
            content = self.get_csv_content()
            if not content.strip():
                self.csv_info_label.config(text="No CSV content")
                self.stats_label.config(text="0 rows, 0 columns")
                return
            
            # Count lines and estimate columns
            lines = content.split('\n')
            row_count = len(lines)
            
            # Try to parse first line to count columns
            col_count = 0
            if lines:
                try:
                    # Simple comma count (not perfect but good enough for display)
                    col_count = len(lines[0].split(','))
                except:
                    col_count = 0
            
            self.csv_info_label.config(text="CSV loaded - editable")
            self.stats_label.config(text=f"{row_count} rows, ~{col_count} columns")
            
        except Exception as e:
            logger.error(f"Error updating CSV info: {e}")
            self.csv_info_label.config(text="CSV parsing error")
    
    def _apply_csv_styling(self):
        """Apply syntax highlighting to CSV content"""
        try:
            # Clear existing tags
            self.text_editor.tag_remove('header', 1.0, tk.END)
            
            # Highlight first line (header)
            self.text_editor.tag_add('header', '1.0', '1.end')
            
        except Exception as e:
            logger.debug(f"Error applying CSV styling: {e}")
    
    def _validate_csv(self):
        """Validate CSV content"""
        content = self.get_csv_content()
        if not content.strip():
            messagebox.showwarning("Validation", "No CSV content to validate")
            return
        
        try:
            # Clear existing error highlighting
            self.text_editor.tag_remove('error', 1.0, tk.END)
            self.text_editor.tag_remove('warning', 1.0, tk.END)
            
            # Parse CSV to check for errors
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            
            if not rows:
                messagebox.showwarning("Validation", "CSV appears to be empty")
                return
            
            # Check for consistency
            issues = []
            header_cols = len(rows[0]) if rows else 0
            
            for i, row in enumerate(rows[1:], 1):  # Skip header
                if len(row) != header_cols:
                    issues.append(f"Row {i + 1}: Expected {header_cols} columns, found {len(row)}")
                    # Highlight problematic line
                    line_start = f"{i + 1}.0"
                    line_end = f"{i + 1}.end"
                    self.text_editor.tag_add('warning', line_start, line_end)
            
            if issues:
                issue_summary = f"Found {len(issues)} issues:\n\n" + "\n".join(issues[:10])
                if len(issues) > 10:
                    issue_summary += f"\n... and {len(issues) - 10} more"
                messagebox.showwarning("CSV Validation", issue_summary)
            else:
                messagebox.showinfo("CSV Validation", f"CSV is valid!\n\n{len(rows)} rows, {header_cols} columns")
            
        except Exception as e:
            messagebox.showerror("Validation Error", f"Failed to validate CSV:\n\n{e}")
    
    def _format_csv(self):
        """Format/prettify CSV content"""
        content = self.get_csv_content()
        if not content.strip():
            messagebox.showwarning("Format", "No CSV content to format")
            return
        
        try:
            # Parse and reformat CSV
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            
            if not rows:
                return
            
            # Rewrite CSV with consistent formatting
            output = io.StringIO()
            csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
            
            for row in rows:
                # Clean up whitespace in each cell
                cleaned_row = [cell.strip() for cell in row]
                csv_writer.writerow(cleaned_row)
            
            formatted_content = output.getvalue().rstrip('\n')
            
            # Update editor with formatted content
            self.set_csv_content(formatted_content)
            
            messagebox.showinfo("Format", "CSV has been formatted")
            
        except Exception as e:
            messagebox.showerror("Format Error", f"Failed to format CSV:\n\n{e}")
    
    def _clear_content(self):
        """Clear all content with confirmation"""
        if self._text_modified or self.get_csv_content().strip():
            if not messagebox.askyesno("Clear Content", "Are you sure you want to clear all CSV content?"):
                return
        
        self.clear()
    
    def _select_all(self, event):
        """Select all text (Ctrl+A handler)"""
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        return 'break'  # Prevent default behavior
    
    def has_content(self) -> bool:
        """Check if editor has content"""
        return bool(self.get_csv_content().strip())
    
    def is_modified(self) -> bool:
        """Check if content has been modified"""
        return self._text_modified or self.text_editor.edit_modified()
    
    def refresh_theme(self):
        """Refresh theme styling"""
        # Could update colors based on current theme
        pass
    
    def insert_sample_csv(self):
        """Insert sample CSV for testing"""
        sample_csv = '''Front,Back,Tag,,
"das Haus","the house (🇳🇱 Dutch: het huis)<br><br><i>Example: Das Haus ist groß</i>","Week1,Vocabulary",,
"gehen","to go<br><br><i>Example: Ich gehe nach Hause</i>","Week1,Vocabulary",,'''
        
        self.set_csv_content(sample_csv)
    
    def export_to_file(self, filename: str) -> bool:
        """Export current CSV content to file"""
        try:
            content = self.get_csv_content()
            if not content.strip():
                return False
            
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"Error exporting CSV to {filename}: {e}")
            return False