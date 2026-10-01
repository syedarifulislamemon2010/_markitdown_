# -*- coding: utf-8 -*-
"""
Tests for core/bengali_repair.py: Bengali font, glyph & PDF ligature repair.
"""

import pytest
from core.bengali_repair import repair_broken_bengali


def test_strip_null_bytes_and_replacement_chars():
    text = "বাংলা\x00দেশ \ufeffঢাকা \ufffeচট্টগ্রাম \ufffdসিলেট"
    res = repair_broken_bengali(text)
    assert "\x00" not in res
    assert "\ufeff" not in res
    assert "\ufffe" not in res
    assert "\ufffd" not in res
    assert "বাংলাদেশ ঢাকা চট্টগ্রাম সিলেট" == res


def test_table_pipe_splits():
    text = "| তািরখ: ৩০ই জলু | াই, ২০২৬ ইং | ছু টেত থাকাকালীন অবস্থানঃ খলু | | না |"
    res = repair_broken_bengali(text)
    assert "জুলাই" in res
    assert "খুলনা" in res
    assert "জলু | াই" not in res
    assert "খলু | | না" not in res


def test_broken_pdf_ligatures():
    cases = [
        ("উপ-মহাব\x00বস্থাপক", "উপ-মহাব্যবস্থাপক"),
        ("সহকারী মহাব বস্থাপক", "সহকারী মহাব্যবস্থাপক"),
        ("অনলাইন ব\x00াংিকং িডপাট\x00েমন্ট", "অনলাইন ব্যাংকিং ডিপার্টমেন্ট"),
        ("জনতা ব\x00াংক িপএলিস,", "জনতা ব্যাংক পিএলসি,"),
        ("প্রধান কাযা\x00লয়, ঢাকা।", "প্রধান কার্যালয়, ঢাকা।"),
        ("কমস্থ\x00ল ত\x00ােগর", "কর্মস্থল ত্যাগের"),
        ("নিমি\x00ক ছু\x00টর জন\x00 আেবদন", "নৈমিত্তিক ছুটির জন্য আবেদন"),
        ("যথািবিহত স\x00ানপবূ ক িবনীত িনেবদন এই  য,", "যথাবিহিত সম্মানপূর্বক বিনীত নিবেদন এই  যে,"),
        ("পািরবািরক ও ব\x00িক্তগত জর\x00ির প্রেয়াজেন", "পারিবারিক ও ব্যক্তিগত জরুরি প্রয়োজনে"),
        ("অিফসার-আই\x00ট", "অফিসার-আইটি"),
        ("উে\x00খ\x00", "উল্লেখ্য"),
        ("ম\x00রু\x00ীর সপু ািরশ করা হেলা।", "মঞ্জুরীর সুপারিশ করা হলো।"),
        ("সেল ইনচাজ\x00", "সেল ইনচার্জ"),
    ]
    for inp, expected in cases:
        out = repair_broken_bengali(inp)
        assert expected in out, f"Failed for {inp}: got {out}, expected {expected}"


def test_preserve_normal_bengali_words():
    # Words like জনাব, ইসলাম should NOT be corrupted by জন্য/সেল rules
    text = "জনাব আরিফুল ইসলাম সেল ইনচার্জ"
    res = repair_broken_bengali(text)
    assert "জনাব" in res
    assert "ইসলাম" in res
    assert "সেল ইনচার্জ" in res
    assert "জন্যাব" not in res
    assert "ইসেলাম" not in res


def test_idempotent_on_valid_unicode():
    text = "উপ-মহাব্যবস্থাপক, অনলাইন ব্যাংকিং ডিপার্টমেন্ট, জনতা ব্যাংক পিএলসি, প্রধান কার্যালয়, ঢাকা।"
    res1 = repair_broken_bengali(text)
    res2 = repair_broken_bengali(res1)
    assert res1 == text
    assert res2 == text
