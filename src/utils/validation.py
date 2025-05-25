"""
Data Validation Module
Validates learning content data structure and content quality
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]
    
    def add_error(self, message: str) -> None:
        """Add an error message"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        self.warnings.append(message)
    
    def add_info(self, message: str) -> None:
        """Add an info message"""
        self.info.append(message)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if not other.is_valid:
            self.is_valid = False


class DataValidator:
    """Validates learning content data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize validator
        
        Args:
            config: Validation configuration
        """
        self.config = config or {}
        
        # Default validation rules
        self.required_fields = self.config.get('required_fields', ['target', 'native'])
        self.optional_fields = self.config.get('optional_fields', ['example', 'pronunciation', 'notes'])
        self.field_patterns = self.config.get('field_patterns', {})
        self.max_field_length = self.config.get('max_field_length', {})
        self.min_entries_per_section = self.config.get('min_entries_per_section', 1)
        self.max_entries_per_section = self.config.get('max_entries_per_section', 100)
    
    def validate_entry(self, entry_data: Dict[str, Any], entry_id: str = "") -> ValidationResult:
        """
        Validate a single content entry
        
        Args:
            entry_data: Entry data dictionary
            entry_id: Entry identifier for error messages
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(True, [], [], [])
        entry_ref = f"Entry {entry_id}" if entry_id else "Entry"
        
        # Check required fields
        for field in self.required_fields:
            if field not in entry_data:
                result.add_error(f"{entry_ref}: Missing required field '{field}'")
            elif not entry_data[field] or str(entry_data[field]).strip() == "":
                result.add_error(f"{entry_ref}: Required field '{field}' is empty")
        
        # Check field patterns (regex validation)
        for field, pattern in self.field_patterns.items():
            if field in entry_data and entry_data[field]:
                if not re.match(pattern, str(entry_data[field])):
                    result.add_error(f"{entry_ref}: Field '{field}' doesn't match required pattern")
        
        # Check field lengths
        for field, max_length in self.max_field_length.items():
            if field in entry_data and entry_data[field]:
                if len(str(entry_data[field])) > max_length:
                    result.add_warning(f"{entry_ref}: Field '{field}' exceeds maximum length ({max_length})")
        
        # Check for suspicious content
        self._check_content_quality(entry_data, result, entry_ref)
        
        return result
    
    def _check_content_quality(self, entry_data: Dict[str, Any], result: ValidationResult, entry_ref: str) -> None:
        """Check content quality issues"""
        
        # Check for placeholder text
        placeholders = ['todo', 'tbd', 'placeholder', 'example', 'test', '...', 'xxx']
        for field, value in entry_data.items():
            if isinstance(value, str):
                value_lower = value.lower().strip()
                if value_lower in placeholders:
                    result.add_warning(f"{entry_ref}: Field '{field}' contains placeholder text: '{value}'")
        
        # Check for very short content
        for field in ['target', 'native', 'example']:
            if field in entry_data and entry_data[field]:
                if len(str(entry_data[field]).strip()) < 2:
                    result.add_warning(f"{entry_ref}: Field '{field}' is very short")
        
        # Check for duplicate target/native (same word in both)
        if 'target' in entry_data and 'native' in entry_data:
            target = str(entry_data['target']).strip().lower()
            native = str(entry_data['native']).strip().lower()
            if target == native:
                result.add_warning(f"{entry_ref}: Target and native fields are identical")
        
        # Check for missing examples on complex words
        if 'target' in entry_data and 'example' in entry_data:
            target = str(entry_data['target']).strip()
            if len(target) > 15 and not entry_data.get('example'):
                result.add_info(f"{entry_ref}: Long word/phrase might benefit from an example")
    
    def validate_section(self, section_data: Dict[str, Any], section_id: str = "") -> ValidationResult:
        """
        Validate a content section
        
        Args:
            section_data: Section data dictionary
            section_id: Section identifier
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(True, [], [], [])
        section_ref = f"Section {section_id}" if section_id else "Section"
        
        # Check section structure
        if 'entries' not in section_data and 'words' not in section_data and 'items' not in section_data:
            result.add_error(f"{section_ref}: No entries found (expected 'entries', 'words', or 'items')")
            return result
        
        # Get entries
        entries = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
        
        # Check entry count
        entry_count = len(entries)
        if entry_count < self.min_entries_per_section:
            result.add_warning(f"{section_ref}: Only {entry_count} entries (minimum recommended: {self.min_entries_per_section})")
        elif entry_count > self.max_entries_per_section:
            result.add_warning(f"{section_ref}: {entry_count} entries (maximum recommended: {self.max_entries_per_section})")
        
        # Validate each entry
        for i, entry_data in enumerate(entries):
            entry_result = self.validate_entry(entry_data, f"{section_id}.{i}" if section_id else str(i))
            result.merge(entry_result)
        
        # Check for duplicate entries
        self._check_section_duplicates(entries, result, section_ref)
        
        # Check section metadata
        if 'topic' not in section_data:
            result.add_info(f"{section_ref}: No topic specified")
        
        return result
    
    def _check_section_duplicates(self, entries: List[Dict[str, Any]], result: ValidationResult, section_ref: str) -> None:
        """Check for duplicate entries in a section"""
        seen_targets = {}
        seen_natives = {}
        
        for i, entry in enumerate(entries):
            # Check target duplicates
            if 'target' in entry and entry['target']:
                target = str(entry['target']).strip().lower()
                if target in seen_targets:
                    result.add_warning(f"{section_ref}: Duplicate target word '{entry['target']}' at positions {seen_targets[target]} and {i}")
                else:
                    seen_targets[target] = i
            
            # Check native duplicates (less critical)
            if 'native' in entry and entry['native']:
                native = str(entry['native']).strip().lower()
                if native in seen_natives:
                    result.add_info(f"{section_ref}: Duplicate native word '{entry['native']}' at positions {seen_natives[native]} and {i}")
                else:
                    seen_natives[native] = i
    
    def validate_unit(self, unit_data: Dict[str, Any], unit_id: str = "") -> ValidationResult:
        """
        Validate a content unit (week, chapter, etc.)
        
        Args:
            unit_data: Unit data dictionary
            unit_id: Unit identifier
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(True, [], [], [])
        unit_ref = f"Unit {unit_id}" if unit_id else "Unit"
        
        # Check unit metadata
        if 'title' not in unit_data and 'topic' not in unit_data:
            result.add_info(f"{unit_ref}: No title or topic specified")
        
        # Find sections
        sections_found = False
        for container_key in ['days', 'lessons', 'sections', 'chapters']:
            if container_key in unit_data:
                sections = unit_data[container_key]
                sections_found = True
                
                for section_id, section_data in sections.items():
                    section_result = self.validate_section(section_data, f"{unit_id}.{section_id}" if unit_id else section_id)
                    result.merge(section_result)
                break
        
        # Check for direct entries (no sections)
        if not sections_found:
            if any(key in unit_data for key in ['entries', 'words', 'items']):
                section_result = self.validate_section(unit_data, f"{unit_id}.main" if unit_id else "main")
                result.merge(section_result)
            else:
                result.add_error(f"{unit_ref}: No content sections or entries found")
        
        return result
    
    def validate_file_structure(self, data: Dict[str, Any], filename: str = "") -> ValidationResult:
        """
        Validate overall file structure
        
        Args:
            data: File data dictionary
            filename: Filename for reference
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(True, [], [], [])
        file_ref = f"File {filename}" if filename else "File"
        
        # Check basic structure
        if not isinstance(data, dict):
            result.add_error(f"{file_ref}: Root data must be a dictionary/object")
            return result
        
        # Check for content
        has_content = any(key in data for key in [
            'entries', 'words', 'items',  # Direct content
            'days', 'lessons', 'sections', 'chapters', 'units'  # Nested content
        ])
        
        if not has_content:
            result.add_error(f"{file_ref}: No recognizable content structure found")
            return result
        
        # Validate as unit
        unit_result = self.validate_unit(data, filename)
        result.merge(unit_result)
        
        return result
    
    def validate_dataset(self, dataset: Dict[str, Dict[str, Any]]) -> ValidationResult:
        """
        Validate an entire dataset (multiple files)
        
        Args:
            dataset: Dictionary of filename -> file_data
            
        Returns:
            ValidationResult
        """
        result = ValidationResult(True, [], [], [])
        
        if not dataset:
            result.add_error("Dataset is empty")
            return result
        
        # Validate each file
        for filename, file_data in dataset.items():
            file_result = self.validate_file_structure(file_data, filename)
            result.merge(file_result)
        
        # Cross-file validation
        self._validate_dataset_consistency(dataset, result)
        
        return result
    
    def _validate_dataset_consistency(self, dataset: Dict[str, Dict[str, Any]], result: ValidationResult) -> None:
        """Check consistency across multiple files"""
        
        # Check for consistent field names across files
        all_fields = set()
        file_fields = {}
        
        for filename, file_data in dataset.items():
            fields = self._extract_all_fields(file_data)
            file_fields[filename] = fields
            all_fields.update(fields)
        
        # Find common fields (present in most files)
        field_counts = {}
        for fields in file_fields.values():
            for field in fields:
                field_counts[field] = field_counts.get(field, 0) + 1
        
        total_files = len(dataset)
        common_fields = {field for field, count in field_counts.items() if count >= total_files * 0.8}
        
        # Check for missing common fields
        for filename, fields in file_fields.items():
            missing_common = common_fields - fields
            if missing_common:
                result.add_info(f"File {filename}: Missing common fields: {', '.join(missing_common)}")
        
        # Check for unusual fields (only in one file)
        for filename, fields in file_fields.items():
            unique_fields = {field for field in fields if field_counts[field] == 1}
            if unique_fields:
                result.add_info(f"File {filename}: Unique fields: {', '.join(unique_fields)}")
    
    def _extract_all_fields(self, file_data: Dict[str, Any]) -> set:
        """Extract all field names used in a file"""
        fields = set()
        
        def extract_from_entries(entries: List[Dict[str, Any]]) -> None:
            for entry in entries:
                if isinstance(entry, dict):
                    fields.update(entry.keys())
        
        # Direct entries
        if 'entries' in file_data:
            extract_from_entries(file_data['entries'])
        elif 'words' in file_data:
            extract_from_entries(file_data['words'])
        elif 'items' in file_data:
            extract_from_entries(file_data['items'])
        
        # Nested structure
        for container_key in ['days', 'lessons', 'sections', 'chapters', 'units']:
            if container_key in file_data:
                container = file_data[container_key]
                for section_data in container.values():
                    section_entries = section_data.get('entries', section_data.get('words', section_data.get('items', [])))
                    extract_from_entries(section_entries)
        
        return fields


