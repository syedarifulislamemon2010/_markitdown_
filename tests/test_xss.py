# -*- coding: utf-8 -*-
"""XSS Neutralization and Sanitization verification tests using Playwright.

Verifies:
1. Malicious payloads (<script>, <img onerror>, <svg onload>, [x](javascript:)) are neutralized.
2. Mermaid click callbacks cannot execute code (securityLevel: 'strict').
3. Legitimate KaTeX math formulas and Mermaid diagrams continue to render correctly.
"""

import os
import time
import pytest
from playwright.sync_api import sync_playwright


def get_browser(p):
    """Find and launch Chrome/Edge executable or default Playwright browser."""
    candidates = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return p.chromium.launch(headless=True, executable_path=c)
            except Exception:
                continue
    try:
        return p.chromium.launch(headless=True)
    except Exception as e:
        pytest.skip(f"No headless browser available: {e}")


def test_xss_payloads_neutralized(server_url):
    """Verify script, img onerror, svg onload, and javascript: links are neutralized."""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        # Listen for any unexpected JavaScript alert/dialog
        dialogs = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

        page.goto(server_url, wait_until="networkidle", timeout=15000)

        # Wait for editor to be interactive
        page.wait_for_selector(".cm-content, #editor", state="attached", timeout=5000)

        # 1. Test <script> injection
        script_payload = '<script>window.__XSS_SCRIPT__ = true; alert("xss-script");</script>'
        page.evaluate("payload => { editor.value = payload; }", script_payload)
        page.evaluate("renderMarkdown()")
        time.sleep(0.3)

        assert page.evaluate("window.__XSS_SCRIPT__") is None
        assert not any("xss-script" in d for d in dialogs)

        # 2. Test <img onerror> injection
        img_payload = '<img src="nonexistent.png" onerror="window.__XSS_IMG__ = true; alert(\'xss-img\');">'
        page.evaluate("payload => { editor.value = payload; }", img_payload)
        page.evaluate("renderMarkdown()")
        time.sleep(0.5)

        assert page.evaluate("window.__XSS_IMG__") is None
        assert not any("xss-img" in d for d in dialogs)

        # 3. Test <svg onload> injection
        svg_payload = '<svg onload="window.__XSS_SVG__ = true; alert(\'xss-svg\');"><circle r=10/></svg>'
        page.evaluate("payload => { editor.value = payload; }", svg_payload)
        page.evaluate("renderMarkdown()")
        time.sleep(0.3)

        assert page.evaluate("window.__XSS_SVG__") is None
        assert not any("xss-svg" in d for d in dialogs)

        # 4. Test [click](javascript:...) link injection
        link_payload = '[Malicious Link](javascript:window.__XSS_LINK__=true;alert("xss-link"))'
        page.evaluate("payload => { editor.value = payload; }", link_payload)
        page.evaluate("renderMarkdown()")
        time.sleep(0.3)

        # In DOMPurify, javascript: href is completely stripped
        bad_links = page.query_selector_all('#previewContent a[href^="javascript:"]')
        assert len(bad_links) == 0

        # Overall dialog assertion
        assert len(dialogs) == 0, f"XSS alerts were triggered: {dialogs}"

        browser.close()


def test_katex_and_mermaid_render_cleanly(server_url):
    """Verify that legitimate KaTeX math formulas and Mermaid charts render correctly."""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        page.goto(server_url, wait_until="networkidle", timeout=15000)
        page.wait_for_selector(".cm-content, #editor", state="attached", timeout=5000)

        # Math formula and safe mermaid diagram
        safe_markdown = """# Safe Document

$$E = mc^2$$

Inline formula: $a^2 + b^2 = c^2$.

```mermaid
graph LR
    Start --> Stop
```
"""
        page.evaluate("payload => { editor.value = payload; }", safe_markdown)
        page.evaluate("renderMarkdown()")
        time.sleep(0.8)

        # 1. Verify KaTeX rendered
        katex_block = page.query_selector("#previewContent .katex-block, #previewContent .katex")
        assert katex_block is not None, "KaTeX formula did not render into .katex"

        # 2. Verify Mermaid chart rendered into SVG or container
        mermaid_chart = page.query_selector("#previewContent .mermaid-chart")
        assert mermaid_chart is not None, "Mermaid chart container not found"

        browser.close()


def test_mermaid_click_callbacks_neutralized(server_url):
    """Verify that Mermaid click callbacks cannot execute code under strict security."""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        dialogs = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

        page.goto(server_url, wait_until="networkidle", timeout=15000)
        page.wait_for_selector(".cm-content, #editor", state="attached", timeout=5000)

        # Mermaid payload with click callback attempt
        mermaid_callback_payload = """```mermaid
graph TD
    NodeA[Click Test] --> NodeB
    click NodeA "javascript:alert('mermaid-click')" "Call tooltip"
```
"""
        page.evaluate("payload => { editor.value = payload; }", mermaid_callback_payload)
        page.evaluate("renderMarkdown()")
        time.sleep(0.8)

        # Click the node if rendered as link or shape
        node = page.query_selector("#previewContent .mermaid-chart a, #previewContent .mermaid-chart .node")
        if node:
            node.click()
            time.sleep(0.3)

        assert len(dialogs) == 0, f"Mermaid click callback triggered dialog: {dialogs}"
        browser.close()
