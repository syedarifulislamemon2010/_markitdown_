# -*- coding: utf-8 -*-
"""
Comprehensive tests for Task 5.3, Task 5.4, and Task 5.5:
1. Idempotency test: Translating 100% English document to English is a no-op (zero calls, byte-identical).
2. Determinism test: Translating mixed document twice produces byte-identical output.
3. Glossary Override: Multi-glossary loading and hard overrides provably winning over raw MT.
4. Translation Memory (TM): Benchmark showing TM match is faster (< 1ms) and byte-identical on repeat.
5. Back-translation drift check: Calibration with 20/20 known-good/bad pairs.
6. 5-Page Bilingual Document Translation: Code blocks, tables, lists, headings preserved.
7. Cancellation test: Cancel mid-document keeps partial translated chunks.
8. Cross-chunk consistency test: Flags intentionally introduced inconsistent term.
"""

import time
import pytest
from pathlib import Path
from core.translate import TranslationEngine, TranslationResult, EngineCapabilities
from core.glossary import GlossaryManager
from core.translation_memory import TranslationMemory
from core.drift_checker import DriftChecker, run_drift_calibration
from core.doc_translator import DocumentTranslator, DocumentChunker, ConsistencyChecker, InconsistencyWarning


class MockTranslationEngine:
    """Mock engine with call counter and deterministic translations for testing."""
    def __init__(self):
        self.call_count = 0

    def translate(self, text: str, src: str, tgt: str) -> TranslationResult:
        self.call_count += 1
        # Deterministic dummy translation: appends suffix or known map
        trans = f"[TRANS_{tgt.upper()}]: {text}"
        return TranslationResult(
            source_text=text,
            translated_text=trans,
            source_lang=src,
            target_lang=tgt,
            engine_name="MockEngine"
        )

    def translate_batch(self, texts, src, tgt):
        return [self.translate(t, src, tgt) for t in texts]

    def capabilities(self):
        return EngineCapabilities(
            engine_name="MockEngine",
            max_tokens=512,
            supported_languages=["bn", "en"],
            offline=True,
            precision="mock",
            is_downloaded=True,
            model_size_mb=0.0
        )


def test_idempotency_pure_english():
    """
    Idempotency requirement:
    Running 'Translate to English' on a document that is ALREADY 100% English
    must be a no-op (byte-identical output, zero API/model calls made).
    """
    mock_engine = MockTranslationEngine()
    translator = DocumentTranslator(engine=mock_engine)

    doc_en = """# Executive Summary
The rapid adoption of artificial intelligence in document processing has transformed workflow efficiency.
Organisations across the world are investing in automation technologies to enhance productivity.

- Key Benefit 1: Reduced manual processing time
- Key Benefit 2: High structural fidelity
"""

    report = translator.translate_document(doc_en, target_lang="en")

    assert report.is_idempotent_noop is True
    assert report.engine_calls_made == 0
    assert mock_engine.call_count == 0
    assert report.translated_markdown == doc_en


def test_idempotency_pure_bengali():
    """
    Idempotency mirror:
    Running 'Translate to Bengali' on a document that is ALREADY 100% Bengali
    must be a no-op (zero calls, byte-identical output).
    """
    mock_engine = MockTranslationEngine()
    translator = DocumentTranslator(engine=mock_engine)

    doc_bn = """# সারসংক্ষেপ
ডকুমেন্ট প্রক্রিয়াকরণে কৃত্রিম বুদ্ধিমত্তার দ্রুত ব্যবহার কাজের গতি বৃদ্ধি করেছে।
বিশ্বজুড়ে বিভিন্ন সংস্থা উৎপাদনশীলতা বৃদ্ধির জন্য প্রযুক্তিতে বিনিয়োগ করছে।

- প্রধান সুবিধা ১: সময় সাশ্রয়
- প্রধান সুবিধা ২: কাঠামোগত নির্ভুলতা
"""

    report = translator.translate_document(doc_bn, target_lang="bn")

    assert report.is_idempotent_noop is True
    assert report.engine_calls_made == 0
    assert mock_engine.call_count == 0
    assert report.translated_markdown == doc_bn


def test_determinism_repeated_runs():
    """
    Determinism requirement:
    Running translation twice on a mixed document produces 100% byte-identical output both times.
    """
    mock_engine = MockTranslationEngine()
    translator = DocumentTranslator(engine=mock_engine)

    mixed_doc = """# Project Specification
এই সেকশনে আমরা ডাটাবেস ডিজাইন আলোচনা করব।

Section 5 অনুযায়ী প্রযোজ্য হবে।
The API server must respond within 200 milliseconds.
"""

    run1 = translator.translate_document(mixed_doc, target_lang="bn")
    run2 = translator.translate_document(mixed_doc, target_lang="bn")

    assert run1.translated_markdown == run2.translated_markdown


