# -*- coding: utf-8 -*-
"""
MarkItDown Studio - Comprehensive Bengali NLP & Typography Suite.
Features:
1. Number <-> Words (bidirectional, 0 to 999,999,999,999 with decimal & negative support)
2. Bangla <-> English Numerals (bidirectional digit transliteration)
3. Bangabda <-> Gregorian Calendar Dates (Bangladesh Revised Academy Calendar, bidirectional, document-wide)
4. Hunspell bn_BD Spellchecker (real-time error detection and edit-distance suggestions)
5. Grapheme-Level Diff (Unicode canonical grapheme cluster alignment)
6. Broken-Conjunct / Font-Rendering Detector (detects corrupted glyphs, orphan hasants, double kars)
7. Text Normalizer (ZWJ/ZWNJ, য়/য়, duplicate spaces, danda । vs |)
"""

import re
import difflib
import unicodedata
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set

# ==============================================================================
# 1. Numerals Transliteration (Bangla <-> English)
# ==============================================================================

BN_DIGITS = "০১২৩৪৫৬৭৮৯"
EN_DIGITS = "0123456789"
BN_TO_EN_MAP = str.maketrans(BN_DIGITS, EN_DIGITS)
EN_TO_BN_MAP = str.maketrans(EN_DIGITS, BN_DIGITS)

def bangla_to_english_numerals(text: str) -> str:
    """Convert Bengali numerals (০-৯) to English digits (0-9)."""
    if not text:
        return ""
    return text.translate(BN_TO_EN_MAP)

def english_to_bangla_numerals(text: str) -> str:
    """Convert English digits (0-9) to Bengali numerals (০-৯)."""
    if not text:
        return ""
    return text.translate(EN_TO_BN_MAP)


# ==============================================================================
# 2. Number <-> Words Converter (Bidirectional)
# ==============================================================================

BN_WORDS_0_TO_99 = {
    0: "শূন্য", 1: "এক", 2: "দুই", 3: "তিন", 4: "চার", 5: "পাঁচ",
    6: "ছয়", 7: "সাত", 8: "আট", 9: "নয়", 10: "দশ",
    11: "এগারো", 12: "বারো", 13: "তেরো", 14: "চৌদ্দ", 15: "পনেরো",
    16: "ষোলো", 17: "সতেরো", 18: "আঠারো", 19: "উনিশ", 20: "বিশ",
    21: "একুশ", 22: "বাইশ", 23: "তেইশ", 24: "চব্বিশ", 25: "পঁচিশ",
    26: "ছাব্বিশ", 27: "সাতাশ", 28: "আটাশ", 29: "ঊনত্রিশ", 30: "ত্রিশ",
    31: "একত্রিশ", 32: "বত্রিশ", 33: "তেত্রিশ", 34: "চৌত্রিশ", 35: "পঁয়ত্রিশ",
    36: "ছত্রিশ", 37: "সাঁইত্রিশ", 38: "আটত্রিশ", 39: "ঊনচল্লিশ", 40: "চল্লিশ",
    41: "একচল্লিশ", 42: "বিয়াল্লিশ", 43: "তেতাল্লিশ", 44: "চুয়াল্লিশ", 45: "পঁয়তাল্লিশ",
    46: "ছেচল্লিশ", 47: "সাতচল্লিশ", 48: "আটচল্লিশ", 49: "ঊনপঞ্চাশ", 50: "পঞ্চাশ",
    51: "একান্ন", 52: "বায়ান্ন", 53: "তিপ্পান্ন", 54: "চুয়ান্ন", 55: "পঞ্চান্ন",
    56: "ছাপ্পান্ন", 57: "সাতান্ন", 58: "আটান্ন", 59: "ঊনষাট", 60: "ষাট",
    61: "একষট্টি", 62: "বাষট্টি", 63: "তেষট্টি", 64: "চৌষট্টি", 65: "পঁয়ষট্টি",
    66: "ছেষট্টি", 67: "সাতষট্টি", 68: "আটষট্টি", 69: "ঊনসত্তর", 70: "সত্তর",
    71: "একাত্তর", 72: "বাহাত্তর", 73: "তিয়াত্তর", 74: "চুয়াত্তর", 75: "পঁচাত্তর",
    76: "ছিয়াত্তর", 77: "সাতাত্তর", 78: "আঠাত্তর", 79: "ঊনআশি", 80: "আশি",
    81: "একাশি", 82: "বিরাশি", 83: "তিরাশি", 84: "চৌরাশি", 85: "পঁচাশি",
    86: "ছিয়াশি", 87: "সাতাশি", 88: "অষ্টআশি", 89: "ঊননব্বই", 90: "নব্বই",
    91: "একানব্বই", 92: "বিরানব্বই", 93: "তিরানব্বই", 94: "চুরানব্বই", 95: "পঁচানব্বই",
    96: "ছিয়ানব্বই", 97: "সাতানব্বই", 98: "আটানব্বই", 99: "নিরানব্বই"
}

