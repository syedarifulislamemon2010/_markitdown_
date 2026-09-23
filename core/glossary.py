# -*- coding: utf-8 -*-
"""
Glossary & 'Never Translate' Engine for MarkItDown Studio.

Features:
  - Multi-glossary simultaneous loading (CSV / JSON)
  - Hard overrides applied before AND after machine translation
  - Case-sensitivity controls per term
  - Automated candidate detection for 'Never Translate' lists (ALL-CAPS acronyms, proper nouns)
"""

from __future__ import annotations
import csv
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any


@dataclass
class GlossaryEntry:
    term: str
    translation: str
    domain: str = "general"
    case_sensitive: bool = False


class GlossaryManager:
    """Manages swappable, user-editable glossaries with multi-file loading and hard overrides."""

    def __init__(self):
        self.entries: Dict[str, GlossaryEntry] = {}
        self.never_translate_list: Set[str] = set()

    def load_csv(self, file_path: Path | str, domain_override: Optional[str] = None):
        """Load a CSV glossary file (columns: term, translation, domain, case_sensitive)."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Glossary file not found: {p}")

        with open(p, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                term = row.get("term", "").strip()
                translation = row.get("translation", "").strip()
                if not term or not translation:
                    continue
                domain = domain_override or row.get("domain", "general").strip()
                case_sensitive = str(row.get("case_sensitive", "false")).lower() in ("true", "1", "yes")

                key = term if case_sensitive else term.lower()
                self.entries[key] = GlossaryEntry(
                    term=term,
                    translation=translation,
                    domain=domain,
                    case_sensitive=case_sensitive
                )

    def load_multiple(self, file_paths: List[Path | str]):
        """Load multiple swappable glossary files simultaneously."""
        for path in file_paths:
            self.load_csv(path)

    def add_never_translate(self, term: str):
        """Add a term to the permanent Never-Translate list."""
        cleaned = term.strip()
        if cleaned:
            self.never_translate_list.add(cleaned)

    def remove_never_translate(self, term: str):
        self.never_translate_list.discard(term.strip())

    @staticmethod
    def detect_never_translate_candidates(text: str) -> List[str]:
        """
        Auto-detect ALL-CAPS acronyms and proper noun candidates.
        Requires explicit user confirmation before permanent addition.
        """
        candidates = set()
        # 1. Acronyms: 2 to 6 uppercase letters (e.g. NID, BPSC, NBR, UNESCO, NASA, API)
        for m in re.finditer(r'\b[A-Z]{2,6}\b', text):
            candidates.add(m.group(0))

        # 2. Capitalized phrases (Proper Nouns): e.g. "MarkItDown Studio", "Dhaka University"
        for m in re.finditer(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text):
            candidates.add(m.group(0))

        return sorted(list(candidates))

    def apply_override(self, text: str, direction: str = "en->bn") -> Tuple[str, int]:
        """
        Apply hard glossary overrides directly to text.
        Returns (result_text, count_of_replacements).
        """
        if not text or not self.entries:
            return text, 0

        result = text
        count = 0
        sorted_entries = sorted(self.entries.values(), key=lambda e: len(e.term), reverse=True)

        for entry in sorted_entries:
            if direction in ("en->bn", "to_bn"):
                src_phrase = entry.term
                tgt_phrase = entry.translation
            else:
                src_phrase = entry.translation
                tgt_phrase = entry.term

            if entry.case_sensitive:
                pattern = re.compile(rf'\b{re.escape(src_phrase)}\b')
            else:
                pattern = re.compile(rf'\b{re.escape(src_phrase)}\b', re.IGNORECASE)

            new_result, n = pattern.subn(tgt_phrase, result)
            if n > 0:
                count += n
                result = new_result

        return result, count
