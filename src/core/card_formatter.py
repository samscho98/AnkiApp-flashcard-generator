"""
Card Formatter Module for Language Learning Flashcard Generator
Handles formatting of flashcard content for different export formats
Enhanced with flexible language support
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FormattedCard:
    """Represents a formatted flashcard"""
    front: str
    back: str
    tags: List[str]
    metadata: Dict[str, Any]
    format_type: str = "html"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'front': self.front,
            'back': self.back,
            'tags': self.tags,
            'metadata': self.metadata,
            'format_type': self.format_type
        }


class LanguageFieldMapper:
    """Handles mapping between language names and JSON field names"""
    
    def __init__(self, languages_file: str = "languages.txt"):
        """Initialize language mapper"""
        self.languages_file = Path(languages_file)
        self.language_mappings = self._load_language_mappings()
    
    def _load_language_mappings(self) -> Dict[str, List[str]]:
        """Load language field mappings from file"""
        mappings = {}
        
        # Default fallback mappings
        default_mappings = {
            'german': ['German', 'german', 'target', 'word', 'term'],
            'english': ['English', 'english', 'native', 'translation', 'answer'],
            'dutch': ['Dutch', 'dutch', 'nederlands'],
            'spanish': ['Spanish', 'spanish', 'español'],
            'french': ['French', 'french', 'français'],
            'italian': ['Italian', 'italian', 'italiano'],
            'portuguese': ['Portuguese', 'portuguese', 'português'],
            'tagalog': ['Tagalog', 'tagalog']
        }
        
        # Try to load from file if it exists
        if self.languages_file.exists():
            try:
                with open(self.languages_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if ':' in line:
                                lang_code, field_names = line.split(':', 1)
                                fields = [name.strip() for name in field_names.split(',')]
                                mappings[lang_code.strip().lower()] = fields
            except Exception as e:
                logger.warning(f"Error loading languages file: {e}, using defaults")
        
        # Merge with defaults
        for lang, fields in default_mappings.items():
            if lang not in mappings:
                mappings[lang] = fields
        
        return mappings
    
    def get_field_names(self, language: str) -> List[str]:
        """Get possible field names for a language"""
        lang_key = language.lower().strip()
        return self.language_mappings.get(lang_key, [language.capitalize(), language.lower()])
    
    def detect_language_fields(self, entry_data: Dict[str, Any]) -> Dict[str, str]:
        """Detect which languages are present in the entry data"""
        detected = {}
        entry_fields = set(entry_data.keys())
        
        for lang_code, possible_fields in self.language_mappings.items():
            for field_name in possible_fields:
                if field_name in entry_fields and entry_data[field_name]:
                    detected[lang_code] = field_name
                    break
        
        return detected


# Global language mapper instance
_language_mapper = LanguageFieldMapper()


class CardFormatter(ABC):
    """Abstract base class for card formatters"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize card formatter
        
        Args:
            config: Configuration for formatting
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def get_headers(self) -> List[str]:
        """Get CSV headers for this format"""
        pass
    
    @abstractmethod
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict = None) -> List[str]:
        """Format entry for export"""
        pass
    
    def get_supported_fields(self) -> List[str]:
        """Get list of supported fields for this formatter"""
        return ['target', 'native', 'example', 'pronunciation', 'notes', 'connections']
    
    def validate_entry(self, entry_data: Dict[str, Any]) -> bool:
        """Validate that entry has required fields"""
        required_fields = self.config.get('required_fields', ['target', 'native'])
        return all(field in entry_data and entry_data[field] for field in required_fields)


