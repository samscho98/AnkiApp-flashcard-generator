# Language Learning Flashcard Generator

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

A powerful and flexible desktop application for converting structured vocabulary and grammar data from JSON files into beautifully formatted CSV files compatible with AnkiApp. Perfect for language learners who want to create professional flashcards with rich formatting, examples, and cross-language connections.

![Screenshot](https://via.placeholder.com/800x500/2E3440/ECEFF4?text=Flashcard+Generator+GUI)

## ✨ Key Features

- 🌍 **Universal Language Support** - Works with any language pair
- 📚 **Multiple Content Types** - Vocabulary, grammar, phrases, and more  
- 🎨 **Rich HTML Formatting** - Bold text, italics, line breaks for beautiful cards
- 🔗 **Language Connections** - Leverage existing knowledge (e.g., Dutch → German)
- 📊 **Progress Tracking** - Built-in study session and achievement system
- 🎯 **Flexible Data Structure** - Supports various JSON organizational patterns
- 💾 **Multiple Export Formats** - AnkiApp, standard Anki, Quizlet, and custom formats
- 🖥️ **Cross-Platform GUI** - Native desktop application using tkinter
- 📈 **Study Analytics** - Track learning progress, streaks, and statistics
- ⚙️ **Highly Configurable** - Customizable formatting, tags, and export options

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Installation

#### Option 1: Direct Download
```bash
git clone https://github.com/yourusername/AnkiApp-flashcard-generator.git
cd AnkiApp-flashcard-generator
pip install -r requirements.txt
```

#### Option 2: Install as Package
```bash
pip install ankiapp-flashcard-generator
```

### First Launch
```bash
# GUI Application
python main.py

# Or if installed as package
flashcard-generator

# Command Line Interface
python cli.py --help
```

## 📋 Usage

### 1. **Organize Your Data**
Create JSON files in the following structure:
```
data/
├── vocabulary/
│   ├── German A1/
│   │   ├── week1.json
│   │   ├── week2.json
│   │   └── ...
│   └── Spanish Beginner/
│       ├── lesson1.json
│       └── ...
└── grammar/
    ├── German A1/
    │   ├── articles.json
    │   └── ...
    └── ...
```

### 2. **JSON File Format**
```json
{
  "target_language": "german",
  "native_language": "english",
  "topic": "Basic Vocabulary",
  "days": {
    "day_1": {
      "topic": "Greetings",
      "words": [
        {
          "german": "Hallo",
          "english": "Hello",
          "dutch_connection": "Hallo",
          "example": "Hallo, wie geht es dir?",
          "example_translation": "Hello, how are you?",
          "pronunciation": "HAH-lo"
        }
      ]
    }
  }
}
```

### 3. **Generate Flashcards**
1. Launch the application: `python main.py`
2. Select your language and content type
3. Choose the JSON file to process
4. Select which sections to include
5. Preview the formatted cards
6. Export to CSV for AnkiApp import

### 4. **Import to AnkiApp**
1. Open AnkiApp on your device
2. Create a new deck or select existing
3. Import the generated CSV file
4. Start studying!

## 🎴 Card Format Examples

### Vocabulary Card
**Front:** `das Haus`

**Back:**
> **the house** *(🇳🇱 Dutch: het huis)*
> 
> *Example: Das Haus ist groß und schön*
> 
> *🔊 Pronunciation: dahs hows*

### Grammar Card
**Front:** `German Articles`

**Back:**
> **der, die, das (the)**
> 
> *Example: der Mann, die Frau, das Kind*
> *Translation: the man, the woman, the child*
> 
> *📝 Note: German has three grammatical genders*

## 🏗️ Project Structure

```
AnkiApp-flashcard-generator/
├── src/                          # Source code
│   ├── __version__.py           # Version information
│   ├── core/                    # Core functionality
│   │   ├── csv_generator.py     # CSV generation engine
│   │   ├── card_formatter.py    # Card formatting logic
│   │   ├── history_manager.py   # Progress tracking
│   │   └── data_manager.py      # Data handling
│   ├── gui/                     # User interface
│   │   ├── main_window.py       # Main application window
│   │   ├── widgets.py           # Custom UI components
│   │   └── settings_window.py   # Configuration dialog
│   ├── config/                  # Configuration management
│   │   └── settings.py          # Settings system
│   └── utils/                   # Utilities
│       ├── file_utils.py        # File operations
│       └── validation.py        # Data validation
├── data/                        # Learning content
│   ├── vocabulary/              # Vocabulary files
│   └── grammar/                 # Grammar files
├── tests/                       # Unit tests
├── main.py                      # GUI application launcher
├── cli.py                       # Command-line interface
└── README.md                    # This file
```

## ⚙️ Configuration

The application stores settings in `config.json`:

```json
{
  "study": {
    "daily_target_items": 20,
    "include_native_connections": true,
    "auto_advance_progress": true
  },
  "export": {
    "output_directory": "output",
    "export_format": "ankiapp",
    "html_formatting": true
  },
  "appearance": {
    "theme": "system",
    "window_width": 1000,
    "window_height": 700
  }
}
```

## 🧪 Advanced Usage

### Command Line Interface
```bash
# Generate cards for specific content
python cli.py --language german --type vocabulary --file week1.json

# Batch process multiple files
python cli.py --batch --input-dir data/vocabulary/German/

# Custom output format
python cli.py --format anki --output custom_cards.csv

# Validate data files
python cli.py --validate --input data/vocabulary/
```

### Programmatic Usage
```python
from src.core.csv_generator import GenericLanguageCSVGenerator
from src.core.card_formatter import AnkiAppFormatter

# Create generator
generator = GenericLanguageCSVGenerator("output")

# Generate from JSON file
csv_path = generator.generate_from_json_file("data/vocabulary/week1.json")

# Custom formatting
formatter = AnkiAppFormatter({
    'show_connections': True,
    'target_language': 'german',
    'native_language': 'english'
})
```

### Custom Data Structures
The application supports various JSON structures:

```json
// Simple structure
{
  "entries": [
    {"target": "word", "native": "translation"}
  ]
}

// Nested structure
{
  "units": {
    "unit_1": {
      "lessons": {
        "lesson_1": {
          "items": [{"target": "word", "native": "translation"}]
        }
      }
    }
  }
}
```

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/yourusername/AnkiApp-flashcard-generator.git
cd AnkiApp-flashcard-generator

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_csv_generator.py
```

### Building and Distribution
```bash
# Build package
python -m build

# Upload to PyPI (requires authentication)
python -m twine upload dist/*
```

## 📊 Supported Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **AnkiApp** | 5-column CSV with HTML formatting | Mobile-first studying |
| **Standard Anki** | Tab-separated with tags | Desktop Anki application |
| **Quizlet** | Simple term/definition pairs | Web-based studying |
| **Generic** | Customizable field mapping | Integration with other tools |

## 🌟 Use Cases

### Perfect For:
- **Language Exam Preparation** (A1-C2 levels)
- **Vocabulary Building** with spaced repetition
- **Grammar Rule Learning** with examples
- **Cross-Language Learning** (leveraging existing knowledge)
- **Educational Content Creation** for language teachers
- **Self-Study Programs** with progress tracking

### Example Learning Scenarios:
- **German A1 Preparation**: 650 official vocabulary words over 6 weeks
- **Spanish Business Vocabulary**: Industry-specific terminology
- **French Grammar Mastery**: Verb conjugations and rules
- **Multi-Language Comparison**: Germanic language connections

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest`
5. **Submit a pull request**

### Contribution Guidelines:
- Follow PEP 8 style guidelines
- Write tests for new functionality
- Update documentation as needed
- Use meaningful commit messages

## 📝 Changelog

### Version 1.0.0 (Current)
- ✨ Initial release
- 🎨 Complete GUI application with tkinter
- 📊 AnkiApp CSV export with HTML formatting
- 🔗 Language connection support
- 📈 Progress tracking and statistics
- ⚙️ Configurable settings system
- 🧪 Comprehensive test suite

### Planned Features:
- 🔊 Audio pronunciation support
- 📱 Mobile companion app
- 🌐 Online vocabulary sources integration
- 🎯 Spaced repetition scheduling
- 📚 B1/B2 content expansion
- 🔄 Bidirectional sync with AnkiApp

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AnkiApp Team** for creating an excellent spaced repetition platform
- **Goethe Institute** for standardized language learning frameworks
- **Python Community** for amazing libraries and tools
- **Language Learning Community** for feedback and testing

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/AnkiApp-flashcard-generator/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/AnkiApp-flashcard-generator/discussions)
- 📧 **Email**: your.email@example.com
- 📖 **Documentation**: [Wiki](https://github.com/yourusername/AnkiApp-flashcard-generator/wiki)

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/AnkiApp-flashcard-generator&type=Date)](https://star-history.com/#yourusername/AnkiApp-flashcard-generator&Date)

---

**Made with ❤️ for language learners worldwide**

*Ready to supercharge your language learning journey? Give it a star ⭐ and start creating amazing flashcards today!*