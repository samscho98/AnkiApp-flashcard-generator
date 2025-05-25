"""
Main Application Entry Point for Language Learning Flashcard Generator
Clean application lifecycle management and setup
"""

import tkinter as tk
import logging
from pathlib import Path
import sys

from .main_window import MainWindow
from .utils.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class LanguageLearningApp:
    """Main application class - handles app lifecycle and global setup"""
    
    def __init__(self):
        """Initialize the application"""
        self.root = tk.Tk()
        self.theme_manager = ThemeManager()
        self.main_window = None
        
        self._setup_root_window()
        self._setup_theme()
        self._create_main_window()
    
    def _setup_root_window(self):
        """Configure the root tkinter window"""
        self.root.title("Language Learning Flashcard Generator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set application icon if available
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Icon not available, continue without it
        
        # Center window on screen
        self._center_window()
        
        # Handle app closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Handle window state changes
        self.root.bind('<Configure>', self._on_window_configure)
    
    def _center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_theme(self):
        """Apply initial theme settings"""
        try:
            # Configure ttk style
            style = self.theme_manager.get_style()
            
            # Apply any custom styling
            self.theme_manager.apply_theme('system')  # Default to system theme
            
        except Exception as e:
            logger.warning(f"Failed to setup theme: {e}")
    
    def _create_main_window(self):
        """Create the main application window"""
        try:
            self.main_window = MainWindow(self.root)
            logger.info("Main window created successfully")
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            self._show_startup_error(e)
            sys.exit(1)
    
    def _show_startup_error(self, error):
        """Show startup error dialog"""
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "Startup Error",
            f"Failed to start application:\n\n{error}\n\nCheck the log file for details."
        )
    
    def _on_window_configure(self, event):
        """Handle window resize/move events"""
        if event.widget == self.root:
            # Save window position/size if needed
            if self.main_window:
                self.main_window.on_window_configure(event)
    
    def _on_closing(self):
        """Handle application closing"""
        try:
            logger.info("Application closing...")
            
            # Ask main window to save state
            if self.main_window:
                if not self.main_window.can_close():
                    return  # User cancelled closing
                
                self.main_window.save_state()
            
            # Save theme preferences
            self.theme_manager.save_preferences()
            
            # Close the application
            self.root.destroy()
            logger.info("Application closed successfully")
            
        except Exception as e:
            logger.error(f"Error during app closing: {e}")
            # Force close even if there's an error
            try:
                self.root.destroy()
            except:
                pass
    
    def run(self):
        """Start the application main loop"""
        try:
            logger.info("Starting application...")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application runtime error: {e}")
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Runtime Error",
                f"An unexpected error occurred:\n\n{e}\n\nThe application will close."
            )
        finally:
            logger.info("Application finished")
    
    def get_root(self):
        """Get the root tkinter window"""
        return self.root
    
    def get_main_window(self):
        """Get the main window instance"""
        return self.main_window
    
    def apply_theme(self, theme_name):
        """Apply a new theme to the application"""
        try:
            self.theme_manager.apply_theme(theme_name)
            if self.main_window:
                self.main_window.refresh_theme()
            logger.info(f"Applied theme: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to apply theme {theme_name}: {e}")


def main():
    """Main entry point for the GUI application"""
    app = LanguageLearningApp()
    app.run()


if __name__ == "__main__":
    main()