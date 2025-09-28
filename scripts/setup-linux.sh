#!/bin/bash

echo "==============================="
echo "Reveal.js Slides - Linux Setup"
echo "==============================="
echo

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    echo "This script is for Linux systems only."
    echo "For other platforms, no additional setup is required."
    exit 1
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "Please do not run this script as root."
    echo "The script will ask for sudo password when needed."
    exit 1
fi

echo "This script will install Chrome dependencies for PDF generation."
echo "The following packages will be installed:"
echo "  - libnss3 (Network Security Services)"
echo "  - libatk-bridge2.0-0 (Accessibility toolkit)"
echo "  - libdrm2 (Direct Rendering Manager)"
echo "  - libxcomposite1 (X Composite Extension)"
echo "  - libxdamage1 (X Damage Extension)"
echo "  - libxrandr2 (X RandR Extension)"
echo "  - libgbm1 (Generic Buffer Management)"
echo "  - libxss1 (X Screen Saver Extension)"
echo "  - libasound2t64/libasound2 (ALSA library)"
echo "  - libgtk-3-0t64/libgtk-3-0 (GTK+ 3.0 library)"
echo "  (Package names may vary depending on your Ubuntu version)"
echo

read -p "Continue with installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

echo
echo "Updating package list..."
sudo apt update

if [ $? -ne 0 ]; then
    echo "Failed to update package list. Please check your internet connection."
    exit 1
fi

echo
echo "Installing Chrome dependencies..."
# Try modern package names first, fallback to older names
sudo apt install -y \
  libnss3 \
  libatk-bridge2.0-0 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libxss1 \
  libasound2t64 \
  libgtk-3-0t64

# If t64 packages fail, try without t64 suffix
if [ $? -ne 0 ]; then
    echo "Trying alternative package names..."
    sudo apt install -y \
      libnss3 \
      libatk-bridge2.0-0 \
      libdrm2 \
      libxcomposite1 \
      libxdamage1 \
      libxrandr2 \
      libgbm1 \
      libxss1 \
      libasound2 \
      libgtk-3-0
fi

if [ $? -eq 0 ]; then
    echo
    echo "✓ Successfully installed Chrome dependencies!"
    echo

    # Verify installation
    echo "Verifying installation..."
    if dpkg -l | grep -q libnss3; then
        echo "✓ libnss3 installed"
    else
        echo "✗ libnss3 not found"
    fi

    if dpkg -l | grep -q "libgtk-3-0"; then
        echo "✓ libgtk-3-0 installed"
    elif dpkg -l | grep -q "libgtk-3-0t64"; then
        echo "✓ libgtk-3-0t64 installed"
    else
        echo "✗ GTK library not found"
    fi

    if dpkg -l | grep -q "libasound2"; then
        echo "✓ libasound2 installed"
    elif dpkg -l | grep -q "libasound2t64"; then
        echo "✓ libasound2t64 installed"
    else
        echo "✗ ALSA library not found"
    fi

    echo
    echo "Setup complete! You can now:"
    echo "1. Start the development server: ./scripts/start-dev.sh"
    echo "2. Generate PDFs: ./scripts/export-pdf.sh 03"
    echo
    echo "If you still encounter issues, try the alternative installation:"
    echo "  sudo apt install -y libnss3-dev libgconf-2-4 libxss1 libxtst6"

else
    echo
    echo "✗ Failed to install some packages."
    echo "Please try running the commands manually:"
    echo
    echo "sudo apt update"
    echo "sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 libgtk-3-0"
    echo
    echo "For troubleshooting, see: instruction.md"
    exit 1
fi