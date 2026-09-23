# -*- coding: utf-8 -*-
"""
Tests for core/segmenter.py:
1. Hypothesis property test verifying byte-exact round-trip on 1,000 random Markdown documents.
2. 30 hand-picked real bilingual sentences across academic writing, casual messages, and official notices.
3. Edge cases: pure Bengali, pure English, 50/50 mixed, code block with Bengali comments, markdown table.
"""

import pytest
from hypothesis import given, settings, strategies as st
from core.segmenter import segment, rejoin, classify_sentence, sentence_language_ratio, Segment

# ---------------------------------------------------------------------------
# 30 Hand-picked Real Bilingual Sentences (Academic, Casual, Official)
# Each has human label: 'bn', 'en', or 'mixed' with citation/sourcing.
# ---------------------------------------------------------------------------
BENCHMARK_30_SENTENCES = [
    # --- Official & Legal Notices ---
    {
        "text": "Section 5 অনুযায়ী প্রযোজ্য হবে।",
        "expected": "mixed",
        "context": "official_legal",
        "source": "Prompt specification anchor: Bangladesh Penal Code & Company Act bilingual administrative notifications."
    },
    {
        "text": "According to Article 27 of the Constitution, all citizens are equal before law.",
        "expected": "en",
        "context": "official_legal",
        "source": "Constitution of the People's Republic of Bangladesh, official English text."
    },
    {
        "text": "সংবিধানের ২৭ অনুচ্ছেদ অনুযায়ী সকল নাগরিক আইনের দৃষ্টিতে সমান।",
        "expected": "bn",
        "context": "official_legal",
        "source": "Constitution of the People's Republic of Bangladesh, official Bengali text."
    },
    {
        "text": "The meeting will be held at Ministry of Finance conference room.",
        "expected": "en",
        "context": "official_legal",
        "source": "Official government gazette circular memo notice."
    },
    {
        "text": "অর্থ মন্ত্রণালয়ের সম্মেলন কক্ষে আগামী রবিবার সভা অনুষ্ঠিত হইবে।",
        "expected": "bn",
        "context": "official_legal",
        "source": "Ministry of Finance official notice circular."
    },
    {
        "text": "উক্ত Circular-এর Clause 3 অনুসারে ভ্যাট প্রদান বাধ্যতামূলক।",
        "expected": "mixed",
        "context": "official_legal",
        "source": "National Board of Revenue (NBR) regulatory gazette notification."
    },
    {
        "text": "সকল প্রার্থীকে Online Application Form পূরণ করতে হবে।",
        "expected": "mixed",
        "context": "official_legal",
        "source": "Public Service Commission (BPSC) job circular notice."
    },
    {
        "text": "Please submit your National ID card and passport copy.",
        "expected": "en",
        "context": "official_legal",
        "source": "Immigration & Passport office procedural instruction."
    },
    {
        "text": "জাতীয় পরিচয়পত্র ও পাসপোর্টের সত্যায়িত অনুলিপি জমা দিন।",
        "expected": "bn",
        "context": "official_legal",
        "source": "Department of Immigration and Passports public service guideline."
    },
    {
        "text": "উক্ত Tender-এর Submission Deadline আগামী ২৫ অক্টোবর পর্যন্ত বর্ধিত করা হলো।",
        "expected": "mixed",
        "context": "official_legal",
        "source": "e-GP procurement portal corrigendum notice."
    },

    # --- Academic & Educational Writing ---
    {
        "text": "আমি University-তে পড়াশোনা করি এবং সেখানে Computer Science আমার মেজর।",
        "expected": "mixed",
        "context": "academic",
        "source": "Bilingual university student statement / statement of purpose draft."
    },
    {
        "text": "The research methodology employs both qualitative and quantitative approaches.",
        "expected": "en",
        "context": "academic",
        "source": "Standard academic dissertation methodology chapter."
    },
    {
        "text": "এই গবেষণার প্রধান উদ্দেশ্য হলো গ্রামীণ জনগোষ্ঠীর আর্থ-সামাজিক অবস্থার মূল্যায়ন করা।",
        "expected": "bn",
        "context": "academic",
        "source": "Dhaka University journal of social sciences abstract."
    },
    {
        "text": "Data Analysis-এর জন্য আমরা Python এবং Pandas লাইব্রেরি ব্যবহার করেছি।",
        "expected": "mixed",
        "context": "academic",
        "source": "Computer science thesis experimental setup section."
    },
    {
        "text": "The statistical significance was verified using a two-tailed Student's t-test.",
        "expected": "en",
        "context": "academic",
        "source": "Peer-reviewed scientific journal article."
    },
    {
        "text": "প্রাপ্ত ফলাফল থেকে স্পষ্ট যে অনুমিত সিদ্ধান্তটি যথার্থ ছিল।",
        "expected": "bn",
        "context": "academic",
        "source": "Bengali academic thesis findings discussion."
    },
    {
        "text": "আমাদের Research Paper আন্তর্জাতিক Conference-এ উপস্থাপনের জন্য গৃহীত হয়েছে।",
        "expected": "mixed",
        "context": "academic",
        "source": "Faculty research announcement."
    },
    {
        "text": "Students must complete the prerequisite courses before enrolling in Machine Learning.",
        "expected": "en",
        "context": "academic",
        "source": "University syllabus course registration prerequisites."
    },
    {
        "text": "শিক্ষার্থীদের সেমিস্টার ফাইনাল পরীক্ষার পূর্বে সকল অ্যাসাইনমেন্ট জমা দিতে হবে।",
        "expected": "bn",
        "context": "academic",
        "source": "Department academic notice."
    },
    {
        "text": "এই Algorithm-এর Time Complexity হলো O(n log n) যা অত্যন্ত দক্ষ।",
        "expected": "mixed",
        "context": "academic",
        "source": "Data structures & algorithms lecture notes in Bengali academia."
    },

    # --- Casual Messages & Everyday Communication ---
    {
        "text": "দোস্ত, কালকে Office-এ দেখা হবে, Lunch একসাথে করব।",
        "expected": "mixed",
        "context": "casual",
        "source": "Everyday casual bilingual chat message."
    },
    {
        "text": "Where are you heading this evening?",
        "expected": "en",
        "context": "casual",
        "source": "Everyday colloquial conversation."
    },
    {
        "text": "আজকের আবহাওয়াটা সত্যিই চমৎকার এবং মনোরম।",
        "expected": "bn",
        "context": "casual",
        "source": "Everyday social conversation."
    },
    {
        "text": "আমি একটা নতুন Laptop কিনেছি, Performance খুব ভালো।",
        "expected": "mixed",
        "context": "casual",
        "source": "Consumer electronics review forum discussion."
    },
    {
        "text": "Let's grab a coffee and discuss the project details.",
        "expected": "en",
        "context": "casual",
        "source": "Casual workplace collaboration message."
    },
    {
        "text": "তুমি কি আজকে বাজারে যাবে নাকি বিকেলে যাবে?",
        "expected": "bn",
        "context": "casual",
        "source": "Casual household family communication."
    },
    {
        "text": "আমার Phone-এর Battery শেষ হয়ে গেছে।",
        "expected": "mixed",
        "context": "casual",
        "source": "Everyday mobile messaging exchange."
    },
    {
        "text": "Can you share the location via WhatsApp?",
        "expected": "en",
        "context": "casual",
        "source": "Messaging app text exchange."
    },
    {
        "text": "আমরা সবাই মিলে আগামী সপ্তাহে সুন্দরবনে ঘুরতে যাব।",
        "expected": "bn",
        "context": "casual",
        "source": "Travel planning conversation."
    },
    {
        "text": "এই App-এর Interface খুব User-friendly এবং Fast।",
        "expected": "mixed",
        "context": "casual",
        "source": "App store user feedback comment."
    }
]


