# -*- coding: utf-8 -*-
"""Credential Security and Storage verification tests.

Verifies:
1. Gemini API key is transmitted via x-goog-api-key header and never in URL query parameter.
2. Server configuration persistence never writes plaintext API keys to repository root.
3. Desktop keyring / secure credential bridge functions correctly and clears keys reliably.
4. Browser mode UI stores API keys strictly in-memory (window.__MEMORY_KEYS__) and NEVER in localStorage.
5. Eye toggle buttons properly toggle password field masking.
6. Clear Keys button completely purges stored keys and UI fields.
"""

import json
import os
import unittest.mock as mock
from pathlib import Path
from PIL import Image
import pytest
from playwright.sync_api import sync_playwright

from core.ocr import _ocr_via_gemini
from desktop.server import get_studio_config, save_studio_config, CONFIG_FILE
from desktop.run_studio import secure_get_key, secure_set_key, secure_clear_keys


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


def test_gemini_key_in_header_not_query_url():
    """Verify Gemini API key is in HTTP header x-goog-api-key and NEVER in query string."""
    img = Image.new("RGB", (10, 10), color="white")
    fake_key = "AIzaSySecretTestKey98765"

    fake_response = mock.MagicMock()
    fake_response.read.return_value = json.dumps({
        "candidates": [{"content": {"parts": [{"text": "Extracted Header Test"}]}}]
    }).encode("utf-8")
    fake_response.__enter__.return_value = fake_response

    captured_req = None

    def fake_urlopen(req, timeout=None):
        nonlocal captured_req
        captured_req = req
        return fake_response

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        res = _ocr_via_gemini(img, api_key=fake_key)

    assert res == "Extracted Header Test"
    assert captured_req is not None
    # Verify key is strictly in headers
    assert captured_req.get_header("X-goog-api-key") == fake_key
    # Verify key is NOT leaked in the URL query string
    assert "key=" not in captured_req.full_url
    assert fake_key not in captured_req.full_url


def test_server_config_does_not_persist_secret_keys():
    """Verify save_studio_config and get_studio_config never store API keys in repo root."""
    test_payload = {
        "provider": "custom_provider",
        "openai_base_url": "https://custom.api.test/v1",
        "openai_model": "test-model-4",
        "openai_key": "sk-super-secret-key-12345",
        "gemini_key": "AIzaSyConfidentialKey999",
    }
    saved = save_studio_config(test_payload)

    # Returned saved config must not include secret keys
    assert "openai_key" not in saved
    assert "gemini_key" not in saved

    # Physical file on disk must not contain secrets
    if CONFIG_FILE.exists():
        raw_content = CONFIG_FILE.read_text(encoding="utf-8")
        assert "sk-super-secret-key-12345" not in raw_content
        assert "AIzaSyConfidentialKey999" not in raw_content

    # get_studio_config must never load secret keys
    cfg = get_studio_config()
    assert "openai_key" not in cfg
    assert "gemini_key" not in cfg


def test_secure_keyring_bridge():
    """Verify secure_set_key, secure_get_key, and secure_clear_keys operate cleanly."""
    try:
        # 1. Set key
        set_res = secure_set_key("openai", "sk-test-keyring-val")
        assert set_res is True

        # 2. Retrieve key
        val = secure_get_key("openai")
        assert val == "sk-test-keyring-val"

        # 3. Clear keys
        clr_res = secure_clear_keys()
        assert clr_res is True

        # 4. Verify cleared
        assert secure_get_key("openai") == ""
    finally:
        secure_clear_keys()


def test_frontend_in_memory_keys_and_zero_localstorage(server_url):
    """Playwright verification of browser-mode in-memory keys and zero localStorage exposure."""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()

        page.goto(server_url, wait_until="networkidle", timeout=15000)
        page.wait_for_selector("#settingsBtn", timeout=5000)

        # 1. Open Settings Modal
        page.click("#settingsBtn")
        page.wait_for_selector("#settingsModal.active", timeout=3000)

        # 2. In browser mode, verify browser warning banner is visible
        assert page.is_visible("#browserModeKeyWarning")
        assert not page.is_visible("#desktopKeyringNotice")

        # 3. Test eye toggles
        key_input = page.locator("#openaiKeyInput")
        assert key_input.get_attribute("type") == "password"
        page.click("#toggleApiKeyVisibility")
        assert key_input.get_attribute("type") == "text"
        page.click("#toggleApiKeyVisibility")
        assert key_input.get_attribute("type") == "password"

        gemini_input = page.locator("#geminiKeyInput")
        assert gemini_input.get_attribute("type") == "password"
        page.click("#toggleGeminiKeyVisibility")
        assert gemini_input.get_attribute("type") == "text"
        page.click("#toggleGeminiKeyVisibility")
        assert gemini_input.get_attribute("type") == "password"

        # 4. Enter test API keys
        test_openai = "sk-live-test-browser-inmemory-key"
        test_gemini = "AIzaSyLiveBrowserInMemoryKey"
        key_input.fill(test_openai)
        gemini_input.fill(test_gemini)

        # 5. Save Settings
        page.click("#saveSettingsBtn")
        page.wait_for_selector("#settingsModal", state="hidden", timeout=3000)

        # 6. Verify ZERO storage in localStorage
        ls_openai = page.evaluate("localStorage.getItem('markitdown_openai_key')")
        ls_gemini = page.evaluate("localStorage.getItem('markitdown_gemini_key')")
        assert ls_openai is None
        assert ls_gemini is None

        # 7. Verify storage in memory (window.__MEMORY_KEYS__)
        mem_openai = page.evaluate("window.__MEMORY_KEYS__.openai")
        mem_gemini = page.evaluate("window.__MEMORY_KEYS__.gemini")
        assert mem_openai == test_openai
        assert mem_gemini == test_gemini

        # 8. Re-open settings modal and verify values are populated from secure store
        page.click("#settingsBtn")
        page.wait_for_selector("#settingsModal.active", timeout=3000)
        assert page.input_value("#openaiKeyInput") == test_openai
        assert page.input_value("#geminiKeyInput") == test_gemini

        # 9. Click "Clear Keys" button
        page.click("#clearApiKeysBtn")

        # 10. Verify inputs and in-memory store are completely purged
        assert page.input_value("#openaiKeyInput") == ""
        assert page.input_value("#geminiKeyInput") == ""
        assert page.evaluate("window.__MEMORY_KEYS__.openai") == ""
        assert page.evaluate("window.__MEMORY_KEYS__.gemini") == ""

        browser.close()
