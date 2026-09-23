# -*- coding: utf-8 -*-
"""
Core Document Conversion Engine.
Shared by Desktop GUI and future Web/API endpoints.
"""

import os
import time
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Any, Generator
from markitdown import MarkItDown

logger = logging.getLogger(__name__)

# List of all file extensions natively supported by MarkItDown
SUPPORTED_EXTENSIONS = {
    # Documents
    ".pdf": "PDF Document",
    ".docx": "Microsoft Word",
    ".pptx": "Microsoft PowerPoint",
    ".xlsx": "Microsoft Excel (modern)",
    ".xls": "Microsoft Excel (legacy)",
    ".epub": "eBook (EPub)",
    # Text / Data
    ".txt": "Plain Text",
    ".md": "Markdown",
    ".csv": "CSV Spreadsheet",
    ".tsv": "TSV Spreadsheet",
    ".json": "JSON Data",
    ".xml": "XML Document",
    ".html": "HTML Webpage",
    ".htm": "HTML Webpage",
    # Media
    ".wav": "Audio (WAV)",
    ".mp3": "Audio (MP3)",
    ".m4a": "Audio (M4A)",
    # Images (EXIF + optional OCR)
    ".jpg": "JPEG Image",
    ".jpeg": "JPEG Image",
    ".png": "PNG Image",
    # Archives
    ".zip": "ZIP Archive",
}


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable units (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


@dataclass
class ConversionResult:
    """Detailed result object for a file conversion."""
    file_path: str
    file_name: str
    file_size_bytes: int
    file_size_str: str
    markdown: str
    title: Optional[str] = None
    duration_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class DocumentConverter:
    """
    Main conversion service wrapper.
    Encapsulates MarkItDown instance and configuration.
    """

    def __init__(
        self,
        enable_plugins: bool = False,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o",
        openai_base_url: Optional[str] = None,
        docintel_endpoint: Optional[str] = None,
    ):
        self.enable_plugins = enable_plugins
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.llm_model = llm_model
        self.openai_base_url = openai_base_url
        self.docintel_endpoint = docintel_endpoint
        self._init_engine()

    def _init_engine(self):
        """Initialize or re-initialize MarkItDown with current config."""
        kwargs: Dict[str, Any] = {
            "enable_plugins": self.enable_plugins,
        }

        # Optional OpenAI / Compatible Relay LLM for OCR/Vision
        if self.openai_api_key:
            try:
                from openai import OpenAI
                effective_base_url = (self.openai_base_url or os.environ.get("OPENAI_BASE_URL") or "").strip()
                client_kwargs = {"api_key": self.openai_api_key}
                if effective_base_url:
                    client_kwargs["base_url"] = effective_base_url.rstrip("/") + "/"
                kwargs["llm_client"] = OpenAI(**client_kwargs)
                kwargs["llm_model"] = self.llm_model
            except ImportError:
                pass

        # Optional Document Intelligence Endpoint
        if self.docintel_endpoint:
            kwargs["docintel_endpoint"] = self.docintel_endpoint

        self._md = MarkItDown(**kwargs)

    def update_config(
        self,
        enable_plugins: Optional[bool] = None,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        docintel_endpoint: Optional[str] = None,
    ):
        """Update runtime configuration and re-initialize MarkItDown."""
        if enable_plugins is not None:
            self.enable_plugins = enable_plugins
        if openai_api_key is not None:
            self.openai_api_key = openai_api_key
        if gemini_api_key is not None:
            self.gemini_api_key = gemini_api_key
        if llm_model is not None:
            self.llm_model = llm_model
        if openai_base_url is not None:
            self.openai_base_url = openai_base_url
        if docintel_endpoint is not None:
            self.docintel_endpoint = docintel_endpoint
        self._init_engine()

    def is_supported(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = Path(file_path).suffix.lower()
        return ext in SUPPORTED_EXTENSIONS

    def convert_file(self, file_path: str) -> ConversionResult:
        """
        Convert a single local file to Markdown.
        Handles large files without in-memory artificial restrictions.
        """
        p = Path(file_path)
        if not p.exists():
            return ConversionResult(
                file_path=file_path,
                file_name=p.name,
                file_size_bytes=0,
                file_size_str="0 B",
                markdown="",
                success=False,
                error_message=f"File not found: {file_path}",
            )

        file_size = p.stat().st_size
        file_size_str = format_file_size(file_size)
        start_time = time.perf_counter()

        try:
            is_pdf = p.suffix.lower() == ".pdf"
            is_image = p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".bmp")

            # 1. Specialized handling for Bangladesh Gazette / Nikosh CID PDFs
            if is_pdf:
                try:
                    from core.gazette_extractor import is_gazette_pdf, extract_gazette_pdf
                    if is_gazette_pdf(str(p.resolve())):
                        gazette_text = extract_gazette_pdf(str(p.resolve()))
                        if gazette_text and len(gazette_text.strip()) > 100:
                            elapsed = time.perf_counter() - start_time
                            return ConversionResult(
                                file_path=str(p.resolve()),
                                file_name=p.name,
                                file_size_bytes=file_size,
                                file_size_str=file_size_str,
                                markdown=gazette_text,
                                title=p.stem,
                                duration_seconds=elapsed,
                                success=True,
                                error_message=None,
                            )
                except Exception as gaz_err:
                    logger.warning("Gazette extractor notice: %s", gaz_err)

            # Run MarkItDown conversion
            res = self._md.convert(str(p.resolve()))
            markdown_content = res.text_content

            # If it's an image, run OCR text extraction
            if is_image:
                try:
                    from core.ocr import extract_text_from_image
                    ocr_text = extract_text_from_image(
                        p,
                        openai_api_key=self.openai_api_key,
                        openai_model=self.llm_model,
                        openai_base_url=self.openai_base_url,
                    )
                    if ocr_text and "No readable text detected" not in ocr_text:
                        markdown_content = f"{markdown_content}\n\n### 📝 Extracted Image Text (OCR):\n\n{ocr_text}\n"
                    elif ocr_text:
                        markdown_content = f"{markdown_content}\n\n_{ocr_text}_\n"
                except Exception as ocr_err:
                    logger.warning("OCR warning: %s", ocr_err)

            # Auto-detect and convert legacy ANSI/Bijoy Bengali to modern Unicode
            try:
                from core.bengali import auto_convert_text
                markdown_content = auto_convert_text(markdown_content)
            except Exception as be_err:
                logger.warning("Bengali conversion warning: %s", be_err)

            # Smart PDF CID Font & Scanned Document Handling
            is_pdf = p.suffix.lower() == ".pdf"
            if is_pdf:
                import re
                cid_count = len(re.findall(r'\(?cid:\d+\)?', markdown_content, re.IGNORECASE))
                is_scanned_or_cid = (cid_count > 10) or (len(markdown_content.strip()) < 30)

                if is_scanned_or_cid:
                    has_vision_api = bool(
                        (self.openai_api_key and self.openai_api_key.strip()) or
                        (self.gemini_api_key and self.gemini_api_key.strip())
                    )

                    if has_vision_api:
                        try:
                            from core.ocr import extract_text_from_pdf_pages
                            ocr_result = extract_text_from_pdf_pages(
                                p,
                                openai_api_key=self.openai_api_key,
                                gemini_api_key=self.gemini_api_key,
                                openai_model=self.llm_model,
                                openai_base_url=self.openai_base_url,
                            )
                            if ocr_result and "⚠️" not in ocr_result:
                                markdown_content = ocr_result
                        except Exception as pdf_ocr_err:
                            logger.error("PDF Vision OCR error: %s", pdf_ocr_err)
                    else:
                        # Clean excessive (cid:X) noise to prevent freezing editor and provide clear user notice
                        cleaned_lines = []
                        for line in markdown_content.split('\n'):
                            if len(re.findall(r'\(?cid:\d+\)?', line, re.IGNORECASE)) > 1:
                                continue
                            cleaned_lines.append(line)
                        clean_body = "\n".join(cleaned_lines).strip()

                        notice = (
                            "\n\n> [!WARNING]\n"
                            "> **পিডিএফ ফন্ট নোটিশ (CID Font / Scanned PDF Detected):**\n"
                            "> এই গেজেট বা পিডিএফ ফাইলের ভেতরের লেখাগুলো একটি কাস্টম ফন্ট (`Nikosh`) দিয়ে সংরক্ষিত, যাতে ইউনিকোড ক্যারেক্টার ম্যাপ (CMap) নেই। ফলে সাধারণ টেক্সট এক্সট্রাক্টর অক্ষরগুলো সরাসরি পড়তে পারছে না।\n"
                            ">\n"
                            "> 💡 **১০০% নিখুঁত ও হুবহু বাংলা টেক্সট পেতে:**\n"
                            "> উপরের ডান পাশের ⚙️ **Settings** থেকে আপনার **OpenAI API Key** (gpt-4o) অথবা **Gemini API Key** যুক্ত করুন। AI Vision স্বয়ংক্রিয়ভাবে প্রতিটি পাতা পড়ে হুবহু বাংলা মার্কডাউনে রূপান্তর করবে!\n"
                        )
                        markdown_content = f"{clean_body}\n{notice}" if clean_body else notice

            elapsed = time.perf_counter() - start_time

            return ConversionResult(
                file_path=str(p.resolve()),
                file_name=p.name,
                file_size_bytes=file_size,
                file_size_str=file_size_str,
                markdown=markdown_content,
                title=getattr(res, "title", None) or p.stem,
                duration_seconds=elapsed,
                success=True,
                error_message=None,
            )
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return ConversionResult(
                file_path=str(p.resolve()),
                file_name=p.name,
                file_size_bytes=file_size,
                file_size_str=file_size_str,
                markdown="",
                title=p.stem,
                duration_seconds=elapsed,
                success=False,
                error_message=str(e),
            )

    def convert_batch(
        self,
        file_paths: List[str],
        callback: Optional[Callable[[int, int, ConversionResult], None]] = None,
    ) -> Generator[ConversionResult, None, None]:
        """
        Convert a batch of files sequentially.
        Calls optional callback(index, total, result) on each completed item.
        """
        total = len(file_paths)
        for idx, path in enumerate(file_paths, start=1):
            result = self.convert_file(path)
            if callback:
                callback(idx, total, result)
            yield result
