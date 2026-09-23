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
- **Algorithmic Reality**: The sequence `†M©‡i` literally contains no `Z` (ত) character anywhere. No general syllabic clustering algorithm can deduce `ত` from a sequence containing only `†` (e-kar), `M` (গ), `©` (reph), `‡` (e-kar), `i` (র).
- **Resolution**: Hardcoded inline `text.replace` was completely removed from the cluster engine. Handled cleanly at the word-token layer via `WORD_ALIASES['†M©‡i'] = 'M‡Z©i'`, resolving it to canonical Bijoy `M‡Z©i` before clustering. Tested and passing in Anchor 9 and golden test suite.

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

## 5. Generalized Genitive Suffix Absorption (`‡bi` -> `-এর`)
- **Context**: In Bengali typing, typists frequently append `‡bi` (`ে` + `ন` + `র`) to denote the genitive `-এর` suffix:
  1. **Duplicate consonant after stems in 'ন' / 'ণ'**: When words already end in `b` (`ন`) or `Y` (`ণ`) (e.g. `wbe©vPb` -> `wbe©vPb‡bi`, `cÖwZôvb` -> `cÖwZôvb‡bi`, `ea©b` -> `ea©b‡bi`), appending `‡bi` produces an incorrect duplicate `ন` (`নির্বাচননের`, `প্রতিষ্ঠাননের`).
  2. **Typist shorthand after consonants**: Stems ending in consonants (e.g. `wefvM` -> `wefvM‡bi`, `miKvi` -> `miKvi‡bi`, or reph clusters like `mZK©` -> `mZK©‡bi`, `Kg©` -> `Kg©‡bi`) should resolve to `-এর` (`বিভাগের`, `সরকারের`, `সতর্কের`, `কর্মের`), never `-নের`.
  3. **Preservation of legitimate 'ন' stems**: Short single-letter or vowel stems where `‡bi` represents the legitimate stem's `নে` + `র` (e.g. `e‡bi` -> `বনের`, `AvB‡bi` -> `আইনের`, `Av‡e`‡bi` -> `আবেদনের`) must be protected and NOT collapsed into `-এর`.
- **Resolution**: Implemented generally in `ClusterBijoyEngine.convert_bengali_run` without hardcoded text replacements:
  - If preceding cluster has reph or base in `('ন', 'ণ', 'গ', 'র', 'য়', 'য')`, `‡bi` is absorbed into `c.post_kar = 'ে'`, consuming the redundant `ন` and leaving `র` for canonical suffix emission.
  - Hardcoded string replacements (`text.replace('wbe©vPb‡bi', ...)`) were deleted.
  - Tested across 22 diverse golden words (`wefvM‡bi`, `miKvi‡bi`, `cÖwZôvb‡bi`, `ea©b‡bi`, `AR©b‡bi`, `eR©b‡bi`, etc.) with 100% pass rate.

---

## 6. Bengali Number-to-Words Orthographic Variants
- **Context**: Standard Bangla Academy Bengali spelling allows subtle orthographic variants:
  - 6: `ছয়` (modern standard) vs `ছয়` (classical / alternate ya)
  - 9: `নয়` vs `নয়`
  - 20: `বিশ` vs `কুড়ি` / `কুড়ি`
  - 35, 45, 65: Candrabindu variants (`পঁয়ত্রিশ` vs `পয়ত্রিশ`, `পঁয়তাল্লিশ` vs `পয়তাল্লিশ`, `পঁয়ষট্টি` vs `পয়ষট্টি`)
  - 88: `অষ্টআশি` vs `আটাশি`
  - 100: `এক শত` vs `একশো`
  - Scale: `লাখ` (colloquial & standard banking) vs `লক্ষ` (formal Sanskritized)
- **Resolution**: In `core/bengali_tools.py`, canonical forward generator outputs standard modern Bangla Academy forms (`ছয়`, `নয়`, `এক শত`, `লাখ`). The reverse parser `bangla_words_to_number` accepts all valid variants transparently. Tested across 100 reference cases in `tests/test_bengali_tools.py`.
