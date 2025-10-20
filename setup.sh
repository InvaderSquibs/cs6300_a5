#!/bin/bash

# Setup script for Vector Database Template

echo "Setting up Vector Database Template..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "Error: pip is required but not installed."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

echo "Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

echo ""
echo "Setup complete! You can now:"
echo "1. Run examples: python examples.py"
echo "2. Run offline example: python offline_example.py"
echo "3. Start the server: python server.py"
echo ""
echo "For more information, see README.md"