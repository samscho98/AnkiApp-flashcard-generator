"""
Template Manager for Enhanced Card Formatting
Handles HTML templates for different card types (vocabulary, grammar, verbs, etc.)
Integrates with the existing GenericLanguageCSVGenerator
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import re
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Simple Mustache-like template engine for card formatting"""
    
    def __init__(self):
        self.compiled_templates = {}
    
    def render(self, template: str, data: Dict[str, Any]) -> str:
        """
        Render template with data using Mustache-like syntax
        
        Args:
            template: Template string with {{variable}} and {{#section}} syntax
            data: Data dictionary for template variables
            
        Returns:
            Rendered template string
        """
        # Simple variable substitution {{variable}}
        result = template
        
        # Handle conditional sections {{#variable}}...{{/variable}}
        result = self._handle_sections(result, data)
        
        # Handle simple variable substitution
        result = self._handle_variables(result, data)
        
        # Clean up any remaining template syntax
        result = self._cleanup_template(result)
        
        return result
    
    def _handle_sections(self, template: str, data: Dict[str, Any]) -> str:
        """Handle conditional sections and loops"""
        # Pattern for {{#variable}}...{{/variable}}
        section_pattern = r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}'
        
        def replace_section(match):
            var_name = match.group(1)
            section_content = match.group(2)
            
            if var_name not in data:
                return ""
            
            value = data[var_name]
            
            # If value is falsy, don't render section
            if not value:
                return ""
            
            # If value is a list, render for each item
            if isinstance(value, list):
                results = []
                for item in value:
                    if isinstance(item, dict):
                        # Merge with parent data
                        item_data = {**data, **item}
                        results.append(self._handle_variables(section_content, item_data))
                    else:
                        # Simple value
                        item_data = {**data, var_name: item}
                        results.append(self._handle_variables(section_content, item_data))
                return "".join(results)
            
            # If value is truthy, render once
            return self._handle_variables(section_content, data)
        
        return re.sub(section_pattern, replace_section, template, flags=re.DOTALL)
    
    def _handle_variables(self, template: str, data: Dict[str, Any]) -> str:
        """Handle simple variable substitution"""
        # Pattern for {{variable}}
        var_pattern = r'\{\{(\w+)\}\}'
        
        def replace_variable(match):
            var_name = match.group(1)
            return str(data.get(var_name, ""))
        
        return re.sub(var_pattern, replace_variable, template)
    
    def _cleanup_template(self, template: str) -> str:
        """Clean up any remaining template syntax"""
        # Remove empty conditional sections
        template = re.sub(r'\{\{#\w+\}\}\s*\{\{/\w+\}\}', '', template)
        # Remove remaining template tags
        template = re.sub(r'\{\{[^}]+\}\}', '', template)
        return template


