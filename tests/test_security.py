# -*- coding: utf-8 -*-
"""Security verification tests for MarkItDown Studio backend.

Validates:
1. Removal of wildcard CORS and enforcement of localhost-only origins.
2. Security response headers (X-Content-Type-Options, X-Frame-Options, Content-Security-Policy).
3. Per-launch session token enforcement on /api/* routes except /api/health (403 on missing/invalid).
4. Payload size limit (MEMFILE_MAX 100MB, 413 on oversized requests).
5. Automatic token injection in root index.html.
"""

import os
import requests


def test_security_headers(server_url):
    """Responses must include nosniff, frame DENY, and strict CSP."""
    resp = requests.get(f"{server_url}/api/health", timeout=5)
    assert resp.status_code == 200

    # 1. No sniff
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    # 2. Clickjacking protection
    assert resp.headers.get("X-Frame-Options") == "DENY"

    # 3. Content Security Policy
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "default-src 'self' 'unsafe-inline'" in csp
    assert "script-src 'self' 'unsafe-inline'" in csp
    assert "img-src 'self' data: blob:" in csp
    assert "font-src 'self' data:" in csp
    assert "connect-src 'self'" in csp


def test_cors_no_wildcard(server_url):
    """Wildcard CORS must NOT be present; evil origins must be denied."""
    # Request without origin
    resp = requests.get(f"{server_url}/api/health", timeout=5)
    assert resp.headers.get("Access-Control-Allow-Origin") != "*"

    # Request from untrusted external origin
    resp_evil = requests.get(
        f"{server_url}/api/health",
        headers={"Origin": "http://evil-attacker.com"},
        timeout=5,
    )
    assert resp_evil.headers.get("Access-Control-Allow-Origin") != "*"
    assert resp_evil.headers.get("Access-Control-Allow-Origin") != "http://evil-attacker.com"

    # Request from trusted localhost origin
    resp_local = requests.get(
        f"{server_url}/api/health",
        headers={"Origin": "http://127.0.0.1:8080"},
        timeout=5,
    )
    assert resp_local.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:8080"

    # Request from null origin (sandboxed iframe / untrusted context) must be denied
    resp_null = requests.get(
        f"{server_url}/api/health",
        headers={"Origin": "null"},
        timeout=5,
    )
    assert resp_null.headers.get("Access-Control-Allow-Origin") is None


def test_session_token_enforcement(monkeypatch, server_url):
    """When STUDIO_SESSION_TOKEN is configured, /api/* routes reject missing/invalid tokens with 403."""
    test_token = "studio-sec-tok-9988776655"
    monkeypatch.setenv("STUDIO_SESSION_TOKEN", test_token)

    # 1. Health endpoint remains public/exempt
    health_resp = requests.get(f"{server_url}/api/health", timeout=5)
    assert health_resp.status_code == 200

    # 2. Protected endpoint with no token -> 403
    resp_no_token = requests.post(f"{server_url}/api/convert", timeout=5)
    assert resp_no_token.status_code == 403
    data_no_tok = resp_no_token.json()
    assert data_no_tok.get("success") is False
    assert "Forbidden" in data_no_tok.get("error", "")

    # 3. Protected endpoint with invalid token -> 403
    resp_bad_token = requests.post(
        f"{server_url}/api/convert",
        headers={"X-Session-Token": "completely-wrong-token"},
        timeout=5,
    )
    assert resp_bad_token.status_code == 403

    # 4. Protected endpoint with valid token -> 400 (bad request due to missing file, not 403)
    resp_valid_token = requests.post(
        f"{server_url}/api/convert",
        headers={"X-Session-Token": test_token},
        timeout=5,
    )
    assert resp_valid_token.status_code == 400
    assert resp_valid_token.status_code != 403


def test_payload_limit_enforcement(server_url):
    """Requests exceeding MEMFILE_MAX must return 413 Payload Too Large."""
    # Simulate oversized payload via Content-Length header
    oversized_length = 105 * 1024 * 1024  # 105MB > 100MB limit
    resp = requests.post(
        f"{server_url}/api/convert",
        headers={"Content-Length": str(oversized_length)},
        timeout=5,
    )
    assert resp.status_code == 413
    data = resp.json()
    assert data.get("success") is False
    assert "Payload Too Large" in data.get("error", "")


def test_root_token_injection(monkeypatch, server_url):
    """Root GET / dynamically injects the session token into window.__STUDIO_TOKEN__."""
    test_token = "token-injection-check-12345"
    monkeypatch.setenv("STUDIO_SESSION_TOKEN", test_token)

    resp = requests.get(f"{server_url}/", timeout=5)
    assert resp.status_code == 200
    assert f'window.__STUDIO_TOKEN__ = "{test_token}";' in resp.text
