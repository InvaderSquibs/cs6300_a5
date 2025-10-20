#!/bin/bash

# Vector Template Setup Script
echo "========================================"
echo "  Vector Template Setup"
echo "========================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file to configure your local LLM endpoint"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file to configure your LLM endpoint:"
echo "   nano .env"
echo ""
echo "2. Make sure your local LLM is running (e.g., Ollama, LM Studio)"
echo ""
echo "3. Run the validation script:"
echo "   python validate_vdb.py"
echo ""
echo "4. To activate the virtual environment in the future:"
echo "   source venv/bin/activate"