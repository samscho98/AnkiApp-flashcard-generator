@echo off
REM Windows batch file to run the Language Learning Flashcard Generator
REM Launches python main.py with error handling and user-friendly messages

title Language Learning Flashcard Generator

echo.
echo =========================================================
echo   Language Learning Flashcard Generator
echo =========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.6+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo 🐍 Python version:
python --version
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ Error: main.py not found
    echo.
    echo Make sure you're running this from the project root directory
    echo Expected file structure:
    echo   run.bat
    echo   main.py
    echo   src\gui\...
    echo   src\core\...
    echo.
    pause
    exit /b 1
)

echo 🚀 Starting application...
echo.

REM Run the application with error handling
python main.py
set app_exit_code=%errorlevel%

echo.
if %app_exit_code% equ 0 (
    echo ✅ Application closed normally
) else (
    echo ❌ Application exited with error code: %app_exit_code%
    echo.
    echo Check flashcard_generator.log for details
)

pause