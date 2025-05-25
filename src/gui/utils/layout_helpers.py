"""
Layout Helper Functions
Utilities for creating common layout patterns and managing widget positioning
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Tuple, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class LayoutHelpers:
    """Collection of layout and positioning utility functions"""
    
    @staticmethod
    def create_scrollable_frame(parent, **kwargs) -> Tuple[tk.Frame, ttk.Scrollbar, ttk.Scrollbar]:
        """
        Create a scrollable frame with both horizontal and vertical scrollbars
        
        Returns:
            Tuple of (scrollable_frame, vertical_scrollbar, horizontal_scrollbar)
        """
        # Create canvas and scrollbars
        canvas = tk.Canvas(parent, **kwargs)
        v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        
        # Create the scrollable frame
        scrollable_frame = tk.Frame(canvas)
        
        # Configure canvas scrolling
        canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Update scroll region when frame size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # Update the scrollable frame width to match canvas width
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Grid layout for the scrollable area
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure parent grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', bind_to_mousewheel)
        canvas.bind('<Leave>', unbind_from_mousewheel)
        
        return scrollable_frame, v_scrollbar, h_scrollbar
    
    @staticmethod
    def create_labeled_entry(parent, label_text: str, entry_width: int = 20, **entry_kwargs) -> Tuple[ttk.Label, ttk.Entry]:
        """
        Create a label and entry pair
        
        Returns:
            Tuple of (label, entry)
        """
        label = ttk.Label(parent, text=label_text)
        entry = ttk.Entry(parent, width=entry_width, **entry_kwargs)
        return label, entry
    
    @staticmethod
    def create_button_row(parent, buttons_config: Dict[str, Dict[str, Any]], 
                         spacing: int = 10) -> Tuple[ttk.Frame, Dict[str, ttk.Button]]:
        """
        Create a row of buttons with consistent spacing
        
        Args:
            parent: Parent widget
            buttons_config: Dict of {button_name: {button_kwargs}}
            spacing: Spacing between buttons
            
        Returns:
            Tuple of (button_frame, {button_name: button_widget})
        """
        button_frame = ttk.Frame(parent)
        buttons = {}
        
        for i, (name, config) in enumerate(buttons_config.items()):
            button = ttk.Button(button_frame, **config)
            padx = (0, spacing) if i < len(buttons_config) - 1 else (0, 0)
            button.grid(row=0, column=i, padx=padx, sticky="ew")
            buttons[name] = button
        
        return button_frame, buttons
    
    @staticmethod
    def create_form_layout(parent, fields: List[Dict[str, Any]], 
                          label_width: int = 15) -> Tuple[ttk.Frame, Dict[str, ttk.Entry]]:
        """
        Create a form layout with labels and entries
        
        Args:
            parent: Parent widget
            fields: List of field definitions: [{'name': str, 'label': str, 'type': str, ...}]
            label_width: Width of labels
            
        Returns:
            Tuple of (form_frame, {field_name: entry_widget})
        """
        form_frame = ttk.Frame(parent)
        entries = {}
        
        for i, field in enumerate(fields):
            name = field['name']
            label_text = field['label']
            field_type = field.get('type', 'entry')
            
            # Create label
            label = ttk.Label(form_frame, text=label_text, width=label_width)
            label.grid(row=i, column=0, sticky="w", padx=(0, 10), pady=2)
            
            # Create input widget based on type
            if field_type == 'entry':
                widget = ttk.Entry(form_frame, **field.get('kwargs', {}))
            elif field_type == 'combobox':
                widget = ttk.Combobox(form_frame, **field.get('kwargs', {}))
            elif field_type == 'spinbox':
                widget = ttk.Spinbox(form_frame, **field.get('kwargs', {}))
            elif field_type == 'text':
                widget = tk.Text(form_frame, **field.get('kwargs', {}))
            else:
                widget = ttk.Entry(form_frame)
            
            widget.grid(row=i, column=1, sticky="ew", pady=2)
            entries[name] = widget
        
        # Configure column weights
        form_frame.columnconfigure(1, weight=1)
        
        return form_frame, entries
    
    @staticmethod
    def create_notebook_with_tabs(parent, tabs_config: Dict[str, Dict[str, Any]]) -> Tuple[ttk.Notebook, Dict[str, ttk.Frame]]:
        """
        Create a notebook widget with tabs
        
        Args:
            parent: Parent widget
            tabs_config: Dict of {tab_name: {'text': str, 'kwargs': dict}}
            
        Returns:
            Tuple of (notebook, {tab_name: tab_frame})
        """
        notebook = ttk.Notebook(parent)
        tabs = {}
        
        for tab_name, config in tabs_config.items():
            frame = ttk.Frame(notebook, **config.get('kwargs', {}))
            notebook.add(frame, text=config.get('text', tab_name))
            tabs[tab_name] = frame
        
        return notebook, tabs
    
    @staticmethod
    def create_panedwindow(parent, orientation: str = 'horizontal', 
                          panes: List[Dict[str, Any]] = None) -> Tuple[ttk.PanedWindow, List[ttk.Frame]]:
        """
        Create a paned window with multiple panes
        
        Args:
            parent: Parent widget
            orientation: 'horizontal' or 'vertical'
            panes: List of pane configurations
            
        Returns:
            Tuple of (panedwindow, [pane_frames])
        """
        orient = tk.HORIZONTAL if orientation == 'horizontal' else tk.VERTICAL
        paned = ttk.PanedWindow(parent, orient=orient)
        
        pane_frames = []
        
        if panes:
            for pane_config in panes:
                frame = ttk.Frame(paned, **pane_config.get('kwargs', {}))
                paned.add(frame, **pane_config.get('add_kwargs', {}))
                pane_frames.append(frame)
        
        return paned, pane_frames
    
    @staticmethod
    def create_toolbar(parent, tools: List[Dict[str, Any]], 
                      relief: str = 'raised') -> Tuple[ttk.Frame, Dict[str, Union[ttk.Button, ttk.Separator]]]:
        """
        Create a toolbar with buttons and separators
        
        Args:
            parent: Parent widget
            tools: List of tool definitions
            relief: Frame relief style
            
        Returns:
            Tuple of (toolbar_frame, {tool_name: widget})
        """
        toolbar = ttk.Frame(parent, relief=relief, borderwidth=1, padding="2")
        widgets = {}
        
        for i, tool in enumerate(tools):
            tool_type = tool.get('type', 'button')
            name = tool.get('name', f'tool_{i}')
            
            if tool_type == 'button':
                widget = ttk.Button(toolbar, **tool.get('kwargs', {}))
                widget.pack(side=tk.LEFT, padx=2)
            elif tool_type == 'separator':
                widget = ttk.Separator(toolbar, orient=tk.VERTICAL)
                widget.pack(side=tk.LEFT, fill=tk.Y, padx=5)
            else:
                continue
            
            widgets[name] = widget
        
        return toolbar, widgets
    
    @staticmethod
    def create_status_panel(parent, sections: List[Dict[str, Any]]) -> Tuple[ttk.Frame, Dict[str, ttk.Label]]:
        """
        Create a status panel with multiple sections
        
        Args:
            parent: Parent widget
            sections: List of section definitions
            
        Returns:
            Tuple of (status_frame, {section_name: label})
        """
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        labels = {}
        
        for i, section in enumerate(sections):
            name = section['name']
            text = section.get('text', name)
            width = section.get('width', 0)
            anchor = section.get('anchor', 'w')
            
            label = ttk.Label(status_frame, text=text, width=width, anchor=anchor)
            
            if section.get('expand', False):
                label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            else:
                label.pack(side=tk.LEFT, padx=2)
            
            # Add separator between sections (except last)
            if i < len(sections) - 1:
                sep = ttk.Separator(status_frame, orient=tk.VERTICAL)
                sep.pack(side=tk.LEFT, fill=tk.Y, padx=2)
            
            labels[name] = label
        
        return status_frame, labels
    
    @staticmethod
    def configure_grid_weights(widget, row_weights: Dict[int, int] = None, 
                              col_weights: Dict[int, int] = None):
        """
        Configure grid row and column weights for a widget
        
        Args:
            widget: Widget to configure
            row_weights: Dict of {row_index: weight}
            col_weights: Dict of {col_index: weight}
        """
        if row_weights:
            for row, weight in row_weights.items():
                widget.grid_rowconfigure(row, weight=weight)
        
        if col_weights:
            for col, weight in col_weights.items():
                widget.grid_columnconfigure(col, weight=weight)
    
    @staticmethod
    def create_resizable_columns(widget, columns: Union[List[int], int]):
        """
        Make specific columns resizable (weight=1)
        
        Args:
            widget: Widget to configure
            columns: List of column indices or single column index
        """
        if isinstance(columns, int):
            columns = [columns]
        
        for col in columns:
            widget.grid_columnconfigure(col, weight=1)
    
    @staticmethod
    def create_resizable_rows(widget, rows: Union[List[int], int]):
        """
        Make specific rows resizable (weight=1)
        
        Args:
            widget: Widget to configure  
            rows: List of row indices or single row index
        """
        if isinstance(rows, int):
            rows = [rows]
        
        for row in rows:
            widget.grid_rowconfigure(row, weight=1)
    
    @staticmethod
    def center_widget_in_parent(widget, parent):
        """Center a widget within its parent using place geometry"""
        widget.place(relx=0.5, rely=0.5, anchor="center")
    
    @staticmethod
    def create_loading_overlay(parent, message: str = "Loading...") -> tk.Toplevel:
        """
        Create a loading overlay window
        
        Returns:
            Toplevel window that can be destroyed when loading is complete
        """
        overlay = tk.Toplevel(parent)
        overlay.title("")
        overlay.geometry("200x100")
        overlay.transient(parent)
        overlay.grab_set()
        overlay.resizable(False, False)
        
        # Remove window decorations
        overlay.overrideredirect(True)
        
        # Center on parent
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 100
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 50
        overlay.geometry(f"200x100+{x}+{y}")
        
        # Create content
        frame = ttk.Frame(overlay, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=message, font=('Arial', 12)).pack(pady=10)
        
        # Progress bar
        progress = ttk.Progressbar(frame, mode='indeterminate')
        progress.pack(fill=tk.X, pady=10)
        progress.start()
        
        return overlay