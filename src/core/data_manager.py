"""
Generic Data Manager System
Modular system for loading and managing language learning data from various sources
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContentEntry:
    """Generic content entry for any learning material"""
    
    def __init__(self, data: Dict[str, Any], content_type: str = "vocabulary"):
        self.raw_data = data
        self.content_type = content_type
        self.id = data.get('id', '')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.updated_at = data.get('updated_at', datetime.now().isoformat())
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a field value"""
        return self.raw_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a field value"""
        self.raw_data[key] = value
        self.updated_at = datetime.now().isoformat()
    
    def has_field(self, key: str) -> bool:
        """Check if entry has a field"""
        return key in self.raw_data
    
    def get_fields(self) -> List[str]:
        """Get all available fields"""
        return list(self.raw_data.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.raw_data.copy()


@dataclass
class ContentSection:
    """A section/unit of learning content"""
    title: str
    topic: str
    entries: List[ContentEntry]
    metadata: Dict[str, Any]
    section_id: str = ""
    
    def __post_init__(self):
        if not self.section_id:
            self.section_id = f"section_{len(self.entries)}"
    
    def add_entry(self, entry: ContentEntry) -> None:
        """Add an entry to this section"""
        self.entries.append(entry)
    
    def get_entries_by_field(self, field: str, value: Any) -> List[ContentEntry]:
        """Get entries matching a field value"""
        return [entry for entry in self.entries if entry.get(field) == value]
    
    def count_entries(self) -> int:
        """Get number of entries in this section"""
        return len(self.entries)


@dataclass
class ContentUnit:
    """A unit/week/chapter of learning content"""
    title: str
    unit_number: int
    sections: Dict[str, ContentSection]
    metadata: Dict[str, Any]
    unit_type: str = "unit"  # unit, week, chapter, etc.
    
    def add_section(self, section_id: str, section: ContentSection) -> None:
        """Add a section to this unit"""
        self.sections[section_id] = section
    
    def get_section(self, section_id: str) -> Optional[ContentSection]:
        """Get a specific section"""
        return self.sections.get(section_id)
    
    def get_all_entries(self) -> List[ContentEntry]:
        """Get all entries from all sections"""
        all_entries = []
        for section in self.sections.values():
            all_entries.extend(section.entries)
        return all_entries
    
    def count_entries(self) -> int:
        """Get total number of entries across all sections"""
        return sum(section.count_entries() for section in self.sections.values())


class DataLoader(ABC):
    """Abstract base class for data loaders"""
    
    @abstractmethod
    def can_load(self, source: str) -> bool:
        """Check if this loader can handle the given source"""
        pass
    
    @abstractmethod
    def load(self, source: str) -> Dict[str, Any]:
        """Load data from source"""
        pass


class JSONDataLoader(DataLoader):
    """Loads data from JSON files"""
    
    def can_load(self, source: str) -> bool:
        """Check if source is a JSON file"""
        return Path(source).suffix.lower() == '.json' and Path(source).exists()
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load JSON data"""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {source}: {e}")
            return {}


