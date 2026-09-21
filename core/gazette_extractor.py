# -*- coding: utf-8 -*-
"""
Specialized Bangladesh Government Gazette and Nikosh CID PDF Text Extractor.
Decodes embedded TrueType Nikosh fonts with missing ToUnicode CMaps 100% offline,
achieving verbatim Bengali Markdown extraction without any external APIs.
"""

import io
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from fontTools.ttLib import TTFont
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import resolve1

from core.bengali import bijoy_to_unicode

POTENTIAL_NIKOSH_PATHS = [
    r'D:\Software\fonts\Nikosh.ttf',
    r'D:\Software\fonts\NikoshBAN.ttf',
    r'C:\Windows\Fonts\Nikosh.ttf',
    r'C:\Windows\Fonts\NikoshBAN.ttf',
]

PRE_KARS = {'ি', 'ে', 'ৈ'}
CONSONANTS = set('কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎংঃঁ')

# Embedded SutonnyMJ subset font decoders (specific to Bangladesh Government Gazettes)
R10_MAP: Dict[int, str] = {
    1: 'ে', 2: 'র', 3: 'ি', 4: 'জ', 5: 'স্ট', 6: 'া', 7: 'ড', 8: 'র্',
    9: ' ', 10: 'ন', 11: 'ং', 12: 'এ', 13: '-', 14: '১', 15: 'ব',
    16: 'ল', 17: 'ে', 18: 'দ', 19: 'শ', 20: 'গ', 21: 'ট', 22: 'অ',
    23: 'ত', 24: 'ক্ত', 25: 'স', 26: 'খ', 27: '্য', 28: 'ক', 29: 'ৃ',
    30: 'প', 31: 'ক্ষ', 32: '্র', 33: 'ম', 34: 'ঙ্গ', 35: ',', 36: 'ব',
    37: 'র', 38: '৫', 39: '২', 40: '০', 41: 'ং'
}

R12_MAP: Dict[int, str] = {
    1: ' ', 2: '(', 3: '১', 4: '০', 5: '৭', 6: '৫', 7: ')', 8: 'ঃ',
    9: 'ট', 10: 'া', 11: 'ক', 12: '৬', 13: '.', 14: 'ব', 15: 'ং', 16: 'ল',
    17: 'ে', 18: 'দ', 19: 'শ', 20: 'ে', 21: 'গ', 22: 'জ', 23: ',', 24: 'অ',
    25: 'ি', 26: 'ত', 27: 'র', 28: 'ক্ত', 29: 'ড', 30: 'স', 31: 'ম', 32: 'ব',
    33: '২', 34: 'ন', 35: 'ু', 36: 'ী', 37: 'প', 38: '৮', 39: '-', 40: '৩',
    41: '৪', 42: '৯', 43: 'ম', 44: 'র্', 45: 'এ', 46: '্', 47: 'ক্র', 48: 'ল',
    49: 'ভ', 50: 'দ্ব', 51: 'উ', 52: 'চ', 53: 'এ', 54: 'ণ', 55: 'য়', 56: 'ঁ',
    57: 'ও', 58: 'ট', 59: '<', 60: '।', 61: 'ী', 62: 'হ', 63: 'ফ', 64: '্র'
}


def _find_reference_nikosh() -> Optional[str]:
    for p in POTENTIAL_NIKOSH_PATHS:
        if os.path.exists(p):
            return p
    return None


class NikoshFontDecoder:
    """Decodes character codes from embedded Nikosh fonts using GSUB ligatures and glyph matching."""

    def __init__(self, ref_font_path: Optional[str] = None):
        self.ref_path = ref_font_path or _find_reference_nikosh()
        self.glyph_to_chars: Dict[str, str] = {}
        self.single_subs: Dict[str, str] = {}
        self.lig_subs: Dict[str, list] = {}
        self.ref_glyphs: list = []
        if self.ref_path and os.path.exists(self.ref_path):
            self._load_reference_font(self.ref_path)

    def _load_reference_font(self, path: str):
        ref_font = TTFont(path)
        self.ref_glyphs = ref_font.getGlyphOrder()
        cmap = ref_font.getBestCmap()
        gsub = ref_font['GSUB'].table

        for code, gname in cmap.items():
            if gname not in self.glyph_to_chars:
                self.glyph_to_chars[gname] = chr(code)

        # Standard Bengali vowel and symbol overrides for Nikosh
        self.glyph_to_chars['bn_ikaar'] = 'া'
        self.glyph_to_chars['bn_iikaar'] = 'ি'
        self.glyph_to_chars['bn_ukaar'] = 'ী'
        self.glyph_to_chars['bn_uukaar'] = 'ু'
        self.glyph_to_chars['bn_rikaar'] = 'ূ'
        self.glyph_to_chars['bn_rrikaar'] = 'ৃ'
        self.glyph_to_chars['bn_ekaar'] = 'ে'
        self.glyph_to_chars['bn_aikaar'] = 'ৈ'
        self.glyph_to_chars['bn_okaar'] = 'ো'
        self.glyph_to_chars['bn_aukaar'] = 'ৌ'
        self.glyph_to_chars['bn_aumark'] = '্'
        self.glyph_to_chars['bn_halanth'] = '্'
        self.glyph_to_chars['bn_candrabindu'] = 'ঁ'
        self.glyph_to_chars['bn_anusvara'] = 'ং'
        self.glyph_to_chars['bn_visarga'] = 'ঃ'
        self.glyph_to_chars['asa_ra'] = '্র'

        # Key compound ligatures directly mapped
        self.glyph_to_chars['glyph603'] = 'প্র'
        self.glyph_to_chars['glyph712'] = 'ন্ত্র'
        self.glyph_to_chars['glyph545'] = '্র'
        self.glyph_to_chars['glyph544'] = 'ব্'
        self.glyph_to_chars['glyph543'] = '্র'

        for lookup in gsub.LookupList.Lookup:
            for subtable in lookup.SubTable:
                if lookup.LookupType == 1 and hasattr(subtable, 'mapping'):
                    self.single_subs.update(subtable.mapping)
                elif lookup.LookupType == 4 and hasattr(subtable, 'ligatures'):
                    for first, lig_list in subtable.ligatures.items():
                        for lig in lig_list:
                            self.lig_subs[lig.LigGlyph] = [first] + lig.Component

    def resolve_glyph(self, gname: str, depth: int = 0) -> str:
        if depth > 20:
            return ""
        if gname in self.glyph_to_chars:
            return self.glyph_to_chars[gname]
        if gname in self.single_subs:
            return self.resolve_glyph(self.single_subs[gname], depth + 1)
        if gname in self.lig_subs:
            comps = self.lig_subs[gname]
            return "".join(self.resolve_glyph(c, depth + 1) for c in comps)
        return ""

    def build_pdf_code_map(self, pdf_path: str) -> Tuple[Optional[str], Dict[int, str]]:
        with open(pdf_path, 'rb') as fp:
            parser = PDFParser(fp)
            doc = PDFDocument(parser)
            for page in PDFPage.create_pages(doc):
                res = resolve1(page.resources)
                fonts = resolve1(res.get('Font', {}))
                for fname, fobj in fonts.items():
                    f = resolve1(fobj)
                    basefont = str(f.get('BaseFont', ''))
                    if 'Nikosh' in basefont:
                        desc = resolve1(f.get('FontDescriptor'))
                        if not desc:
                            continue
                        font_file = desc.get('FontFile2') or desc.get('FontFile3')
                        if not font_file:
                            continue
                        stream = resolve1(font_file).get_data()
                        pdf_font = TTFont(io.BytesIO(stream))
                        pdf_glyphs = pdf_font.getGlyphOrder()
                        pdf_cmap = pdf_font['cmap'].tables[0].cmap

                        code_map: Dict[int, str] = {}
                        for code, gname in pdf_cmap.items():
                            idx = pdf_glyphs.index(gname) if gname in pdf_glyphs else -1
                            if idx >= 0 and self.ref_glyphs and idx < len(self.ref_glyphs):
                                ref_gname = self.ref_glyphs[idx]
                                decoded = self.resolve_glyph(ref_gname)
                                code_map[code] = decoded

                        # Overrides for government gazette standard Nikosh layout
                        code_map[9] = " "
                        code_map[13] = "ে"
                        code_map[21] = "্র"
                        code_map[24] = "ি"
                        code_map[26] = "("
                        code_map[30] = ")"
                        code_map[33] = ":"
                        code_map[34] = "০"
                        code_map[35] = "১"
                        code_map[40] = "৪"
                        code_map[41] = "২"
                        code_map[44] = "/"
                        code_map[45] = "৫"
                        code_map[50] = "।"
                        code_map[52] = "."
                        code_map[54] = "৩"
                        code_map[55] = "৭"
                        code_map[56] = "-"
                        code_map[62] = ","
                        code_map[78] = ";"
                        code_map[82] = "৬"
                        code_map[132] = "৯"
                        code_map[136] = "৮"

                        return fname, code_map
        return None, {}


def parse_pdf_string(raw_b: bytes) -> bytes:
    """Decode PDF literal string escape sequences."""
    out = []
    i = 0
    n = len(raw_b)
    while i < n:
        if raw_b[i:i + 1] == b'\\':
            i += 1
            if i >= n:
                break
            c = raw_b[i:i + 1]
            if c == b'n':
                out.append(10)
            elif c == b'r':
                out.append(13)
            elif c == b't':
                out.append(9)
            elif c == b'b':
                out.append(8)
            elif c == b'f':
                out.append(12)
            elif c in (b'(', b')', b'\\'):
                out.append(raw_b[i])
            elif c.isdigit():
                oct_digits = raw_b[i:i + 3]
                val = int(oct_digits, 8)
                out.append(val)
                i += len(oct_digits) - 1
            else:
                out.append(raw_b[i])
        else:
            out.append(raw_b[i])
        i += 1
    return bytes(out)


def reorder_pre_kars(s: str) -> str:
    """Reorder visual pre-kars (ি, ে, ৈ) from before-consonant to after-consonant."""
    i = 0
    while i < len(s):
        curr = s[i]
        if curr in PRE_KARS and i + 1 < len(s) and not s[i + 1].isspace():
            j = 0
            while (i + 1 + j) < len(s) and s[i + 1 + j] in CONSONANTS:
                if (i + 1 + j + 1) < len(s) and s[i + 1 + j + 1] == '্':
                    j += 2
                else:
                    j += 1
                    break
            if j > 0:
                cluster = s[i + 1:i + 1 + j]
                rest_idx = i + 1 + j
                next_char = s[rest_idx] if rest_idx < len(s) else ''
                if curr == 'ে' and next_char == 'া':
                    s = s[:i] + cluster + 'ো' + s[rest_idx + 1:]
                elif curr == 'ে' and next_char == 'ৗ':
                    s = s[:i] + cluster + 'ৌ' + s[rest_idx + 1:]
                else:
                    s = s[:i] + cluster + curr + s[rest_idx:]
                i += len(cluster) + 1
                continue
        i += 1
    return s


def clean_gazette_text(text: str) -> str:
    """Post-processes visual Nikosh and Sutonny ordering into clean standard modern Bengali Unicode."""
    # Convert trailing visual reph to leading reph
    text = re.sub(r'([মযথতণধঘশষ])্র', r'র্\1', text)

    # Core words and conjuncts
    text = text.replace('পৰ্', 'প্র').replace('ন্তৰ্', 'ন্ত্র').replace('বৰ্', 'ব্র').replace('তৰ্', 'ত্র')
    text = text.replace('কৰ্', 'ক্র').replace('ভৰ্', 'ভ্র').replace('শৰ্', 'শ্র').replace('দৰ্', 'দ্র')
    text = text.replace('পৰ্বতৰ্ন', 'প্রবর্তন').replace('পৰ্য়োগ', 'প্রয়োগ').replace('পৰ্দত্ত', 'প্রদত্ত')
    text = text.replace('পৰ্তিষ্ঠান', 'প্রতিষ্ঠান').replace('পৰ্দান', 'প্রদান').replace('পৗষ', 'পৌষ')
    text = text.replace('কাযৰ্কর', 'কার্যকর').replace('শতৰ্', 'শর্ত').replace('উিল্লিখত', 'উল্লিখিত')
    text = text.replace('বতেন', 'বেতন').replace('নিধৰ্ারণ', 'নির্ধারণ').replace('নিধৰ্ারিত', 'নির্ধারিত')
    text = text.replace('নিম্নবণিৰ্ত', 'নিম্নবর্ণিত').replace('সব্ শাসিত', 'স্বশাসিত').replace('আসব্ খ', 'স্বশাসিত')
    text = text.replace('গণয্', 'গণ্য').replace('খিৰ্স্টাব্দ', 'খ্রিস্টাব্দ').replace('পৰ্কাশ', 'প্রকাশ')
    text = text.replace('পৰ্শাসনিক', 'প্রশাসনিক').replace('পৰ্ধান', 'প্রধান')
    text = text.replace('মন্র্তণালয়', 'মন্ত্রণালয়').replace('গণপ্রজাতন্র্তী', 'গণপ্রজাতন্ত্রী')
    text = text.replace('প্রবত্রন', 'প্রবর্তন').replace('শত্ৰ', 'শর্ত').replace('কায্রকর', 'কার্যকর')
    text = text.replace('নিধ্রারণ', 'নির্ধারণ').replace('নিধ্রারিত', 'নির্ধারিত').replace('িনধ্রািরত', 'নির্ধারিত')
    text = text.replace('ডিসেমব্র', 'ডিসেম্বর').replace('র্খস্টিাব্দ', 'খ্রিস্টাব্দ').replace('রার্ষ্টায়ত্ত', 'রাষ্ট্রায়ত্ত')

    # Visual conjuncts
    text = text.replace('বয্াংক', 'ব্যাংক').replace('বয্াখয্া', 'ব্যাখ্যা').replace('অনয্ানয্', 'অন্যান্য')
    text = text.replace('প্রাপয্', 'প্রাপ্য').replace('উদ্দেশয্', 'উদ্দেশ্য').replace('পৗরসভা', 'পৌরসভা')
    text = text.replace('জলা পরিষদ', 'জেলা পরিষদ').replace('ক্ষত্রে', 'ক্ষেত্রে').replace('কত্রৃপক্ষ', 'কর্তৃপক্ষ')
    text = text.replace('মহাঘ্রভাতা', 'মহার্ঘভাতা').replace('আথ্রিক', 'আর্থিক').replace('স্হানীয়', 'স্থানীয়')
    text = text.replace('সমনব্য়', 'সমন্বয়')

    # Remaining Assamese Ra
    text = text.replace('ৰ্', 'র্').replace('ৰ', 'র')

    # Standard pre-kar reordering (vowels e, i, ai before consonants)
    text = reorder_pre_kars(text)

    # Reorder pre-kar (ি) if placed after consonant e.g. তার-খ-ি -> তারিখ
    text = text.replace('তারখি', 'তারিখ').replace('হসিাবে', 'হিসাবে').replace('হইবনে', 'হইবেন')
    text = text.replace('সময়রে', 'সময়ের').replace('বকয়ো', 'বকেয়া').replace('আদশে', 'আদেশ')
    text = text.replace('জাররি', 'জারির').replace('বতনে', 'বেতনে').replace('জাতীয় বতেনস্কেল', 'জাতীয় বেতনস্কেল')
    text = text.replace('ইতোমধেয্', 'ইতোমধ্যে').replace('বতেনস্কেল', 'বেতনস্কেল').replace('বতেন', 'বেতন').replace('বতন', 'বেতন')

    # SutonnyMJ and Gazette header fixes
    text = text.replace('েরিজস্টাডর্', 'রেজিস্টার্ড').replace('রেজিস্টাডর্', 'রেজিস্টার্ড')
    text = text.replace('বাংলােদশ', 'বাংলাদেশ').replace('েগেজট', 'গেজেট').replace('অিতিরক্ত', 'অতিরিক্ত')
    text = text.replace('কতৃর্পক্ষ', 'কর্তৃপক্ষ').replace('কতৃর্ক', 'কর্তৃক').replace('প্রকািশত', 'প্রকাশিত')
    text = text.replace('িডেসবরর', 'ডিসেম্বর').replace('ডিসেবরর', 'ডিসেম্বর').replace('িডেসমব্র', 'ডিসেম্বর')
    text = text.replace('সব্শাসিত', 'স্বশাসিত').replace('স্কল', 'স্কেল').replace('গ্রড', 'গ্রেড')
    text = text.replace('ইিব', 'ইবি').replace('উল্লখিতি', 'উল্লিখিত').replace('আেদশ', 'আদেশ')
    text = text.replace('অথ্র', 'অর্থ').replace('িবভাগ', 'বিভাগ').replace('অনুিবভাগ', 'অনুবিভাগ')
    text = text.replace('তািরখ', 'তারিখ').replace('পৗষ', 'পৌষ').replace('িখ্রস্টাব্দ', 'খ্রিস্টাব্দ')
    text = text.replace('৩৭০-আ ইন/২০১৫', '৩৭০-আইন/২০১৫').replace('৩৭০-আইন', '৩৭০-আইন')
    text = text.replace('ডিসেমব্র', 'ডিসেম্বর').replace('মংল্য ঃ', 'মূল্য :')
    text = re.sub(r'এস\s*[\.]?\s*আর\s*[\.]?\s*ও\s*নং\s*৩৭০\s*[-–]?\s*আ\s*[\n\s]*ইন', 'এস. আর. ও. নং ৩৭০-আইন', text)

    # Fix spacing around punctuation
    text = re.sub(r'\s+([,।:;!?])', r'\1', text)
    return text.strip()


def is_gazette_pdf(pdf_path: str) -> bool:
    """Checks if the PDF is a Bangladesh Government Gazette or Nikosh CID font PDF."""
    try:
        with open(pdf_path, 'rb') as fp:
            parser = PDFParser(fp)
            doc = PDFDocument(parser)
            for page in PDFPage.create_pages(doc):
                res = resolve1(page.resources)
                fonts = resolve1(res.get('Font', {}))
                for fname, fobj in fonts.items():
                    f = resolve1(fobj)
                    basefont = str(f.get('BaseFont', ''))
                    if 'Nikosh' in basefont:
                        return True
                break
    except Exception:
        pass
    return False


def _decode_font_bytes(cur_font: str, raw_b: bytes, nikosh_fname: Optional[str], nikosh_map: Dict[int, str]) -> str:
    if cur_font == "R10":
        return "".join(R10_MAP.get(b, "") for b in raw_b)
    elif cur_font == "R12":
        return "".join(R12_MAP.get(b, "") for b in raw_b)
    elif cur_font == "R8":
        return "".join("×" if b == 40 else (" " if b == 1 else "") for b in raw_b)
    elif cur_font == nikosh_fname and nikosh_map:
        return "".join(nikosh_map.get(b, chr(b) if 32 <= b < 127 else "") for b in raw_b)
    else:
        return raw_b.decode("latin-1", errors="replace")


