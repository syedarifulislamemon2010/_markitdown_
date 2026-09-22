# -*- coding: utf-8 -*-
"""
Local Lightweight Backend Server for MarkItDown Studio.
Serves the web application and exposes endpoints for Document Conversion and Image OCR.
"""

import io
import os
import sys
import tempfile
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import quote
from bottle import Bottle, request, response, static_file, HTTPResponse

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configuration persistence (stores non-sensitive UI preferences only; credentials never stored in repo)
CONFIG_FILE = PROJECT_ROOT / ".studio_config.json"
DEFAULT_CONFIG = {
    "provider": os.environ.get("STUDIO_AI_PROVIDER", "hcnsec"),
    "openai_base_url": os.environ.get("OPENAI_BASE_URL", "https://api.hcnsec.cn/v1"),
    "openai_model": os.environ.get("OPENAI_MODEL", "auto"),
}


def get_studio_config():
    """Load non-sensitive configuration with default fallbacks."""
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Ensure secret keys are never loaded from repo config
                for secret in ("openai_key", "gemini_key", "api_key"):
                    saved.pop(secret, None)
                cfg.update(saved)
        except Exception:
            pass
    return cfg


def save_studio_config(data: dict):
    """Save non-sensitive studio configuration to disk (never stores API keys in repo root)."""
    cfg = get_studio_config()
    # Strip any secret keys to ensure credentials are never written to repository root
    sanitized = {k: v for k, v in data.items() if k not in ("openai_key", "gemini_key", "api_key")}
    cfg.update(sanitized)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving studio config: {e}")
    return cfg


_converter_instance = None
_batch_progress = {}

def get_converter():
    global _converter_instance
    if _converter_instance is None:
        from core.converter import DocumentConverter
        cfg = get_studio_config()
        _converter_instance = DocumentConverter(
            openai_api_key=cfg.get("openai_key") or None,
            openai_base_url=cfg.get("openai_base_url") or None,
            gemini_api_key=cfg.get("gemini_key") or None,
            llm_model=cfg.get("openai_model") or "auto",
        )
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


@app.get('/api/settings')
def api_get_settings():
    """Retrieve persisted AI and Studio settings."""
    cfg = get_studio_config()
    return {"success": True, "config": cfg}


@app.post('/api/settings')
def api_save_settings():
    """Save AI and Studio settings persistently."""
    data = request.json or {}
    if not data:
        data = {k: request.forms.get(k) for k in ('provider', 'openai_key', 'openai_base_url', 'openai_model', 'gemini_key') if request.forms.get(k) is not None}
    saved = save_studio_config(data)
    # Also update active converter instance
    conv = get_converter()
    conv.update_config(
        openai_api_key=data.get("openai_key") or os.environ.get("OPENAI_API_KEY"),
        openai_base_url=saved.get("openai_base_url") or None,
        gemini_api_key=data.get("gemini_key") or os.environ.get("GEMINI_API_KEY"),
        llm_model=saved.get("openai_model", "auto"),
    )
    return {"success": True, "config": saved, "message": "Settings saved successfully."}