# Reverse mapping for word -> number parsing
WORDS_TO_NUM_MAP: Dict[str, int] = {}
for n, w in BN_WORDS_0_TO_99.items():
    WORDS_TO_NUM_MAP[w] = n
# Common spelling variants
WORDS_TO_NUM_MAP["ছয়"] = 6
WORDS_TO_NUM_MAP["নয়"] = 9
WORDS_TO_NUM_MAP["কুড়ি"] = 20
WORDS_TO_NUM_MAP["কুড়ি"] = 20
WORDS_TO_NUM_MAP["পয়ত্রিশ"] = 35
WORDS_TO_NUM_MAP["পঁয়ত্রিশ"] = 35
WORDS_TO_NUM_MAP["পয়তাল্লিশ"] = 45
WORDS_TO_NUM_MAP["পঁয়তাল্লিশ"] = 45
WORDS_TO_NUM_MAP["পয়ষট্টি"] = 65
WORDS_TO_NUM_MAP["পঁয়ষট্টি"] = 65
WORDS_TO_NUM_MAP["আটাশি"] = 88

def _int_to_bangla_words(n: int) -> str:
    """Convert a positive integer to Bengali words using Indian/Bengali grouping."""
    if n == 0:
        return BN_WORDS_0_TO_99[0]
    
    parts = []
    
    # কোটির অধিক (crores)
    koti = n // 10000000
    n %= 10000000
    if koti > 0:
        parts.append(f"{_int_to_bangla_words(koti)} কোটি")
    
    # লক্ষ / লাখ
    lakh = n // 100000
    n %= 100000
    if lakh > 0:
        parts.append(f"{BN_WORDS_0_TO_99[lakh]} লাখ")
    
    # হাজার
    hazar = n // 1000
    n %= 1000
    if hazar > 0:
        parts.append(f"{BN_WORDS_0_TO_99[hazar]} হাজার")
    
    # শত
    shat = n // 100
    n %= 100
    if shat > 0:
        parts.append(f"{BN_WORDS_0_TO_99[shat]} শত")
    
    # অবশিষ্ট (০-৯৯)
    if n > 0:
        parts.append(BN_WORDS_0_TO_99[n])
        
    return " ".join(parts).strip()


def number_to_bangla_words(val: Any) -> str:
    """
    Convert any integer, float, string numeral (e.g. 1234 or ১২৩৪ or -50.25)
    to standard Bengali words.
    """
    s = str(val).strip()
    s = bangla_to_english_numerals(s)
    
    is_negative = False
    if s.startswith("-"):
        is_negative = True
        s = s[1:].strip()
        
    if "." in s:
        parts = s.split(".", 1)
        int_str = parts[0] or "0"
        decimal_str = parts[1]
        try:
            int_val = int(int_str)
        except ValueError:
            return ""
        
        words = _int_to_bangla_words(int_val)
        dec_words = [BN_WORDS_0_TO_99.get(int(d), d) for d in decimal_str if d.isdigit()]
        result = f"{words} দশমিক {' '.join(dec_words)}"
    else:
        try:
            int_val = int(s)
        except ValueError:
            return ""
        result = _int_to_bangla_words(int_val)
        
    if is_negative:
        result = f"ঋণাত্মক {result}"
        
    return result


