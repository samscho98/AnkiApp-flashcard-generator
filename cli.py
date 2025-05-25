#!/usr/bin/env python3
"""
Language Learning Flashcard Generator - Command Line Interface
Generic CLI for generating AnkiApp flashcards from JSON vocabulary data

Usage:
    python cli.py --file data/vocabulary/German/week1.json    # Generate from specific file
    python cli.py --batch --input-dir data/vocabulary/       # Batch process directory
    python cli.py --validate --input data/vocabulary/        # Validate data files
    python cli.py --preview --file week1.json                # Preview card format
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import from our actual project modules
try:
    from src.core.csv_generator import GenericLanguageCSVGenerator
    from src.core.history_manager import HistoryManager
    from src.config.settings import SettingsManager
    from src.utils.validation import ValidationRunner
    from src.utils.file_utils import JSONFileManager, DirectoryScanner
    from __version__ import __version__, APP_NAME, print_version
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you're running from the project root directory and src/ exists")
    print("Expected project structure:")
    print("  cli.py")
    print("  src/")
    print("    core/")
    print("    utils/")
    print("    config/")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def setup_directories():
    """Ensure required directories exist"""
    directories = [
        'data',
        'data/vocabulary', 
        'data/grammar',
        'output', 
        'logs',
        'backups'
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info("✓ Directories setup complete")


def scan_available_data():
    """Scan for available data files"""
    scanner = DirectoryScanner("data")
    content_files = scanner.scan_for_content({
        'vocabulary': ['*.json'],
        'grammar': ['*.json'],
        'phrases': ['*.json']
    })
    
    return content_files


def generate_from_file(file_path: str, output_dir: str = "output", format_type: str = "ankiapp"):
    """Generate flashcards from a specific JSON file"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        # Initialize generator
        settings_manager = SettingsManager()
        generator = GenericLanguageCSVGenerator(
            output_dir=output_dir,
            config={
                'export_format': format_type,
                'include_html_formatting': True,
                'show_connections': True
            }
        )
        
        # Generate CSV
        print(f"📚 Processing: {file_path.name}")
        csv_path = generator.generate_from_json_file(str(file_path), format_type)
        
        if csv_path:
            print(f"✅ Generated: {csv_path}")
            
            # Show statistics
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                card_count = len(lines) - 1 if lines else 0  # Subtract header
            
            print(f"📊 Cards generated: {card_count}")
            
            # Update history
            history_manager = HistoryManager()
            history_manager.add_generated_file(
                csv_path, 
                str(file_path),
                "vocabulary",  # Default content type
                card_count
            )
            
            return csv_path
        else:
            print("❌ Failed to generate CSV")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        logger.error(f"Error in generate_from_file: {e}", exc_info=True)
        return None


def batch_process_directory(input_dir: str, output_dir: str = "output", format_type: str = "ankiapp"):
    """Batch process all JSON files in a directory"""
    try:
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Directory not found: {input_dir}")
            return []
        
        # Find all JSON files
        json_files = list(input_path.rglob("*.json"))
        
        if not json_files:
            print(f"❌ No JSON files found in: {input_dir}")
            return []
        
        print(f"📁 Found {len(json_files)} JSON files")
        print(f"🔄 Processing batch...")
        
        generated_files = []
        success_count = 0
        
        for json_file in json_files:
            print(f"\n📄 Processing: {json_file.relative_to(input_path)}")
            csv_path = generate_from_file(str(json_file), output_dir, format_type)
            
            if csv_path:
                generated_files.append(csv_path)
                success_count += 1
            else:
                print(f"⚠️  Skipped: {json_file.name}")
        
        print(f"\n✅ Batch complete: {success_count}/{len(json_files)} files processed")
        return generated_files
        
    except Exception as e:
        print(f"❌ Error in batch processing: {e}")
        logger.error(f"Error in batch_process_directory: {e}", exc_info=True)
        return []


