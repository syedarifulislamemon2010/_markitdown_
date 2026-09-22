# Bijoy / SutonnyMJ to Unicode Mapping Reference

This document catalogs the complete character mapping table from legacy Bijoy / ANSI (SutonnyMJ)
to standard UTF-8 Unicode Bengali, along with audited corrections against official SutonnyMJ layout specifications.

## 1. Audited Mismatch Analysis & Rectifications

| Key (ANSI) | Codepoint | Prior Mapping | Official / Correct Mapping | Root Cause & Impact |
| :---: | :---: | :---: | :---: | :--- |
| `ø` | `U+00F8` | `স্ন` (sna) | `্ল` (la-fola: `্ল`) | **CRITICAL BUG**: In SutonnyMJ, `ø` is la-fola (subscript ল), used in `jø` (`ল্ল`), `cø` (`প্ল`), `kø` (`শ্ল`), `¯cø` (`স্প্ল`). Mapping `ø` to `স্ন` corrupted `Kzwgjøv` into `কুমিলস্না` instead of `কুমিল্লা`. Rectified to `্ল`. |
| `\|` | `U+005C U+007C` | `।` (dari) | (Removed) | Literal backslash followed by pipe matched LaTeX/markdown escapes, corrupting `\|`. Unescaped `\|` correctly maps to `।`. |
| `\&` | `U+005C U+0026` | `্‌` (hasant+zwnj) | (Removed) | Literal backslash followed by ampersand corrupted code/LaTeX. Unescaped `&` correctly maps to `্`. |
| `\^` | `U+005C U+005E` | `্ব` (ba-fola) | (Removed) | Literal backslash followed by caret corrupted regex/LaTeX. Unescaped `^` correctly maps to `্ব`. |
| `yy` / `vv` | - | `y` / `v` | (Scoped to Bengali runs) | Global `PRE_CONVERSION_MAP` replacement corrupted English words (`savvy`, `revved`, `fluffy`). Restricted to Bengali-only runs. |
| `\\` | `U+005C U+005C` | `''` (stripped) | (Removed from global regex) | Stripping double backslashes destroyed LaTeX math formulas (`\\` linebreaks) and Windows paths. |

---

## 2. Complete Conversion Map (SutonnyMJ ANSI -> Unicode)