class CSVDataLoader(DataLoader):
    """Loads data from CSV files"""
    
    def can_load(self, source: str) -> bool:
        """Check if source is a CSV file"""
        return Path(source).suffix.lower() == '.csv' and Path(source).exists()
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load CSV data and convert to standard format"""
        try:
            import csv
            entries = []
            
            with open(source, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entries.append(dict(row))
            
            # Convert to standard format
            return {
                'entries': entries,
                'source_type': 'csv',
                'source_file': source
            }
        except Exception as e:
            logger.error(f"Error loading CSV file {source}: {e}")
            return {}


class DataParser:
    """Parses loaded data into ContentEntry objects"""
    
    def __init__(self, structure_config: Dict[str, Any] = None):
        self.structure_config = structure_config or {}
    
    def parse_data(self, data: Dict[str, Any], content_type: str = "vocabulary") -> List[ContentEntry]:
        """Parse raw data into ContentEntry objects"""
        entries = []
        
        # Direct entries list
        if 'entries' in data:
            for entry_data in data['entries']:
                entries.append(ContentEntry(entry_data, content_type))
        
        # Words/items list
        elif 'words' in data or 'items' in data:
            word_list = data.get('words', data.get('items', []))
            for entry_data in word_list:
                entries.append(ContentEntry(entry_data, content_type))
        
        return entries
    
    def parse_into_sections(self, data: Dict[str, Any], content_type: str = "vocabulary") -> List[ContentSection]:
        """Parse data into ContentSection objects"""
        sections = []
        
        # Pattern: nested structure (days, lessons, etc.)
        for container_key in ['days', 'lessons', 'sections', 'chapters', 'units']:
            if container_key in data:
                container = data[container_key]
                
                for section_key, section_data in container.items():
                    # Parse entries
                    section_entries = self.parse_data(section_data, content_type)
                    
                    # Create section
                    section = ContentSection(
                        title=section_data.get('title', section_key),
                        topic=section_data.get('topic', 'General'),
                        entries=section_entries,
                        metadata=section_data.get('metadata', {}),
                        section_id=section_key
                    )
                    sections.append(section)
                break
        
        # If no nested structure, create single section
        if not sections:
            entries = self.parse_data(data, content_type)
            if entries:
                section = ContentSection(
                    title=data.get('title', 'Main'),
                    topic=data.get('topic', 'General'),
                    entries=entries,
                    metadata=data.get('metadata', {}),
                    section_id='main'
                )
                sections.append(section)
        
        return sections
    
    def parse_into_unit(self, data: Dict[str, Any], content_type: str = "vocabulary") -> ContentUnit:
        """Parse data into a ContentUnit object"""
        sections = self.parse_into_sections(data, content_type)
        
        # Create unit
        unit = ContentUnit(
            title=data.get('title', data.get('topic', 'Unit')),
            unit_number=data.get('unit', data.get('week', data.get('chapter', 1))),
            sections={},
            metadata=data.get('metadata', {}),
            unit_type=data.get('unit_type', 'unit')
        )
        
        # Add sections
        for section in sections:
            unit.add_section(section.section_id, section)
        
        return unit


class DataCache:
    """Simple in-memory cache for loaded data"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()