@app.post('/api/test-ai-connection')
def api_test_ai_connection():
    """Test connectivity to any OpenAI-compatible relay or Gemini API with latency measurement."""
    data = request.json or {}
    cfg = get_studio_config()

    provider = data.get('provider') or request.forms.get('provider') or cfg.get('provider', 'hcnsec')
    api_key = data.get('api_key') or request.forms.get('api_key') or (cfg.get('openai_key') if provider != 'gemini' else cfg.get('gemini_key'))
    base_url = (data.get('base_url') or request.forms.get('base_url') or cfg.get('openai_base_url') or 'https://api.openai.com/v1').strip()
    model = (data.get('model') or request.forms.get('model') or cfg.get('openai_model') or 'auto').strip()

    if not api_key:
        return {"success": False, "error": "API Key is required to test connection."}

    start_time = time.perf_counter()

    if provider == 'gemini':
        # Probe Gemini models endpoint via x-goog-api-key header (never in URL)
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        headers = {
            "x-goog-api-key": api_key,
            "User-Agent": "MarkItDownStudio/3.2",
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:  # nosec B310
                raw = json.loads(resp.read().decode('utf-8'))
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                models = [m['name'].replace('models/', '') for m in raw.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                return {
                    "success": True,
                    "latency_ms": latency_ms,
                    "models": models[:30],
                    "message": f"Connected to Google Gemini ({latency_ms}ms)! {len(models)} models available."
                }
        except Exception as e:
            return {"success": False, "error": f"Gemini connection failed: {str(e)}"}

    # OpenAI-compatible / Custom Relay (HCNSEC, DeepSeek, OpenRouter, Ollama, etc.)
    models_url = f"{base_url.rstrip('/')}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "MarkItDownStudio/3.2"
    }

    try:
        req = urllib.request.Request(models_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
            raw = json.loads(resp.read().decode('utf-8'))
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            models_data = raw.get('data', [])
            model_ids = [m['id'] for m in models_data if isinstance(m, dict) and 'id' in m]
            if not model_ids and isinstance(raw, list):
                model_ids = [m.get('id') or m.get('name') for m in raw if isinstance(m, dict)]

            return {
                "success": True,
                "latency_ms": latency_ms,
                "models": model_ids if model_ids else [model],
                "message": f"Connected ({latency_ms}ms)! {len(model_ids)} models detected."
            }
    except Exception:
        # If /models endpoint is restricted or not implemented by minimal relay, fallback to minimal chat completion probe
        chat_url = f"{base_url.rstrip('/')}/chat/completions"
        probe_payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 2
        }).encode('utf-8')
        try:
            req_chat = urllib.request.Request(
                chat_url,
                data=probe_payload,
                headers={**headers, "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req_chat, timeout=12) as resp:  # nosec B310
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                return {
                    "success": True,
                    "latency_ms": latency_ms,
                    "models": [model],
                    "message": f"Connected ({latency_ms}ms)! Ready to process with model '{model}'."
                }
        except Exception as probe_err:
            err_msg = str(probe_err)
            if hasattr(probe_err, 'read'):
                try:
                    err_body = json.loads(probe_err.read().decode('utf-8'))
                    err_msg = err_body.get('error', {}).get('message', err_msg)
                except Exception:
                    pass
            return {
                "success": False,
                "error": f"Connection failed: {err_msg}"
            }


@app.post('/api/ai-action')
def api_ai_action():
    """Perform AI actions (Polish, Summarize, Translate BN/EN, Markdown Table, Explain) using connected LLM."""
    data = {}
    try:
        data = request.json or {}
    except Exception:
        pass
    if not data:
        try:
            raw = request.body.read().decode('utf-8')
            if raw:
                data = json.loads(raw)
        except Exception:
            pass

    action = data.get('action') or request.forms.get('action') or 'polish'
    text = data.get('text') or request.forms.get('text') or ''
    custom_prompt = data.get('custom_prompt') or request.forms.get('custom_prompt') or ''

    if not text.strip():
        response.status = 400
        return {"success": False, "error": "No text provided for AI processing."}

    cfg = get_studio_config()
    api_key = data.get('api_key') or request.forms.get('api_key') or cfg.get('openai_key')
    base_url = (data.get('base_url') or request.forms.get('base_url') or cfg.get('openai_base_url') or 'https://api.openai.com/v1').strip()
    model = (data.get('model') or request.forms.get('model') or cfg.get('openai_model') or 'auto').strip()

    if not api_key:
        response.status = 400
        return {"success": False, "error": "No API Key configured. Please configure your API key in Studio Settings."}

    system_prompts = {
        "polish": (
            "You are an expert bilingual proofreader and editor for Bengali and English text. "
            "Improve and polish the provided Markdown text for clarity, grammar, and natural flow. "
            "Preserve all Markdown formatting, links, tables, code fences, and math formulas exactly as they are. "
            "Output ONLY the improved Markdown text without conversational remarks."
        ),
        "summarize": (
            "You are an executive document analyst. Create a clear, high-impact summary of the provided text. "
            "Include key takeaways as structured Markdown bullet points and bold highlights. "
            "Match the language of the source document (Bengali or English). Output strictly as Markdown."
        ),
        "translate_bn_en": (
            "You are a master bilingual translator specializing in English and Bengali (বাংলা). "
            "If the source text is predominantly Bengali, translate it into natural, idiomatic English. "
            "If it is English, translate it into standard, modern Bengali Unicode (বাংলিশ বা অবান্তর অক্ষরহীন)। "
            "Preserve all Markdown layout, code blocks, tables, and math syntax verbatim. Output ONLY the translated Markdown."
        ),
        "table": (
            "Convert the provided unstructured data, list, or prose into a clean, well-aligned "
            "GitHub-Flavored Markdown table with appropriate column headers. Output ONLY the table."
        ),
        "explain": (
            "Explain the technical concepts, complex formulas, or logic in the provided text in simple, "
            "easy-to-understand terms with bullet points in clean Markdown."
        )
    }

    instruction = system_prompts.get(action, custom_prompt or system_prompts["polish"])

    chat_url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3
    }).encode('utf-8')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "MarkItDownStudio/3.2"
    }

    try:
        req = urllib.request.Request(chat_url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=45) as resp:  # nosec B310
            res_data = json.loads(resp.read().decode('utf-8'))
            choices = res_data.get('choices', [])
            if not choices:
                return {"success": False, "error": "No response generated by AI model."}
            result_text = choices[0].get('message', {}).get('content', '').strip()
            return {
                "success": True,
                "action": action,
                "result": result_text,
                "model": model
            }
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'read'):
            try:
                err_body = json.loads(e.read().decode('utf-8'))
                err_msg = err_body.get('error', {}).get('message', err_msg)
            except Exception:
                pass
        return {"success": False, "error": f"AI action failed: {err_msg}"}


