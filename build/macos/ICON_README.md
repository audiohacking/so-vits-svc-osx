# SoVitsSVC macOS Icon

This directory should contain `SoVitsSVC.icns` - the application icon for the macOS app bundle.

## Creating the Icon

To create `SoVitsSVC.icns`:

1. Create or obtain a 1024x1024 PNG image for your app icon
2. Save it as `icon.png` in this directory
3. Run the following commands to create the .icns file:

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

## Default Behavior

If `SoVitsSVC.icns` is not present, PyInstaller will use the default Python icon.
The app will still function correctly without a custom icon.

## Icon Design Guidelines

For best results, follow Apple's Human Interface Guidelines:
- Use a 1024x1024 source image
- Design should be recognizable at all sizes
- Use simple, bold shapes
- Avoid fine details that won't scale well
- Consider using a gradient or 3D effects for depth

## Resources

- [Apple Human Interface Guidelines - App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [iconutil man page](https://ss64.com/osx/iconutil.html)