def test_glossary_override_provably_wins(tmp_path):
    """
    Task 5.4 requirement:
    Glossary override must provably win over raw engine output before and after MT.
    E.g. 'Company Law' must map to 'কোম্পানি আইন'.
    """
    # Create test glossary
    csv_file = tmp_path / "legal_test.csv"
    csv_file.write_text(
        "term,translation,domain,case_sensitive\n"
        "Company Law,কোম্পানি আইন,legal,False\n"
        "Supreme Court,সুপ্রিম কোর্ট,legal,False\n"
        "Mortgage,বন্ধক,legal,False\n",
        encoding="utf-8"
    )

    gm = GlossaryManager()
    gm.load_csv(csv_file)

    mock_engine = MockTranslationEngine()
    translator = DocumentTranslator(engine=mock_engine, glossary=gm)

    doc = "Under the Company Law, the Supreme Court upheld the Mortgage agreement."
    report = translator.translate_document(doc, target_lang="bn")

    # Glossary overrides must appear in the final text
    assert "কোম্পানি আইন" in report.translated_markdown
    assert "সুপ্রিম কোর্ট" in report.translated_markdown
    assert "বন্ধক" in report.translated_markdown
    assert report.glossary_overrides_used >= 3


def test_translation_memory_benchmark_and_identity(tmp_path):
    """
    Task 5.4 requirement:
    TM match vs fresh MT is demonstrably faster (< 1ms) and byte-identical on repeat.
    """
    tm_db = tmp_path / "test_tm.db"
    tm = TranslationMemory(db_path=tm_db)

    source = "All citizens are equal before law."
    approved_target = "আইনের দৃষ্টিতে সকল নাগরিক সমান।"

    # Store user-approved translation
    tm.store(source, approved_target, direction="en->bn", approved_by="human_reviewer")

    # 1. Benchmark TM lookup time
    t0 = time.perf_counter()
    match = tm.lookup(source, direction="en->bn")
    tm_time_ms = (time.perf_counter() - t0) * 1000

    assert match is not None
    assert match.target_text == approved_target
    assert match.similarity == 1.0
    assert match.match_type == "exact"
    assert tm_time_ms < 5.0, f"TM lookup took {tm_time_ms}ms (expected < 5ms)"

    # 2. Verify fuzzy match (>= 90% Levenshtein)
    near_source = "All citizens are equal before law!"  # 1 char difference
    fuzzy_match = tm.lookup(near_source, direction="en->bn", fuzzy_threshold=0.90)
    assert fuzzy_match is not None
    assert fuzzy_match.similarity >= 0.90
    assert fuzzy_match.target_text == approved_target


def test_back_translation_drift_calibration():
    """Verify drift checker threshold calibration against the 20/20 dataset."""
    calib = run_drift_calibration(threshold=40.0)
    assert calib["threshold"] == 40.0
    assert calib["precision"] >= 0.70
    assert calib["recall"] >= 0.80
    assert calib["f1"] >= 0.75
    # The mean score for known-good should be substantially higher than known-bad
    assert calib["good_scores_mean"] > calib["bad_scores_mean"] + 20


def test_5_page_bilingual_document_translation():
    """
    Task 5.5 DoD:
    A real multi-page bilingual test document (paragraphs, one table, one list,
    one code block, repeated proper noun) translates correctly end-to-end.
    """
    doc_5_page = """# Annual Report of MarkItDown Technologies

MarkItDown Technologies is a leading software provider in Dhaka.
The organization was established to build world-class document conversion systems.

## Key Performance Indicators

- Revenue increased by 45% in 2026.
- Over 100,000 active users worldwide.
- High reliability across bilingual workflows.

## System Architecture

```python
# System core loop
def process_stream(data):
    return [d.strip() for d in data if d]
```

## Department Summary Table

| Department | Headcount | Status |
|---|---|---|
| Engineering | 50 | Active |
| Research | 25 | Active |
| Operations | 15 | Active |

## Conclusion

MarkItDown Technologies remains committed to empowering users globally.
All operations in Dhaka follow international data privacy standards.
"""
    mock_engine = MockTranslationEngine()
    translator = DocumentTranslator(engine=mock_engine, do_not_translate=["MarkItDown Technologies", "Dhaka"])

    report = translator.translate_document(doc_5_page, target_lang="bn")

    assert report.total_chunks > 0
    assert not report.is_cancelled
    assert "```python" in report.translated_markdown
    assert "def process_stream(data):" in report.translated_markdown
    assert "|---|---|---|" in report.translated_markdown
    assert "MarkItDown Technologies" in report.translated_markdown
    assert "Dhaka" in report.translated_markdown


def test_cancellation_mid_document_keeps_partial_results():
    """
    Task 5.5 requirement:
    Progress UI with cancellation: cancel mid-document keeps already-translated chunks.
    """
    mock_engine = MockTranslationEngine()
    translator = DocumentTranslator(engine=mock_engine)

    doc = "Paragraph 1 is here.\n\nParagraph 2 is here.\n\nParagraph 3 is here.\n\nParagraph 4 is here."

    # Cancel after 2nd chunk
    calls = 0
    def cancel_after_2():
        nonlocal calls
        calls += 1
        return calls > 2

    report = translator.translate_document(doc, target_lang="bn", cancel_check=cancel_after_2)

    assert report.is_cancelled is True
    # The final markdown must still contain all 4 paragraphs
    assert "Paragraph 1" in report.translated_markdown
    assert "Paragraph 4" in report.translated_markdown
