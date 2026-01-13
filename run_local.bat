@echo off
echo ========================================
echo Starting Flask App for Local Testing
echo ========================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found.
    echo You may want to create one with: python -m venv venv
    echo.
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Set debug mode for local testing
set FLASK_DEBUG=True

REM Run the application
echo Starting Flask app on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python main.py
