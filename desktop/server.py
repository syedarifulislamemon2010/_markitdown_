# -*- coding: utf-8 -*-
"""
Local Lightweight Backend Server for MarkItDown Studio.
Serves the web application and exposes endpoints for Document Conversion and Image OCR.
"""

import io
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
_batch_progress = {}

def get_converter():
    global _converter_instance
    if _converter_instance is None:
        from core.converter import DocumentConverter
        _converter_instance = DocumentConverter()
    return _converter_instance

import bottle

MEMFILE_MAX = int(os.environ.get("STUDIO_MEMFILE_MAX", 100 * 1024 * 1024))
bottle.BaseRequest.MEMFILE_MAX = MEMFILE_MAX

app = Bottle()
WEB_DIR = PROJECT_ROOT / "web"


@app.hook('before_request')
def security_checks():
    """Enforce payload size limits and session token validation on API endpoints."""
    # 1. Enforce payload size limit (MEMFILE_MAX)
    try:
        cl = int(request.headers.get('Content-Length') or 0)
        if cl > bottle.BaseRequest.MEMFILE_MAX:
            raise HTTPResponse(
                body='{"success": false, "error": "Payload Too Large: exceeded 100MB limit"}',
                status=413,
                headers={'Content-Type': 'application/json'}
            )
    except (ValueError, TypeError):
        pass

    # 2. Session token validation (if token is configured in environment)
    session_token = os.environ.get("STUDIO_SESSION_TOKEN")
    if session_token and request.method != 'OPTIONS':
        # All /api/* routes except /api/health require valid X-Session-Token
        if request.path.startswith('/api/') and request.path != '/api/health':
            client_token = request.headers.get('X-Session-Token')
            if not client_token or client_token != session_token:
                raise HTTPResponse(
                    body='{"success": false, "error": "Forbidden: invalid or missing session token"}',
                    status=403,
                    headers={'Content-Type': 'application/json'}
                )


@app.hook('after_request')
def apply_security_headers():
    """Apply strict security headers and restrict CORS to localhost only."""
    # 1. Strict Security Headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self';"
    )

    # 2. Localhost-only CORS: NEVER wildcard '*'
    origin = request.headers.get('Origin')
    if origin:
        allowed_origins = ('http://127.0.0.1', 'http://localhost', 'vscode-webview://', 'null')
        if any(origin.startswith(prefix) for prefix in allowed_origins):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = (
                'Origin, Accept, Content-Type, X-Requested-With, X-Session-Token, X-Batch-Id'
            )
            response.headers['Access-Control-Allow-Credentials'] = 'true'


@app.route('/')
def serve_root():
    index_file = WEB_DIR / 'index.html'
    if not index_file.exists():
        return static_file('index.html', root=str(WEB_DIR))

    html = index_file.read_text(encoding='utf-8')
    session_token = os.environ.get("STUDIO_SESSION_TOKEN", "")
    if session_token:
        injection = f'<script>window.__STUDIO_TOKEN__ = "{session_token}";</script>\n</head>'
        html = html.replace('</head>', injection, 1)

    response.content_type = 'text/html; charset=utf-8'
    return html


@app.route('/api/health')
def api_health():
    """Ultra-fast health check endpoint for status bar and connectivity monitoring."""
    response.content_type = 'application/json'
    return '{"status": "ok", "version": "3.2.0"}'


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




def generate_pdf_from_markdown(markdown_text, title="Document"):
    """Generate high-fidelity PDF from markdown using Chrome/Edge headless."""
    import subprocess
    import html as html_module

    chrome_candidates = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    chrome_path = None
    for c in chrome_candidates:
        if os.path.exists(c):
            chrome_path = c
            break

    if not chrome_path:
        return None

    # Minimal clean Markdown to HTML parser for PDF
    escaped_body = html_module.escape(markdown_text).replace('\n', '<br>')
    html_content = f"""<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <title>{html_module.escape(title)}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap');
    @page {{
      size: A4;
      margin: 20mm 15mm 20mm 15mm;
    }}
    body {{
      font-family: 'Hind Siliguri', 'Segoe UI', system-ui, sans-serif;
      font-size: 11pt;
      line-height: 1.65;
      color: #1a1a1a;
    }}
    h1, h2, h3, h4 {{
      color: #0078d4;
      margin-top: 1.2em;
      margin-bottom: 0.5em;
      font-weight: 600;
    }}
    h1 {{ font-size: 20pt; border-bottom: 2px solid #0078d4; padding-bottom: 6px; }}
    pre, code {{ font-family: Consolas, monospace; background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1em 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f2f2f2; }}
    img {{ max-width: 100%; height: auto; }}
  </style>
</head>
<body>
  <h1>{html_module.escape(title)}</h1>
  <div class="content">{escaped_body}</div>
</body>
</html>"""

    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f_html:
        f_html.write(html_content)
        html_path = f_html.name

    pdf_path = html_path.replace('.html', '.pdf')

    cmd = [
        chrome_path,
        '--headless=new',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_path}',
        html_path
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, timeout=15)
        if res.returncode == 0 and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f_pdf:
                return f_pdf.read()
    except Exception as e:
        print("PDF gen exception:", e)
    finally:
        if os.path.exists(html_path):
            try: os.remove(html_path)
            except Exception: pass
        if os.path.exists(pdf_path):
            try: os.remove(pdf_path)
            except Exception: pass
    return None


