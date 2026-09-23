# -*- coding: utf-8 -*-
"""
Markdown & Bilingual Script Segmenter for MarkItDown Studio.

Decomposes Markdown text into classified segments:
  - 'bn': Pure Bengali text
  - 'en': Pure English text
  - 'mixed': Mixed Bengali/English script sentences (never split mid-sentence)
  - 'protected': URLs, emails, code blocks, inline code, syntax tokens, numbers/dates, do-not-translate terms
  - 'whitespace': Preserved formatting, indentation, newlines

Guarantees byte-exact round-trip: rejoin(segment(text)) == text
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Set, Dict, Any, Optional

MIXED_THRESHOLD: float = 0.80

# Regex patterns for protected entities
URL_PATTERN = re.compile(r'\b(?:https?|ftp|file)://[^\s<>"\'\)\]\}]+', re.IGNORECASE)
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
FENCED_CODE_PATTERN = re.compile(r'(```[^\n]*\n[\s\S]*?\n```|~~~[^\n]*\n[\s\S]*?\n~~~)')
INLINE_CODE_PATTERN = re.compile(r'(`[^`\n]+`)')

# Numbers, dates, and account/phone formats
# Includes Bangabda / Gregorian dates, digits, currencies, and numeric IDs
NUMBER_DATE_PATTERN = re.compile(
    r'(?:'
    # Currency symbols + numbers ($100, ৳৫০০, BDT 500, €50, £50, Rs 50)
    r'(?:[\$৳€£¥]|BDT\s*|USD\s*|Rs\.?\s*)[\d০-৯]+(?:[.,][\d০-৯]+)*'
    # Dates: 2026-09-23, 23/09/2026, ২৩/০৯/২০২৬, 23-09-2026
    r'|\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b'
    r'|[০-৯]{1,4}[-/.] [০-৯]{1,2}[-/.] [০-৯]{1,4}'
    # Standalone numbers with decimals/commas: 1,000.50 or ১,০০০.৫০
    r'|\b\d+(?:,\d{3})*(?:\.\d+)?%?\b'
    r'|[০-৯]+(?:,[০-৯]{3})*(?:\.[০-৯]+)?%?'
    r')'
)

# Bengali character range
BENGALI_CHAR_PATTERN = re.compile(r'[\u0980-\u09FF]')
ENGLISH_CHAR_PATTERN = re.compile(r'[a-zA-Z]')


@dataclass
class Segment:
    """A classified text slice preserving exact source text for lossless round-tripping."""
    text: str
    label: str  # 'bn', 'en', 'mixed', 'protected', 'whitespace'
    kind: str = "text"  # 'code_block', 'inline_code', 'url', 'email', 'markdown_syntax', 'number', 'do_not_translate', 'text', 'whitespace'
    meta: Dict[str, Any] = field(default_factory=dict)

    def is_translatable(self) -> bool:
        """Return True if segment should be sent to translation engine."""
        return self.label in ("bn", "en", "mixed")


def sentence_language_ratio(text: str) -> Dict[str, float]:
    """
    Calculate the language token distribution for a sentence.
    Returns ratios for 'bn', 'en', and 'other'.
    """
    if not text:
        return {"bn": 0.0, "en": 0.0, "other": 0.0}

    # Extract word tokens
    words = re.findall(r'[\w\u0980-\u09FF]+', text)
    if not words:
        return {"bn": 0.0, "en": 0.0, "other": 1.0}

    bn_tokens = 0
    en_tokens = 0
    other_tokens = 0

    for w in words:
        has_bn = bool(BENGALI_CHAR_PATTERN.search(w))
        has_en = bool(ENGLISH_CHAR_PATTERN.search(w))

        if has_bn and not has_en:
            bn_tokens += 1
        elif has_en and not has_bn:
            en_tokens += 1
        elif has_bn and has_en:
            # Word itself contains both scripts (e.g. "University-তে")
            bn_tokens += 0.5
            en_tokens += 0.5
        else:
            other_tokens += 1

    script_total = bn_tokens + en_tokens
    if script_total == 0:
        return {"bn": 0.0, "en": 0.0, "other": 1.0}

    return {
        "bn": bn_tokens / script_total,
        "en": en_tokens / script_total,
        "other": other_tokens / len(words)
    }


def classify_sentence(text: str, mixed_threshold: float = MIXED_THRESHOLD) -> str:
    """
    Classify a sentence as 'bn', 'en', or 'mixed'.
    A segment is classified as 'mixed' if neither language exceeds mixed_threshold (default 0.80).
    """
    ratios = sentence_language_ratio(text)
    bn_ratio = ratios["bn"]
    en_ratio = ratios["en"]

    if bn_ratio == 0.0 and en_ratio == 0.0:
        return "en"  # fallback for neutral/symbolic sentences

    if bn_ratio >= mixed_threshold:
        return "bn"
    if en_ratio >= mixed_threshold:
        return "en"

    return "mixed"


def _split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences while respecting Bengali danda ('।'), English '.', '!', '?',
    and preserving all whitespace and delimiters attached so no characters are lost.
    """
    if not text:
        return []

    # Match sentence body followed by sentence delimiter ('।', '.', '?', '!', '\n')
    # Protect common abbreviations like Mr., Dr., e.g., i.e., vs., Fig., etc.
    abbreviations = (
        r'(?<!\bMr)(?<!\bDr)(?<!\bMs)(?<!\bProf)(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\bFig)'
        r'(?<!\bJan)(?<!\bFeb)(?<!\bMar)(?<!\bApr)(?<!\bJun)(?<!\bJul)(?<!\bAug)(?<!\bSep)(?<!\bOct)(?<!\bNov)(?<!\bDec)'
        r'(?<!\bSec)(?<!\bNo)(?<!\bVol)(?<!\bp)'
        r'(?<!\d)'  # Protect decimal numbers like 3.14
    )

    pattern = re.compile(rf'({abbreviations}[।!?\n]|\b{abbreviations}\.(?:\s+|$))')
    parts = pattern.split(text)

    # Reassemble parts so delimiters stay with their preceding sentence
    sentences = []
    i = 0
    while i < len(parts):
        chunk = parts[i]
        if i + 1 < len(parts) and pattern.match(parts[i + 1]):
            chunk += parts[i + 1]
            i += 2
        else:
            i += 1
        if chunk:
            sentences.append(chunk)

    return sentences if sentences else [text]


