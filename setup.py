#!/usr/bin/env python3
"""
Setup script for Language Learning Flashcard Generator
"""

import sys
from pathlib import Path
from setuptools import setup, find_packages

# Add src to path to import version
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from __version__ import (
        __version__,
        APP_NAME,
        APP_DESCRIPTION,
        APP_AUTHOR,
        APP_EMAIL,
        APP_URL,
        APP_LICENSE,
        PYTHON_REQUIRES,
        REQUIRED_PACKAGES,
        DEV_REQUIREMENTS,
        check_python_version
    )
except ImportError as e:
    print(f"Error importing version information: {e}")
    print("Make sure src/__version__.py exists and is properly formatted")
    sys.exit(1)

# Check Python version early
try:
    check_python_version()
except RuntimeError as e:
    print(f"Error: {e}")
    sys.exit(1)

# Read README for long description
def read_readme():
    """Read README file for long description"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return APP_DESCRIPTION

# Read requirements from file if it exists
def read_requirements(filename):
    """Read requirements from requirements file"""
    req_path = Path(__file__).parent / filename
    if req_path.exists():
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

# Get requirements
install_requires = read_requirements("requirements.txt") or REQUIRED_PACKAGES
dev_requires = read_requirements("requirements-dev.txt") or DEV_REQUIREMENTS

# Package configuration
setup(
    # Basic package information
    name="ankiapp-flashcard-generator",
    version=__version__,
    description=APP_DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # Author information
    author=APP_AUTHOR,
    author_email=APP_EMAIL,
    url=APP_URL,
    
    # License and classifiers
    license=APP_LICENSE,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    
    # Requirements
    python_requires=PYTHON_REQUIRES,
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "pytest-mock>=3.0.0",
        ],
        "gui": [
            # GUI-specific requirements if any
            # tkinter is usually included with Python
        ],
    },
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "flashcard-generator=main:main",
            "ankiapp-generator=main:main",
            "flashcard-cli=cli:main",
        ],
        "gui_scripts": [
            "flashcard-generator-gui=main:main",
        ],
    },
    
    # Keywords for PyPI
    keywords=[
        "anki", "ankiapp", "flashcards", "language-learning", 
        "vocabulary", "education", "german", "csv", "json",
        "spaced-repetition", "study", "learning"
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": f"{APP_URL}/issues",
        "Source": APP_URL,
        "Documentation": f"{APP_URL}#readme",
        "Changelog": f"{APP_URL}/blob/main/CHANGELOG.md",
    },
    
    # Zip safe
    zip_safe=False,
)

# Post-installation message
print(f"\n{'='*50}")
print(f"✓ {APP_NAME} v{__version__} installed successfully!")
print(f"{'='*50}")
print("To get started:")
print("  1. Run 'flashcard-generator' to launch the GUI")
print("  2. Run 'flashcard-cli --help' for command-line options")
print("  3. Check the README.md for detailed usage instructions")
print(f"{'='*50}\n")