class ContentQualityChecker:
    """Advanced content quality checking"""
    
    def __init__(self, language_config: Dict[str, Any] = None):
        """
        Initialize quality checker
        
        Args:
            language_config: Language-specific configuration
        """
        self.config = language_config or {}
        self.target_language = self.config.get('target_language', 'unknown')
        self.native_language = self.config.get('native_language', 'english')
    
    def check_language_consistency(self, entries: List[Dict[str, Any]]) -> ValidationResult:
        """Check for language consistency issues"""
        result = ValidationResult(True, [], [], [])
        
        # Check for mixed scripts/alphabets
        target_scripts = set()
        for entry in entries:
            if 'target' in entry and entry['target']:
                script = self._detect_script(str(entry['target']))
                target_scripts.add(script)
        
        if len(target_scripts) > 1:
            result.add_warning(f"Mixed scripts detected in target language: {', '.join(target_scripts)}")
        
        # Check for likely translation errors
        for i, entry in enumerate(entries):
            if 'target' in entry and 'native' in entry:
                if self._likely_translation_error(entry['target'], entry['native']):
                    result.add_warning(f"Entry {i}: Possible translation error - words seem unrelated")
        
        return result
    
    def _detect_script(self, text: str) -> str:
        """Detect writing script of text"""
        if not text:
            return 'empty'
        
        # Basic script detection
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return 'chinese'
        elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            return 'japanese'
        elif any('\uac00' <= char <= '\ud7af' for char in text):
            return 'korean'
        elif any('\u0400' <= char <= '\u04ff' for char in text):
            return 'cyrillic'
        elif any('\u0590' <= char <= '\u05ff' for char in text):
            return 'hebrew'
        elif any('\u0600' <= char <= '\u06ff' for char in text):
            return 'arabic'
        elif any(char.isalpha() and ord(char) > 127 for char in text):
            return 'extended_latin'
        else:
            return 'latin'
    
    def _likely_translation_error(self, target: str, native: str) -> bool:
        """Check if target and native words seem unrelated (basic heuristic)"""
        if not target or not native:
            return False
        
        target_clean = re.sub(r'[^a-zA-Z]', '', target.lower())
        native_clean = re.sub(r'[^a-zA-Z]', '', native.lower())
        
        # Very basic check - if they're too similar, might be wrong
        if len(target_clean) > 3 and len(native_clean) > 3:
            if target_clean == native_clean:
                return True
        
        return False
    
    def check_example_quality(self, entries: List[Dict[str, Any]]) -> ValidationResult:
        """Check quality of example sentences"""
        result = ValidationResult(True, [], [], [])
        
        for i, entry in enumerate(entries):
            if 'example' not in entry or not entry['example']:
                continue
            
            example = str(entry['example']).strip()
            target = str(entry.get('target', '')).strip()
            
            # Check if example contains the target word
            if target and target.lower() not in example.lower():
                result.add_warning(f"Entry {i}: Example doesn't contain the target word '{target}'")
            
            # Check example length
            if len(example) < 10:
                result.add_info(f"Entry {i}: Example sentence is very short")
            elif len(example) > 200:
                result.add_warning(f"Entry {i}: Example sentence is very long")
            
            # Check for incomplete sentences
            if not example.endswith(('.', '!', '?')):
                result.add_info(f"Entry {i}: Example might be incomplete (no ending punctuation)")
        
        return result


