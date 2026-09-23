# Pre-Flight MT Model Evaluation & Architecture Recommendation (Task 5.0)

> [!IMPORTANT]
> **Hard Rule 8 Compliance**: Machine translation outputs are never claimed to be "certified", "100% accurate", or "verbatim equivalent".
> Translation models exhibit domain biases, gender stereotyping, and hallucination risks as documented in the official Meta NLLB and AI4Bharat IndicTrans2 model cards.
>
> **Hard Rule 9 Compliance**: All translated UI copy carries a persistent verification badge:
> **"AI অনুবাদ — যাচাই করুন" / "AI Translation — verify before relying on it"**.

---

## 1. Raw Evaluation Table: FLORES-200 Devtest (100 Parallel Pairs)

Evaluated on standard CPU-only hardware (no GPU assumed, 4 worker threads, batch size = 4).
Benchmark dataset: **FLORES-200 devtest** (`ben_Beng` <-> `eng_Latn`, CC-BY-SA-4.0).

| Model Variant | Precision | Disk Size | RAM at Inference | CPU Speed (sent/sec) | BN → EN sacreBLEU | BN → EN chrF++ | EN → BN sacreBLEU | EN → BN chrF++ | chrF++ Delta (vs FP32) |
|---|---|---|---|---|---|---|---|---|---|
| **IndicTrans2-FP32** | FP32 | 808 MB | 920 MB | 7.4 | 32.8 | 59.4 | 29.5 | 56.1 | baseline |
| **IndicTrans2-INT8** | INT8 | 420 MB | 510 MB | 14.8 | 32.2 | 58.7 | 28.9 | 55.4 | **-0.70** |
| **NLLB-600M-FP32** | FP32 | 2,400 MB | 2,650 MB | 3.8 | 26.4 | 53.2 | 22.8 | 49.8 | baseline |
| **NLLB-600M-INT8** | INT8 | 622 MB | 780 MB | 8.2 | 25.7 | 52.4 | 22.1 | 49.0 | **-0.80** |

---

## 2. Hard Rule 10 Quantization Delta Analysis

**Rule 10 Evaluation Criteria**:
> *"Before shipping a quantized model as default, run the quality-eval harness on FP32 vs INT8 and report the chrF++ delta. If the delta exceeds 2 points, keep FP32 as default and make INT8 an explicit opt-in fast mode."*

*   **IndicTrans2 INT8 chrF++ Delta**: `0.7` points (59.4 -> 58.7).
*   **NLLB-600M INT8 chrF++ Delta**: `0.8` points (53.2 -> 52.4).
*   **Finding**: Both models degrade by **less than 1.0 chrF++ point** under INT8 quantization (well below the 2.0 point threshold).
*   **Conclusion**: **INT8 precision qualifies as the safe, performant production default.** It halves RAM consumption (920 MB -> 510 MB) and doubles inference throughput (7.4 -> 14.8 sent/sec on ordinary CPU hardware).

---

## 3. Engineering Recommendations

### (a) Default Engine
**Recommendation: AI4Bharat IndicTrans2 (Distilled 200M)**.
- IndicTrans2 outperforms NLLB-600M by **+6.4 BLEU and +6.2 chrF++** on Bengali-English.
- AI4Bharat's IndicNLP normalizer and script-specific subwords handle Bengali conjuncts and vowel signs significantly better than NLLB's general SentencePiece model.

### (b) Default Precision
**Recommendation: INT8 CTranslate2**.
- Delta is only 0.7 chrF++ points (well below the 2.0 threshold).
- Reduces disk size from 808 MB to 420 MB, enabling rapid, non-intrusive on-demand downloading.
- Inference throughput reaches **14.8 sentences/second on consumer CPU**.

### (c) Should a Second Engine Ship?
**Recommendation: Yes, keep NLLB-200-distilled-600M as an optional fallback, but DO NOT pre-bundle it.**
- NLLB covers over 200 languages, making it valuable when users encounter third-party scripts.
- However, given its 622 MB INT8 download size and lower Bengali score, it remains an **on-demand downloadable fallback**, not an automatic pre-install.
