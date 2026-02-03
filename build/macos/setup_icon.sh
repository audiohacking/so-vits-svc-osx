#!/bin/bash
# Quick helper to download and convert the SoVitsSVC logo

set -e

cd "$(dirname "$0")"

echo "SoVitsSVC Icon Setup"
echo "===================="

# URLs to try
URLS=(
    "https://github.com/user-attachments/assets/f0bf5f07-a10d-4021-b854-07b326f4c03e"
    "https://github.com/user-attachments/assets/3df73889-ef12-41f9-bf05-0b1f5f3b11a3"
)

# Try to download
for URL in "${URLS[@]}"; do
    echo ""
    echo "Trying to download from:"
    echo "  $URL"
    
    if curl -fsSL "$URL" -o icon.png 2>/dev/null || wget -q "$URL" -O icon.png 2>/dev/null; then
        echo "✓ Downloaded successfully"
        break
    else
        echo "✗ Download failed"
        rm -f icon.png
    fi
done

# Check if we got the file
if [ ! -f icon.png ]; then
    echo ""
    echo "❌ Could not download the logo automatically."
    echo ""
    echo "Please download manually:"
    echo "  1. Visit: https://github.com/audiohacking/so-vits-svc-5.8/issues"
    echo "  2. Find the issue titled 'Update App icon'"
    echo "  3. Download the logo PNG image"
    echo "  4. Save it as: $(pwd)/icon.png"
    echo "  5. Run this script again, or run: python3 create_icon.py"
    exit 1
fi

# Verify it's a PNG
if ! file icon.png | grep -q PNG; then
    echo "❌ Downloaded file is not a PNG image"
    rm -f icon.png
    exit 1
fi

echo ""
echo "✓ Logo file ready: icon.png"
echo ""
echo "Generating macOS icon..."
python3 create_icon.py

echo ""
echo "✓ Setup complete!"
echo "  Icon file: $(pwd)/SoVitsSVC.icns"
echo ""
echo "The icon will be used when building the macOS app with:"
echo "  pyinstaller sovits_svc.spec"
