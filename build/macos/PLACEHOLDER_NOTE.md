# PLACEHOLDER ICON NOTICE

⚠️ **The current `SoVitsSVC.icns` file contains a PLACEHOLDER icon.**

## To Use the Official Logo

The official SoVitsSVC logo (with rainbow-colored letters) needs to be manually downloaded:

### Step 1: Download the Logo

Download the transparent PNG logo from one of these sources:
- Primary URL: https://github.com/user-attachments/assets/f0bf5f07-a10d-4021-b854-07b326f4c03e
- Fallback URL: https://github.com/user-attachments/assets/3df73889-ef12-41f9-bf05-0b1f5f3b11a3

Or extract it from the GitHub issue where it was provided.

### Step 2: Replace the Placeholder

Save the downloaded PNG as:
```
build/macos/icon.png
```

### Step 3: Regenerate the Icon

Run the conversion script:
```bash
cd build/macos
python3 create_icon.py
```

This will regenerate `SoVitsSVC.icns` with the official logo while preserving transparency.

## Current Status

✅ Icon infrastructure is ready
✅ Conversion script works on all platforms (Linux/Mac/Windows)
✅ PyInstaller spec file is configured to use the icon
⚠️ Placeholder icon is currently in place (waiting for manual download)

## Why Manual Download?

The build environment has restricted network access and cannot download from GitHub asset URLs.
This is a security feature to prevent unauthorized external connections.
