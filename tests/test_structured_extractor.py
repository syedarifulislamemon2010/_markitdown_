# -*- coding: utf-8 -*-
"""
Tests for Pluggable Structured Document Extraction Engine.
Includes 10 redacted samples for Government Gazette, Academic Papers, and Business Contracts.
"""

import unicodedata
import requests
from core.structured_extractor import (
    list_templates,
    get_template,
    extract_structured_data,
    bangabda_to_gregorian_approx,
    bn_to_en_digits,
    en_to_bn_digits,
)

# 10 Redacted Government Gazette Samples
GAZETTE_SAMPLES = [
    {
        "text": """
রেজিস্টার্ড নং ডি এ-১
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
কর্তৃপক্ষ কর্তৃক প্রকাশিত
মঙ্গলবার, ডিসেম্বর ১৫, ২০১৫
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
অর্থ মন্ত্রণালয়
অর্থ বিভাগ
প্রজ্ঞাপন
তারিখ, ০১ অগ্রহায়ণ ১৪২২ বঙ্গাব্দ / ১৫ নভেম্বর ২০১৫ খ্রিষ্টাব্দ
এস.আর.ও. নং ৩৫৫-আইন/২০১৫
বাংলাদেশ গেজেট অতিরিক্ত সংখ্যায় প্রকাশিত সরকারি চাকরি (বেতন ও ভাতাদি) আদেশ, ২০১৫ এর ধারা ৩ এবং ধারা ৪ এর অধীন...
""",
        "expected_sro": "৩৫৫-আইন/২০১৫",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "অর্থ বিভাগ",
        "expected_bangabda": "০১ অগ্রহায়ণ ১৪২২ বঙ্গাব্দ",
        "expected_gregorian": "১৫ নভেম্বর ২০১৫ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট, অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
আইন, বিচার ও সংসদ বিষয়ক মন্ত্রণালয়
লেজিসলেটিভ ও সংসদ বিষয়ক বিভাগ
এস. আর. ও. নং ১২০-আইন/২০১৮
তারিখ: ১২ চৈত্র ১৪২৪ বঙ্গাব্দ / ২৫ মার্চ ২০১৮ খ্রিষ্টাব্দ
দেওয়ানী কার্যবিধি আইনের ধারা ১১৫ এবং ধারা ১১৫ক অনুযায়ী...
""",
        "expected_sro": "১২০-আইন/২০১৮",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "আইন, বিচার ও সংসদ বিষয়ক মন্ত্রণালয়",
        "expected_bangabda": "১২ চৈত্র ১৪২৪ বঙ্গাব্দ",
        "expected_gregorian": "২৫ মার্চ ২০১৮ খ্রিষ্টাব্দ",
    },
    {
        "text": """
রেজিস্টার্ড নং ডি এ-১
বাংলাদেশ গেজেট (সাধারণ সংখ্যা)
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
জনপ্রশাসন মন্ত্রণালয়
প্রজ্ঞাপন
তারিখ: ১০ বৈশাখ ১৪২৬ বঙ্গাব্দ / ২৩ এপ্রিল ২০১৯ খ্রিষ্টাব্দ
এস.আর.ও. নং ৮৮-আইন/২০১৯
সরকারি কর্মচারী শৃঙ্খলা ও আপিল বিধিমালা, ২০১৮ এর ধারা ৭ এর বিধান মোতাবেক...
""",
        "expected_sro": "৮৮-আইন/২০১৯",
        "expected_type": "সাধারণ সংখ্যা",
        "expected_authority": "জনপ্রশাসন মন্ত্রণালয়",
        "expected_bangabda": "১০ বৈশাখ ১৪২৬ বঙ্গাব্দ",
        "expected_gregorian": "২৩ এপ্রিল ২০১৯ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
বাণিজ্য মন্ত্রণালয়
এস.আর.ও. নং ২১০-আইন/২০২০
তারিখ: ১৮ আষাঢ় ১৪২৭ বঙ্গাব্দ / ০২ জুলাই ২০২০ খ্রিষ্টাব্দ
আমদানি ও রপ্তানি নিয়ন্ত্রণ আইনের ধারা ৩ মোতাবেক সংশোধনী...
""",
        "expected_sro": "২১০-আইন/২০২০",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "বাণিজ্য মন্ত্রণালয়",
        "expected_bangabda": "১৮ আষাঢ় ১৪২৭ বঙ্গাব্দ",
        "expected_gregorian": "০২ জুলাই ২০২০ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
স্বাস্থ্য ও পরিবার কল্যাণ মন্ত্রণালয়
স্বাস্থ্য সেবা বিভাগ
এস.আর.ও. নং ১৪-আইন/২০২১
তারিখ: ৫ পৌষ ১৪২৭ বঙ্গাব্দ / ১৯ ডিসেম্বর ২০২০ খ্রিষ্টাব্দ
জাতীয় স্বাস্থ্য সুরক্ষা আইনের ধারা ৯ অনুযায়ী...
""",
        "expected_sro": "১৪-আইন/২০২১",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "স্বাস্থ্য ও পরিবার কল্যাণ মন্ত্রণালয়",
        "expected_bangabda": "৫ পৌষ ১৪২৭ বঙ্গাব্দ",
        "expected_gregorian": "১৯ ডিসেম্বর ২০২০ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
তথ্য ও সম্প্রচার মন্ত্রণালয়
এস.আর.ও. নং ৪৪-আইন/২০২২
তারিখ: ৩০ ফাল্গুন ১৪২৮ বঙ্গাব্দ / ১৪ মার্চ ২০২২ খ্রিষ্টাব্দ
জাতীয় সম্প্রচার নীতিমালার ধারা ১২ মোতাবেক...
""",
        "expected_sro": "৪৪-আইন/২০২২",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "তথ্য ও সম্প্রচার মন্ত্রণালয়",
        "expected_bangabda": "৩০ ফাল্গুন ১৪২৮ বঙ্গাব্দ",
        "expected_gregorian": "১৪ মার্চ ২০২২ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
গৃহায়ন ও গণপূর্ত মন্ত্রণালয়
এস.আর.ও. নং ৯৯-আইন/২০২৩
তারিখ: ১৫ মাঘ ১৪২৯ বঙ্গাব্দ / ২৯ জানুয়ারি ২০২৩ খ্রিষ্টাব্দ
ইমারত নির্মাণ আইনের ধারা ১৮ এর অধীন...
""",
        "expected_sro": "৯৯-আইন/২০২৩",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "গৃহায়ন ও গণপূর্ত মন্ত্রণালয়",
        "expected_bangabda": "১৫ মাঘ ১৪২৯ বঙ্গাব্দ",
        "expected_gregorian": "২৯ জানুয়ারি ২০২৩ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
ডাক, টেলিযোগাযোগ ও তথ্যপ্রযুক্তি মন্ত্রণালয়
তথ্য ও যোগাযোগ প্রযুক্তি বিভাগ
এস.আর.ও. নং ২৩৫-আইন/২০২৩
তারিখ: ২০ ভাদ্র ১৪৩০ বঙ্গাব্দ / ০৪ সেপ্টেম্বর ২০২৩ খ্রিষ্টাব্দ
সাইবার নিরাপত্তা আইনের ধারা ৪ এবং ধারা ৮ এর অধীন...
""",
        "expected_sro": "২৩৫-আইন/২০২৩",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "ডাক, টেলিযোগাযোগ ও তথ্যপ্রযুক্তি মন্ত্রণালয়",
        "expected_bangabda": "২০ ভাদ্র ১৪৩০ বঙ্গাব্দ",
        "expected_gregorian": "০৪ সেপ্টেম্বর ২০২৩ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
শিক্ষা মন্ত্রণালয়
মাধ্যমিক ও উচ্চ শিক্ষা বিভাগ
এস.আর.ও. নং ১৭৭-আইন/২০২৪
তারিখ: ২ জ্যৈষ্ঠ ১৪৩১ বঙ্গাব্দ / ১৬ মে ২০২৪ খ্রিষ্টাব্দ
বেসরকারি শিক্ষা প্রতিষ্ঠান এমপিও নীতিমালার ধারা ৫ অনুসারে...
""",
        "expected_sro": "১৭৭-আইন/২০২৪",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "শিক্ষা মন্ত্রণালয়",
        "expected_bangabda": "২ জ্যৈষ্ঠ ১৪৩১ বঙ্গাব্দ",
        "expected_gregorian": "১৬ মে ২০২৪ খ্রিষ্টাব্দ",
    },
    {
        "text": """
বাংলাদেশ গেজেট
অতিরিক্ত সংখ্যা
গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
পরিবেশ, বন ও জলবায়ু পরিবর্তন মন্ত্রণালয়
এস.আর.ও. নং ৩০২-আইন/২০২৪
তারিখ: ৭ আশ্বিন ১৪৩১ বঙ্গাব্দ / ২২ সেপ্টেম্বর ২০২৪ খ্রিষ্টাব্দ
পরিবেশ সংরক্ষণ আইনের ধারা ৪ এর ক্ষমতাবলে...
""",
        "expected_sro": "৩০২-আইন/২০২৪",
        "expected_type": "অতিরিক্ত সংখ্যা",
        "expected_authority": "পরিবেশ, বন ও জলবায়ু পরিবর্তন মন্ত্রণালয়",
        "expected_bangabda": "৭ আশ্বিন ১৪৩১ বঙ্গাব্দ",
        "expected_gregorian": "২২ সেপ্টেম্বর ২০২৪ খ্রিষ্টাব্দ",
    },
]


def test_template_registry():
    """Verify built-in templates are discovered and loaded."""
    templates = list_templates()
    assert len(templates) >= 3
    ids = [t["template_id"] for t in templates]
    assert "government_gazette" in ids
    assert "academic_paper" in ids
    assert "business_invoice_contract" in ids


def test_bangabda_date_conversion():
    """Verify Bangabda to Gregorian approximate date conversion."""
    res1 = bangabda_to_gregorian_approx("০১ অগ্রহায়ণ ১৪২২ বঙ্গাব্দ")
    assert res1 is not None
    assert "2015 CE" in res1

    res2 = bangabda_to_gregorian_approx("১২ চৈত্র ১৪২৪ বঙ্গাব্দ")
    assert res2 is not None
    assert "2018 CE" in res2

    assert bn_to_en_digits("১২৩৪৫") == "12345"
    assert en_to_bn_digits("67890") == "৬৭৮৯০"


def test_ten_gazette_samples_extraction():
    """Test 10 redacted Government Gazette samples against the gazette template."""
    for i, sample in enumerate(GAZETTE_SAMPLES, start=1):
        res = extract_structured_data(sample["text"], "government_gazette")
        assert res["success"] is True, f"Failed sample {i}"
        fields = res["fields"]

        assert fields["sro_number"]["value"] == sample["expected_sro"], (
            f"Sample {i} SRO mismatch: expected {sample['expected_sro']}, got {fields['sro_number']['value']}"
        )
        assert sample["expected_type"] in (fields["gazette_type"]["value"] or ""), (
            f"Sample {i} type mismatch: {fields['gazette_type']['value']}"
        )
        assert fields["date_bangabda"]["value"] == sample["expected_bangabda"], (
            f"Sample {i} Bangabda mismatch: {fields['date_bangabda']['value']}"
        )
        norm_expected_auth = unicodedata.normalize("NFC", sample["expected_authority"])
        norm_actual_auth = unicodedata.normalize("NFC", fields["authority"]["value"] or "")
        assert norm_expected_auth in norm_actual_auth, (
            f"Sample {i} Authority mismatch: {fields['authority']['value']}"
        )
        assert res["overall_confidence"] >= 0.70


def test_academic_and_business_templates():
    """Test academic paper and business contract templates."""
    academic_text = """
# Neural Machine Translation for Bengali-English Code-Switched Documents

Authors: Syed Ariful Islam, Dr. Rahat Khan
Affiliation: Department of Computer Science

Abstract:
In this work, we propose a novel transformer-based architecture specifically optimized for low-resource Bengali linguistic nuances and SutonnyMJ ANSI legacy encoding. Our experiments demonstrate a 4.2 BLEU improvement.

Keywords: Bengali NLP, Machine Translation, SutonnyMJ, Transformers

References:
1. Vaswani et al., Attention is All You Need, 2017.
2. Rahman et al., Bengali Corpus Analysis, 2021.
"""
    res_acad = extract_structured_data(academic_text, "academic_paper")
    assert res_acad["success"] is True
    assert "Neural Machine Translation" in res_acad["fields"]["title"]["value"]
    assert "Syed Ariful Islam" in res_acad["fields"]["authors"]["value"]
    assert "transformer-based" in res_acad["fields"]["abstract"]["value"]
    assert len(res_acad["fields"]["keywords"]["value"]) > 0

    business_text = """
Software Development Agreement / চুক্তিপত্র

Between: Acme Tech Solutions Ltd.
Party 2: Global Logistics Corporation

Date: October 15, 2025

Monetary Amounts:
Total Contract Value: BDT 1,250,000.00
Initial Deposit: $ 5,000.00

Terms & Conditions:
The software shall be delivered within 90 days of contract execution.
"""
    res_biz = extract_structured_data(business_text, "business_invoice_contract")
    assert res_biz["success"] is True
    assert "Agreement" in res_biz["fields"]["doc_type"]["value"]
    assert len(res_biz["fields"]["parties"]["value"]) >= 1
    assert any("1,250,000" in amt for amt in res_biz["fields"]["amounts"]["value"])


def test_api_extract_endpoint(server_url):
    """Test /api/extract and /api/extract/templates endpoints over HTTP."""
    # 1. Templates list
    tmpl_resp = requests.get(f"{server_url}/api/extract/templates", timeout=5.0)
    assert tmpl_resp.status_code == 200
    templates = tmpl_resp.json().get("templates", [])
    assert len(templates) >= 3

    # 2. Extract call
    payload = {
        "template_id": "government_gazette",
        "text": GAZETTE_SAMPLES[0]["text"]
    }
    resp = requests.post(f"{server_url}/api/extract", json=payload, timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["fields"]["sro_number"]["value"] == "৩৫৫-আইন/২০১৫"
    assert "markdown_table" in data
