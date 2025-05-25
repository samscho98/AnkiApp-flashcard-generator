"""
Generic CSV Generator for Language Learning Flashcards
Converts JSON content to AnkiApp-compatible CSV files for any language
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass

from .card_formatter import AnkiAppFormatter, FormatterFactory

logger = logging.getLogger(__name__)


@dataclass
class GenericContentEntry:
    """Generic content entry for language learning"""
    target: str  # Target language word/phrase
    native: str  # Native language translation
    content_type: str = "vocabulary"  # vocabulary, grammar, phrase, etc.
    example: Optional[str] = None
    example_translation: Optional[str] = None
    pronunciation: Optional[str] = None
    notes: Optional[str] = None
    difficulty: Optional[int] = None
    tags: Optional[List[str]] = None
    connections: Optional[Dict[str, str]] = None  # Connections to other languages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'target': self.target,
            'native': self.native,
            'content_type': self.content_type,
            'example': self.example,
            'example_translation': self.example_translation,
            'pronunciation': self.pronunciation,
            'notes': self.notes,
            'difficulty': self.difficulty,
            'tags': self.tags or [],
            'connections': self.connections or {}
        }

class GenericLanguageCSVGenerator:
    """Generic CSV generator for language learning content"""
    
    def __init__(self, output_dir: str = "output", config: Dict[str, Any] = None):
        """
        Initialize Generic CSV Generator
        
        Args:
            output_dir: Directory to save generated CSV files
            config: Configuration for generation
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {}
        
        # Available formatters
        self.formatters = {
            'ankiapp': AnkiAppFormatter,
            'generic': self._get_generic_formatter
        }
    
    def _get_generic_formatter(self):
        """Get generic formatter"""
        return AnkiAppFormatter  # For now, use AnkiApp as generic
    
    def generate_from_json_file(self, json_file: str, 
                               formatter_type: str = 'ankiapp',
                               custom_config: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate CSV from JSON file
        
        Args:
            json_file: Path to JSON file
            formatter_type: Type of formatter to use
            custom_config: Custom configuration for formatter
            
        Returns:
            Path to generated CSV file or None if failed
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_file}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {json_file}: {e}")
            return None
        
        return self.generate_from_data(data, json_file, formatter_type, custom_config)
    
    def generate_from_data(self, data: Dict[str, Any], 
                          source_name: str = "",
                          formatter_type: str = 'ankiapp',
                          custom_config: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate CSV from data dictionary
        
        Args:
            data: Data dictionary
            source_name: Name of source (for filename)
            formatter_type: Type of formatter to use
            custom_config: Custom configuration for formatter
            
        Returns:
            Path to generated CSV file or None if failed
        """
        # Extract entries from various possible structures
        entries_with_metadata = self._extract_entries(data)
        
        if not entries_with_metadata:
            logger.warning(f"No entries found in data")
            return None
        
        # Setup formatter
        formatter_config = custom_config or self._get_default_config()
        formatter_class = self.formatters.get(formatter_type, AnkiAppFormatter)
        formatter = formatter_class(formatter_config)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        source_clean = Path(source_name).stem if source_name else "flashcards"
        filename = f"{source_clean}_{timestamp}.csv"
        filepath = self.output_dir / filename
        
        # Generate CSV
        return self._write_csv(entries_with_metadata, formatter, filepath)
    
    def generate_from_entries(self, entries: List[Dict[str, Any]], 
                             metadata: Dict[str, Any] = None,
                             output_filename: str = None,
                             formatter_type: str = 'ankiapp',
                             custom_config: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate CSV from list of entries
        
        Args:
            entries: List of entry dictionaries
            metadata: Metadata to apply to all entries
            output_filename: Custom output filename
            formatter_type: Type of formatter to use
            custom_config: Custom configuration for formatter
            
        Returns:
            Path to generated CSV file or None if failed
        """
        if not entries:
            logger.warning("No entries provided")
            return None
        
        metadata = metadata or {}
        
        # Create entries with metadata tuples
        entries_with_metadata = [(entry, metadata) for entry in entries]
        
        # Setup formatter
        formatter_config = custom_config or self._get_default_config()
        formatter_class = self.formatters.get(formatter_type, AnkiAppFormatter)
        formatter = formatter_class(formatter_config)
        
        # Generate filename
        if output_filename:
            filename = output_filename
            if not filename.endswith('.csv'):
                filename += '.csv'
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            content_type = metadata.get('content_type', 'flashcards')
            filename = f"{content_type}_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Generate CSV
        return self._write_csv(entries_with_metadata, formatter, filepath)
    
    def _extract_entries(self, data: Dict[str, Any]) -> List[tuple]:
        """
        Extract entries from various JSON structures
        
        Args:
            data: Data dictionary
            
        Returns:
            List of (entry_data, metadata) tuples
        """
        entries_with_metadata = []
        
        # Base metadata from top level
        base_metadata = {
            'target_language': data.get('target_language', data.get('language', '')),
            'native_language': data.get('native_language', 'english'),
            'content_type': data.get('content_type', data.get('type', 'vocabulary')),
            'topic': data.get('topic', data.get('title', '')),
            'level': data.get('level', data.get('difficulty', '')),
            'source': data.get('source', '')
        }
        
        # Direct entries (flat structure)
        if 'entries' in data:
            entries = data['entries']
            for entry in entries:
                entries_with_metadata.append((entry, base_metadata.copy()))
        
        elif 'words' in data:
            entries = data['words']
            for entry in entries:
                entries_with_metadata.append((entry, base_metadata.copy()))
        
        elif 'items' in data:
            entries = data['items']
            for entry in entries:
                entries_with_metadata.append((entry, base_metadata.copy()))
        
        # Nested structure (units/weeks/days/lessons/etc.)
        else:
            for container_key in ['units', 'weeks', 'days', 'lessons', 'sections', 'chapters']:
                if container_key in data:
                    container = data[container_key]
                    
                    for unit_key, unit_data in container.items():
                        # Extract unit number from key (e.g., "week_1" -> 1, "unit1" -> 1)
                        unit_number = self._extract_number_from_key(unit_key)
                        
                        unit_metadata = base_metadata.copy()
                        unit_metadata.update({
                            'unit': unit_number,
                            'unit_name': unit_key,
                            'unit_topic': unit_data.get('topic', unit_data.get('title', ''))
                        })
                        
                        # Check for nested sections within unit
                        unit_entries = []
                        if 'entries' in unit_data:
                            unit_entries = unit_data['entries']
                        elif 'words' in unit_data:
                            unit_entries = unit_data['words']
                        elif 'items' in unit_data:
                            unit_entries = unit_data['items']
                        
                        # Add entries from this unit
                        for entry in unit_entries:
                            entries_with_metadata.append((entry, unit_metadata.copy()))
                        
                        # Check for sub-sections (days within weeks, etc.)
                        for sub_container_key in ['days', 'lessons', 'sections']:
                            if sub_container_key in unit_data:
                                sub_container = unit_data[sub_container_key]
                                
                                for sub_key, sub_data in sub_container.items():
                                    sub_number = self._extract_number_from_key(sub_key)
                                    
                                    sub_metadata = unit_metadata.copy()
                                    sub_metadata.update({
                                        'section': sub_number,
                                        'section_name': sub_key,
                                        'section_topic': sub_data.get('topic', sub_data.get('title', ''))
                                    })
                                    
                                    # Get entries from sub-section
                                    sub_entries = []
                                    if 'entries' in sub_data:
                                        sub_entries = sub_data['entries']
                                    elif 'words' in sub_data:
                                        sub_entries = sub_data['words']
                                    elif 'items' in sub_data:
                                        sub_entries = sub_data['items']
                                    
                                    for entry in sub_entries:
                                        entries_with_metadata.append((entry, sub_metadata.copy()))
                    
                    break  # Only process first found container type
        
        return entries_with_metadata
    
    def _extract_number_from_key(self, key: str) -> int:
        """Extract number from key like 'week_1', 'day1', 'unit_2', etc."""
        import re
        numbers = re.findall(r'\d+', key)
        return int(numbers[0]) if numbers else 1
    
    def _write_csv(self, entries_with_metadata: List[tuple], formatter, filepath: Path) -> Optional[str]:
        """Write CSV file"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write entries only
                success_count = 0
                for entry_data, metadata in entries_with_metadata:
                    try:
                        row = formatter.format_entry(entry_data, metadata)
                        writer.writerow(row)
                        success_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to format entry: {e}")
                        continue
            
            logger.info(f"Generated CSV: {filepath} ({success_count} entries)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error writing CSV file {filepath}: {e}")
            return None
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'tag_prefix': 'Language_Learning',
            'include_html_formatting': True,
            'show_connections': True,
            'target_language': 'Target',
            'native_language': 'English',
            'field_mappings': {
                'target': 'target',
                'native': 'native',
                'example': 'example',
                'pronunciation': 'pronunciation',
                'notes': 'notes'
            }
        }
    
    def create_sample_json(self, output_path: str, content_type: str = "vocabulary") -> bool:
        """
        Create a sample JSON file for reference
        
        Args:
            output_path: Path for sample file
            content_type: Type of content (vocabulary, grammar, etc.)
            
        Returns:
            True if successful
        """
        if content_type == "vocabulary":
            sample_data = {
                "target_language": "german",
                "native_language": "english",
                "content_type": "vocabulary",
                "title": "Sample Vocabulary",
                "topic": "Basic Words",
                "level": "beginner",
                "entries": [
                    {
                        "target": "das Haus",
                        "native": "the house",
                        "example": "Das Haus ist groß.",
                        "example_translation": "The house is big.",
                        "pronunciation": "dahs hows",
                        "connections": {
                            "dutch": "het huis",
                            "spanish": "la casa"
                        },
                        "difficulty": 1,
                        "tags": ["building", "noun"]
                    },
                    {
                        "target": "gehen",
                        "native": "to go",
                        "example": "Ich gehe nach Hause.",
                        "example_translation": "I go home.",
                        "pronunciation": "GAY-en",
                        "connections": {
                            "dutch": "gaan"
                        },
                        "difficulty": 1,
                        "tags": ["verb", "movement"]
                    }
                ]
            }
        elif content_type == "grammar":
            sample_data = {
                "target_language": "german",
                "native_language": "english",
                "content_type": "grammar",
                "title": "Sample Grammar Rules",
                "topic": "Basic Grammar",
                "level": "beginner",
                "entries": [
                    {
                        "target": "German Articles",
                        "native": "der, die, das (the)",
                        "content_type": "grammar",
                        "example": "der Mann, die Frau, das Kind",
                        "example_translation": "the man, the woman, the child",
                        "notes": "German has three grammatical genders",
                        "difficulty": 2,
                        "tags": ["articles", "gender"]
                    }
                ]
            }
        else:
            sample_data = {
                "target_language": "target_lang",
                "native_language": "english",
                "content_type": content_type,
                "title": f"Sample {content_type.title()}",
                "entries": [
                    {
                        "target": "sample target",
                        "native": "sample translation",
                        "example": "sample example",
                        "notes": "sample notes"
                    }
                ]
            }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Created sample JSON: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating sample JSON: {e}")
            return False


# Utility functions for easy usage
def generate_flashcards_from_json(json_file: str, output_dir: str = "output") -> Optional[str]:
    """Quick function to generate flashcards from JSON file"""
    generator = GenericLanguageCSVGenerator(output_dir)
    return generator.generate_from_json_file(json_file)

def create_sample_files(output_dir: str = "data") -> bool:
    """Create sample JSON files for reference"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    generator = GenericLanguageCSVGenerator()
    success = True
    
    # Create vocabulary sample
    success &= generator.create_sample_json(f"{output_dir}/sample_vocabulary.json", "vocabulary")
    # Create grammar sample
    success &= generator.create_sample_json(f"{output_dir}/sample_grammar.json", "grammar")
    
    return success


# Example usage and testing
if __name__ == "__main__":
    # Create generator
    generator = GenericLanguageCSVGenerator("output")
    
    # Create sample files
    print("Creating sample files...")
    create_sample_files("data")
    
    # Generate CSV from sample vocabulary
    vocab_csv = generator.generate_from_json_file("data/sample_vocabulary.json")
    if vocab_csv:
        print(f"Generated vocabulary CSV: {vocab_csv}")
    
    # Generate CSV from sample grammar
    grammar_csv = generator.generate_from_json_file("data/sample_grammar.json")
    if grammar_csv:
        print(f"Generated grammar CSV: {grammar_csv}")
    
    # Test with custom entries
    custom_entries = [
        {
            "target": "bonjour",
            "native": "hello",
            "example": "Bonjour, comment allez-vous?",
            "example_translation": "Hello, how are you?",
            "pronunciation": "bon-ZHOOR"
        },
        {
            "target": "merci",
            "native": "thank you",
            "example": "Merci beaucoup!",
            "example_translation": "Thank you very much!",
            "pronunciation": "mer-SEE"
        }
    ]
    
    custom_metadata = {
        "target_language": "french",
        "content_type": "vocabulary",
        "topic": "greetings"
    }
    
    custom_csv = generator.generate_from_entries(
        custom_entries, 
        custom_metadata, 
        "french_greetings.csv"
    )
    if custom_csv:
        print(f"Generated custom CSV: {custom_csv}")