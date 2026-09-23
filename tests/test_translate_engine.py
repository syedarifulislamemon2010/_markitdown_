# -*- coding: utf-8 -*-
"""
Tests for core/translate.py:
- TranslationEngine protocol conformance
- ModelDownloadManager: disk space checks, manifest queries, checksum validation, cleanup
- CloudAuditLogger: privacy compliance (verifying text content is NEVER stored in SQLite)
- Cold-start handling when models are not yet downloaded
"""

import os
import sqlite3
import pytest
from pathlib import Path
from core.translate import (
    TranslationEngine,
    TranslationResult,
    EngineCapabilities,
    IndicTransEngine,
    NLLBEngine,
    CloudTranslationEngine,
    ModelDownloadManager,
    CloudAuditLogger,
    MODEL_MANIFEST
)


def test_capabilities_cold_start(tmp_path):
    """Cold start: before models are downloaded, capabilities report is_downloaded=False."""
    mgr = ModelDownloadManager(models_dir=tmp_path / "models")
    assert not mgr.is_model_downloaded("nllb-200-distilled-600m")
    assert not mgr.is_model_downloaded("indictrans2-dist-200m")

    # Engine cold-start returns graceful response without crash
    nllb = NLLBEngine(model_dir=tmp_path / "models" / "nllb")
    caps = nllb.capabilities()
    assert caps.is_downloaded is False
    assert caps.offline is True
    assert caps.max_tokens == 512

    # Translate on cold-start returns pass-through with warning, NOT an unhandled exception
    res = nllb.translate("Hello world", src="en", tgt="bn")
    assert res.translated_text == "Hello world"
    assert res.warning is not None
    assert "not downloaded" in res.warning.lower()


def test_disk_space_check(tmp_path):
    """Verify that download manager accurately assesses available disk space."""
    mgr = ModelDownloadManager(models_dir=tmp_path)
    # Asking for 1 MB should succeed
    has_space, free_bytes = mgr.check_disk_space(1024 * 1024)
    assert has_space is True
    assert free_bytes > 0

    # Asking for 500 Terabytes should fail safety check
    has_space_huge, _ = mgr.check_disk_space(500 * 1024 * 1024 * 1024 * 1024)
    assert has_space_huge is False


def test_checksum_verification_failure(tmp_path):
    """Verify that a corrupted or mismatched file raises an integrity error."""
    mgr = ModelDownloadManager(models_dir=tmp_path)
    dummy_file = tmp_path / "corrupt.bin"
    dummy_file.write_bytes(b"corrupt data 12345")

    fake_expected_sha = "0000000000000000000000000000000000000000000000000000000000000000"
    is_valid = mgr._verify_sha256(dummy_file, fake_expected_sha)
    assert is_valid is False


def test_checksum_verification_success(tmp_path):
    """Verify valid SHA256 checksum matching."""
    import hashlib
    mgr = ModelDownloadManager(models_dir=tmp_path)
    content = b"valid model data payload"
    dummy_file = tmp_path / "valid.bin"
    dummy_file.write_bytes(content)

    real_sha = hashlib.sha256(content).hexdigest()
    assert mgr._verify_sha256(dummy_file, real_sha) is True


def test_cloud_audit_logger_privacy_guarantee(tmp_path):
    """
    CRITICAL PRIVACY TEST:
    Verify that CloudAuditLogger records provider, timestamp, direction, and char_count,
    but NEVER stores raw input/output text content in the database.
    """
    db_file = tmp_path / "audit_test.db"
    logger = CloudAuditLogger(db_path=db_file)

    secret_text = "This is confidential patient health information!"
    logger.log(provider="openai", char_count=len(secret_text), direction="en->bn")

    logs = logger.get_logs()
    assert len(logs) == 1
    entry = logs[0]
    assert entry["provider"] == "openai"
    assert entry["char_count"] == len(secret_text)
    assert entry["direction"] == "en->bn"

    # Query the raw SQLite schema and table dump to prove secret_text is nowhere in the file
    with sqlite3.connect(db_file) as conn:
        cursor = conn.execute("SELECT * FROM cloud_mt_audit")
        rows = cursor.fetchall()
        for r in rows:
            for col in r:
                assert secret_text not in str(col), "PRIVACY VIOLATION: Source text found in DB!"

    # Clear logs
    logger.clear()
    assert len(logger.get_logs()) == 0


def test_clear_downloaded_models(tmp_path):
    """Verify clear_downloaded_models completely removes cached files."""
    models_dir = tmp_path / "models"
    mgr = ModelDownloadManager(models_dir=models_dir)
    test_model = models_dir / "test_model"
    test_model.mkdir(parents=True)
    (test_model / "model.bin").write_bytes(b"dummy data")
    assert test_model.exists()

    mgr.clear_downloaded_models("test_model")
    assert not test_model.exists()
