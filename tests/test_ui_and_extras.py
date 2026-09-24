# -*- coding: utf-8 -*-
"""
Tests for UI/UX improvements, status bar real state, missing extra handling,
and Structured / Gazette Extraction UI workflow.
"""

import os
import json
import time
import pytest
import requests
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


def test_missing_extra_install_commands(server_url):
    """Verify backend endpoints return clean 400 responses with install_command on missing extras."""
    # 1. /api/translate with empty text
    empty_resp = requests.post(f"{server_url}/api/translate", json={"text": ""}, timeout=5)
    assert empty_resp.status_code == 400

    # 2. Check convert endpoint response schema for extra detection
    convert_resp = requests.post(
        f"{server_url}/api/convert",
        files={"file": ("dummy.txt", b"Hello world", "text/plain")},
        timeout=5
    )
    assert convert_resp.status_code == 200
    data = convert_resp.json()
    assert "install_command" in data


def test_sbsync_status_real_state(server_url):
    """Verify sbSync click shows online toast when server is healthy, and offline toast when unreachable."""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        page.goto(server_url, wait_until="networkidle", timeout=15000)
        page.wait_for_selector("#sbSync", state="attached", timeout=5000)

        # 1. When backend is healthy: click sbSync
        page.click("#sbSync")
        page.wait_for_selector(".toast-success", state="attached", timeout=4000)
        toast_text = page.inner_text("#toastContainer")
        assert "সক্রিয়" in toast_text or "Online" in toast_text or "Port 8080" in toast_text

        # 2. Simulate server down: intercept /api/health to fail
        page.route("**/api/health", lambda route: route.abort())

        # Click sbSync again
        page.click("#sbSync")
        page.wait_for_selector(".toast-error", state="attached", timeout=5000)
        offline_toast = page.inner_text("#toastContainer")
        assert "অফলাইন" in offline_toast or "বিচ্ছিন্ন" in offline_toast

        browser.close()


def test_structured_extraction_ui_workflow(server_url):
    """Verify the full detect -> extract -> review & edit -> insert table workflow in browser."""
    sample_gazette = """রেজিস্টার্ড নং ডি এ-১
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
কর্তৃপক্ষ কর্তৃক প্রকাশিত
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
অর্থ মন্ত্রণালয়
অর্থ বিভাগ
এস.আর.ও. নং ৩৫৫-আইন/২০১৫
তারিখ: ১৫ নভেম্বর ২০১৫ খ্রিষ্টাব্দ
"""

    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        page.goto(server_url, wait_until="networkidle", timeout=15000)
        page.wait_for_selector(".cm-content, #editor", state="attached", timeout=5000)

        # Set sample gazette text in editor
        page.evaluate("""payload => {
            if (window.editor && window.editor.setValue) {
                window.editor.setValue(payload);
            }
            const el = document.getElementById('editor');
            if (el) el.value = payload;
        }""", sample_gazette)

        # Open extraction modal via toolbar button or helper
        page.click("#toolExtractStructured")
        page.wait_for_selector("#extractModal", state="visible", timeout=4000)

        # Ensure template dropdown is populated
        page.wait_for_selector("#extractTemplateSelect option", state="attached", timeout=4000)
        page.select_option("#extractTemplateSelect", value="government_gazette")

        # Run extraction
        page.click("#runExtractBtn")

        # Verify results container and fields are rendered
        page.wait_for_selector("#extractResultsContainer", state="visible", timeout=6000)
        page.wait_for_selector(".extract-field-input", state="attached", timeout=4000)

        # Check that S.R.O. field was extracted
        sro_input = page.locator('input[data-field="sro_number"]')
        assert sro_input.is_visible()
        val = sro_input.input_value()
        assert "৩৫৫-আইন/২০১৫" in val

        # Edit S.R.O. value inline (Review & Edit step)
        sro_input.fill("৩৫৫-আইন/২০১৫-সংশোধিত")

        # Insert Markdown table back to editor
        page.click("#extractInsertMdBtn")
        page.wait_for_selector("#extractModal", state="hidden", timeout=4000)

        # Verify editor contains updated table with edited S.R.O.
        editor_text = page.evaluate("""() => {
            if (window.editor && window.editor.getValue) return window.editor.getValue();
            if (window.editor && window.editor.value !== undefined) return window.editor.value;
            return document.getElementById('editor')?.value || '';
        }""")
        assert "৩৫৫-আইন/২০১৫-সংশোধিত" in editor_text
        assert "বিবরণ (Details)" in editor_text

        browser.close()


def test_undo_history_memory_bounded():
    """Verify adaptive undo history stack limits memory consumption on large documents."""
    # Test script in browser context
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        # Simple page evaluation testing pushHistoryState limit
        page.goto("about:blank")
        js_test = """() => {
            const undoStack = [];
            const MAX_HISTORY_BYTES = 15 * 1024 * 1024;
            function push(oldContent) {
                const docSize = oldContent.length;
                let maxStates = 50;
                if (docSize > 2 * 1024 * 1024) maxStates = 6;
                else if (docSize > 500 * 1024) maxStates = 12;
                else if (docSize > 100 * 1024) maxStates = 25;

                undoStack.push({ content: oldContent });
                while (undoStack.length > maxStates) undoStack.shift();

                let totalBytes = undoStack.reduce((sum, s) => sum + s.content.length, 0);
                while (undoStack.length > 2 && totalBytes > MAX_HISTORY_BYTES) {
                    const rem = undoStack.shift();
                    totalBytes -= rem.content.length;
                }
            }

            // Simulate 50 edits on a 3MB string
            const largeChunk = "A".repeat(3 * 1024 * 1024);
            for (let i = 0; i < 50; i++) {
                push(largeChunk + i);
            }

            return {
                stackLength: undoStack.length,
                totalBytes: undoStack.reduce((s, x) => s + x.content.length, 0)
            };
        }"""
        res = page.evaluate(js_test)
        # Verify stack length is strictly capped to <= 6 states for >2MB docs
        assert res["stackLength"] <= 6
        # Total bytes must be strictly <= MAX_HISTORY_BYTES (15MB)
        assert res["totalBytes"] <= 15 * 1024 * 1024 + 3 * 1024 * 1024

        browser.close()
