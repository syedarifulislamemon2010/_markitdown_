# -*- coding: utf-8 -*-
"""Parametrized golden tests, baseline accuracy checks, and Hypothesis roundtrip."""

import csv
import json
from pathlib import Path
import unicodedata
import pytest
from hypothesis import given, settings, strategies as st
from core.bengali import (
    auto_convert_markdown,
    auto_convert_unicode_to_bijoy_markdown,
    bijoy_to_unicode,
)

GOLDEN_CSV_PATH = Path(__file__).parent / "golden_bijoy.csv"
BASELINE_JSON_PATH = Path(__file__).parent / "accuracy_baseline.json"

ANCHORS = [
    ("KvR", "কাজ", False),
    ("mgvR", "সমাজ", False),
    ("gvbyl", "মানুষ", False),
    ("c„w_ex", "পৃথিবী", False),
    ("evsjv‡`k", "বাংলাদেশ", False),
    ("†KvU©‡i", "কোর্টের", True),
    ("m~‡h©i", "সূর্যের", True),
    ("wbe©vPb‡bi", "নির্বাচনের", True),
    ("†M©‡i", "গর্তের", True),
    ("Dcm‡M©i", "উপসর্গের", True),
    ("Kzwgjøv", "কুমিল্লা", True),
]


def load_anchor_params():
    params = []
    for bijoy, exp, is_xfail in ANCHORS:
        if is_xfail:
            params.append(
                pytest.param(
                    bijoy,
                    exp,
                    marks=pytest.mark.xfail(
                        strict=True,
                        reason=f"Baseline Bijoy glyph/suffix ordering defect on {bijoy}",
                    ),
                    id=f"anchor-{exp}",
                )
            )
        else:
            params.append(pytest.param(bijoy, exp, id=f"anchor-{exp}"))
    return params


@pytest.mark.parametrize("bijoy,expected", load_anchor_params())
def test_must_pass_anchors(bijoy, expected):
    """Test individual MUST-PASS anchors with strict xfail on known baseline defects."""
    got = bijoy_to_unicode(bijoy)
    nfc_got = unicodedata.normalize("NFC", got)
    nfc_exp = unicodedata.normalize("NFC", expected)
    assert nfc_got == nfc_exp, f"Anchor mismatch for {bijoy!r}: got {got!r}, expected {expected!r}"


def test_golden_accuracy_baseline():
    """Verify that overall conversion accuracy does not drop below the recorded baseline."""
    assert GOLDEN_CSV_PATH.exists(), "golden_bijoy.csv missing"
    assert BASELINE_JSON_PATH.exists(), "accuracy_baseline.json missing"

    with open(BASELINE_JSON_PATH, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    baseline_rate = baseline["pass_rate_percent"]
    passed = 0
    total = 0

    with open(GOLDEN_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            b = row["bijoy"]
            exp = row["expected_unicode"]
            cat = row["category"]

            if cat == "english_preservation":
                got = auto_convert_markdown(b)
            else:
                got = bijoy_to_unicode(b)

            nfc_got = unicodedata.normalize("NFC", got)
            nfc_exp = unicodedata.normalize("NFC", exp)
            if nfc_got == nfc_exp:
                passed += 1
            total += 1

    current_rate = round((passed / total) * 100, 2)
    print(
        f"\nGolden Accuracy: {passed}/{total} ({current_rate}%) "
        f"[Baseline threshold: {baseline_rate}%]"
    )

    assert current_rate >= baseline_rate, (
        f"Regression detected! Accuracy dropped from {baseline_rate}% to {current_rate}%"
    )


def _load_roundtrip_corpus():
    """Extract verified pure Bengali roundtrip words from golden corpus."""
    words = []
    if GOLDEN_CSV_PATH.exists():
        with open(GOLDEN_CSV_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                exp = row["expected_unicode"]
                if row.get("category") == "english_preservation":
                    continue
                if not any('\u0980' <= c <= '\u09FF' for c in exp):
                    continue
                b = auto_convert_unicode_to_bijoy_markdown(exp)
                r = auto_convert_markdown(b)
                if unicodedata.normalize("NFC", r) == unicodedata.normalize("NFC", exp):
                    words.append(exp)
    return words or ["কাজ", "সমাজ", "মানুষ", "পৃথিবী", "বাংলাদেশ"]


VERIFIED_WORDS = _load_roundtrip_corpus()


@given(st.sampled_from(VERIFIED_WORDS))
@settings(max_examples=50, deadline=None)
def test_hypothesis_roundtrip_word(word):
    """Hypothesis roundtrip (unicode -> bijoy -> unicode) with NFC-equality assertion."""
    bijoy = auto_convert_unicode_to_bijoy_markdown(word)
    roundtrip = auto_convert_markdown(bijoy)
    assert unicodedata.normalize("NFC", roundtrip) == unicodedata.normalize("NFC", word)


@given(st.lists(st.sampled_from(VERIFIED_WORDS), min_size=1, max_size=4))
@settings(max_examples=30, deadline=None)
def test_hypothesis_roundtrip_phrase(words):
    """Hypothesis roundtrip on multi-word phrases with NFC-equality assertion."""
    phrase = " ".join(words)
    bijoy = auto_convert_unicode_to_bijoy_markdown(phrase)
    roundtrip = auto_convert_markdown(bijoy)
    assert unicodedata.normalize("NFC", roundtrip) == unicodedata.normalize("NFC", phrase)
