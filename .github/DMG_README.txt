SoVits-SVC 5.0 for macOS
============================

Thank you for downloading SoVits-SVC!

INSTALLATION
------------

To install SoVits-SVC:

1. Drag the "SoVitsSVC.app" icon to the "Applications" folder
2. Open the Applications folder in Finder
3. Right-click (or Control-click) on SoVitsSVC.app
4. Select "Open" from the menu
5. Click "Open" in the dialog that appears

This is required for first launch only because the app is not signed with an Apple Developer certificate.

SYSTEM REQUIREMENTS
-------------------

- macOS 12.0 (Monterey) or later
- Apple Silicon (M1/M2/M3) recommended for best performance
- Intel Macs are supported but may be slower
- At least 8GB RAM recommended
- 4GB free disk space

FEATURES
--------

- Voice conversion using state-of-the-art AI models
- Support for multiple content encoders (Whisper, ContentVec, data2vec)
- Hybrid pitch detection (CREPE + RMVPE)
- Apple Silicon acceleration via Metal Performance Shaders (MPS)
- User-friendly web interface

USAGE
-----

After launching the app, a window will open with the SoVits-SVC interface.
You can use the interface to:

1. Preprocess audio data
2. Train voice conversion models
3. Perform voice conversion on audio files

For detailed instructions, please visit:
https://github.com/audiohacking/so-vits-svc-5.8

TROUBLESHOOTING
---------------

If the app doesn't open:
- Make sure you followed the installation steps above
- Try running: xattr -cr /Applications/SoVitsSVC.app
  (This removes the quarantine attribute)

If you encounter performance issues:
- Close other applications to free up memory
- Check Activity Monitor for resource usage

SUPPORT
-------

For issues, questions, or contributions:
https://github.com/audiohacking/so-vits-svc-5.8/issues

LICENSE
-------

This software is provided under the terms specified in the LICENSE file.

ACKNOWLEDGMENTS
---------------

SoVits-SVC is based on research and open-source contributions from the community.
See the GitHub repository for full credits and acknowledgments.
