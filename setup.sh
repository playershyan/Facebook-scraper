#!/bin/bash

echo "Setting up Deep Seek Web Crawler environment..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not found in PATH."
    echo "Please install Python 3.12 or later and add it to your PATH."
    exit 1
fi

echo "Python found!"
python3 --version
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

echo "Virtual environment created successfully!"
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

echo "Virtual environment activated!"
echo

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

echo
echo "Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Copy .env.example to .env and add your GROQ_API_KEY"
echo "2. Activate the virtual environment with: source venv/bin/activate"
echo "3. Run the crawler with: python main.py"
echo

