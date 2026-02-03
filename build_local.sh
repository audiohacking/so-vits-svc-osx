#!/bin/bash
# Local build script for SoVitsSVC macOS app
# This script builds the app locally for testing

set -euo pipefail

echo "=================================================="
echo "SoVitsSVC Local Build Script"
echo "=================================================="
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Step 1: Checking dependencies..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller>=6.0
fi

if ! python3 -c "import webview" 2>/dev/null; then
    echo "Installing pywebview..."
    pip3 install pywebview>=4.0
fi

echo "Step 2: Cleaning previous builds..."
rm -rf dist/SoVitsSVC.app dist/SoVitsSVC build/SoVitsSVC

echo "Step 3: Building with PyInstaller..."
python3 -m PyInstaller sovits_svc.spec --clean --noconfirm

if [ ! -d "dist/SoVitsSVC.app" ]; then
    echo "Error: Build failed - dist/SoVitsSVC.app not created"
    exit 1
fi

echo "Step 4: Setting up app bundle executable..."
# Copy SoVitsSVC_bin to SoVitsSVC
cp dist/SoVitsSVC.app/Contents/MacOS/SoVitsSVC_bin dist/SoVitsSVC.app/Contents/MacOS/SoVitsSVC
chmod +x dist/SoVitsSVC.app/Contents/MacOS/SoVitsSVC

echo "Step 5: Code signing..."
if [ -f "build/macos/codesign.sh" ]; then
    chmod +x build/macos/codesign.sh
    ./build/macos/codesign.sh dist/SoVitsSVC.app
else
    echo "Warning: codesign.sh not found, skipping code signing"
fi

echo ""
echo "=================================================="
echo "✓ Build completed successfully!"
echo "=================================================="
echo ""
echo "The app is located at: dist/SoVitsSVC.app"
echo ""
echo "To test the app:"
echo "  open dist/SoVitsSVC.app"
echo ""
echo "To create a DMG:"
echo "  ./build_dmg.sh"
echo ""