class TemplateManager:
    """Manages card templates for different content types"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize Template Manager
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.engine = TemplateEngine()
        self.templates = {}
        self.template_configs = {}
        
        # Create default templates if they don't exist
        self._create_default_templates()
        self._load_templates()
    
    def _create_default_templates(self):
        """Create default template files if they don't exist"""
        default_templates = {
            "vocabulary_card.html": self._get_default_vocabulary_template(),
            "grammar_card.html": self._get_default_grammar_template(),
            "verb_card.html": self._get_default_verb_template(),
            "phrase_card.html": self._get_default_phrase_template(),
            "listening_card.html": self._get_default_listening_template()
        }
        
        for filename, content in default_templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created default template: {filename}")
    
    def _load_templates(self):
        """Load all templates from the templates directory"""
        for template_file in self.templates_dir.glob("*.html"):
            template_name = template_file.stem
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.templates[template_name] = f.read()
                logger.info(f"Loaded template: {template_name}")
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")
        
        # Load template configurations
        config_file = self.templates_dir / "template_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.template_configs = json.load(f)
            except Exception as e:
                logger.error(f"Error loading template config: {e}")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get template by name"""
        return self.templates.get(template_name)
    
    def render_card(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render a card using specified template
        
        Args:
            template_name: Name of template to use
            data: Data for template rendering
            
        Returns:
            Rendered HTML string
        """
        template = self.get_template(template_name)
        if not template:
            logger.warning(f"Template not found: {template_name}")
            return self._render_fallback_card(data)
        
        try:
            return self.engine.render(template, data)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return self._render_fallback_card(data)
    
    def _render_fallback_card(self, data: Dict[str, Any]) -> str:
        """Render basic fallback card when template fails"""
        parts = []
        for key, value in data.items():
            if value and key not in ['type', 'template']:
                parts.append(f"<strong>{key.replace('_', ' ').title()}:</strong> {value}")
        return "<br>".join(parts)
    
    def get_template_for_content_type(self, content_type: str) -> str:
        """
        Get appropriate template name for content type
        
        Args:
            content_type: Type of content (vocabulary, grammar, verb, etc.)
            
        Returns:
            Template name
        """
        type_mapping = {
            'vocabulary': 'vocabulary_card',
            'vocab': 'vocabulary_card',
            'word': 'vocabulary_card',
            'grammar': 'grammar_card',
            'rule': 'grammar_card',
            'verb': 'verb_card',
            'conjugation': 'verb_card',
            'phrase': 'phrase_card',
            'expression': 'phrase_card',
            'listening': 'listening_card',
            'audio': 'listening_card'
        }
        
        return type_mapping.get(content_type.lower(), 'vocabulary_card')
    
    def _get_default_vocabulary_template(self) -> str:
        """Default vocabulary card template"""
        return '''<div class="vocab-card" style="font-family: Arial, sans-serif; padding: 10px; border-left: 4px solid #2196F3;">
    <div class="german-word" style="font-size: 18px; font-weight: bold; color: #1565C0; margin-bottom: 8px;">{{german}}</div>
    
    {{#dutch_connection}}
    <div class="dutch-hint" style="background: #E3F2FD; padding: 4px 8px; border-radius: 4px; margin-bottom: 8px; font-size: 14px;">
        🇳🇱 <strong>Dutch connection:</strong> <em>{{dutch_connection}}</em>
        {{#connection_type}}
        <span style="color: #666;">({{{connection_type}}})</span>
        {{/connection_type}}
    </div>
    {{/dutch_connection}}
    
    <div class="translation" style="font-size: 16px; margin-bottom: 10px;">
        <strong>{{english}}</strong>
    </div>
    
    {{#example}}
    <div class="example" style="background: #F5F5F5; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
        <strong>Example:</strong> {{example}}<br>
        {{#example_translation}}
        <em style="color: #666;">{{example_translation}}</em>
        {{/example_translation}}
    </div>
    {{/example}}
    
    {{#pronunciation_tip}}
    <div class="pronunciation" style="color: #4CAF50; font-size: 14px; margin-bottom: 6px;">
        🔊 <strong>Pronunciation:</strong> {{pronunciation_tip}}
    </div>
    {{/pronunciation_tip}}
    
    {{#memory_tip}}
    <div class="memory-tip" style="background: #FFF3E0; padding: 6px 8px; border-radius: 4px; font-size: 14px; color: #E65100;">
        💡 <strong>Memory tip:</strong> {{memory_tip}}
    </div>
    {{/memory_tip}}
</div>'''
    
    def _get_default_grammar_template(self) -> str:
        """Default grammar card template"""
        return '''<div class="grammar-card" style="font-family: Arial, sans-serif; padding: 10px; border-left: 4px solid #FF9800;">
    <div class="rule-title" style="font-size: 18px; font-weight: bold; color: #E65100; margin-bottom: 10px;">{{rule_name}}</div>
    
    <div class="explanation" style="font-size: 15px; margin-bottom: 12px; line-height: 1.4;">{{explanation}}</div>
    
    {{#examples}}
    <div class="grammar-examples" style="background: #FFF3E0; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
        <strong style="color: #E65100;">Examples:</strong><br>
        {{#example_list}}
        <div class="example-item" style="margin: 6px 0; padding-left: 10px;">
            <span style="color: #4CAF50;">✓</span> <strong>{{correct_example}}</strong>
            {{#translation}}
            <br><span style="margin-left: 15px; color: #666; font-style: italic;">{{translation}}</span>
            {{/translation}}
            {{#incorrect_example}}
            <br><span style="color: #F44336;">✗</span> <strike style="color: #999;">{{incorrect_example}}</strike>
            {{/incorrect_example}}
        </div>
        {{/example_list}}
    </div>
    {{/examples}}
    
    {{#dutch_comparison}}
    <div class="dutch-comparison" style="background: #E3F2FD; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
        🇳🇱 <strong>Dutch comparison:</strong> {{dutch_comparison}}
    </div>
    {{/dutch_comparison}}
    
    {{#memory_tip}}
    <div class="memory-tip" style="background: #E8F5E8; padding: 8px; border-radius: 4px; color: #2E7D32;">
        💡 <strong>Memory tip:</strong> {{memory_tip}}
    </div>
    {{/memory_tip}}
</div>'''
    
    def _get_default_verb_template(self) -> str:
        """Default verb conjugation template"""
        return '''<div class="verb-card" style="font-family: Arial, sans-serif; padding: 10px; border-left: 4px solid #9C27B0;">
    <div class="infinitive" style="font-size: 18px; font-weight: bold; color: #7B1FA2; margin-bottom: 6px;">{{infinitive}}</div>
    <div class="verb-meaning" style="font-size: 16px; margin-bottom: 10px;"><strong>{{meaning}}</strong></div>
    
    {{#dutch_cognate}}
    <div class="dutch-connection" style="background: #E3F2FD; padding: 4px 8px; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
        🇳🇱 <strong>Dutch:</strong> <em>{{dutch_cognate}}</em>
    </div>
    {{/dutch_cognate}}
    
    <table class="conjugation-table" style="width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 14px;">
        <tr><td style="padding: 4px 8px; font-weight: bold; width: 30%;">ich</td><td style="padding: 4px 8px; background: #F3E5F5;">{{ich_form}}</td></tr>
        <tr><td style="padding: 4px 8px; font-weight: bold;">du</td><td style="padding: 4px 8px;">{{du_form}}</td></tr>
        <tr><td style="padding: 4px 8px; font-weight: bold;">er/sie/es</td><td style="padding: 4px 8px; background: #F3E5F5;">{{er_sie_es_form}}</td></tr>
        <tr><td style="padding: 4px 8px; font-weight: bold;">wir</td><td style="padding: 4px 8px;">{{wir_form}}</td></tr>
        <tr><td style="padding: 4px 8px; font-weight: bold;">ihr</td><td style="padding: 4px 8px; background: #F3E5F5;">{{ihr_form}}</td></tr>
        <tr><td style="padding: 4px 8px; font-weight: bold;">sie/Sie</td><td style="padding: 4px 8px;">{{sie_form}}</td></tr>
    </table>
    
    {{#example_sentence}}
    <div class="verb-example" style="background: #F5F5F5; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
        <strong>Example:</strong> {{example_sentence}}<br>
        {{#example_translation}}
        <em style="color: #666;">{{example_translation}}</em>
        {{/example_translation}}
    </div>
    {{/example_sentence}}
    
    {{#irregular_note}}
    <div class="irregular-note" style="background: #FFEBEE; padding: 6px 8px; border-radius: 4px; color: #C62828; font-size: 14px;">
        ⚠️ <strong>Note:</strong> {{irregular_note}}
    </div>
    {{/irregular_note}}
</div>'''
    
    def _get_default_phrase_template(self) -> str:
        """Default phrase/expression template"""
        return '''<div class="phrase-card" style="font-family: Arial, sans-serif; padding: 10px; border-left: 4px solid #4CAF50;">
    <div class="phrase" style="font-size: 16px; font-weight: bold; color: #2E7D32; margin-bottom: 8px;">{{phrase}}</div>
    
    <div class="translation" style="font-size: 15px; margin-bottom: 10px;">
        <strong>{{translation}}</strong>
    </div>
    
    {{#context}}
    <div class="context" style="background: #E8F5E8; padding: 6px 8px; border-radius: 4px; margin-bottom: 8px; font-size: 14px;">
        <strong>When to use:</strong> {{context}}
    </div>
    {{/context}}
    
    {{#dialogue_example}}
    <div class="dialogue" style="background: #F5F5F5; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
        <strong>Dialogue:</strong><br>
        {{dialogue_example}}
    </div>
    {{/dialogue_example}}
    
    {{#formality}}
    <div class="formality" style="color: #666; font-size: 13px; margin-bottom: 6px;">
        <strong>Formality:</strong> {{formality}}
    </div>
    {{/formality}}
</div>'''
    
    def _get_default_listening_template(self) -> str:
        """Default listening comprehension template"""
        return '''<div class="listening-card" style="font-family: Arial, sans-serif; padding: 10px; border-left: 4px solid #FF5722;">
    <div class="instruction" style="font-size: 16px; font-weight: bold; color: #D84315; margin-bottom: 10px;">🎧 {{instruction}}</div>
    
    {{#audio_text}}
    <div class="audio-text" style="background: #FFF3E0; padding: 10px; border-radius: 4px; margin-bottom: 10px; font-style: italic;">
        "{{audio_text}}"
    </div>
    {{/audio_text}}
    
    {{#key_words}}
    <div class="key-words" style="margin-bottom: 10px;">
        <strong>Key words to listen for:</strong><br>
        {{#word_list}}
        <span style="background: #FFCCBC; padding: 2px 6px; border-radius: 3px; margin: 2px; display: inline-block;">{{.}}</span>
        {{/word_list}}
    </div>
    {{/key_words}}
    
    {{#pronunciation_focus}}
    <div class="pronunciation-focus" style="background: #E3F2FD; padding: 8px; border-radius: 4px; color: #1565C0;">
        🔊 <strong>Pronunciation focus:</strong> {{pronunciation_focus}}
    </div>
    {{/pronunciation_focus}}
</div>'''


