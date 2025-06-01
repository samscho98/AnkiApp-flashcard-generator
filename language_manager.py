#!/usr/bin/env python3
"""
Language Manager Utility
Helps manage the languages configuration file for the flashcard generator
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set


class LanguageManager:
    """Manages language configuration for the flashcard generator"""
    
    def __init__(self, languages_file: str = "languages.txt"):
        """Initialize language manager"""
        self.languages_file = Path(languages_file)
        self.languages = self._load_languages()
    
    def _load_languages(self) -> Dict[str, List[str]]:
        """Load languages from file"""
        languages = {}
        
        if self.languages_file.exists():
            with open(self.languages_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            lang_code, field_names = line.split(':', 1)
                            fields = [name.strip() for name in field_names.split(',')]
                            languages[lang_code.strip().lower()] = fields
        
        return languages
    
    def _save_languages(self) -> None:
        """Save languages to file"""
        with open(self.languages_file, 'w', encoding='utf-8') as f:
            f.write("# Language Configuration for Flashcard Generator\n")
            f.write("# Format: language_code:field_name_in_json\n")
            f.write("# Add new languages as needed\n\n")
            f.write("# Main supported languages\n")
            
            for lang_code, field_names in sorted(self.languages.items()):
                field_str = ','.join(field_names)
                f.write(f"{lang_code}:{field_str}\n")
            
            f.write("\n# You can add more languages here following the same pattern\n")
            f.write("# The first field name listed will be the primary one to look for\n")
    
    def add_language(self, language_code: str, field_names: List[str]) -> None:
        """Add a new language"""
        self.languages[language_code.lower()] = field_names
        print(f"Added language: {language_code} -> {field_names}")
    
    def update_language(self, language_code: str, field_names: List[str]) -> None:
        """Update existing language"""
        lang_key = language_code.lower()
        if lang_key in self.languages:
            self.languages[lang_key] = field_names
            print(f"Updated language: {language_code} -> {field_names}")
        else:
            print(f"Language {language_code} not found. Use add_language to create it.")
    
    def remove_language(self, language_code: str) -> None:
        """Remove a language"""
        lang_key = language_code.lower()
        if lang_key in self.languages:
            del self.languages[lang_key]
            print(f"Removed language: {language_code}")
        else:
            print(f"Language {language_code} not found.")
    
    def list_languages(self) -> None:
        """List all configured languages"""
        if not self.languages:
            print("No languages configured.")
            return
        
        print("Configured languages:")
        print("-" * 50)
        for lang_code, field_names in sorted(self.languages.items()):
            print(f"{lang_code:12} -> {', '.join(field_names)}")
    
    def detect_fields_in_json(self, json_file: str) -> Set[str]:
        """Detect field names in a JSON file"""
        import json
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fields = set()
            self._extract_fields_recursive(data, fields)
            return fields
            
        except Exception as e:
            print(f"Error reading JSON file {json_file}: {e}")
            return set()
    
    def _extract_fields_recursive(self, data, fields: Set[str]) -> None:
        """Recursively extract field names from nested data"""
        if isinstance(data, dict):
            fields.update(data.keys())
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self._extract_fields_recursive(value, fields)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_fields_recursive(item, fields)
    
    def suggest_mappings_from_json(self, json_file: str) -> None:
        """Suggest language mappings based on JSON file content"""
        fields = self.detect_fields_in_json(json_file)
        
        if not fields:
            print("No fields found in JSON file.")
            return
        
        print(f"Fields found in {json_file}:")
        for field in sorted(fields):
            print(f"  - {field}")
        
        print("\nSuggested language mappings:")
        
        # Try to detect language fields
        language_fields = {}
        
        for field in fields:
            field_lower = field.lower()
            
            # Common language patterns
            if field_lower in ['german', 'deutsch']:
                language_fields['german'] = field
            elif field_lower in ['english', 'en']:
                language_fields['english'] = field
            elif field_lower in ['dutch', 'nederlands']:
                language_fields['dutch'] = field
            elif field_lower in ['spanish', 'español', 'espanol']:
                language_fields['spanish'] = field
            elif field_lower in ['french', 'français', 'francais']:
                language_fields['french'] = field
            elif field_lower in ['italian', 'italiano']:
                language_fields['italian'] = field
            elif field_lower in ['portuguese', 'português', 'portugues']:
                language_fields['portuguese'] = field
            elif field_lower in ['tagalog']:
                language_fields['tagalog'] = field
        
        if language_fields:
            for lang, field in language_fields.items():
                existing_fields = self.languages.get(lang, [])
                if field not in existing_fields:
                    suggested_fields = [field] + existing_fields
                    print(f"  {lang}: {','.join(suggested_fields)}")
                else:
                    print(f"  {lang}: already configured with {field}")
        else:
            print("  No obvious language fields detected.")
            print("  Consider manually adding fields like:")
            for field in sorted(fields):
                if any(term in field.lower() for term in ['target', 'native', 'word', 'translation']):
                    print(f"    - {field}")
    
    def save(self) -> None:
        """Save current configuration"""
        self._save_languages()
        print(f"Configuration saved to {self.languages_file}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Manage language configuration for flashcard generator")
    parser.add_argument("--file", "-f", default="languages.txt", 
                       help="Languages configuration file (default: languages.txt)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all configured languages")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new language")
    add_parser.add_argument("language", help="Language code (e.g., 'german')")
    add_parser.add_argument("fields", nargs="+", help="Field names (e.g., 'German' 'german' 'target')")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update existing language")
    update_parser.add_argument("language", help="Language code")
    update_parser.add_argument("fields", nargs="+", help="Field names")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a language")
    remove_parser.add_argument("language", help="Language code")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze JSON file for field names")
    analyze_parser.add_argument("json_file", help="JSON file to analyze")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = LanguageManager(args.file)
    
    if args.command == "list":
        manager.list_languages()
    
    elif args.command == "add":
        manager.add_language(args.language, args.fields)
        manager.save()
    
    elif args.command == "update":
        manager.update_language(args.language, args.fields)
        manager.save()
    
    elif args.command == "remove":
        manager.remove_language(args.language)
        manager.save()
    
    elif args.command == "analyze":
        manager.suggest_mappings_from_json(args.json_file)


if __name__ == "__main__":
    main()