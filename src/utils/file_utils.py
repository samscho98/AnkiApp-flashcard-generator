"""
File Utilities Module
Handles file operations, directory management, and backup functionality
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator, Tuple
from datetime import datetime
import logging
import hashlib
import zipfile

logger = logging.getLogger(__name__)


class FileManager:
    """Generic file operations manager"""
    
    def __init__(self, base_directory: str = "."):
        """
        Initialize FileManager
        
        Args:
            base_directory: Base directory for operations
        """
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(exist_ok=True)
    
    def ensure_directory(self, directory: str) -> Path:
        """
        Ensure directory exists, create if not
        
        Args:
            directory: Directory path (relative to base_dir or absolute)
            
        Returns:
            Path object of the directory
        """
        if Path(directory).is_absolute():
            dir_path = Path(directory)
        else:
            dir_path = self.base_dir / directory
        
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def list_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        List files matching pattern in directory
        
        Args:
            directory: Directory to search
            pattern: File pattern (e.g., "*.json", "week*.json")
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        dir_path = self.base_dir / directory if not Path(directory).is_absolute() else Path(directory)
        
        if not dir_path.exists():
            return []
        
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
    
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        file_path = self.base_dir / filepath if not Path(filepath).is_absolute() else Path(filepath)
        return file_path.exists()
    
    def get_file_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Get file information
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file info or None if file doesn't exist
        """
        file_path = self.base_dir / filepath if not Path(filepath).is_absolute() else Path(filepath)
        
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        return {
            'filepath': str(file_path),
            'filename': file_path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': file_path.suffix,
            'is_file': file_path.is_file(),
            'is_directory': file_path.is_dir()
        }
    
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Copy file from source to destination
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful
        """
        try:
            src_path = self.base_dir / source if not Path(source).is_absolute() else Path(source)
            dst_path = self.base_dir / destination if not Path(destination).is_absolute() else Path(destination)
            
            if dst_path.exists() and not overwrite:
                logger.warning(f"Destination file exists and overwrite=False: {dst_path}")
                return False
            
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            logger.info(f"Copied file: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying file {source} to {destination}: {e}")
            return False
    
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Move file from source to destination
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful
        """
        try:
            src_path = self.base_dir / source if not Path(source).is_absolute() else Path(source)
            dst_path = self.base_dir / destination if not Path(destination).is_absolute() else Path(destination)
            
            if dst_path.exists() and not overwrite:
                logger.warning(f"Destination file exists and overwrite=False: {dst_path}")
                return False
            
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            logger.info(f"Moved file: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving file {source} to {destination}: {e}")
            return False
    
    def delete_file(self, filepath: str, confirm: bool = True) -> bool:
        """
        Delete file
        
        Args:
            filepath: Path to file to delete
            confirm: Whether file must exist (False = no error if missing)
            
        Returns:
            True if successful
        """
        try:
            file_path = self.base_dir / filepath if not Path(filepath).is_absolute() else Path(filepath)
            
            if not file_path.exists():
                if confirm:
                    logger.error(f"File not found for deletion: {file_path}")
                    return False
                else:
                    return True  # Already doesn't exist
            
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
            return False
    
    def get_file_hash(self, filepath: str, algorithm: str = "md5") -> Optional[str]:
        """
        Get file hash
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256)
            
        Returns:
            Hex digest of hash or None if error
        """
        try:
            file_path = self.base_dir / filepath if not Path(filepath).is_absolute() else Path(filepath)
            
            if not file_path.exists():
                return None
            
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating hash for {filepath}: {e}")
            return None


