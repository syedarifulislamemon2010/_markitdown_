# -*- coding: utf-8 -*-
"""
Desktop Launcher for MarkItDown Studio.
Launches the application as a standalone desktop window using Microsoft Edge WebView2,
or falls back to the default web browser.
"""

import sys
import time
import socket
import threading
import webbrowser
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from desktop.server import run_server


def find_free_port(start_port=8080):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port


def main():
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    # Start server in background daemon thread
    server_thread = threading.Thread(
        target=run_server,
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,
    )
    server_thread.start()

    # Wait a moment for server to start
    time.sleep(0.5)

    print(f"==================================================")
    print(f"✨ MarkItDown Studio is running at: {url}")
    print(f"==================================================")

    # Check if --browser flag is passed
    if "--browser" in sys.argv:
        webbrowser.open(url)
        print("Opened in web browser. Press Ctrl+C to terminate.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            return

    # Attempt to open as native desktop window via pywebview
    try:
        import webview
        window = webview.create_window(
            title="MarkItDown Studio - Universal Markdown Editor",
            url=url,
            width=1280,
            height=850,
            min_size=(980, 680),
            background_color="#12151c",
        )
        webview.start()
    except Exception as e:
        print(f"Webview note: {e}. Opening in default system browser instead...")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
