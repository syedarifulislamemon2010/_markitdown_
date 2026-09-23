# -*- coding: utf-8 -*-
"""Verification tests for Phonetic Engine loading and AI API Key configuration."""

import json
import unittest.mock as mock
import pytest
import requests
from playwright.sync_api import sync_playwright

from desktop.run_studio import secure_get_key, secure_set_key, secure_clear_keys
from tests.test_credentials import get_browser


def test_api_settings_and_secure_persistence(server_url):
    """Verify /api/settings securely stores keys in keyring/credentials and server AI routes can access them."""
    test_key = "sk-test-ai-key-secure-12345"
    test_gemini = "AIzaSyTestGeminiKey99988"

    try:
        # POST settings with keys (Connection: close to prevent WSGI socket contention)
        resp = requests.post(
            f"{server_url}/api/settings",
            json={
                "openai_key": test_key,
                "gemini_key": test_gemini,
                "provider": "openai",
                "openai_model": "gpt-4o",
            },
            headers={"Connection": "close"},
            timeout=5,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True

        # Verify keys are in secure keyring store
        assert secure_get_key("openai") == test_key
        assert secure_get_key("gemini") == test_gemini

        # Verify GET /api/settings reports keys exist without leaking raw secrets
        get_resp = requests.get(
            f"{server_url}/api/settings",
            headers={"Connection": "close"},
            timeout=5,
        )
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data.get("has_openai_key") is True
        assert get_data.get("has_gemini_key") is True
        assert "openai_key" not in get_data.get("config", {})
        assert "gemini_key" not in get_data.get("config", {})

    finally:
        secure_clear_keys()


def test_api_ai_action_with_gemini(server_url):
    """Verify /api/ai-action routes to Gemini REST API when provider is gemini."""
    fake_gemini_key = "AIzaSyFakeKeyForTest123"
    fake_resp_body = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "সফল অনুবাদ সম্পন্ন হয়েছে"}
                    ]
                }
            }
        ]
    }

    mock_resp = mock.MagicMock()
    mock_resp.read.return_value = json.dumps(fake_resp_body).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    captured_req = None

    def fake_urlopen(req, timeout=None):
        nonlocal captured_req
        captured_req = req
        return mock_resp

    with mock.patch("desktop.server.urllib.request.urlopen", side_effect=fake_urlopen), \
         mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        resp = requests.post(
            f"{server_url}/api/ai-action",
            json={
                "action": "polish",
                "text": "amader desh bangladesh",
                "api_key": fake_gemini_key,
                "provider": "gemini",
                "model": "gemini-1.5-flash",
            },
            timeout=5,
        )

    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json.get("success") is True
    assert res_json.get("result") == "সফল অনুবাদ সম্পন্ন হয়েছে"
    assert captured_req is not None
    assert captured_req.get_header("X-goog-api-key") == fake_gemini_key
    assert "generativelanguage.googleapis.com" in captured_req.full_url


def test_phonetic_engine_loaded_in_browser(server_url):
    """Verify Phonetic engine script is loaded, window.PhoneticBangla is available, and toggles without error."""
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.new_page()
        try:
            page.goto(server_url, wait_until="networkidle", timeout=15000)

            # 1. Verify window.PhoneticBangla exists on window
            has_phonetic = page.evaluate("() => typeof window.PhoneticBangla !== 'undefined'")
            assert has_phonetic is True, "window.PhoneticBangla was not loaded by index.html"

            # 2. Click the Phonetic toggle button in toolbar
            page.wait_for_selector("#toolPhoneticBangla", timeout=5000)
            page.click("#toolPhoneticBangla")

            # 3. Verify it is now enabled
            is_enabled = page.evaluate("() => window.PhoneticBangla.isEnabled")
            assert is_enabled is True, "PhoneticBangla failed to enable on button click"

            # 4. Verify toast does NOT contain error 'লোড হয়নি'
            toast_text = page.locator("#toastContainer").inner_text()
            assert "লোড হয়নি" not in toast_text
            assert "ফোনেটিক বাংলা: চালু" in toast_text or "সক্রিয়" in toast_text or "অন" in page.locator("#toolPhoneticBangla").inner_text()

            # 5. Verify transliteration parse works
            transliterated = page.evaluate("() => window.PhoneticBangla.parse('amader bangladesh')")
            assert "আমাদের" in transliterated
        finally:
            page.close()
            browser.close()