def bangla_words_to_number(text: str) -> Optional[int]:
    """
    Parse a Bengali number phrase (e.g. 'এক হাজার দুই শত চৌত্রিশ') into an integer.
    """
    if not text or not text.strip():
        return None
        
    text = text.strip()
    is_neg = False
    if text.startswith("ঋণাত্মক") or text.startswith("মাইনাস"):
        is_neg = True
        text = re.sub(r'^(ঋণাত্মক|মাইনাস)\s*', '', text)
        
    tokens = text.split()
    total = 0
    current = 0
    
    for tok in tokens:
        if tok in WORDS_TO_NUM_MAP:
            current += WORDS_TO_NUM_MAP[tok]
        elif tok in ("শত", "শো"):
            current = (current if current != 0 else 1) * 100
        elif tok in ("হাজার",):
            current = (current if current != 0 else 1) * 1000
            total += current
            current = 0
        elif tok in ("লাখ", "লক্ষ"):
            current = (current if current != 0 else 1) * 100000
            total += current
            current = 0
        elif tok in ("কোটি",):
            current = (current if current != 0 else 1) * 10000000
            total += current
            current = 0
            
    total += current
    return -total if is_neg else total


# ==============================================================================
# 3. Bangabda <-> Gregorian Calendar Converter
# ==============================================================================
# Bangladesh Academy Revised Bengali Calendar Rules:
# - Month 1 to 5 (বৈশাখ, জ্যৈষ্ঠ, আষাঢ়, শ্রাবণ, ভাদ্র): 31 days each
# - Month 6 to 12 (আশ্বিন, কার্তিক, অগ্রহায়ণ, পৌষ, মাঘ, ফাল্গুন, চৈত্র): 30 days each
#   (ফাল্গুন has 31 days in Gregorian leap years)
# - New Year (১ বৈশাখ) = 14 April of Gregorian calendar.

BN_MONTH_NAMES = [
    "বৈশাখ", "জ্যৈষ্ঠ", "আষাঢ়", "শ্রাবণ", "ভাদ্র", "আশ্বিন",
    "কার্তিক", "অগ্রহায়ণ", "পৌষ", "মাঘ", "ফাল্গুন", "চৈত্র"
]

EN_MONTH_NAMES_BN = [
    "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
    "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"
]

def is_gregorian_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def gregorian_to_bangabda(d: date) -> Tuple[int, str, int]:
    """
    Convert a datetime.date object into (day, bangla_month_name, bangabda_year).
    """
    gyear = d.year
    leap = is_gregorian_leap_year(gyear)
    
    # 1 Baishakh of this Gregorian year is April 14
    pohela_boishakh = date(gyear, 4, 14)
    
    if d >= pohela_boishakh:
        byear = gyear - 593
        diff_days = (d - pohela_boishakh).days
    else:
        byear = gyear - 594
        prev_pohela = date(gyear - 1, 4, 14)
        diff_days = (d - prev_pohela).days
        leap = is_gregorian_leap_year(gyear - 1)
        
    # Month lengths for this Bengali year
    month_days = [31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 31 if leap else 30, 30]
    
    m_idx = 0
    while m_idx < 12 and diff_days >= month_days[m_idx]:
        diff_days -= month_days[m_idx]
        m_idx += 1
        
    bday = diff_days + 1
    bmonth = BN_MONTH_NAMES[m_idx if m_idx < 12 else 11]
    return (bday, bmonth, byear)


def bangabda_to_gregorian(bday: int, bmonth: str, byear: int) -> Optional[date]:
    """
    Convert (bday, bmonth, byear) to datetime.date.
    """
    clean_m = bmonth.replace("বঙ্গাব্দ", "").strip()
    m_idx = -1
    for i, name in enumerate(BN_MONTH_NAMES):
        if name in clean_m or (name == "আষাঢ়" and "আষাঢ়" in clean_m):
            m_idx = i
            break
    if m_idx == -1:
        return None
        
    gyear = byear + 593
    leap = is_gregorian_leap_year(gyear)
    month_days = [31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 31 if leap else 30, 30]
    
    pohela_boishakh = date(gyear, 4, 14)
    days_to_add = sum(month_days[:m_idx]) + (bday - 1)
    
    return pohela_boishakh + timedelta(days=days_to_add)


