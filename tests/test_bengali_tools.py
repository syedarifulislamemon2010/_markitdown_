# -*- coding: utf-8 -*-
"""
Tests for Bengali NLP and Typography Suite (core/bengali_tools.py).
Includes 100 verified reference cases for Number <-> Words.
"""

from datetime import date
import pytest
from core.bengali_tools import (
    bangla_to_english_numerals,
    english_to_bangla_numerals,
    number_to_bangla_words,
    bangla_words_to_number,
    gregorian_to_bangabda,
    bangabda_to_gregorian,
    convert_document_dates,
    check_bengali_spelling,
    split_into_bengali_graphemes,
    grapheme_diff,
    grapheme_diff_html,
    detect_broken_conjuncts,
    normalize_bengali_text,
)

# 100 Reference cases for number-to-words
NUMBER_WORDS_100_CASES = [
    (0, "শূন্য"), (1, "এক"), (2, "দুই"), (3, "তিন"), (4, "চার"), (5, "পাঁচ"),
    (6, "ছয়"), (7, "সাত"), (8, "আট"), (9, "নয়"), (10, "দশ"),
    (11, "এগারো"), (12, "বারো"), (13, "তেরো"), (14, "চৌদ্দ"), (15, "পনেরো"),
    (16, "ষোলো"), (17, "সতেরো"), (18, "আঠারো"), (19, "উনিশ"), (20, "বিশ"),
    (21, "একুশ"), (22, "বাইশ"), (23, "তেইশ"), (24, "চব্বিশ"), (25, "পঁচিশ"),
    (26, "ছাব্বিশ"), (27, "সাতাশ"), (28, "আটাশ"), (29, "ঊনত্রিশ"), (30, "ত্রিশ"),
    (31, "একত্রিশ"), (32, "বত্রিশ"), (33, "তেত্রিশ"), (34, "চৌত্রিশ"), (35, "পঁয়ত্রিশ"),
    (36, "ছত্রিশ"), (37, "সাঁইত্রিশ"), (38, "আটত্রিশ"), (39, "ঊনচল্লিশ"), (40, "চল্লিশ"),
    (41, "একচল্লিশ"), (42, "বিয়াল্লিশ"), (43, "তেতাল্লিশ"), (44, "চুয়াল্লিশ"), (45, "পঁয়তাল্লিশ"),
    (46, "ছেচল্লিশ"), (47, "সাতচল্লিশ"), (48, "আটচল্লিশ"), (49, "ঊনপঞ্চাশ"), (50, "পঞ্চাশ"),
    (51, "একান্ন"), (52, "বায়ান্ন"), (53, "তিপ্পান্ন"), (54, "চুয়ান্ন"), (55, "পঞ্চান্ন"),
    (56, "ছাপ্পান্ন"), (57, "সাতান্ন"), (58, "আটান্ন"), (59, "ঊনষাট"), (60, "ষাট"),
    (61, "একষট্টি"), (62, "বাষট্টি"), (63, "তেষট্টি"), (64, "চৌষট্টি"), (65, "পঁয়ষট্টি"),
    (66, "ছেষট্টি"), (67, "সাতষট্টি"), (68, "আটষট্টি"), (69, "ঊনসত্তর"), (70, "সত্তর"),
    (71, "একাত্তর"), (72, "বাহাত্তর"), (73, "তিয়াত্তর"), (74, "চুয়াত্তর"), (75, "পঁচাত্তর"),
    (76, "ছিয়াত্তর"), (77, "সাতাত্তর"), (78, "আঠাত্তর"), (79, "ঊনআশি"), (80, "আশি"),
    (81, "একাশি"), (82, "বিরাশি"), (83, "তিরাশি"), (84, "চৌরাশি"), (85, "পঁচাশি"),
    (86, "ছিয়াশি"), (87, "সাতাশি"), (88, "অষ্টআশি"), (89, "ঊননব্বই"), (90, "নব্বই"),
    (91, "একানব্বই"), (92, "বিরানব্বই"), (93, "তিরানব্বই"), (94, "চুরানব্বই"), (95, "পঁচানব্বই"),
    (96, "ছিয়ানব্বই"), (97, "সাতানব্বই"), (98, "আটানব্বই"), (99, "নিরানব্বই"),
    (100, "এক শত"),
    # Higher scale milestones
    (105, "এক শত পাঁচ"),
    (1234, "এক হাজার দুই শত চৌত্রিশ"),
    (50000, "পঞ্চাশ হাজার"),
    (100000, "এক লাখ"),
    (2500000, "পঁচিশ লাখ"),
    (10000000, "এক কোটি"),
]


