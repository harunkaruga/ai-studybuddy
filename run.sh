#!/bin/bash

echo "========================================"
echo "   AI Study Buddy - Flashcard Generator"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "Python found! Installing dependencies..."
pip3 install -r requirements.txt

echo
echo "Running setup check..."
python3 setup.py

echo
echo "Starting the application..."
echo "The app will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

python3 app.py
