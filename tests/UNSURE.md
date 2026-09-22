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
- **Status**: Recorded in `golden_bijoy.csv` exactly as requested. Typists using non-standard key sequences or phonetic shorthand may produce `†M©‡i`. Decoder support should treat `†M©‡i` as an alias or specific ligature variant for "গর্তের".

---

## 2. Ref (র্) & Pre-Kar (ে) Ordering Permutations
- **Context**: In manual Bijoy layout typesetting, typists frequently input ref before e-kar or e-kar before ref, e.g.:
  - `†...©` vs `...©‡` (e.g. `†KvU©‡i` vs `†Kv‡U©i`).
  - In `†KvU©‡i`, `U©` (ট + ref) is followed by `‡i` (e-kar + ro).
  - In `m~‡h©i`, `m~` is followed by `‡` (e-kar) + `h` (yo) + `©` (ref) + `i` (ro).
- **Status**: Standard SutonnyMJ reorderers often produce "সূর্যরে" when `‡` is misplaced before `i`. The golden dataset tests both canonical and shifted suffixes.

---

## 3. Backtick (`` ` ``) Consonant Representation
- **Context**: In Bijoy/SutonnyMJ keyboards, the ASCII backtick character `` ` `` represents the Bengali consonant **দ** (U+09A6).
- **Conflict**: In Markdown, backticks denote inline code formatting (`` `code` ``).
- **Rule**: When isolated inside code or English sentences, backticks must be preserved. When adjacent to Bijoy vowels/consonants (e.g. `evsjv‡`k`), it must resolve to 'দ'.