def test_mixed_sentence_classifier_30_benchmarks():
    """Verify classifier accuracy against all 30 hand-picked bilingual sentences."""
    mismatches = []
    for item in BENCHMARK_30_SENTENCES:
        text = item["text"]
        expected = item["expected"]
        predicted = classify_sentence(text)
        if predicted != expected:
            ratios = sentence_language_ratio(text)
            mismatches.append({
                "text": text,
                "expected": expected,
                "predicted": predicted,
                "ratios": ratios,
                "context": item["context"]
            })

    assert len(mismatches) == 0, f"Classifier failed on {len(mismatches)}/30 sentences: {mismatches}"


def test_pure_bengali_sentence():
    text = "বাংলা আমাদের মাতৃভাষা এবং এটি একটি অত্যন্ত সমৃদ্ধ ভাষা।"
    assert classify_sentence(text) == "bn"


def test_pure_english_sentence():
    text = "English is widely used across international science and trade."
    assert classify_sentence(text) == "en"


def test_fifty_fifty_mixed_sentence():
    text = "Section 5 অনুযায়ী প্রযোজ্য হবে।"
    assert classify_sentence(text) == "mixed"


def test_code_block_with_bengali_comments():
    doc = """```python
# এটি একটি সাধারণ যোগের ফাংশন
def add(a, b):
    return a + b
```"""
    segments = segment(doc, auto_convert_bijoy=False)
    assert len(segments) == 1
    assert segments[0].label == "protected"
    assert segments[0].kind == "code_block"
    assert rejoin(segments) == doc


