# -*- coding: utf-8 -*-
"""
Bengali Encoding Converter: Bijoy / ANSI (SutonnyMJ) to Unicode.
Flawless conversion of legacy ANSI Bengali text to modern UTF-8 Unicode,
with safe bounds checking for conjuncts and re-orderings.
"""

import re
from typing import Dict

# 1. Pre-conversion replacements
PRE_CONVERSION_MAP: Dict[str, str] = {
    ' +': ' ',
    'yy': 'y',
    'vv': 'v',
    'y&': 'y',
    '„&': '„',
    '‡u': 'u‡',
    'wu': 'uw',
    ' ,': ',',
    ' \\|': '\\|',
    '\\\\ ': '',
    ' \\\\': '',
    '\\\\': '',
    '\n +': '\n',
    ' +\n': '\n',
    '\n\n\n\n\n': '\n\n',
    '\n\n\n\n': '\n\n',
    '\n\n\n': '\n\n',
}

# 2. Character mapping (Bijoy ANSI / SutonnyMJ to Unicode)
CONVERSION_MAP: Dict[str, str] = {
    # Vowels
    'Av': 'আ',
    'A': 'অ',
    'B': 'ই',
    'C': 'ঈ',
    'D': 'উ',
    'E': 'ঊ',
    'F': 'ঋ',
    'G': 'এ',
    'H': 'ঐ',
    'I': 'ও',
    'J': 'ঔ',
    # Consonants
    'K': 'ক',
    'L': 'খ',
    'M': 'গ',
    'N': 'ঘ',
    'O': 'ঙ',
    'P': 'চ',
    'Q': 'ছ',
    'R': 'জ',
    'S': 'ঝ',
    'T': 'ঞ',
    'U': 'ট',
    'V': 'ঠ',
    'W': 'ড',
    'X': 'ঢ',
    'Y': 'ণ',
    'Z': 'ত',
    '_': 'থ',
    '`': 'দ',
    'a': 'ধ',
    'b': 'ন',
    'c': 'প',
    'd': 'ফ',
    'e': 'ব',
    'f': 'ভ',
    'g': 'ম',
    'h': 'য',
    'i': 'র',
    'j': 'ল',
    'k': 'শ',
    'l': 'ষ',
    'm': 'স',
    'n': 'হ',
    'o': 'ড়',
    'p': 'ঢ়',
    'q': 'য়',
    'r': 'ৎ',
    's': 'ং',
    't': 'ঃ',
    'u': 'ঁ',
    # Digits
    '0': '০',
    '1': '১',
    '2': '২',
    '3': '৩',
    '4': '৪',
    '5': '৫',
    '6': '৬',
    '7': '৭',
    '8': '৮',
    '9': '৯',
    # Kars / Modifiers
    '•': 'ঙ্',
    'v': 'া',
    'w': 'ি',
    'x': 'ী',
    'y': 'ু',
    'z': 'ু',
    '“': 'ু',
    '–': 'ু',
    '~': 'ূ',
    'ƒ': 'ূ',
    '‚': 'ূ',
    '„„': 'ৃ',
    '„': 'ৃ',
    '…': 'ৃ',
    '†': 'ে',
    '‡': 'ে',
    'ˆ': 'ৈ',
    '‰': 'ৈ',
    'Š': 'ৗ',
    '\\|': '।',
    '|': '।',
    '\\&': '্‌',
    '&': '্',
    '\\^': '্ব',
    '^': '্ব',
    'ÿ': 'ক্ষ',
    # Conjuncts    # Multi-character conjunct overrides
    'šÍ': 'ন্ত',
    'š’': 'ন্থ',
    'š‘': 'ন্তু',
    '\\^': '্ব',
    '‘': '্তু',
    '’': '্থ',
    '‹': '্ক',
    'Œ': '্ক্র',
    '”': 'চ্',
    '—': '্ত',
    '˜': 'দ্',
    '™': 'দ্',
    'š': 'ন্',
    '›': 'ন্',
    'œ': '্ন',
    'Ÿ': '্ব',
    '¡': '্ব',
    '¢': '্ভ',
    '£': '্ভ্র',
    '¤': 'ম্',
    '¥': '্ম',
    '¦': '্ব',
    '§': '্ম',
    '¨': '্য',
    '©': 'র্',
    'ª': '্র',
    '«': '্র',
    '¬': '্ল',
    '­': '্ল',
    '®': 'ষ্',
    '¯': 'স্',
    '°': 'ক্ক',
    '±': 'ক্ট',
    '²': 'ক্ষ্ণ',
    '³': 'ক্ত',
    '´': 'ক্ম',
    'µ': 'ক্র',
    '¶': 'ক্ষ',
    '·': 'ক্স',
    '¸': 'গু',
    '¹': 'জ্ঞ',
    'º': 'গ্দ',
    '»': 'গ্ধ',
    '¼': 'ঙ্ক',
    '½': 'ঙ্গ',
    '¾': 'জ্জ',
    '¿': '্ত্র',
    'À': 'জ্ঝ',
    'Á': 'জ্ঞ',
    'Â': 'ঞ্চ',
    'Ã': 'ঞ্ছ',
    'Ä': 'ঞ্জ',
    'Å': 'ঞ্ঝ',
    'Æ': 'ট্ট',
    'Ç': 'ড্ড',
    'È': 'ণ্ট',
    'É': 'ণ্ঠ',
    'Ê': 'ণ্ড',
    'Ë': 'ত্ত',
    'Ì': 'ত্থ',
    'Í': 'ত্ম',
    'Î': 'ত্র',
    'Ï': 'দ্দ',
    'Ð': '-',
    'Ñ': '-',
    'Ò': '"',
    'Ó': '"',
    'Ô': "'",
    'Õ': "'",
    'Ö': '্র',
    '×': 'দ্ধ',
    'Ø': 'দ্ব',
    'Ù': 'দ্ম',
    'Ú': 'ন্ঠ',
    'Û': 'ন্ড',
    'Ü': 'ন্ধ',
    'Ý': 'ন্স',
    'Þ': 'প্ট',
    'ß': 'প্ত',
    'à': 'প্প',
    'á': 'প্স',
    'â': 'ব্জ',
    'ã': 'ব্দ',
    'ä': 'ব্ধ',
    'å': 'ভ্র',
    'æ': 'ম্ন',
    'ç': 'ম্ফ',
    'è': '্ন',
    'é': 'ল্ক',
    'ê': 'ল্গ',
    'ë': 'ল্ট',
    'ì': 'ল্ড',
    'í': 'ল্প',
    'î': 'ল্ফ',
    'ï': 'শু',
    'ð': 'শ্চ',
    'ñ': 'শ্ছ',
    'ò': 'ষ্ণ',
    'ó': 'ষ্ট',
    'ô': 'ষ্ঠ',
    'õ': 'ষ্ফ',
    'ö': 'স্খ',
    '÷': 'স্ট',
    'ø': 'স্ন',
    'ù': 'স্ফ',
    'ú': '্প',
    'û': 'হু',
    'ü': 'হৃ',
    'ý': 'হ্ন',
    'þ': 'হ্ম',
}

