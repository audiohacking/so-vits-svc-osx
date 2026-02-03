#!/usr/bin/env python3
"""
Helper script to add the logo to the icon files.
Supports multiple input methods.
"""

import sys
import base64
from pathlib import Path

def from_base64(b64_string, output_path):
    """Decode base64 string and save as PNG."""
    try:
        # Remove data URL prefix if present
        if ',' in b64_string:
            b64_string = b64_string.split(',', 1)[1]
        
        img_data = base64.b64decode(b64_string)
        with open(output_path, 'wb') as f:
            f.write(img_data)
        print(f"✓ Decoded and saved {len(img_data):,} bytes to {output_path}")
        return True
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return False

def from_url(url, output_path):
    """Download from URL."""
    try:
        import urllib.request
        import ssl
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            data = response.read()
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"✓ Downloaded {len(data):,} bytes to {output_path}")
            return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

def from_file(input_path, output_path):
    """Copy from file."""
    try:
        import shutil
        shutil.copy2(input_path, output_path)
        size = Path(output_path).stat().st_size
        print(f"✓ Copied {size:,} bytes to {output_path}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

def main():
    script_dir = Path(__file__).parent
    output_path = script_dir / "icon.png"
    
    print("SoVitsSVC Logo Import Helper")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 add_logo.py <file_path>    # Copy from file")
        print("  python3 add_logo.py <url>          # Download from URL")
        print("  python3 add_logo.py --base64       # Read base64 from stdin")
        print("\nExamples:")
        print("  python3 add_logo.py ~/Downloads/logo.png")
        print("  python3 add_logo.py https://example.com/logo.png")
        print("  echo 'iVBORw0KG...' | python3 add_logo.py --base64")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    success = False
    
    if input_arg == '--base64':
        print("\nReading base64 from stdin...")
        b64_data = sys.stdin.read().strip()
        success = from_base64(b64_data, output_path)
    elif input_arg.startswith('http://') or input_arg.startswith('https://'):
        print(f"\nDownloading from URL: {input_arg}")
        success = from_url(input_arg, output_path)
    else:
        print(f"\nCopying from file: {input_arg}")
        success = from_file(input_arg, output_path)
    
    if success:
        print("\n✓ Logo imported successfully!")
        print(f"  Saved to: {output_path}")
        print("\nNext step:")
        print("  python3 create_icon.py")
    else:
        print("\n✗ Failed to import logo")
        sys.exit(1)

if __name__ == "__main__":
    main()
