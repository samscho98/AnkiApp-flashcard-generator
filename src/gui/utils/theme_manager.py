"""
Theme Manager for consistent GUI styling
Handles theme switching and style management
"""

import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        """Initialize theme manager"""
        self.style = ttk.Style()
        self.current_theme = "system"
        self.theme_config = self._load_theme_config()
        
        # Available themes
        self.available_themes = {
            'system': 'System Default',
            'light': 'Light Theme',
            'dark': 'Dark Theme',
            'blue': 'Blue Theme'
        }
    
    def _load_theme_config(self) -> Dict[str, Any]:
        """Load theme configuration from file"""
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "themes.json"
        
        # Default theme configuration
        default_config = {
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'button_bg': '#f0f0f0',
                'button_fg': '#000000'
            },
            'dark': {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'select_bg': '#404040',
                'select_fg': '#ffffff',
                'entry_bg': '#404040',
                'entry_fg': '#ffffff',
                'button_bg': '#505050',
                'button_fg': '#ffffff'
            }
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for theme_name, theme_data in default_config.items():
                        if theme_name not in loaded_config:
                            loaded_config[theme_name] = theme_data
                    return loaded_config
        except Exception as e:
            logger.warning(f"Failed to load theme config: {e}")
        
        return default_config
    
    def get_style(self) -> ttk.Style:
        """Get the ttk Style object"""
        return self.style
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get dictionary of available themes"""
        return self.available_themes.copy()
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the application"""
        try:
            if theme_name == 'system':
                self._apply_system_theme()
            elif theme_name in self.theme_config:
                self._apply_custom_theme(theme_name)
            else:
                logger.warning(f"Unknown theme: {theme_name}")
                return
            
            self.current_theme = theme_name
            logger.info(f"Applied theme: {theme_name}")
            
        except Exception as e:
            logger.error(f"Failed to apply theme {theme_name}: {e}")
    
    def _apply_system_theme(self):
        """Apply system default theme"""
        try:
            # Try to use system theme
            available_themes = self.style.theme_names()
            
            # Prefer modern themes if available
            preferred_themes = ['vista', 'xpnative', 'winnative', 'clam', 'alt', 'default']
            
            for theme in preferred_themes:
                if theme in available_themes:
                    self.style.theme_use(theme)
                    break
            
            # Apply some custom styling for better appearance
            self._apply_custom_styling()
            
        except Exception as e:
            logger.error(f"Error applying system theme: {e}")
    
    def _apply_custom_theme(self, theme_name: str):
        """Apply a custom theme"""
        if theme_name not in self.theme_config:
            return
        
        theme_data = self.theme_config[theme_name]
        
        try:
            # Start with a base theme
            available_themes = self.style.theme_names()
            base_theme = 'clam' if 'clam' in available_themes else 'default'
            self.style.theme_use(base_theme)
            
            # Configure custom colors
            self.style.configure('TLabel', 
                               background=theme_data.get('bg'),
                               foreground=theme_data.get('fg'))
            
            self.style.configure('TFrame', 
                               background=theme_data.get('bg'))
            
            self.style.configure('TLabelFrame', 
                               background=theme_data.get('bg'),
                               foreground=theme_data.get('fg'))
            
            self.style.configure('TEntry',
                               fieldbackground=theme_data.get('entry_bg'),
                               foreground=theme_data.get('entry_fg'),
                               bordercolor=theme_data.get('select_bg'))
            
            self.style.configure('TCombobox',
                               fieldbackground=theme_data.get('entry_bg'),
                               foreground=theme_data.get('entry_fg'))
            
            self.style.configure('TButton',
                               background=theme_data.get('button_bg'),
                               foreground=theme_data.get('button_fg'))
            
            # Apply additional custom styling
            self._apply_custom_styling()
            
        except Exception as e:
            logger.error(f"Error applying custom theme {theme_name}: {e}")
    
    def _apply_custom_styling(self):
        """Apply custom styling improvements"""
        try:
            # Improve button appearance
            self.style.configure('TButton',
                               padding=(10, 5),
                               relief='raised')
            
            # Improve frame appearance
            self.style.configure('TLabelFrame',
                               padding=(10, 10),
                               relief='groove',
                               borderwidth=1)
            
            # Improve entry appearance
            self.style.configure('TEntry',
                               padding=(5, 3),
                               relief='sunken',
                               borderwidth=1)
            
            self.style.configure('TCombobox',
                               padding=(5, 3))
            
        except Exception as e:
            logger.debug(f"Error applying custom styling: {e}")
    
    def save_preferences(self):
        """Save theme preferences"""
        try:
            config_dir = Path(__file__).parent.parent.parent.parent / "config"
            config_dir.mkdir(exist_ok=True)
            
            prefs_file = config_dir / "gui_preferences.json"
            preferences = {
                'theme': self.current_theme,
                'last_updated': str(Path(__file__).stat().st_mtime)
            }
            
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save theme preferences: {e}")
    
    def load_preferences(self):
        """Load saved theme preferences"""
        try:
            prefs_file = Path(__file__).parent.parent.parent.parent / "config" / "gui_preferences.json"
            
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    
                theme = preferences.get('theme', 'system')
                if theme in self.available_themes:
                    self.apply_theme(theme)
                    
        except Exception as e:
            logger.warning(f"Failed to load theme preferences: {e}")
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get color scheme for a theme"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name == 'system':
            # Return approximate system colors
            return {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff'
            }
        
        return self.theme_config.get(theme_name, {})
    
    def create_themed_widget(self, widget_class, parent, **kwargs):
        """Create a widget with current theme applied"""
        # This could be extended to apply theme-specific widget creation
        return widget_class(parent, **kwargs)