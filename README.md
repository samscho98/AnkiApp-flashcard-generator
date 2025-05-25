# Goethe A1 Vocabulary Generator

A powerful tkinter-based desktop application that generates beautifully formatted CSV files for AnkiApp from the complete official Goethe Institute A1 vocabulary list. Designed specifically for learners preparing for the **Goethe A1 Start Deutsch 1** exam.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Goethe](https://img.shields.io/badge/Goethe-A1%20Official-red.svg)

## 🎯 Key Features

- **📚 Complete A1 Vocabulary**: All 650 official Goethe Institute words
- **🗓️ Structured Learning**: 6-week program with daily topics (5.5 weeks total)
- **🇳🇱 Dutch Connections**: Leverages existing A1 Dutch knowledge
- **🔄 Auto Translation**: German examples automatically translated to English
- **📈 Progress Tracking**: Automatic week advancement and download history  
- **💳 AnkiApp Ready**: Beautiful HTML-formatted flashcards
- **🎨 Rich Formatting**: Bold, italic, and line breaks for optimal learning
- **⚙️ Grammar Support**: Extensible architecture for future grammar content

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Internet connection (for translation features)

### Installation
1. **Clone or download** this repository
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   - **Windows:** Double-click `run.bat`
   - **Linux/Mac:** Run `./run.sh` or `python src/main.py`

### Usage
1. **Select Week:** Use the dropdown to choose your current study week
2. **Pick Day:** Select the specific day from the topic list
3. **Preview:** Review vocabulary and formatting in the preview panel
4. **Export:** Click "Export to CSV" to generate your AnkiApp file
5. **Import:** Load the CSV file into AnkiApp for studying

## 📋 Study Schedule

Perfect for **August 2025 Goethe A1 exam** preparation:

| Week | Topic | Words | Daily Load |
|------|-------|-------|------------|
| **Week 1** | Essential Grammar & Final A1 Words | 50 | 10/day (5 days) |
| **Week 2** | Time & Daily Activities | 120 | 20/day (6 days) |
| **Week 3** | Wohnen - Living & Housing | 120 | 20/day (6 days) |
| **Week 4** | Essen/Trinken & Einkaufen - Food & Shopping | 120 | 20/day (6 days) |
| **Week 5** | Körper/Gesundheit & Dienstleistungen - Health & Services | 120 | 20/day (6 days) |
| **Week 6** | Person & Basic Communication | 120 | 20/day (6 days) |

**Schedule:** Monday-Saturday study, Sunday rest  
**Total Duration:** 5.5 weeks (33 study days)  
**Target:** 650 official vocabulary words

## 💳 AnkiApp Card Format

### Example Card

**Front:** `der Hund`

**Back:**
> **the dog** *(similar to Dutch: de hond)*
> 
> **Example:** Der Hund ist am spielen  
> **Translation:** *The dog is playing*

### Features
- **Bold** English translations for emphasis
- **Italic** Dutch connections when available
- Clear example sentences with translations
- HTML formatting for beautiful cards
- Smart connection detection (similar/identical)

## 🏗️ Project Structure

```
goethe-a1-vocab-app/
├── src/                     # Source code
│   ├── main.py             # Application entry point
│   ├── gui/                # User interface components
│   │   ├── main_window.py  # Main application window
│   │   ├── widgets.py      # Custom UI components
│   │   └── settings_window.py # Configuration dialog
│   ├── core/               # Core functionality
│   │   ├── data_manager.py # JSON vocabulary loader
│   │   ├── csv_generator.py # AnkiApp CSV generator
│   │   ├── translator.py   # German-English translation
│   │   ├── card_formatter.py # HTML card formatting
│   │   └── history_manager.py # Progress tracking
│   ├── utils/              # Utilities
│   └── config/             # Settings management
├── data/                   # Vocabulary data
│   ├── vocabulary/         # Official Goethe A1 JSON files
│   │   ├── week1.json     # Essential Grammar (50 words)
│   │   ├── week2.json     # Time & Activities (120 words)
│   │   ├── week3.json     # Living & Housing (120 words)
│   │   ├── week4.json     # Food & Shopping (120 words)
│   │   ├── week5.json     # Health & Services (120 words)
│   │   └── week6.json     # Person & Communication (120 words)
│   └── grammar/           # Future grammar content
├── output/                # Generated CSV files
├── tests/                 # Unit tests
├── config.json           # Application settings
├── history.json          # Progress tracking
└── requirements.txt      # Python dependencies
```

## ⚙️ Configuration

### Application Settings (`config.json`)
```json
{
  "data_path": "data/vocabulary",
  "output_path": "output", 
  "csv_format": "ankiapp",
  "include_dutch_connections": true,
  "auto_advance_weeks": true,
  "enable_translation": true,
  "window_geometry": "1000x600"
}
```

### Progress Tracking (`history.json`)
- Current week tracking
- Downloaded file history
- Completed weeks list
- Automatic week advancement

## 🔧 Advanced Features

### Translation System
- **Google Translate** integration for example sentences
- **Smart caching** to avoid repeated translations
- **Offline fallback** when translation unavailable
- **Rate limiting** to respect API usage

### Dutch Integration
- Automatic detection of similar/identical words
- Smart labeling: "similar to Dutch" vs "identical to Dutch"
- Leverages existing A1 Dutch knowledge
- Optional hiding for non-Dutch speakers

### Progress Management
- **Auto-advancement**: Moves to next week when current week completed
- **Download tracking**: Visual indicators for completed days
- **History preservation**: Never lose progress
- **Flexible scheduling**: Skip days or repeat weeks as needed

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding Vocabulary
1. Create JSON files in `data/vocabulary/`
2. Follow the existing structure:
```json
{
  "week": 1,
  "topic": "Topic Name",
  "total_words": 50,
  "days": {
    "day_1": {
      "topic": "Daily Topic",
      "words": [
        {
          "german": "das Wort",
          "english": "the word", 
          "dutch_connection": "het woord",
          "example": "Das ist ein deutsches Wort.",
          "official": true
        }
      ]
    }
  }
}
```

### Extending Features
- **New learning modes**: Add grammar, pronunciation, etc.
- **Custom export formats**: Beyond AnkiApp CSV
- **Additional languages**: Extend Dutch connections
- **Advanced scheduling**: Spaced repetition integration

## 🎓 Perfect For

- **Goethe A1 exam preparation** (Start Deutsch 1)
- **Structured German learning** programs
- **Students with Dutch background** (A1+ level)
- **Adult learners** preparing for German residency/citizenship
- **AnkiApp users** who want professional flashcards

## 📚 Vocabulary Coverage

Based on **official Goethe Institute A1 Start Deutsch 1 Wortliste**:

✅ **Person** - Names, family, personal information  
✅ **Wohnen** - Living situations, housing, furniture  
✅ **Umwelt** - Environment, weather, time  
✅ **Reisen/Verkehr** - Travel, transportation  
✅ **Essen/Trinken** - Food, beverages, restaurants  
✅ **Einkaufen** - Shopping, stores, clothing  
✅ **Dienstleistungen** - Services, post, telecommunications  
✅ **Körper/Gesundheit** - Body, health, medical care  
✅ **Arbeit/Beruf** - Work, professions  
✅ **Freizeit/Unterhaltung** - Leisure, entertainment

## 🌟 Success Story

*"This app helped my partner from the Philippines pass her Goethe A1 exam in Düsseldorf! The Dutch connections were incredibly helpful since she already had A1 Dutch from living in Belgium. The automatic translations made studying so much more efficient."*

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues, feature requests, or pull requests.

## 🎯 Roadmap

- [ ] Grammar exercise integration
- [ ] Audio pronunciation support  
- [ ] Multiple export formats (Anki, Quizlet, etc.)
- [ ] Spaced repetition scheduling
- [ ] Mobile companion app
- [ ] B1/B2 vocabulary expansion

---

**Viel Erfolg beim Deutschlernen!** 🇩🇪

*Ready for your Goethe A1 exam in August 2025!*