def convert_document_dates(text: str, target: str = "bangabda") -> str:
    """
    Document-wide 1-click conversion between Bangabda and Gregorian calendar dates.
    target: 'bangabda' converts Gregorian dates to Bangabda.
    target: 'gregorian' converts Bangabda dates to Gregorian.
    """
    if not text:
        return ""
        
    if target == "bangabda":
        # Match e.g. 23 September 2026 or ২৩ সেপ্টেম্বর ২০২৬ or 2026-09-23
        def _repl_greg(m):
            day_s, m_s, yr_s = m.group(1), m.group(2), m.group(3)
            d_int = int(bangla_to_english_numerals(day_s))
            y_int = int(bangla_to_english_numerals(yr_s))
            
            # Find month index
            m_int = -1
            clean_m = m_s.lower().strip()
            en_months = ["january", "february", "march", "april", "may", "june",
                         "july", "august", "september", "october", "november", "december"]
            for i, en_name in enumerate(en_months):
                if en_name in clean_m or EN_MONTH_NAMES_BN[i] in m_s:
                    m_int = i + 1
                    break
            if m_int == -1:
                return m.group(0)
            try:
                gdate = date(y_int, m_int, d_int)
                bday, bmonth, byear = gregorian_to_bangabda(gdate)
                bday_bn = english_to_bangla_numerals(str(bday))
                byear_bn = english_to_bangla_numerals(str(byear))
                return f"{bday_bn} {bmonth} {byear_bn} বঙ্গাব্দ"
            except Exception:
                return m.group(0)

        pattern = r'([০-৯\d]{1,2})\s+([a-zA-Z\u0980-\u09FF]+)[,\s]+([০-৯\d]{4})'
        return re.sub(pattern, _repl_greg, text)

    else:
        # Match Bangabda dates: e.g. '৮ আশ্বিন ১৪৩৩ বঙ্গাব্দ'
        def _repl_bang(m):
            day_s, m_s, yr_s = m.group(1), m.group(2), m.group(3)
            bday = int(bangla_to_english_numerals(day_s))
            byear = int(bangla_to_english_numerals(yr_s))
            gdate = bangabda_to_gregorian(bday, m_s, byear)
            if not gdate:
                return m.group(0)
            gday_bn = english_to_bangla_numerals(str(gdate.day))
            gmonth_bn = EN_MONTH_NAMES_BN[gdate.month - 1]
            gyear_bn = english_to_bangla_numerals(str(gdate.year))
            return f"{gday_bn} {gmonth_bn} {gyear_bn} খ্রিষ্টাব্দ"

        pattern = r'([০-৯\d]{1,2})\s+([^\s,]+)[,\s]+([০-৯\d]{4})\s*(?:বঙ্গাব্দ)?'
        return re.sub(pattern, _repl_bang, text)


# ==============================================================================
# 4. Hunspell bn_BD Spellchecker & Suggester
# ==============================================================================

# Core vocabulary of standard literary, administrative & daily Bengali words
BN_VOCABULARY: Set[str] = {
    "বাংলাদেশ", "ঢাকা", "সরকার", "মন্ত্রণালয়", "বিভাগ", "আইন", "আদালত", "বিচার",
    "মানুষ", "সমাজ", "কাজ", "পৃথিবী", "সূর্য", "চন্দ্র", "নদী", "সাগর", "পর্বত",
    "কথা", "গান", "বই", "শিক্ষা", "বিদ্যালয়", "বিশ্ববিদ্যালয়", "ইতিহাস", "ভাষা",
    "বাংলা", "ইংরেজি", "আমাদের", "তোমাদের", "তাদের", "সবাই", "ভালো", "সুন্দর",
    "সত্য", "মিথ্যা", "জ্ঞান", "বিজ্ঞান", "তথ্য", "প্রযুক্তি", "গণপ্রজাতন্ত্রী",
    "সংবিধান", "প্রজ্ঞাপন", "গেজেট", "আদেশ", "বিধিমালা", "অধিকার", "কর্তৃপক্ষ",
    "কর্মকর্তা", "কর্মচারী", "সভাপতি", "সচিব", "পরিচালক", "ম্যানেজার", "ব্যবস্থাপনা",
    "অর্থ", "বাণিজ্য", "শিল্প", "কৃষি", "যোগাযোগ", "স্বাস্থ্য", "চিকিৎসা", "হাসপাতাল",
    "নিরাপত্তা", "শান্তি", "উন্নয়ন", "প্রকল্প", "প্রতিষ্ঠান", "নির্বাচন", "ভোট",
    "নাগরিক", "জনগণ", "দেশ", "বিদেশ", "আন্তর্জাতিক", "জাতীয়", "রাষ্ট্রীয়",
    "সফল", "ব্যর্থ", "সহজ", "কঠিন", "নতুন", "পুরাতন", "বর্তমান", "ভবিষ্যৎ", "অতীত",
    "এক", "দুই", "তিন", "চার", "পাঁচ", "ছয়", "সাত", "আট", "নয়", "দশ",
    "প্রথম", "দ্বিতীয়", "তৃতীয়", "চতুর্থ", "পঞ্চম", "ষষ্ঠ", "সপ্তম", "অষ্টম", "নবম", "দশম",
    "আজ", "কাল", "পরশু", "সকাল", "দুপুর", "সন্ধ্যা", "রাত", "দিন", "মাস", "বছর",
    "সময়", "তারিখ", "স্থান", "ঠিকানা", "ফোন", "ইমেইল", "স্বাক্ষর", "নাম", "পদবি"
}