POST_CONVERSION_MAP: Dict[str, str] = {
    '০ঃ': '০:',
    '১ঃ': '১:',
    '২ঃ': '২:',
    '৩ঃ': '৩:',
    '৪ঃ': '৪:',
    '৫ঃ': '৫:',
    '৬ঃ': '৬:',
    '৭ঃ': '৭:',
    '৮ঃ': '৮:',
    '৯ঃ': '৯:',
    ' ঃ': ':',
    '\nঃ': '\n:',
    ']ঃ': ']:',
    '  ': ' ',
    'অা': 'আ',
    '্‌্‌': '্‌',
    '্্': '্',
}

PRE_KARS = {'ি', 'ৈ', 'ে'}
POST_KARS = {'া', 'ো', 'ৌ', 'ৗ', 'ু', 'ূ', 'ী', 'ৃ'}
CONSONANTS = {
    'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ',
    'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন',
    'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ',
    'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ'
}


def _safe_char(text: str, idx: int) -> str:
    if 0 <= idx < len(text):
        return text[idx]
    return ''


def _rearrange_unicode(text: str) -> str:
    """Rearrange vowel signs, ref, and conjunct positions to match Unicode grammar."""
    s = text
    i = 0
    while i < len(s):
        # 1. Ref (র + ্) reordering before consonant
        if (i < len(s) - 1 and _safe_char(s, i) == 'র' and _safe_char(s, i + 1) == '্'
                and _safe_char(s, i - 1) != '্'):
            j = 1
            while True:
                prev_char = _safe_char(s, i - j)
                prev_prev = _safe_char(s, i - j - 1)
                if i - j < 0:
                    break
                if prev_char in CONSONANTS and prev_prev == '্':
                    j += 2
                elif j == 1 and (prev_char in PRE_KARS or prev_char in POST_KARS):
                    j += 1
                else:
                    break

            start_idx = max(0, i - j)
            temp = s[:start_idx] + s[i:i + 2] + s[start_idx:i] + s[i + 2:]
            s = temp
            i += 1
            continue

        # 2. Vowel + HALANT + Consonant -> HALANT + Consonant + Vowel
        if (i > 0 and _safe_char(s, i) == '্'
                and (_safe_char(s, i - 1) in PRE_KARS or _safe_char(s, i - 1) in POST_KARS)
                and i < len(s) - 1):
            s = s[:i - 1] + s[i:i + 2] + s[i - 1] + s[i + 2:]

        # 3. RA + HALANT + Vowel -> Vowel + RA + HALANT
        if (i > 0 and i < len(s) - 1 and _safe_char(s, i) == '্'
                and _safe_char(s, i - 1) == 'র' and _safe_char(s, i - 2) != '্'
                and (_safe_char(s, i + 1) in PRE_KARS or _safe_char(s, i + 1) in POST_KARS)):
            s = s[:i - 1] + s[i + 1] + s[i - 1] + s[i] + s[i + 2:]

        # 4. Pre-kar (ি, ে, ৈ) reordering to post format for Unicode
        if i < len(s) - 1 and _safe_char(s, i) in PRE_KARS and not _safe_char(s, i + 1).isspace():
            j = 1
            while (i + j) < len(s) and _safe_char(s, i + j) in CONSONANTS:
                if (i + j + 1) < len(s) and _safe_char(s, i + j + 1) == '্':
                    j += 2
                else:
                    break

            temp = s[:i] + s[i + 1:i + j + 1]

            l = 0
            curr_kar = _safe_char(s, i)
            next_kar = _safe_char(s, i + j + 1)
            if curr_kar == 'ে' and next_kar == 'া':
                temp += 'ো'
                l = 1
            elif curr_kar == 'ে' and next_kar == 'ৗ':
                temp += 'ৌ'
                l = 1
            else:
                temp += curr_kar

            temp += s[i + j + l + 1:]
            s = temp
            i += j

        # 5. Chandrabindu / Nukta after kars
        if (i < len(s) - 1 and _safe_char(s, i) == 'ঁ'
                and _safe_char(s, i + 1) in POST_KARS):
            s = s[:i] + s[i + 1] + s[i] + s[i + 2:]

        i += 1
    return s


