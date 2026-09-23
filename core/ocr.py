# -*- coding: utf-8 -*-
"""
OCR Engine for MarkItDown.
Extracts Bengali and English text from images.
Supports:
1. Windows Native Media OCR (100% Offline & Free)
2. OpenAI Vision (GPT-4o) for high-accuracy handwritten/complex scans
"""

import os
import base64
import logging
from pathlib import Path
from typing import Optional, Union, Callable, Any
from PIL import Image

logger = logging.getLogger(__name__)

# Check for winocr (Windows 10/11 built-in OCR)
try:
    import winocr
    HAS_WINOCR = True
except Exception:
    HAS_WINOCR = False

# Check for pytesseract
try:
    import pytesseract
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False


def extract_text_from_image(
    image_input: Union[str, Path, Image.Image],
    openai_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    openai_model: Optional[str] = None,
    openai_base_url: Optional[str] = None,
    gemini_model: Optional[str] = None,
    language: str = "auto",
) -> str:
    """
    Extract text (Bengali & English) from an image.
    Supports:
    1. OpenAI Vision & Custom Relay (GPT-4o, DeepSeek, HCNSEC, etc.)
    2. Google Gemini Vision (Gemini 1.5 Flash / 2.0 Flash)
    3. Windows Native Media OCR (Offline, Windows 10/11)
    4. Tesseract OCR (Fallback)
    """
    eff_openai_model = openai_model or os.environ.get("OPENAI_MODEL") or "gpt-4o"
    eff_gemini_model = gemini_model or os.environ.get("GEMINI_MODEL") or "gemini-1.5-flash"

    # 1. AI Vision OCR via OpenAI or Compatible Relay
    if openai_api_key and openai_api_key.strip():
        try:
            return _ocr_via_openai(
                image_input,
                api_key=openai_api_key,
                model=eff_openai_model,
                base_url=openai_base_url,
            )
        except Exception as e:
            logger.warning("OpenAI / Custom Relay OCR error: %s. Falling back...", e)

    # 2. AI Vision OCR via Google Gemini
    if gemini_api_key and gemini_api_key.strip():
        try:
            return _ocr_via_gemini(image_input, gemini_api_key, model=eff_gemini_model)
        except Exception as e:
            logger.warning("Gemini OCR error: %s. Falling back...", e)

    # 3. Windows Native OCR (Offline, Windows 10/11)
    if HAS_WINOCR:
        try:
            return _ocr_via_winocr(image_input)
        except Exception as e:
            logger.error("Windows OCR error: %s", e)

    # 4. Tesseract OCR (Fallback if installed)
    if HAS_TESSERACT:
        try:
            pil_img = _ensure_pil(image_input)
            lang = "ben+eng" if "ben" in pytesseract.get_languages() else "eng"
            return pytesseract.image_to_string(pil_img, lang=lang).strip()
        except Exception:
            pass

    return "⚠️ Could not extract text: Configure an OpenAI or Gemini API key in Settings for AI Vision OCR."


def _ensure_pil(image_input: Union[str, Path, Image.Image]) -> Image.Image:
    if isinstance(image_input, Image.Image):
        return image_input
    return Image.open(str(image_input))


def _ocr_via_winocr(image_input: Union[str, Path, Image.Image]) -> str:
    pil_img = _ensure_pil(image_input)
    # Convert RGBA or Palette to RGB for OCR compatibility
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    res = winocr.recognize_pil_sync(pil_img)
    text = res.get("text", "").strip() if isinstance(res, dict) else ""
    return text if text else "⚠️ No readable text detected in this image."


def _ocr_via_openai(
    image_input: Union[str, Path, Image.Image],
    api_key: str,
    model: str = "gpt-4o",
    base_url: Optional[str] = None,
    timeout: float = 60.0,
) -> str:
    import io
    from openai import OpenAI

    pil_img = _ensure_pil(image_input)
    buf = io.BytesIO()
    # Save as PNG/JPEG in buffer
    fmt = "PNG" if pil_img.mode in ("RGBA", "P") else "JPEG"
    pil_img.save(buf, format=fmt)
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/png" if fmt == "PNG" else "image/jpeg"

    effective_base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "").strip()
    client_kwargs = {"api_key": api_key, "timeout": timeout}
    if effective_base_url:
        client_kwargs["base_url"] = effective_base_url.rstrip("/") + "/"
    client = OpenAI(**client_kwargs)

    prompt = (
        "Extract and transcribe ALL text from this image verbatim. "
        "Pay special attention to Bengali (বাংলা) and English characters, formatting, tables, "
        "headings, and mathematical symbols. Output strictly as clean GitHub-Flavored Markdown. "
        "Do not include conversational preamble or markdown code fences unless the image content is code."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64_str}"},
                    },
                ],
            }
        ],
        max_tokens=4000,
    )
    return response.choices[0].message.content.strip()


def _ocr_via_gemini(
    image_input: Union[str, Path, Image.Image],
    api_key: str,
    model: str = "gemini-1.5-flash",
) -> str:
    """Run OCR via Google Gemini REST API (no extra pip package required)."""
    import io
    import json
    import urllib.request

    pil_img = _ensure_pil(image_input)
    buf = io.BytesIO()
    fmt = "PNG" if pil_img.mode in ("RGBA", "P") else "JPEG"
    pil_img.save(buf, format=fmt)
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/png" if fmt == "PNG" else "image/jpeg"

    prompt = (
        "Extract and transcribe ALL text from this document image verbatim. "
        "Pay special attention to Bengali (বাংলা) and English characters, formatting, tables, "
        "headings, and mathematical symbols. Output strictly as clean GitHub-Flavored Markdown. "
        "Do not include conversational preamble or markdown code fences."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime, "data": b64_str}}
            ]
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=60) as resp:  # nosec B310
        data = json.loads(resp.read().decode("utf-8"))
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
    return ""


def extract_text_from_pdf_pages(
    pdf_path: Union[str, Path],
    openai_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    openai_model: Optional[str] = None,
    openai_base_url: Optional[str] = None,
    gemini_model: Optional[str] = None,
    max_pages: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], Optional[bool]]] = None,
    cancel_token: Optional[Any] = None,
) -> str:
    """
    Renders PDF pages to high-resolution images and transcribes them using AI Vision OCR.
    Crucial for PDFs with embedded CID fonts (missing ToUnicode CMap, e.g. Bangladesh Gazette)
    or scanned documents.
    """
    try:
        import pypdfium2
    except ImportError:
        return "⚠️ pypdfium2 is required for PDF page rendering."

    pdf_doc = pypdfium2.PdfDocument(str(pdf_path))
    doc_len = len(pdf_doc)
    if doc_len == 0:
        return ""

    if max_pages is not None and max_pages > 0:
        pages_to_process = min(doc_len, max_pages)
    else:
        pages_to_process = doc_len

    page_markdowns = []
    cancelled = False

    for i in range(pages_to_process):
        # Check cancellation
        if cancel_token and getattr(cancel_token, "is_set", lambda: False)():
            cancelled = True
            logger.info("PDF OCR processing cancelled at page %d/%d", i + 1, pages_to_process)
            break

        if progress_callback:
            continue_processing = progress_callback(i + 1, pages_to_process)
            if continue_processing is False:
                cancelled = True
                logger.info("PDF OCR processing cancelled by callback at page %d/%d", i + 1, pages_to_process)
                break

        page = pdf_doc[i]
        # Render at 2x scale (144 dpi) for optimal OCR clarity
        img = page.render(scale=2.0).to_pil()
        text = extract_text_from_image(
            img,
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
            openai_model=openai_model,
            openai_base_url=openai_base_url,
            gemini_model=gemini_model,
        )
        page_markdowns.append(f"<!-- 📄 Page {i+1} of {pages_to_process} -->\n\n{text}")

    result = "\n\n---\n\n".join(page_markdowns)

    if cancelled:
        result += f"\n\n> [!NOTE]\n> PDF OCR transcription cancelled by user after {len(page_markdowns)} of {doc_len} page(s).\n"
    elif doc_len > pages_to_process:
        result += (
            f"\n\n> [!WARNING]\n"
            f"> PDF OCR transcription completed for the first {pages_to_process} of {doc_len} page(s). "
            f"Pass a higher `max_pages` configuration to process the remaining {doc_len - pages_to_process} page(s).\n"
        )

    return result

