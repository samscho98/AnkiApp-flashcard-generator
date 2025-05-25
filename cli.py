#!/usr/bin/env python3
"""
Daily Card Generator for Goethe A1 Preparation
Command-line interface for generating AnkiApp flashcards

Usage:
    python daily_cards.py --week 1 --day 1          # Generate today's cards
    python daily_cards.py --week 2 --full           # Generate full week
    python daily_cards.py --schedule                 # Create study schedule
    python daily_cards.py --preview                  # Preview card format
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Import our enhanced generator (assuming it's in the same directory)
try:
    from csv_generator import EnhancedCSVGenerator, generate_todays_cards, generate_week_cards
    from template_manager import TemplateManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure template_manager.py and enhanced_csv_generator.py are in the same directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def setup_directories():
    """Ensure required directories exist"""
    directories = ['templates', 'output', 'data/vocabulary']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info("✓ Directories setup complete")


def calculate_study_progress(target_date: str = "2025-08-04") -> dict:
    """Calculate study progress and recommendations"""
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_remaining = (target - today).days
        
        # Study schedule: 33 study days total (5.5 weeks)
        total_study_days = 33
        total_words = 650
        
        return {
            'target_date': target_date,
            'days_remaining': days_remaining,
            'total_study_days': total_study_days,
            'total_words': total_words,
            'words_per_day_average': total_words / total_study_days,
            'weeks_remaining': days_remaining / 7,
            'status': 'on_track' if days_remaining >= total_study_days else 'intensive_needed'
        }
    except ValueError:
        return {'error': 'Invalid date format. Use YYYY-MM-DD'}


def generate_daily_cards(week: int, day: int, output_dir: str = "output"):
    """Generate daily flashcards"""
    try:
        generator = EnhancedCSVGenerator(output_dir, "templates")
        csv_path = generator.generate_daily_cards(week, day)
        
        if csv_path:
            print(f"✅ Generated daily cards: {csv_path}")
            
            # Show card count and study info
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                card_count = len(lines) - 1  # Subtract header
            
            expected_words = 10 if week == 1 else 20
            print(f"📊 Cards generated: {card_count} (expected: {expected_words})")
            print(f"📚 Study focus: Week {week}, Day {day}")
            
            if week == 1:
                print("🎯 Week 1 Focus: Essential grammar and high-frequency words")
            else:
                week_topics = {
                    2: "Time & Daily Activities",
                    3: "Living & Housing (Wohnen)",
                    4: "Food & Shopping (Essen/Trinken & Einkaufen)",
                    5: "Health & Services (Körper/Gesundheit & Dienstleistungen)",
                    6: "Person & Communication"
                }
                print(f"🎯 Week {week} Focus: {week_topics.get(week, 'General vocabulary')}")
            
            return csv_path
        else:
            print("❌ Failed to generate daily cards")
            return None
            
    except Exception as e:
        print(f"❌ Error generating daily cards: {e}")
        return None


def generate_weekly_cards(week: int, output_dir: str = "output"):
    """Generate full week flashcards"""
    try:
        generator = EnhancedCSVGenerator(output_dir, "templates")
        csv_path = generator.generate_weekly_cards(week)
        
        if csv_path:
            print(f"✅ Generated weekly cards: {csv_path}")
            
            # Show card count
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                card_count = len(lines) - 1
            
            expected_words = 50 if week == 1 else 120
            print(f"📊 Cards generated: {card_count} (expected: {expected_words})")
            print(f"📚 Full week {week} vocabulary")
            
            return csv_path
        else:
            print("❌ Failed to generate weekly cards")
            return None
            
    except Exception as e:
        print(f"❌ Error generating weekly cards: {e}")
        return None


def create_study_schedule(output_dir: str = "output"):
    """Create complete study schedule"""
    try:
        generator = EnhancedCSVGenerator(output_dir, "templates")
        schedule_path = generator.create_study_schedule_csv()
        
        if schedule_path:
            print(f"✅ Generated study schedule: {schedule_path}")
            print("📅 Complete 6-week Goethe A1 preparation plan")
            print("📋 Import this into Excel/Google Sheets to track progress")
            return schedule_path
        else:
            print("❌ Failed to generate study schedule")
            return None
            
    except Exception as e:
        print(f"❌ Error creating study schedule: {e}")
        return None


def preview_card_formats():
    """Show preview of different card formats"""
    print("🎴 Card Format Preview")
    print("=" * 50)
    
    try:
        generator = EnhancedCSVGenerator("output", "templates")
        
        # Sample vocabulary entry
        vocab_sample = {
            "german": "das Haus",
            "english": "the house",
            "dutch_connection": "het huis",
            "example": "Das Haus ist groß und schön.",
            "example_translation": "The house is big and beautiful.",
            "pronunciation_tip": "Rhymes with English 'house'",
            "memory_tip": "Same word as Dutch 'huis' but with German article 'das'"
        }
        
        print("📖 VOCABULARY CARD PREVIEW:")
        vocab_preview = generator.preview_card(vocab_sample, "vocabulary_card")
        # Remove HTML tags for clean console output
        import re
        clean_preview = re.sub('<[^<]+?>', '', vocab_preview)
        clean_preview = clean_preview.replace('&nbsp;', ' ').strip()
        print(clean_preview[:300] + "..." if len(clean_preview) > 300 else clean_preview)
        
        print("\n" + "=" * 50)
        
        # Sample grammar entry
        grammar_sample = {
            "type": "grammar",
            "rule_name": "German Articles: der, die, das",
            "explanation": "German nouns have grammatical gender: masculine (der), feminine (die), neuter (das).",
            "examples": True,
            "example_list": [
                {
                    "correct_example": "der Mann (the man)",
                    "translation": "masculine noun"
                },
                {
                    "correct_example": "die Frau (the woman)",
                    "translation": "feminine noun"
                }
            ],
            "dutch_comparison": "Dutch only has 'de' and 'het' - much simpler!",
            "memory_tip": "Learn every noun with its article from day one"
        }
        
        print("📚 GRAMMAR CARD PREVIEW:")
        grammar_preview = generator.preview_card(grammar_sample, "grammar_card")
        clean_grammar = re.sub('<[^<]+?>', '', grammar_preview)
        clean_grammar = clean_grammar.replace('&nbsp;', ' ').strip()
        print(clean_grammar[:300] + "..." if len(clean_grammar) > 300 else clean_grammar)
        
        print("\n✨ Available templates:", generator.get_available_templates())
        
    except Exception as e:
        print(f"❌ Error generating preview: {e}")


def show_study_progress(target_date: str = "2025-08-04"):
    """Show study progress and timeline"""
    progress = calculate_study_progress(target_date)
    
    if 'error' in progress:
        print(f"❌ {progress['error']}")
        return
    
    print("📊 GOETHE A1 STUDY PROGRESS")
    print("=" * 40)
    print(f"🎯 Target exam date: {progress['target_date']}")
    print(f"⏰ Days remaining: {progress['days_remaining']}")
    print(f"📚 Total words to learn: {progress['total_words']}")
    print(f"📈 Average words per day: {progress['words_per_day_average']:.1f}")
    print(f"🗓️  Study weeks remaining: {progress['weeks_remaining']:.1f}")
    
    if progress['status'] == 'intensive_needed':
        print("⚠️  STATUS: INTENSIVE STUDY NEEDED")
        print("💪 Recommendation: Study 25-30 words per day")
    else:
        print("✅ STATUS: ON TRACK")
        print("😊 Recommendation: Follow the standard 10-20 words per day plan")
    
    print("\n📅 RECOMMENDED WEEKLY SCHEDULE:")
    print("Week 1: Essential Grammar (10 words/day × 5 days)")
    print("Week 2: Time & Activities (20 words/day × 6 days)")
    print("Week 3: Living & Housing (20 words/day × 6 days)")
    print("Week 4: Food & Shopping (20 words/day × 6 days)")
    print("Week 5: Health & Services (20 words/day × 6 days)")
    print("Week 6: Person & Communication (20 words/day × 6 days)")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate AnkiApp flashcards for Goethe A1 preparation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --week 1 --day 1           Generate today's cards (Week 1, Day 1)
  %(prog)s --week 2 --full            Generate all cards for Week 2
  %(prog)s --schedule                 Create complete study schedule
  %(prog)s --preview                  Preview card formats
  %(prog)s --progress                 Show study progress
  %(prog)s --setup                    Setup directories and templates
        """
    )
    
    parser.add_argument('--week', type=int, choices=range(1, 7),
                       help='Week number (1-6)')
    parser.add_argument('--day', type=int, choices=range(1, 7),
                       help='Day number (1-6, or 1-5 for week 1)')
    parser.add_argument('--full', action='store_true',
                       help='Generate full week instead of single day')
    parser.add_argument('--schedule', action='store_true',
                       help='Create complete study schedule')
    parser.add_argument('--preview', action='store_true',
                       help='Preview card formats')
    parser.add_argument('--progress', action='store_true',
                       help='Show study progress')
    parser.add_argument('--setup', action='store_true',
                       help='Setup directories and create default templates')
    parser.add_argument('--output', default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--target-date', default='2025-08-04',
                       help='Target exam date (YYYY-MM-DD, default: 2025-08-04)')
    
    args = parser.parse_args()
    
    # Handle setup
    if args.setup:
        setup_directories()
        print("✅ Setup complete! You can now generate flashcards.")
        return
    
    # Handle preview
    if args.preview:
        preview_card_formats()
        return
    
    # Handle progress
    if args.progress:
        show_study_progress(args.target_date)
        return
    
    # Handle schedule creation
    if args.schedule:
        create_study_schedule(args.output)
        return
    
    # Handle card generation
    if args.week:
        if args.full:
            # Generate full week
            generate_weekly_cards(args.week, args.output)
        elif args.day:
            # Generate specific day
            # Validate day range for week 1
            if args.week == 1 and args.day > 5:
                print("❌ Week 1 only has 5 days (Day 1-5)")
                return
            generate_daily_cards(args.week, args.day, args.output)
        else:
            print("❌ Please specify --day for daily cards or --full for weekly cards")
            print("Example: --week 1 --day 1")
    else:
        # No arguments provided, show help and current status
        print("🎓 GOETHE A1 FLASHCARD GENERATOR")
        print("=" * 40)
        show_study_progress(args.target_date)
        print("\n" + "=" * 40)
        print("💡 QUICK START:")
        print("  python daily_cards.py --week 1 --day 1    # Today's cards")
        print("  python daily_cards.py --schedule          # Study plan")
        print("  python daily_cards.py --preview           # See card formats")
        print("  python daily_cards.py --help              # Full help")


