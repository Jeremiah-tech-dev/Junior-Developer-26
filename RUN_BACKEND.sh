#!/bin/bash
cd "$(dirname "$0")/backend"

# Kill any process on port 5000
echo "Checking port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Run the backend
echo ""
echo "🚀 Starting LedgerDB Backend..."
echo ""
python api.py
