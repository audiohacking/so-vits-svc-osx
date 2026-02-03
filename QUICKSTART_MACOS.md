# Quick Start: Building SoVitsSVC for macOS

This is a quick reference guide for building the macOS app. For detailed information, see [BUILD_MACOS.md](BUILD_MACOS.md).

## Prerequisites

- macOS 12.0 or later
- Python 3.11 or later
- Xcode Command Line Tools

## Quick Build

### 1. Install Dependencies

```bash
pip install -r requirements_macos.txt
```

### 2. Build the App

```bash
./build_local.sh
```

The app will be created at `dist/SoVitsSVC.app`.

### 3. Test the App

```bash
open dist/SoVitsSVC.app
```

### 4. Create DMG (Optional)

```bash
./build_dmg.sh
```

Creates `SoVitsSVC-macOS.dmg` for distribution.

## Automated Builds

### Via GitHub Release

1. Create and push a tag:
```bash
git tag v5.0.0
git push origin v5.0.0
```

2. Create a release from the tag on GitHub

3. GitHub Actions will automatically build and attach the DMG

### Manual Workflow

1. Go to: Actions → Build macOS Release
2. Click "Run workflow"
3. Enter version (e.g., `v5.0.0-macos`)
4. Download artifacts when complete

## Troubleshooting

### Build Fails

**Check configuration:**
```bash
./test_build_config.sh
```

**Common issues:**
- PyInstaller not installed: `pip install pyinstaller>=6.0`
- pywebview not installed: `pip install pywebview>=4.0`
- Missing permissions: `chmod +x build_local.sh build_dmg.sh`

### App Won't Open

**Remove quarantine:**
```bash
xattr -cr dist/SoVitsSVC.app
```

**Check for errors:**
```bash
dist/SoVitsSVC.app/Contents/MacOS/SoVitsSVC
```

## Files Created

After building:
```
dist/
└── SoVitsSVC.app/          # macOS app bundle
    ├── Contents/
    │   ├── MacOS/
    │   │   └── SoVitsSVC   # Main executable
    │   ├── Resources/      # Python runtime and deps
    │   └── Info.plist      # App metadata
```

After creating DMG:
```
SoVitsSVC-macOS.dmg         # Distribution package
├── SoVitsSVC.app           # App bundle
├── Applications@           # Symlink to /Applications
├── SoVitsSVC.command       # Launcher script
└── README.txt              # User instructions
```

## Next Steps

- **For testing:** Share the `.app` bundle directly
- **For distribution:** Share the `.dmg` file
- **For wider release:** Consider notarization (see BUILD_MACOS.md)

## Documentation

- [BUILD_MACOS.md](BUILD_MACOS.md) - Comprehensive build guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
- [README.md](README.md) - Project overview

## Support

- Build issues: Check `test_build_config.sh` output
- App issues: Run app from terminal to see errors
- Questions: Open an issue on GitHub

---

**Quick Reference:**
- Build: `./build_local.sh`
- Test: `open dist/SoVitsSVC.app`
- DMG: `./build_dmg.sh`
- Verify: `./test_build_config.sh`