def quick_start_wizard():
    """Interactive wizard for first-time users"""
    print("🎓 GOETHE A1 PREPARATION WIZARD")
    print("=" * 40)
    print("Let's set up your German A1 study plan!\n")
    
    # Get user info
    name = input("What's your partner's name? ").strip()
    if not name:
        name = "Student"
    
    print(f"\nHi {name}! 👋")
    print("Perfect timing for the August 2025 Goethe A1 exam in Düsseldorf!")
    print("Your Dutch knowledge will be a huge advantage! 🇳🇱➡️🇩🇪\n")
    
    # Check current week
    try:
        current_week = int(input("Which week are you starting with? (1-6): ").strip())
        if current_week < 1 or current_week > 6:
            current_week = 1
    except:
        current_week = 1
    
    # Check current day
    max_days = 5 if current_week == 1 else 6
    try:
        current_day = int(input(f"Which day of week {current_week}? (1-{max_days}): ").strip())
        if current_day < 1 or current_day > max_days:
            current_day = 1
    except:
        current_day = 1
    
    print(f"\n🎯 Starting at Week {current_week}, Day {current_day}")
    
    # Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Generate today's cards
    print(f"\n📚 Generating your first set of flashcards...")
    csv_path = generate_daily_cards(current_week, current_day)
    
    if csv_path:
        print(f"\n✅ SUCCESS! Your flashcards are ready:")
        print(f"   📄 File: {csv_path}")
        print(f"\n📱 NEXT STEPS:")
        print(f"   1. Import {Path(csv_path).name} into AnkiApp")
        print(f"   2. Study the cards (focus on Dutch connections! 🇳🇱)")
        print(f"   3. Tomorrow, run: python daily_cards.py --week {current_week} --day {current_day + 1 if current_day < max_days else 1}")
        
        # Create study schedule
        print(f"\n📅 Creating your complete study schedule...")
        schedule_path = create_study_schedule()
        if schedule_path:
            print(f"   📊 Schedule: {schedule_path}")
            print(f"   📋 Import this into Excel/Google Sheets to track progress")
    
    print(f"\n🎉 You're all set up, {name}!")
    print(f"💪 With consistent daily study, you'll be ready for August 2025!")
    print(f"🇩🇪 Viel Erfolg beim Deutschlernen!")


if __name__ == "__main__":
    # Check if this is first run (no arguments and no output directory)
    if len(sys.argv) == 1 and not Path("output").exists():
        try:
            quick_start_wizard()
        except KeyboardInterrupt:
            print("\n\n👋 Setup cancelled. Run with --help for manual options.")
        except Exception as e:
            print(f"\n❌ Error in wizard: {e}")
            print("💡 Try running with --setup first, then --help for options")
    else:
        main()