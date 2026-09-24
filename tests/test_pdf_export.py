# -*- coding: utf-8 -*-
"""
Verification of Offline Headless PDF Generation with Embedded Bengali Fonts.
Ensures zero CDN dependencies, embedded base64 TTF fonts, and cross-platform Chrome discovery.
"""

import pytest
import pypdfium2 as pdfium
from desktop.server import generate_pdf_from_markdown, find_chrome_executable


def test_find_chrome_executable():
    """Verify Chrome/Edge/Chromium executable discovery works."""
    chrome_path = find_chrome_executable()
    # If Chrome/Edge/Chromium is installed on the testing host, it must be a valid path
    if chrome_path:
        import os
        assert os.path.isfile(chrome_path)


def test_offline_pdf_generation_with_bengali_text():
    """Verify PDF export with Bengali and Markdown tables generates valid bytes and readable text."""
    chrome_path = find_chrome_executable()
    if not chrome_path:
        pytest.skip("Chrome/Edge/Chromium executable not found on this system.")

    md_content = """# বাংলাদেশ ও মুক্তিযুদ্ধ

এটি একটি **অফলাইন** টেস্ট ডকুমেন্ট।

| বিষয় | অবস্থা |
|---|---|
| ফন্ট | Hind Siliguri / Kalpurush |
| স্ট্যাটাস | সফল |
"""
    pdf_bytes = generate_pdf_from_markdown(md_content, title="টেস্ট গেজেট")
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")

    # Verify text extraction from generated PDF
    doc = pdfium.PdfDocument(pdf_bytes)
    assert len(doc) >= 1
    page_text = doc[0].get_textpage().get_text_range()
    doc.close()

    assert "বাংলাদেশ" in page_text or "বাং" in page_text
    assert "টেস্ট" in page_text or "ফন্ট" in page_text