class DataManager:
    """Generic data manager for language learning content"""
    
    def __init__(self, data_directory: str = "data", cache_enabled: bool = True):
        """
        Initialize DataManager
        
        Args:
            data_directory: Base directory for data files
            cache_enabled: Whether to enable caching
        """
        self.data_directory = Path(data_directory)
        self.cache_enabled = cache_enabled
        self.cache = DataCache() if cache_enabled else None
        
        # Registry of data loaders
        self.loaders = {
            'json': JSONDataLoader(),
            'csv': CSVDataLoader()
        }
        
        # Data parser
        self.parser = DataParser()
        
        # Loaded content units by type
        self.content_units = {}  # content_type -> {unit_id: ContentUnit}
        
    def register_loader(self, name: str, loader: DataLoader) -> None:
        """Register a custom data loader"""
        self.loaders[name] = loader
        logger.info(f"Registered data loader: {name}")
    
    def _get_cache_key(self, source: str, content_type: str) -> str:
        """Generate cache key"""
        return f"{content_type}:{source}"
    
    def _find_loader(self, source: str) -> Optional[DataLoader]:
        """Find appropriate loader for source"""
        for loader in self.loaders.values():
            if loader.can_load(source):
                return loader
        return None
    
    def load_from_file(self, filepath: str, content_type: str = "vocabulary") -> Optional[ContentUnit]:
        """
        Load content from a single file
        
        Args:
            filepath: Path to data file
            content_type: Type of content (vocabulary, grammar, etc.)
            
        Returns:
            ContentUnit object or None if failed
        """
        cache_key = self._get_cache_key(filepath, content_type)
        
        # Check cache first
        if self.cache_enabled and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Loaded from cache: {filepath}")
                return cached
        
        # Find appropriate loader
        loader = self._find_loader(filepath)
        if not loader:
            logger.error(f"No loader found for file: {filepath}")
            return None
        
        # Load raw data
        raw_data = loader.load(filepath)
        if not raw_data:
            return None
        
        # Parse into ContentUnit
        unit = self.parser.parse_into_unit(raw_data, content_type)
        
        # Cache result
        if self.cache_enabled and self.cache:
            self.cache.set(cache_key, unit)
        
        logger.info(f"Loaded {content_type} unit: {filepath} ({unit.count_entries()} entries)")
        return unit
    
    def load_content_type(self, content_type: str, pattern: str = "*.json") -> Dict[str, ContentUnit]:
        """
        Load all files of a content type matching pattern
        
        Args:
            content_type: Type of content
            pattern: File pattern to match
            
        Returns:
            Dictionary of unit_id -> ContentUnit
        """
        content_dir = self.data_directory / content_type
        if not content_dir.exists():
            logger.warning(f"Content directory not found: {content_dir}")
            return {}
        
        units = {}
        files = list(content_dir.glob(pattern))
        
        for filepath in files:
            unit = self.load_from_file(str(filepath), content_type)
            if unit:
                unit_id = filepath.stem  # Use filename without extension as ID
                units[unit_id] = unit
        
        # Store in manager
        self.content_units[content_type] = units
        
        logger.info(f"Loaded {len(units)} {content_type} units")
        return units
    
    def get_content_unit(self, content_type: str, unit_id: str) -> Optional[ContentUnit]:
        """Get a specific content unit"""
        if content_type in self.content_units:
            return self.content_units[content_type].get(unit_id)
        return None
    
    def get_content_section(self, content_type: str, unit_id: str, section_id: str) -> Optional[ContentSection]:
        """Get a specific content section"""
        unit = self.get_content_unit(content_type, unit_id)
        if unit:
            return unit.get_section(section_id)
        return None
    
    def search_entries(self, content_type: str, field: str, value: Any) -> List[ContentEntry]:
        """Search for entries matching field value across all units"""
        results = []
        
        if content_type in self.content_units:
            for unit in self.content_units[content_type].values():
                for entry in unit.get_all_entries():
                    if entry.get(field) == value:
                        results.append(entry)
        
        return results
    
    def get_available_content_types(self) -> List[str]:
        """Get list of available content types"""
        types = []
        if self.data_directory.exists():
            for item in self.data_directory.iterdir():
                if item.is_dir():
                    types.append(item.name)
        return types
    
    def get_available_units(self, content_type: str) -> List[str]:
        """Get list of available unit IDs for a content type"""
        if content_type in self.content_units:
            return list(self.content_units[content_type].keys())
        return []
    
    def get_statistics(self, content_type: str) -> Dict[str, Any]:
        """Get statistics for a content type"""
        if content_type not in self.content_units:
            return {}
        
        units = self.content_units[content_type]
        total_entries = sum(unit.count_entries() for unit in units.values())
        total_sections = sum(len(unit.sections) for unit in units.values())
        
        return {
            'content_type': content_type,
            'total_units': len(units),
            'total_sections': total_sections,
            'total_entries': total_entries,
            'units': {
                unit_id: {
                    'entries': unit.count_entries(),
                    'sections': len(unit.sections)
                }
                for unit_id, unit in units.items()
            }
        }
    
    def reload_content_type(self, content_type: str) -> bool:
        """Reload all content for a type"""
        try:
            # Clear cache for this content type
            if self.cache_enabled and self.cache:
                keys_to_remove = [key for key in self.cache.cache.keys() if key.startswith(f"{content_type}:")]
                for key in keys_to_remove:
                    del self.cache.cache[key]
                    if key in self.cache.access_order:
                        self.cache.access_order.remove(key)
            
            # Reload content
            self.load_content_type(content_type)
            return True
        except Exception as e:
            logger.error(f"Error reloading {content_type}: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        if self.cache:
            self.cache.clear()
        logger.info("Cache cleared")


# Example usage
if __name__ == "__main__":
    # Create data manager
    data_manager = DataManager("data")
    
    # Load vocabulary content
    vocabulary_units = data_manager.load_content_type("vocabulary")
    print(f"Loaded vocabulary units: {list(vocabulary_units.keys())}")
    
    # Get specific unit
    week1 = data_manager.get_content_unit("vocabulary", "week1")
    if week1:
        print(f"Week 1 has {week1.count_entries()} entries in {len(week1.sections)} sections")
    
    # Get statistics
    stats = data_manager.get_statistics("vocabulary")
    print(f"Vocabulary statistics: {stats}")
    
    # Search for entries
    results = data_manager.search_entries("vocabulary", "difficulty", 1)
    print(f"Found {len(results)} easy vocabulary entries")