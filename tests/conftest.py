# -*- coding: utf-8 -*-
"""Pytest fixtures for MarkItDown Studio test suite."""

import socket
import threading
import time
import pytest
from desktop.server import run_server
from desktop.run_studio import wait_for_server


def find_free_port(start_port=8100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port


@pytest.fixture(scope="session")
def server_url():
    """Start desktop/server.py on a free port for the test session."""
    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"

    server_thread = threading.Thread(
        target=run_server,
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,
    )
    server_thread.start()

    ready = wait_for_server("127.0.0.1", port, timeout=5.0)
    if not ready:
        pytest.fail(f"Server failed to start within 5.0s on {base_url}")

    # Ensure /api/health responds
    time.sleep(0.1)
    yield base_url
