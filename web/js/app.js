/**
 * MarkItDown Studio - Application Engine
 * Live Synced Preview, KaTeX Math, Mermaid Diagrams, Bengali Typography, Document Converter & OCR
 */

(function () {
  'use strict';

  // DOM Elements
  const editor = document.getElementById('editor');
  const preview = document.getElementById('preview');
  const previewContent = document.getElementById('previewContent');
  const docTitleInput = document.getElementById('docTitle');
  const wordCountEl = document.getElementById('wordCount');
  const charCountEl = document.getElementById('charCount');
  const lineCountEl = document.getElementById('lineCount');
  const readTimeEl = document.getElementById('readTime');
  const saveStatusEl = document.getElementById('saveStatus');

  // Modals
  const importModal = document.getElementById('importModal');
  const ocrModal = document.getElementById('ocrModal');
  const settingsModal = document.getElementById('settingsModal');
  const shortcutsModal = document.getElementById('shortcutsModal');
  const exportDropdown = document.getElementById('exportDropdown');

  // State & History Stack (Undo / Redo)
  let isScrolling = false;
  let renderTimeout = null;
  let historyDebounceTimeout = null;
  const undoStack = [];
  const redoStack = [];
  const MAX_HISTORY = 60;

  function pushHistoryState(val) {
    if (val === undefined) val = editor.value;
    if (undoStack.length > 0 && undoStack[undoStack.length - 1] === val) {
      return;
    }
    undoStack.push(val);
    if (undoStack.length > MAX_HISTORY) undoStack.shift();
    redoStack.length = 0;
    updateUndoRedoUI();
  }

  function undo() {
    if (undoStack.length === 0) return;
    const current = editor.value;
    redoStack.push(current);
    const prev = undoStack.pop();
    editor.value = prev;
    renderMarkdown();
    updateUndoRedoUI();
    saveStatusEl.textContent = '↩ Undo performed';
    setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 1500);
  }

  function redo() {
    if (redoStack.length === 0) return;
    const current = editor.value;
    undoStack.push(current);
    const next = redoStack.pop();
    editor.value = next;
    renderMarkdown();
    updateUndoRedoUI();
    saveStatusEl.textContent = '↪ Redo performed';
    setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 1500);
  }

  function updateUndoRedoUI() {
    const hasUndo = undoStack.length > 0;
    const hasRedo = redoStack.length > 0;
    ['paneUndoBtn', 'toolUndo', 'menuUndo'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.disabled = !hasUndo;
    });
    ['paneRedoBtn', 'toolRedo', 'menuRedo'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.disabled = !hasRedo;
    });
  }

  // Initialize Mermaid
  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      theme: document.body.getAttribute('data-theme') === 'light' ? 'default' : 'dark',
      securityLevel: 'loose',
    });
  }

  // ==================== Startup & State Restoration ====================
  function init() {
    const savedDraft = localStorage.getItem('markitdown_studio_draft');
    const savedTitle = localStorage.getItem('markitdown_studio_title');
    const savedTheme = localStorage.getItem('markitdown_studio_theme') || 'dark';

    setTheme(savedTheme);

    if (savedTitle) {
      docTitleInput.value = savedTitle;
    }

    if (savedDraft !== null) {
      editor.value = savedDraft;
    } else {
      // Default initial welcome template with Bengali, Math, Table and Mermaid demo
      editor.value = `# MarkItDown Studio ✨

স্বাগতম! এটি একটি সম্পূর্ণ আধুনিক **মার্কডাউন এডিটর ও ইউনিভার্সাল কনভার্টার**। 

---

### ১. বাংলা যুক্তবর্ণ ও টাইপোগ্রাফি (Flawless Bengali)
এখানে বাংলা লেখা, যুক্তবর্ণ এবং কারচিহ্ন সম্পূর্ণ নিখুঁতভাবে রেন্ডার হয়:
- **উদাহরণ:** কম্পিউটার, প্রজেক্ট, স্বাগতম, আন্তর্জাতিক, দৃষ্টিভঙ্গি, প্রযুক্তি।
- কালপুরুষ (Kalpurush) ও হিন্দ শিলিগুড়ি ফন্ট সাপোর্ট থাকায় কোনো লেখা ভাঙবে না।

---

### ২. গাণিতিক সমীকরণ (LaTeX / KaTeX Math)
ইনলাইন গণিত সমীকরণ: $E = mc^2$ এবং আইনস্টাইনের আপেক্ষিকতা।

ব্লক সমীকরণ:
$$\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$

---

### ৩. ফ্লোচার্ট ও ডায়াগ্রাম (Mermaid.js)

\`\`\`mermaid
graph TD
    A[ডকুমেন্ট আপলোড / ড্রপ] --> B{MarkItDown ইঞ্জিন}
    B -->|PDF / Word / Excel| C[মার্কডাউন টেক্সট]
    B -->|ইমেজ / স্ক্যান| D[OCR বাংলা/ইংরেজি]
    C --> E[লাইভ সাইড-বাই-সাইড এডিটর]
    D --> E
    E --> F[এক্সপোর্ট: MD / HTML / PDF]
\`\`\`

---

### ৪. ডেটা টেবিল ও চেকলিস্ট (Tables & Task List)

| ফিচার | স্ট্যাটাস | সুবিধা |
| :--- | :---: | :--- |
| **লাইভ প্রিভিউ** | ✅ সচল | টাইপ করার সাথে সাথে রেন্ডার |
| **স্ক্রোল সিঙ্ক** | ✅ সচল | উভয় পাশ একসাথে স্ক্রোল হবে |
| **ছবির লেখা (OCR)** | ✅ সচল | উইন্ডোজ অফলাইন ও এআই ভিশন |
| **পিডিএফ এক্সপোর্ট** | ✅ সচল | এক ক্লিকে প্রিন্ট ও ডাউনলোড |

- [x] ড্র্যাগ & ড্রপ ফাইল কনভার্টার
- [x] বাংলা ফন্ট টেক্সট শেপিং
- [x] অফলাইন লোকাল স্টোরেজ ড্রাফট সেভ
- [ ] ক্লাউড গিটহাব পুশ
`;
    }

    renderMarkdown();
    updateUndoRedoUI();
    setupEventListeners();
  }

  // ==================== Live Rendering Pipeline ====================
  function renderMarkdown() {
    const rawText = editor.value;

    // Automatic Unicode Conversion for Preview:
    // Guarantee that preview ALWAYS renders in pure Unicode Bengali even if editor contains legacy ANSI
    let textToRender = rawText;
    if (window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown && window.BijoyToUnicode.isLikelyBijoy(rawText)) {
      textToRender = window.BijoyToUnicode.convertMarkdown(rawText);
    }

    // 1. Pre-process LaTeX Math to protect from marked parser
    const mathBlocks = [];
    const inlineMath = [];

    // Block math $$...$$
    let processed = textToRender.replace(/\$\$([\s\S]+?)\$\$/g, (match, formula) => {
      mathBlocks.push(formula.trim());
      return `@@MATH_BLOCK_${mathBlocks.length - 1}@@`;
    });

    // Inline math $...$
    processed = processed.replace(/\$([^\$\n]+?)\$/g, (match, formula) => {
      inlineMath.push(formula.trim());
      return `@@MATH_INLINE_${inlineMath.length - 1}@@`;
    });

    // 2. Parse Markdown with marked.js
    let html = '';
    if (window.marked) {
      html = marked.parse(processed, {
        gfm: true,
        breaks: true,
      });
    } else {
      html = `<pre>${escapeHtml(textToRender)}</pre>`;
    }

    // 3. Restore and Render Math with KaTeX
    html = html.replace(/@@MATH_BLOCK_(\d+)@@/g, (match, id) => {
      const formula = mathBlocks[parseInt(id)];
      try {
        return `<div class="katex-block">${katex.renderToString(formula, { displayMode: true, throwOnError: false })}</div>`;
      } catch (e) {
        return `<div class="katex-error">$$${escapeHtml(formula)}$$</div>`;
      }
    });

    html = html.replace(/@@MATH_INLINE_(\d+)@@/g, (match, id) => {
      const formula = inlineMath[parseInt(id)];
      try {
        return katex.renderToString(formula, { displayMode: false, throwOnError: false });
      } catch (e) {
        return `$${escapeHtml(formula)}$`;
      }
    });

    // 4. Inject Rendered HTML
    previewContent.innerHTML = html;

    // 5. Render Mermaid Diagrams
    renderMermaidDiagrams();

    // 6. Update Document Statistics
    updateStats(rawText);

    // 7. Auto-save to LocalStorage
    saveDraft();
  }

  function renderMermaidDiagrams() {
    if (!window.mermaid) return;

    const codeBlocks = previewContent.querySelectorAll('pre code.language-mermaid');
    codeBlocks.forEach((codeEl, idx) => {
      const rawDiagram = codeEl.textContent;
      const preEl = codeEl.parentElement;

      const container = document.createElement('div');
      container.className = 'mermaid-diagram';
      const id = `mermaid-svg-${Date.now()}-${idx}`;
      container.id = id;

      try {
        mermaid.render(id + '-render', rawDiagram).then(({ svg }) => {
          container.innerHTML = svg;
          if (preEl.parentNode) {
            preEl.parentNode.replaceChild(container, preEl);
          }
        }).catch(err => {
          console.warn("Mermaid syntax error:", err);
        });
      } catch (e) {
        console.warn("Mermaid error:", e);
      }
    });
  }

  function updateStats(text) {
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const lines = text ? text.split('\n').length : 0;
    const readMinutes = Math.max(1, Math.ceil(words / 200));

    wordCountEl.textContent = `${words.toLocaleString()} words`;
    charCountEl.textContent = `${chars.toLocaleString()} chars`;
    lineCountEl.textContent = `${lines.toLocaleString()} lines`;
    readTimeEl.textContent = `${readMinutes} min read`;
  }

  function saveDraft() {
    localStorage.setItem('markitdown_studio_draft', editor.value);
    localStorage.setItem('markitdown_studio_title', docTitleInput.value);
    saveStatusEl.textContent = 'Saved locally';
  }

  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
  }

  // ==================== Synchronized Scrolling ====================
  function setupScrollSync() {
    editor.addEventListener('scroll', () => {
      if (isScrolling) return;
      isScrolling = true;
      const pct = editor.scrollTop / (editor.scrollHeight - editor.clientHeight || 1);
      preview.scrollTop = pct * (preview.scrollHeight - preview.clientHeight);
      setTimeout(() => { isScrolling = false; }, 40);
    });

    preview.addEventListener('scroll', () => {
      if (isScrolling) return;
      isScrolling = true;
      const pct = preview.scrollTop / (preview.scrollHeight - preview.clientHeight || 1);
      editor.scrollTop = pct * (editor.scrollHeight - editor.clientHeight);
      setTimeout(() => { isScrolling = false; }, 40);
    });
  }

  // ==================== Toolbar Formatting Tools ====================
  function insertFormat(prefix, suffix = '', defaultText = 'text') {
    pushHistoryState(editor.value);
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const val = editor.value;
    const selected = val.substring(start, end) || defaultText;

    const replacement = prefix + selected + suffix;
    editor.value = val.substring(0, start) + replacement + val.substring(end);

    editor.focus();
    editor.setSelectionRange(start + prefix.length, start + prefix.length + selected.length);
    renderMarkdown();
  }

  function insertBlock(template) {
    pushHistoryState(editor.value);
    const start = editor.selectionStart;
    const val = editor.value;
    const before = val.substring(0, start);
    const after = val.substring(start);
    const newline = before.endsWith('\n') || before === '' ? '' : '\n\n';

    editor.value = before + newline + template + '\n\n' + after;
    editor.focus();
    renderMarkdown();
  }

  // ==================== Multi-Format Exporters ====================
  function exportMarkdown() {
    const filename = `${sanitizeFilename(docTitleInput.value)}.md`;
    downloadFile(editor.value, filename, 'text/markdown;charset=utf-8');
  }

  function exportHtml() {
    const filename = `${sanitizeFilename(docTitleInput.value)}.html`;
    const fullHtml = `<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <title>${escapeHtml(docTitleInput.value)}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap');
    body {
      font-family: 'Hind Siliguri', 'Kalpurush', 'Nirmala UI', sans-serif;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
      max-width: 860px;
      margin: 40px auto;
      padding: 0 20px;
      line-height: 1.7;
      color: #1e293b;
    }
    table { width: 100%; border-collapse: collapse; margin: 1.5em 0; }
    th, td { border: 1px solid #cbd5e1; padding: 8px 12px; }
    th { background: #f1f5f9; }
    pre { background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 8px; overflow-x: auto; }
    code { background: #f1f5f9; color: #d946ef; padding: 2px 6px; border-radius: 4px; }
    blockquote { border-left: 4px solid #3b82f6; padding-left: 14px; color: #64748b; margin: 1em 0; }
    img { max-width: 100%; border-radius: 8px; }
  </style>
</head>
<body>
  <div class="preview-content">
    ${previewContent.innerHTML}
  </div>
</body>
</html>`;
    downloadFile(fullHtml, filename, 'text/html;charset=utf-8');
  }

  function exportPdf() {
    // Uses native browser / webview print-to-pdf
    window.print();
  }

  function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function sanitizeFilename(name) {
    return (name || 'document').trim().replace(/[/\\?%*:|"<>]/g, '-');
  }

  // ==================== Document Conversion Bridge (MarkItDown) ====================
  async function convertUploadedFile(file) {
    saveStatusEl.textContent = '⏳ Converting with MarkItDown...';

    // If running in pywebview desktop window
    if (window.pywebview && window.pywebview.api && window.pywebview.api.convert_file_content) {
      try {
        const reader = new FileReader();
        reader.onload = async function (e) {
          const b64Data = e.target.result.split(',')[1];
          const res = await window.pywebview.api.convert_file_content(file.name, b64Data);
          handleConversionResult(file.name, res);
        };
        reader.readAsDataURL(file);
        return;
      } catch (err) {
        console.error("Pywebview conversion error:", err);
      }
    }

    // Standard HTTP / local backend fallback
    try {
      const formData = new FormData();
      formData.append('file', file);
      const openaiKey = localStorage.getItem('markitdown_openai_key') || '';
      const geminiKey = localStorage.getItem('markitdown_gemini_key') || '';
      const model = localStorage.getItem('markitdown_openai_model') || 'gpt-4o';
      if (openaiKey) formData.append('openai_key', openaiKey);
      if (geminiKey) formData.append('gemini_key', geminiKey);
      if (model) formData.append('openai_model', model);

      const resp = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });

      if (resp.ok) {
        const data = await resp.json();
        handleConversionResult(file.name, data.markdown);
      } else {
        alert('Conversion failed. Ensure local backend is running.');
      }
    } catch (e) {
      // Offline fallback: If text file or read as text
      if (file.name.match(/\.(txt|md|csv|json|html|htm|xml)$/i)) {
        const text = await file.text();
        handleConversionResult(file.name, text);
      } else {
        alert(`Converting ${file.name} requires MarkItDown backend.\nFile: ${file.name} (${(file.size/1024).toFixed(1)} KB)`);
      }
    } finally {
      saveStatusEl.textContent = 'Saved locally';
    }
  }

  function handleConversionResult(filename, markdown) {
    const title = filename.replace(/\.[^/.]+$/, '');
    docTitleInput.value = title;

    // Guarantee converted content is pure Unicode Bengali
    let finalMarkdown = markdown;
    if (window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown && window.BijoyToUnicode.isLikelyBijoy(finalMarkdown)) {
      finalMarkdown = window.BijoyToUnicode.convertMarkdown(finalMarkdown);
    }

    pushHistoryState(editor.value);

    // Append or replace editor content
    if (confirm(`Do you want to replace current content with converted '${filename}'?`)) {
      editor.value = finalMarkdown;
    } else {
      editor.value += `\n\n---\n# Converted from: ${filename}\n\n` + finalMarkdown;
    }

    renderMarkdown();
    saveDraft();
  }

  // ==================== OCR Processing ====================
  async function performImageOcr(file) {
    saveStatusEl.textContent = '🔍 Running OCR...';

    // Python Webview Native API (Desktop)
    if (window.pywebview && window.pywebview.api && window.pywebview.api.ocr_image_content) {
      try {
        const reader = new FileReader();
        reader.onload = async function (e) {
          const b64Data = e.target.result.split(',')[1];
          const text = await window.pywebview.api.ocr_image_content(file.name, b64Data);
          insertOcrText(file.name, text);
        };
        reader.readAsDataURL(file);
        return;
      } catch (err) {
        console.error("OCR API error:", err);
      }
    }

    // Web API Fallback
    try {
      const formData = new FormData();
      formData.append('image', file);
      const openaiKey = localStorage.getItem('markitdown_openai_key') || '';
      const geminiKey = localStorage.getItem('markitdown_gemini_key') || '';
      const model = localStorage.getItem('markitdown_openai_model') || 'gpt-4o';
      if (openaiKey) formData.append('openai_key', openaiKey);
      if (geminiKey) formData.append('gemini_key', geminiKey);
      if (model) formData.append('openai_model', model);

      const resp = await fetch('/api/ocr', { method: 'POST', body: formData });
      if (resp.ok) {
        const data = await resp.json();
        insertOcrText(file.name, data.text);
      }
    } catch (e) {
      alert("OCR requires Python backend (WinOCR / AI Vision).");
    } finally {
      saveStatusEl.textContent = 'Saved locally';
    }
  }

  function insertOcrText(filename, text) {
    const formatted = `\n\n### 📝 OCR Text (${filename})\n\n${text}\n\n`;
    insertBlock(formatted);
    closeAllModals();
  }

  // ==================== Bengali Conversion Actions ====================
  function convertAnsiToUnicodeAction() {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const rawVal = editor.value;
    const hasSelection = start !== end;
    const targetText = hasSelection ? rawVal.substring(start, end) : rawVal;

    if (!targetText.trim()) {
      alert("কোনো টেক্সট পাওয়া যায়নি। এডিটরে কিছু টেক্সট লিখুন বা পেস্ট করুন।");
      return;
    }

    pushHistoryState(rawVal);
    saveStatusEl.textContent = '🔄 Converting ANSI to Unicode...';

    // 1. Direct Client-side In-Memory Conversion (English & Markdown Safe)
    if (window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown) {
      try {
        const converted = window.BijoyToUnicode.convertMarkdown(targetText);
        if (hasSelection) {
          editor.value = rawVal.substring(0, start) + converted + rawVal.substring(end);
          editor.setSelectionRange(start, start + converted.length);
        } else {
          editor.value = converted;
        }
        renderMarkdown();
        saveStatusEl.textContent = '✅ ANSI converted to Unicode!';
        setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
        return;
      } catch (err) {
        console.warn("Client-side conversion error, attempting backend fallback:", err);
      }
    }

    // 2. Fallback to Backend API
    fetch('/api/convert-ansi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: targetText })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.converted) {
          if (hasSelection) {
            editor.value = rawVal.substring(0, start) + data.converted + rawVal.substring(end);
            editor.setSelectionRange(start, start + data.converted.length);
          } else {
            editor.value = data.converted;
          }
          renderMarkdown();
          saveStatusEl.textContent = '✅ ANSI converted to Unicode!';
          setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
        }
      })
      .catch(e => {
        console.error("ANSI conversion error:", e);
        saveStatusEl.textContent = 'Saved locally';
      });
  }

  async function convertUnicodeToAnsiAction() {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const rawVal = editor.value;
    const hasSelection = start !== end;
    const targetText = hasSelection ? rawVal.substring(start, end) : rawVal;

    if (!targetText.trim()) {
      alert("কোনো টেক্সট পাওয়া যায়নি। এডিটরে কিছু ইউনিকোড বাংলা টেক্সট লিখুন বা পেস্ট করুন।");
      return;
    }

    pushHistoryState(rawVal);
    saveStatusEl.textContent = '🔄 Converting Unicode to ANSI (Bijoy)...';

    // 1. Direct Client-side In-Memory Conversion (English & Markdown Safe)
    if (window.BijoyToUnicode && window.BijoyToUnicode.convertUnicodeToBijoyMarkdown) {
      try {
        const converted = window.BijoyToUnicode.convertUnicodeToBijoyMarkdown(targetText);
        if (hasSelection) {
          editor.value = rawVal.substring(0, start) + converted + rawVal.substring(end);
          editor.setSelectionRange(start, start + converted.length);
        } else {
          editor.value = converted;
        }
        renderMarkdown();
        saveStatusEl.textContent = '✅ Unicode converted to ANSI (Bijoy)!';
        setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
        return;
      } catch (err) {
        console.warn("Client-side Unicode to ANSI error, trying backend:", err);
      }
    }

    // 2. Fallback to Backend API
    try {
      const resp = await fetch('/api/convert-unicode-to-ansi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: targetText })
      });
      const data = await resp.json();
      if (data.success && data.converted) {
        if (hasSelection) {
          editor.value = rawVal.substring(0, start) + data.converted + rawVal.substring(end);
          editor.setSelectionRange(start, start + data.converted.length);
        } else {
          editor.value = data.converted;
        }
        renderMarkdown();
        saveStatusEl.textContent = '✅ Unicode converted to ANSI (Bijoy)!';
        setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
      }
    } catch (e) {
      console.error("Unicode to ANSI conversion error:", e);
      saveStatusEl.textContent = 'Saved locally';
    }
  }

  // ==================== Editor & Preview Utility Actions ====================
  function selectAllAction() {
    editor.focus();
    editor.setSelectionRange(0, editor.value.length);
  }

  async function copyMarkdownAction(btn) {
    const text = editor.value;
    try {
      await navigator.clipboard.writeText(text);
      saveStatusEl.textContent = '✅ Markdown copied to clipboard!';
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
      }
      setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
    } catch (e) {
      editor.select();
      document.execCommand('copy');
      saveStatusEl.textContent = '✅ Copied!';
    }
  }

  async function copyPreviewTextAction(btn) {
    const text = previewContent.innerText;
    try {
      await navigator.clipboard.writeText(text);
      saveStatusEl.textContent = '✅ Preview text copied!';
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
      }
      setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
    } catch (e) {
      alert("Failed to copy text.");
    }
  }

  async function copyPreviewHtmlAction(btn) {
    const html = previewContent.innerHTML;
    try {
      await navigator.clipboard.writeText(html);
      saveStatusEl.textContent = '✅ Preview HTML copied!';
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
      }
      setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
    } catch (e) {
      alert("Failed to copy HTML.");
    }
  }

  function clearEditorAction() {
    if (!editor.value.trim()) return;
    if (confirm("আপনি কি নিশ্চিত যে আপনি এডিটরের সমস্ত লেখা মুছে ফেলতে চান?\n(Are you sure? You can undo this with Ctrl+Z)")) {
      pushHistoryState(editor.value);
      editor.value = '';
      renderMarkdown();
      saveStatusEl.textContent = '🗑️ Editor cleared. Press Ctrl+Z to undo.';
      setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 3000);
    }
  }

  function refreshPreviewAction() {
    saveStatusEl.textContent = '🔄 Refreshing preview...';
    renderMarkdown();
    saveStatusEl.textContent = '✅ Preview refreshed!';
    setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 1500);
  }

  function newDocAction() {
    if (editor.value.trim() && !confirm("নতুন ডকুমেন্ট শুরু করতে চান? বর্তমান ডকুমেন্ট ক্লিয়ার হবে। (Press Ctrl+Z to restore)")) {
      return;
    }
    pushHistoryState(editor.value);
    docTitleInput.value = 'Untitled Document';
    editor.value = '';
    renderMarkdown();
    saveStatusEl.textContent = '📄 New document created';
    setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2000);
  }

  function setViewMode(mode) {
    const leftPane = document.getElementById('editorPane');
    const rightPane = document.getElementById('previewPane');
    const resizer = document.getElementById('resizer');
    if (!leftPane || !rightPane) return;

    if (mode === 'editor') {
      leftPane.style.display = 'flex';
      leftPane.style.flex = '1 1 100%';
      rightPane.style.display = 'none';
      if (resizer) resizer.style.display = 'none';
    } else if (mode === 'preview') {
      leftPane.style.display = 'none';
      rightPane.style.display = 'flex';
      rightPane.style.flex = '1 1 100%';
      if (resizer) resizer.style.display = 'none';
    } else {
      leftPane.style.display = 'flex';
      leftPane.style.flex = '1 1 50%';
      rightPane.style.display = 'flex';
      rightPane.style.flex = '1 1 50%';
      if (resizer) resizer.style.display = 'block';
    }
    renderMarkdown();
  }

  // ==================== Theme & UI Helpers ====================
  function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('markitdown_studio_theme', theme);
    const btn = document.getElementById('themeToggleBtn');
    if (btn) btn.textContent = theme === 'light' ? '🌙 Dark' : '☀️ Light';

    if (window.mermaid) {
      mermaid.initialize({
        startOnLoad: false,
        theme: theme === 'light' ? 'default' : 'dark',
      });
      renderMermaidDiagrams();
    }
  }

  function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
  }

  // ==================== Desktop Menu Bar Setup ====================
  function setupMenuBar() {
    const menuItems = document.querySelectorAll('.menu-item');
    let isAnyMenuOpen = false;

    function closeAllMenus() {
      menuItems.forEach(item => item.classList.remove('active'));
      isAnyMenuOpen = false;
    }

    menuItems.forEach(item => {
      const trigger = item.querySelector('.menu-trigger');
      if (!trigger) return;

      trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const wasActive = item.classList.contains('active');
        closeAllMenus();
        if (!wasActive) {
          item.classList.add('active');
          isAnyMenuOpen = true;
        }
      });

      item.addEventListener('mouseenter', () => {
        if (isAnyMenuOpen) {
          closeAllMenus();
          item.classList.add('active');
          isAnyMenuOpen = true;
        }
      });
    });

    // Close menus when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.menubar')) {
        closeAllMenus();
      }
    });

    // Close menu when a dropdown item is clicked
    document.querySelectorAll('.menu-dropdown .dropdown-item').forEach(btn => {
      btn.addEventListener('click', () => {
        closeAllMenus();
      });
    });

    // File Menu Actions
    document.getElementById('menuNewDoc')?.addEventListener('click', newDocAction);
    document.getElementById('menuImportDoc')?.addEventListener('click', () => importModal.classList.add('active'));
    document.getElementById('menuSaveMd')?.addEventListener('click', exportMarkdown);
    document.getElementById('menuSaveHtml')?.addEventListener('click', exportHtml);
    document.getElementById('menuPrintPdf')?.addEventListener('click', exportPdf);
    document.getElementById('menuReload')?.addEventListener('click', () => {
      if (confirm("পৃষ্ঠাটি রিলোড করতে চান? কোনো অসংরক্ষিত ড্রাফট থাকলে তা মুছে যেতে পারে।")) {
        location.reload();
      }
    });

    // Edit Menu Actions
    document.getElementById('menuUndo')?.addEventListener('click', undo);
    document.getElementById('menuRedo')?.addEventListener('click', redo);
    document.getElementById('menuCut')?.addEventListener('click', () => {
      editor.focus();
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      if (start !== end) {
        pushHistoryState(editor.value);
        const textToCut = editor.value.substring(start, end);
        navigator.clipboard.writeText(textToCut).catch(() => {});
        editor.value = editor.value.substring(0, start) + editor.value.substring(end);
        editor.setSelectionRange(start, start);
        renderMarkdown();
      }
    });
    document.getElementById('menuCopy')?.addEventListener('click', () => copyMarkdownAction());
    document.getElementById('menuSelectAll')?.addEventListener('click', selectAllAction);
    document.getElementById('menuClear')?.addEventListener('click', clearEditorAction);

    // View Menu Actions
    document.getElementById('menuRefreshPreview')?.addEventListener('click', refreshPreviewAction);
    document.getElementById('menuToggleTheme')?.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
    document.getElementById('menuViewBoth')?.addEventListener('click', () => setViewMode('both'));
    document.getElementById('menuViewEditorOnly')?.addEventListener('click', () => setViewMode('editor'));
    document.getElementById('menuViewPreviewOnly')?.addEventListener('click', () => setViewMode('preview'));

    // Tools & Bengali Menu Actions
    document.getElementById('menuAnsiToUnicode')?.addEventListener('click', convertAnsiToUnicodeAction);
    document.getElementById('menuUnicodeToAnsi')?.addEventListener('click', convertUnicodeToAnsiAction);
    document.getElementById('menuOcr')?.addEventListener('click', () => ocrModal.classList.add('active'));
    document.getElementById('menuCopyPreviewText')?.addEventListener('click', () => copyPreviewTextAction());
    document.getElementById('menuCopyHtml')?.addEventListener('click', () => copyPreviewHtmlAction());

    // Settings & Help Actions
    document.getElementById('menuOpenSettings')?.addEventListener('click', () => {
      document.getElementById('openaiKeyInput').value = localStorage.getItem('markitdown_openai_key') || '';
      const geminiInput = document.getElementById('geminiKeyInput');
      if (geminiInput) geminiInput.value = localStorage.getItem('markitdown_gemini_key') || '';
      document.getElementById('openaiModelSelect').value = localStorage.getItem('markitdown_openai_model') || 'gpt-4o';
      settingsModal.classList.add('active');
    });
    document.getElementById('menuShortcuts')?.addEventListener('click', () => shortcutsModal.classList.add('active'));
  }

  // ==================== Event Listeners Setup ====================
  function setupEventListeners() {
    // Setup Desktop Menu Bar
    setupMenuBar();

    // Editor Input Listener (Debounced Rendering & History)
    editor.addEventListener('input', () => {
      clearTimeout(historyDebounceTimeout);
      historyDebounceTimeout = setTimeout(() => {
        pushHistoryState(editor.value);
      }, 1000);

      clearTimeout(renderTimeout);
      saveStatusEl.textContent = 'Saving...';
      renderTimeout = setTimeout(renderMarkdown, 180);
    });

    // Automatic ANSI / Bijoy detection and instant conversion on Paste
    editor.addEventListener('paste', (e) => {
      const clipboardData = e.clipboardData || window.clipboardData;
      if (!clipboardData) return;
      const pastedText = clipboardData.getData('text');
      if (window.BijoyToUnicode && window.BijoyToUnicode.isLikelyBijoy && window.BijoyToUnicode.isLikelyBijoy(pastedText)) {
        e.preventDefault();
        pushHistoryState(editor.value);
        const converted = window.BijoyToUnicode.convertMarkdown(pastedText);
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        const val = editor.value;
        editor.value = val.substring(0, start) + converted + val.substring(end);
        editor.setSelectionRange(start + converted.length, start + converted.length);
        renderMarkdown();
        saveStatusEl.textContent = '✨ Auto-converted Bijoy to Unicode!';
        setTimeout(() => { saveStatusEl.textContent = 'Saved locally'; }, 2500);
      }
    });

    // Keyboard Shortcuts (Ctrl+Z, Ctrl+Y, Ctrl+Shift+Z, Ctrl+B, Ctrl+I, Ctrl+S, Ctrl+O, Ctrl+N, Ctrl+P, F5, Tab)
    editor.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'z' || e.key === 'Z') {
          e.preventDefault();
          if (e.shiftKey) {
            redo();
          } else {
            undo();
          }
          return;
        }
        if (e.key === 'y' || e.key === 'Y') {
          e.preventDefault();
          redo();
          return;
        }
        if (e.key === 'b' || e.key === 'B') {
          e.preventDefault();
          insertFormat('**', '**', 'bold text');
          return;
        }
        if (e.key === 'i' || e.key === 'I') {
          e.preventDefault();
          insertFormat('*', '*', 'italic text');
          return;
        }
        if (e.key === 's' || e.key === 'S') {
          e.preventDefault();
          exportMarkdown();
          return;
        }
        if (e.key === 'o' || e.key === 'O') {
          e.preventDefault();
          importModal.classList.add('active');
          return;
        }
        if (e.key === 'n' || e.key === 'N') {
          e.preventDefault();
          newDocAction();
          return;
        }
        if (e.key === 'p' || e.key === 'P') {
          e.preventDefault();
          exportPdf();
          return;
        }
      } else if (e.key === 'Tab') {
        e.preventDefault();
        insertFormat('  ', '', '');
      } else if (e.key === 'F5') {
        if (!e.ctrlKey) {
          e.preventDefault();
          refreshPreviewAction();
        }
      }
    });

    // Title Input
    docTitleInput.addEventListener('input', () => {
      localStorage.setItem('markitdown_studio_title', docTitleInput.value);
    });

    // Setup Sync Scrolling
    setupScrollSync();

    // Theme Toggle
    document.getElementById('themeToggleBtn')?.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });

    // Toolbar Formatting Buttons
    document.getElementById('toolBold')?.addEventListener('click', () => insertFormat('**', '**', 'bold text'));
    document.getElementById('toolItalic')?.addEventListener('click', () => insertFormat('*', '*', 'italic text'));
    document.getElementById('toolStrike')?.addEventListener('click', () => insertFormat('~~', '~~', 'strikethrough'));
    document.getElementById('toolH1')?.addEventListener('click', () => insertFormat('# ', '', 'Heading 1'));
    document.getElementById('toolH2')?.addEventListener('click', () => insertFormat('## ', '', 'Heading 2'));
    document.getElementById('toolH3')?.addEventListener('click', () => insertFormat('### ', '', 'Heading 3'));
    document.getElementById('toolCode')?.addEventListener('click', () => insertFormat('`', '`', 'code'));
    document.getElementById('toolCodeBlock')?.addEventListener('click', () => insertBlock('```python\n# Your code here\nprint("Hello")\n```'));
    document.getElementById('toolQuote')?.addEventListener('click', () => insertFormat('> ', '', 'Quote'));
    document.getElementById('toolUl')?.addEventListener('click', () => insertFormat('- ', '', 'List item'));
    document.getElementById('toolOl')?.addEventListener('click', () => insertFormat('1. ', '', 'Numbered item'));
    document.getElementById('toolTask')?.addEventListener('click', () => insertFormat('- [ ] ', '', 'Task item'));
    document.getElementById('toolTable')?.addEventListener('click', () => {
      insertBlock('| কলাম ১ | কলাম ২ | কলাম ৩ |\n| :--- | :--- | :--- |\n| ডেটা ১ | ডেটা ২ | ডেটা ৩ |\n| তথ্য ৪ | তথ্য ৫ | তথ্য ৬ |');
    });
    document.getElementById('toolMath')?.addEventListener('click', () => {
      insertBlock('$$\n\\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}\n$$');
    });
    document.getElementById('toolMermaid')?.addEventListener('click', () => {
      insertBlock('```mermaid\ngraph LR\n    শুরু[Start] --> প্রক্রিয়া[Process]\n    প্রক্রিয়া --> শেষ[End]\n```');
    });

    // Toolbar History & Bengali Conversion Buttons
    document.getElementById('toolUndo')?.addEventListener('click', undo);
    document.getElementById('toolRedo')?.addEventListener('click', redo);
    document.getElementById('toolAnsiToUnicode')?.addEventListener('click', convertAnsiToUnicodeAction);
    document.getElementById('toolUnicodeToAnsi')?.addEventListener('click', convertUnicodeToAnsiAction);

    // Toolbar Quick Utilities
    document.getElementById('toolRefresh')?.addEventListener('click', refreshPreviewAction);
    document.getElementById('toolSelectAll')?.addEventListener('click', selectAllAction);
    const toolCopyBtn = document.getElementById('toolCopy');
    toolCopyBtn?.addEventListener('click', () => copyMarkdownAction(toolCopyBtn));
    document.getElementById('toolClear')?.addEventListener('click', clearEditorAction);

    // Editor Pane Header Action Buttons
    document.getElementById('paneUndoBtn')?.addEventListener('click', undo);
    document.getElementById('paneRedoBtn')?.addEventListener('click', redo);
    document.getElementById('paneSelectAllBtn')?.addEventListener('click', selectAllAction);
    const paneCopyBtn = document.getElementById('paneCopyBtn');
    paneCopyBtn?.addEventListener('click', () => copyMarkdownAction(paneCopyBtn));
    document.getElementById('paneClearBtn')?.addEventListener('click', clearEditorAction);

    // Preview Pane Header Action Buttons
    document.getElementById('paneRefreshBtn')?.addEventListener('click', refreshPreviewAction);
    const paneCopyTextBtn = document.getElementById('paneCopyTextBtn');
    paneCopyTextBtn?.addEventListener('click', () => copyPreviewTextAction(paneCopyTextBtn));
    const paneCopyHtmlBtn = document.getElementById('paneCopyHtmlBtn');
    paneCopyHtmlBtn?.addEventListener('click', () => copyPreviewHtmlAction(paneCopyHtmlBtn));

    // Export Dropdown
    const exportBtn = document.getElementById('exportDropdownBtn');
    exportBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      exportDropdown.classList.toggle('show');
    });

    window.addEventListener('click', () => {
      exportDropdown.classList.remove('show');
    });

    document.getElementById('exportMdBtn')?.addEventListener('click', exportMarkdown);
    document.getElementById('exportHtmlBtn')?.addEventListener('click', exportHtml);
    document.getElementById('exportPdfBtn')?.addEventListener('click', exportPdf);

    // Modal Triggers
    document.getElementById('importDocBtn')?.addEventListener('click', () => importModal.classList.add('active'));
    document.getElementById('ocrImgBtn')?.addEventListener('click', () => ocrModal.classList.add('active'));
    document.getElementById('settingsBtn')?.addEventListener('click', () => {
      document.getElementById('openaiKeyInput').value = localStorage.getItem('markitdown_openai_key') || '';
      const geminiInput = document.getElementById('geminiKeyInput');
      if (geminiInput) geminiInput.value = localStorage.getItem('markitdown_gemini_key') || '';
      document.getElementById('openaiModelSelect').value = localStorage.getItem('markitdown_openai_model') || 'gpt-4o';
      settingsModal.classList.add('active');
    });

    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
      btn.addEventListener('click', closeAllModals);
    });

    // Close modals on Escape key
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeAllModals();
        exportDropdown.classList.remove('show');
      }
    });

    // File Dropzones in Modals
    setupDropZone('importDropZone', 'importFileInput', convertUploadedFile);
    setupDropZone('ocrDropZone', 'ocrFileInput', performImageOcr);

    // Main Window Drag & Drop
    window.addEventListener('dragover', (e) => e.preventDefault());
    window.addEventListener('drop', (e) => {
      e.preventDefault();
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.type.startsWith('image/')) {
          performImageOcr(file);
        } else {
          convertUploadedFile(file);
        }
      }
    });

    // Resizer logic
    const resizer = document.getElementById('resizer');
    const leftPane = document.getElementById('editorPane');
    let isResizing = false;

    resizer?.addEventListener('mousedown', () => {
      isResizing = true;
      resizer.classList.add('dragging');
    });

    window.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      const containerRect = document.querySelector('.workspace').getBoundingClientRect();
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      if (newWidth > 15 && newWidth < 85) {
        leftPane.style.flex = `0 0 ${newWidth}%`;
      }
    });

    window.addEventListener('mouseup', () => {
      isResizing = false;
      resizer?.classList.remove('dragging');
    });

    // Settings Save
    document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
      const apiKey = document.getElementById('openaiKeyInput').value.trim();
      const geminiKey = document.getElementById('geminiKeyInput')?.value.trim() || '';
      const model = document.getElementById('openaiModelSelect').value;
      localStorage.setItem('markitdown_openai_key', apiKey);
      localStorage.setItem('markitdown_gemini_key', geminiKey);
      localStorage.setItem('markitdown_openai_model', model);

      // Notify Python desktop backend if available
      if (window.pywebview && window.pywebview.api && window.pywebview.api.update_settings) {
        window.pywebview.api.update_settings(apiKey, model, geminiKey);
      }
      closeAllModals();
      alert('Settings saved successfully!');
    });
  }

  function setupDropZone(dropZoneId, fileInputId, handler) {
    const dz = document.getElementById(dropZoneId);
    const fi = document.getElementById(fileInputId);
    if (!dz || !fi) return;

    dz.addEventListener('click', () => fi.click());
    fi.addEventListener('change', () => {
      if (fi.files && fi.files[0]) handler(fi.files[0]);
    });

    dz.addEventListener('dragover', (e) => {
      e.preventDefault();
      dz.classList.add('dragover');
    });
    dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
    dz.addEventListener('drop', (e) => {
      e.preventDefault();
      dz.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handler(e.dataTransfer.files[0]);
      }
    });
  }

  // Launch on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
