@echo off
echo ========================================
echo    AI Study Buddy - Flashcard Generator
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
pip install -r requirements.txt

echo.
echo Running setup check...
python setup.py

echo.
echo Starting the application...
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
