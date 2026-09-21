# -*- coding: utf-8 -*-
"""
Local Lightweight Backend Server for MarkItDown Studio.
Serves the web application and exposes endpoints for Document Conversion and Image OCR.
"""

import os
import sys
import tempfile
from pathlib import Path
from bottle import Bottle, request, response, static_file

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.converter import DocumentConverter
from core.ocr import extract_text_from_image

app = Bottle()
WEB_DIR = PROJECT_ROOT / "web"
converter = DocumentConverter()


@app.hook('after_request')
def enable_cors():
    """Enable CORS for local development if needed."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'


@app.route('/')
def serve_root():
    return static_file('index.html', root=str(WEB_DIR))


@app.route('/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root=str(WEB_DIR))


@app.post('/api/convert')
def api_convert():
    """Convert uploaded document (PDF, Word, Excel, PPTX, etc.) to Markdown."""
    upload = request.files.get('file')
    if not upload:
        response.status = 400
        return {"success": False, "error": "No file uploaded"}

    filename = upload.filename
    suffix = Path(filename).suffix

    # Extract optional AI Vision keys from request or environment
    openai_key = request.forms.get('openai_key') or request.headers.get('X-OpenAI-Key') or os.environ.get('OPENAI_API_KEY')
    gemini_key = request.forms.get('gemini_key') or request.headers.get('X-Gemini-Key') or os.environ.get('GEMINI_API_KEY')
    openai_model = request.forms.get('openai_model') or request.headers.get('X-OpenAI-Model') or "gpt-4o"

    converter.update_config(
        openai_api_key=openai_key,
        gemini_api_key=gemini_key,
        llm_model=openai_model,
    )

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        upload.save(tmp.name, overwrite=True)
        tmp_path = tmp.name

    try:
        res = converter.convert_file(tmp_path)
        return {
            "success": res.success,
            "filename": filename,
            "file_size": res.file_size_str,
            "markdown": res.markdown,
            "duration": res.duration_seconds,
            "error": res.error_message,
        }
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@app.post('/api/ocr')
def api_ocr():
    """Extract text from uploaded image using Windows Media OCR or AI Vision."""
    upload = request.files.get('image') or request.files.get('file')
    if not upload:
        response.status = 400
        return {"success": False, "error": "No image uploaded"}

    openai_key = request.forms.get('openai_key') or request.headers.get('X-OpenAI-Key') or os.environ.get('OPENAI_API_KEY')
    gemini_key = request.forms.get('gemini_key') or request.headers.get('X-Gemini-Key') or os.environ.get('GEMINI_API_KEY')
    openai_model = request.forms.get('openai_model') or request.headers.get('X-OpenAI-Model') or "gpt-4o"

    suffix = Path(upload.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        upload.save(tmp.name, overwrite=True)
        tmp_path = tmp.name

    try:
        extracted = extract_text_from_image(
            tmp_path,
            openai_api_key=openai_key,
            gemini_api_key=gemini_key,
            openai_model=openai_model,
        )
        return {
            "success": True,
            "filename": upload.filename,
            "text": extracted,
        }
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@app.post('/api/convert-ansi')
def api_convert_ansi():
    """Convert Bijoy/ANSI (SutonnyMJ) Bengali text to Unicode (preserving English words & code)."""
    data = request.json or {}
    raw_text = data.get('text', '')
    if not raw_text:
        raw_text = request.forms.get('text', '')

    from core.bengali import auto_convert_markdown
    converted = auto_convert_markdown(raw_text)
    return {
        "success": True,
        "converted": converted,
    }


@app.post('/api/convert-unicode-to-ansi')
def api_convert_unicode_to_ansi():
    """Convert Unicode Bengali text to legacy Bijoy/ANSI (preserving English words & code)."""
    data = request.json or {}
    raw_text = data.get('text', '')
    if not raw_text:
        raw_text = request.forms.get('text', '')

    from core.bengali import auto_convert_unicode_to_bijoy_markdown
    converted = auto_convert_unicode_to_bijoy_markdown(raw_text)
    return {
        "success": True,
        "converted": converted,
    }


def run_server(host="127.0.0.1", port=8080):
    app.run(host=host, port=port, quiet=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting MarkItDown Studio backend on http://127.0.0.1:{port}")
    run_server(port=port)