class ValidationRunner:
    """Runs comprehensive validation on datasets"""
    
    def __init__(self, validation_config: Dict[str, Any] = None):
        """
        Initialize validation runner
        
        Args:
            validation_config: Configuration for validation rules
        """
        self.config = validation_config or {}
        self.validator = DataValidator(self.config.get('basic_validation', {}))
        self.quality_checker = ContentQualityChecker(self.config.get('quality_checking', {}))
    
    def run_full_validation(self, data_source: Union[str, Dict[str, Any], Dict[str, Dict[str, Any]]]) -> ValidationResult:
        """
        Run comprehensive validation on data source
        
        Args:
            data_source: File path, single file data, or dataset
            
        Returns:
            Combined validation result
        """
        result = ValidationResult(True, [], [], [])
        
        # Determine data type and load if needed
        if isinstance(data_source, str):
            # File path
            try:
                import json
                with open(data_source, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                file_result = self.validator.validate_file_structure(file_data, data_source)
                result.merge(file_result)
            except Exception as e:
                result.add_error(f"Failed to load file {data_source}: {e}")
                return result
        
        elif isinstance(data_source, dict):
            # Check if it's a dataset (multiple files) or single file
            if all(isinstance(v, dict) for v in data_source.values()):
                # Assume it's a dataset
                dataset_result = self.validator.validate_dataset(data_source)
                result.merge(dataset_result)
            else:
                # Single file data
                file_result = self.validator.validate_file_structure(data_source)
                result.merge(file_result)
        
        return result
    
    def generate_validation_report(self, result: ValidationResult, output_format: str = "text") -> str:
        """
        Generate formatted validation report
        
        Args:
            result: Validation result
            output_format: "text", "html", or "markdown"
            
        Returns:
            Formatted report string
        """
        if output_format == "markdown":
            return self._generate_markdown_report(result)
        elif output_format == "html":
            return self._generate_html_report(result)
        else:
            return self._generate_text_report(result)
    
    def _generate_text_report(self, result: ValidationResult) -> str:
        """Generate plain text report"""
        lines = []
        lines.append("=" * 50)
        lines.append("DATA VALIDATION REPORT")
        lines.append("=" * 50)
        
        if result.is_valid:
            lines.append("✅ OVERALL STATUS: VALID")
        else:
            lines.append("❌ OVERALL STATUS: INVALID")
        
        lines.append("")
        
        if result.errors:
            lines.append(f"🚨 ERRORS ({len(result.errors)}):")
            for error in result.errors:
                lines.append(f"  • {error}")
            lines.append("")
        
        if result.warnings:
            lines.append(f"⚠️  WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings:
                lines.append(f"  • {warning}")
            lines.append("")
        
        if result.info:
            lines.append(f"ℹ️  INFO ({len(result.info)}):")
            for info in result.info:
                lines.append(f"  • {info}")
            lines.append("")
        
        lines.append("=" * 50)
        return "\n".join(lines)
    
    def _generate_markdown_report(self, result: ValidationResult) -> str:
        """Generate markdown report"""
        lines = []
        lines.append("# Data Validation Report")
        lines.append("")
        
        if result.is_valid:
            lines.append("## ✅ Overall Status: VALID")
        else:
            lines.append("## ❌ Overall Status: INVALID")
        
        lines.append("")
        
        if result.errors:
            lines.append(f"## 🚨 Errors ({len(result.errors)})")
            lines.append("")
            for error in result.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        if result.warnings:
            lines.append(f"## ⚠️ Warnings ({len(result.warnings)})")
            lines.append("")
            for warning in result.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        if result.info:
            lines.append(f"## ℹ️ Information ({len(result.info)})")
            lines.append("")
            for info in result.info:
                lines.append(f"- {info}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, result: ValidationResult) -> str:
        """Generate HTML report"""
        status_class = "valid" if result.is_valid else "invalid"
        status_text = "VALID" if result.is_valid else "INVALID"
        status_icon = "✅" if result.is_valid else "❌"
        
        html = f"""
        <html>
        <head>
            <title>Data Validation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .status.valid {{ color: green; }}
                .status.invalid {{ color: red; }}
                .section {{ margin: 20px 0; }}
                .errors {{ color: #d32f2f; }}
                .warnings {{ color: #f57c00; }}
                .info {{ color: #1976d2; }}
                ul {{ list-style-type: none; padding-left: 0; }}
                li {{ margin: 5px 0; padding: 5px; background: #f9f9f9; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Validation Report</h1>
                <h2 class="status {status_class}">{status_icon} Overall Status: {status_text}</h2>
            </div>
        """
        
        if result.errors:
            html += f"""
            <div class="section errors">
                <h3>🚨 Errors ({len(result.errors)})</h3>
                <ul>
            """
            for error in result.errors:
                html += f"<li>{error}</li>"
            html += "</ul></div>"
        
        if result.warnings:
            html += f"""
            <div class="section warnings">
                <h3>⚠️ Warnings ({len(result.warnings)})</h3>
                <ul>
            """
            for warning in result.warnings:
                html += f"<li>{warning}</li>"
            html += "</ul></div>"
        
        if result.info:
            html += f"""
            <div class="section info">
                <h3>ℹ️ Information ({len(result.info)})</h3>
                <ul>
            """
            for info in result.info:
                html += f"<li>{info}</li>"
            html += "</ul></div>"
        
        html += "</body></html>"
        return html


# Example usage
if __name__ == "__main__":
    # Create validation runner with custom config
    validation_config = {
        'basic_validation': {
            'required_fields': ['german', 'english'],
            'optional_fields': ['example', 'dutch_connection', 'pronunciation'],
            'min_entries_per_section': 5,
            'max_entries_per_section': 25,
            'max_field_length': {
                'german': 100,
                'english': 100,
                'example': 200
            }
        },
        'quality_checking': {
            'target_language': 'german',
            'native_language': 'english'
        }
    }
    
    runner = ValidationRunner(validation_config)
    
    # Validate a single file
    result = runner.run_full_validation("data/vocabulary/week1.json")
    
    # Generate reports
    text_report = runner.generate_validation_report(result, "text")
    markdown_report = runner.generate_validation_report(result, "markdown")
    html_report = runner.generate_validation_report(result, "html")
    
    print(text_report)
    
    # Save reports
    with open("validation_report.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)
    
    with open("validation_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)