def bijoy_to_unicode(text: str) -> str:
    """
    Convert Bijoy / ANSI / SutonnyMJ encoded Bengali string to standard UTF-8 Unicode.
    Safe, fast, and handles full documents.
    """
    if not text:
        return ""

    # Protect (cid:X) from being converted to (পরফ:X)
    # Using Unicode Private Use Area (PUA) characters so they never collide with Bijoy maps
    cid_placeholders = []
    def _save_cid(match):
        idx = len(cid_placeholders)
        cid_placeholders.append(match.group(0))
        high = idx // 1000
        low = idx % 1000
        return f"\uE000{chr(0xE100 + high)}{chr(0xE400 + low)}\uE001"

    text = re.sub(r'\(?cid:\d+\)?', _save_cid, text, flags=re.IGNORECASE)

    # Pre-conversion replacements
    for pattern, replacement in PRE_CONVERSION_MAP.items():
        text = re.sub(pattern, replacement, text)

    # Character mapping (multi-char matches first)
    sorted_keys = sorted(CONVERSION_MAP.keys(), key=len, reverse=True)
    res = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for k in sorted_keys:
            if text.startswith(k, i):
                res.append(CONVERSION_MAP[k])
                i += len(k)
                matched = True
                break
        if not matched:
            res.append(text[i])
            i += 1

    intermediate = "".join(res)

    # Rearrange vowel and conjunct tokens into Unicode order
    rearranged = _rearrange_unicode(intermediate)

    # Post-conversion cleanup
    for pattern, replacement in POST_CONVERSION_MAP.items():
        rearranged = rearranged.replace(pattern, replacement)

    # Restore CID placeholders
    for idx, orig in enumerate(cid_placeholders):
        high = idx // 1000
        low = idx % 1000
        placeholder = f"\uE000{chr(0xE100 + high)}{chr(0xE400 + low)}\uE001"
        rearranged = rearranged.replace(placeholder, orig)

    return rearranged


BIJOY_SPECIALS = set('†‡ˆ‰Š‹Œ”˜™š›œŸ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþ')

BIJOY_EXACT_WORDS = {
    'eivei', 'cwiPvjK', 'gnvcwiPvjK', 'miKvi', 'wefvM', 'Dc‡Rjv', 'Zvs', 'wkÿv',
    'cixÿv', '†Pqvig¨vb', 'mnKvix', 'MYcÖRvZš¿x', 'Av‡e', 'evsjv', 'evsjvq', 'evsjvi',
    'Avgvi', 'Avwg', 'Avgv‡`i', 'Avgv‡K', 'Avgvq', 'Avcbvi', 'Avcbv‡`i', 'Mvb', 'MvB',
    '†mvbvi', '†Zvgvq', 'cÖ_g', 'wØZxq', 'ZvwiL', 'weeiY', 'mKj', 'Rb¨', 'hy³', 'wPÎ',
    'wbe©vPb', 'gvÎ', 'c„ôv', 'gš¿Yvjq', 'Awa', 'Awdm', 'AvBb', 'evsjv‡`k', 'evsjv‡`kx',
    'fvj', 'fv‡jv', 'K‡i', 'n‡e', 'GB', '†h', '†m', 'bv', 'hveZxq', 'mshy³',
    '¯^vÿi', 'Abywjwc', 'wmw×', 'MwVZ', 'nIqv', 'wewfbœ', 'we‡kl', 'welq', 'Dci',
    'AvaywbK', 'cÖKvk', 'msNwVZ', 'mswkøó', 'cÖavb', 'weMZ', 'cÖ`vb', 'Av‡e`b',
    'Av‡jvPbv', 'Dcgnv', 'wb‡qvM', 'weÁwß', 'cÎ', 'wek^vm', 'wk^vm', 'cÖwZ',
    'ZvB', 'fvB', 'hw`', 'wKš‘', 'KviY', 'Ges', 'A_ev', 'ev', 'wQj', 'Av‡Q', '†bB'
}

BIJOY_CONSONANT_KARS = re.compile(
    r'([K-Z][vwxy])|'                 # Uppercase consonant + kar e.g. Kv, Mv, Zv, Ky, My, Pv, Rv
    r'([jckdfgpq]v)|'                 # Lowercase consonant + aa-kar e.g. jv, kv, cv, fv, gv, qv, pv (NEVER in English)
    r'(vq)|(xq)|(sj)|'                # vq (ায়), xq (ীয়), sj (ংলা) - NEVER in English
    r'(w[K-Z])|'                      # i-kar before uppercase consonant e.g. wP, wM, wZ
    r'(\bw[kmpbftdcjqzly])|'          # Word starts with w + Bijoy consonant e.g. wk (কি), wb (নি), wg (মি), wP (চি), wj (লি)
    r'(&[K-Za-z])|'                   # Conjunct halant e.g. &K
    r'(\bAv[a-zA-Z])'                 # Starts with Av e.g. Avwg, Avgvi, Avcbvi
)

ENGLISH_COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
    'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
    'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been', 'has',
    'had', 'report', 'project', 'table', 'date', 'name', 'title', 'status',
    'director', 'general', 'executive', 'officer', 'department', 'ministry',
    'government', 'page', 'code', 'file', 'data', 'test', 'result', 'error',
    'warning', 'success', 'hello', 'world', 'summary', 'details', 'total'
}


