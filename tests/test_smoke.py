# -*- coding: utf-8 -*-
"""Smoke tests verifying every route in desktop/server.py returns non-500."""

import io
import os
import zipfile
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


def test_route_api_batch_convert_two_valid(server_url):
    """POST /api/batch-convert with 2 valid files returns 200 and ZIP with 2 .md files."""
    files = [
        ("files", ("doc1.md", b"# Doc 1\n\nFirst document", "text/markdown")),
        ("files", ("doc2.md", b"# Doc 2\n\nSecond document", "text/markdown")),
    ]
    resp = requests.post(f"{server_url}/api/batch-convert", files=files, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.headers.get("Content-Type") == "application/zip"

    with zipfile.ZipFile(io.BytesIO(resp.content), "r") as zf:
        namelist = zf.namelist()
        assert "doc1.md" in namelist
        assert "doc2.md" in namelist
        assert "_errors.txt" not in namelist
        doc1_content = zf.read("doc1.md").decode("utf-8")
        assert "First document" in doc1_content


def test_route_api_batch_convert_one_valid_one_corrupt(server_url):
    """POST /api/batch-convert with 1 valid + 1 corrupt file returns 200 and ZIP with 1 .md + _errors.txt."""
    files = [
        ("files", ("valid.md", b"# Valid\n\nValid markdown content", "text/markdown")),
        ("files", ("corrupted.pdf", b"\x00\x01\x02\xff\xfe", "application/pdf")),
    ]
    resp = requests.post(f"{server_url}/api/batch-convert", files=files, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.headers.get("Content-Type") == "application/zip"

    with zipfile.ZipFile(io.BytesIO(resp.content), "r") as zf:
        namelist = zf.namelist()
        assert "valid.md" in namelist
        assert "_errors.txt" in namelist
        errors_text = zf.read("_errors.txt").decode("utf-8")
        assert "corrupted.pdf" in errors_text


def test_route_api_batch_convert_zero_files(server_url):
    """POST /api/batch-convert with 0 files returns 400 Bad Request."""
    resp = requests.post(f"{server_url}/api/batch-convert", data={}, timeout=10)
    assert resp.status_code == 400
    data = resp.json()
    assert data.get("success") is False
    assert "No files" in data.get("error", "")


def test_route_api_batch_progress(server_url):
    """GET /api/batch-progress/<id> returns progress JSON."""
    resp = requests.get(f"{server_url}/api/batch-progress/test-batch-123", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data
    assert "total" in data
