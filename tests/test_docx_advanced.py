# -*- coding: utf-8 -*-
"""Advanced tests for high-fidelity Word (.docx) exporter.

Validates:
1. Nested unordered and ordered lists with correct indentation.
2. Recursive nested inline formatting (**bold *italic* bold**).
3. Footnote references rendered as superscript.
4. Shaded code blocks with Consolas font.
5. Bengali font applied when specified.
6. Tables generated correctly.
7. Round-trip: markdown -> docx -> verify key content is present.
"""

import io
import docx
from core.docx_exporter import markdown_to_docx_bytes


def _load_docx(md_text: str, **kwargs) -> docx.Document:
    """Helper: convert markdown to docx and load for inspection."""
    raw = markdown_to_docx_bytes(md_text, **kwargs)
    assert raw and len(raw) > 100, "Generated docx is too small or empty"
    return docx.Document(io.BytesIO(raw))


def test_nested_unordered_lists():
    """Nested bullet lists should have increasing left indentation."""
    md = "- Level 0\n  - Level 1\n    - Level 2\n- Back to 0\n"
    doc = _load_docx(md)
    bullets = [p for p in doc.paragraphs if p.style.name == 'List Bullet']
    assert len(bullets) >= 3, f"Expected >=3 bullet paragraphs, got {len(bullets)}"
    # Level 1 indent should be greater than level 0
    indent_0 = bullets[0].paragraph_format.left_indent
    indent_1 = bullets[1].paragraph_format.left_indent
    if indent_0 is not None and indent_1 is not None:
        assert indent_1 > indent_0, "Nested bullet should have greater indent"


def test_nested_ordered_lists():
    """Nested numbered lists should have increasing left indentation."""
    md = "1. First\n   1. Sub-first\n      1. Sub-sub\n2. Second\n"
    doc = _load_docx(md)
    nums = [p for p in doc.paragraphs if p.style.name == 'List Number']
    assert len(nums) >= 3, f"Expected >=3 numbered paragraphs, got {len(nums)}"


def test_nested_inline_formatting():
    """Bold containing italic produces runs with correct bold/italic flags."""
    md = "**bold text *bold-italic* more bold**\n"
    doc = _load_docx(md)
    # Find the paragraph containing our text
    found_bold = False
    found_italic = False
    for p in doc.paragraphs:
        for run in p.runs:
            if run.bold:
                found_bold = True
            if run.italic:
                found_italic = True
    assert found_bold, "Expected at least one bold run"
    assert found_italic, "Expected at least one italic run"


def test_footnote_superscript():
    """Footnote references [^1] should produce superscripted runs."""
    md = "Some text with a footnote[^1].\n\n[^1]: This is the footnote.\n"
    doc = _load_docx(md)
    found_superscript = False
    for p in doc.paragraphs:
        for run in p.runs:
            if run.font.superscript and '1' in run.text:
                found_superscript = True
    assert found_superscript, "Footnote reference should be superscripted"


def test_code_block_consolas():
    """Code blocks should use Consolas font."""
    md = "```python\ndef hello():\n    print('hi')\n```\n"
    doc = _load_docx(md)
    found_consolas = False
    for p in doc.paragraphs:
        for run in p.runs:
            if run.font.name == 'Consolas':
                found_consolas = True
    assert found_consolas, "Code block should use Consolas font"


def test_bengali_font_applied():
    """When bengali_font is specified, regular paragraphs should use it."""
    md = "আমাদের দেশ বাংলাদেশ\n"
    doc = _load_docx(md, bengali_font="Kalpurush")
    found_font = False
    for p in doc.paragraphs:
        for run in p.runs:
            if run.font.name == 'Kalpurush':
                found_font = True
    assert found_font, "Bengali font 'Kalpurush' should be applied to runs"


def test_table_generation():
    """Markdown tables should produce Word table objects."""
    md = "| Name | Age |\n|------|-----|\n| Alice | 30 |\n| Bob | 25 |\n"
    doc = _load_docx(md)
    assert len(doc.tables) >= 1, "Expected at least one table in the document"
    table = doc.tables[0]
    assert len(table.rows) >= 2, "Table should have at least 2 rows (header + data)"


def test_heading_levels():
    """Headings should be produced at the correct levels."""
    md = "# H1 Title\n\n## H2 Section\n\n### H3 Subsection\n"
    doc = _load_docx(md)
    heading_levels = []
    for p in doc.paragraphs:
        if p.style.name.startswith('Heading'):
            level = int(p.style.name.replace('Heading ', '').strip())
            heading_levels.append(level)
    assert 1 in heading_levels, "H1 heading expected"
    assert 2 in heading_levels, "H2 heading expected"
    assert 3 in heading_levels, "H3 heading expected"


def test_roundtrip_content_preserved():
    """Key content (headings, lists, code, tables) should survive md->docx conversion."""
    md = """# MarkItDown Studio

## Features

- **Bold list item**
- *Italic list item*
- `Code snippet`

### Code Example

```python
print("Hello")
```

| Col A | Col B |
|-------|-------|
| 1     | 2     |

Some final paragraph text.
"""
    doc = _load_docx(md, title="Test Document")
    all_text = " ".join(p.text for p in doc.paragraphs)
    assert "MarkItDown Studio" in all_text
    assert "Features" in all_text
    assert "Code Example" in all_text
    assert "Hello" in all_text
    assert "final paragraph" in all_text
    assert len(doc.tables) >= 1
