import io
import re
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def add_styled_paragraph_runs(paragraph, text):
    """
    Parse inline markdown formatting (**bold**, *italic*, `code`, ~~strike~~)
    and add them as formatted runs to the paragraph.
    """
    pattern = re.compile(r'(\*\*.*?\*\*|\*.*?\*|`.*?`|~~.*?~~|\[.*?\]\(.*?\))')
    parts = pattern.split(text)

    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(180, 40, 80)
        elif part.startswith('~~') and part.endswith('~~') and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.font.strike = True
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            link_text = part[1:part.index('](')]
            run = paragraph.add_run(link_text)
            run.underline = True
            run.font.color.rgb = RGBColor(0, 102, 204)
        else:
            paragraph.add_run(part)


def markdown_to_docx_bytes(markdown_text: str, title: str = "Document") -> bytes:
    """
    Convert a Markdown string into a formatted Microsoft Word (.docx) byte stream.
    Supports headings, paragraphs, bold, italic, lists, tables, blockquotes, and code.
    """
    doc = docx.Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Set default style font to Calibri / Hind Siliguri / Segoe UI
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Segoe UI'
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 30, 30)

    lines = markdown_text.split('\n')
    i = 0
    in_code_block = False
    code_block_lines = []
    table_lines = []

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
                        add_styled_paragraph_runs(p, cell_value)
                        if r_idx == 0:
                            for run in p.runs:
                                run.bold = True
                            shd = parse_xml(r'<w:shd {} w:fill="F2F2F2"/>'.format(nsdecls('w')))
                            cell._tc.get_or_add_tcPr().append(shd)

        table_lines = []
        doc.add_paragraph()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 1. Code Blocks
        if stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                p = doc.add_paragraph('\n'.join(code_block_lines))
                p.style = 'Normal'
                for run in p.runs:
                    run.font.name = 'Consolas'
                    run.font.size = Pt(9.5)
                    run.font.color.rgb = RGBColor(40, 40, 40)
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

        # 5. Headings
        if stripped.startswith('#'):
            level_match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if level_match:
                level = len(level_match.group(1))
                h_text = level_match.group(2)
                h = doc.add_heading(level=min(level, 4))
                add_styled_paragraph_runs(h, h_text)
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
            add_styled_paragraph_runs(p, quote_text)
            for r in p.runs:
                r.italic = True
            i += 1
            continue

        # 7. Unordered / Task List
        bullet_match = re.match(r'^\s*[-*+]\s+(?:\[([ xX])\]\s+)?(.*)$', line)
        if bullet_match:
            is_task = bullet_match.group(1) is not None
            task_checked = bullet_match.group(1) in ('x', 'X') if is_task else False
            item_text = bullet_match.group(2)

            prefix = "☑ " if (is_task and task_checked) else ("☐ " if is_task else "")
            p = doc.add_paragraph(style='List Bullet')
            if prefix:
                p.add_run(prefix)
            add_styled_paragraph_runs(p, item_text)
            i += 1
            continue

        # 8. Ordered List
        num_match = re.match(r'^\s*\d+\.\s+(.*)$', line)
        if num_match:
            item_text = num_match.group(1)
            p = doc.add_paragraph(style='List Number')
            add_styled_paragraph_runs(p, item_text)
            i += 1
            continue

        # 9. Regular Paragraph
        p = doc.add_paragraph()
        add_styled_paragraph_runs(p, line)
        i += 1

    if table_lines:
        flush_table()

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
