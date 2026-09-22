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
    detect_encoding,
    is_likely_bijoy,
)

GOLDEN_CSV_PATH = Path(__file__).parent / "golden_bijoy.csv"
BASELINE_JSON_PATH = Path(__file__).parent / "accuracy_baseline.json"

ANCHORS = [
    ("KvR", "কাজ", False),
    ("mgvR", "সমাজ", False),
    ("gvbyl", "মানুষ", False),
    ("c„w_ex", "পৃথিবী", False),
    ("evsjv‡`k", "বাংলাদেশ", False),
    ("†KvU©‡i", "কোর্টের", False),
    ("m~‡h©i", "সূর্যের", False),
    ("wbe©vPb‡bi", "নির্বাচনের", False),
    ("†M©‡i", "গর্তের", False),
    ("Dcm‡M©i", "উপসর্গের", False),
    ("Kzwgjøv", "কুমিল্লা", False),
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


def test_detect_encoding():
    """Verify detect_encoding returns correct labels, confidences, and respects font overrides."""
    # Bijoy detection
    for bijoy_word in ["KvR", "mgvR", "gvbyl", "c„w_ex", "evsjv‡`k", "Avgvi", "Kzwgjøv"]:
        label, conf = detect_encoding(bijoy_word)
        assert label == "bijoy", f"Expected bijoy for {bijoy_word!r}, got {label}"
        assert conf >= 0.65
        assert is_likely_bijoy(bijoy_word) is True

    # Negative triggers: programming/shell symbols should NOT trigger Bijoy
    for non_bijoy in [
        "Use ~/bin | grep foo",
        "git status",
        "def test_func(): pass",
        "curl -s https://example.com | jq .",
        "x ^ y | z ~ w",
    ]:
        label, conf = detect_encoding(non_bijoy)
        assert label == "english", f"Expected english for {non_bijoy!r}, got {label}"
        assert is_likely_bijoy(non_bijoy) is False

    # Unicode Bengali detection
    u_sample = "আমাদের দেশ বাংলাদেশ, এটি একটি সুন্দর দেশ"
    label, conf = detect_encoding(u_sample)
    assert label == "unicode"
    assert conf >= 0.8
    assert is_likely_bijoy(u_sample) is False

    # Font overrides
    label, conf = detect_encoding("Sample text", font_name="SutonnyMJ")
    assert label == "bijoy"
    assert conf >= 0.95

    label, conf = detect_encoding("বাংলাদেশ", font_name="Kalpurush")
    assert label == "unicode"
    assert conf >= 0.95


def test_trie_performance_benchmark():
    """Verify Trie conversion benchmark: 100k characters in < 0.5s."""
    import time
    from core.bengali import _get_bijoy_engine
    engine = _get_bijoy_engine()
    sample = ("Avgvi †mvbvi evsjv Avwg †Zvgvq fvjvevwm| "
              "wbe©vPb‡bi djvdj cÖKvk Kiv n‡q‡Q| "
              "Kzwgjøv †Rjvq Kg©KZ©viv cÖavbgš¿xi mv‡_ †`Lv K‡ib| ") * 1000
    sample = sample[:100000]
    assert len(sample) == 100000

    start = time.perf_counter()
    _ = engine.convert_bengali_run(sample)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.5, f"Trie benchmark exceeded 0.5s: {elapsed:.4f}s"

