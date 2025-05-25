# src/__version__.py
"""
Version information for Language Learning Flashcard Generator

This module contains all version-related information for the application.
It follows semantic versioning (https://semver.org/) principles.

Version format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD_METADATA]
- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality additions
- PATCH: Backward-compatible bug fixes
- PRERELEASE: Pre-release identifiers (alpha, beta, rc1, etc.)
- BUILD_METADATA: Build metadata (commit hash, build date, etc.)
"""

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_BUILD = None  # For development builds, set to build number

# Pre-release identifiers (None for stable releases)
# Examples: 'alpha', 'beta', 'rc1', 'dev'
VERSION_PRERELEASE = "beta"

# Build metadata (not part of version precedence)
# Examples: commit hash, build date, etc.
VERSION_BUILD_METADATA = None

# Construct version string
def _construct_version():
    """Construct version string following semantic versioning"""
    version_parts = [str(VERSION_MAJOR), str(VERSION_MINOR), str(VERSION_PATCH)]
    version = ".".join(version_parts)
    
    if VERSION_PRERELEASE:
        version += f"-{VERSION_PRERELEASE}"
    
    if VERSION_BUILD:
        if VERSION_PRERELEASE:
            version += f".{VERSION_BUILD}"
        else:
            version += f"-{VERSION_BUILD}"
    
    if VERSION_BUILD_METADATA:
        version += f"+{VERSION_BUILD_METADATA}"
    
    return version

# Main version string
__version__ = _construct_version()

# Version tuple for programmatic comparison
VERSION_TUPLE = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Additional version info
VERSION_INFO = {
    'major': VERSION_MAJOR,
    'minor': VERSION_MINOR,
    'patch': VERSION_PATCH,
    'build': VERSION_BUILD,
    'prerelease': VERSION_PRERELEASE,
    'build_metadata': VERSION_BUILD_METADATA,
    'version_string': __version__,
    'version_tuple': VERSION_TUPLE
}

# Application metadata
APP_NAME = "Language Learning Flashcard Generator"
APP_DESCRIPTION = "Generate AnkiApp-compatible flashcards from JSON vocabulary data to CSV format, importable by the AnkiApp."
APP_AUTHOR = "Sam Schonenberg"
APP_EMAIL = "sam@schonenberg.dev"
APP_URL = "https://github.com/samscho98/AnkiApp-flashcard-generator"
APP_LICENSE = "MIT"

# Minimum requirements
PYTHON_REQUIRES = ">=3.7"
REQUIRED_PACKAGES = [
    # Add your dependencies here
    # Example: "requests>=2.25.0",
]

# Development requirements
DEV_REQUIREMENTS = [
    "pytest>=6.0.0",
    "pytest-cov>=2.10.0",
    "black>=21.0.0",
    "flake8>=3.8.0",
    "mypy>=0.800",
]

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO.copy()

def print_version():
    """Print version information"""
    print(f"{APP_NAME} v{__version__}")
    if VERSION_PRERELEASE:
        print(f"Pre-release: {VERSION_PRERELEASE}")
    if VERSION_BUILD:
        print(f"Build: {VERSION_BUILD}")
    if VERSION_BUILD_METADATA:
        print(f"Build metadata: {VERSION_BUILD_METADATA}")

def check_python_version():
    """Check if current Python version meets requirements"""
    import sys
    
    required_version = tuple(map(int, PYTHON_REQUIRES.replace(">=", "").split(".")))
    current_version = sys.version_info[:len(required_version)]
    
    if current_version < required_version:
        raise RuntimeError(
            f"Python {'.'.join(map(str, required_version))} or higher is required. "
            f"Current version: {'.'.join(map(str, current_version))}"
        )
    
    return True

# For backward compatibility
version = __version__
version_info = VERSION_TUPLE

if __name__ == "__main__":
    print_version()
    print(f"Python requirement: {PYTHON_REQUIRES}")
    try:
        check_python_version()
        print("✓ Python version requirement met")
    except RuntimeError as e:
        print(f"✗ {e}")

# Export commonly used items
__all__ = [
    '__version__',
    'VERSION_TUPLE',
    'VERSION_INFO',
    'APP_NAME',
    'APP_DESCRIPTION',
    'get_version',
    'get_version_info',
    'print_version',
    'check_python_version'
]