# -*- coding: utf-8 -*-
"""
Tests for server.py Machine Translation routes:
- GET /api/translate/capabilities
- POST /api/translate
- GET /api/translate/audit-logs
- POST /api/translate/audit-logs/clear
- POST /api/translate/tm/store
- POST /api/translate/clear
"""

import requests


def test_api_translate_capabilities(server_url):
    """Verify /api/translate/capabilities returns engine statuses and required badges."""
    resp = requests.get(
        f"{server_url}/api/translate/capabilities",
        timeout=5.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "AI অনুবাদ — যাচাই করুন" in data["disclaimer_badge"]
    assert "chunk" in data["chunking_notice"].lower()
    assert len(data["engines"]) >= 3

    engine_ids = [e["id"] for e in data["engines"]]
    assert "indictrans2" in engine_ids
    assert "nllb" in engine_ids
    assert "cloud" in engine_ids


def test_api_translate_endpoint(server_url):
    """Verify /api/translate handles Bengali and English translation requests."""
    payload = {
        "text": "The meeting will start soon. Section 5 অনুযায়ী প্রযোজ্য হবে।",
        "action": "to_bengali",
        "engine": "indictrans2",
        "scope": "document"
    }
    resp = requests.post(
        f"{server_url}/api/translate",
        json=payload,
        timeout=10.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "translated_text" in data
    assert "disclaimer_badge" in data
    assert "AI অনুবাদ — যাচাই করুন" in data["disclaimer_badge"]


def test_api_translate_tm_store(server_url):
    """Verify /api/translate/tm/store saves approved translation pair."""
    payload = {
        "source": "Knowledge is power.",
        "target": "জ্ঞানই শক্তি।",
        "direction": "en->bn"
    }
    resp = requests.post(
        f"{server_url}/api/translate/tm/store",
        json=payload,
        timeout=5.0,
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_api_translate_audit_logs(server_url):
    """Verify /api/translate/audit-logs and clear."""
    resp = requests.get(
        f"{server_url}/api/translate/audit-logs",
        timeout=5.0,
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    clear_resp = requests.post(
        f"{server_url}/api/translate/audit-logs/clear",
        timeout=5.0,
    )
    assert clear_resp.status_code == 200
    assert clear_resp.json()["success"] is True
