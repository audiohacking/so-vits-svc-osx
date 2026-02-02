#!/bin/bash
# SoVitsSVC.command - Easy launcher for SoVitsSVC macOS app
# Double-click this file to launch SoVitsSVC from the DMG or any location

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if the app exists in the same directory
if [ -d "$DIR/SoVitsSVC.app" ]; then
    echo "Launching SoVitsSVC..."
    open "$DIR/SoVitsSVC.app"
else
    echo "Error: SoVitsSVC.app not found in $DIR"
    echo "Please make sure this launcher is in the same folder as SoVitsSVC.app"
    read -p "Press Enter to exit..."
fi
