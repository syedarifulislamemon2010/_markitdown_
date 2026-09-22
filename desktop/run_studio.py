# -*- coding: utf-8 -*-
"""
Desktop Launcher for MarkItDown Studio.
Launches the application as a standalone desktop window using Microsoft Edge WebView2,
or falls back to the default web browser.
"""

import os
import secrets
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

SERVICE_NAME = "MarkItDownStudio"


def secure_get_key(service: str) -> str:
    """Retrieve an API key from OS keyring with local secure fallback."""
    try:
        import keyring
        val = keyring.get_password(SERVICE_NAME, service)
        if val:
            return val
    except Exception:
        pass

    store_file = Path.home() / ".markitdown" / "credentials.json"
    if store_file.exists():
        try:
            import json
            data = json.loads(store_file.read_text(encoding="utf-8"))
            return data.get(service, "")
        except Exception:
            pass
    return ""


def secure_set_key(service: str, key: str) -> bool:
    """Store an API key in OS keyring with local secure fallback."""
    try:
        import keyring
        keyring.set_password(SERVICE_NAME, service, key)
    except Exception:
        pass

    store_dir = Path.home() / ".markitdown"
    store_dir.mkdir(parents=True, exist_ok=True)
    store_file = store_dir / "credentials.json"
    data = {}
    if store_file.exists():
        try:
            import json
            data = json.loads(store_file.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data[service] = key
    import json
    store_file.write_text(json.dumps(data), encoding="utf-8")
    try:
        os.chmod(store_file, 0o600)
    except Exception:
        pass
    return True


def secure_clear_keys() -> bool:
    """Clear all stored API keys from OS keyring and local store."""
    for service in ("openai", "gemini"):
        try:
            import keyring
            keyring.delete_password(SERVICE_NAME, service)
        except Exception:
            pass
    store_file = Path.home() / ".markitdown" / "credentials.json"
    if store_file.exists():
        try:
            store_file.unlink()
        except Exception:
            pass
    return True


def find_free_port(start_port=8080):
    """Find an available port starting from start_port using SO_REUSEADDR."""
    for port in range(start_port, start_port + 50):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port


def wait_for_server(host="127.0.0.1", port=8080, timeout=5.0):
    """Poll until server socket is ready to accept connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.15):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.04)
    return False


def main():
    session_token = os.environ.get("STUDIO_SESSION_TOKEN") or secrets.token_urlsafe(32)
    os.environ["STUDIO_SESSION_TOKEN"] = session_token

    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    # Start server in background daemon thread
    server_thread = threading.Thread(
        target=run_server,
        kwargs={"host": "127.0.0.1", "port": port, "session_token": session_token},
        daemon=True,
    )
    server_thread.start()

    # Actively wait until the server is ready to accept connections
    if not wait_for_server("127.0.0.1", port, timeout=5.0):
        print(f"⚠️ Warning: Server did not respond within 5s at {url}")

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
        import base64

        try:
            webview.settings['ALLOW_DOWNLOADS'] = True
        except Exception:
            pass

        class StudioApi:
            def __init__(self, token=None):
                self.window = None
                self.session_token = token or os.environ.get("STUDIO_SESSION_TOKEN", "")

            def get_session_token(self):
                return self.session_token

            def get_api_key(self, service):
                return secure_get_key(service)

            def set_api_key(self, service, key):
                return secure_set_key(service, key)

            def clear_api_keys(self):
                return secure_clear_keys()

            def save_file_dialog(self, filename, content_b64):
                if not self.window:
                    return {"success": False, "error": "No window"}
                res = self.window.create_file_dialog(webview.SAVE_DIALOG, save_filename=filename)
                if res:
                    target_path = res if isinstance(res, str) else res[0]
                    with open(target_path, 'wb') as f:
                        f.write(base64.b64decode(content_b64))
                    return {"success": True, "path": target_path}
                return {"success": False, "cancelled": True}

            def convert_file_content(self, filename, content_b64):
                import tempfile
                from desktop.server import get_converter
                suffix = Path(filename).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(base64.b64decode(content_b64))
                    tmp_path = tmp.name
                try:
                    conv = get_converter()
                    res = conv.convert_file(tmp_path)
                    return res.markdown if res.success else f"Error: {res.error_message}"
                finally:
                    if Path(tmp_path).exists():
                        try:
                            Path(tmp_path).unlink()
                        except Exception:
                            pass

        api = StudioApi(token=session_token)
        window = webview.create_window(
            title="MarkItDown Studio - Universal Markdown Editor",
            url=url,
            width=1280,
            height=850,
            min_size=(980, 680),
            background_color="#181818",
            js_api=api,
        )
        api.window = window
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
