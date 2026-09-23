# -*- coding: utf-8 -*-
"""
High-Fidelity Microsoft Word (.docx) Exporter for MarkItDown Studio.
Supports:
- Nested lists with arbitrary indentation levels
- Recursive nested inline formatting (**bold *italic* bold**)
- Offline Data URIs, local images, and remote HTTP/HTTPS images with timeout and error logging
- Footnotes ([^1] references and definitions)
- Table of Contents (TOC) and Page Numbers in footer
- Bengali typography font selection (Kalpurush, Hind Siliguri, etc.)
- Shaded code blocks with border styling and monospace font
- LaTeX / KaTeX mathematical expressions
"""

import io
import os
import re
import base64
import logging
from typing import Optional, List, Dict, Tuple, Any

import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

logger = logging.getLogger(__name__)


def add_styled_paragraph_runs(
    paragraph,
    text: str,
    base_font: Optional[str] = None,
    is_bold: bool = False,
    is_italic: bool = False,
    is_strike: bool = False,
):
    """
    Parse inline markdown formatting supporting nested tokens (e.g. **bold *italic* bold**),
    hyperlinks [text](url), inline code `code`, and footnotes [^1].
    """
    if not text:
        return

    # Tokenizer pattern for outermost tokens
    token_pattern = re.compile(
        r'(`[^`]+`)'                                         # 1. inline code
        r'|(\[[^\]]+\]\([^\)]+\))'                           # 2. hyperlink
        r'|(\[\^[a-zA-Z0-9_\-]+\])'                          # 3. footnote ref
        r'|(\*\*\*(?:[^*]|\*(?!\*\*))+\*\*\*)'               # 4. bold+italic
        r'|(\*\*(?:[^*]|\*(?!\*))+\*\*)'                     # 5. bold
        r'|((?<!\*)\*[^*]+?\*(?!\*)|(?<!_)_[^_]+?_(?!_))'    # 6. italic
        r'|(~~(?:[^~]|~(?!~))+~~)'                           # 7. strikethrough
    )

    last_idx = 0
    for match in token_pattern.finditer(text):
        start, end = match.span()
        # Plain text segment before match
        if start > last_idx:
            plain_text = text[last_idx:start]
            run = paragraph.add_run(plain_text)
            if base_font: run.font.name = base_font
            if is_bold: run.bold = True
            if is_italic: run.italic = True
            if is_strike: run.font.strike = True

        matched_str = match.group(0)

        if matched_str.startswith('`') and matched_str.endswith('`'):
            run = paragraph.add_run(matched_str[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(180, 40, 80)

        elif matched_str.startswith('[^') and matched_str.endswith(']'):
            fn_id = matched_str[2:-1]
            run = paragraph.add_run(f"[{fn_id}]")
            run.font.superscript = True
            run.font.color.rgb = RGBColor(0, 102, 204)

        elif matched_str.startswith('[') and '](' in matched_str and matched_str.endswith(')'):
            link_text = matched_str[1:matched_str.index('](')]
            run = paragraph.add_run(link_text)
            if base_font: run.font.name = base_font
            run.underline = True
            run.font.color.rgb = RGBColor(0, 102, 204)

        elif matched_str.startswith('***') and matched_str.endswith('***'):
            inner = matched_str[3:-3]
            add_styled_paragraph_runs(paragraph, inner, base_font=base_font, is_bold=True, is_italic=True, is_strike=is_strike)

        elif matched_str.startswith('**') and matched_str.endswith('**'):
            inner = matched_str[2:-2]
            add_styled_paragraph_runs(paragraph, inner, base_font=base_font, is_bold=True, is_italic=is_italic, is_strike=is_strike)

        elif (matched_str.startswith('*') and matched_str.endswith('*')) or (matched_str.startswith('_') and matched_str.endswith('_')):
            inner = matched_str[1:-1]
            add_styled_paragraph_runs(paragraph, inner, base_font=base_font, is_bold=is_bold, is_italic=True, is_strike=is_strike)

        elif matched_str.startswith('~~') and matched_str.endswith('~~'):
            inner = matched_str[2:-2]
            add_styled_paragraph_runs(paragraph, inner, base_font=base_font, is_bold=is_bold, is_italic=is_italic, is_strike=True)

        else:
            run = paragraph.add_run(matched_str)
            if base_font: run.font.name = base_font
            if is_bold: run.bold = True
            if is_italic: run.italic = True
            if is_strike: run.font.strike = True

        last_idx = end

    if last_idx < len(text):
        remaining = text[last_idx:]
        run = paragraph.add_run(remaining)
        if base_font: run.font.name = base_font
        if is_bold: run.bold = True
        if is_italic: run.italic = True
        if is_strike: run.font.strike = True


def add_footer_page_number(run):
    """Add a dynamic Word page number field to a footer run."""
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    run._r.append(fldSimple)


def add_footer_total_pages(run):
    """Add a dynamic Word total page count field to a footer run."""
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="NUMPAGES"/>' % nsdecls('w'))
    run._r.append(fldSimple)


def add_table_of_contents(doc):
    """Insert a standard Word Table of Contents (TOC) field."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run("সূচিপত্র / Table of Contents\n")
    r.bold = True
    r.font.size = Pt(13)
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="TOC \o &quot;1-3&quot; \h \z \u"/>' % nsdecls('w'))
    p._p.append(fldSimple)


def add_styled_code_block(doc, code_text: str):
    """Insert a code block with shaded background, left blue border, and Consolas font."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    pPr = p._p.get_or_add_pPr()

    # Add light gray background shading
    shd = parse_xml(r'<w:shd %s w:fill="F4F4F6"/>' % nsdecls('w'))
    pPr.append(shd)

    # Add stylish left border
    pBdr = parse_xml(r'<w:pBdr %s><w:left w:val="single" w:sz="18" w:space="8" w:color="0078D7"/></w:pBdr>' % nsdecls('w'))
    pPr.append(pBdr)

    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(40, 40, 40)


def markdown_to_docx_bytes(
    markdown_text: str,
    title: str = "Document",
    bengali_font: str = "Kalpurush",
    include_toc: bool = False,
    include_page_numbers: bool = True,
) -> bytes:
    """
    Convert Markdown to Microsoft Word (.docx) byte stream with full typography support,
    nested lists, nested inline styles, image downloads, footnotes, and page numbers.
    """
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Configure Default Style Font
    style = doc.styles['Normal']
    font = style.font
    font.name = bengali_font
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 30, 30)

    # Page Numbers in Footer
    if include_page_numbers and doc.sections:
        footer = doc.sections[0].footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_txt1 = footer_p.add_run("Page ")
        r_txt1.font.size = Pt(9)
        r_txt1.font.color.rgb = RGBColor(120, 120, 120)
        r_page = footer_p.add_run()
        add_footer_page_number(r_page)
        r_page.font.size = Pt(9)
        r_page.font.color.rgb = RGBColor(120, 120, 120)
        r_txt2 = footer_p.add_run(" of ")
        r_txt2.font.size = Pt(9)
        r_txt2.font.color.rgb = RGBColor(120, 120, 120)
        r_total = footer_p.add_run()
        add_footer_total_pages(r_total)
        r_total.font.size = Pt(9)
        r_total.font.color.rgb = RGBColor(120, 120, 120)

    # Check for [TOC] in text or include_toc parameter
    if include_toc or re.search(r'^\s*(\[TOC\]|<!--\s*TOC\s*-->)\s*$', markdown_text, re.MULTILINE):
        add_table_of_contents(doc)
        markdown_text = re.sub(r'^\s*(\[TOC\]|<!--\s*TOC\s*-->)\s*$', '', markdown_text, flags=re.MULTILINE)

    lines = markdown_text.split('\n')
    i = 0
    in_code_block = False
    code_block_lines = []
    table_lines = []
    footnotes: Dict[str, str] = {}

    def flush_table():
        nonlocal table_lines
        if not table_lines:
            return

        rows_data = []
        for tl in table_lines:
            stripped = tl.strip()
            if stripped.startswith('|') and stripped.endswith('|'):
                if re.match(r'^\|[\s:\-]+(?:\|[\s:\-]+)*\|$', stripped):
                    continue
                cells = [c.strip() for c in stripped[1:-1].split('|')]
                rows_data.append(cells)

        if rows_data:
            num_cols = max(len(r) for r in rows_data)
            table = doc.add_table(rows=len(rows_data), cols=num_cols)
            table.style = 'Table Grid'
            for r_idx, row in enumerate(rows_data):
                for c_idx, cell_value in enumerate(row):
                    if c_idx < num_cols:
                        cell = table.cell(r_idx, c_idx)
                        p = cell.paragraphs[0]
                        p.text = ""
                        add_styled_paragraph_runs(p, cell_value, base_font=bengali_font)
                        if r_idx == 0:
                            for run in p.runs:
                                run.bold = True
                            shd = parse_xml(r'<w:shd %s w:fill="F2F2F2"/>' % nsdecls('w'))
                            cell._tc.get_or_add_tcPr().append(shd)

        table_lines = []
        doc.add_paragraph()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 0. Footnote Definition: [^1]: Note text
        fn_match = re.match(r'^\s*\[\^([a-zA-Z0-9_\-]+)\]:\s+(.*)$', line)
        if fn_match:
            fn_id = fn_match.group(1)
            fn_text = fn_match.group(2)
            footnotes[fn_id] = fn_text
            i += 1
            continue

        # 1. Code Blocks
        if stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                add_styled_code_block(doc, '\n'.join(code_block_lines))
                code_block_lines = []
            else:
                if table_lines:
                    flush_table()
                in_code_block = True
                code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # 2. Tables
        if stripped.startswith('|') and stripped.endswith('|'):
            table_lines.append(line)
            i += 1
            continue
        elif table_lines:
            flush_table()

        # 3. Blank lines
        if not stripped:
            i += 1
            continue

        # 4. Horizontal Rules
        if stripped in ('---', '***', '___'):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run('—' * 30)
            run.font.color.rgb = RGBColor(180, 180, 180)
            i += 1
            continue

        # 4.5 Image handling: ![alt](src)
        img_match = re.match(r'^\s*!\[(.*?)\]\((.*?)\)\s*$', stripped)
        if img_match:
            alt_text = img_match.group(1) or "Image"
            img_src = img_match.group(2).strip()
            image_inserted = False

            if img_src.startswith('data:image/'):
                try:
                    b64_part = img_src.split(',', 1)[1]
                    raw_bytes = base64.b64decode(b64_part)
                    stream = io.BytesIO(raw_bytes)
                    doc.add_picture(stream, width=Inches(5.0))
                    image_inserted = True
                except Exception as b64_err:
                    logger.warning("Failed to decode base64 image: %s", b64_err)

            elif img_src.startswith(('http://', 'https://')):
                try:
                    import requests
                    resp = requests.get(img_src, timeout=8.0, headers={'User-Agent': 'MarkItDownStudio/3.2'})
                    if resp.status_code == 200:
                        stream = io.BytesIO(resp.content)
                        doc.add_picture(stream, width=Inches(5.0))
                        image_inserted = True
                    else:
                        logger.warning("Remote image fetch failed (%d): %s", resp.status_code, img_src)
                except Exception as http_err:
                    logger.warning("Failed to download remote image %s: %s", img_src, http_err)

            elif os.path.exists(img_src):
                try:
                    doc.add_picture(img_src, width=Inches(5.0))
                    image_inserted = True
                except Exception as file_err:
                    logger.warning("Failed to read local image %s: %s", img_src, file_err)

            if image_inserted:
                caption_p = doc.add_paragraph()
                caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption_run = caption_p.add_run(f"চিত্র: {alt_text}")
                caption_run.font.name = bengali_font
                caption_run.font.size = Pt(9.5)
                caption_run.font.italic = True
                caption_run.font.color.rgb = RGBColor(120, 120, 120)
                i += 1
                continue

        # 4.6 Math display block: $$ ... $$
        if stripped.startswith('$$'):
            formula = stripped.strip('$').strip()
            if not formula and i + 1 < len(lines):
                i += 1
                math_lines = []
                while i < len(lines) and not lines[i].strip().startswith('$$'):
                    math_lines.append(lines[i].strip())
                    i += 1
                formula = ' '.join(math_lines).strip()

            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            math_run = p.add_run(f"∑  {formula}")
            math_run.font.name = 'Cambria Math'
            math_run.font.size = Pt(11.5)
            math_run.font.italic = True
            math_run.font.color.rgb = RGBColor(0, 102, 204)
            i += 1
            continue

        # 5. Headings
        if stripped.startswith('#'):
            level_match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if level_match:
                level = len(level_match.group(1))
                h_text = level_match.group(2)
                h = doc.add_heading(level=min(level, 4))
                add_styled_paragraph_runs(h, h_text, base_font=bengali_font)
                i += 1
                continue

        # 6. Blockquotes
        if stripped.startswith('>'):
            quote_text = re.sub(r'^>\s*', '', stripped)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            run = p.add_run('│ ')
            run.font.color.rgb = RGBColor(0, 120, 215)
            run.bold = True
            add_styled_paragraph_runs(p, quote_text, base_font=bengali_font)
            for r in p.runs:
                r.italic = True
            i += 1
            continue

        # 7. Nested Unordered / Task List
        bullet_match = re.match(r'^(\s*)[-*+]\s+(?:\[([ xX])\]\s+)?(.*)$', line)
        if bullet_match:
            indent_spaces = len(bullet_match.group(1))
            indent_level = min(4, indent_spaces // 2)
            is_task = bullet_match.group(2) is not None
            task_checked = bullet_match.group(2) in ('x', 'X') if is_task else False
            item_text = bullet_match.group(3)

            prefix = "☑ " if (is_task and task_checked) else ("☐ " if is_task else "")
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            if prefix:
                r_pre = p.add_run(prefix)
                r_pre.font.name = bengali_font
            add_styled_paragraph_runs(p, item_text, base_font=bengali_font)
            i += 1
            continue

        # 8. Nested Ordered List
        num_match = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
        if num_match:
            indent_spaces = len(num_match.group(1))
            indent_level = min(4, indent_spaces // 2)
            item_text = num_match.group(2)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            add_styled_paragraph_runs(p, item_text, base_font=bengali_font)
            i += 1
            continue

        # 9. Regular Paragraph
        p = doc.add_paragraph()
        add_styled_paragraph_runs(p, line, base_font=bengali_font)
        i += 1

    if table_lines:
        flush_table()

    # Append Footnotes Section if any footnotes were defined
    if footnotes:
        doc.add_paragraph()
        p_fn_head = doc.add_paragraph()
        r_fn_head = p_fn_head.add_run("পাদটীকা / Footnotes")
        r_fn_head.bold = True
        r_fn_head.font.size = Pt(11)
        r_fn_head.font.name = bengali_font

        for fn_id, fn_text in footnotes.items():
            p_fn = doc.add_paragraph()
            p_fn.paragraph_format.left_indent = Inches(0.2)
            r_id = p_fn.add_run(f"[{fn_id}] ")
            r_id.font.superscript = True
            r_id.font.color.rgb = RGBColor(0, 102, 204)
            add_styled_paragraph_runs(p_fn, fn_text, base_font=bengali_font)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
