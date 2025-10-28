@echo off
REM Batch script to run the Streamlit application on Windows

echo ========================================
echo ISEC Contract Note Data Extractor
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found
    echo Please create a .env file with your OPENAI_API_KEY
    echo Example: OPENAI_API_KEY=your_api_key_here
    echo.
    pause
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting Streamlit application...
echo.
echo The app will open in your default browser at http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause

