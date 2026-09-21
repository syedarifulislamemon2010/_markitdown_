# -*- coding: utf-8 -*-
"""
Local Lightweight Backend Server for MarkItDown Studio.
Serves the web application and exposes endpoints for Document Conversion and Image OCR.
"""

import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote
from bottle import Bottle, request, response, static_file, HTTPResponse

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_converter_instance = None

def get_converter():
    global _converter_instance
    if _converter_instance is None:
        from core.converter import DocumentConverter
        _converter_instance = DocumentConverter()
    return _converter_instance

app = Bottle()
WEB_DIR = PROJECT_ROOT / "web"


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
    res = static_file(filepath, root=str(WEB_DIR))
    # Cache static assets like vendor JS, fonts, and CSS for 1 day
    if any(filepath.startswith(prefix) for prefix in ('vendor/', 'css/', 'js/')):
        res.set_header('Cache-Control', 'public, max-age=86400')
    return res


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

    conv = get_converter()
    conv.update_config(
        openai_api_key=openai_key,
        gemini_api_key=gemini_key,
        llm_model=openai_model,
    )

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        upload.save(tmp.name, overwrite=True)
        tmp_path = tmp.name

    try:
        res = conv.convert_file(tmp_path)
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
        from core.ocr import extract_text_from_image
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


@app.post('/api/export-docx')
def api_export_docx():
    """Convert Markdown to Word (.docx) file and trigger download."""
    data = request.json or {}
    markdown_text = data.get('markdown', '')
    title = data.get('title', 'Document')
    if not markdown_text:
        markdown_text = request.forms.get('markdown', '')
    if not title:
        title = request.forms.get('title', 'Document')

    from core.docx_exporter import markdown_to_docx_bytes
    docx_bytes = markdown_to_docx_bytes(markdown_text, title)

    ascii_title = "".join(c for c in title if c.isascii() and (c.isalnum() or c in (' ', '-', '_'))).strip() or "Document"
    encoded_title = quote(f"{title}.docx")
    headers = {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'Content-Disposition': f'attachment; filename="{ascii_title}.docx"; filename*=UTF-8\'\'{encoded_title}',
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'Content-Length': str(len(docx_bytes)),
    }
    return HTTPResponse(body=docx_bytes, status=200, headers=headers)


@app.post('/api/download-file')
def api_download_file():
    """Universal file download endpoint with Content-Disposition for desktop and web."""
    data = request.json or {}
    content = data.get('content', '')
    filename = data.get('filename', 'document.txt')
    mime_type = data.get('mime_type', 'text/plain; charset=utf-8')

    ascii_filename = "".join(c for c in filename if c.isascii() and (c.isalnum() or c in ('.', ' ', '-', '_'))).strip() or "document.txt"
    encoded_filename = quote(filename)
    encoded = content.encode('utf-8')
    headers = {
        'Content-Type': mime_type,
        'Content-Disposition': f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'Content-Length': str(len(encoded)),
    }
    return HTTPResponse(body=encoded, status=200, headers=headers)


from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server
from bottle import ServerAdapter


class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True

    def address_string(self):
        # Return client IP directly to bypass slow reverse-DNS lookups on Windows
        return self.client_address[0]


class ThreadedWSGIAdapter(ServerAdapter):
    """Multi-threaded WSGI adapter preventing synchronous server stalls."""

    def run(self, handler):
        class QuietHandler(WSGIRequestHandler):
            def log_message(self, format, *args):
                pass

            def address_string(self):
                return self.client_address[0]

        server = make_server(
            self.host,
            self.port,
            handler,
            server_class=ThreadedWSGIServer,
            handler_class=QuietHandler,
        )
        server.serve_forever()


def run_server(host="127.0.0.1", port=8080):
    app.run(host=host, port=port, server=ThreadedWSGIAdapter, quiet=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting MarkItDown Studio backend on http://127.0.0.1:{port}")
    run_server(port=port)