class JSONFileManager(FileManager):
    """Specialized manager for JSON files"""
    
    def load_json(self, filepath: str, default: Any = None) -> Any:
        """
        Load JSON file
        
        Args:
            filepath: Path to JSON file
            default: Default value if file doesn't exist or is invalid
            
        Returns:
            Loaded data or default value
        """
        file_path = self.base_dir / filepath if not Path(filepath).is_absolute() else Path(filepath)
        
        if not file_path.exists():
            logger.warning(f"JSON file not found: {file_path}")
            return default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            return default
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return default
    
    def save_json(self, data: Any, filepath: str, indent: int = 2, backup: bool = True) -> bool:
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            filepath: Path to JSON file
            indent: JSON indentation
            backup: Whether to create backup if file exists
            
        Returns:
            True if successful
        """
        file_path = self.base_dir / filepath if not Path(filepath).is_absolute() else Path(filepath)
        
        try:
            # Create backup if requested and file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                shutil.copy2(file_path, backup_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.info(f"Saved JSON file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSON file {file_path}: {e}")
            return False
    
    def merge_json_files(self, filepaths: List[str], output_path: str, merge_strategy: str = "combine") -> bool:
        """
        Merge multiple JSON files
        
        Args:
            filepaths: List of JSON file paths
            output_path: Output file path
            merge_strategy: "combine" (list), "merge" (dict), "deep_merge" (recursive dict merge)
            
        Returns:
            True if successful
        """
        try:
            merged_data = None
            
            for filepath in filepaths:
                data = self.load_json(filepath)
                if data is None:
                    logger.warning(f"Skipping invalid JSON file: {filepath}")
                    continue
                
                if merged_data is None:
                    merged_data = data
                elif merge_strategy == "combine":
                    if isinstance(merged_data, list) and isinstance(data, list):
                        merged_data.extend(data)
                    else:
                        merged_data = [merged_data, data] if not isinstance(merged_data, list) else merged_data + [data]
                elif merge_strategy == "merge":
                    if isinstance(merged_data, dict) and isinstance(data, dict):
                        merged_data.update(data)
                    else:
                        logger.warning(f"Cannot merge non-dict data with strategy '{merge_strategy}'")
                elif merge_strategy == "deep_merge":
                    if isinstance(merged_data, dict) and isinstance(data, dict):
                        merged_data = self._deep_merge_dicts(merged_data, data)
                    else:
                        logger.warning(f"Cannot deep merge non-dict data")
            
            if merged_data is not None:
                return self.save_json(merged_data, output_path)
            else:
                logger.error("No valid data to merge")
                return False
                
        except Exception as e:
            logger.error(f"Error merging JSON files: {e}")
            return False
    
    def _deep_merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result


class BackupManager:
    """Manages file backups and versioning"""
    
    def __init__(self, backup_directory: str = "backups"):
        """
        Initialize BackupManager
        
        Args:
            backup_directory: Directory to store backups
        """
        self.backup_dir = Path(backup_directory)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, source: str, backup_name: Optional[str] = None) -> Optional[str]:
        """
        Create backup of file or directory
        
        Args:
            source: Source file or directory path
            backup_name: Custom backup name (None for auto-generated)
            
        Returns:
            Path to created backup or None if failed
        """
        try:
            source_path = Path(source)
            
            if not source_path.exists():
                logger.error(f"Source not found for backup: {source}")
                return None
            
            # Generate backup name
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{source_path.name}_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            
            if source_path.is_file():
                shutil.copy2(source_path, backup_path)
            else:
                shutil.copytree(source_path, backup_path)
            
            logger.info(f"Created backup: {source} -> {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup of {source}: {e}")
            return None
    
    def create_zip_backup(self, sources: List[str], backup_name: str) -> Optional[str]:
        """
        Create ZIP backup of multiple files/directories
        
        Args:
            sources: List of source paths
            backup_name: Name for backup ZIP file
            
        Returns:
            Path to created ZIP file or None if failed
        """
        try:
            if not backup_name.endswith('.zip'):
                backup_name += '.zip'
            
            zip_path = self.backup_dir / backup_name
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source in sources:
                    source_path = Path(source)
                    
                    if not source_path.exists():
                        logger.warning(f"Source not found, skipping: {source}")
                        continue
                    
                    if source_path.is_file():
                        zipf.write(source_path, source_path.name)
                    else:
                        # Add directory contents
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                arcname = str(file_path.relative_to(source_path.parent))
                                zipf.write(file_path, arcname)
            
            logger.info(f"Created ZIP backup: {zip_path}")
            return str(zip_path)
            
        except Exception as e:
            logger.error(f"Error creating ZIP backup: {e}")
            return None
    
    def list_backups(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """
        List available backups
        
        Args:
            pattern: Pattern to match backup names
            
        Returns:
            List of backup info dictionaries
        """
        backups = []
        
        for backup_path in self.backup_dir.glob(pattern):
            if backup_path.is_file() or backup_path.is_dir():
                stat = backup_path.stat()
                backups.append({
                    'name': backup_path.name,
                    'path': str(backup_path),
                    'size': stat.st_size if backup_path.is_file() else self._get_directory_size(backup_path),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': 'file' if backup_path.is_file() else 'directory'
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str, destination: str, overwrite: bool = False) -> bool:
        """
        Restore backup to destination
        
        Args:
            backup_name: Name of backup to restore
            destination: Destination path
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if successful
        """
        try:
            backup_path = self.backup_dir / backup_name
            dest_path = Path(destination)
            
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_name}")
                return False
            
            if dest_path.exists() and not overwrite:
                logger.error(f"Destination exists and overwrite=False: {destination}")
                return False
            
            if backup_path.suffix == '.zip':
                # Extract ZIP backup
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(dest_path.parent)
            elif backup_path.is_file():
                # Copy file
                shutil.copy2(backup_path, dest_path)
            else:
                # Copy directory
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(backup_path, dest_path)
            
            logger.info(f"Restored backup: {backup_name} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup {backup_name}: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10, keep_days: int = 30) -> int:
        """
        Clean up old backups
        
        Args:
            keep_count: Number of most recent backups to keep
            keep_days: Days of backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()
        deleted_count = 0
        
        # Keep recent backups by count
        recent_backups = set(backup['name'] for backup in backups[:keep_count])
        
        # Keep backups within time window
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup in backups:
            if backup['name'] in recent_backups:
                continue
            
            backup_date = datetime.fromisoformat(backup['created']).timestamp()
            if backup_date >= cutoff_date:
                continue
            
            # Delete old backup
            try:
                backup_path = Path(backup['path'])
                if backup_path.is_file():
                    backup_path.unlink()
                else:
                    shutil.rmtree(backup_path)
                
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup['name']}")
                
            except Exception as e:
                logger.error(f"Error deleting backup {backup['name']}: {e}")
        
        return deleted_count
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory"""
        total_size = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size


class ConfigManager:
    """Manages configuration files with validation and defaults"""
    
    def __init__(self, config_file: str = "config.json", schema: Optional[Dict] = None):
        """
        Initialize ConfigManager
        
        Args:
            config_file: Path to configuration file
            schema: Optional configuration schema for validation
        """
        self.config_file = Path(config_file)
        self.schema = schema
        self.json_manager = JSONFileManager()
        self._config_data = None
    
    def load_config(self, create_if_missing: bool = True) -> Dict[str, Any]:
        """
        Load configuration file
        
        Args:
            create_if_missing: Create with defaults if file doesn't exist
            
        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists() and create_if_missing:
            logger.info(f"Creating default configuration: {self.config_file}")
            default_config = self._get_default_config()
            self.json_manager.save_json(default_config, str(self.config_file))
            self._config_data = default_config
        else:
            self._config_data = self.json_manager.load_json(str(self.config_file), {})
        
        return self._config_data or {}
    
    def save_config(self, config_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save configuration file
        
        Args:
            config_data: Configuration to save (uses loaded config if None)
            
        Returns:
            True if successful
        """
        data_to_save = config_data or self._config_data or {}
        
        # Validate against schema if provided
        if self.schema and not self._validate_config(data_to_save):
            logger.error("Configuration validation failed")
            return False
        
        return self.json_manager.save_json(data_to_save, str(self.config_file))
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration setting using dot notation
        
        Args:
            key_path: Setting path (e.g., "database.host")
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        if self._config_data is None:
            self.load_config()
        
        keys = key_path.split('.')
        current = self._config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key_path: str, value: Any) -> bool:
        """
        Set configuration setting using dot notation
        
        Args:
            key_path: Setting path (e.g., "database.host")
            value: Value to set
            
        Returns:
            True if successful
        """
        if self._config_data is None:
            self.load_config()
        
        keys = key_path.split('.')
        current = self._config_data
        
        try:
            # Navigate to parent
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set value
            current[keys[-1]] = value
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error setting configuration {key_path}: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "created_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "settings": {}
        }
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration against schema"""
        if not self.schema:
            return True
        
        # Basic schema validation (can be extended)
        try:
            for required_key in self.schema.get('required', []):
                if required_key not in config:
                    logger.error(f"Missing required configuration key: {required_key}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False


class DirectoryScanner:
    """Scans directories for learning content files"""
    
    def __init__(self, base_directory: str = "data"):
        """
        Initialize DirectoryScanner
        
        Args:
            base_directory: Base directory to scan
        """
        self.base_dir = Path(base_directory)
    
    def scan_for_content(self, content_patterns: Dict[str, List[str]] = None) -> Dict[str, List[str]]:
        """
        Scan for learning content files
        
        Args:
            content_patterns: Dictionary of content_type -> [patterns]
            
        Returns:
            Dictionary of content_type -> [file_paths]
        """
        if content_patterns is None:
            content_patterns = {
                'vocabulary': ['*.json', 'vocab_*.json', 'words_*.json'],
                'grammar': ['grammar*.json', 'rules_*.json'],
                'exercises': ['exercise*.json', 'practice_*.json'],
                'lessons': ['lesson*.json', 'unit_*.json']
            }
        
        found_content = {}
        
        for content_type, patterns in content_patterns.items():
            files = []
            content_dir = self.base_dir / content_type
            
            if content_dir.exists():
                for pattern in patterns:
                    files.extend(content_dir.glob(pattern))
            
            # Also search in base directory
            for pattern in patterns:
                files.extend(self.base_dir.glob(pattern))
            
            # Remove duplicates and convert to strings
            unique_files = list(set(str(f) for f in files))
            found_content[content_type] = sorted(unique_files)
        
        return found_content
    
    def get_directory_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get directory structure
        
        Args:
            max_depth: Maximum depth to scan
            
        Returns:
            Nested dictionary representing directory structure
        """
        def scan_directory(directory: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {}
            
            structure = {
                'type': 'directory',
                'name': directory.name,
                'path': str(directory),
                'children': {}
            }
            
            try:
                for item in directory.iterdir():
                    if item.is_dir():
                        structure['children'][item.name] = scan_directory(item, current_depth + 1)
                    else:
                        structure['children'][item.name] = {
                            'type': 'file',
                            'name': item.name,
                            'path': str(item),
                            'size': item.stat().st_size,
                            'extension': item.suffix
                        }
            except PermissionError:
                structure['error'] = 'Permission denied'
            
            return structure
        
        return scan_directory(self.base_dir)
    
    def find_files_by_content(self, search_terms: List[str], file_extensions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Find files containing specific terms
        
        Args:
            search_terms: Terms to search for
            file_extensions: File extensions to search (None for all text files)
            
        Returns:
            List of matching files with match information
        """
        if file_extensions is None:
            file_extensions = ['.json', '.txt', '.md', '.csv']
        
        matches = []
        
        for file_path in self.base_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    found_terms = []
                    for term in search_terms:
                        if term.lower() in content:
                            found_terms.append(term)
                    
                    if found_terms:
                        matches.append({
                            'file': str(file_path),
                            'found_terms': found_terms,
                            'match_count': len(found_terms)
                        })
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        # Sort by match count (most matches first)
        matches.sort(key=lambda x: x['match_count'], reverse=True)
        return matches


# Example usage and integration
if __name__ == "__main__":
    # File management example
    file_manager = FileManager("data")
    json_manager = JSONFileManager("data")
    
    # List all JSON files
    json_files = file_manager.list_files("vocabulary", "*.json")
    print(f"Found JSON files: {[f.name for f in json_files]}")
    
    # Load and merge multiple JSON files
    if len(json_files) >= 2:
        merged_success = json_manager.merge_json_files(
            [str(f) for f in json_files[:2]],
            "merged_vocabulary.json",
            merge_strategy="combine"
        )
        print(f"Merge successful: {merged_success}")
    
    # Backup management example
    backup_manager = BackupManager()
    
    # Create backup of vocabulary directory
    backup_path = backup_manager.create_zip_backup(
        ["data/vocabulary"],
        "vocabulary_backup"
    )
    print(f"Backup created: {backup_path}")
    
    # List all backups
    backups = backup_manager.list_backups()
    print(f"Available backups: {[b['name'] for b in backups]}")
    
    # Configuration management example
    config_manager = ConfigManager("app_config.json")
    config = config_manager.load_config()
    
    # Set some configuration values
    config_manager.set_setting("app.name", "AnkiApp Flashcard Generator")
    config_manager.set_setting("data.vocabulary_path", "data/vocabulary")
    config_manager.set_setting("export.default_format", "ankiapp")
    
    print(f"App name: {config_manager.get_setting('app.name')}")
    
    # Directory scanning example
    scanner = DirectoryScanner("data")
    content_files = scanner.scan_for_content()
    
    for content_type, files in content_files.items():
        if files:
            print(f"{content_type}: {len(files)} files")
    
    # Search for files containing specific terms
    search_results = scanner.find_files_by_content(["german", "vocabulary", "week"])
    print(f"Files containing search terms: {len(search_results)}")