def is_bijoy_token(token: str) -> bool:
    """Check if a token/word is written in legacy Bijoy / ANSI Bengali."""
    clean = token.strip(".,;:?!'\"()[]{}<>«»\u201c\u201d\u2018\u2019/\\|-*#_~1234567890")
    if not clean:
        return False
    # If already Unicode Bengali -> NOT Bijoy
    if any('\u0980' <= c <= '\u09FF' for c in clean):
        return False
    # If contains Bijoy extended ASCII character -> 100% Bijoy
    if any(c in BIJOY_SPECIALS for c in clean):
        return True
    # If in common English words -> NOT Bijoy
    if clean.lower() in ENGLISH_COMMON_WORDS:
        return False
    # If in exact Bijoy words
    if clean in BIJOY_EXACT_WORDS:
        return True
    # If matches Bijoy structural patterns
    if BIJOY_CONSONANT_KARS.search(clean):
        return True
    return False


def is_likely_bijoy(text: str) -> bool:
    """
    Intelligently detect if text contains legacy ANSI / Bijoy Bengali patterns.
    Uses token analysis, special character density, and structural heuristics.
    """
    if not text:
        return False

    # Check for Bijoy special characters (always 100% indicative of Bijoy)
    if any(c in BIJOY_SPECIALS for c in text):
        return True

    # If text already contains pure Unicode Bengali (> 15 chars) and no Bijoy specials,
    # it is already a modern Unicode document, not legacy ANSI!
    unicode_bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    if unicode_bengali_chars >= 15:
        return False

    # Check for known markers
    bijoy_markers = ['Avgvi', 'evsjv', 'wPÎ', 'cÖ', 'hy³', 'Avwg', '†mvbvi', '†Zvgvq', 'eivei', 'cwiPvjK', 'miKvi']
    for marker in bijoy_markers:
        if marker in text:
            return True

    # Check token-level sample (first 100 tokens)
    tokens = text.split()[:100]
    bijoy_count = sum(1 for t in tokens if is_bijoy_token(t))
    if bijoy_count >= 2:
        return True

    return False


