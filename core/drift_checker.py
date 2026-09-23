# -*- coding: utf-8 -*-
"""
Back-Translation Drift Checker & Confidence Scorer.

Features:
  - Round-trip back-translation: A(src) -> B(tgt) -> A'(src)
  - Sentence-level chrF++ evaluation (word_order=2) via sacreBLEU
  - Meaning drift detection with configurable threshold (default: 40.0)
  - Calibration dataset with 20 known-good and 20 known-bad pairs
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
import sacrebleu


@dataclass
class DriftReport:
    original_text: str
    translated_text: str
    back_translated_text: str
    chrf_score: float
    is_drifted: bool
    threshold: float
    warning: Optional[str] = None


class DriftChecker:
    """Evaluates translation semantic fidelity via back-translation round-trip chrF++."""

    def __init__(self, threshold: float = 40.0):
        self.threshold = threshold

    def compute_chrf(self, hypothesis: str, reference: str) -> float:
        """Calculate chrF++ (character n-gram F-score with word 2-grams) between strings."""
        if not hypothesis or not reference:
            return 0.0
        # sacrebleu sentence_chrf with word_order=2 implements standard chrF++
        res = sacrebleu.sentence_chrf(hypothesis, [reference], word_order=2)
        return round(res.score, 2)

    def evaluate_drift(
        self,
        original_text: str,
        translated_text: str,
        back_translated_text: str
    ) -> DriftReport:
        """Compare original text with its back-translation to flag semantic drift."""
        score = self.compute_chrf(back_translated_text, original_text)
        is_drifted = score < self.threshold
        warning = (
            "⚠️ Possible meaning drift — review carefully before relying on this translation"
            if is_drifted else None
        )
        return DriftReport(
            original_text=original_text,
            translated_text=translated_text,
            back_translated_text=back_translated_text,
            chrf_score=score,
            is_drifted=is_drifted,
            threshold=self.threshold,
            warning=warning
        )


# ---------------------------------------------------------------------------
# Calibration Dataset: 20 Known-Good vs 20 Known-Bad Pairs
# ---------------------------------------------------------------------------
CALIBRATION_PAIRS: Dict[str, List[Dict[str, str]]] = {
    "known_good": [
        {"original": "আমি ভাত খাই।", "back_trans": "আমি ভাত খাই।", "note": "Exact identity"},
        {"original": "আজ আকাশ খুব মেঘলা।", "back_trans": "আজ আকাশ অত্যন্ত মেঘাচ্ছন্ন।", "note": "Synonym shift"},
        {"original": "ঢাকা বাংলাদেশের রাজধানী।", "back_trans": "ঢাকা হচ্ছে বাংলাদেশের রাজধানী।", "note": "Minor copula variation"},
        {"original": "আইনের দৃষ্টিতে সবাই সমান।", "back_trans": "আইনের চোখে সবাই সমান।", "note": "Colloquial synonym"},
        {"original": "বইটি টেবিলের উপরে আছে।", "back_trans": "বইটি টেবিলের ওপর রয়েছে।", "note": "Equivalent preposition"},
        {"original": "তিনি একজন ভালো শিক্ষক।", "back_trans": "তিনি একজন উত্তম শিক্ষক।", "note": "Adjective synonym"},
        {"original": "আমরা আগামীকাল সেখানে যাব।", "back_trans": "আমরা কাল সেখানে যাব।", "note": "Time adverb contraction"},
        {"original": "নদীটি অত্যন্ত গভীর ও স্রোতস্বিনী।", "back_trans": "নদীটি খুবই গভীর ও প্রবল স্রোতের।", "note": "Phrasing shift"},
        {"original": "স্বাস্থ্যই সকল সুখের মূল।", "back_trans": "স্বাস্থ্য হলো সকল সুখের মূল।", "note": "Proverb minor variation"},
        {"original": "সূর্য পূর্ব দিকে উদিত হয়।", "back_trans": "পূর্ব দিকে সূর্য ওঠে।", "note": "Word order permutation"},
        {"original": "The meeting will start at 10 AM.", "back_trans": "The meeting starts at 10 AM.", "note": "Tense slight shift"},
        {"original": "All citizens must pay taxes on time.", "back_trans": "Every citizen has to pay tax timely.", "note": "Synonym substitution"},
        {"original": "Water boils at 100 degrees Celsius.", "back_trans": "Water boils at 100°C.", "note": "Symbol abbreviation"},
        {"original": "The judge issued a stay order.", "back_trans": "A stay order was issued by the judge.", "note": "Passive voice shift"},
        {"original": "Please sign the contract document.", "back_trans": "Please sign the contract agreement.", "note": "Noun synonym"},
        {"original": "University admission will begin next week.", "back_trans": "College admission starts next week.", "note": "Minor near-synonym"},
        {"original": "He is suffering from severe fever.", "back_trans": "He has a high fever.", "note": "Clinical near-equivalent"},
        {"original": "Knowledge is power.", "back_trans": "Knowledge means power.", "note": "Proverb shift"},
        {"original": "The company reported record quarterly profit.", "back_trans": "The company announced record profits for the quarter.", "note": "Financial expansion"},
        {"original": "No parking allowed in front of the gate.", "back_trans": "Do not park vehicles before the gate.", "note": "Signboard variation"}
    ],
    "known_bad": [
        {"original": "আমি আদালতে মামলা দায়ের করেছি।", "back_trans": "আমি রান্নাঘরে খাবার রান্না করেছি।", "note": "Completely hallucinated domain (court vs kitchen)"},
        {"original": "কোম্পানি আইন অনুযায়ী এটি নিষিদ্ধ।", "back_trans": "কোম্পানি লাভজনকভাবে বিক্রি হয়েছে।", "note": "Legal prohibition turned into financial sale"},
        {"original": "তিনি জামিনে মুক্তি পেয়েছেন।", "back_trans": "তিনি কারাগারে মারা গেছেন।", "note": "Bail release turned into death in custody"},
        {"original": "রোগী এখন শঙ্কামুক্ত ও সুস্থ আছেন।", "back_trans": "রোগীর অবস্থা অত্যন্ত আশঙ্কাজনক।", "note": "Polarity inversion: healthy vs critical"},
        {"original": "আগামীকাল পরীক্ষা স্থগিত করা হলো।", "back_trans": "পরীক্ষা সঠিক সময়ে শুরু হবে।", "note": "Cancellation inverted to on-schedule"},
        {"original": "প্রকল্পের বাজেট বরাদ্দ কমানো হয়েছে।", "back_trans": "প্রকল্পের বাজেট দ্বিগুণ বৃদ্ধি পেয়েছে।", "note": "Budget cut inverted to budget doubling"},
        {"original": "বাদী সকল অভিযোগ প্রত্যাহার করেছেন।", "back_trans": "বাদী নতুন হত্যা মামলা দায়ের করেছেন।", "note": "Withdrawal turned into murder charge"},
        {"original": "খাদ্য সরবরাহ স্বাভাবিক রয়েছে।", "back_trans": "দেশে ভয়াবহ দুর্ভিক্ষ দেখা দিয়েছে।", "note": "Normal supply turned into famine"},
        {"original": "পুলিশ চোরকে গ্রেপ্তার করেছে।", "back_trans": "চোর পুলিশকে হত্যা করে পালিয়ে গেছে।", "note": "Agent-patient thematic role swap"},
        {"original": "বৃষ্টির কারণে খেলা বন্ধ রইল।", "back_trans": "সূর্যালোকে দর্শকরা আনন্দ উদযাপন করল।", "note": "Complete contextual hallucination"},
        {"original": "The defendant was acquitted of all charges.", "back_trans": "The defendant was sentenced to life in prison.", "note": "Acquittal inverted to life imprisonment"},
        {"original": "The bank account has a positive balance.", "back_trans": "The bank declared total bankruptcy.", "note": "Solvent balance inverted to bankruptcy"},
        {"original": "Vaccination is completely safe and effective.", "back_trans": "Vaccines cause widespread fatal poisonings.", "note": "Safety inverted to fatal poison"},
        {"original": "The flight was delayed due to heavy fog.", "back_trans": "The airplane crashed into the ocean.", "note": "Flight delay mutated to plane crash"},
        {"original": "Turn left at the traffic signal.", "back_trans": "Jump over the high brick wall.", "note": "Navigation hallucination"},
        {"original": "The agreement was signed voluntarily by both parties.", "back_trans": "The agreement was signed under armed robbery coercion.", "note": "Voluntary mutated to armed coercion"},
        {"original": "Inflation dropped to a five-year low.", "back_trans": "Hyperinflation destroyed the national currency overnight.", "note": "Disinflation mutated to hyperinflation"},
        {"original": "The laboratory test confirmed negative results.", "back_trans": "The patient tested positive for incurable cancer.", "note": "Negative diagnostic flipped to positive cancer"},
        {"original": "The fire was successfully extinguished within minutes.", "back_trans": "The entire city burned to ashes in the fire.", "note": "Contained incident mutated to cataclysm"},
        {"original": "School classes will resume on Monday.", "back_trans": "All educational institutions are permanently demolished.", "note": "Reopening inverted to demolition"}
    ]
}


def run_drift_calibration(threshold: float = 40.0) -> Dict[str, Any]:
    """
    Run threshold calibration against the 20 known-good and 20 known-bad pairs.
    Returns precision, recall, F1, and score distribution.
    """
    checker = DriftChecker(threshold=threshold)
    good_scores = []
    bad_scores = []

    # Known good: expect is_drifted == False
    true_negatives = 0
    false_positives = 0
    for item in CALIBRATION_PAIRS["known_good"]:
        score = checker.compute_chrf(item["back_trans"], item["original"])
        good_scores.append(score)
        if score >= threshold:
            true_negatives += 1
        else:
            false_positives += 1

    # Known bad: expect is_drifted == True
    true_positives = 0
    false_negatives = 0
    for item in CALIBRATION_PAIRS["known_bad"]:
        score = checker.compute_chrf(item["back_trans"], item["original"])
        bad_scores.append(score)
        if score < threshold:
            true_positives += 1
        else:
            false_negatives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "threshold": threshold,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "good_scores_mean": round(sum(good_scores) / len(good_scores), 2),
        "bad_scores_mean": round(sum(bad_scores) / len(bad_scores), 2),
        "min_good_score": min(good_scores),
        "max_bad_score": max(bad_scores),
    }