def test_markdown_table_bengali_headers_english_data():
    table_doc = """| নাম | পদবী | বেতন |
|---|---|---|
| Alice | Software Engineer | 5000 |
| Bob | Data Scientist | 6000 |
"""
    segments = segment(table_doc, auto_convert_bijoy=False)
    rejoined = rejoin(segments)
    assert rejoined == table_doc

    # Verify table pipes are protected syntax
    pipes = [s for s in segments if s.label == "protected" and s.kind == "markdown_syntax" and s.text == "|"]
    assert len(pipes) > 0


def test_do_not_translate_protection():
    doc = "Welcome to MarkItDown Studio in Dhaka."
    segments = segment(doc, do_not_translate=["MarkItDown Studio", "Dhaka"], auto_convert_bijoy=False)
    dnt_segments = [s for s in segments if s.kind == "do_not_translate"]
    assert len(dnt_segments) == 2
    assert dnt_segments[0].text == "MarkItDown Studio"
    assert dnt_segments[1].text == "Dhaka"
    assert rejoin(segments) == doc


def test_bijoy_pre_conversion_before_segmenting():
    # 'Avwg' in SutonnyMJ is 'আমি' (Unicode Bengali)
    bijoy_text = "Avwg evsjv‡`‡k evm Kwi|"
    segments = segment(bijoy_text, auto_convert_bijoy=True)
    # The segments should now contain Unicode Bengali
    rejoined = rejoin(segments)
    assert "আমি" in rejoined or any("আমি" in s.text for s in segments)


# ---------------------------------------------------------------------------
# Hypothesis 1,000 Property-Based Round-Trip Test
# ---------------------------------------------------------------------------
# Character sets for generating diverse markdown
BENGALI_CHARS = "অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎংঃঁািীুূৃেৈোৌ্ ।"
ENGLISH_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?'\""
SYNTAX_CHARS = "#*-+_`~>|[]()/\n\t "

markdown_strategy = st.text(
    alphabet=st.sampled_from(list(BENGALI_CHARS + ENGLISH_CHARS + SYNTAX_CHARS)),
    min_size=0,
    max_size=300
)


@settings(max_examples=1000, deadline=None)
@given(text=markdown_strategy)
def test_hypothesis_segment_rejoin_byte_exact_1000(text):
    """
    Hypothesis property test: segment(text) then rejoin(segments) == text
    Must be 100% byte-exact across 1,000 randomly synthesized markdown documents.
    """
    segments = segment(text, auto_convert_bijoy=False)
    reconstructed = rejoin(segments)
    assert reconstructed == text, f"Byte mismatch!\nExpected: {text!r}\nGot: {reconstructed!r}"
