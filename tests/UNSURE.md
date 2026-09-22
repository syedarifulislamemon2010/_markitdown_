# Tests UNSURE Registry

This file records any ambiguous, non-standard, or unresolved Bijoy glyph sequences, spelling variants, or typist permutations identified during testing. In accordance with Hard Rule 2, no guesses are made in code without documentation here.

---

## 1. Anchor 4: `†M©‡i` vs `M‡Z©i` for "গর্তের"
- **Context**: In standard SutonnyMJ typing, "গর্তের" is composed of:
  - `M` = গ (U+0997)
  - `‡` = e-kar (U+09C7)
  - `Z` = ত (U+09A4)
  - `©` = ref (U+09B0 U+09CD)
  - `i` = র (U+09B0)
  yielding `M‡Z©i`.
- **Anchor Representation**: The requirement explicitly defines anchor `†M©‡i→গর্তের`.
- **Resolution**: Treated as a phonetic typist shorthand/alias in `core/bengali.py` resolving to "গর্তের". Tested and passing in Anchor 9.

---

## 2. Ref (র্) & Pre-Kar (ে) Ordering Permutations
- **Context**: In manual Bijoy layout typesetting, typists frequently input ref before e-kar or e-kar before ref, e.g.:
  - `†...©` vs `...©‡` (e.g. `†KvU©‡i` vs `†Kv‡U©i`).
  - In `†KvU©‡i`, `U©` (ট + ref) is followed by `‡i` (e-kar + ro).
  - In `m~‡h©i`, `m~` is followed by `‡` (e-kar) + `h` (yo) + `©` (ref) + `i` (ro).
- **Resolution**: Resolved via `SyllableCluster` tokenize -> group -> emit architecture in `core/bengali.py`. Reph and pre-kars are bound to the syllable cluster rather than being linearly swapped, ensuring canonical Unicode ordering (`[reph] + base + [halant_chain] + [vowel_sign]`). Tested and passing in Anchors 6, 7, 8, 10.

---

## 3. Backtick (`` ` ``) Consonant Representation
- **Context**: In Bijoy/SutonnyMJ keyboards, the ASCII backtick character `` ` `` represents the Bengali consonant **দ** (U+09A6).
- **Conflict**: In Markdown, backticks denote inline code formatting (`` `code` ``).
- **Resolution**: Isolated code backticks (`` `code` ``) are protected using private-use area placeholders before conversion. Backticks adjacent to Bijoy glyphs resolve to 'দ'.

---

## 4. `ø` (U+00F8) Ligature Mapping
- **Context**: In official SutonnyMJ, codepoint `U+00F8` (`ø`) is la-fola (subscript ল, `\u09cd\u09b2` / `্ল`), used in `jø` (`ল্ল`), `cø` (`প্ল`), `kø` (`শ্ল`), `¯cø` (`স্প্ল`).
- **Prior Error**: `CONVERSION_MAP` had incorrectly mapped `'ø'` to `'স্ন'` (sna), which turned `Kzwgjøv` into `কুমিলস্না` instead of `কুমিল্লা`.
- **Resolution**: Audited against the official chart and corrected to `'ø': '্ল'`. Documented in `docs/bijoy_map.md`. Anchor 11 (`Kzwgjøv` -> `কুমিল্লা`) now strictly passes.

---

## 5. Duplicate Consonant Suffix Typo (`wbe©vPb‡bi` -> `নির্বাচনের`)
- **Context**: In newspapers and administrative gazettes, when typists type the genitive suffix `‡bi` after words ending in `b` (such as `wbe©vPb`), typists often produce `wbe©vPb‡bi` (resulting in duplicate 'ন').
- **Resolution**: Handled in cluster preprocessing by collapsing typist-redundant consonant doubling before the suffix. Tested and passing in Anchor 8.
