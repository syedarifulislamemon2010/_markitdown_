# -*- coding: utf-8 -*-
"""
Pluggable Structured Document Extraction Engine for MarkItDown Studio.
Generalizes document parsing using swappable, user-editable JSON template schemas
for Government Gazettes, Academic Papers, and Business Contracts/Invoices.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"

BN_DIGITS = "০১২৩৪৫৬৭৮৯"
EN_DIGITS = "0123456789"
BN_TO_EN_MAP = str.maketrans(BN_DIGITS, EN_DIGITS)
EN_TO_BN_MAP = str.maketrans(EN_DIGITS, BN_DIGITS)


def bn_to_en_digits(text: str) -> str:
    """Convert Bengali numerals to English digits."""
    return text.translate(BN_TO_EN_MAP)


def en_to_bn_digits(text: str) -> str:
    """Convert English digits to Bengali numerals."""
    return text.translate(EN_TO_BN_MAP)


# Bengali Calendar Months & Offsets (Bangladesh Revised Calendar)
BANGABDA_MONTHS = {
    "বৈশাখ": (1, "Baishakh", 31),
    "জ্যৈষ্ঠ": (2, "Jaishtha", 31),
    "আষাঢ়": (3, "Ashadha", 31),
    "আষাঢ়": (3, "Ashadha", 31),
    "শ্রাবণ": (4, "Shravana", 31),
    "ভাদ্র": (5, "Bhadra", 31),
    "আশ্বিন": (6, "Ashwin", 31),
    "কার্তিক": (7, "Kartik", 30),
    "অগ্রহায়ণ": (8, "Agrahayana", 30),
    "পৌষ": (9, "Pausha", 30),
    "মাঘ": (10, "Magha", 30),
    "ফাল্গুন": (11, "Phalguna", 30),
    "চৈত্র": (12, "Chaitra", 30),
}


def bangabda_to_gregorian_approx(bangabda_str: str) -> Optional[str]:
    """
    Convert a Bengali Bangabda date string (e.g. '১৫ অগ্রহায়ণ ১৪২২ বঙ্গাব্দ')
    to an approximate Gregorian calendar date.
    """
    pattern = r'([০-৯\d]+)\s*([^\s,]+)[,\s]+([০-৯\d]{4})'
    m = re.search(pattern, bangabda_str)
    if not m:
        return None

    day_str, month_str, year_str = m.group(1), m.group(2), m.group(3)
    try:
        b_day = int(bn_to_en_digits(day_str))
        b_year = int(bn_to_en_digits(year_str))
    except ValueError:
        return None

    month_clean = month_str.replace("বঙ্গাব্দ", "").strip()
    month_info = BANGABDA_MONTHS.get(month_clean)
    if not month_info:
        for k, v in BANGABDA_MONTHS.items():
            if k in month_clean:
                month_info = v
                break

    if not month_info:
        # Default rough conversion: Gregorian Year = Bangabda Year + 593
        return f"{b_year + 593} CE (Approx)"

    month_idx, _, _ = month_info
    # Months 1-9 (Baishakh to Pausha) are in Gregorian year + 593
    # Months 10-12 (Magha to Chaitra) are in Gregorian year + 594 (Jan-mid April)
    if month_idx >= 10:
        g_year = b_year + 594
    else:
        g_year = b_year + 593

    return f"{b_day} {month_info[1]}, {g_year} CE (Approx)"


def list_templates() -> List[Dict[str, Any]]:
    """List all available extraction templates (bundled and user-created)."""
    templates = []
    if TEMPLATES_DIR.is_dir():
        for p in TEMPLATES_DIR.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                templates.append({
                    "template_id": data.get("template_id", p.stem),
                    "title": data.get("title", p.stem),
                    "description": data.get("description", ""),
                    "category": data.get("category", "general"),
                    "version": data.get("version", "1.0.0"),
                    "path": str(p),
                })
            except Exception as e:
                logger.warning("Error reading template %s: %s", p, e)
    return templates


def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """Load a specific extraction template by ID."""
    if TEMPLATES_DIR.is_dir():
        for p in TEMPLATES_DIR.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("template_id") == template_id or p.stem == template_id:
                    return data
            except Exception:
                pass
    return None


def extract_structured_data(
    text: str,
    template_id_or_dict: Union[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Extract structured fields from text using a pluggable template schema.
    Returns parsed fields with confidence scores and a clean Markdown presentation.
    """
    if isinstance(template_id_or_dict, str):
        template = get_template(template_id_or_dict)
        if not template:
            return {
                "success": False,
                "error": f"Template '{template_id_or_dict}' not found."
            }
    else:
        template = template_id_or_dict

    fields_config = template.get("fields", [])
    extracted_fields = {}
    matched_count = 0
    total_fields = len(fields_config)

    for field in fields_config:
        name = field["name"]
        label = field.get("label", name)
        pattern = field["pattern"]
        field_type = field.get("type", "string")
        threshold = field.get("confidence_threshold", 0.7)

        try:
            regex = re.compile(pattern, re.MULTILINE)
            if field_type == "list":
                matches = regex.findall(text)
                cleaned_matches = []
                for m in matches:
                    val = m.strip() if isinstance(m, str) else " ".join(part.strip() for part in m if part)
                    if val and val not in cleaned_matches:
                        cleaned_matches.append(val)

                if cleaned_matches:
                    confidence = min(1.0, 0.7 + 0.1 * min(len(cleaned_matches), 3))
                    matched_count += 1
                else:
                    confidence = 0.0

                extracted_fields[name] = {
                    "label": label,
                    "type": "list",
                    "value": cleaned_matches,
                    "confidence": round(confidence, 2),
                    "passed_threshold": confidence >= threshold,
                }
            else:
                m = regex.search(text)
                if m:
                    # Prefer first non-empty group, otherwise entire match
                    groups = m.groups()
                    val = next((g.strip() for g in groups if g and g.strip()), m.group(0).strip())
                    confidence = 0.90 if len(val) > 3 else 0.75
                    matched_count += 1
                else:
                    val = None
                    confidence = 0.0

                # Bangabda Date auto-conversion enhancement
                extra = {}
                if name == "date_bangabda" and val:
                    greg_approx = bangabda_to_gregorian_approx(val)
                    if greg_approx:
                        extra["gregorian_converted"] = greg_approx

                extracted_fields[name] = {
                    "label": label,
                    "type": "string",
                    "value": val,
                    "confidence": round(confidence, 2),
                    "passed_threshold": confidence >= threshold,
                    **extra
                }
        except Exception as field_err:
            logger.warning("Error parsing field '%s': %s", name, field_err)
            extracted_fields[name] = {
                "label": label,
                "type": field_type,
                "value": None,
                "confidence": 0.0,
                "error": str(field_err),
            }

    overall_confidence = round(matched_count / total_fields, 2) if total_fields > 0 else 0.0

    # Build formatted Markdown summary table
    md_lines = [
        f"## 📋 {template.get('title', 'Structured Data')}",
        f"> **Template:** `{template.get('template_id', 'custom')}` | **Overall Confidence:** `{int(overall_confidence * 100)}%`",
        "",
        "| Field (ক্ষেত্র) | Extracted Value (নিষ্কাশিত মান) | Confidence |",
        "| :--- | :--- | :---: |",
    ]

    for name, f_data in extracted_fields.items():
        lbl = f_data["label"]
        val = f_data["value"]
        conf = f"{int(f_data['confidence'] * 100)}%"

        if f_data.get("type") == "list":
            val_str = ", ".join(val) if val else "—"
        else:
            val_str = str(val) if val else "—"

        if "gregorian_converted" in f_data:
            val_str += f" <br>*(≈ {f_data['gregorian_converted']})*"

        # Sanitize pipe symbols inside markdown table cells
        val_str = val_str.replace("|", "\\|").replace("\n", " ")
        md_lines.append(f"| **{lbl}** | {val_str} | {conf} |")

    return {
        "success": True,
        "template_id": template.get("template_id"),
        "template_title": template.get("title"),
        "overall_confidence": overall_confidence,
        "matched_fields": matched_count,
        "total_fields": total_fields,
        "fields": extracted_fields,
        "markdown_table": "\n".join(md_lines),
    }