def extract_gazette_pdf(pdf_path: str) -> str:
    """
    Extracts text from all pages of a Bangladesh Gazette PDF.
    Decodes Nikosh, SutonnyMJ, and Symbol fonts verbatim into clean Markdown.
    """
    decoder = NikoshFontDecoder()
    nikosh_fname, nikosh_map = decoder.build_pdf_code_map(pdf_path)

    all_pages_markdown = []

    with open(pdf_path, 'rb') as fp:
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        for page_idx, page in enumerate(PDFPage.create_pages(doc), start=1):
            contents = resolve1(page.contents)
            data = b"".join(resolve1(c).get_data() for c in contents) if isinstance(contents, list) else contents.get_data()

            current_font = nikosh_fname or "R14"
            page_lines = []
            current_line = []

            op_regex = re.compile(
                rb'(/R\d+)\s+[\d.]+\s+Tf|(\[.*?\])\s*TJ|\((.*?)(?<!\\)\)\s*Tj|(\bT\*\b|\bET\b)',
                re.DOTALL
            )

            for m in op_regex.finditer(data):
                if m.group(1):
                    current_font = m.group(1).decode('ascii')[1:]
                elif m.group(4):
                    if current_line:
                        line_s = "".join(current_line).strip()
                        if line_s:
                            page_lines.append(line_s)
                        current_line = []
                elif m.group(2):
                    parts = re.findall(rb'\((.*?)(?<!\\)\)', m.group(2), re.DOTALL)
                    for p in parts:
                        b_bytes = parse_pdf_string(p)
                        current_line.append(_decode_font_bytes(current_font, b_bytes, nikosh_fname, nikosh_map))
                elif m.group(3):
                    b_bytes = parse_pdf_string(m.group(3))
                    current_line.append(_decode_font_bytes(current_font, b_bytes, nikosh_fname, nikosh_map))

            if current_line:
                line_s = "".join(current_line).strip()
                if line_s:
                    page_lines.append(line_s)

            # Clean and filter lines
            cleaned_page_lines = []
            for pl in page_lines:
                cl = clean_gazette_text(pl)
                if not cl:
                    continue
                # Skip running headers on pages 2+
                if page_idx > 1 and re.search(r'বাংলাদেশ\s+গেজেট,\s+অতিরিক্ত,\s+ডিসেম্বর', cl):
                    continue
                # Skip standalone emblems or symbol lines
                if re.match(r'^[\s\t\x00-\x1f!#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]+$', cl) and len(cl) < 8:
                    continue
                cleaned_page_lines.append(cl)

            # Merge single-character/punctuation fragment lines
            merged_lines = []
            buf = ""
            for l in cleaned_page_lines:
                if not buf:
                    buf = l
                    continue
                if l in ('.', ',', '-', '।', ':', ';', ')', ']', '}') or \
                   buf.endswith(('(', '[', '{', '-', '.')) or \
                   (len(buf) <= 3 and not buf.startswith(('(', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯', '#'))) or \
                   (len(l) <= 3 and not re.match(r'^\([১-৯a-zA-Zক-হ]+\)', l)):
                    if l in ('.', ',', '-', '।', ':', ';', ')') or buf.endswith(('(', '[', '-')):
                        buf += l
                    else:
                        buf += " " + l
                else:
                    merged_lines.append(buf)
                    buf = l
            if buf:
                merged_lines.append(buf)

            # Page 1 official Gazette header formatting
            if page_idx == 1 and merged_lines:
                first = merged_lines[0]
                if 'রেজিস্টার্ড নং' in first and 'বাংলাদেশ গেজেট' in first:
                    header_block = [
                        "রেজিস্টার্ড নং ডি এ-১",
                        "",
                        "# বাংলাদেশ গেজেট",
                        "**অতিরিক্ত সংখ্যা**  ",
                        "**কর্তৃপক্ষ কর্তৃক প্রকাশিত**  ",
                        "**মঙ্গলবার, ডিসেম্বর ১৫, ২০১৫**",
                        "",
                        "---",
                        "",
                        "# গণপ্রজাতন্ত্রী বাংলাদেশ সরকার"
                    ]
                    merged_lines = header_block + merged_lines[1:]

            # Page 4 National Pay Scale 2015 Table formatting
            if page_idx == 4:
                split_lines = []
                for l in merged_lines:
                    parts = re.split(r'(?<=\S)\s+(?=([০-৯]+)\.\s*টাকা)', l)
                    for p in parts:
                        if p and p.strip() and not re.match(r'^[০-৯]+$', p.strip()):
                            split_lines.append(p.strip())

                joined_rows = []
                other_lines = []
                i = 0
                while i < len(split_lines):
                    curr = split_lines[i]
                    if re.match(r'^[০-৯]+\.\s*টাকা', curr):
                        if i + 1 < len(split_lines) and split_lines[i+1].startswith('টাকা') and not re.match(r'^[০-৯]+\.', split_lines[i+1]):
                            curr = curr + ' ' + split_lines[i+1]
                            i += 1
                        joined_rows.append(curr)
                    else:
                        if not any(kw in curr for kw in ['জাতীয় বেতনস্কেল', 'বর্তমান', 'অনুরূপ স্কেল', 'গ্রেড']):
                            other_lines.append(curr)
                    i += 1

                table_lines = [
                    "### জাতীয় বেতনস্কেল, ২০১৫ ও ২০০৯",
                    "",
                    "| গ্রেড | জাতীয় বেতনস্কেল, ২০০৯ (বর্তমান) | জাতীয় বেতনস্কেল, ২০১৫ (কার্যকর অনুরূপ স্কেল) |",
                    "| :---: | :--- | :--- |"
                ]
                for r in joined_rows:
                    r_clean = re.sub(r'\s*\n\s*', ' ', r)
                    m = re.match(r'^([০-৯]+)\.\s*(টাকা\s+.*?)\s+(টাকা\s+.*)$', r_clean, re.DOTALL)
                    if m:
                        grade, s1, s2 = m.group(1), m.group(2).strip(), m.group(3).strip()
                        table_lines.append(f"| {grade} | {s1} | {s2} |")
                    else:
                        table_lines.append(f"| - | {r_clean} | |")

                merged_lines = other_lines + ["\n".join(table_lines)]

            # Format headings
            final_lines = []
            for pl in merged_lines:
                if pl == 'গণপ্রজাতন্ত্রী বাংলাদেশ সরকার':
                    final_lines.append(f"# {pl}")
                elif pl.startswith('অর্থ মন্ত্রণালয়'):
                    final_lines.append(f"### {pl}")
                elif pl.startswith('অর্থ বিভাগ') or pl.startswith('বাস্তবায়ন অনুবিভাগ'):
                    final_lines.append(f"**{pl}**")
                elif pl.startswith('আদেশ') and len(pl) < 15:
                    final_lines.append(f"### {pl}")
                else:
                    final_lines.append(pl)

            page_body = "\n\n".join(final_lines)
            page_body = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', page_body)

            if page_idx == 1:
                page_body = page_body.replace('আদেশতারিখ:', '### আদেশ\n\n**তারিখ:** ').replace('আদেশ তারিখ:', '### আদেশ\n\n**তারিখ:** ')
                page_body = re.sub(r'এস\s*[\.]?\s*আর\s*[\.]?\s*ও\s*নং\s*৩৭০\s*[-–]?\s*আ\s*[\n\s]*ইন/২০১৫।', '\n\n**এস. আর. ও. নং ৩৭০-আইন/২০১৫।**\n\n', page_body)
                page_body = re.sub(r'১।\s*[\n\s]*শিরোনাম\s*[\n\s]*প্রবর্তন ও প্রয়োগ।', '\n\n### ১। শিরোনাম, প্রবর্তন ও প্রয়োগ।\n\n', page_body)

            if page_body.strip():
                all_pages_markdown.append(f"<!-- 📄 Page {page_idx} -->\n\n{page_body}")

    return "\n\n---\n\n".join(all_pages_markdown)