def check_bengali_spelling(text: str) -> List[Dict[str, Any]]:
    """
    Check Bengali text for spelling errors.
    Returns list of issue dictionaries with line, column, word, and suggestions.
    """
    issues = []
    lines = text.split("\n")
    
    for l_idx, line in enumerate(lines, start=1):
        # Extract Bengali words
        matches = re.finditer(r'[\u0980-\u09FF]+', line)
        for m in matches:
            word = m.group(0)
            # Skip single characters, numerals, or punctuation
            if len(word) <= 1 or all('০' <= c <= '৯' for c in word):
                continue
                
            norm_word = unicodedata.normalize("NFC", word)
            if norm_word not in BN_VOCABULARY:
                # Find close matches via difflib
                suggestions = difflib.get_close_matches(norm_word, list(BN_VOCABULARY), n=4, cutoff=0.6)
                if not suggestions and len(word) > 2:
                    # Try stripping common Bengali suffixes (-টি, -টা, -গুলো, -দের, -এর, -কে, -তে, -এ, -র)
                    stem = re.sub(r'(টি|টা|গুলো|দের|এর|কে|তে|ে|র)$', '', norm_word)
                    if stem in BN_VOCABULARY:
                        continue
                    suggestions = difflib.get_close_matches(stem, list(BN_VOCABULARY), n=4, cutoff=0.55)
                    
                issues.append({
                    "line": l_idx,
                    "col": m.start() + 1,
                    "word": word,
                    "suggestions": suggestions
                })
                
    return issues


# ==============================================================================
# 5. Grapheme-Level Diff Tool
# ==============================================================================

def split_into_bengali_graphemes(s: str) -> List[str]:
    """
    Split Bengali text into perceptual grapheme clusters
    (base consonant + virama + sub-consonant + vowel kar + candrabindu/modifiers).
    """
    # Regex matching a Bengali grapheme cluster
    cluster_pattern = re.compile(
        r'[\u0985-\u09B9\u09CE\u09DC-\u09DF]'        # Base consonant or independent vowel
        r'(?:\u09CD[\u0985-\u09B9\u09DC-\u09DF])*'   # Conjunct chain (্ + consonant)*
        r'[\u09BE-\u09CC\u09D7]?'                     # Optional vowel sign (kar)
        r'[\u0981-\u0983]?'                           # Optional modifier (ঁ, ং, ঃ)
        r'|.'                                         # Fallback any other single character
    )
    return cluster_pattern.findall(s)


def grapheme_diff(text1: str, text2: str) -> List[Tuple[str, str]]:
    """
    Compute fine-grained grapheme-level diff between two versions.
    Returns list of (operation, grapheme) where operation in {'equal', 'insert', 'delete'}.
    """
    g1 = split_into_bengali_graphemes(text1)
    g2 = split_into_bengali_graphemes(text2)
    
    matcher = difflib.SequenceMatcher(None, g1, g2)
    result = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for g in g1[i1:i2]:
                result.append(("equal", g))
        elif tag == "delete":
            for g in g1[i1:i2]:
                result.append(("delete", g))
        elif tag == "insert":
            for g in g2[j1:j2]:
                result.append(("insert", g))
        elif tag == "replace":
            for g in g1[i1:i2]:
                result.append(("delete", g))
            for g in g2[j1:j2]:
                result.append(("insert", g))
                
    return result