@pytest.mark.parametrize("num,expected_words", NUMBER_WORDS_100_CASES)
def test_number_to_bangla_words_100_cases(num, expected_words):
    """Verify number-to-words across 100 reference cases."""
    got = number_to_bangla_words(num)
    assert got == expected_words, f"Mismatch for {num}: got {got!r}, expected {expected_words!r}"


def test_bangla_words_to_number_roundtrip():
    """Verify reverse parsing of number words into integers."""
    assert bangla_words_to_number("এক হাজার দুই শত চৌত্রিশ") == 1234
    assert bangla_words_to_number("পঁচিশ লাখ") == 2500000
    assert bangla_words_to_number("এক কোটি") == 10000000
    assert bangla_words_to_number("শূন্য") == 0


def test_number_with_decimals_and_negatives():
    """Verify decimal and negative number-to-words handling."""
    assert number_to_bangla_words(-50) == "ঋণাত্মক পঞ্চাশ"
    assert number_to_bangla_words("12.34") == "বারো দশমিক তিন চার"
    assert number_to_bangla_words("১২.৩৪") == "বারো দশমিক তিন চার"


def test_numerals_bidirectional_transliteration():
    """Verify Bangla <-> English digits."""
    assert bangla_to_english_numerals("০১২৩৪৫৬৭৮৯") == "0123456789"
    assert english_to_bangla_numerals("0123456789") == "০১২৩৪৫৬৭৮৯"
    assert bangla_to_english_numerals("আইন নং ৩৫৫-আইন/২০১৫") == "আইন নং 355-আইন/2015"


def test_bangabda_calendar_conversion():
    """Verify Bangladesh Academy revised calendar conversion."""
    # 14 April 2026 is 1 Boishakh 1433
    d = date(2026, 4, 14)
    bday, bmonth, byear = gregorian_to_bangabda(d)
    assert (bday, bmonth, byear) == (1, "বৈশাখ", 1433)
    
    # Reverse conversion
    g_date = bangabda_to_gregorian(1, "বৈশাখ", 1433)
    assert g_date == d
    
    # 23 September 2026
    d2 = date(2026, 9, 23)
    bday2, bmonth2, byear2 = gregorian_to_bangabda(d2)
    assert bmonth2 == "আশ্বিন"
    assert byear2 == 1433
    
    # Document-wide 1-click conversion
    doc = "প্রজ্ঞাপন জারির তারিখ ২৩ সেপ্টেম্বর ২০২৬।"
    conv = convert_document_dates(doc, target="bangabda")
    assert "১৪৩৩ বঙ্গাব্দ" in conv


def test_hunspell_bengali_spellchecker():
    """Verify spellchecking and error suggestions."""
    clean_text = "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার"
    assert len(check_bengali_spelling(clean_text)) == 0
    
    typo_text = "বাংলদেশ সরকর"
    issues = check_bengali_spelling(typo_text)
    assert len(issues) >= 1
    words = [iss["word"] for iss in issues]
    assert "বাংলদেশ" in words or "সরকর" in words


def test_grapheme_diff():
    """Verify Unicode grapheme cluster diffing."""
    v1 = "বাংলাদেশ"
    v2 = "বাংলাদশ"
    diff = grapheme_diff(v1, v2)
    operations = [op for op, g in diff]
    assert "delete" in operations
    html = grapheme_diff_html(v1, v2)
    assert "<del" in html


def test_broken_conjunct_detector():
    """Verify broken conjunct, orphan halant and double kar detection."""
    clean = "শ্রীমঙ্গল"
    assert len(detect_broken_conjuncts(clean)) == 0
    
    broken = "বাংলা্ দেশ" # orphan halant
    issues = detect_broken_conjuncts(broken)
    assert any(iss["type"] == "orphan_halant" for iss in issues)
    
    double_kar = "ক্বাা" # double kar
    issues_kar = detect_broken_conjuncts(double_kar)
    assert any(iss["type"] == "double_vowel_sign" for iss in issues_kar)


def test_bengali_text_normalizer():
    """Verify normalization of decomposed য়, duplicate spaces, danda."""
    decomposed = "য\u09BC" # য + nukta
    assert normalize_bengali_text(decomposed) == "য়"
    
    pipe_text = "আমরা বাংলায় গান গাই | তোমরাও গাও ||"
    norm = normalize_bengali_text(pipe_text)
    assert "|" not in norm
    assert "।" in norm
    assert "॥" in norm
    
    spaces = "অনেক   ফাঁকা    স্থান"
    assert normalize_bengali_text(spaces) == "অনেক ফাঁকা স্থান"
