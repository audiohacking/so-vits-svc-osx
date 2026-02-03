# Building SoVitsSVC for macOS

This document explains how to build SoVitsSVC as a native macOS application using PyInstaller and pywebview.

## Overview

The macOS build system creates a standalone `.app` bundle that can be distributed to users. The build process:

1. Uses PyInstaller to bundle the Python application and all dependencies
2. Creates a native macOS app bundle with pywebview for a native window experience
3. Code signs the application (optional, for distribution)
4. Packages the app into a DMG for easy distribution

## Prerequisites

### System Requirements

- macOS 12.0 (Monterey) or later
- Xcode Command Line Tools (for code signing)
- Python 3.11 or later

### Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# PyInstaller and pywebview are included in requirements.txt
```

## Local Build

### Quick Build

To build the app locally:

```bash
./build_local.sh
```

This script will:
1. Install/check dependencies (PyInstaller, pywebview)
2. Clean previous builds
3. Build the app with PyInstaller
4. Set up the app bundle
5. Code sign the app (ad-hoc signing)

The built app will be located at `dist/SoVitsSVC.app`.

### Testing the App

```bash
# Open the app
open dist/SoVitsSVC.app

# Or from Finder:
# Navigate to the dist/ folder and double-click SoVitsSVC.app
```

### Creating a DMG

After building, create a DMG for distribution:

```bash
./build_dmg.sh
```

This creates `SoVitsSVC-macOS.dmg` containing:
- SoVitsSVC.app
- Applications folder symlink (for drag-and-drop install)
- README.txt with installation instructions
- SoVitsSVC.command launcher (optional)

## Build Configuration

### PyInstaller Spec File

The build is configured in `sovits_svc.spec`. Key settings:

```python
# Main entry point
['sovits_app.py']

# App bundle settings
app = BUNDLE(
    name='SoVitsSVC.app',
    bundle_identifier='com.sovitssvc.app',
    icon='build/macos/SoVitsSVC.icns',  # Optional
    ...
)
```

### Application Wrapper

`sovits_app.py` is the native app wrapper that:
- Starts a Gradio server in the background
- Opens a pywebview window pointing to the server
- Provides a native macOS app experience

### Code Signing

Code signing is handled by `build/macos/codesign.sh`. By default, it uses ad-hoc signing (no developer certificate required).

For distribution, set the `MACOS_SIGNING_IDENTITY` environment variable:

```bash
export MACOS_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
./build_local.sh
```

Entitlements are defined in `build/macos/entitlements.plist`.

## Automated Builds (GitHub Actions)

Releases are built automatically using GitHub Actions.

### Triggering a Build

#### On Release

Create a release on GitHub:

```bash
git tag v5.0.0
git push origin v5.0.0
```

Then create a release from the tag in the GitHub UI.

#### Manual Workflow

Trigger manually from the Actions tab:
1. Go to Actions → Build macOS Release
2. Click "Run workflow"
3. Enter version (e.g., `v5.0.0-macos`)
4. Click "Run workflow"

### Build Artifacts

The workflow creates:
- `SoVitsSVC-macOS.dmg` - DMG installer
- `SoVitsSVC-macOS.zip` - ZIP archive of the app
- `checksums.txt` - SHA256 checksums

These are uploaded as:
- GitHub Actions artifacts (for manual runs)
- Release assets (for release builds)

## Build Structure

```
so-vits-svc-5.8/
├── build/
│   └── macos/
│       ├── entitlements.plist       # Code signing entitlements
│       ├── codesign.sh              # Code signing script
│       ├── SoVitsSVC.icns           # App icon (optional)
│       └── ICON_README.md           # Icon creation guide
├── .github/
│   ├── workflows/
│   │   └── build-release.yml        # GitHub Actions workflow
│   └── DMG_README.txt               # User-facing README for DMG
├── sovits_app.py                    # Native app wrapper
├── sovits_svc.spec                  # PyInstaller spec file
├── SoVitsSVC.command                # Optional launcher script
├── build_local.sh                   # Local build script
└── build_dmg.sh                     # DMG creation script
```

## Customization

### App Icon

Create a custom icon:

1. Create a 1024x1024 PNG image
2. Follow the instructions in `build/macos/ICON_README.md`
3. Place `SoVitsSVC.icns` in `build/macos/`

### App Metadata

Edit `sovits_svc.spec`:

```python
info_plist={
    'CFBundleName': 'SoVitsSVC',
    'CFBundleDisplayName': 'Your Display Name',
    'CFBundleShortVersionString': '5.0.0',
    'CFBundleVersion': '5.0.0',
    ...
}
```

### Hidden Imports

If PyInstaller misses modules, add them to `hiddenimports` in `sovits_svc.spec`:

```python
hiddenimports=[
    'your_module',
    ...
]
```

## Troubleshooting

### Build Fails

**Problem**: PyInstaller fails with module not found errors

**Solution**: Add missing modules to `hiddenimports` in `sovits_svc.spec`

### App Won't Open

**Problem**: "App is damaged and can't be opened"

**Solution**: Remove quarantine attribute:
```bash
xattr -cr dist/SoVitsSVC.app
```

**Problem**: App crashes on startup

**Solution**: Run from terminal to see error messages:
```bash
dist/SoVitsSVC.app/Contents/MacOS/SoVitsSVC
```

### Large Bundle Size

**Problem**: App bundle is too large

**Solution**: 
1. Review included data files in `sovits_svc.spec`
2. Exclude unnecessary dependencies
3. Use `upx` compression (already enabled)

### Code Signing Issues

**Problem**: Signing fails with certificate errors

**Solution**: 
- For testing: Use ad-hoc signing (default)
- For distribution: Obtain Apple Developer certificate

## Performance Notes

### Apple Silicon Optimization

The app automatically uses Metal Performance Shaders (MPS) on Apple Silicon for hardware acceleration. No special configuration needed.

### Memory Usage

The app includes large ML models. Ensure at least 8GB RAM is available.

## Distribution

### For Testing

Share the DMG file directly. Users may need to:
1. Right-click app and select "Open"
2. Or run: `xattr -cr /Applications/SoVitsSVC.app`

### For Public Release

For wider distribution:
1. Obtain an Apple Developer certificate
2. Sign the app with the certificate
3. Notarize the app with Apple
4. Staple the notarization ticket

See Apple's documentation on [Notarizing macOS Software](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution).

## References

- [PyInstaller Documentation](https://pyinstaller.org/)
- [pywebview Documentation](https://pywebview.flowrl.com/)
- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Creating macOS App Bundles](https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html)

## Credits

Build system adapted from [AceForge](https://github.com/audiohacking/AceForge).
