#!/bin/bash
# Local build script for SoVitsSVC macOS app
# Uses a project venv so PyInstaller bundles all app dependencies (no system packages).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "SoVitsSVC Local Build Script"
echo "=================================================="
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Use project venv so build has gradio, torch, yaml, etc. (same as CI)
VENV_DIR="${SCRIPT_DIR}/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Step 0: Creating project venv at .venv..."
    python3 -m venv "$VENV_DIR"
fi
source "${VENV_DIR}/bin/activate"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

echo "Using Python: $($PYTHON -c 'import sys; print(sys.executable)')"

echo "Step 1: Installing dependencies into venv..."
$PIP install -q --upgrade pip
$PIP install -q -r requirements.txt
# PyTorch (MPS for Apple Silicon) - install if not present
if ! $PYTHON -c "import torch" 2>/dev/null; then
    echo "Installing PyTorch (MPS)..."
    $PIP install -q torch torchaudio torchvision
fi
$PIP install -q "pyinstaller>=6.0" "pywebview>=4.0"

echo "Step 2: Cleaning previous builds..."
rm -rf dist/SoVitsSVC.app dist/SoVitsSVC build/SoVitsSVC

echo "Step 3: Building with PyInstaller..."
$PYTHON -m PyInstaller sovits_svc.spec --clean --noconfirm

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