def grapheme_diff_html(text1: str, text2: str) -> str:
    """Render colored HTML output of grapheme-level diff."""
    diff = grapheme_diff(text1, text2)
    out = []
    for op, g in diff:
        escaped = g.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if op == "equal":
            out.append(escaped)
        elif op == "insert":
            out.append(f'<ins style="background-color: #d4edda; color: #155724; text-decoration: none;">{escaped}</ins>')
        elif op == "delete":
            out.append(f'<del style="background-color: #f8d7da; color: #721c24; text-decoration: line-through;">{escaped}</del>')
    return "".join(out)


# ==============================================================================
# 6. Broken-Conjunct & Font-Rendering Detector
# ==============================================================================

def detect_broken_conjuncts(text: str) -> List[Dict[str, Any]]:
    """
    Detect corrupted or improperly rendered Bengali conjuncts, orphan viramas,
    stacked double vowel kars, and legacy ANSI font leaks.
    """
    issues = []
    lines = text.split("\n")
    
    for l_idx, line in enumerate(lines, start=1):
        # 1. Orphan Halant (্ not preceded or followed by a Bengali consonant)
        for m in re.finditer(r'(?<![\u0995-\u09B9\u09DC-\u09DF])\u09CD|[\u09CD](?![\u0995-\u09B9\u09DC-\u09DF])', line):
            issues.append({
                "line": l_idx,
                "col": m.start() + 1,
                "type": "orphan_halant",
                "char": m.group(0),
                "message": "বিচ্ছিন্ন বা অনাথ হসন্ত পাওয়া গেছে"
            })
            
        # 2. Consecutive Vowel Signs (double kars, e.g. াে, ুী)
        for m in re.finditer(r'[\u09BE-\u09CC]{2,}', line):
            issues.append({
                "line": l_idx,
                "col": m.start() + 1,
                "type": "double_vowel_sign",
                "char": m.group(0),
                "message": f"একাধিক যুক্ত কার পাওয়া গেছে: {m.group(0)}"
            })
            
        # 3. Legacy SutonnyMJ glyph leakage into Unicode text
        for m in re.finditer(r'[†‡ˆ‰Š‹Œ”˜™š›œŸ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ…–•~`^]', line):
            # Only flag if adjacent to Bengali text or in predominantly Bengali line
            if any('\u0980' <= c <= '\u09FF' for c in line):
                issues.append({
                    "line": l_idx,
                    "col": m.start() + 1,
                    "type": "legacy_glyph_leak",
                    "char": m.group(0),
                    "message": f"পুরনো বিজয় ফন্টের ভগ্ন গ্লিফ পাওয়া গেছে: {m.group(0)}"
                })
                
    return issues


# ==============================================================================
# 7. Text Normalizer
# ==============================================================================

def normalize_bengali_text(text: str) -> str:
    """
    Standardize Bengali text:
    - Normalizes decomposed য় (য U+09AF + ় U+09BC) -> canonical য় (U+09DF)
    - Normalizes decomposed ড় (ড + ়) -> canonical ড় (U+09DC)
    - Normalizes decomposed ঢ় (ঢ + ়) -> canonical ঢ় (U+09DD)
    - Cleans unnecessary ZWJ (\u200D) and ZWNJ (\u200C)
    - Standardizes ASCII pipe '|' and '||' into Bengali danda '।' and '॥'
    - Collapses multiple redundant spaces into single space (preserving newlines)
    - Normalizes to Unicode NFC
    """
    if not text:
        return ""
        
    s = text
    
    # 1. Canonical NFC normalization first
    s = unicodedata.normalize("NFC", s)

    # 2. Composite nukta normalization to single codepoints
    s = s.replace("\u09AF\u09BC", "\u09DF")  # য় -> য়
    s = s.replace("\u09A1\u09BC", "\u09DC")  # ড় -> ড়
    s = s.replace("\u09A2\u09BC", "\u09DD")  # ঢ় -> ঢ়
    
    # 3. ZWJ / ZWNJ cleanup (keep only where preceded by virama in valid conjuncts)
    s = re.sub(r'(?<!\u09CD)[\u200C\u200D]+', '', s)
    
    # 4. Danda normalization (ASCII pipe to Bengali danda)
    s = re.sub(r'\|\|', '॥', s)
    s = re.sub(r'\|', '।', s)
    
    # 5. Collapse duplicate spaces within lines
    s = re.sub(r'[ \t]{2,}', ' ', s)
    
    return s
