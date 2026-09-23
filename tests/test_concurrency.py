# -*- coding: utf-8 -*-
"""
Concurrency and thread-safety tests for MarkItDown Studio.
Verifies that 20 parallel requests with different API keys experience zero cross-contamination.
"""

import time
import concurrent.futures
from desktop.server import get_converter


def test_concurrent_converter_config_isolation():
    """Verify that 20 parallel calls with unique API credentials get completely isolated converters."""
    num_threads = 20
    results = {}

    def worker(worker_id: int):
        fake_key = f"sk-test-fake-key-thread-{worker_id:02d}-{time.time()}"
        fake_base_url = f"https://api.relay-{worker_id:02d}.local/v1"
        fake_model = f"custom-model-{worker_id:02d}"

        # Get converter with thread-specific parameters
        conv = get_converter(
            openai_api_key=fake_key,
            openai_base_url=fake_base_url,
            llm_model=fake_model,
        )

        # Sleep slightly to allow other threads to interleave and potentially overwrite shared state
        time.sleep(0.01)

        # Verify converter preserves EXACT caller credentials without leakage
        return {
            "worker_id": worker_id,
            "expected_key": fake_key,
            "actual_key": conv.openai_api_key,
            "expected_url": fake_base_url,
            "actual_url": conv.openai_base_url,
            "expected_model": fake_model,
            "actual_model": conv.llm_model,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, i) for i in range(num_threads)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            results[res["worker_id"]] = res

    assert len(results) == num_threads
    for wid, r in results.items():
        assert r["actual_key"] == r["expected_key"], (
            f"Cross-contamination detected for worker {wid}! Expected {r['expected_key']}, got {r['actual_key']}"
        )
        assert r["actual_url"] == r["expected_url"], (
            f"URL contamination for worker {wid}! Expected {r['expected_url']}, got {r['actual_url']}"
        )
        assert r["actual_model"] == r["expected_model"], (
            f"Model contamination for worker {wid}! Expected {r['expected_model']}, got {r['actual_model']}"
        )


def test_ocr_capabilities_endpoint(server_url):
    """Test /api/ocr-capabilities endpoint response schema."""
    import requests
    resp = requests.get(f"{server_url}/api/ocr-capabilities", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "platform" in data
    assert "winocr_available" in data
    assert "tesseract_available" in data
    assert "has_offline_bengali" in data
    assert "helper_instructions" in data
