# SoVitsSVC macOS Icon

This directory contains `SoVitsSVC.icns` - the application icon for the macOS app bundle.

## Current Icon

✓ The official SoVitsSVC logo is installed and ready to use!

The colorful "SO VITS SVC" rainbow logo with transparency is now included in the app icon.

## Creating/Updating the Icon

The `create_icon.py` script provides a cross-platform solution for creating the `.icns` file from a PNG image:

```bash
# Use the default icon.png in this directory
python3 create_icon.py

# Or specify a different PNG file
python3 create_icon.py /path/to/your/icon.png
```

### How It Works

The script:
- Loads the PNG image (preserving transparency)
- Generates 7 different icon sizes (16x16 to 1024x1024)
- Packages them in the macOS `.icns` format
- Works on Linux, Windows, and macOS (pure Python implementation)

### Manual Creation (macOS Only)

If you prefer using macOS native tools:

```bash
# Create iconset directory
mkdir SoVitsSVC.iconset

# Generate different sizes
sips -z 16 16     icon.png --out SoVitsSVC.iconset/icon_16x16.png
sips -z 32 32     icon.png --out SoVitsSVC.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out SoVitsSVC.iconset/icon_32x32.png
sips -z 64 64     icon.png --out SoVitsSVC.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out SoVitsSVC.iconset/icon_128x128.png
sips -z 256 256   icon.png --out SoVitsSVC.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out SoVitsSVC.iconset/icon_256x256.png
sips -z 512 512   icon.png --out SoVitsSVC.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out SoVitsSVC.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out SoVitsSVC.iconset/icon_512x512@2x.png

# Convert to icns
iconutil -c icns SoVitsSVC.iconset

# Clean up
rm -rf SoVitsSVC.iconset
```

## Integration with PyInstaller

The `sovits_svc.spec` file automatically uses the icon when building the macOS app:

```python
icon_path = spec_root / 'build' / 'macos' / 'SoVitsSVC.icns'
app = BUNDLE(
    ...
    icon=str(icon_path) if icon_path.exists() else None,
    ...
)
```

If `SoVitsSVC.icns` is not present, PyInstaller will use the default Python icon.

## Icon Design Guidelines

For best results, follow Apple's Human Interface Guidelines:
- Use a 1024x1024 source image (or larger)
- Ensure transparency is preserved (PNG with alpha channel)
- Design should be recognizable at all sizes (test at 16x16)
- Use simple, bold shapes
- Avoid fine details that won't scale well
- Consider using a gradient or 3D effects for depth

## Transparency Notes

The conversion script preserves PNG transparency by:
- Converting images to RGBA mode if needed
- Using PNG format for all icon sizes (icns supports PNG)
- High-quality Lanczos resampling to maintain quality

## Resources

- [Apple Human Interface Guidelines - App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [iconutil man page](https://ss64.com/osx/iconutil.html)
- [ICNS Format Specification](https://en.wikipedia.org/wiki/Apple_Icon_Image_format)