def validate_data_files(input_path: str):
    """Validate JSON data files"""
    try:
        path = Path(input_path)
        if not path.exists():
            print(f"❌ Path not found: {input_path}")
            return
        
        print(f"🔍 Validating data files in: {input_path}")
        
        # Initialize validator
        validator = ValidationRunner({
            'basic_validation': {
                'required_fields': ['target', 'native'],
                'min_entries_per_section': 1,
                'max_entries_per_section': 100
            }
        })
        
        if path.is_file():
            # Single file validation
            result = validator.run_full_validation(str(path))
            report = validator.generate_validation_report(result, "text")
            print(report)
        else:
            # Directory validation
            json_files = list(path.rglob("*.json"))
            
            if not json_files:
                print("❌ No JSON files found")
                return
            
            total_errors = 0
            total_warnings = 0
            
            for json_file in json_files:
                print(f"\n📄 Validating: {json_file.relative_to(path)}")
                result = validator.run_full_validation(str(json_file))
                
                if result.errors:
                    total_errors += len(result.errors)
                    print(f"  ❌ {len(result.errors)} errors")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"    • {error}")
                    if len(result.errors) > 3:
                        print(f"    ... and {len(result.errors) - 3} more")
                
                if result.warnings:
                    total_warnings += len(result.warnings)
                    print(f"  ⚠️  {len(result.warnings)} warnings")
                
                if not result.errors and not result.warnings:
                    print("  ✅ Valid")
            
            print(f"\n📊 Validation Summary:")
            print(f"  Files checked: {len(json_files)}")
            print(f"  Total errors: {total_errors}")
            print(f"  Total warnings: {total_warnings}")
            
            if total_errors == 0:
                print("✅ All files are valid!")
            else:
                print("❌ Some files have validation errors")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        logger.error(f"Error in validate_data_files: {e}", exc_info=True)


def preview_card_format(file_path: str = None):
    """Show preview of card formatting"""
    print("🎴 Card Format Preview")
    print("=" * 50)
    
    try:
        # Initialize components
        settings_manager = SettingsManager()
        generator = GenericLanguageCSVGenerator("output")
        
        # Sample data for preview
        sample_entries = [
            {
                "target": "das Haus",
                "native": "the house",
                "example": "Das Haus ist groß und schön.",
                "example_translation": "The house is big and beautiful.",
                "pronunciation": "dahs hows",
                "connections": {
                    "dutch": "het huis",
                    "spanish": "la casa"
                },
                "notes": "Neuter noun, plural: die Häuser"
            },
            {
                "target": "gehen",
                "native": "to go",
                "example": "Ich gehe nach Hause.",
                "example_translation": "I go home.",
                "pronunciation": "GAY-en",
                "connections": {
                    "dutch": "gaan"
                }
            }
        ]
        
        # If file specified, load real data
        if file_path and Path(file_path).exists():
            json_manager = JSONFileManager()
            data = json_manager.load_json(file_path)
            if data:
                # Extract first few entries from the file
                entries = []
                if 'entries' in data:
                    entries = data['entries'][:2]
                elif 'words' in data:
                    entries = data['words'][:2]
                elif 'days' in data:
                    for day_data in data['days'].values():
                        if 'words' in day_data:
                            entries.extend(day_data['words'][:2])
                            break
                
                if entries:
                    sample_entries = entries
                    print(f"📖 Preview from: {Path(file_path).name}")
        
        print("\n📚 VOCABULARY CARDS:")
        for i, entry in enumerate(sample_entries[:2], 1):
            print(f"\n--- Card {i} ---")
            print(f"Front: {entry.get('target', 'N/A')}")
            print(f"Back: {entry.get('native', 'N/A')}")
            
            if entry.get('example'):
                print(f"Example: {entry['example']}")
            
            if entry.get('connections'):
                connections = entry['connections']
                conn_str = " | ".join(f"{lang}: {word}" for lang, word in connections.items())
                print(f"Connections: {conn_str}")
            
            if entry.get('pronunciation'):
                print(f"Pronunciation: {entry['pronunciation']}")
        
        print(f"\n✨ Available formats: AnkiApp, Anki, Quizlet, Generic")
        print(f"🎨 HTML formatting: Bold, italic, line breaks supported")
        
    except Exception as e:
        print(f"❌ Error generating preview: {e}")
        logger.error(f"Error in preview_card_format: {e}", exc_info=True)


def show_available_data():
    """Show available data files"""
    print("📚 Available Data Files")
    print("=" * 40)
    
    try:
        content_files = scan_available_data()
        
        if not any(content_files.values()):
            print("❌ No data files found")
            print("💡 Create JSON files in data/vocabulary/ or data/grammar/")
            return
        
        for content_type, files in content_files.items():
            if files:
                print(f"\n📖 {content_type.title()}:")
                for file_path in sorted(files):
                    rel_path = Path(file_path).relative_to(Path.cwd())
                    print(f"  • {rel_path}")
        
        print(f"\n💡 Use --file to process a specific file")
        print(f"💡 Use --batch to process all files in a directory")
        
    except Exception as e:
        print(f"❌ Error scanning data: {e}")


