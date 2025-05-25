"""
Generic Settings Manager for Language Learning Flashcard Generator
Handles application configuration and user preferences for any language
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


@dataclass
class StudySettings:
    """Study-related settings for language learning"""
    daily_target_items: int = 20
    include_native_connections: bool = True
    study_reminder_enabled: bool = True
    reminder_time: str = "09:00"  # HH:MM format
    auto_advance_progress: bool = True
    show_pronunciation_hints: bool = True
    difficulty_adjustment: bool = False
    spaced_repetition: bool = False


@dataclass
class ExportSettings:
    """CSV export settings for flashcard generation"""
    output_directory: str = "output"
    filename_template: str = "{category}_{subcategory}_{date}"
    include_date_in_filename: bool = True
    csv_delimiter: str = ","
    include_headers: bool = True
    export_format: str = "ankiapp"  # "ankiapp", "anki", "quizlet", "generic"
    include_tags: bool = True
    html_formatting: bool = True


@dataclass
class AppearanceSettings:
    """GUI appearance settings"""
    theme: str = "system"  # "light", "dark", "system"
    font_family: str = "Segoe UI"
    font_size: int = 10
    window_width: int = 1000
    window_height: int = 700
    remember_window_position: bool = True
    show_progress_indicators: bool = True
    preview_panel_size: float = 0.4  # Fraction of window width


@dataclass
class AdvancedSettings:
    """Advanced application settings"""
    data_directory: str = "data"
    backup_enabled: bool = True
    backup_frequency: int = 7  # days
    log_level: str = "INFO"
    auto_update_check: bool = True
    performance_mode: bool = False
    cache_enabled: bool = True
    max_recent_files: int = 10


class SettingsManager:
    """Manages application settings and configuration for language learning"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize Settings Manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.settings = self._load_settings()
        
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default application settings
        
        Returns:
            Dictionary with default settings
        """
        return {
            "app_info": {
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "user_name": "",
                "app_name": "Language Learning Flashcard Generator"
            },
            "study": asdict(StudySettings()),
            "export": asdict(ExportSettings()),
            "appearance": asdict(AppearanceSettings()),
            "advanced": asdict(AdvancedSettings()),
            "paths": {
                "data_directory": "data",
                "output_directory": "output", 
                "backup_directory": "backups",
                "log_directory": "logs",
                "templates_directory": "templates"
            },
            "language_learning": {
                "target_language": "",
                "native_language": "english",
                "learning_method": "flashcards",
                "content_types": ["vocabulary", "grammar", "phrases"],
                "show_connections": True
            },
            "recent_files": [],
            "bookmarks": []
        }
    
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from configuration file
        
        Returns:
            Dictionary with settings
        """
        if not self.config_file.exists():
            logger.info("Creating new configuration file")
            default_settings = self._get_default_settings()
            self._save_settings(default_settings)
            return default_settings
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Update last_updated timestamp
            settings.setdefault("app_info", {})["last_updated"] = datetime.now().isoformat()
            
            # Merge with defaults to ensure all keys exist
            default_settings = self._get_default_settings()
            merged_settings = self._merge_settings(default_settings, settings)
            
            return merged_settings
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading settings: {e}")
            logger.info("Using default settings")
            return self._get_default_settings()
    
    def _merge_settings(self, defaults: Dict, loaded: Dict) -> Dict:
        """
        Merge loaded settings with defaults to ensure all keys exist
        
        Args:
            defaults: Default settings dictionary
            loaded: Loaded settings dictionary
            
        Returns:
            Merged settings dictionary
        """
        merged = defaults.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def _save_settings(self, settings: Optional[Dict] = None) -> bool:
        """
        Save settings to configuration file
        
        Args:
            settings: Settings to save (uses self.settings if None)
            
        Returns:
            True if successful
        """
        if settings is None:
            settings = self.settings
        
        # Update timestamp
        settings.setdefault("app_info", {})["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def get_study_settings(self) -> StudySettings:
        """Get study settings as dataclass"""
        study_dict = self.settings.get("study", {})
        return StudySettings(**study_dict)
    
    def set_study_settings(self, study_settings: StudySettings) -> bool:
        """Set study settings"""
        self.settings["study"] = asdict(study_settings)
        return self._save_settings()
    
    def get_export_settings(self) -> ExportSettings:
        """Get export settings as dataclass"""
        export_dict = self.settings.get("export", {})
        return ExportSettings(**export_dict)
    
    def set_export_settings(self, export_settings: ExportSettings) -> bool:
        """Set export settings"""
        self.settings["export"] = asdict(export_settings)
        return self._save_settings()
    
    def get_appearance_settings(self) -> AppearanceSettings:
        """Get appearance settings as dataclass"""
        appearance_dict = self.settings.get("appearance", {})
        return AppearanceSettings(**appearance_dict)
    
    def set_appearance_settings(self, appearance_settings: AppearanceSettings) -> bool:
        """Set appearance settings"""
        self.settings["appearance"] = asdict(appearance_settings)
        return self._save_settings()
    
    def get_advanced_settings(self) -> AdvancedSettings:
        """Get advanced settings as dataclass"""
        advanced_dict = self.settings.get("advanced", {})
        return AdvancedSettings(**advanced_dict)
    
    def set_advanced_settings(self, advanced_settings: AdvancedSettings) -> bool:
        """Set advanced settings"""
        self.settings["advanced"] = asdict(advanced_settings)
        return self._save_settings()
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get a specific setting using dot notation
        
        Args:
            key_path: Path to setting (e.g., "study.daily_target_items")
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        keys = key_path.split('.')
        current = self.settings
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key_path: str, value: Any) -> bool:
        """
        Set a specific setting using dot notation
        
        Args:
            key_path: Path to setting (e.g., "study.daily_target_items")
            value: Value to set
            
        Returns:
            True if successful
        """
        keys = key_path.split('.')
        current = self.settings
        
        try:
            # Navigate to the parent dictionary
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the final value
            current[keys[-1]] = value
            return self._save_settings()
            
        except Exception as e:
            logger.error(f"Error setting {key_path}: {e}")
            return False
    
    def get_language_settings(self) -> Dict[str, str]:
        """Get language learning settings"""
        return {
            "target_language": self.get_setting("language_learning.target_language", ""),
            "native_language": self.get_setting("language_learning.native_language", "english"),
            "learning_method": self.get_setting("language_learning.learning_method", "flashcards")
        }
    
    def set_language_settings(self, target_lang: str, native_lang: str = "english", method: str = "flashcards") -> bool:
        """Set language learning settings"""
        success = True
        success &= self.set_setting("language_learning.target_language", target_lang)
        success &= self.set_setting("language_learning.native_language", native_lang)
        success &= self.set_setting("language_learning.learning_method", method)
        return success
    
    def get_paths(self) -> Dict[str, str]:
        """Get all configured paths"""
        return self.settings.get("paths", {})
    
    def get_data_directory(self) -> Path:
        """Get data directory path"""
        data_dir = self.get_setting("paths.data_directory", "data")
        return Path(data_dir)
    
    def get_output_directory(self) -> Path:
        """Get output directory path"""
        output_dir = self.get_setting("paths.output_directory", "output")
        return Path(output_dir)
    
    def get_backup_directory(self) -> Path:
        """Get backup directory path"""
        backup_dir = self.get_setting("paths.backup_directory", "backups")
        return Path(backup_dir)
    
    def add_recent_file(self, filepath: str) -> bool:
        """Add file to recent files list"""
        recent_files = self.get_setting("recent_files", [])
        
        # Remove if already exists
        if filepath in recent_files:
            recent_files.remove(filepath)
        
        # Add to beginning
        recent_files.insert(0, filepath)
        
        # Limit to max recent files
        max_recent = self.get_setting("advanced.max_recent_files", 10)
        recent_files = recent_files[:max_recent]
        
        return self.set_setting("recent_files", recent_files)
    
    def get_recent_files(self) -> List[str]:
        """Get list of recent files"""
        return self.get_setting("recent_files", [])
    
    def add_bookmark(self, name: str, filepath: str) -> bool:
        """Add bookmark for quick access"""
        bookmarks = self.get_setting("bookmarks", [])
        
        # Check if bookmark already exists
        for bookmark in bookmarks:
            if bookmark.get("filepath") == filepath:
                bookmark["name"] = name  # Update name
                return self._save_settings()
        
        # Add new bookmark
        bookmarks.append({
            "name": name,
            "filepath": filepath,
            "added_date": datetime.now().isoformat()
        })
        
        return self.set_setting("bookmarks", bookmarks)
    
    def get_bookmarks(self) -> List[Dict[str, str]]:
        """Get list of bookmarks"""
        return self.get_setting("bookmarks", [])
    
    def remove_bookmark(self, filepath: str) -> bool:
        """Remove bookmark by filepath"""
        bookmarks = self.get_setting("bookmarks", [])
        bookmarks = [b for b in bookmarks if b.get("filepath") != filepath]
        return self.set_setting("bookmarks", bookmarks)
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """
        Validate all settings
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": [],
            "warnings": [],
            "errors": []
        }
        
        # Validate study settings
        study = self.get_study_settings()
        if not (1 <= study.daily_target_items <= 100):
            results["warnings"].append("Daily target should be between 1-100 items")
        
        try:
            # Validate reminder time format
            time.fromisoformat(study.reminder_time)
            results["valid"].append("Reminder time format is valid")
        except ValueError:
            results["errors"].append("Invalid reminder time format (use HH:MM)")
        
        # Validate paths
        paths = self.get_paths()
        for path_name, path_value in paths.items():
            path_obj = Path(path_value)
            if path_name.endswith("_directory"):
                if not path_obj.exists():
                    results["warnings"].append(f"Directory does not exist: {path_value}")
                elif not path_obj.is_dir():
                    results["errors"].append(f"Path is not a directory: {path_value}")
                else:
                    results["valid"].append(f"Directory exists: {path_value}")
        
        # Validate export format
        export_format = self.get_setting("export.export_format", "ankiapp")
        valid_formats = ["ankiapp", "anki", "quizlet", "generic"]
        if export_format not in valid_formats:
            results["warnings"].append(f"Unknown export format: {export_format}")
        else:
            results["valid"].append(f"Export format is valid: {export_format}")
        
        return results
    
    def create_directories(self) -> bool:
        """
        Create all configured directories if they don't exist
        
        Returns:
            True if all directories were created successfully
        """
        success = True
        paths = self.get_paths()
        
        for path_name, path_value in paths.items():
            if path_name.endswith("_directory"):
                try:
                    Path(path_value).mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {path_value}")
                except Exception as e:
                    logger.error(f"Failed to create directory {path_value}: {e}")
                    success = False
        
        return success
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to defaults
        
        Returns:
            True if successful
        """
        logger.warning("Resetting all settings to defaults")
        self.settings = self._get_default_settings()
        return self._save_settings()
    
    def export_settings(self, export_path: str) -> bool:
        """
        Export settings to a file
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if successful
        """
        try:
            export_data = {
                "exported_date": datetime.now().isoformat(),
                "app_version": self.get_setting("app_info.version", "1.0.0"),
                "settings": self.settings
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """
        Import settings from a file
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if successful
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "settings" in import_data:
                # Merge with current settings to preserve any new keys
                merged_settings = self._merge_settings(self.settings, import_data["settings"])
                self.settings = merged_settings
                success = self._save_settings()
                
                if success:
                    logger.info(f"Settings imported from: {import_path}")
                return success
            else:
                logger.error("Invalid settings file format")
                return False
                
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Create settings manager
    settings = SettingsManager()
    
    # Get study settings
    study_settings = settings.get_study_settings()
    print(f"Daily target: {study_settings.daily_target_items} items")
    print(f"Include connections: {study_settings.include_native_connections}")
    
    # Get language settings
    lang_settings = settings.get_language_settings()
    print(f"Language settings: {lang_settings}")
    
    # Validate settings
    validation = settings.validate_settings()
    print(f"Validation results: {validation}")
    
    # Create directories
    success = settings.create_directories()
    print(f"Directories created: {success}")
    
    # Add recent file
    settings.add_recent_file("data/vocabulary/sample.json")
    print(f"Recent files: {settings.get_recent_files()}")
    
    # Add bookmark
    settings.add_bookmark("Sample Vocabulary", "data/vocabulary/sample.json")
    print(f"Bookmarks: {settings.get_bookmarks()}")