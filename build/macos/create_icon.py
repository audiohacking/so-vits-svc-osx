#!/usr/bin/env python3
"""
Script to create the SoVitsSVC.icns icon from a PNG file.
This script handles the conversion of a PNG logo to macOS icns format
while preserving transparency.

This is a cross-platform solution that works on Linux, Windows, and macOS.
"""

import os
import sys
import struct
from pathlib import Path
from PIL import Image
from io import BytesIO

def create_icns_from_png(png_path, output_name="SoVitsSVC"):
    """
    Convert a PNG file to macOS icns format with all required sizes.
    Uses a pure Python implementation that works on all platforms.
    
    Args:
        png_path: Path to the source PNG file (should be at least 1024x1024)
        output_name: Base name for the output icon (without .icns extension)
    
    Returns:
        Path to the created icns file
    """
    png_path = Path(png_path)
    if not png_path.exists():
        print(f"Error: PNG file not found: {png_path}")
        sys.exit(1)
    
    script_dir = Path(__file__).parent
    output_icns = script_dir / f"{output_name}.icns"
    
    print(f"Loading PNG image: {png_path}")
    
    # Load the source image
    img = Image.open(png_path)
    
    # Ensure it has an alpha channel for transparency
    if img.mode != 'RGBA':
        print("  Converting to RGBA to preserve transparency...")
        img = img.convert('RGBA')
    
    print(f"  Source image size: {img.size[0]}x{img.size[1]}")
    
    # Define the icon sizes and their OSType codes for icns format
    # OSType codes are 4-byte identifiers for each icon size
    icon_sizes = [
        (1024, b'ic10'),  # 1024x1024 (512x512@2x)
        (512, b'ic09'),   # 512x512
        (256, b'ic08'),   # 256x256
        (128, b'ic07'),   # 128x128
        (64, b'it32'),    # 64x64 (32x32@2x)
        (32, b'il32'),    # 32x32
        (16, b'is32'),    # 16x16
    ]
    
    print("Generating icon sizes...")
    icns_data = []
    
    for size, ostype in icon_sizes:
        # Resize image with high-quality Lanczos resampling
        print(f"  Creating {size}x{size} ({ostype.decode('ascii')})...")
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Convert to PNG bytes (PNG format preserves transparency)
        png_bytes = BytesIO()
        resized.save(png_bytes, format='PNG', optimize=True)
        png_data = png_bytes.getvalue()
        
        # Create icns entry: OSType (4 bytes) + Length (4 bytes, big-endian) + Data
        entry_length = 8 + len(png_data)
        entry = ostype + struct.pack('>I', entry_length) + png_data
        icns_data.append(entry)
    
    # Create the icns file
    # Header: 'icns' magic number + total file length
    print(f"Writing icns file: {output_icns}")
    all_entries = b''.join(icns_data)
    total_length = 8 + len(all_entries)
    icns_file = b'icns' + struct.pack('>I', total_length) + all_entries
    
    # Write to file
    with open(output_icns, 'wb') as f:
        f.write(icns_file)
    
    print(f"\n✓ Successfully created {output_icns}")
    print(f"  File size: {len(icns_file):,} bytes")
    print(f"  Contains {len(icon_sizes)} icon sizes with transparency preserved")
    return output_icns

def download_logo(url, output_path):
    """Download the logo from GitHub."""
    import urllib.request
    import ssl
    
    print(f"Downloading logo from {url}...")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(url, context=ssl_context, timeout=30) as response:
            data = response.read()
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"✓ Downloaded {len(data):,} bytes to {output_path}")
            return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

def main():
    script_dir = Path(__file__).parent
    
    # Check for icon.png
    icon_png = script_dir / "icon.png"
    
    if not icon_png.exists():
        print(f"PNG file not found: {icon_png}")
        print("\nPlease download the logo and save it as 'icon.png' in this directory,")
        print("or provide the path to the PNG file as an argument.")
        print("\nUsage:")
        print(f"  python {Path(__file__).name} [path/to/icon.png]")
        print("\nFor the SoVitsSVC logo, you can download from:")
        print("  https://github.com/user-attachments/assets/3df73889-ef12-41f9-bf05-0b1f5f3b11a3")
        
        # Offer to download
        print("\nAttempting to download logo...")
        logo_url = "https://github.com/user-attachments/assets/3df73889-ef12-41f9-bf05-0b1f5f3b11a3"
        if download_logo(logo_url, icon_png):
            print("✓ Logo downloaded successfully")
        else:
            print("\nDownload failed. Please download manually.")
            sys.exit(1)
    
    # Use provided path or default
    if len(sys.argv) > 1:
        png_path = Path(sys.argv[1])
    else:
        png_path = icon_png
    
    # Create the icns file
    create_icns_from_png(png_path)
    
    print("\n✓ Icon creation complete!")
    print("  The icon is now ready to be used in the macOS app bundle.")

if __name__ == "__main__":
    main()