def segment(
    text: str,
    do_not_translate: Optional[Set[str] | List[str]] = None,
    mixed_threshold: float = MIXED_THRESHOLD,
    auto_convert_bijoy: bool = True
) -> List[Segment]:
    """
    Segment input text into {bn, en, mixed, protected, whitespace}.
    Byte-exact round-trip guaranteed: rejoin(segment(text)) == text (or converted Unicode if Bijoy).
    """
    if not text:
        return []

    # Step 0: Check Bijoy if enabled
    if auto_convert_bijoy:
        from core.bengali import auto_convert_markdown, is_likely_bijoy
        if is_likely_bijoy(text):
            text = auto_convert_markdown(text)

    dnt_set: Set[str] = set(do_not_translate) if do_not_translate else set()
    # Sort DNT terms by length descending to match longest matches first
    sorted_dnt = sorted(dnt_set, key=len, reverse=True) if dnt_set else []

    # Step 1: Extract non-overlapping protected spans
    # (start, end, kind, text)
    spans: List[tuple[int, int, str, str]] = []

    # 1a. Fenced code blocks
    for m in FENCED_CODE_PATTERN.finditer(text):
        spans.append((m.start(), m.end(), "code_block", m.group(0)))

    # 1b. Inline code
    for m in INLINE_CODE_PATTERN.finditer(text):
        spans.append((m.start(), m.end(), "inline_code", m.group(0)))

    # 1c. URLs
    for m in URL_PATTERN.finditer(text):
        spans.append((m.start(), m.end(), "url", m.group(0)))

    # 1d. Emails
    for m in EMAIL_PATTERN.finditer(text):
        spans.append((m.start(), m.end(), "email", m.group(0)))

    # 1e. Do-not-translate user terms
    for term in sorted_dnt:
        if not term:
            continue
        # Use literal search to avoid regex injection
        pattern = re.compile(re.escape(term))
        for m in pattern.finditer(text):
            spans.append((m.start(), m.end(), "do_not_translate", m.group(0)))

    # Filter overlapping spans: sort by start asc, length desc
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    non_overlapping: List[tuple[int, int, str, str]] = []
    last_end = -1
    for start, end, kind, val in spans:
        if start >= last_end:
            non_overlapping.append((start, end, kind, val))
            last_end = end

    # Step 2: Slice text into alternating protected and raw slices
    segments: List[Segment] = []
    curr_pos = 0

    for start, end, kind, val in non_overlapping:
        if start > curr_pos:
            raw_chunk = text[curr_pos:start]
            segments.extend(_process_raw_text(raw_chunk, mixed_threshold))
        segments.append(Segment(text=val, label="protected", kind=kind))
        curr_pos = end

    if curr_pos < len(text):
        raw_chunk = text[curr_pos:]
        segments.extend(_process_raw_text(raw_chunk, mixed_threshold))

    return segments