class TemplateCardFormatter:
    """Enhanced card formatter that uses templates"""
    
    def __init__(self, template_manager: TemplateManager, config: Dict[str, Any] = None):
        """
        Initialize template-based formatter
        
        Args:
            template_manager: TemplateManager instance
            config: Configuration for formatter
        """
        self.template_manager = template_manager
        self.config = config or {}
        
        # Default field mappings
        self.field_mappings = self.config.get('field_mappings', {
            'german': 'german',
            'english': 'english', 
            'dutch_connection': 'dutch_connection',
            'example': 'example',
            'pronunciation': 'pronunciation_tip'
        })
    
    def format_entry(self, entry_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> str:
        """
        Format entry using appropriate template
        
        Args:
            entry_data: Entry data dictionary
            metadata: Additional metadata
            
        Returns:
            Formatted HTML card
        """
        metadata = metadata or {}
        
        # Determine content type and template
        content_type = entry_data.get('type', metadata.get('content_type', 'vocabulary'))
        template_name = self.template_manager.get_template_for_content_type(content_type)
        
        # Prepare template data
        template_data = self._prepare_template_data(entry_data, metadata)
        
        # Render card
        return self.template_manager.render_card(template_name, template_data)
    
    def _prepare_template_data(self, entry_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        # Start with entry data
        template_data = dict(entry_data)
        
        # Add metadata
        template_data.update(metadata)
        
        # Apply field mappings
        for source_field, template_field in self.field_mappings.items():
            if source_field in entry_data:
                template_data[template_field] = entry_data[source_field]
        
        # Add Dutch connection type if available
        if 'dutch_connection' in template_data and template_data['dutch_connection']:
            template_data['connection_type'] = self._determine_connection_type(
                template_data.get('german', ''),
                template_data['dutch_connection']
            )
        
        # Ensure boolean fields are properly set
        for field in template_data:
            if template_data[field] is None or template_data[field] == '':
                template_data[field] = False
        
        return template_data
    
    def _determine_connection_type(self, german_word: str, dutch_word: str) -> str:
        """Determine type of Dutch-German connection"""
        if not german_word or not dutch_word:
            return ""
        
        german_clean = german_word.lower().strip()
        dutch_clean = dutch_word.lower().strip()
        
        # Remove articles for comparison
        german_clean = re.sub(r'^(der|die|das)\s+', '', german_clean)
        dutch_clean = re.sub(r'^(de|het)\s+', '', dutch_clean)
        
        if german_clean == dutch_clean:
            return "identical"
        elif self._calculate_similarity(german_clean, dutch_clean) > 0.8:
            return "very similar"
        elif self._calculate_similarity(german_clean, dutch_clean) > 0.6:
            return "similar"
        else:
            return "related"
    
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words (simple Levenshtein-based)"""
        if not word1 or not word2:
            return 0.0
        
        # Simple similarity calculation
        if len(word1) < 3 or len(word2) < 3:
            return 1.0 if word1 == word2 else 0.0
        
        # Count common characters
        common = 0
        for char in set(word1):
            common += min(word1.count(char), word2.count(char))
        
        return common / max(len(word1), len(word2))


# Example usage and testing
if __name__ == "__main__":
    # Create template manager
    template_manager = TemplateManager("templates")
    
    # Create formatter
    formatter = TemplateCardFormatter(template_manager)
    
    # Test vocabulary card
    vocab_data = {
        "german": "das Haus",
        "english": "the house",
        "dutch_connection": "het huis",
        "example": "Das Haus ist groß.",
        "example_translation": "The house is big.",
        "pronunciation_tip": "'Haus' rhymes with English 'house'",
        "memory_tip": "Same as Dutch 'huis' but with different article"
    }
    
    vocab_card = formatter.format_entry(vocab_data)
    print("Vocabulary Card:")
    print(vocab_card)
    print("\n" + "="*50 + "\n")
    
    # Test grammar card
    grammar_data = {
        "type": "grammar",
        "rule_name": "German Articles (der, die, das)",
        "explanation": "German nouns have three genders: masculine (der), feminine (die), and neuter (das).",
        "examples": True,
        "example_list": [
            {
                "correct_example": "der Mann (the man)",
                "translation": "masculine noun",
                "incorrect_example": "die Mann"
            },
            {
                "correct_example": "die Frau (the woman)", 
                "translation": "feminine noun"
            }
        ],
        "dutch_comparison": "Dutch only has 'de' and 'het' - simpler than German!",
        "memory_tip": "Learn nouns with their articles from the beginning"
    }
    
    grammar_card = formatter.format_entry(grammar_data)
    print("Grammar Card:")
    print(grammar_card)
    print("\n" + "="*50 + "\n")
    
    # Test verb card
    verb_data = {
        "type": "verb",
        "infinitive": "sein",
        "meaning": "to be",
        "dutch_cognate": "zijn",
        "ich_form": "bin",
        "du_form": "bist", 
        "er_sie_es_form": "ist",
        "wir_form": "sind",
        "ihr_form": "seid",
        "sie_form": "sind",
        "example_sentence": "Ich bin Student.",
        "example_translation": "I am a student.",
        "irregular_note": "This is the most important irregular verb in German!"
    }
    
    verb_card = formatter.format_entry(verb_data)
    print("Verb Card:")
    print(verb_card)