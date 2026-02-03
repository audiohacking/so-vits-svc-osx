#!/bin/bash
# Create DMG for distribution

set -euo pipefail

echo "=================================================="
echo "Creating SoVitsSVC DMG"
echo "=================================================="
echo ""

# Check if app exists
if [ ! -d "dist/SoVitsSVC.app" ]; then
    echo "Error: dist/SoVitsSVC.app not found"
    echo "Please run ./build_local.sh first"
    exit 1
fi

# Create temporary directory for DMG contents
echo "Step 1: Preparing DMG contents..."
rm -rf dmg_temp
mkdir -p dmg_temp
cp -R dist/SoVitsSVC.app dmg_temp/

# Copy the .command file if it exists
if [ -f "SoVitsSVC.command" ]; then
    cp SoVitsSVC.command dmg_temp/
    chmod +x dmg_temp/SoVitsSVC.command
fi

# Create Applications symlink for easy drag-and-drop install
ln -s /Applications dmg_temp/Applications

# Copy README if it exists
if [ -f ".github/DMG_README.txt" ]; then
    cp .github/DMG_README.txt dmg_temp/README.txt
fi

# Remove any existing DMG
rm -f SoVitsSVC-macOS.dmg

echo "Step 2: Creating DMG..."
# Create DMG
hdiutil create -volname "SoVitsSVC" \
    -srcfolder dmg_temp \
    -ov -format UDZO \
    SoVitsSVC-macOS.dmg

# Clean up
rm -rf dmg_temp

echo ""
echo "=================================================="
echo "✓ DMG created successfully!"
echo "=================================================="
echo ""
echo "DMG location: SoVitsSVC-macOS.dmg"
echo ""
echo "To test:"
echo "  open SoVitsSVC-macOS.dmg"
echo ""
