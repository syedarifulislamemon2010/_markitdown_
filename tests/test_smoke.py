# -*- coding: utf-8 -*-
"""Smoke tests verifying every route in desktop/server.py returns non-500."""

import os
import pytest
import requests

# 1x1 transparent PNG bytes for OCR minimal valid request
TINY_PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
    b'\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
    b'H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
)


def test_route_root(server_url):
    """GET / serves index.html."""
    resp = requests.get(f"{server_url}/", timeout=5)
    assert resp.status_code == 200
    assert "<html" in resp.text.lower()


def test_route_api_health(server_url):
    """GET /api/health returns 200 and healthy JSON status."""
    resp = requests.get(f"{server_url}/api/health", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"


def test_route_static_file(server_url):
    """GET /<filepath:path> serves static assets."""
    resp = requests.get(f"{server_url}/css/style.css", timeout=5)
    assert resp.status_code == 200
    assert "text/css" in resp.headers.get("Content-Type", "")


def test_route_api_convert(server_url):
    """POST /api/convert converts an uploaded markdown file."""
    files = {"file": ("test_input.md", b"# Header\nContent line", "text/markdown")}
    resp = requests.post(f"{server_url}/api/convert", files=files, timeout=10)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True


def test_route_api_ocr(server_url):
    """POST /api/ocr processes an image upload without 500."""
    files = {"image": ("pixel.png", TINY_PNG_BYTES, "image/png")}
    resp = requests.post(f"{server_url}/api/ocr", files=files, timeout=10)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True


def test_route_api_convert_ansi(server_url):
    """POST /api/convert-ansi converts Bijoy ANSI to Unicode."""
    payload = {"text": "evsjv"}
    resp = requests.post(f"{server_url}/api/convert-ansi", json=payload, timeout=5)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True


def test_route_api_convert_unicode_to_ansi(server_url):
    """POST /api/convert-unicode-to-ansi converts Unicode to Bijoy ANSI."""
    payload = {"text": "বাংলা"}
    resp = requests.post(f"{server_url}/api/convert-unicode-to-ansi", json=payload, timeout=5)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True


def test_route_api_export_docx(server_url):
    """POST /api/export-docx generates a Word .docx stream."""
    payload = {"markdown": "# Test Title\n\nParagraph text", "title": "TestDoc"}
    resp = requests.post(f"{server_url}/api/export-docx", json=payload, timeout=5)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    assert len(resp.content) > 0


def test_route_api_download_file(server_url):
    """POST /api/download-file streams back raw file content with Content-Disposition."""
    payload = {
        "content": "Sample file text",
        "filename": "sample.txt",
        "mime_type": "text/plain; charset=utf-8",
    }
    resp = requests.post(f"{server_url}/api/download-file", json=payload, timeout=5)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    assert resp.content == b"Sample file text"


def test_route_api_export_pdf(server_url):
    """POST /api/export-pdf generates a PDF stream if headless browser is available."""
    chrome_candidates = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    if not any(os.path.exists(p) for p in chrome_candidates):
        pytest.xfail("Headless Chrome/Edge not installed at standard Windows path")

    payload = {"markdown": "# Test PDF\n\nParagraph", "title": "TestPdf"}
    resp = requests.post(f"{server_url}/api/export-pdf", json=payload, timeout=15)
    assert resp.status_code < 500, f"Server error: {resp.text}"
    assert resp.status_code == 200
    assert len(resp.content) > 0


@pytest.mark.xfail(
    strict=True,
    reason="batch-convert crashes due to missing io and undefined converter in server.py",
)
def test_route_api_batch_convert(server_url):
    """POST /api/batch-convert converts multiple files and streams a ZIP."""
    files = [
        ("files", ("doc1.md", b"# Doc 1", "text/markdown")),
        ("files", ("doc2.md", b"# Doc 2", "text/markdown")),
    ]
    resp = requests.post(f"{server_url}/api/batch-convert", files=files, timeout=10)
    assert resp.status_code < 500, f"Expected non-500, got {resp.status_code}: {resp.text}"
    assert resp.status_code == 200