@app.post('/api/export-pdf')
def api_export_pdf():
    """Convert Markdown to Direct Downloadable PDF using headless Chrome/Edge."""
    data = request.json or {}
    markdown_text = data.get('markdown', '')
    title = data.get('title', 'Document')
    if not markdown_text:
        markdown_text = request.forms.get('markdown', '')
    if not title:
        title = request.forms.get('title', 'Document')

    pdf_bytes = generate_pdf_from_markdown(markdown_text, title)
    if not pdf_bytes:
        response.status = 500
        return {"success": False, "error": "Direct PDF generation failed. Use browser print dialog."}

    ascii_title = "".join(c for c in title if c.isascii() and (c.isalnum() or c in (' ', '-', '_'))).strip() or "Document"
    encoded_title = quote(f"{title}.pdf")
    headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename="{ascii_title}.pdf"; filename*=UTF-8\'\'{encoded_title}',
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'Content-Length': str(len(pdf_bytes)),
    }
    return HTTPResponse(body=pdf_bytes, status=200, headers=headers)


@app.route('/api/batch-progress/<batch_id>')
def api_batch_progress(batch_id):
    """Return conversion progress for a running batch."""
    prog = _batch_progress.get(batch_id, {"current": 0, "total": 0, "done": False})
    return prog


@app.post('/api/batch-convert')
def api_batch_convert():
    """Convert multiple files to Markdown and download as a single ZIP archive."""
    import zipfile
    files = request.files.getall('files') or request.files.getall('file')
    if not files:
        response.status = 400
        return {"success": False, "error": "No files uploaded"}

    batch_id = request.headers.get('X-Batch-Id') or request.forms.get('batch_id')
    if batch_id:
        if len(_batch_progress) > 100:
            for old_k in list(_batch_progress.keys())[:-50]:
                _batch_progress.pop(old_k, None)
        _batch_progress[batch_id] = {"current": 0, "total": len(files), "done": False}

    conv = get_converter()
    zip_buffer = io.BytesIO()
    converted_count = 0
    errors = []

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, upload in enumerate(files, 1):
            if batch_id and batch_id in _batch_progress:
                _batch_progress[batch_id]["current"] = i

            filename = upload.filename
            suffix = Path(filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                upload.save(tmp.name, overwrite=True)
                tmp_path = tmp.name

            try:
                res = conv.convert_file(tmp_path)
                if res.success and res.markdown:
                    md_name = f"{Path(filename).stem}.md"
                    zip_file.writestr(md_name, res.markdown.encode('utf-8'))
                    converted_count += 1
                else:
                    err_msg = res.error_message if hasattr(res, 'error_message') and res.error_message else "Conversion failed"
                    errors.append(f"{filename}: {err_msg}")
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

        if errors and converted_count > 0:
            zip_file.writestr("_errors.txt", "\n".join(errors).encode('utf-8'))

    if batch_id and batch_id in _batch_progress:
        _batch_progress[batch_id]["done"] = True

    if converted_count == 0:
        response.status = 400
        error_detail = "\n".join(errors) if errors else "No files could be converted successfully"
        return {"success": False, "error": error_detail}

    zip_bytes = zip_buffer.getvalue()
    headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="markitdown_batch_converted.zip"',
        'Access-Control-Expose-Headers': 'Content-Disposition',
        'Content-Length': str(len(zip_bytes)),
    }
    return HTTPResponse(body=zip_bytes, status=200, headers=headers)


@app.route('/<filepath:path>')
def serve_static(filepath):
    res = static_file(filepath, root=str(WEB_DIR))
    # Cache heavy vendor libraries (Mermaid, KaTeX, TTF fonts) for 1 day
    if filepath.startswith('vendor/') or filepath.endswith('.ttf') or filepath.endswith('.woff2'):
        res.set_header('Cache-Control', 'public, max-age=86400')
    else:
        # Application code (app.js, style.css) must always stay fresh without stale cache
        res.set_header('Cache-Control', 'no-cache, must-revalidate')
    return res


def run_server(host="127.0.0.1", port=8080, session_token=None):
    if session_token:
        os.environ["STUDIO_SESSION_TOKEN"] = session_token
    app.run(host=host, port=port, server=ThreadedWSGIAdapter, quiet=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting MarkItDown Studio backend on http://127.0.0.1:{port}")
    run_server(port=port)
