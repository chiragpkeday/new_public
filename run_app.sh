#!/bin/bash
# Shell script to run the Streamlit application on Linux/Mac

echo "========================================"
echo "ISEC Contract Note Data Extractor"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found: $(python3 --version)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo "Example: OPENAI_API_KEY=your_api_key_here"
    echo ""
    read -p "Press Enter to continue..."
fi

# Check if streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "Starting Streamlit application..."
echo ""
echo "The app will open in your default browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py