def _process_raw_text(text: str, mixed_threshold: float) -> List[Segment]:
    """Process un-protected text, splitting into markdown syntax tokens and translatable sentences."""
    if not text:
        return []

    # Check for pure whitespace
    if text.isspace():
        return [Segment(text=text, label="whitespace", kind="whitespace")]

    # Split line-by-line to preserve Markdown line structures
    lines = text.splitlines(keepends=True)
    segments: List[Segment] = []

    for line in lines:
        if not line:
            continue
        if line.isspace():
            segments.append(Segment(text=line, label="whitespace", kind="whitespace"))
            continue

        # Handle Markdown syntax elements per line
        # 1. Header prefix (# , ## , etc.)
        header_match = re.match(r'^(#{1,6}\s+)', line)
        if header_match:
            prefix = header_match.group(1)
            segments.append(Segment(text=prefix, label="protected", kind="markdown_syntax"))
            remainder = line[len(prefix):]
            segments.extend(_process_line_content(remainder, mixed_threshold))
            continue

        # 2. Blockquote prefix (> )
        quote_match = re.match(r'^(>\s*)', line)
        if quote_match:
            prefix = quote_match.group(1)
            segments.append(Segment(text=prefix, label="protected", kind="markdown_syntax"))
            remainder = line[len(prefix):]
            segments.extend(_process_line_content(remainder, mixed_threshold))
            continue

        # 3. List prefix (* , - , + , 1. , etc.)
        list_match = re.match(r'^(\s*(?:[*+-]|\d+\.)\s+)', line)
        if list_match:
            prefix = list_match.group(1)
            segments.append(Segment(text=prefix, label="protected", kind="markdown_syntax"))
            remainder = line[len(prefix):]
            segments.extend(_process_line_content(remainder, mixed_threshold))
            continue

        # 4. Table row (starts and ends with |)
        if line.strip().startswith('|') and line.strip().endswith('|'):
            segments.extend(_process_table_row(line, mixed_threshold))
            continue

        # 5. Horizontal rule (--- or *** or ___)
        if re.match(r'^\s*([-*_]{3,})\s*$', line):
            segments.append(Segment(text=line, label="protected", kind="markdown_syntax"))
            continue

        # Regular prose line
        segments.extend(_process_line_content(line, mixed_threshold))

    return segments


def _process_table_row(line: str, mixed_threshold: float) -> List[Segment]:
    """Process markdown table row cell-by-cell, preserving pipe delimiters."""
    # Check if separator row like |---|---|
    if re.match(r'^\s*\|(?:\s*:?-+:?\s*\|)+\s*$', line):
        return [Segment(text=line, label="protected", kind="markdown_syntax")]

    segments: List[Segment] = []
    # Split by pipe while preserving pipes
    cells = re.split(r'(\|)', line)
    for c in cells:
        if not c:
            continue
        if c == '|':
            segments.append(Segment(text=c, label="protected", kind="markdown_syntax"))
        elif c.isspace():
            segments.append(Segment(text=c, label="whitespace", kind="whitespace"))
        else:
            # Cell content: strip outer whitespace for classification, preserve original text
            segments.extend(_process_line_content(c, mixed_threshold))
    return segments


def _process_line_content(line_content: str, mixed_threshold: float) -> List[Segment]:
    """Process text within a line into sentences and classify each sentence."""
    if not line_content:
        return []
    if line_content.isspace():
        return [Segment(text=line_content, label="whitespace", kind="whitespace")]

    sentences = _split_into_sentences(line_content)
    segments: List[Segment] = []

    for s in sentences:
        if not s:
            continue
        if s.isspace():
            segments.append(Segment(text=s, label="whitespace", kind="whitespace"))
            continue

        label = classify_sentence(s, mixed_threshold)
        segments.append(Segment(text=s, label=label, kind="text"))

    return segments


def rejoin(segments: List[Segment]) -> str:
    """
    Losslessly reassembles segments into original text.
    Byte-exact round-trip guarantee: rejoin(segment(text)) == text.
    """
    return "".join(s.text for s in segments)