class HTMLCardFormatter(CardFormatter):
    """Base HTML formatter for rich formatting"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize HTML formatter"""
        super().__init__(config)
        
        # HTML formatting settings
        self.use_html = self.config.get('use_html', True)
        self.css_classes = self.config.get('css_classes', {})
        self.custom_styles = self.config.get('custom_styles', {})
    
    def wrap_html_tag(self, content: str, tag: str, attributes: Dict[str, str] = None) -> str:
        """Wrap content in HTML tag"""
        if not self.use_html:
            return content
        
        attrs = ""
        if attributes:
            attrs = " " + " ".join(f'{k}="{v}"' for k, v in attributes.items())
        
        return f"<{tag}{attrs}>{content}</{tag}>"
    
    def format_bold(self, text: str) -> str:
        """Format text as bold"""
        return self.wrap_html_tag(text, "b") if self.use_html else f"**{text}**"
    
    def format_italic(self, text: str) -> str:
        """Format text as italic"""
        return self.wrap_html_tag(text, "i") if self.use_html else f"*{text}*"
    
    def format_line_break(self) -> str:
        """Format line break"""
        return "<br>" if self.use_html else "\n"
    
    def format_paragraph_break(self) -> str:
        """Format paragraph break"""
        return "<br><br>" if self.use_html else "\n\n"
    
    def format_list(self, items: List[str], ordered: bool = False) -> str:
        """Format list of items"""
        if not self.use_html:
            return "\n".join(f"{'1.' if ordered else '•'} {item}" for item in items)
        
        tag = "ol" if ordered else "ul"
        list_items = "".join(f"<li>{item}</li>" for item in items)
        return f"<{tag}>{list_items}</{tag}>"
    
    def get_headers(self) -> List[str]:
        """Default headers for HTML formatter"""
        return ["Front", "Back"]
    
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict = None) -> List[str]:
        """Basic HTML formatting"""
        metadata = metadata or {}
        
        front = entry_data.get('target', '')
        back = self.format_bold(entry_data.get('native', ''))
        
        return [front, back]


