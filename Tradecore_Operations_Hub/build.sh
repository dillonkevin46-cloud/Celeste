#!/bin/bash

# Ensure pyinstaller is available
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Please run: pip install -r requirements.txt"
    exit 1
fi

echo "Cleaning up old builds..."
rm -rf build dist *.spec

echo "Building Tradecore Operations Hub executable..."

# PyInstaller command:
# -n sets the name of the executable
# --windowed removes the terminal window (crucial for GUI apps on Windows/Mac)
# --noconsole also ensures no terminal window
# --onefile creates a single portable .exe file
# --hidden-import=... handles dynamic imports not caught automatically
pyinstaller -n "Tradecore_Operations_Hub" \
            --windowed \
            --noconsole \
            --onefile \
            --hidden-import="customtkinter" \
            --hidden-import="matplotlib" \
            --hidden-import="pandas" \
            --hidden-import="openpyxl" \
            --hidden-import="sqlite3" \
            main.py

echo "Build complete! Check the 'dist' directory."
