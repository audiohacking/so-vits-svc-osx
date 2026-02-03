#!/usr/bin/env python3
"""
SoVitsSVC - Gradio + pywebview Application
Native macOS app wrapper for the SoVitsSVC web interface.
"""

from __future__ import annotations

import sys
import os
import asyncio
import threading
import time
import socket
import webbrowser
from pathlib import Path

# Set environment variables early
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
if 'PYTORCH_MPS_HIGH_WATERMARK_RATIO' not in os.environ:
    os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

# For frozen apps: Add the bundle directory to sys.path and cwd so configs/ etc. are found
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
    os.chdir(bundle_dir)  # configs/, pretrain dirs are bundled here
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

print(f"[SoVitsSVC] Starting application...", flush=True)
print(f"[SoVitsSVC] Bundle directory: {bundle_dir}", flush=True)
print(f"[SoVitsSVC] Working directory: {os.getcwd()}", flush=True)

# Import pywebview
try:
    import webview
    WEBVIEW_AVAILABLE = True
    print("[SoVitsSVC] pywebview imported successfully", flush=True)
except ImportError as e:
    WEBVIEW_AVAILABLE = False
    print(f"[SoVitsSVC] WARNING: pywebview not available: {e}", flush=True)
    print("[SoVitsSVC] Falling back to browser mode", flush=True)

# Server configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7860  # Default Gradio port
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Global state
_gradio_app = None
_server_thread = None
_server_started = False

def find_free_port(start_port=7860, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((SERVER_HOST, port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port

def start_gradio_server():
    """Start the Gradio server in a background thread"""
    global _gradio_app, _server_thread, _server_started, SERVER_PORT, SERVER_URL
    
    if _server_started:
        print("[SoVitsSVC] Server already started", flush=True)
        return True
    
    print("[SoVitsSVC] Importing Gradio and app modules...", flush=True)
    
    # Note: The original app.py hardcodes port 2333
    # We use that port to avoid conflicts
    original_port = 2333
    SERVER_PORT = find_free_port(original_port)
    SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
    print(f"[SoVitsSVC] Using port: {SERVER_PORT}", flush=True)
    
    def run_server():
        """Run the Gradio server"""
        global _gradio_app
        
        # Gradio/Starlette use asyncio; this thread must have an event loop
        asyncio.set_event_loop(asyncio.new_event_loop())
        try:
            print("[SoVitsSVC] Starting Gradio server...", flush=True)
            
            # The app.py creates and launches a Gradio UI when imported
            # This is a blocking call that starts the server
            # We run it in a separate thread so the main thread can continue
            
            # Set environment so app uses our port and does not open browser
            os.environ['GRADIO_SERVER_PORT'] = str(SERVER_PORT)
            os.environ['SOVITS_NATIVE_APP'] = '1'
            
            # Import app then run its UI (app.py only runs WebUI when __name__ == '__main__')
            import app
            app.webui = app.WebUI()  # blocks until ui.launch() exits
            
            print(f"[SoVitsSVC] Gradio server exited", flush=True)
                
        except Exception as e:
            print(f"[SoVitsSVC] ERROR starting server: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    _server_started = True
    
    # Wait for server to start - try the configured port first, then the original
    print("[SoVitsSVC] Waiting for server to start...", flush=True)
    max_wait = 45  # seconds - give more time for imports
    start_time = time.time()
    
    ports_to_try = [SERVER_PORT]
    if SERVER_PORT != original_port:
        ports_to_try.append(original_port)
    
    while time.time() - start_time < max_wait:
        for port in ports_to_try:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((SERVER_HOST, port))
                sock.close()
                if result == 0:
                    # Update SERVER_PORT and SERVER_URL if different
                    if port != SERVER_PORT:
                        SERVER_PORT = port
                        SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
                    print(f"[SoVitsSVC] Server is ready at {SERVER_URL}", flush=True)
                    return True
            except Exception:
                pass
        time.sleep(0.5)
    
    print("[SoVitsSVC] WARNING: Server startup timeout", flush=True)
    # Continue anyway - the app might still be starting
    return True

def open_in_browser():
    """Open the app in the default web browser"""
    print(f"[SoVitsSVC] Opening {SERVER_URL} in browser...", flush=True)
    webbrowser.open(SERVER_URL)
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[SoVitsSVC] Shutting down...", flush=True)

def main():
    """Main entry point"""
    print("[SoVitsSVC] Initializing application...", flush=True)
    
    # Start the Gradio server
    if not start_gradio_server():
        print("[SoVitsSVC] Failed to start server", flush=True)
        # Continue anyway - server might still be starting
    
    # Wait a bit for server to fully initialize
    time.sleep(3)
    
    # Verify the server is actually running and update URL if needed
    # The app.py uses port 2333 by default
    for port in [2333, SERVER_PORT, 7860]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((SERVER_HOST, port))
            sock.close()
            if result == 0:
                actual_url = f"http://{SERVER_HOST}:{port}"
                print(f"[SoVitsSVC] Server confirmed at {actual_url}", flush=True)
                break
        except Exception:
            pass
    else:
        actual_url = SERVER_URL
    
    if WEBVIEW_AVAILABLE:
        print("[SoVitsSVC] Creating native window with pywebview...", flush=True)
        
        # Create the webview window
        window = webview.create_window(
            title='SoVits-SVC 5.0',
            url=actual_url,
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False,
            min_size=(1000, 700),
        )
        
        print("[SoVitsSVC] Starting webview...", flush=True)
        webview.start(debug=False)
        print("[SoVitsSVC] Webview closed", flush=True)
    else:
        # Fallback to browser
        print("[SoVitsSVC] pywebview not available, opening in browser...", flush=True)
        webbrowser.open(actual_url)
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[SoVitsSVC] Shutting down...", flush=True)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
