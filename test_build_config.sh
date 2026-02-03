#!/bin/bash
# Test script to verify build configuration
# This script checks that all necessary files and directories are present

set -e

echo "=================================================="
echo "SoVitsSVC Build Configuration Test"
echo "=================================================="
echo ""

EXIT_CODE=0

# Function to check if a file exists
check_file() {
    if [ -f "$1" ]; then
        echo "✓ $1"
    else
        echo "✗ $1 (missing)"
        EXIT_CODE=1
    fi
}

# Function to check if a directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo "✓ $1/"
    else
        echo "✗ $1/ (missing)"
        EXIT_CODE=1
    fi
}

echo "Checking build configuration files..."
check_file "sovits_app.py"
check_file "sovits_svc.spec"
check_file "build_local.sh"
check_file "build_dmg.sh"
check_file "SoVitsSVC.command"
check_file "BUILD_MACOS.md"
check_file "VERSION"
check_file "requirements.txt"
check_file "requirements_macos.txt"

echo ""
echo "Checking build/macos directory..."
check_dir "build/macos"
check_file "build/macos/entitlements.plist"
check_file "build/macos/codesign.sh"
check_file "build/macos/ICON_README.md"

echo ""
echo "Checking GitHub Actions workflow..."
check_dir ".github/workflows"
check_file ".github/workflows/build-release.yml"
check_file ".github/DMG_README.txt"

echo ""
echo "Checking main application files..."
check_file "app.py"

echo ""
echo "Checking module directories..."
for dir in models vits vits_decoder vits_extend pitch hubert contentvec whisper data2vec crepe rmvpe speaker utils prepare vad feature_retrieval vits_pretrain hubert_pretrain whisper_pretrain speaker_pretrain; do
    check_dir "$dir"
done

echo ""
echo "Checking configurations..."
check_dir "configs"

echo ""
echo "Checking script permissions..."
if [ -x "build/macos/codesign.sh" ]; then
    echo "✓ build/macos/codesign.sh is executable"
else
    echo "✗ build/macos/codesign.sh is not executable"
    EXIT_CODE=1
fi

if [ -x "build_local.sh" ]; then
    echo "✓ build_local.sh is executable"
else
    echo "✗ build_local.sh is not executable"
    EXIT_CODE=1
fi

if [ -x "build_dmg.sh" ]; then
    echo "✓ build_dmg.sh is executable"
else
    echo "✗ build_dmg.sh is not executable"
    EXIT_CODE=1
fi

if [ -x "SoVitsSVC.command" ]; then
    echo "✓ SoVitsSVC.command is executable"
else
    echo "✗ SoVitsSVC.command is not executable"
    EXIT_CODE=1
fi

echo ""
echo "Checking Python syntax..."
if command -v python3 &> /dev/null; then
    if python3 -m py_compile sovits_app.py 2>/dev/null; then
        echo "✓ sovits_app.py syntax is valid"
    else
        echo "✗ sovits_app.py has syntax errors"
        EXIT_CODE=1
    fi
    
    if python3 -c "import ast; ast.parse(open('sovits_svc.spec').read())" 2>/dev/null; then
        echo "✓ sovits_svc.spec syntax is valid"
    else
        echo "✗ sovits_svc.spec has syntax errors"
        EXIT_CODE=1
    fi
else
    echo "⚠ Python 3 not found, skipping syntax checks"
fi

echo ""
echo "Checking requirements.txt..."
if grep -q "pywebview" requirements.txt; then
    echo "✓ pywebview in requirements.txt"
else
    echo "✗ pywebview not in requirements.txt"
    EXIT_CODE=1
fi

if grep -q "pyinstaller" requirements.txt; then
    echo "✓ pyinstaller in requirements.txt"
else
    echo "✗ pyinstaller not in requirements.txt"
    EXIT_CODE=1
fi

echo ""
echo "=================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All checks passed!"
    echo "=================================================="
    echo ""
    echo "Build configuration is complete and valid."
    echo ""
    echo "Next steps:"
    echo "1. On macOS, run: ./build_local.sh"
    echo "2. Test the app: open dist/SoVitsSVC.app"
    echo "3. Create DMG: ./build_dmg.sh"
    echo ""
    echo "For automated builds:"
    echo "- Create a release on GitHub"
    echo "- Or manually trigger the 'Build macOS Release' workflow"
else
    echo "✗ Some checks failed!"
    echo "=================================================="
    echo ""
    echo "Please fix the issues above before building."
fi
echo ""

exit $EXIT_CODE
