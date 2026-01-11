#!/bin/bash
cd "$(dirname "$0")/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Run the frontend
echo "Starting LedgerDB frontend on http://localhost:5173"
npm run dev
