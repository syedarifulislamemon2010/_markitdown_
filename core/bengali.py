# -*- coding: utf-8 -*-
"""
Bengali Encoding Converter: Bijoy / ANSI (SutonnyMJ) to Unicode.
Flawless conversion of legacy ANSI Bengali text to modern UTF-8 Unicode,
with safe bounds checking for conjuncts and re-orderings.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any

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
    '|': '।',
    '&': '্',
    '^': '্ব',
    'ÿ': 'ক্ষ',
    # Conjuncts    # Multi-character conjunct overrides
    '¯Í': 'স্ত',
    '¯^': 'স্ব',
    '¤^': 'ম্ব',
    '”Q': 'চ্ছ',
    '”P': 'চ্চ',
    '¯’': 'স্থ',
    '¯‹': 'স্ক',
    '¯ú': 'স্প',
    '¯œ': 'স্ন',
    '¯¿': 'স্ত্র',
    '¯cø': 'স্প্ল',
    '¯c': 'স্প',
    '¯d': 'স্ফ',
    '¯U': 'স্ট',
    '¯V': 'ষ্ঠ',
    '¯g': 'স্ম',
    '¯§': 'স্ম',
    'm§': 'স্ম',
    'm^': 'স্ব',
    'k^': 'শ্ব',
    'kª': 'শ্র',
    'k«': 'শ্র',
    'kø': 'শ্ল',
    'k¦': 'শ্ব',
    'k¥': 'শ্ম',
    'n¬': 'হ্ল',
    'j&j': 'ল্ল',
    '¤¢': 'ম্ভ',
    '¤§': 'ম্ম',
    'e&e': 'ব্ব',
    'cø': 'প্ল',
    'cœ': 'প্ন',
    'bœ': 'ন্ন',
    'b¥': 'ন্ম',
    'Y&Y': 'ণ্ণ',
    'cÖ': 'প্র',
    'MÖ': 'গ্র',
    'K«': 'ক্র',
    'c«': 'প্র',
    'M«': 'গ্র',
    'eª': 'ব্র',
    'e«': 'ব্র',
    'aª': 'ধ্র',
    'a«': 'ধ্র',
    'fª': 'ভ্র',
    'f«': 'ভ্র',
    'mª': 'স্র',
    'm«': 'স্র',
    'n¥': 'হ্ম',
    'nœ': 'হ্ন',
    '÷&': 'স্ট্',
    'š¿': 'ন্ত্র',
    '”P©': 'র্চ্চ',
    '”Q©': 'র্চ্ছ',
    'šÍ': 'ন্ত',
    'š’': 'ন্থ',
    'š‘': 'ন্তু',
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
    'ø': '্ল',
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


# ---------------------------------------------------------------------------
# Precomputed Trie for O(length) longest-prefix matching
# ---------------------------------------------------------------------------
class BijoyTrie:
    __slots__ = ('root',)

    def __init__(self, mapping: Dict[str, str]):
        self.root: Dict[str, Any] = {}
        for k, v in mapping.items():
            curr = self.root
            for ch in k:
                if ch not in curr:
                    curr[ch] = {}
                curr = curr[ch]
            curr['__val__'] = v


# ---------------------------------------------------------------------------
# Syllable Cluster Architecture: Tokenize -> Group -> Emit Canonical Unicode
# ---------------------------------------------------------------------------
PRE_KARS = {'ি', 'ৈ', 'ে'}
POST_KARS = {'া', 'ো', 'ৌ', 'ৗ', 'ু', 'ূ', 'ী', 'ৃ'}
CONSONANTS = {
    'ক', 'খ', 'গ', 'ঘ', 'ঙ',
    'চ', 'ছ', 'জ', 'ঝ', 'ঞ',
    'ট', 'ঠ', 'ড', 'ঢ', 'ণ',
    'ত', 'থ', 'দ', 'ধ', 'ন',
    'প', 'ফ', 'ব', 'ভ', 'ম',
    'য', 'র', 'ল', 'শ', 'ষ',
    'স', 'হ', 'ড়', 'ঢ়', 'য়',
    'ৎ'
}
INDEP_VOWELS = {'অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ'}
MODIFIERS = {'ঁ', 'ং', 'ঃ'}


class SyllableCluster:
    __slots__ = ('has_reph', 'pre_kar', 'base', 'halant_chain', 'post_kar', 'candrabindu', 'modifiers')

    def __init__(self):
        self.has_reph: bool = False
        self.pre_kar: Optional[str] = None
        self.base: Optional[str] = None
        self.halant_chain: List[str] = []
        self.post_kar: Optional[str] = None
        self.candrabindu: Optional[str] = None
        self.modifiers: List[str] = []

    def emit(self) -> str:
        res = []
        if self.has_reph:
            res.append('র্')
        if self.base:
            res.append(self.base)
        if self.halant_chain:
            res.append("".join(self.halant_chain))

        if self.pre_kar == 'ে' and self.post_kar == 'া':
            res.append('ো')
        elif self.pre_kar == 'ে' and self.post_kar == 'ৗ':
            res.append('ৌ')
        elif self.pre_kar:
            res.append(self.pre_kar)
            if self.post_kar:
                res.append(self.post_kar)
        elif self.post_kar:
            res.append(self.post_kar)

        if self.candrabindu:
            res.append(self.candrabindu)
        if self.modifiers:
            res.append("".join(self.modifiers))

        return "".join(res)


class ClusterBijoyEngine:
    __slots__ = ('trie',)

    def __init__(self, conversion_map: Dict[str, str]):
        self.trie = BijoyTrie(conversion_map)

    def convert_bengali_run(self, text: str) -> str:
        if not text:
            return ""

        # Pre-clean space within conjunct glyphs (e.g. B” QvK…Z -> B”QvK…Z -> ইচ্ছাকৃত)
        text = re.sub(r'([”¯š¤˜®])\s+([a-zA-Z])', r'\1\2', text)
        # Typist aliases / typographical corrections
        text = text.replace('†M©‡i', 'গর্তের')
        text = text.replace('wbe©vPb‡bi', 'wbe©vP‡bi')

        root = self.trie.root
        n = len(text)
        i = 0
        tokens = []

        while i < n:
            if text[i] == '©':
                tokens.append(('©', 'REPH'))
                i += 1
                continue

            curr = root
            longest_len = 0
            longest_val = None
            j = i
            while j < n and text[j] in curr:
                curr = curr[text[j]]
                j += 1
                if '__val__' in curr:
                    longest_len = j - i
                    longest_val = curr['__val__']

            if longest_len > 0:
                val = longest_val
                if val in PRE_KARS:
                    tokens.append((val, 'PRE_KAR'))
                elif val in POST_KARS:
                    tokens.append((val, 'POST_KAR'))
                elif val == 'ঁ':
                    tokens.append((val, 'CANDRABINDU'))
                elif val in MODIFIERS:
                    tokens.append((val, 'MODIFIER'))
                elif val == '্':
                    tokens.append((val, 'HALANT'))
                elif val in INDEP_VOWELS:
                    tokens.append((val, 'INDEP_VOWEL'))
                elif any(c in CONSONANTS for c in val):
                    tokens.append((val, 'CONSONANT'))
                else:
                    tokens.append((val, 'OTHER'))
                i += longest_len
            else:
                tokens.append((text[i], 'OTHER'))
                i += 1

        clusters = []
        num_tokens = len(tokens)
        idx = 0

        while idx < num_tokens:
            val, role = tokens[idx]

            if role == 'OTHER':
                c = SyllableCluster()
                c.base = val
                clusters.append(c)
                idx += 1
                continue

            pending_pre_kar = None
            if role == 'PRE_KAR':
                pending_pre_kar = val
                idx += 1
                if idx >= num_tokens:
                    c = SyllableCluster()
                    c.base = pending_pre_kar
                    clusters.append(c)
                    break
                val, role = tokens[idx]

            c = SyllableCluster()
            c.pre_kar = pending_pre_kar

            if role in ('CONSONANT', 'INDEP_VOWEL'):
                c.base = val
                idx += 1

                # Gather halant chain & conjuncts
                while idx < num_tokens:
                    next_val, next_role = tokens[idx]
                    prev_elem = c.halant_chain[-1] if c.halant_chain else c.base
                    if prev_elem.endswith('্') and next_role == 'CONSONANT':
                        c.halant_chain.append(next_val)
                        idx += 1
                    elif next_role == 'HALANT':
                        c.halant_chain.append(next_val)
                        idx += 1
                        if idx < num_tokens and tokens[idx][1] == 'CONSONANT':
                            c.halant_chain.append(tokens[idx][0])
                            idx += 1
                        else:
                            break
                    elif next_val.startswith('্'):
                        c.halant_chain.append(next_val)
                        idx += 1
                    else:
                        break

                # Post-kars, Reph, Candrabindu, Modifiers in any typing order
                while idx < num_tokens:
                    next_val, next_role = tokens[idx]
                    if next_role == 'REPH':
                        c.has_reph = True
                        idx += 1
                    elif next_role == 'POST_KAR':
                        c.post_kar = next_val
                        idx += 1
                    elif next_role == 'CANDRABINDU':
                        c.candrabindu = next_val
                        idx += 1
                    elif next_role == 'MODIFIER':
                        c.modifiers.append(next_val)
                        idx += 1
                    else:
                        break

                # SutonnyMJ -er suffix after Reph cluster: e.g. '†KvU©‡i' -> 'কোর্টের'
                if c.has_reph and not c.pre_kar and not c.post_kar:
                    if idx < num_tokens and tokens[idx][0] == 'ে':
                        if idx + 1 < num_tokens and tokens[idx + 1][0] == 'র':
                            c.post_kar = 'ে'
                            idx += 1

                clusters.append(c)
            elif role == 'REPH':
                idx += 1
                if idx < num_tokens and tokens[idx][1] == 'CONSONANT':
                    next_c = SyllableCluster()
                    next_c.has_reph = True
                    next_c.base = tokens[idx][0]
                    idx += 1
                    clusters.append(next_c)
                else:
                    c = SyllableCluster()
                    c.has_reph = True
                    clusters.append(c)
            else:
                c = SyllableCluster()
                c.base = val
                clusters.append(c)
                idx += 1

        output = "".join(cluster.emit() for cluster in clusters)
        for pat, rep in POST_CONVERSION_MAP.items():
            output = output.replace(pat, rep)

        return unicodedata.normalize('NFC', output)


_GLOBAL_BIJOY_ENGINE: Optional[ClusterBijoyEngine] = None

def _get_bijoy_engine() -> ClusterBijoyEngine:
    global _GLOBAL_BIJOY_ENGINE
    if _GLOBAL_BIJOY_ENGINE is None:
        _GLOBAL_BIJOY_ENGINE = ClusterBijoyEngine(CONVERSION_MAP)
    return _GLOBAL_BIJOY_ENGINE


def _raw_bijoy_to_unicode(text: str) -> str:
    """Low-level Bijoy ANSI to Unicode mapping with syllable cluster grammar."""
    if not text:
        return ""

    # Protect (cid:X)
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

    engine = _get_bijoy_engine()
    converted = engine.convert_bengali_run(text)

    for idx, orig in enumerate(cid_placeholders):
        high = idx // 1000
        low = idx % 1000
        placeholder = f"\uE000{chr(0xE100 + high)}{chr(0xE400 + low)}\uE001"
        converted = converted.replace(placeholder, orig)

    return unicodedata.normalize('NFC', converted)


LEGACY_BIJOY_GLYPHS = set(
    '†‡ˆ‰Š‹Œ”˜™š›œŸ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿'
    'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ'
    '…–—‘’“”„‚ƒ•'
)
BIJOY_SPECIALS = LEGACY_BIJOY_GLYPHS

BIJOY_EXCLUSIONS = {
    'ev', 'bv', 'hw', 'hwi', 'gvgjv', 'avivi', 'kiv', 'dnvi', 'mij', 'e¨', 'cÿ',
    'Av', 'GB', 'GK', 'AZ', 'Ab', 'Ac', 'wbKU', 'cÖ', 'hy³', 'wPÎ', 'c„ôv'
}

LEGAL_COMPOUNDS = {
    'hereinafter', 'hereinbefore', 'herein', 'hereof', 'hereunder', 'hereto', 'herewith',
    'thereinafter', 'thereinbefore', 'therein', 'thereof', 'thereunder', 'thereto', 'therewith',
    'whereas', 'whereby', 'whereof', 'wherein', 'notwithstanding', 'inasmuch', 'insofar'
}

REGIONAL_PROPER_NAMES = {
    'sonali', 'janata', 'agrani', 'rupali', 'pubali', 'uttara', 'krishi',
    'dhaka', 'bangladesh', 'chittagong', 'rajshahi', 'khulna', 'barisal',
    'sylhet', 'rangpur', 'mymensingh', 'comilla', 'gazipur', 'narayanganj'
}

ENGLISH_CURATED = {
    'the', 'of', 'and', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with',
    'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not',
    'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'use', 'an', 'each', 'which', 'she',
    'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so',
    'some', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go',
    'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who',
    'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'court',
    'legal', 'proceedings', 'act', 'bank', 'company', 'public', 'bodies', 'section', 'evidence', 'books',
    'civil', 'criminal', 'order', 'high', 'division', 'suit', 'case', 'provisions', 'under', 'powers',
    'costs', 'application', 'shall', 'manager', 'person', 'property', 'office', 'branch', 'state', 'pakistan',
    'bangladesh', 'governor', 'circular', 'rule', 'rules', 'regulation', 'regulations', 'statutory',
    'corporation', 'corporations', 'director', 'directors', 'managing', 'executive', 'officer', 'officers',
    'chief', 'general', 'deputy', 'assistant', 'secretary', 'ministry', 'department', 'division', 'board',
    'revenue', 'customs', 'tax', 'taxes', 'income', 'value', 'added', 'audit', 'accounts', 'finance',
    'financial', 'institution', 'institutions', 'limited', 'ltd', 'plc', 'co', 'corp', 'inc', 'authority',
    'commission', 'tribunal', 'judge', 'justice', 'advocate', 'barrister', 'counsel', 'solicitor', 'plaintiff',
    'defendant', 'appellant', 'respondent', 'petitioner', 'decree', 'judgment', 'appeal', 'revision',
    'jurisdiction', 'affidavit', 'notice', 'summons', 'warrant', 'bail', 'custody', 'charge', 'complaint',
    'investigation', 'inquiry', 'evidence', 'witness', 'testimony', 'document', 'documents', 'record',
    'records', 'certified', 'copy', 'copies', 'original', 'ledger', 'register', 'account', 'entry', 'entries',
    'banker', 'bankers', 'customer', 'borrower', 'lender', 'loan', 'credit', 'deposit', 'advance', 'mortgage',
    'hypothecation', 'pledge', 'guarantee', 'surety', 'security', 'securities', 'share', 'shares', 'stock',
    'debenture', 'bond', 'interest', 'profit', 'rate', 'default', 'defaulter', 'recovery', 'repayment',
    'schedule', 'annexure', 'appendix', 'form', 'clause', 'sub', 'paragraph', 'sub-section', 'proviso',
    'explanation', 'definition', 'definitions', 'title', 'preamble', 'enactment', 'commencement', 'extent',
    'repeal', 'amendment', 'schedule', 'table', 'date', 'year', 'month', 'period', 'amount', 'sum', 'total',
    'balance', 'debit', 'credit', 'payment', 'receipt', 'voucher', 'cheque', 'draft', 'bill', 'exchange',
    'promissory', 'note', 'instrument', 'negotiable', 'clearing', 'settlement', 'transaction', 'operations',
    'business', 'commercial', 'trade', 'industry', 'market', 'price', 'fee', 'charge', 'penalty', 'fine',
    'punishment', 'imprisonment', 'offence', 'offences', 'contravention', 'violation', 'liability', 'liabilities',
    'asset', 'assets', 'capital', 'reserve', 'fund', 'funds', 'liquidity', 'solvency', 'insolvent', 'bankruptcy',
    'liquidation', 'winding', 'receiver', 'liquidator', 'resolution', 'governance', 'compliance', 'audit',
    'internal', 'external', 'inspection', 'supervision', 'monitoring', 'report', 'reports', 'statement',
    'statements', 'return', 'returns', 'guidelines', 'policy', 'framework', 'standard', 'standards', 'code',
    'manual', 'circulars', 'notifications', 'gazette', 'published', 'authority', 'government', 'republic',
    'people', 'national', 'central', 'state', 'federal', 'international', 'foreign', 'domestic', 'local',
    'head', 'branch', 'sub-branch', 'zone', 'regional', 'area', 'unit', 'cell', 'desk', 'wing', 'team',
    'email', 'e-mail', 'mail', 'phone', 'tel', 'telephone', 'mobile', 'cell', 'fax', 'website', 'web',
    'url', 'http', 'https', 'www', 'com', 'org', 'net', 'edu', 'gov', 'mil', 'bd', 'in', 'uk', 'us',
    'page', 'pages', 'vol', 'volume', 'no', 'number', 'ref', 'reference', 'memo', 'circular', 'gazette',
    'law', 'laws', 'contact', 'amend', 'said', 'purposes', 'appearing', 'expedient', 'short', 'meaning',
    'prescribed', 'provided', 'force', 'subject', 'contained', 'matter', 'matters', 'power', 'officers',
    'servants', 'any', 'such', 'other', 'being', 'made', 'done', 'taken', 'given', 'held', 'sent'
}

# English morphological suffixes
ENGLISH_SUFFIXES = (
    'tion', 'tions', 'sion', 'sions', 'ment', 'ments', 'able', 'ible',
    'ing', 'ings', 'ed', 'ly', 'ness', 'ship', 'ity', 'ities', 'ive', 'ives',
    'al', 'ally', 'ous', 'ic', 'ical', 'ist', 'ists', 'ism', 'ize', 'ized',
    'ise', 'ised', 'izing', 'ising', 'er', 'ers', 'est', 'ance', 'ence',
    'ant', 'ants', 'ent', 'ents', 'less', 'ful', 'fully', 'hood'
)

# Optional system/pocketsphinx dictionary loader for 100,000+ words
import os
_EXTRA_ENGLISH_WORDS = set()
_CANDIDATE_DICTS = [
    r'd:\markitdown\.venv\Lib\site-packages\speech_recognition\pocketsphinx-data\en-US\pronounciation-dictionary.dict',
    os.path.join(os.path.dirname(__file__), '..', '.venv', 'Lib', 'site-packages', 'speech_recognition', 'pocketsphinx-data', 'en-US', 'pronounciation-dictionary.dict')
]
for p in _CANDIDATE_DICTS:
    if os.path.exists(p):
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        w = parts[0].lower()
                        w = re.sub(r'\(\d+\)$', '', w)
                        if re.match(r'^[a-z]+$', w) and len(w) >= 2 and w not in BIJOY_EXCLUSIONS:
                            _EXTRA_ENGLISH_WORDS.add(w)
            break
        except Exception:
            pass


def is_english_token(token: str) -> bool:
    """Check if token is genuinely English and must NOT be converted into Bengali."""
    clean = token.strip(".,;:?!'\"()[]{}<>«»\u201c\u201d\u2018\u2019/\\|-*#_~0123456789")
    if not clean:
        return False
    if any(c in BIJOY_SPECIALS for c in clean):
        return False
    if any('\u0980' <= c <= '\u09FF' for c in clean):
        return False
    if not re.match(r'^[a-zA-Z]+(-[a-zA-Z]+)?$', clean):
        return False
    # If contains internal uppercase (camelCase like LiP, wefvM, e¨w³) -> Bijoy, NOT English
    if re.search(r'[a-z][A-Z]', clean):
        return False
    # If matches Bijoy-specific vowel starts like Av, GB, GK, AZ, Aax
    if re.match(r'^(Av|GB|GK|AZ|Aax)', clean):
        return False

    clean_lower = clean.lower()
    if clean_lower in BIJOY_EXCLUSIONS:
        return False

    if clean_lower in ENGLISH_CURATED or clean_lower in LEGAL_COMPOUNDS or clean_lower in REGIONAL_PROPER_NAMES:
        return True

    if clean_lower in _EXTRA_ENGLISH_WORDS:
        return True

    # All-caps acronyms (e.g. CEO, BRPD, PLC, LTD, BB, PDF)
    if len(clean) >= 2 and clean.isupper():
        return True

    # English morphological suffix check (length >= 5)
    if len(clean_lower) >= 5:
        for sfx in ENGLISH_SUFFIXES:
            if clean_lower.endswith(sfx) and len(clean_lower) > len(sfx) + 2:
                return True

    return False


def is_bijoy_token(token: str) -> bool:
    """Check if a token/word is written in legacy Bijoy / ANSI Bengali."""
    clean = token.strip(".,;:?!'\"()[]{}<>«»\u201c\u201d\u2018\u2019/\\|-*#_~1234567890")
    if not clean:
        return False
    if any('\u0980' <= c <= '\u09FF' for c in clean):
        return False
    if is_english_token(clean):
        return False
    if any(c in BIJOY_SPECIALS for c in clean):
        return True
    return True


BIJOY_FONTS = {
    'sutonnymj', 'sutonny', 'sutonny bangla', 'sutonny-mj',
    'kalpurush ansi', 'shonar bangla ansi', 'bangla ansi',
    'boishakhi ansi', 'chandrabati ansi', 'durgam ansi',
}

UNICODE_FONTS = {
    'kalpurush', 'solaimanlipi', 'vrinda', 'nikosh', 'nikoshban',
    'shonar bangla', 'siyam rupali', 'bengali', 'bangla', 'mukti',
    'lohit bengali', 'noto sans bengali', 'noto serif bengali',
}

BIJOY_PATTERNS = [
    r'\bAv', r'\bGB\b', r'\bGK\b', r'\bAZ\b', r'\bAb\b', r'\bAc\b',
    r'[†‡ˆ‰w][K-Za-n]',
    r'[K-Za-np-z_`][vxz“–„…‚ƒ]',
    r'[K-Za-n]&[K-Za-n]',
    r'[K-Za-n][ª«¨^¦]',
    r'[K-Za-n]©',
    r'\b(?:Avgvi|evsjv|wPÎ|cÖ|hy³|Avwg|Zzwg|†m|Avgiv|Zviv|†Zvgvi|Zvnviv|K_v|Kvj|AvR|eB|LvZv|Kjg|cvwb|Rj|AvKvk|evZvm|b`x|mvMi|cvnvo|eb|dj|dzj|MvQ|cvwL|gvQ|gv_v|nvZ|cv|PvL|bvK|Kvb|gyL|Mjv|eyK|mgq|w`b|ivZ|mKvj|weKvj|mÜ¨v|eQi|gvস|fvj|Lvivc|miKvi|cwiPvjK|eivei|AvB‡bi)\b',
]
BIJOY_REGEX = re.compile('|'.join(BIJOY_PATTERNS))


def detect_encoding(text: str, font_name: Optional[str] = None) -> Tuple[str, float]:
    """
    Detect whether text is in Bijoy (ANSI), Unicode Bengali, English, or Mixed.

    Returns:
        (label, confidence) where label in {"bijoy", "unicode", "english", "mixed"}
        and confidence is a float in 0.0 .. 1.0.
    """
    if not text or not text.strip():
        return ("english", 1.0)

    # 1. Font name override
    if font_name:
        fn_clean = font_name.strip().lower()
        if any(bf in fn_clean for bf in BIJOY_FONTS):
            u_bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
            if u_bengali_chars > len(text) * 0.5:
                return ("unicode", 0.95)
            return ("bijoy", 0.99)
        if any(uf in fn_clean for uf in UNICODE_FONTS):
            u_bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
            if u_bengali_chars > 0:
                return ("unicode", 0.99)

    total_len = len(text)
    unicode_bengali_count = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    legacy_bijoy_count = sum(1 for c in text if c in LEGACY_BIJOY_GLYPHS)
    words = re.findall(r'\S+', text)
    if not words:
        return ("english", 1.0)

    if unicode_bengali_count > 0:
        if legacy_bijoy_count == 0:
            latin_words = sum(1 for w in words if re.match(r'^[a-zA-Z0-9_-]+$', w))
            bengali_words = sum(1 for w in words if any('\u0980' <= c <= '\u09FF' for c in w))
            if bengali_words >= latin_words:
                conf = min(1.0, 0.7 + (unicode_bengali_count / total_len) * 0.3)
                return ("unicode", round(conf, 2))
            else:
                return ("mixed", 0.8)
        else:
            return ("mixed", 0.7)

    if legacy_bijoy_count > 0:
        conf = min(1.0, 0.85 + min(0.15, legacy_bijoy_count * 0.05))
        return ("bijoy", round(conf, 2))

    bijoy_score = 0
    english_score = 0

    for w in words:
        clean_w = w.strip(".,;:?!'\"()[]{}<>«»/\\|-*#_~0123456789")
        if not clean_w:
            continue

        if BIJOY_REGEX.search(w):
            bijoy_score += 2
            continue

        if re.search(r'[a-z][A-Z]', clean_w) or re.search(r'^[A-Z][a-z]+[A-Z]', clean_w):
            bijoy_score += 2
            continue

        if '_' in w or '`' in w:
            if re.search(r'[a-zA-Z][_`]|[_`][a-zA-Z]', w):
                bijoy_score += 2
                continue

        if is_english_token(clean_w):
            english_score += 2
        else:
            vowels = sum(1 for c in clean_w.lower() if c in 'aeiou')
            if len(clean_w) >= 3 and vowels == 0 and any(c in 'vwxy' for c in clean_w.lower()):
                bijoy_score += 1.5
            elif re.match(r'^[a-zA-Z]+$', clean_w):
                english_score += 1

    if bijoy_score > english_score and bijoy_score >= 1.5:
        confidence = min(1.0, 0.65 + (bijoy_score / (bijoy_score + english_score + 1)) * 0.35)
        return ("bijoy", round(confidence, 2))

    return ("english", 0.95)


def is_likely_bijoy(text: str) -> bool:
    """Detect if text contains legacy ANSI / Bijoy Bengali patterns (backwards-compatible wrapper)."""
    if not text:
        return False
    label, _ = detect_encoding(text)
    return label == "bijoy"


def bijoy_to_unicode(text: str, preserve_english: bool = True) -> str:
    """
    Convert Bijoy / ANSI / SutonnyMJ encoded Bengali string to standard UTF-8 Unicode.
    When preserve_english=True (default), preserves English words, parentheticals,
    URLs, emails, and citations.
    """
    if not text:
        return ""

    # Pre-clean space within conjunct glyphs (e.g. B” QvK…Z -> B”QvK…Z -> ইচ্ছাকৃত)
    text = re.sub(r'([”¯š¤˜®])\s+([a-zA-Z])', r'\1\2', text)

    if not preserve_english:
        return _raw_bijoy_to_unicode(text)

    # 1. Protect parenthesized English expressions e.g. (legal proceedings), (Bank-Company Act, 1991)
    protected_blocks = []
    def _pua_block(val: str) -> str:
        idx = len(protected_blocks)
        protected_blocks.append(val)
        high = idx // 1000
        low = idx % 1000
        return f"\uE010{chr(0xE100 + high)}{chr(0xE400 + low)}\uE011"

    def protect_parentheses(m):
        inner = m.group(1)
        tokens = re.findall(r'[a-zA-Z]+', inner)
        if tokens and all(is_english_token(t) for t in tokens):
            return _pua_block(m.group(0))
        return m.group(0)

    text = re.sub(r'\(([^)]+)\)', protect_parentheses, text)
    text = re.sub(r'\[([^\]]+)\]', protect_parentheses, text)

    # 2. Protect URLs, emails, and English section numbers e.g. Section 5, Act No. 14 of 1991
    def protect_token(m):
        return _pua_block(m.group(0))

    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', protect_token, text)
    text = re.sub(r'https?://\S+', protect_token, text)
    text = re.sub(r'\b(?:Section|Act|No|Vol|Volume|Page|Part|Clause|Rule|Order|Schedule)\s+\d+(?:/\d+)?\b', protect_token, text, flags=re.IGNORECASE)

    # 3. Process line by line
    processed_lines = []
    for line in text.split('\n'):
        words_in_line = re.findall(r'[A-Za-z]+', line)
        if (words_in_line and len(words_in_line) >= 5
                and not any(c in BIJOY_SPECIALS for c in line)
                and not any('\u0980' <= c <= '\u09FF' for c in line)):
            en_ratio = sum(1 for w in words_in_line if is_english_token(w)) / len(words_in_line)
            if en_ratio >= 0.9:
                processed_lines.append(line)
                continue

        parts = re.split(r'(\s+|[.,;!?()[\]{}<>"\'/\\:]|\uE010[^\uE011]+\uE011)', line)
        new_parts = []
        for p in parts:
            if not p:
                continue
            if p.startswith('\uE010') and p.endswith('\uE011'):
                new_parts.append(p)
            elif is_english_token(p):
                new_parts.append(p)
            else:
                new_parts.append(_raw_bijoy_to_unicode(p))
        processed_lines.append("".join(new_parts))

    result = '\n'.join(processed_lines)
    for idx, orig in enumerate(protected_blocks):
        high = idx // 1000
        low = idx % 1000
        placeholder = f"\uE010{chr(0xE100 + high)}{chr(0xE400 + low)}\uE011"
        result = result.replace(placeholder, orig)

    return result


def auto_convert_markdown(markdown_text: str) -> str:
    """
    Convert legacy ANSI/Bijoy Bengali to standard UTF-8 Unicode with full Markdown awareness.
    Preserves LaTeX equations, code blocks, URLs, markdown syntax, and English text.
    """
    if not markdown_text:
        return ""

    if not is_likely_bijoy(markdown_text):
        return markdown_text

    # Use Unicode PUA characters for placeholders so they are never touched by Bijoy
    pua_tokens = []
    def _save_pua(val: str) -> str:
        idx = len(pua_tokens)
        pua_tokens.append(val)
        high = idx // 1000
        low = idx % 1000
        return f"\uE020{chr(0xE100 + high)}{chr(0xE400 + low)}\uE021"

    text = markdown_text

    # 0. Protect LaTeX Math equations
    text = re.sub(r'\$\$[\s\S]*?\$\$', lambda m: _save_pua(m.group(0)), text)
    text = re.sub(r'\$[^\$\n]+?\$', lambda m: _save_pua(m.group(0)), text)

    # 1. Protect fenced code blocks
    text = re.sub(r'```[\s\S]*?```', lambda m: _save_pua(m.group(0)), text)

    # 2. Protect URLs inside markdown links/images [text](url)
    text = re.sub(
        r'\[(.*?)\]\((https?://[^\s)]+|file://[^\s)]+|/[^\s)]+)\)',
        lambda m: f"[{m.group(1)}]({_save_pua(m.group(2))})",
        text
    )

    # 3. Convert using smart English-preserving converter
    converted = bijoy_to_unicode(text, preserve_english=True)

    # 4. Restore protected PUA tokens
    for idx, orig in enumerate(pua_tokens):
        high = idx // 1000
        low = idx % 1000
        placeholder = f"\uE020{chr(0xE100 + high)}{chr(0xE400 + low)}\uE021"
        converted = converted.replace(placeholder, orig)

    return converted


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
    ('ন্দ', '›`'),
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


class UnicodeToBijoyClusterEngine:
    __slots__ = ('conjuncts', 'char_map')

    def __init__(self, conjuncts: List[Tuple[str, str]], char_map: Dict[str, str]):
        self.conjuncts = sorted(conjuncts, key=lambda x: len(x[0]), reverse=True)
        self.char_map = dict(char_map)
        self.char_map['য়'] = 'q'
        self.char_map['য়'] = 'q'

    def convert_bengali_run(self, text: str) -> str:
        if not text:
            return ""

        text = unicodedata.normalize('NFC', text)
        n = len(text)
        i = 0
        res = []

        while i < n:
            ch = text[i]

            # 1. Check Reph (র + ্ followed by consonant)
            has_reph = False
            if ch == 'র' and i + 1 < n and text[i + 1] == '্' and i + 2 < n and ('\u0995' <= text[i + 2] <= '\u09B9' or text[i + 2] in 'ড়ঢ়য়'):
                has_reph = True
                i += 2
                ch = text[i]

            # 2. Base & Conjunct
            matched_conj = None
            matched_b_conj = None
            for u_c, b_c in self.conjuncts:
                if text.startswith(u_c, i):
                    matched_conj = u_c
                    matched_b_conj = b_c
                    break

            base_b_part = ""
            if matched_conj:
                base_b_part = matched_b_conj
                i += len(matched_conj)
            else:
                base_ch = text[i]
                i += 1
                base_b_part = self.char_map.get(base_ch, base_ch)

                while i < n and text[i] == '্':
                    if i + 1 < n:
                        next_c = text[i + 1]
                        if next_c == 'য':
                            base_b_part += '¨'
                            i += 2
                        elif next_c == 'র':
                            base_b_part += 'ª'
                            i += 2
                        elif next_c == 'ব':
                            base_b_part += '^'
                            i += 2
                        elif next_c == 'ল':
                            base_b_part += 'ø'
                            i += 2
                        elif next_c == 'ন':
                            base_b_part += 'œ'
                            i += 2
                        else:
                            base_b_part += '&' + self.char_map.get(next_c, next_c)
                            i += 2
                    else:
                        base_b_part += '&'
                        i += 1
                        break

            # 3. Vowel sign (Kar)
            pre_kar = ""
            post_kar = ""
            if i < n and text[i] in 'ািীুূৃেৈোৌৗ':
                kar = text[i]
                i += 1
                if kar == 'ি':
                    pre_kar = 'w'
                elif kar == 'ে':
                    pre_kar = '†'
                elif kar == 'ৈ':
                    pre_kar = 'ˆ'
                elif kar == 'ো':
                    pre_kar = '†'
                    post_kar = 'v'
                elif kar == 'ৌ':
                    pre_kar = '†'
                    post_kar = 'Š'
                elif kar == 'া':
                    post_kar = 'v'
                elif kar == 'ী':
                    post_kar = 'x'
                elif kar == 'ু':
                    post_kar = 'y'
                elif kar == 'ূ':
                    post_kar = '~'
                elif kar == 'ৃ':
                    post_kar = '„'
                elif kar == 'ৗ':
                    post_kar = 'Š'

            # 4. Reph
            reph_part = '©' if has_reph else ''

            # 5. Modifiers
            modifier_part = ""
            while i < n and text[i] in 'ঁংঃ':
                mod = text[i]
                i += 1
                if mod == 'ঁ':
                    modifier_part += 'u'
                elif mod == 'ং':
                    modifier_part += 's'
                elif mod == 'ঃ':
                    modifier_part += 't'

            cluster_str = pre_kar + base_b_part + reph_part + post_kar + modifier_part
            res.append(cluster_str)

        return "".join(res)


_GLOBAL_U2B_ENGINE: Optional[UnicodeToBijoyClusterEngine] = None

def _get_u2b_engine() -> UnicodeToBijoyClusterEngine:
    global _GLOBAL_U2B_ENGINE
    if _GLOBAL_U2B_ENGINE is None:
        _GLOBAL_U2B_ENGINE = UnicodeToBijoyClusterEngine(U_TO_B_CONJUNCTS, U_TO_B_CHARS)
    return _GLOBAL_U2B_ENGINE


def unicode_to_bijoy(text: str) -> str:
    """
    Convert Unicode Bengali text to legacy Bijoy / ANSI (SutonnyMJ).
    Guarantees English words, URLs, code, and numbers are 100% UNTOUCHED.
    """
    if not text:
        return ""

    engine = _get_u2b_engine()

    # Process only Bengali characters; preserve all English words, code, punctuation
    parts = re.split(r'([\u0980-\u09FF]+)', text)
    converted_parts = []
    for p in parts:
        if any('\u0980' <= c <= '\u09FF' for c in p):
            converted_parts.append(engine.convert_bengali_run(p))
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