| Index | Bijoy Glyph | Codepoint(s) | Unicode Bengali | Unicode Codepoint(s) | Description / Role |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `Av` | U+0041 U+0076 | `আ` | U+0986 | Vowel (স্বরেবর্ণ) |
| 2 | `A` | U+0041 | `অ` | U+0985 | Vowel (স্বরেবর্ণ) |
| 3 | `B` | U+0042 | `ই` | U+0987 | Vowel (স্বরেবর্ণ) |
| 4 | `C` | U+0043 | `ঈ` | U+0988 | Vowel (স্বরেবর্ণ) |
| 5 | `D` | U+0044 | `উ` | U+0989 | Vowel (স্বরেবর্ণ) |
| 6 | `E` | U+0045 | `ঊ` | U+098A | Vowel (স্বরেবর্ণ) |
| 7 | `F` | U+0046 | `ঋ` | U+098B | Vowel (স্বরেবর্ণ) |
| 8 | `G` | U+0047 | `এ` | U+098F | Vowel (স্বরেবর্ণ) |
| 9 | `H` | U+0048 | `ঐ` | U+0990 | Vowel (স্বরেবর্ণ) |
| 10 | `I` | U+0049 | `ও` | U+0993 | Vowel (স্বরেবর্ণ) |
| 11 | `J` | U+004A | `ঔ` | U+0994 | Vowel (স্বরেবর্ণ) |
| 12 | `K` | U+004B | `ক` | U+0995 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 13 | `L` | U+004C | `খ` | U+0996 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 14 | `M` | U+004D | `গ` | U+0997 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 15 | `N` | U+004E | `ঘ` | U+0998 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 16 | `O` | U+004F | `ঙ` | U+0999 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 17 | `P` | U+0050 | `চ` | U+099A | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 18 | `Q` | U+0051 | `ছ` | U+099B | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 19 | `R` | U+0052 | `জ` | U+099C | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 20 | `S` | U+0053 | `ঝ` | U+099D | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 21 | `T` | U+0054 | `ঞ` | U+099E | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 22 | `U` | U+0055 | `ট` | U+099F | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 23 | `V` | U+0056 | `ঠ` | U+09A0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 24 | `W` | U+0057 | `ড` | U+09A1 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 25 | `X` | U+0058 | `ঢ` | U+09A2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 26 | `Y` | U+0059 | `ণ` | U+09A3 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 27 | `Z` | U+005A | `ত` | U+09A4 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 28 | `_` | U+005F | `থ` | U+09A5 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 29 | ``` | U+0060 | `দ` | U+09A6 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 30 | `a` | U+0061 | `ধ` | U+09A7 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 31 | `b` | U+0062 | `ন` | U+09A8 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 32 | `c` | U+0063 | `প` | U+09AA | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 33 | `d` | U+0064 | `ফ` | U+09AB | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 34 | `e` | U+0065 | `ব` | U+09AC | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 35 | `f` | U+0066 | `ভ` | U+09AD | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 36 | `g` | U+0067 | `ম` | U+09AE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 37 | `h` | U+0068 | `য` | U+09AF | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 38 | `i` | U+0069 | `র` | U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 39 | `j` | U+006A | `ল` | U+09B2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 40 | `k` | U+006B | `শ` | U+09B6 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 41 | `l` | U+006C | `ষ` | U+09B7 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 42 | `m` | U+006D | `স` | U+09B8 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 43 | `n` | U+006E | `হ` | U+09B9 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 44 | `o` | U+006F | `ড়` | U+09DC | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 45 | `p` | U+0070 | `ঢ়` | U+09DD | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 46 | `q` | U+0071 | `য়` | U+09DF | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 47 | `r` | U+0072 | `ৎ` | U+09CE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 48 | `s` | U+0073 | `ং` | U+0982 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 49 | `t` | U+0074 | `ঃ` | U+0983 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 50 | `u` | U+0075 | `ঁ` | U+0981 | Glyph / Symbol |
| 51 | `0` | U+0030 | `০` | U+09E6 | Digit (সংখ্যা) |
| 52 | `1` | U+0031 | `১` | U+09E7 | Digit (সংখ্যা) |
| 53 | `2` | U+0032 | `২` | U+09E8 | Digit (সংখ্যা) |
| 54 | `3` | U+0033 | `৩` | U+09E9 | Digit (সংখ্যা) |
| 55 | `4` | U+0034 | `৪` | U+09EA | Digit (সংখ্যা) |
| 56 | `5` | U+0035 | `৫` | U+09EB | Digit (সংখ্যা) |
| 57 | `6` | U+0036 | `৬` | U+09EC | Digit (সংখ্যা) |
| 58 | `7` | U+0037 | `৭` | U+09ED | Digit (সংখ্যা) |
| 59 | `8` | U+0038 | `৮` | U+09EE | Digit (সংখ্যা) |
| 60 | `9` | U+0039 | `৯` | U+09EF | Digit (সংখ্যা) |
| 61 | `•` | U+2022 | `ঙ্` | U+0999 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 62 | `v` | U+0076 | `া` | U+09BE | Vowel (স্বরেবর্ণ) |
| 63 | `w` | U+0077 | `ি` | U+09BF | Kar / Vowel Sign (কার) |
| 64 | `x` | U+0078 | `ী` | U+09C0 | Kar / Vowel Sign (কার) |
| 65 | `y` | U+0079 | `ু` | U+09C1 | Kar / Vowel Sign (কার) |
| 66 | `z` | U+007A | `ু` | U+09C1 | Kar / Vowel Sign (কার) |
| 67 | `“` | U+201C | `ু` | U+09C1 | Glyph / Symbol |
| 68 | `–` | U+2013 | `ু` | U+09C1 | Glyph / Symbol |
| 69 | `~` | U+007E | `ূ` | U+09C2 | Kar / Vowel Sign (কার) |
| 70 | `ƒ` | U+0192 | `ূ` | U+09C2 | Kar / Vowel Sign (কার) |
| 71 | `‚` | U+201A | `ূ` | U+09C2 | Glyph / Symbol |
| 72 | `„„` | U+201E U+201E | `ৃ` | U+09C3 | Kar / Vowel Sign (কার) |
| 73 | `„` | U+201E | `ৃ` | U+09C3 | Kar / Vowel Sign (কার) |
| 74 | `…` | U+2026 | `ৃ` | U+09C3 | Kar / Vowel Sign (কার) |
| 75 | `†` | U+2020 | `ে` | U+09C7 | Kar / Vowel Sign (কার) |
| 76 | `‡` | U+2021 | `ে` | U+09C7 | Kar / Vowel Sign (কার) |
| 77 | `ˆ` | U+02C6 | `ৈ` | U+09C8 | Kar / Vowel Sign (কার) |
| 78 | `‰` | U+2030 | `ৈ` | U+09C8 | Kar / Vowel Sign (কার) |
| 79 | `Š` | U+0160 | `ৗ` | U+09D7 | Kar / Vowel Sign (কার) |
| 80 | `\\|` | U+005C U+007C | `।` | U+0964 | Glyph / Symbol |
| 81 | `|` | U+007C | `।` | U+0964 | Punctuation / Modifier |
| 82 | `\\&` | U+005C U+0026 | `্‌` | U+09CD U+200C | Conjunct / Ligature (যুক্তাক্ষর) |
| 83 | `&` | U+0026 | `্` | U+09CD | Punctuation / Modifier |
| 84 | `\\^` | U+005C U+005E | `্ব` | U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 85 | `^` | U+005E | `্ব` | U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 86 | `ÿ` | U+00FF | `ক্ষ` | U+0995 U+09CD U+09B7 | Conjunct / Ligature (যুক্তাক্ষর) |
| 87 | `¯Í` | U+00AF U+00CD | `স্ত` | U+09B8 U+09CD U+09A4 | Conjunct / Ligature (যুক্তাক্ষর) |
| 88 | `¯^` | U+00AF U+005E | `স্ব` | U+09B8 U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 89 | `¤^` | U+00A4 U+005E | `ম্ব` | U+09AE U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 90 | `”Q` | U+201D U+0051 | `চ্ছ` | U+099A U+09CD U+099B | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 91 | `”P` | U+201D U+0050 | `চ্চ` | U+099A U+09CD U+099A | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 92 | `¯’` | U+00AF U+2019 | `স্থ` | U+09B8 U+09CD U+09A5 | Conjunct / Ligature (যুক্তাক্ষর) |
| 93 | `¯‹` | U+00AF U+2039 | `স্ক` | U+09B8 U+09CD U+0995 | Conjunct / Ligature (যুক্তাক্ষর) |
| 94 | `¯ú` | U+00AF U+00FA | `স্প` | U+09B8 U+09CD U+09AA | Conjunct / Ligature (যুক্তাক্ষর) |
| 95 | `¯œ` | U+00AF U+0153 | `স্ন` | U+09B8 U+09CD U+09A8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 96 | `¯¿` | U+00AF U+00BF | `স্ত্র` | U+09B8 U+09CD U+09A4 U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 97 | `¯cø` | U+00AF U+0063 U+00F8 | `স্প্ল` | U+09B8 U+09CD U+09AA U+09CD U+09B2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 98 | `¯c` | U+00AF U+0063 | `স্প` | U+09B8 U+09CD U+09AA | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 99 | `¯d` | U+00AF U+0064 | `স্ফ` | U+09B8 U+09CD U+09AB | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 100 | `¯U` | U+00AF U+0055 | `স্ট` | U+09B8 U+09CD U+099F | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 101 | `¯V` | U+00AF U+0056 | `ষ্ঠ` | U+09B7 U+09CD U+09A0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 102 | `¯g` | U+00AF U+0067 | `স্ম` | U+09B8 U+09CD U+09AE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 103 | `¯§` | U+00AF U+00A7 | `স্ম` | U+09B8 U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 104 | `m§` | U+006D U+00A7 | `স্ম` | U+09B8 U+09CD U+09AE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 105 | `m^` | U+006D U+005E | `স্ব` | U+09B8 U+09CD U+09AC | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 106 | `k^` | U+006B U+005E | `শ্ব` | U+09B6 U+09CD U+09AC | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 107 | `kª` | U+006B U+00AA | `শ্র` | U+09B6 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 108 | `k«` | U+006B U+00AB | `শ্র` | U+09B6 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 109 | `kø` | U+006B U+00F8 | `শ্ল` | U+09B6 U+09CD U+09B2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 110 | `k¦` | U+006B U+00A6 | `শ্ব` | U+09B6 U+09CD U+09AC | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 111 | `k¥` | U+006B U+00A5 | `শ্ম` | U+09B6 U+09CD U+09AE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 112 | `n¬` | U+006E U+00AC | `হ্ল` | U+09B9 U+09CD U+09B2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 113 | `j&j` | U+006A U+0026 U+006A | `ল্ল` | U+09B2 U+09CD U+09B2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 114 | `¤¢` | U+00A4 U+00A2 | `ম্ভ` | U+09AE U+09CD U+09AD | Conjunct / Ligature (যুক্তাক্ষর) |
| 115 | `¤§` | U+00A4 U+00A7 | `ম্ম` | U+09AE U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 116 | `e&e` | U+0065 U+0026 U+0065 | `ব্ব` | U+09AC U+09CD U+09AC | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 117 | `cø` | U+0063 U+00F8 | `প্ল` | U+09AA U+09CD U+09B2 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 118 | `cœ` | U+0063 U+0153 | `প্ন` | U+09AA U+09CD U+09A8 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 119 | `bœ` | U+0062 U+0153 | `ন্ন` | U+09A8 U+09CD U+09A8 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 120 | `b¥` | U+0062 U+00A5 | `ন্ম` | U+09A8 U+09CD U+09AE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 121 | `Y&Y` | U+0059 U+0026 U+0059 | `ণ্ণ` | U+09A3 U+09CD U+09A3 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 122 | `cÖ` | U+0063 U+00D6 | `প্র` | U+09AA U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 123 | `MÖ` | U+004D U+00D6 | `গ্র` | U+0997 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 124 | `K«` | U+004B U+00AB | `ক্র` | U+0995 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 125 | `c«` | U+0063 U+00AB | `প্র` | U+09AA U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 126 | `M«` | U+004D U+00AB | `গ্র` | U+0997 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 127 | `eª` | U+0065 U+00AA | `ব্র` | U+09AC U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 128 | `e«` | U+0065 U+00AB | `ব্র` | U+09AC U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 129 | `aª` | U+0061 U+00AA | `ধ্র` | U+09A7 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 130 | `a«` | U+0061 U+00AB | `ধ্র` | U+09A7 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 131 | `fª` | U+0066 U+00AA | `ভ্র` | U+09AD U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 132 | `f«` | U+0066 U+00AB | `ভ্র` | U+09AD U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 133 | `mª` | U+006D U+00AA | `স্র` | U+09B8 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 134 | `m«` | U+006D U+00AB | `স্র` | U+09B8 U+09CD U+09B0 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 135 | `n¥` | U+006E U+00A5 | `হ্ম` | U+09B9 U+09CD U+09AE | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 136 | `nœ` | U+006E U+0153 | `হ্ন` | U+09B9 U+09CD U+09A8 | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 137 | `÷&` | U+00F7 U+0026 | `স্ট্` | U+09B8 U+09CD U+099F U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 138 | `š¿` | U+0161 U+00BF | `ন্ত্র` | U+09A8 U+09CD U+09A4 U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 139 | `”P©` | U+201D U+0050 U+00A9 | `র্চ্চ` | U+09B0 U+09CD U+099A U+09CD U+099A | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 140 | `”Q©` | U+201D U+0051 U+00A9 | `র্চ্ছ` | U+09B0 U+09CD U+099A U+09CD U+099B | Consonant / Base (ব্যঞ্জনবর্ণ) |
| 141 | `šÍ` | U+0161 U+00CD | `ন্ত` | U+09A8 U+09CD U+09A4 | Conjunct / Ligature (যুক্তাক্ষর) |
| 142 | `š’` | U+0161 U+2019 | `ন্থ` | U+09A8 U+09CD U+09A5 | Conjunct / Ligature (যুক্তাক্ষর) |
| 143 | `š‘` | U+0161 U+2018 | `ন্তু` | U+09A8 U+09CD U+09A4 U+09C1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 144 | `‘` | U+2018 | `্তু` | U+09CD U+09A4 U+09C1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 145 | `’` | U+2019 | `্থ` | U+09CD U+09A5 | Conjunct / Ligature (যুক্তাক্ষর) |
| 146 | `‹` | U+2039 | `্ক` | U+09CD U+0995 | Conjunct / Ligature (যুক্তাক্ষর) |
| 147 | `Œ` | U+0152 | `্ক্র` | U+09CD U+0995 U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 148 | `”` | U+201D | `চ্` | U+099A U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 149 | `—` | U+2014 | `্ত` | U+09CD U+09A4 | Conjunct / Ligature (যুক্তাক্ষর) |
| 150 | `˜` | U+02DC | `দ্` | U+09A6 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 151 | `™` | U+2122 | `দ্` | U+09A6 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 152 | `š` | U+0161 | `ন্` | U+09A8 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 153 | `›` | U+203A | `ন্` | U+09A8 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 154 | `œ` | U+0153 | `্ন` | U+09CD U+09A8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 155 | `Ÿ` | U+0178 | `্ব` | U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 156 | `¡` | U+00A1 | `্ব` | U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 157 | `¢` | U+00A2 | `্ভ` | U+09CD U+09AD | Conjunct / Ligature (যুক্তাক্ষর) |
| 158 | `£` | U+00A3 | `্ভ্র` | U+09CD U+09AD U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 159 | `¤` | U+00A4 | `ম্` | U+09AE U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 160 | `¥` | U+00A5 | `্ম` | U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 161 | `¦` | U+00A6 | `্ব` | U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 162 | `§` | U+00A7 | `্ম` | U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 163 | `¨` | U+00A8 | `্য` | U+09CD U+09AF | Conjunct / Ligature (যুক্তাক্ষর) |
| 164 | `©` | U+00A9 | `র্` | U+09B0 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 165 | `ª` | U+00AA | `্র` | U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 166 | `«` | U+00AB | `্র` | U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 167 | `¬` | U+00AC | `্ল` | U+09CD U+09B2 | Conjunct / Ligature (যুক্তাক্ষর) |
| 168 | `\xad` | U+00AD | `্ল` | U+09CD U+09B2 | Conjunct / Ligature (যুক্তাক্ষর) |
| 169 | `®` | U+00AE | `ষ্` | U+09B7 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 170 | `¯` | U+00AF | `স্` | U+09B8 U+09CD | Conjunct / Ligature (যুক্তাক্ষর) |
| 171 | `°` | U+00B0 | `ক্ক` | U+0995 U+09CD U+0995 | Conjunct / Ligature (যুক্তাক্ষর) |
| 172 | `±` | U+00B1 | `ক্ট` | U+0995 U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 173 | `²` | U+00B2 | `ক্ষ্ণ` | U+0995 U+09CD U+09B7 U+09CD U+09A3 | Conjunct / Ligature (যুক্তাক্ষর) |
| 174 | `³` | U+00B3 | `ক্ত` | U+0995 U+09CD U+09A4 | Conjunct / Ligature (যুক্তাক্ষর) |
| 175 | `´` | U+00B4 | `ক্ম` | U+0995 U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 176 | `µ` | U+00B5 | `ক্র` | U+0995 U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 177 | `¶` | U+00B6 | `ক্ষ` | U+0995 U+09CD U+09B7 | Conjunct / Ligature (যুক্তাক্ষর) |
| 178 | `·` | U+00B7 | `ক্স` | U+0995 U+09CD U+09B8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 179 | `¸` | U+00B8 | `গু` | U+0997 U+09C1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 180 | `¹` | U+00B9 | `জ্ঞ` | U+099C U+09CD U+099E | Conjunct / Ligature (যুক্তাক্ষর) |
| 181 | `º` | U+00BA | `গ্দ` | U+0997 U+09CD U+09A6 | Conjunct / Ligature (যুক্তাক্ষর) |
| 182 | `»` | U+00BB | `গ্ধ` | U+0997 U+09CD U+09A7 | Conjunct / Ligature (যুক্তাক্ষর) |
| 183 | `¼` | U+00BC | `ঙ্ক` | U+0999 U+09CD U+0995 | Conjunct / Ligature (যুক্তাক্ষর) |
| 184 | `½` | U+00BD | `ঙ্গ` | U+0999 U+09CD U+0997 | Conjunct / Ligature (যুক্তাক্ষর) |
| 185 | `¾` | U+00BE | `জ্জ` | U+099C U+09CD U+099C | Conjunct / Ligature (যুক্তাক্ষর) |
| 186 | `¿` | U+00BF | `্ত্র` | U+09CD U+09A4 U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 187 | `À` | U+00C0 | `জ্ঝ` | U+099C U+09CD U+099D | Conjunct / Ligature (যুক্তাক্ষর) |
| 188 | `Á` | U+00C1 | `জ্ঞ` | U+099C U+09CD U+099E | Conjunct / Ligature (যুক্তাক্ষর) |
| 189 | `Â` | U+00C2 | `ঞ্চ` | U+099E U+09CD U+099A | Conjunct / Ligature (যুক্তাক্ষর) |
| 190 | `Ã` | U+00C3 | `ঞ্ছ` | U+099E U+09CD U+099B | Conjunct / Ligature (যুক্তাক্ষর) |
| 191 | `Ä` | U+00C4 | `ঞ্জ` | U+099E U+09CD U+099C | Conjunct / Ligature (যুক্তাক্ষর) |
| 192 | `Å` | U+00C5 | `ঞ্ঝ` | U+099E U+09CD U+099D | Conjunct / Ligature (যুক্তাক্ষর) |
| 193 | `Æ` | U+00C6 | `ট্ট` | U+099F U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 194 | `Ç` | U+00C7 | `ড্ড` | U+09A1 U+09CD U+09A1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 195 | `È` | U+00C8 | `ণ্ট` | U+09A3 U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 196 | `É` | U+00C9 | `ণ্ঠ` | U+09A3 U+09CD U+09A0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 197 | `Ê` | U+00CA | `ণ্ড` | U+09A3 U+09CD U+09A1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 198 | `Ë` | U+00CB | `ত্ত` | U+09A4 U+09CD U+09A4 | Conjunct / Ligature (যুক্তাক্ষর) |
| 199 | `Ì` | U+00CC | `ত্থ` | U+09A4 U+09CD U+09A5 | Conjunct / Ligature (যুক্তাক্ষর) |
| 200 | `Í` | U+00CD | `ত্ম` | U+09A4 U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 201 | `Î` | U+00CE | `ত্র` | U+09A4 U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 202 | `Ï` | U+00CF | `দ্দ` | U+09A6 U+09CD U+09A6 | Conjunct / Ligature (যুক্তাক্ষর) |
| 203 | `Ð` | U+00D0 | `-` | U+002D | Glyph / Symbol |
| 204 | `Ñ` | U+00D1 | `-` | U+002D | Glyph / Symbol |
| 205 | `Ò` | U+00D2 | `"` | U+0022 | Glyph / Symbol |
| 206 | `Ó` | U+00D3 | `"` | U+0022 | Glyph / Symbol |
| 207 | `Ô` | U+00D4 | `'` | U+0027 | Glyph / Symbol |
| 208 | `Õ` | U+00D5 | `'` | U+0027 | Glyph / Symbol |
| 209 | `Ö` | U+00D6 | `্র` | U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 210 | `×` | U+00D7 | `দ্ধ` | U+09A6 U+09CD U+09A7 | Conjunct / Ligature (যুক্তাক্ষর) |
| 211 | `Ø` | U+00D8 | `দ্ব` | U+09A6 U+09CD U+09AC | Conjunct / Ligature (যুক্তাক্ষর) |
| 212 | `Ù` | U+00D9 | `দ্ম` | U+09A6 U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
| 213 | `Ú` | U+00DA | `ন্ঠ` | U+09A8 U+09CD U+09A0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 214 | `Û` | U+00DB | `ন্ড` | U+09A8 U+09CD U+09A1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 215 | `Ü` | U+00DC | `ন্ধ` | U+09A8 U+09CD U+09A7 | Conjunct / Ligature (যুক্তাক্ষর) |
| 216 | `Ý` | U+00DD | `ন্স` | U+09A8 U+09CD U+09B8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 217 | `Þ` | U+00DE | `প্ট` | U+09AA U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 218 | `ß` | U+00DF | `প্ত` | U+09AA U+09CD U+09A4 | Conjunct / Ligature (যুক্তাক্ষর) |
| 219 | `à` | U+00E0 | `প্প` | U+09AA U+09CD U+09AA | Conjunct / Ligature (যুক্তাক্ষর) |
| 220 | `á` | U+00E1 | `প্স` | U+09AA U+09CD U+09B8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 221 | `â` | U+00E2 | `ব্জ` | U+09AC U+09CD U+099C | Conjunct / Ligature (যুক্তাক্ষর) |
| 222 | `ã` | U+00E3 | `ব্দ` | U+09AC U+09CD U+09A6 | Conjunct / Ligature (যুক্তাক্ষর) |
| 223 | `ä` | U+00E4 | `ব্ধ` | U+09AC U+09CD U+09A7 | Conjunct / Ligature (যুক্তাক্ষর) |
| 224 | `å` | U+00E5 | `ভ্র` | U+09AD U+09CD U+09B0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 225 | `æ` | U+00E6 | `ম্ন` | U+09AE U+09CD U+09A8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 226 | `ç` | U+00E7 | `ম্ফ` | U+09AE U+09CD U+09AB | Conjunct / Ligature (যুক্তাক্ষর) |
| 227 | `è` | U+00E8 | `্ন` | U+09CD U+09A8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 228 | `é` | U+00E9 | `ল্ক` | U+09B2 U+09CD U+0995 | Conjunct / Ligature (যুক্তাক্ষর) |
| 229 | `ê` | U+00EA | `ল্গ` | U+09B2 U+09CD U+0997 | Conjunct / Ligature (যুক্তাক্ষর) |
| 230 | `ë` | U+00EB | `ল্ট` | U+09B2 U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 231 | `ì` | U+00EC | `ল্ড` | U+09B2 U+09CD U+09A1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 232 | `í` | U+00ED | `ল্প` | U+09B2 U+09CD U+09AA | Conjunct / Ligature (যুক্তাক্ষর) |
| 233 | `î` | U+00EE | `ল্ফ` | U+09B2 U+09CD U+09AB | Conjunct / Ligature (যুক্তাক্ষর) |
| 234 | `ï` | U+00EF | `শু` | U+09B6 U+09C1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 235 | `ð` | U+00F0 | `শ্চ` | U+09B6 U+09CD U+099A | Conjunct / Ligature (যুক্তাক্ষর) |
| 236 | `ñ` | U+00F1 | `শ্ছ` | U+09B6 U+09CD U+099B | Conjunct / Ligature (যুক্তাক্ষর) |
| 237 | `ò` | U+00F2 | `ষ্ণ` | U+09B7 U+09CD U+09A3 | Conjunct / Ligature (যুক্তাক্ষর) |
| 238 | `ó` | U+00F3 | `ষ্ট` | U+09B7 U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 239 | `ô` | U+00F4 | `ষ্ঠ` | U+09B7 U+09CD U+09A0 | Conjunct / Ligature (যুক্তাক্ষর) |
| 240 | `õ` | U+00F5 | `ষ্ফ` | U+09B7 U+09CD U+09AB | Conjunct / Ligature (যুক্তাক্ষর) |
| 241 | `ö` | U+00F6 | `স্খ` | U+09B8 U+09CD U+0996 | Conjunct / Ligature (যুক্তাক্ষর) |
| 242 | `÷` | U+00F7 | `স্ট` | U+09B8 U+09CD U+099F | Conjunct / Ligature (যুক্তাক্ষর) |
| 243 | `ø` | U+00F8 | `স্ন` | U+09B8 U+09CD U+09A8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 244 | `ù` | U+00F9 | `স্ফ` | U+09B8 U+09CD U+09AB | Conjunct / Ligature (যুক্তাক্ষর) |
| 245 | `ú` | U+00FA | `্প` | U+09CD U+09AA | Conjunct / Ligature (যুক্তাক্ষর) |
| 246 | `û` | U+00FB | `হু` | U+09B9 U+09C1 | Conjunct / Ligature (যুক্তাক্ষর) |
| 247 | `ü` | U+00FC | `হৃ` | U+09B9 U+09C3 | Conjunct / Ligature (যুক্তাক্ষর) |
| 248 | `ý` | U+00FD | `হ্ন` | U+09B9 U+09CD U+09A8 | Conjunct / Ligature (যুক্তাক্ষর) |
| 249 | `þ` | U+00FE | `হ্ম` | U+09B9 U+09CD U+09AE | Conjunct / Ligature (যুক্তাক্ষর) |
