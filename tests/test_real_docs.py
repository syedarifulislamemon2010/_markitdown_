# -*- coding: utf-8 -*-
"""Real documents test harness.

Processes real documents from tests/real_docs/ (private, gitignored)
and reports per-file conversion status and diffs.
Runs gracefully when tests/real_docs/ is empty.
"""

import difflib
from pathlib import Path
import pytest
from core.converter import DocumentConverter


def test_real_docs_harness():
    """Evaluate real documents in tests/real_docs/ or skip gracefully when empty."""
    real_docs_dir = Path(__file__).parent / "real_docs"
    if not real_docs_dir.exists():
        real_docs_dir.mkdir(parents=True, exist_ok=True)

    supported_extensions = {".pdf", ".docx", ".xlsx", ".xls", ".pptx", ".txt", ".md"}
    test_files = [
        f for f in real_docs_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions and not f.name.endswith(".expected.md")
    ]

    if not test_files:
        pytest.skip("tests/real_docs/ is empty; harness is ready to receive real documents.")

    converter = DocumentConverter()
    results = []

    for doc_path in test_files:
        res = converter.convert_file(doc_path)
        expected_md_file = doc_path.with_suffix(".expected.md")
        has_expected = expected_md_file.exists()

        diff_summary = ""
        if has_expected and res.success:
            expected_content = expected_md_file.read_text(encoding="utf-8")
            diff = list(difflib.unified_diff(
                expected_content.splitlines(keepends=True),
                res.markdown.splitlines(keepends=True),
                fromfile=str(expected_md_file.name),
                tofile=f"{doc_path.name}.converted.md",
            ))
            diff_summary = "".join(diff[:50])

        results.append({
            "file": doc_path.name,
            "success": res.success,
            "error": res.error_message,
            "has_expected": has_expected,
            "diff": diff_summary,
        })

    failed = [r for r in results if not r["success"] or r["diff"]]
    if failed:
        report = "\n".join(
            f"File: {r['file']} | Success: {r['success']} | Error: {r['error']} | Diff:\n{r['diff']}"
            for r in failed
        )
        pytest.fail(f"Real docs regression detected:\n{report}")
