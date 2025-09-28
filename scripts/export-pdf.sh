#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: ./export-pdf.sh [week_number]"
    echo "Example: ./export-pdf.sh 03"
    echo
    echo "Available options:"
    echo "  Week number: 01, 02, 03, 04, 05, etc."
    echo
    exit 1
fi

WEEK=$1

echo "Exporting PDF for Week $WEEK..."
echo

# Auto-detect running development server port
echo "Detecting development server..."
DEV_PORT=""

# Check common ports
for port in 5173 5174 3000 8080; do
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        DEV_PORT=$port
        echo "Found development server on port $port"
        break
    fi
done

if [ -z "$DEV_PORT" ]; then
    echo "Error: No development server found on common ports (5173, 5174, 3000, 8080)"
    echo "Please start the development server first with: ./scripts/start-dev.sh"
    echo
    exit 1
fi

# Create pdf-exports directory if it doesn't exist
mkdir -p pdf-exports

echo "Generating PDF... This may take a few moments."
node tools/export-pdf.mjs --week $WEEK --port $DEV_PORT

if [ $? -eq 0 ]; then
    echo
    echo "✓ PDF generated successfully!"
    echo "Check pdf-exports folder for week$WEEK.pdf"
else
    echo
    echo "✗ PDF generation failed!"
    echo "Make sure:"
    echo "  1. Development server is running"
    echo "  2. Week $WEEK content exists"
    echo "  3. All dependencies are installed"
    echo "  4. Chrome dependencies are installed (for Linux):"
    echo "     sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2"
fi

echo