def auto_convert_markdown(markdown_text: str) -> str:
    """
    Convert legacy ANSI/Bijoy Bengali to standard UTF-8 Unicode with full Markdown awareness.
    Preserves:
    - LaTeX Math equations ($$...$$ and $...$)
    - Fenced code blocks (``` ... ```)
    - Inline code (`...`)
    - URLs in links and images [text](url)
    - Markdown headings (#), blockquotes (>), lists (-, *, 1.), tables (|)
    - Existing Unicode Bengali and plain English words.
    """
    if not markdown_text:
        return ""

    # Fast bail-out if no Bijoy is present
    if not is_likely_bijoy(markdown_text):
        return markdown_text

    # 0. Protect LaTeX Math equations
    math_blocks = []
    def math_block_sub(match):
        math_blocks.append(match.group(0))
        return f"__MATH_BLOCK_{len(math_blocks)-1}__"

    text = re.sub(r'\$\$[\s\S]*?\$\$', math_block_sub, markdown_text)

    inline_maths = []
    def inline_math_sub(match):
        inline_maths.append(match.group(0))
        return f"__INLINE_MATH_{len(inline_maths)-1}__"

    text = re.sub(r'\$[^\$\n]+?\$', inline_math_sub, text)

    # 1. Protect code blocks
    code_blocks = []
    def code_block_sub(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    text = re.sub(r'```[\s\S]*?```', code_block_sub, text)

    # 2. Protect inline code
    inline_codes = []
    def inline_code_sub(match):
        inline_codes.append(match.group(0))
        return f"__INLINE_CODE_{len(inline_codes)-1}__"

    text = re.sub(r'`[^`\n]+`', inline_code_sub, text)

    # 3. Protect URLs inside markdown links/images [text](url)
    urls = []
    def url_sub(match):
        urls.append(match.group(2))
        return f"[{match.group(1)}](__URL_{len(urls)-1}__)"

    text = re.sub(r'\[(.*?)\]\((https?://[^\s)]+|file://[^\s)]+|/[^\s)]+)\)', url_sub, text)

    # 4. Process lines selectively
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("__CODE_BLOCK_"):
            processed_lines.append(line)
            continue

        # Check for standard Markdown block prefixes (heading, list bullet, task, quote)
        m = re.match(r'^(\s*(?:#{1,6}\s+|[-*+]\s+(?:\[[ xX]\]\s+)?|\d+\.\s+|>\s*))(.*)$', line)
        if m:
            prefix = m.group(1)
            content = m.group(2)
        else:
            prefix = ""
            content = line

        # If line is a markdown table row with pipes
        stripped_c = content.strip()
        if stripped_c.startswith('|') and stripped_c.endswith('|'):
            # Preserve table separator row e.g. | :--- | :--- |
            if re.match(r'^\|[\s:\-]+(?:\|[\s:\-]+)*\|$', stripped_c):
                processed_lines.append(line)
                continue
            cells = content.split('|')
            converted_cells = []
            for cell in cells:
                parts = re.split(r'(\s+|[.,;!?()[\]{}<>"\'/\\:])', cell)
                new_parts = []
                for p in parts:
                    if is_bijoy_token(p):
                        new_parts.append(bijoy_to_unicode(p))
                    else:
                        new_parts.append(p)
                converted_cells.append("".join(new_parts))
            processed_lines.append(prefix + "|".join(converted_cells))
            continue

        # Check tokens in content
        tokens = re.findall(r'\S+', content)
        if not tokens:
            processed_lines.append(line)
            continue

        bijoy_tokens = [t for t in tokens if is_bijoy_token(t)]
        if not bijoy_tokens:
            processed_lines.append(line)
            continue

        # Segment/token-level conversion for lines containing Bijoy
        parts = re.split(r'(\s+|[.,;!?()[\]{}<>"\'/\\:])', content)
        converted_parts = []
        for p in parts:
            if is_bijoy_token(p):
                converted_parts.append(bijoy_to_unicode(p))
            else:
                converted_parts.append(p)
        processed_lines.append(prefix + "".join(converted_parts))

    result = '\n'.join(processed_lines)

    # 5. Restore protected tokens
    for i, im in enumerate(inline_maths):
        result = result.replace(f"__INLINE_MATH_{i}__", im)
    for i, mb in enumerate(math_blocks):
        result = result.replace(f"__MATH_BLOCK_{i}__", mb)
    for i, u in enumerate(urls):
        result = result.replace(f"__URL_{i}__", u)
    for i, ic in enumerate(inline_codes):
        result = result.replace(f"__INLINE_CODE_{i}__", ic)
    for i, cb in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", cb)

    return result


def auto_convert_text(text: str) -> str:
    """
    Automatically converts text to Unicode if it appears to be ANSI / Bijoy.
    Leaves clean English or Unicode Bengali unchanged.
    """
    return auto_convert_markdown(text)


U_TO_B_CONJUNCTS = [
    ('ক্ষ্ণ', '²'),
    ('স্ত্র', '¯¿'),
    ('ন্ত্ৰ', 'š¿'),
    ('ন্ত্র', 'š¿'),
    ('্ত্র', '¿'),
    ('র্চ্চ', '”P©'),
    ('র্চ্ছ', '”Q©'),
    ('স্প্ল', '¯cø'),
    ('স্ট্', '÷&'),
    ('স্ফ', 'ù'),
    ('স্ক', '¯‹'),
    ('স্ত', '¯Í'),
    ('স্থ', '¯’'),
    ('স্প', '¯ú'),
    ('স্ব', '¯^'),
    ('স্ন', '¯œ'),
    ('শ্র', 'kª'),
    ('শ্ল', 'kø'),
    ('শ্ব', 'k¦'),
    ('শ্ম', 'k¥'),
    ('শু', 'ï'),
    ('শ্চ', 'ð'),
    ('শ্ছ', 'ñ'),
    ('ষ্ণ', 'ò'),
    ('ষ্ট', 'ó'),
    ('ষ্ঠ', 'ô'),
    ('ষ্ফ', 'õ'),
    ('স্খ', 'ö'),
    ('স্ট', '÷'),
    ('হ্ন', 'ý'),
    ('হ্ম', 'þ'),
    ('হৃ', 'ü'),
    ('হু', 'û'),
    ('হ্ল', 'n¬'),
    ('ল্ক', 'é'),
    ('ল্গ', 'ê'),
    ('ল্ট', 'ë'),
    ('ল্ড', 'ì'),
    ('ল্প', 'í'),
    ('ল্ফ', 'î'),
    ('ল্ল', 'j&j'),
    ('ম্ন', 'æ'),
    ('ম্ফ', 'ç'),
    ('ম্ব', '¤^'),
    ('ম্ভ', '¤¢'),
    ('ম্ম', '¤§'),
    ('ব্জ', 'â'),
    ('ব্দ', 'ã'),
    ('ব্ধ', 'ä'),
    ('ব্ব', 'e&e'),
    ('ভ্র', 'å'),
    ('প্ট', 'Þ'),
    ('প্ত', 'ß'),
    ('প্প', 'à'),
    ('প্স', 'á'),
    ('প্ল', 'cø'),
    ('প্ন', 'cœ'),
    ('ন্ত', 'šÍ'),
    ('ন্থ', 'š’'),
    ('ন্তু', 'š‘'),
    ('ন্দ', '›'),
    ('ন্ধ', 'Ü'),
    ('ন্স', 'Ý'),
    ('ন্ন', 'bœ'),
    ('ন্ম', 'b¥'),
    ('ণ্ঠ', 'É'),
    ('ণ্ট', 'È'),
    ('ণ্ড', 'Ê'),
    ('ণ্ণ', 'Y&Y'),
    ('ত্ত', 'Ë'),
    ('ত্থ', 'Ì'),
    ('ত্ম', 'Í'),
    ('ত্র', 'Î'),
    ('দ্দ', 'Ï'),
    ('দ্ধ', '×'),
    ('দ্ব', 'Ø'),
    ('দ্ম', 'Ù'),
    ('ঞ্চ', 'Â'),
    ('ঞ্ছ', 'Ã'),
    ('ঞ্জ', 'Ä'),
    ('ঞ্ঝ', 'Å'),
    ('ট্ট', 'Æ'),
    ('ড্ড', 'Ç'),
    ('জ্ঞ', '¹'),
    ('গ্দ', 'º'),
    ('গ্ধ', '»'),
    ('ঙ্ক', '¼'),
    ('ঙ্গ', '½'),
    ('জ্জ', '¾'),
    ('জ্ঝ', 'À'),
    ('ক্ত', '³'),
    ('ক্ম', '´'),
    ('ক্র', 'µ'),
    ('ক্ষ', '¶'),
    ('ক্স', '·'),
    ('ক্ক', '°'),
    ('ক্ট', '±'),
    ('চ্ছ', '”Q'),
    ('চ্চ', '”P'),
    ('প্র', 'cÖ'),
    ('গ্র', 'MÖ'),
]

U_TO_B_CHARS = {
    'অ': 'A', 'আ': 'Av', 'ই': 'B', 'ঈ': 'C', 'উ': 'D', 'ঊ': 'E', 'ঋ': 'F',
    'এ': 'G', 'ঐ': 'H', 'ও': 'I', 'ঔ': 'J',
    'ক': 'K', 'খ': 'L', 'গ': 'M', 'ঘ': 'N', 'ঙ': 'O',
    'চ': 'P', 'ছ': 'Q', 'জ': 'R', 'ঝ': 'S', 'ঞ': 'T',
    'ট': 'U', 'ঠ': 'V', 'ড': 'W', 'ঢ': 'X', 'ণ': 'Y',
    'ত': 'Z', 'থ': '_', 'দ': '`', 'ধ': 'a', 'ন': 'b',
    'প': 'c', 'ফ': 'd', 'ব': 'e', 'ভ': 'f', 'ম': 'g',
    'য': 'h', 'র': 'i', 'ল': 'j', 'শ': 'k', 'ষ': 'l',
    'স': 'm', 'হ': 'n', 'ড়': 'o', 'ঢ়': 'p', 'য়': 'q',
    'ৎ': 'r', 'ং': 's', 'ঃ': 't', 'ঁ': 'u',
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
    '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
    'া': 'v', 'ী': 'x', 'ু': 'y', 'ূ': '~', 'ৃ': '„',
    '।': '|', '্': '&',
}


def unicode_to_bijoy(text: str) -> str:
    """
    Convert Unicode Bengali text to legacy Bijoy / ANSI (SutonnyMJ).
    Guarantees English words, URLs, code, and numbers are 100% UNTOUCHED.
    """
    if not text:
        return ""

    def convert_bengali_run(b_text: str) -> str:
        s = b_text

        # 1. Apply multi-character conjuncts
        for u_conj, b_conj in U_TO_B_CONJUNCTS:
            s = s.replace(u_conj, b_conj)

        # 2. General Ra-fola / Ya-fola / Ba-fola
        s = re.sub(r'([ক-হ])্\s*র', r'\1ª', s)
        s = re.sub(r'([ক-হ])্\s*য', r'\1¨', s)
        s = s.replace('্য', '¨')
        s = re.sub(r'([ক-হ])্\s*ব', r'\1^', s)

        # 3. Pre-kar reordering (Move to front of consonant cluster)
        CLUSTER = r'((?:[ক-হa-zA-Z\u00C0-\u017F²³´µ¶·¹º»¼½¾¿ÀÂÃÄÅÆÇÈÉÊËÌÍÎÏ×ØÙÚÛÜÝÞßàáâãäåæçéêëìíîïðñòóôõö÷øùûüýþš¯ª¨^°±”][&্])*[ক-হa-zA-Z\u00C0-\u017F²³´µ¶·¹º»¼½¾¿ÀÂÃÄÅÆÇÈÉÊËÌÍÎÏ×ØÙÚÛÜÝÞßàáâãäåæçéêëìíîïðñòóôõö÷øùûüýþš¯ª¨^°±”])'

        # Ref with pre-kar: র্ + Cluster + ি -> w + Cluster + ©
        s = re.sub(r'র্' + CLUSTER + r'ি', r'w\1©', s)
        s = re.sub(r'র্' + CLUSTER + r'ে', r'†\1©', s)
        s = re.sub(r'র্' + CLUSTER + r'ৈ', r'ˆ\1©', s)
        # Ref alone: র্ + Cluster -> Cluster + ©
        s = re.sub(r'র্' + CLUSTER, r'\1©', s)

        # Standard Pre-kars:
        s = re.sub(CLUSTER + r'ো', r'†\1v', s)
        s = re.sub(CLUSTER + r'ৌ', r'†\1Š', s)
        s = re.sub(CLUSTER + r'ে', r'†\1', s)
        s = re.sub(CLUSTER + r'ি', r'w\1', s)
        s = re.sub(CLUSTER + r'ৈ', r'ˆ\1', s)

        # 4. Handle য় (ya + nukta / Yya) -> q
        s = s.replace('য়', 'q')
        s = s.replace('য়', 'q')

        # 5. Map remaining individual Unicode characters
        res = []
        for char in s:
            res.append(U_TO_B_CHARS.get(char, char))

        return "".join(res)

    # Process only Bengali characters; preserve all English words, code, punctuation
    parts = re.split(r'([\u0980-\u09FF]+)', text)
    converted_parts = []
    for p in parts:
        if any('\u0980' <= c <= '\u09FF' for c in p):
            converted_parts.append(convert_bengali_run(p))
        else:
            converted_parts.append(p)

    return "".join(converted_parts)


def auto_convert_unicode_to_bijoy_markdown(markdown_text: str) -> str:
    """
    Convert Markdown content from Unicode to Bijoy (ANSI) while strictly preserving:
    - Code blocks and inline code
    - URLs and markdown syntax
    - English words and numbers
    """
    if not markdown_text:
        return ""

    # Protect code blocks
    code_blocks = []
    def code_block_sub(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    text = re.sub(r'```[\s\S]*?```', code_block_sub, markdown_text)

    # Protect inline code
    inline_codes = []
    def inline_code_sub(match):
        inline_codes.append(match.group(0))
        return f"__INLINE_CODE_{len(inline_codes)-1}__"

    text = re.sub(r'`[^`\n]+`', inline_code_sub, text)

    # Protect URLs
    urls = []
    def url_sub(match):
        urls.append(match.group(2))
        return f"[{match.group(1)}](__URL_{len(urls)-1}__)"

    text = re.sub(r'\[(.*?)\]\((https?://[^\s)]+|file://[^\s)]+|/[^\s)]+)\)', url_sub, text)

    # Convert only Unicode Bengali segments
    converted = unicode_to_bijoy(text)

    # Restore protected tokens
    for i, u in enumerate(urls):
        converted = converted.replace(f"__URL_{i}__", u)
    for i, ic in enumerate(inline_codes):
        converted = converted.replace(f"__INLINE_CODE_{i}__", ic)
    for i, cb in enumerate(code_blocks):
        converted = converted.replace(f"__CODE_BLOCK_{i}__", cb)

    return converted