class AnkiAppFormatter(HTMLCardFormatter):
    """Formats content entries for AnkiApp import with flexible language support"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize AnkiApp formatter
        
        Args:
            config: Configuration for formatting
        """
        super().__init__(config)
        
        # Configuration
        self.tag_prefix = self.config.get('tag_prefix', 'Language_Learning')
        self.include_html_formatting = self.config.get('include_html_formatting', True)
        self.show_connections = self.config.get('show_connections', True)
        self.target_language = self.config.get('target_language', 'Target')
        self.native_language = self.config.get('native_language', 'English')
        
        # Use language mapper for flexible field detection
        self.language_mapper = _language_mapper
        
        # Base field mappings - will be enhanced by language detection
        self.field_mappings = self.config.get('field_mappings', {
            'target': ['target', 'word', 'term', 'question', 'front'],
            'native': ['native', 'translation', 'answer', 'meaning', 'back'],
            'example': ['example', 'examples', 'example_sentence'],
            'pronunciation': ['pronunciation', 'phonetic', 'sound'],
            'notes': ['notes', 'note', 'memory_tip', 'tip'],
            'tags': ['tags', 'Tags', 'categories', 'tag']
        })
    
    def _detect_and_update_field_mappings(self, entry_data: Dict[str, Any]) -> None:
        """Detect languages in entry and update field mappings accordingly"""
        detected_languages = self.language_mapper.detect_language_fields(entry_data)
        
        # Debug logging
        logger.debug(f"Entry fields: {list(entry_data.keys())}")
        logger.debug(f"Detected languages: {detected_languages}")
        
        # If we don't have specific target/native language config, try to auto-detect
        target_lang = self.target_language.lower() if self.target_language != 'Target' else None
        native_lang = self.native_language.lower() if self.native_language != 'English' else None
        
        # Auto-detect target and native languages from the entry
        non_english_langs = [lang for lang in detected_languages.keys() if lang != 'english']
        english_detected = 'english' in detected_languages
        
        # If we found a non-English language and English, use them
        if non_english_langs and english_detected:
            # Use the first non-English language as target
            auto_target = non_english_langs[0]
            auto_native = 'english'
            
            # Override config if not specifically set
            if target_lang is None or target_lang == 'german':
                target_lang = auto_target
            if native_lang is None:
                native_lang = auto_native
                
            logger.debug(f"Auto-detected target: {target_lang}, native: {native_lang}")
        
        # Add detected field names directly to mappings
        for lang_code, field_name in detected_languages.items():
            # If this language matches our target language
            if (lang_code == target_lang or 
                (target_lang is None and lang_code != 'english')):
                if field_name not in self.field_mappings['target']:
                    self.field_mappings['target'].insert(0, field_name)
                    logger.debug(f"Added '{field_name}' to target fields")
            
            # If this language matches our native language  
            elif (lang_code == native_lang or 
                  (native_lang is None and lang_code == 'english')):
                if field_name not in self.field_mappings['native']:
                    self.field_mappings['native'].insert(0, field_name)
                    logger.debug(f"Added '{field_name}' to native fields")
        
        # Also add language-specific fields from the mapper
        if target_lang and target_lang in self.language_mapper.language_mappings:
            target_fields = self.language_mapper.get_field_names(target_lang)
            for field in target_fields:
                if field not in self.field_mappings['target']:
                    self.field_mappings['target'].append(field)
        
        if native_lang and native_lang in self.language_mapper.language_mappings:
            native_fields = self.language_mapper.get_field_names(native_lang)
            for field in native_fields:
                if field not in self.field_mappings['native']:
                    self.field_mappings['native'].append(field)
        
        logger.debug(f"Final target fields: {self.field_mappings['target']}")
        logger.debug(f"Final native fields: {self.field_mappings['native']}")
    
    def _safe_get_string(self, data: Dict[str, Any], field_keys: Union[str, List[str]], default: str = '') -> str:
        """
        Safely extract string value from data, handling lists and multiple field names
        
        Args:
            data: Data dictionary
            field_keys: Single field name or list of possible field names
            default: Default value if not found
            
        Returns:
            String value
        """
        if isinstance(field_keys, str):
            field_keys = [field_keys]
        
        for field_key in field_keys:
            if field_key in data:
                value = data[field_key]
                if isinstance(value, list):
                    # If it's a list, join with commas or take first item
                    if value:
                        return ', '.join(str(item) for item in value) if len(value) > 1 else str(value[0])
                elif value:
                    return str(value)
        
        return default
    
    def _safe_get_dict(self, data: Dict[str, Any], field_key: str) -> Dict[str, Any]:
        """Safely get dictionary value"""
        value = data.get(field_key, {})
        return value if isinstance(value, dict) else {}
    
    def get_headers(self) -> List[str]:
        """Get CSV headers for AnkiApp (5 columns to match AnkiApp format)"""
        return ["Front", "Back", "Tag", "", ""]
    
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict = None) -> List[str]:
        """
        Format entry for AnkiApp (5-column format to match AnkiApp CSV structure)
        
        Args:
            entry_data: Entry data dictionary
            metadata: Additional metadata
            
        Returns:
            List representing CSV row [Front, Back, Tags, "", ""]
        """
        metadata = metadata or {}
        
        # Update field mappings based on detected languages
        self._detect_and_update_field_mappings(entry_data)
        
        # Column 1: Front - Target language word/phrase (try multiple field names)
        front = self._safe_get_string(entry_data, self.field_mappings['target'], 'Unknown')
        
        # Column 2: Back - Clean formatted content
        back = self._format_clean_back(entry_data, metadata)
        
        # Column 3: Tags - Simple week + topic format
        tags = self._generate_simple_tags(entry_data, metadata)
        
        # Columns 4 & 5: Empty (AnkiApp format requirement)
        return [front, back, tags, "", ""]
    
    def _format_html_back(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Format back side with HTML"""
        parts = []
        
        # Native translation (bold)
        native = self._safe_get_string(entry_data, self.field_mappings['native'])
        if native:
            parts.append(self.format_bold(native))
        
        # Language connections (if available and enabled)
        if self.show_connections:
            connections = self._safe_get_dict(entry_data, 'connections')
            if connections:
                conn_parts = []
                for lang, word in connections.items():
                    word_str = self._safe_get_string({lang: word}, lang)
                    if word_str:
                        conn_parts.append(f"{lang.title()}: {self.format_italic(word_str)}")
                if conn_parts:
                    parts.append("🔗 " + " | ".join(conn_parts))
        
        # Example sentence
        example = self._safe_get_string(entry_data, self.field_mappings['example'])
        if example:
            parts.append(f"{self.format_bold('Example:')} {example}")
            
            # Example translation
            example_translation = self._safe_get_string(entry_data, 'example_translation')
            if example_translation:
                parts.append(f"{self.format_italic('Translation:')} {example_translation}")
        
        # Pronunciation hint
        pronunciation = self._safe_get_string(entry_data, self.field_mappings['pronunciation'])
        if pronunciation:
            parts.append(f"🔊 {self.format_italic(pronunciation)}")
        
        # Notes
        notes = self._safe_get_string(entry_data, self.field_mappings['notes'])
        if notes:
            parts.append(f"📝 {notes}")
        
        return self.format_paragraph_break().join(parts)
    
    def _format_simple_back(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Format back side with simple text"""
        parts = []
        
        # Native translation
        native = self._safe_get_string(entry_data, self.field_mappings['native'])
        if native:
            parts.append(native)
        
        # Language connections
        if self.show_connections:
            connections = self._safe_get_dict(entry_data, 'connections')
            if connections:
                conn_parts = []
                for lang, word in connections.items():
                    word_str = self._safe_get_string({lang: word}, lang)
                    if word_str:
                        conn_parts.append(f"{lang.title()}: {word_str}")
                if conn_parts:
                    parts.append(" | ".join(conn_parts))
        
        # Example
        example = self._safe_get_string(entry_data, self.field_mappings['example'])
        if example:
            parts.append(f"Example: {example}")
            
            example_translation = self._safe_get_string(entry_data, 'example_translation')
            if example_translation:
                parts.append(f"({example_translation})")
        
        # Pronunciation
        pronunciation = self._safe_get_string(entry_data, self.field_mappings['pronunciation'])
        if pronunciation:
            parts.append(f"Pronunciation: {pronunciation}")
        
        # Notes
        notes = self._safe_get_string(entry_data, self.field_mappings['notes'])
        if notes:
            parts.append(f"Note: {notes}")
        
        return " | ".join(parts)
    
    def _format_clean_back(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Format back side with clean, simple formatting - handles lists safely"""
        parts = []
        
        # Main translation (no bold formatting)
        native = self._safe_get_string(entry_data, self.field_mappings['native'])
        if native:
            main_translation = native
            
            # Add Dutch connection inline if available
            dutch_connection = ''
            
            # Try 'dutch_connection' field first
            if 'dutch_connection' in entry_data:
                dutch_connection = self._safe_get_string(entry_data, 'dutch_connection')
            
            # Try connections dict
            elif self.show_connections:
                connections = self._safe_get_dict(entry_data, 'connections')
                if 'dutch' in connections:
                    dutch_connection = self._safe_get_string(connections, 'dutch')
            
            if dutch_connection:
                main_translation += f" (🇳🇱 Dutch: {dutch_connection})"
            
            parts.append(main_translation)
        
        # Example in italics
        example = self._safe_get_string(entry_data, self.field_mappings['example'])
        if example:
            parts.append(f"<i>Example: {example}</i>")
        
        # Pronunciation (if available, in italics)
        pronunciation = self._safe_get_string(entry_data, self.field_mappings['pronunciation'])
        if pronunciation:
            parts.append(f"<i>🔊 Pronunciation: {pronunciation}</i>")
        
        # Notes (if available, in italics)  
        notes = self._safe_get_string(entry_data, self.field_mappings['notes'])
        if notes:
            parts.append(f"<i>📝 Note: {notes}</i>")
        
        return "<br><br>".join(parts)
    
    def _generate_simple_tags(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generate simple, clean tags like 'Week1,Greetings' - handles lists safely"""
        tags = []
        
        # Week tag
        week = metadata.get('week', metadata.get('unit', ''))
        if week:
            tags.append(f"Week{week}")
        
        # Topic tag (cleaned and simplified)
        topic = metadata.get('section_topic', metadata.get('topic', ''))
        if topic:
            # Clean up the topic - safely handle if it's a list
            topic_str = str(topic) if not isinstance(topic, list) else str(topic[0]) if topic else ''
            topic_clean = (topic_str
                          .split(',')[0]  # Take first part if comma-separated
                          .replace('&', 'and')  # Replace & with 'and'
                          .replace(' and ', ' ')  # Simplify "greetings and politeness" -> "greetings"
                          .strip()
                          .split()[0]  # Take first word only
                          .capitalize())  # Capitalize first letter
            
            if topic_clean:
                tags.append(topic_clean)
        
        # Add content type if not vocabulary (default)
        content_type = self._safe_get_string(entry_data, ['content_type', 'type'], 'vocabulary')
        if content_type.lower() != 'vocabulary':
            tags.append(content_type.capitalize())
        
        # Add any explicit tags from the entry data (handle lists)
        entry_tags = entry_data.get('tags', [])
        if entry_tags:
            if isinstance(entry_tags, list):
                # Take first few tags and clean them
                for tag in entry_tags[:2]:  # Limit to 2 additional tags
                    clean_tag = str(tag).strip().capitalize()
                    if clean_tag and clean_tag not in tags:
                        tags.append(clean_tag)
            else:
                clean_tag = str(entry_tags).strip().capitalize()
                if clean_tag and clean_tag not in tags:
                    tags.append(clean_tag)
        
        return ",".join(tags)
    
    def _generate_tag(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generate single tag for compatibility - delegates to _generate_simple_tags"""
        return self._generate_simple_tags(entry_data, metadata)
    
    def format_card_preview(self, entry_data: Dict[str, Any], metadata: Dict = None) -> FormattedCard:
        """Create a formatted card object for preview"""
        metadata = metadata or {}
        
        front = self._safe_get_string(entry_data, self.field_mappings['target'], 'Unknown')
        back = self._format_html_back(entry_data, metadata) if self.include_html_formatting else self._format_simple_back(entry_data, metadata)
        tag = self._generate_simple_tags(entry_data, metadata)
        
        return FormattedCard(
            front=front,
            back=back,
            tags=[tag],
            metadata=metadata,
            format_type="ankiapp"
        )


class CommonPhrasesFormatter(AnkiAppFormatter):
    """Specialized formatter for common phrases with enhanced formatting"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize common phrases formatter"""
        super().__init__(config)
        
        # Phrase-specific settings
        self.show_context_indicators = self.config.get('show_context_indicators', True)
        self.phrase_category_prefix = self.config.get('phrase_category_prefix', '💬')
        
    def _detect_and_update_field_mappings(self, entry_data: Dict[str, Any]) -> None:
        """Override to handle phrase-specific field detection"""
        super()._detect_and_update_field_mappings(entry_data)
        
        # Add phrase-specific field mappings
        phrase_target_fields = ['phrase', 'question']
        phrase_native_fields = ['answer', 'translation']
        
        # Add phrase fields to the beginning of the mapping lists
        for field in reversed(phrase_target_fields):
            if field in entry_data and field not in self.field_mappings['target']:
                self.field_mappings['target'].insert(0, field)
        
        for field in reversed(phrase_native_fields):
            if field in entry_data and field not in self.field_mappings['native']:
                self.field_mappings['native'].insert(0, field)
        
    def _format_clean_back(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Format back side with clean, simple formatting for phrases"""
        parts = []
        
        # Main translation with phrase indicator
        native = self._safe_get_string(entry_data, self.field_mappings['native'])
        if native:
            if self.show_context_indicators:
                main_translation = f"{self.phrase_category_prefix} {native}"
            else:
                main_translation = native
            parts.append(main_translation)
        
        # Context from day topic
        day_topic = metadata.get('section_topic', metadata.get('topic', ''))
        if day_topic and day_topic != 'No topic':
            parts.append(f"<i>Context: {day_topic}</i>")
        
        # Notes (if available)
        notes = self._safe_get_string(entry_data, self.field_mappings['notes'])
        if notes:
            parts.append(f"<i>📝 {notes}</i>")
        
        # Usage level indicator
        week = metadata.get('week', metadata.get('unit', ''))
        if week:
            parts.append(f"<i>Level: A1 Week {week}</i>")
        
        return "<br><br>".join(parts)
    
    def _generate_simple_tags(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generate simple, clean tags for phrases"""
        tags = []
        
        # Week tag
        week = metadata.get('week', metadata.get('unit', ''))
        if week:
            tags.append(f"Week{week}")
        
        # Content type tag
        tags.append("Phrases")
        
        # Day topic tag (cleaned and simplified)
        topic = metadata.get('section_topic', metadata.get('topic', ''))
        if topic:
            # Clean up topic for tag use
            topic_clean = (topic
                          .replace('&', 'and')
                          .replace(' & ', ' ')
                          .replace(',', '')
                          .strip()
                          .split()[0]  # Take first word
                          .capitalize())
            
            if topic_clean and topic_clean not in ['No', 'Topic']:
                tags.append(topic_clean)
        
        # Tags from the JSON data
        json_tags = entry_data.get('Tags', entry_data.get('tags', []))
        if json_tags:
            if isinstance(json_tags, list):
                # Clean and capitalize tags from JSON
                for tag in json_tags[:2]:  # Limit to 2 additional tags
                    clean_tag = str(tag).strip().capitalize()
                    if clean_tag and clean_tag not in tags:
                        tags.append(clean_tag)
            else:
                clean_tag = str(json_tags).strip().capitalize()
                if clean_tag and clean_tag not in tags:
                    tags.append(clean_tag)
        
        return ",".join(tags)


class AnkiFormatter(HTMLCardFormatter):
    """Formats content entries for standard Anki import"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Anki formatter"""
        super().__init__(config)
        
        # Anki-specific settings
        self.note_type = self.config.get('note_type', 'Basic')
        self.deck_name = self.config.get('deck_name', 'Language Learning')
        self.field_separator = self.config.get('field_separator', '\t')
    
    def get_headers(self) -> List[str]:
        """Get headers for Anki import"""
        return ["Front", "Back", "Tags"]
    
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict = None) -> List[str]:
        """Format entry for Anki"""
        metadata = metadata or {}
        
        front = entry_data.get('target', '')
        
        # Build back content
        parts = []
        
        # Native translation
        native = entry_data.get('native', '')
        if native:
            parts.append(self.format_bold(native))
        
        # Example
        example = entry_data.get('example', '')
        if example:
            parts.append(f"{self.format_bold('Example:')} {example}")
        
        back = self.format_line_break().join(parts)
        
        # Tags (space-separated for Anki)
        tags_list = []
        if 'content_type' in entry_data:
            tags_list.append(entry_data['content_type'])
        if metadata.get('unit'):
            tags_list.append(f"Unit{metadata['unit']}")
        
        tags = " ".join(tags_list)
        
        return [front, back, tags]


class QuizletFormatter(CardFormatter):
    """Formats content entries for Quizlet import"""
    
    def get_headers(self) -> List[str]:
        """Get headers for Quizlet (no headers needed)"""
        return []
    
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict = None) -> List[str]:
        """Format entry for Quizlet (term, definition)"""
        term = entry_data.get('target', '')
        
        # Build definition
        definition_parts = []
        
        native = entry_data.get('native', '')
        if native:
            definition_parts.append(native)
        
        example = entry_data.get('example', '')
        if example:
            definition_parts.append(f"Example: {example}")
        
        definition = " | ".join(definition_parts)
        
        return [term, definition]


class GenericFormatter(CardFormatter):
    """Generic formatter for custom export formats"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize generic formatter"""
        super().__init__(config)
        
        self.custom_headers = self.config.get('headers', ['Term', 'Definition'])
        self.field_mapping = self.config.get('field_mapping', {
            'front': 'target',
            'back': 'native'
        })
    
    def get_headers(self) -> List[str]:
        """Get custom headers"""
        return self.custom_headers
    
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict = None) -> List[str]:
        """Format entry using custom field mapping"""
        result = []
        
        for header in self.custom_headers:
            field_key = self.field_mapping.get(header.lower(), header.lower())
            value = entry_data.get(field_key, '')
            result.append(str(value))
        
        return result


class FormatterFactory:
    """Factory for creating card formatters"""
    
    _formatters = {
        'ankiapp': AnkiAppFormatter,
        'phrases': CommonPhrasesFormatter,
        'common_phrases': CommonPhrasesFormatter,
        'anki': AnkiFormatter,
        'quizlet': QuizletFormatter,
        'generic': GenericFormatter,
        'html': HTMLCardFormatter
    }
    
    @classmethod
    def create_formatter(cls, formatter_type: str, config: Dict[str, Any] = None) -> CardFormatter:
        """
        Create formatter instance
        
        Args:
            formatter_type: Type of formatter to create
            config: Configuration for the formatter
            
        Returns:
            Formatter instance
        """
        if formatter_type not in cls._formatters:
            logger.warning(f"Unknown formatter type: {formatter_type}, using generic")
            formatter_type = 'generic'
        
        formatter_class = cls._formatters[formatter_type]
        return formatter_class(config)
    
    @classmethod
    def get_available_formatters(cls) -> List[str]:
        """Get list of available formatter types"""
        return list(cls._formatters.keys())
    
    @classmethod
    def register_formatter(cls, name: str, formatter_class: type) -> None:
        """Register a custom formatter"""
        if not issubclass(formatter_class, CardFormatter):
            raise ValueError(f"Formatter class must inherit from CardFormatter")
        
        cls._formatters[name] = formatter_class
        logger.info(f"Registered custom formatter: {name}")


def create_phrases_sample_data():
    """Create sample data demonstrating the phrases structure"""
    sample_data = {
        "week": 1,
        "topic": "Essential A1 Phrases: Greetings, Politeness, and Basics",
        "source": "Common Goethe A1 Phrases",
        "total_phrases": 4,
        "days": {
            "day_1": {
                "topic": "Greetings & Introductions",
                "phrases": [
                    {
                        "German": "Guten Morgen!",
                        "English": "Good morning!",
                        "Notes": "Used until about 10-11 AM",
                        "Tags": ["greetings", "morning"]
                    },
                    {
                        "German": "Wie heißen Sie?",
                        "English": "What is your name?",
                        "Notes": "Formal version - use with strangers, older people, or in professional settings",
                        "Tags": ["introductions", "questions", "formal"]
                    }
                ]
            },
            "day_2": {
                "topic": "Politeness",
                "phrases": [
                    {
                        "German": "Entschuldigung!",
                        "English": "Excuse me!",
                        "Notes": "Used to get attention or when you need to pass by someone",
                        "Tags": ["politeness", "attention"]
                    },
                    {
                        "German": "Es tut mir leid.",
                        "English": "I'm sorry.",
                        "Notes": "More formal than 'Entschuldigung' - use for genuine apologies",
                        "Tags": ["apologies", "politeness", "formal"]
                    }
                ]
            }
        }
    }
    return sample_data


# Utility functions
def preview_card_formatting(entry_data: Dict[str, Any], 
                          formatter_type: str = 'ankiapp',
                          config: Dict[str, Any] = None) -> str:
    """
    Preview how a card would be formatted
    
    Args:
        entry_data: Entry data to format
        formatter_type: Type of formatter to use
        config: Formatter configuration
        
    Returns:
        Formatted preview string
    """
    formatter = FormatterFactory.create_formatter(formatter_type, config)
    
    if hasattr(formatter, 'format_card_preview'):
        card = formatter.format_card_preview(entry_data)
        return f"Front: {card.front}\n\nBack: {card.back}\n\nTags: {', '.join(card.tags)}"
    else:
        formatted = formatter.format_entry(entry_data)
        headers = formatter.get_headers()
        
        preview_parts = []
        for i, header in enumerate(headers):
            if i < len(formatted):
                preview_parts.append(f"{header}: {formatted[i]}")
        
        return "\n\n".join(preview_parts)


def validate_entry_for_formatter(entry_data: Dict[str, Any], 
                               formatter_type: str = 'ankiapp') -> Dict[str, Any]:
    """
    Validate entry data for a specific formatter
    
    Args:
        entry_data: Entry data to validate
        formatter_type: Type of formatter to validate for
        
    Returns:
        Validation result dictionary
    """
    formatter = FormatterFactory.create_formatter(formatter_type)
    
    result = {
        'is_valid': formatter.validate_entry(entry_data),
        'supported_fields': formatter.get_supported_fields(),
        'missing_fields': [],
        'extra_fields': []
    }
    
    # Check for missing required fields
    required_fields = formatter.config.get('required_fields', ['target', 'native'])
    for field in required_fields:
        if field not in entry_data or not entry_data[field]:
            result['missing_fields'].append(field)
    
    # Check for extra fields
    supported_fields = set(formatter.get_supported_fields())
    entry_fields = set(entry_data.keys())
    result['extra_fields'] = list(entry_fields - supported_fields)
    
    return result


# Example usage and testing
if __name__ == "__main__":
    # Test the formatters with multiple languages
    print("=== Testing Flexible Language Support ===")
    print()
    
    # Test German entry
    german_entry = {
        'German': 'das Haus',
        'English': 'the house',
        'example': 'Das Haus ist groß.',
        'example_translation': 'The house is big.',
        'pronunciation': 'dahs hows',
        'connections': {
            'dutch': 'het huis',
            'spanish': 'la casa'
        },
        'notes': 'Neuter noun, plural: die Häuser'
    }
    
    # Test Spanish entry
    spanish_entry = {
        'Spanish': 'la casa',
        'English': 'the house',
        'example': 'La casa es grande.',
        'pronunciation': 'lah KAH-sah'
    }
    
    # Test French entry
    french_entry = {
        'French': 'la maison',
        'english': 'the house',
        'example': 'La maison est grande.',
        'notes': 'Feminine noun'
    }
    
    sample_metadata = {
        'target_language': 'german',
        'unit': 1,
        'week': 2,
        'topic': 'Housing'
    }
    
    # Test with different entries
    test_entries = [
        ("German", german_entry),
        ("Spanish", spanish_entry), 
        ("French", french_entry)
    ]
    
    formatter = FormatterFactory.create_formatter('ankiapp')
    
    for lang_name, entry in test_entries:
        print(f"=== {lang_name} Entry ===")
        result = formatter.format_entry(entry, sample_metadata)
        print(f"Front: {result[0]}")
        print(f"Back: {result[1]}")
        print(f"Tags: {result[2]}")
        print()
    
    print("=== Card Preview ===")
    preview = preview_card_formatting(german_entry, 'ankiapp')
    print(preview)
    
    print("\n=== Available Formatters ===")
    print(FormatterFactory.get_available_formatters())
    
    print("\n=== Language Detection Test ===")
    mapper = _language_mapper
    for lang_name, entry in test_entries:
        detected = mapper.detect_language_fields(entry)
        print(f"{lang_name}: {detected}")
    
    print("\n=== Phrases Formatter Test ===")
    config = {
        'show_context_indicators': True,
        'phrase_category_prefix': '💬',
        'target_language': 'german',
        'native_language': 'english'
    }
    
    phrases_formatter = FormatterFactory.create_formatter('phrases', config)
    sample_data = create_phrases_sample_data()
    
    # Process first phrase
    phrase = sample_data['days']['day_1']['phrases'][0]
    metadata = {
        'week': sample_data['week'],
        'topic': sample_data['topic'],
        'section_topic': sample_data['days']['day_1']['topic'],
        'content_type': 'phrases'
    }
    
    phrase_result = phrases_formatter.format_entry(phrase, metadata)
    print(f"Phrase Front: {phrase_result[0]}")
    print(f"Phrase Back: {phrase_result[1]}")
    print(f"Phrase Tags: {phrase_result[2]}")