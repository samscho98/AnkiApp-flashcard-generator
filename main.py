#!/usr/bin/env python3
"""
Main launcher for Language Learning Flashcard Generator
Updated to use the new refactored GUI structure
"""

import sys
import logging
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flashcard_generator.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met"""
    try:
        import tkinter
    except ImportError:
        print("❌ Error: tkinter is not available")
        print("   On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   On CentOS/RHEL: sudo yum install tkinter")
        print("   On macOS/Windows: tkinter should be included with Python")
        return False
    
    return True


def setup_directories():
    """Ensure required directories exist"""
    directories = [
        Path("data"),
        Path("data/vocabulary"),
        Path("data/grammar"),
        Path("output"),
        Path("logs")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    logger.info("Directory structure verified")


def main():
    """Main entry point"""
    try:
        # Check requirements
        if not check_requirements():
            return 1
        
        # Setup directories
        setup_directories()
        
        # Import and run GUI application (now from the new location)
        from src.gui.app import LanguageLearningApp  # CHANGED: Import from gui.app instead of gui.main_window
        
        logger.info("Starting Language Learning Flashcard Generator")
        
        app = LanguageLearningApp()
        app.run()
        
        logger.info("Application closed normally")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        print(f"❌ Import error: {e}")
        print("Make sure all required files are present in the src/ directory")
        print("\nTrying fallback to original structure...")
        
        # Fallback to original structure if new one isn't ready
        try:
            from src.gui.main_window import LanguageLearningApp
            logger.info("Using fallback import")
            app = LanguageLearningApp()
            app.run()
            return 0
        except ImportError as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            print("Please ensure the GUI files are properly set up")
            return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        print("Check flashcard_generator.log for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())