@app.post('/api/convert')
def api_convert():
    """Convert uploaded document (PDF, Word, Excel, PPTX, etc.) to Markdown."""
    upload = request.files.get('file')
    if not upload:
        response.status = 400
        return {"success": False, "error": "No file uploaded"}

    filename = upload.filename
    suffix = Path(filename).suffix

    # Extract optional AI Vision keys from request or environment or config
    cfg = get_studio_config()
    openai_key = request.forms.get('openai_key') or request.headers.get('X-OpenAI-Key') or os.environ.get('OPENAI_API_KEY') or cfg.get('openai_key')
    openai_base_url = request.forms.get('openai_base_url') or request.headers.get('X-OpenAI-Base-Url') or os.environ.get('OPENAI_BASE_URL') or cfg.get('openai_base_url')
    gemini_key = request.forms.get('gemini_key') or request.headers.get('X-Gemini-Key') or os.environ.get('GEMINI_API_KEY') or cfg.get('gemini_key')
    openai_model = request.forms.get('openai_model') or request.headers.get('X-OpenAI-Model') or cfg.get('openai_model') or "auto"

    conv = get_converter()
    conv.update_config(
        openai_api_key=openai_key,
        openai_base_url=openai_base_url,
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

    cfg = get_studio_config()
    openai_key = request.forms.get('openai_key') or request.headers.get('X-OpenAI-Key') or os.environ.get('OPENAI_API_KEY') or cfg.get('openai_key')
    openai_base_url = request.forms.get('openai_base_url') or request.headers.get('X-OpenAI-Base-Url') or os.environ.get('OPENAI_BASE_URL') or cfg.get('openai_base_url')
    gemini_key = request.forms.get('gemini_key') or request.headers.get('X-Gemini-Key') or os.environ.get('GEMINI_API_KEY') or cfg.get('gemini_key')
    openai_model = request.forms.get('openai_model') or request.headers.get('X-OpenAI-Model') or cfg.get('openai_model') or "auto"

    suffix = Path(upload.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        upload.save(tmp.name, overwrite=True)
        tmp_path = tmp.name

    try:
        from core.ocr import extract_text_from_image
        extracted = extract_text_from_image(
            tmp_path,
            openai_api_key=openai_key,
            openai_base_url=openai_base_url,
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

    from core.bengali import auto_convert_markdown, detect_encoding
    label, confidence = detect_encoding(raw_text)
    converted = auto_convert_markdown(raw_text)

    # Paragraph-level breakdown for granular inspection and per-block undo
    paragraphs = raw_text.split('\n\n')
    breakdown = []
    for p in paragraphs:
        if p.strip():
            p_label, p_conf = detect_encoding(p)
            p_conv = auto_convert_markdown(p)
            breakdown.append({
                "original": p,
                "converted": p_conv,
                "label": p_label,
                "confidence": p_conf,
            })

    return {
        "success": True,
        "converted": converted,
        "label": label,
        "confidence": confidence,
        "breakdown": breakdown,
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

    cfg = get_studio_config()
    openai_key = request.forms.get('openai_key') or request.headers.get('X-OpenAI-Key') or os.environ.get('OPENAI_API_KEY') or cfg.get('openai_key')
    openai_base_url = request.forms.get('openai_base_url') or request.headers.get('X-OpenAI-Base-Url') or os.environ.get('OPENAI_BASE_URL') or cfg.get('openai_base_url')
    gemini_key = request.forms.get('gemini_key') or request.headers.get('X-Gemini-Key') or os.environ.get('GEMINI_API_KEY') or cfg.get('gemini_key')
    openai_model = request.forms.get('openai_model') or request.headers.get('X-OpenAI-Model') or cfg.get('openai_model') or "auto"

    conv = get_converter()
    conv.update_config(
        openai_api_key=openai_key,
        openai_base_url=openai_base_url,
        gemini_api_key=gemini_key,
        llm_model=openai_model,
    )
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
