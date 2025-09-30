#!/bin/bash

echo "Starting Development Server..."
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not available"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Check if Python3 is available and run bootstrap.py
echo "Running bootstrap.py to sync slides..."
if command -v python3 &> /dev/null; then
    python3 tools/bootstrap.py
    if [ $? -ne 0 ]; then
        echo "Warning: bootstrap.py failed, but continuing..."
    fi
else
    echo "Warning: Python3 not found, skipping bootstrap.py"
fi

echo "Starting Vite development server..."
echo "Open your browser and go to: http://localhost:5173"
echo "Press Ctrl+C to stop the server"
echo

# Start the development server with config from config folder
npx vite --config config/vite.config.ts