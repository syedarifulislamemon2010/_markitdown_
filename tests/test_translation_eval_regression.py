# -*- coding: utf-8 -*-
"""Regression test for MT accuracy baseline."""
import json
import pytest
from pathlib import Path

BASELINE_PATH = Path(__file__).parent / "accuracy_baseline_mt.json"


def test_mt_accuracy_regression_baseline():
    """Verify that MT accuracy does not regress beyond documented tolerance."""
    assert BASELINE_PATH.exists(), "accuracy_baseline_mt.json not found"
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    tolerance = data.get("regression_tolerance_chrf", 0.5)
    assert 0 < tolerance <= 1.0
    models = data.get("models", {})
    assert len(models) >= 4

    # Verify baseline properties
    for m_name, metrics in models.items():
        assert metrics["flores_bn_en_chrf"] >= 45.0, f"Unacceptably low chrF++ on {m_name}"
        assert metrics["flores_bn_en_bleu"] >= 20.0, f"Unacceptably low BLEU on {m_name}"

    # Verify Rule 10: IndicTrans2 INT8 delta vs FP32 <= 2.0 chrF++
    it_fp32 = models["IndicTrans2-FP32"]["flores_bn_en_chrf"]
    it_int8 = models["IndicTrans2-INT8"]["flores_bn_en_chrf"]
    delta = it_fp32 - it_int8
    assert delta <= 2.0, f"Rule 10 violation: INT8 degradation {delta:.2f} exceeds 2.0 chrF++"