def show_progress():
    """Show learning progress and statistics"""
    try:
        history_manager = HistoryManager()
        
        print("📊 Learning Progress")
        print("=" * 40)
        
        summary = history_manager.get_progress_summary()
        today_progress = history_manager.get_today_progress()
        
        print(f"📚 Total items learned: {summary.get('total_items_learned', 0)}")
        print(f"⏱️  Total study time: {summary.get('total_study_time_hours', 0):.1f} hours")
        print(f"📈 Study streak: {summary.get('study_streak', 0)} days")
        print(f"📄 Generated files: {summary.get('generated_files_count', 0)}")
        
        # Today's progress
        if today_progress.get('items_learned', 0) > 0:
            print(f"\n🎯 Today's Progress:")
            print(f"  Items learned: {today_progress['items_learned']}")
            print(f"  Target: {today_progress['daily_target']}")
            print(f"  Progress: {today_progress['target_progress']:.1f}%")
        
        # Recent sessions
        recent_sessions = history_manager.get_recent_sessions(5)
        if recent_sessions:
            print(f"\n📋 Recent Sessions:")
            for session in recent_sessions[:3]:
                if session.get('status') == 'completed':
                    date = session.get('start_time', '').split('T')[0]
                    items = session.get('items_learned', 0)
                    lang = session.get('target_language', 'Unknown')
                    print(f"  • {date}: {items} items ({lang})")
        
    except Exception as e:
        print(f"❌ Error showing progress: {e}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                                    # Show available data files
  %(prog)s --file data/vocabulary/week1.json        # Generate from specific file
  %(prog)s --batch --input-dir data/vocabulary/     # Process all files in directory
  %(prog)s --validate --input data/vocabulary/      # Validate data files
  %(prog)s --preview --file week1.json              # Preview card format
  %(prog)s --progress                                # Show learning statistics
        """
    )
    
    # File operations
    parser.add_argument('--file', type=str,
                       help='Generate flashcards from specific JSON file')
    parser.add_argument('--batch', action='store_true',
                       help='Batch process multiple files')
    parser.add_argument('--input-dir', type=str, default='data',
                       help='Input directory for batch processing (default: data)')
    
    # Validation and preview
    parser.add_argument('--validate', action='store_true',
                       help='Validate JSON data files')
    parser.add_argument('--input', type=str,
                       help='Input file or directory for validation')
    parser.add_argument('--preview', action='store_true',
                       help='Preview card formatting')
    
    # Output configuration
    parser.add_argument('--output', type=str, default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--format', type=str, 
                       choices=['ankiapp', 'anki', 'quizlet', 'generic'],
                       default='ankiapp',
                       help='Output format (default: ankiapp)')
    
    # Information commands
    parser.add_argument('--list', action='store_true',
                       help='List available data files')
    parser.add_argument('--progress', action='store_true',
                       help='Show learning progress and statistics')
    parser.add_argument('--setup', action='store_true',
                       help='Setup directories')
    parser.add_argument('--version', action='store_true',
                       help='Show version information')
    
    args = parser.parse_args()
    
    # Handle version
    if args.version:
        print_version()
        return
    
    # Handle setup
    if args.setup:
        setup_directories()
        print("✅ Setup complete! You can now add JSON files to data/ directories.")
        return
    
    # Handle list
    if args.list:
        show_available_data()
        return
    
    # Handle progress
    if args.progress:
        show_progress()
        return
    
    # Handle validation
    if args.validate:
        input_path = args.input or args.input_dir
        if not input_path:
            print("❌ Please specify --input for validation")
            return
        validate_data_files(input_path)
        return
    
    # Handle preview
    if args.preview:
        preview_card_format(args.file)
        return
    
    # Handle file processing
    if args.file:
        if args.batch:
            print("❌ Cannot use --file and --batch together")
            return
        generate_from_file(args.file, args.output, args.format)
        return
    
    # Handle batch processing
    if args.batch:
        batch_process_directory(args.input_dir, args.output, args.format)
        return
    
    # No arguments provided, show help and available data
    print(f"🎓 {APP_NAME} v{__version__}")
    print("=" * 50)
    show_available_data()
    print("\n" + "=" * 50)
    print("💡 QUICK START:")
    print("  python cli.py --list                    # Show available files")
    print("  python cli.py --file your_file.json    # Generate flashcards")
    print("  python cli.py --help                   # Full help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"CLI error: {e}", exc_info=True)
        sys.exit(1)