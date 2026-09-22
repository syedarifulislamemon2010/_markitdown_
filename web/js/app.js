/**
 * MarkItDown Studio - Advanced VS Code Dark Modern Markdown Workspace
 * Author: Syed Ariful Islam Emon (syedarifulislamemon2010)
 * Copyright (c) 2026 Syed Ariful Islam Emon
 */

(function () {
  'use strict';

  // ==================== Security: Session Token Interceptor ====================
  const _nativeFetch = window.fetch;
  window.fetch = function (resource, init) {
    init = init || {};
    let url = typeof resource === 'string' ? resource : (resource ? resource.url : '');
    if (url && (url.startsWith('/api/') || url.includes('/api/')) && !url.endsWith('/api/health')) {
      const token = window.__STUDIO_TOKEN__;
      if (token) {
        if (typeof Request !== 'undefined' && resource instanceof Request) {
          resource.headers.set('X-Session-Token', token);
        } else {
          const headers = new Headers(init.headers || {});
          if (!headers.has('X-Session-Token')) {
            headers.set('X-Session-Token', token);
          }
          init.headers = headers;
        }
      }
    }
    return _nativeFetch.call(this, resource, init);
  };

  // Sync session token from pywebview bridge if available
  window.addEventListener('pywebviewready', async () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_session_token) {
      try {
        const tok = await window.pywebview.api.get_session_token();
        if (tok) window.__STUDIO_TOKEN__ = tok;
      } catch (_) {}
    }
  });

  // ==================== Global Elements & State ====================
  const editor = document.getElementById('editor');
  const preview = document.getElementById('preview');
  const previewContent = document.getElementById('previewContent');
  const docTitleInput = document.getElementById('docTitle');
  const lineNumbers = document.getElementById('lineNumbers');
  const saveStatus = document.getElementById('saveStatus');
  const sbLineCol = document.getElementById('sbLineCol');
  const sbWordCount = document.getElementById('sbWordCount');
  const breadcrumbCurrentDoc = document.getElementById('breadcrumbCurrentDoc');

  // Modals
  const importModal = document.getElementById('importModal');
  const ocrModal = document.getElementById('ocrModal');
  const settingsModal = document.getElementById('settingsModal');
  const shortcutsModal = document.getElementById('shortcutsModal');
  const findReplaceModal = document.getElementById('findReplaceModal');
  const statsModal = document.getElementById('statsModal');
  const aboutModal = document.getElementById('aboutModal');
  const exportModal = document.getElementById('exportModal');
  const exportDropdown = document.getElementById('exportDropdown');

  // Sidebar & Activity Bar
  const primarySidebar = document.getElementById('primarySidebar');
  const sidebarTabList = document.getElementById('sidebarTabList');

  // Multi-Document Tabs State
  let tabs = [];
  let activeTabId = null;
  let isScrolling = false;
  let currentFontSize = 13;
  let selectedExportFormat = 'docx';
  let activeToastTimer = null;

  // Default Welcome Content
  const DEFAULT_WELCOME_MD = `# MarkItDown Studio
**সর্বাধুনিক বাংলা ও ইংরেজি মার্কডাউন এডিটর ও ইউনিভার্সাল কনভার্টার**
*নির্মাতা: সৈয়দ আরিফুল ইসলাম ইমন (Syed Ariful Islam Emon)*

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
    C --> E[VS Code ডার্ক স্টুডিও]
    D --> E
    E --> F[এক্সপোর্ট: Word / PDF / MD / HTML]
\`\`\`

---

### ৪. ডেটা টেবিল ও চেকলিস্ট (Tables & Task List)

| ফিচার | স্ট্যাটাস | সুবিধা |
| :--- | :---: | :--- |
| **লাইভ প্রিভিউ** | ✅ সচল | টাইপ করার সাথে সাথে রেন্ডার |
| **স্ক্রোল সিঙ্ক** | ✅ সচল | উভয় পাশ একসাথে স্ক্রোল হবে |
| **মাল্টি-ট্যাব** | ✅ সচল | একাধিক ডকুমেন্টে একসাথে কাজ |
| **ওয়ার্ড ও পিডিএফ** | ✅ সচল | এক ক্লিকে .docx ও .pdf এক্সপোর্ট |

- [x] ড্র্যাগ & ড্রপ ফাইল কনভার্টার
- [x] বাংলা ফন্ট টেক্সট শেপিং
- [x] অফলাইন লোকাল স্টোরেজ ড্রাফট সেভ
- [x] VS Code ডার্ক মডার্ন ইন্টারফেস
`;

  // ==================== Single-Toast Notification Manager ====================
  function showToast(message, type = 'info', duration = 2500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    if (activeToastTimer) {
      clearTimeout(activeToastTimer);
      activeToastTimer = null;
    }
    container.innerHTML = '';

    const toast = document.createElement('div');
    toast.className = `toast-message toast-${type}`;
    const icon = type === 'success' ? '✅' : (type === 'error' ? '❌' : (type === 'warning' ? '⚠️' : 'ℹ️'));
    toast.innerHTML = `<span style="font-size: 15px;">${icon}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    activeToastTimer = setTimeout(() => {
      toast.classList.add('toast-fadeout');
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 250);
    }, duration);
  }

  // ==================== In-App Confirmation Modal ====================
  function showConfirmModal(title, message, onConfirm) {
    const modal = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const msgEl = document.getElementById('confirmMessage');
    const okBtn = document.getElementById('confirmOkBtn');
    const cancelBtn = document.getElementById('confirmCancelBtn');
    const closeBtn = document.getElementById('confirmCloseBtn');

    if (!modal) {
      if (confirm(message)) onConfirm();
      return;
    }

    titleEl.textContent = title;
    msgEl.textContent = message;
    modal.classList.add('active');

    function cleanup() {
      modal.classList.remove('active');
      okBtn.removeEventListener('click', handleOk);
      cancelBtn.removeEventListener('click', handleCancel);
      closeBtn.removeEventListener('click', handleCancel);
    }

    function handleOk() {
      cleanup();
      if (typeof onConfirm === 'function') onConfirm();
    }

    function handleCancel() {
      cleanup();
    }

    okBtn.addEventListener('click', handleOk);
    cancelBtn.addEventListener('click', handleCancel);
    closeBtn.addEventListener('click', handleCancel);
  }

  // ==================== Multi-Document Tab System ====================
  function initTabs() {
    let savedTabs = null;
    try {
      const raw = localStorage.getItem('markitdown_studio_tabs_v2');
      if (raw) savedTabs = JSON.parse(raw);
    } catch (e) {
      console.warn("Error parsing saved tabs:", e);
    }

    const savedActiveId = localStorage.getItem('markitdown_studio_active_tab_id_v2');

    if (Array.isArray(savedTabs) && savedTabs.length > 0) {
      tabs = savedTabs;
    } else {
      const oldDraft = localStorage.getItem('markitdown_editor_content');
      const oldTitle = localStorage.getItem('markitdown_studio_title');
      tabs = [
        {
          id: 'tab_' + Date.now(),
          title: oldTitle || 'Untitled Document 1',
          content: oldDraft || DEFAULT_WELCOME_MD,
          undoStack: [],
          redoStack: []
        }
      ];
    }

    tabs.forEach(t => {
      if (!Array.isArray(t.undoStack)) t.undoStack = [];
      if (!Array.isArray(t.redoStack)) t.redoStack = [];
    });

    const targetTab = tabs.find(t => t.id === savedActiveId) || tabs[0];
    activeTabId = targetTab.id;

    editor.value = targetTab.content;
    docTitleInput.value = targetTab.title;
    if (breadcrumbCurrentDoc) {
      breadcrumbCurrentDoc.textContent = `${targetTab.title}.md`;
    }

    renderTabs();
    updateLineNumbers();
    updateStatusBar();
  }

  function renderTabs() {
    const tabList = document.getElementById('tabList');
    if (tabList) {
      tabList.innerHTML = '';
      tabs.forEach(tab => {
        const item = document.createElement('div');
        item.className = `tab-item ${tab.id === activeTabId ? 'active' : ''}`;
        item.dataset.tabId = tab.id;

        const icon = document.createElement('span');
        icon.className = 'tab-icon';
        icon.textContent = '📄';
        item.appendChild(icon);

        const titleSpan = document.createElement('span');
        titleSpan.className = 'tab-title';
        titleSpan.textContent = tab.title || 'Untitled Document';
        item.appendChild(titleSpan);

        const closeSpan = document.createElement('span');
        closeSpan.className = 'tab-close';
        closeSpan.innerHTML = '✕';
        closeSpan.title = 'ট্যাব বন্ধ করুন (Close Tab)';
        closeSpan.addEventListener('click', (e) => {
          e.stopPropagation();
          closeTab(tab.id);
        });
        item.appendChild(closeSpan);

        item.addEventListener('click', () => {
          if (tab.id !== activeTabId) {
            switchTab(tab.id);
          }
        });

        tabList.appendChild(item);
      });
    }

    renderSidebarTabs();
  }

  function renderSidebarTabs() {
    if (!sidebarTabList) return;
    sidebarTabList.innerHTML = '';

    tabs.forEach(tab => {
      const item = document.createElement('div');
      item.className = `sidebar-tab-item ${tab.id === activeTabId ? 'active' : ''}`;
      item.innerHTML = `<span>📄</span> <span style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(tab.title)}</span> <span class="tab-close-icon">✕</span>`;

      item.querySelector('.tab-close-icon').addEventListener('click', (e) => {
        e.stopPropagation();
        closeTab(tab.id);
      });

      item.addEventListener('click', () => {
        if (tab.id !== activeTabId) {
          switchTab(tab.id);
        }
      });

      sidebarTabList.appendChild(item);
    });
  }

  function getNextTabNumber() {
    let maxNum = 0;
    tabs.forEach(t => {
      const match = t.title.match(/Untitled Document\s*(\d+)/i);
      if (match) {
        const num = parseInt(match[1]);
        if (num > maxNum) maxNum = num;
      }
    });
    return maxNum + 1;
  }

  function createNewTab(title = null, content = '') {
    const curr = tabs.find(t => t.id === activeTabId);
    if (curr) {
      curr.content = editor.value;
      curr.title = docTitleInput.value.trim() || 'Untitled Document';
    }

    const tabNum = getNextTabNumber();
    const finalTitle = title || `Untitled Document ${tabNum}`;
    const newTab = {
      id: 'tab_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
      title: finalTitle,
      content: content,
      undoStack: [],
      redoStack: []
    };

    tabs.push(newTab);
    activeTabId = newTab.id;

    editor.value = newTab.content;
    docTitleInput.value = newTab.title;
    if (breadcrumbCurrentDoc) {
      breadcrumbCurrentDoc.textContent = `${newTab.title}.md`;
    }

    saveAllTabs();
    renderTabs();
    renderMarkdown();
    updateUndoRedoUI();
    updateLineNumbers();
    updateStatusBar();
    editor.focus();
    showToast(`📄 নতুন ডকুমেন্ট ট্যাব খোলা হয়েছে: ${finalTitle}`, 'info', 1500);
  }

  function switchTab(targetId) {
    if (targetId === activeTabId) return;

    const curr = tabs.find(t => t.id === activeTabId);
    if (curr) {
      curr.content = editor.value;
      curr.title = docTitleInput.value.trim() || 'Untitled Document';
    }

    const target = tabs.find(t => t.id === targetId);
    if (!target) return;

    activeTabId = target.id;
    editor.value = target.content;
    docTitleInput.value = target.title;
    if (breadcrumbCurrentDoc) {
      breadcrumbCurrentDoc.textContent = `${target.title}.md`;
    }

    saveAllTabs();
    renderTabs();
    renderMarkdown();
    updateUndoRedoUI();
    updateLineNumbers();
    updateStatusBar();
  }

  function closeTab(tabIdToClose) {
    if (tabs.length === 1) {
      showConfirmModal("ট্যাব রিসেট", "এটি একমাত্র খোলা ট্যাব। এটি বন্ধ করলে কন্টেন্ট মুছে একটি নতুন খালি ডকুমেন্ট তৈরি হবে। এগিয়ে যেতে চান?", () => {
        tabs[0].content = '';
        tabs[0].title = 'Untitled Document 1';
        tabs[0].undoStack = [];
        tabs[0].redoStack = [];
        editor.value = '';
        docTitleInput.value = 'Untitled Document 1';
        if (breadcrumbCurrentDoc) breadcrumbCurrentDoc.textContent = 'Untitled Document 1.md';
        saveAllTabs();
        renderTabs();
        renderMarkdown();
        updateUndoRedoUI();
        updateLineNumbers();
        updateStatusBar();
        showToast("ট্যাব খালি করা হয়েছে", "info", 1500);
      });
      return;
    }

    const idx = tabs.findIndex(t => t.id === tabIdToClose);
    if (idx === -1) return;

    tabs.splice(idx, 1);

    if (activeTabId === tabIdToClose) {
      const nextIdx = Math.max(0, idx - 1);
      const nextTab = tabs[nextIdx];
      activeTabId = nextTab.id;
      editor.value = nextTab.content;
      docTitleInput.value = nextTab.title;
      if (breadcrumbCurrentDoc) {
        breadcrumbCurrentDoc.textContent = `${nextTab.title}.md`;
      }
    }

    saveAllTabs();
    renderTabs();
    renderMarkdown();
    updateUndoRedoUI();
    updateLineNumbers();
    updateStatusBar();
  }

  function saveAllTabs() {
    const activeTab = tabs.find(t => t.id === activeTabId);
    if (activeTab) {
      activeTab.content = editor.value;
      activeTab.title = docTitleInput.value.trim() || 'Untitled Document';
    }

    try {
      localStorage.setItem('markitdown_studio_tabs_v2', JSON.stringify(tabs));
      localStorage.setItem('markitdown_studio_active_tab_id_v2', activeTabId);
      localStorage.setItem('markitdown_editor_content', editor.value);
      localStorage.setItem('markitdown_studio_title', docTitleInput.value);
      setSaveStatus('saved');
    } catch (e) {
      console.warn("Storage save error:", e);
    }
  }

  // ==================== Undo & Redo System ====================
  function getActiveTab() {
    return tabs.find(t => t.id === activeTabId) || null;
  }

  function pushHistoryState(oldContent) {
    const tab = getActiveTab();
    if (!tab) return;
    if (oldContent === editor.value) return;

    tab.undoStack.push({
      content: oldContent,
      selStart: editor.selectionStart,
      selEnd: editor.selectionEnd
    });

    if (tab.undoStack.length > 50) tab.undoStack.shift();
    tab.redoStack = [];
    updateUndoRedoUI();
  }

  function undo() {
    const tab = getActiveTab();
    if (!tab || tab.undoStack.length === 0) return;

    const previous = tab.undoStack.pop();
    tab.redoStack.push({
      content: editor.value,
      selStart: editor.selectionStart,
      selEnd: editor.selectionEnd
    });

    editor.value = previous.content;
    editor.setSelectionRange(previous.selStart, previous.selEnd);
    renderMarkdown();
    updateUndoRedoUI();
    updateLineNumbers();
    updateStatusBar();
    saveAllTabs();
  }

  function redo() {
    const tab = getActiveTab();
    if (!tab || tab.redoStack.length === 0) return;

    const next = tab.redoStack.pop();
    tab.undoStack.push({
      content: editor.value,
      selStart: editor.selectionStart,
      selEnd: editor.selectionEnd
    });

    editor.value = next.content;
    editor.setSelectionRange(next.selStart, next.selEnd);
    renderMarkdown();
    updateUndoRedoUI();
    updateLineNumbers();
    updateStatusBar();
    saveAllTabs();
  }

  function updateUndoRedoUI() {
    const tab = getActiveTab();
    const canUndo = tab && tab.undoStack && tab.undoStack.length > 0;
    const canRedo = tab && tab.redoStack && tab.redoStack.length > 0;

    ['paneUndoBtn', 'toolUndo', 'menuUndo'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.disabled = !canUndo;
        btn.style.opacity = canUndo ? '1' : '0.4';
        btn.style.pointerEvents = canUndo ? 'auto' : 'none';
      }
    });

    ['paneRedoBtn', 'toolRedo', 'menuRedo'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.disabled = !canRedo;
        btn.style.opacity = canRedo ? '1' : '0.4';
        btn.style.pointerEvents = canRedo ? 'auto' : 'none';
      }
    });
  }

  // Caches for expensive rendering operations
  const katexCache = new Map();
  const mermaidCache = new Map();
  let lastHeadersSerialized = '';

  function renderKatexCached(formula, displayMode) {
    const key = `${displayMode ? 'D' : 'I'}:${formula}`;
    if (katexCache.has(key)) return katexCache.get(key);
    try {
      const rendered = katex.renderToString(formula, { displayMode: displayMode, throwOnError: false });
      if (katexCache.size > 300) {
        const firstKey = katexCache.keys().next().value;
        katexCache.delete(firstKey);
      }
      katexCache.set(key, rendered);
      return rendered;
    } catch (e) {
      return displayMode ? `<div class="katex-error">$$${escapeHtml(formula)}$$</div>` : `$${escapeHtml(formula)}$`;
    }
  }

  // ==================== Markdown & Math Rendering ====================
  function renderMarkdown() {
    const rawText = editor.value;

    const mathBlocks = [];
    const inlineMath = [];

    // Isolate Math blocks $$...$$
    let textToRender = rawText.replace(/\$\$([\s\S]+?)\$\$/g, (match, formula) => {
      mathBlocks.push(formula.trim());
      return `@@MATH_BLOCK_${mathBlocks.length - 1}@@`;
    });

    // Inline math $...$
    textToRender = textToRender.replace(/\$([^\$\n]+?)\$/g, (match, formula) => {
      inlineMath.push(formula.trim());
      return `@@MATH_INLINE_${inlineMath.length - 1}@@`;
    });

    // Automatic Unicode Conversion for Preview ONLY if pure Bijoy is detected without existing Unicode
    if (!(/[\u0980-\u09FF]/.test(textToRender)) && window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown && window.BijoyToUnicode.isLikelyBijoy(textToRender)) {
      textToRender = window.BijoyToUnicode.convertMarkdown(textToRender);
    }

    // Parse Markdown with marked.js
    let html = '';
    if (window.marked) {
      html = marked.parse(textToRender, {
        gfm: true,
        breaks: true,
      });
    } else {
      html = `<pre>${escapeHtml(textToRender)}</pre>`;
    }

    // Restore Math blocks with cached KaTeX rendering
    html = html.replace(/@@MATH_BLOCK_(\d+)@@/g, (match, id) => {
      const formula = mathBlocks[parseInt(id)];
      const rendered = renderKatexCached(formula, true);
      return `<div class="katex-block">${rendered}</div>`;
    });

    html = html.replace(/@@MATH_INLINE_(\d+)@@/g, (match, id) => {
      const formula = inlineMath[parseInt(id)];
      return renderKatexCached(formula, false);
    });

    previewContent.innerHTML = html;
    renderMermaidDiagrams();
    updateOutline();
  }

  function renderMermaidDiagrams() {
    if (!window.mermaid) return;
    const mermaidNodes = previewContent.querySelectorAll('pre code.language-mermaid');
    mermaidNodes.forEach((codeNode, idx) => {
      const preNode = codeNode.parentElement;
      const rawGraph = codeNode.textContent.trim();
      const container = document.createElement('div');
      container.className = 'mermaid-chart';
      preNode.parentNode.replaceChild(container, preNode);

      // Instant render from cache if diagram definition unchanged
      if (mermaidCache.has(rawGraph)) {
        container.innerHTML = mermaidCache.get(rawGraph);
        return;
      }

      const uniqueId = 'mermaid-' + Date.now() + '-' + idx;
      try {
        mermaid.render(uniqueId, rawGraph).then(({ svg }) => {
          mermaidCache.set(rawGraph, svg);
          if (mermaidCache.size > 50) {
            const firstKey = mermaidCache.keys().next().value;
            mermaidCache.delete(firstKey);
          }
          container.innerHTML = svg;
        }).catch(err => {
          container.innerHTML = `<div style="color:#f87171;font-size:12px;">⚠️ ডায়াগ্রাম রেন্ডার ত্রুটি: ${escapeHtml(err.message)}</div>`;
        });
      } catch (e) {
        container.innerHTML = `<div style="color:#f87171;font-size:12px;">⚠️ ডায়াগ্রাম ত্রুটি</div>`;
      }
    });
  }

  // ==================== Real VS Code Document Outline ====================
  function updateOutline() {
    const outlineList = document.getElementById('sidebarOutlineList');
    if (!outlineList) return;
    const ed = document.getElementById('editor');
    if (!ed) return;

    const text = ed.value || '';
    const lines = text.split('\n');
    const headers = [];

    for (let i = 0; i < lines.length; i++) {
      const match = lines[i].match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        headers.push({
          level: match[1].length,
          text: match[2].replace(/[#*_`~]/g, '').trim(),
          line: i
        });
      }
    }

    // Skip DOM recreation if headers have not changed
    const serialized = headers.map(h => `${h.level}:${h.line}:${h.text}`).join('|');
    if (serialized === lastHeadersSerialized) return;
    lastHeadersSerialized = serialized;

    if (headers.length === 0) {
      outlineList.innerHTML = '<div style="padding: 8px 12px; font-size: 11px; color: var(--text-secondary); font-style: italic;">কোনো হেডিং পাওয়া যায়নি</div>';
      return;
    }

    outlineList.innerHTML = headers.map(h => `
      <div class="sidebar-outline-item" data-line="${h.line}" style="padding-left: ${8 + (h.level - 1) * 10}px;" title="Go to line ${h.line + 1}: ${escapeHtml(h.text)}">
        <span class="outline-icon">H${h.level}</span>
        <span class="outline-text">${escapeHtml(h.text)}</span>
      </div>
    `).join('');

    outlineList.querySelectorAll('.sidebar-outline-item').forEach(item => {
      item.addEventListener('click', () => {
        const lineNum = parseInt(item.dataset.line, 10);
        scrollToEditorLine(lineNum);
      });
    });
  }

  function scrollToEditorLine(lineNum) {
    const ed = document.getElementById('editor');
    if (!ed) return;
    const lines = ed.value.split('\n');
    let charIndex = 0;
    for (let i = 0; i < lineNum && i < lines.length; i++) {
      charIndex += lines[i].length + 1;
    }
    ed.focus();
    ed.setSelectionRange(charIndex, charIndex + (lines[lineNum] ? lines[lineNum].length : 0));
    const lineHeight = 20.8;
    ed.scrollTop = Math.max(0, lineNum * lineHeight - 100);

    const prev = document.getElementById('preview');
    if (prev) {
      const headings = prev.querySelectorAll('h1, h2, h3, h4, h5, h6');
      for (const h of headings) {
        if (lines[lineNum] && lines[lineNum].includes(h.textContent.trim())) {
          h.scrollIntoView({ behavior: 'smooth', block: 'start' });
          break;
        }
      }
    }
  }

  function toggleWordWrap() {
    const ed = document.getElementById('editor');
    if (!ed) return;
    const isNoWrap = ed.classList.toggle('no-wrap');
    showToast(isNoWrap ? 'Word Wrap: বন্ধ (Off)' : 'Word Wrap: চালু (On)', 'info', 1500);
  }

  // ==================== Font Mode Controller (Kalpurush Unicode vs Kalpurush ANSI) ====================
  let currentFontMode = 'unicode'; // 'unicode' (Kalpurush) or 'bijoy' (Kalpurush ANSI)

  function setFontMode(mode, silent = false) {
    currentFontMode = mode;
    const toolBtn = document.getElementById('toolToggleFont');
    const sbBtn = document.getElementById('sbFontMode');
    const sbEnc = document.getElementById('sbEncoding');

    if (mode === 'bijoy') {
      editor.classList.add('font-bijoy');
      editor.classList.remove('font-unicode');
      if (toolBtn) toolBtn.innerHTML = '🔤 কালপুরুষ ANSI (বিজয়)';
      if (sbBtn) sbBtn.innerHTML = '🔤 Kalpurush ANSI (বিজয়)';
      if (sbEnc) sbEnc.textContent = 'ANSI (বিজয়)';
      if (!silent) showToast('🔤 ফন্ট: Kalpurush ANSI (বিজয়) সক্রিয়', 'info', 1500);
    } else {
      editor.classList.remove('font-bijoy');
      editor.classList.add('font-unicode');
      if (toolBtn) toolBtn.innerHTML = '🔤 কালপুরুষ (ইউনিকোড)';
      if (sbBtn) sbBtn.innerHTML = '🔤 Kalpurush';
      if (sbEnc) sbEnc.textContent = 'UTF-8';
      if (!silent) showToast('🔤 ফন্ট: Kalpurush (ইউনিকোড) সক্রিয়', 'info', 1500);
    }
  }

  function toggleFontMode() {
    setFontMode(currentFontMode === 'unicode' ? 'bijoy' : 'unicode');
  }

  // ==================== Dynamic Status Bar Helpers ====================
  function setSaveStatus(status, timestamp = null) {
    if (!saveStatus) return;
    if (status === 'dirty') {
      saveStatus.innerHTML = '<span style="color:#e5c07b;">● Unsaved edits</span>';
      saveStatus.classList.add('save-dirty');
      saveStatus.classList.remove('save-clean');
      updateBranchStatus(true);
    } else if (status === 'saved') {
      const timeStr = timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      saveStatus.innerHTML = `<span style="color:var(--success-color);">✓ Saved locally (${timeStr})</span>`;
      saveStatus.classList.remove('save-dirty');
      saveStatus.classList.add('save-clean');
      updateBranchStatus(false);
    }
  }

  function updateBranchStatus(dirty = false) {
    const sbBranchText = document.getElementById('sbBranchName') || document.getElementById('sbBranchText');
    if (!sbBranchText) return;
    const activeTab = getActiveTab();
    const name = activeTab ? (activeTab.title.length > 18 ? activeTab.title.substring(0, 15) + '...' : activeTab.title) : 'main';
    sbBranchText.textContent = dirty ? `${name}*` : name;
  }

  async function checkServerStatus() {
    const sbSyncStatus = document.getElementById('sbSyncStatus');
    const sbSync = document.getElementById('sbSync');
    if (!sbSync) return;

    try {
      const resp = await fetch('/api/health', { method: 'GET', cache: 'no-store' });
      if (resp.ok) {
        if (sbSyncStatus) sbSyncStatus.textContent = 'Port 8080 (Online)';
        sbSync.title = 'Python ব্যাকএন্ড সার্ভার সক্রিয় ও সংযুক্ত';
      }
    } catch (e) {
      if (sbSyncStatus) sbSyncStatus.textContent = 'Offline';
      sbSync.title = 'Python ব্যাকএন্ড ডিসকানেক্টেড';
    }
  }

  function updateDiagnostics() {
    const sbDiag = document.getElementById('sbDiagnostics');
    const sbBadge = document.getElementById('sbDiagBadge');
    if (!sbDiag || !sbBadge) return { errors: 0, warnings: 0, diagnosticNotes: [] };

    const text = editor.value;
    let errors = 0;
    let warnings = 0;
    let diagnosticNotes = [];

    // Check unclosed code blocks ```
    const codeBlockCount = (text.match(/^```/gm) || []).length;
    if (codeBlockCount % 2 !== 0) {
      errors++;
      diagnosticNotes.push("অসম্পূর্ণ কোড ব্লক (Unclosed ``` code block)");
    }

    // Check unclosed display math blocks $$
    const mathBlockCount = (text.match(/\$\$/g) || []).length;
    if (mathBlockCount % 2 !== 0) {
      errors++;
      diagnosticNotes.push("অসম্পূর্ণ ম্যাথ ব্লক (Unclosed $$ math block)");
    }

    // Check broken empty links [text]()
    const emptyLinks = (text.match(/\[[^\]]+\]\(\s*\)/g) || []).length;
    if (emptyLinks > 0) {
      warnings += emptyLinks;
      diagnosticNotes.push(`${emptyLinks}টি খালি লিংক`);
    }

    if (errors > 0) {
      sbBadge.innerHTML = `<span style="color:var(--danger-color); font-weight:bold;">⨂ ${errors}</span>  <span style="color:var(--warning-color);">⚠ ${warnings}</span>`;
      sbDiag.title = `ত্রুটি: ${diagnosticNotes.join(', ')} (ক্লিক করে বিস্তারিত দেখুন)`;
    } else if (warnings > 0) {
      sbBadge.innerHTML = `<span>⨂ 0</span>  <span style="color:var(--warning-color); font-weight:bold;">⚠ ${warnings}</span>`;
      sbDiag.title = `সতর্কতা: ${diagnosticNotes.join(', ')}`;
    } else {
      sbBadge.innerHTML = `<span>⨂ 0  ⚠ 0</span>`;
      sbDiag.title = `কোনো সিনট্যাক্স ত্রুটি নেই (No errors)`;
    }

    return { errors, warnings, diagnosticNotes };
  }

  let currentIndent = 'Spaces: 4';
  function detectIndentation() {
    const text = editor.value;
    const sbIndent = document.getElementById('sbIndent');
    if (/^\t+/m.test(text)) {
      currentIndent = 'Tabs';
    } else if (/^ {2}[^ ]/m.test(text)) {
      currentIndent = 'Spaces: 2';
    } else {
      currentIndent = 'Spaces: 4';
    }
    if (sbIndent) sbIndent.textContent = currentIndent;
  }

  function toggleIndentation() {
    if (currentIndent === 'Spaces: 4') {
      currentIndent = 'Spaces: 2';
    } else if (currentIndent === 'Spaces: 2') {
      currentIndent = 'Tabs';
    } else {
      currentIndent = 'Spaces: 4';
    }
    const sbIndent = document.getElementById('sbIndent');
    if (sbIndent) sbIndent.textContent = currentIndent;
    showToast(`ইন্ডেন্টেশন: ${currentIndent}`, 'info', 1200);
  }

  function detectLineEnding() {
    const isCrlf = editor.value.includes('\r\n');
    const sbLineEnding = document.getElementById('sbLineEnding');
    if (sbLineEnding) sbLineEnding.textContent = isCrlf ? 'CRLF' : 'LF';
    return isCrlf ? 'CRLF' : 'LF';
  }

  function toggleLineEnding() {
    const isCrlf = editor.value.includes('\r\n');
    pushHistoryState(editor.value);
    if (isCrlf) {
      editor.value = editor.value.replace(/\r\n/g, '\n');
      showToast('লাইন এন্ডিং: LF (Unix/Linux/macOS)', 'info', 1200);
    } else {
      editor.value = editor.value.replace(/\n/g, '\r\n');
      showToast('লাইন এন্ডিং: CRLF (Windows)', 'info', 1200);
    }
    detectLineEnding();
    debouncedSaveAllTabs(200);
  }

  // ==================== Line Numbers & Status Bar ====================
  let lastLineCount = -1;
  function updateLineNumbers(force = false) {
    if (!lineNumbers) return;
    const lines = editor.value.split('\n');
    const lineCount = lines.length;
    if (!force && lineCount === lastLineCount) return;
    lastLineCount = lineCount;
    let html = '';
    for (let i = 1; i <= lineCount; i++) {
      html += `<span>${i}</span>`;
    }
    lineNumbers.innerHTML = html;
  }

  let statusDebounceTimer = null;
  function updateStatusBar() {
    const text = editor.value;
    const chars = text.length;

    // Fast cursor position calculation without memory allocation
    const startPos = editor.selectionStart || 0;
    const endPos = editor.selectionEnd || 0;
    const isSelected = startPos !== endPos;
    const selectedCount = Math.abs(endPos - startPos);

    let lineNum = 1;
    let lastNl = -1;
    for (let i = 0; i < startPos; i++) {
      if (text.charCodeAt(i) === 10) {
        lineNum++;
        lastNl = i;
      }
    }
    const colNum = startPos - lastNl;

    if (sbLineCol) {
      sbLineCol.textContent = isSelected
        ? `Ln ${lineNum}, Col ${colNum} (${selectedCount} selected)`
        : `Ln ${lineNum}, Col ${colNum}`;
    }

    // Debounce full-text metrics
    if (statusDebounceTimer) clearTimeout(statusDebounceTimer);
    statusDebounceTimer = setTimeout(() => {
      const words = text.trim() ? text.trim().split(/\s+/).length : 0;
      const lines = text ? (text.match(/\n/g) || []).length + 1 : 0;

      if (sbWordCount) sbWordCount.textContent = `Words: ${words.toLocaleString()}`;

      const wcEl = document.getElementById('wordCount');
      if (wcEl) wcEl.textContent = `${words} words`;
      const ccEl = document.getElementById('charCount');
      if (ccEl) ccEl.textContent = `${chars} chars`;
      const lcEl = document.getElementById('lineCount');
      if (lcEl) lcEl.textContent = `${lines} lines`;

      updateDiagnostics();
      detectLineEnding();
      detectIndentation();
    }, 150);
  }

  // ==================== Resilient File Download Pipeline ====================
  async function triggerDownload(content, filename, mimeType) {
    // 1. If running inside Pywebview Native Window with JS API
    if (window.pywebview && window.pywebview.api && window.pywebview.api.save_file_dialog) {
      try {
        let b64 = '';
        if (typeof content === 'string') {
          b64 = btoa(unescape(encodeURIComponent(content)));
        } else if (content instanceof Blob) {
          b64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.readAsDataURL(content);
          });
        }
        const res = await window.pywebview.api.save_file_dialog(filename, b64);
        if (res && res.success) {
          showToast(`💾 ফাইল সফলভাবে সেভ হয়েছে: ${filename}`, 'success');
          return;
        } else if (res && res.cancelled) {
          return;
        }
      } catch (e) {
        console.warn('Pywebview native save fallback to web download:', e);
      }
    }

    // 2. Browser Blob Download with safe 30s retention
    try {
      const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        if (a.parentNode) a.parentNode.removeChild(a);
        URL.revokeObjectURL(url);
      }, 30000);
      showToast(`📥 ${filename} ডাউনলোড শুরু হয়েছে!`, 'success');
      return;
    } catch (err) {
      console.warn('Blob download error, trying server download endpoint:', err);
    }

    // 3. Server-side Download Fallback
    try {
      const resp = await fetch('/api/download-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: typeof content === 'string' ? content : '',
          filename: filename,
          mime_type: mimeType
        })
      });
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        if (a.parentNode) a.parentNode.removeChild(a);
        URL.revokeObjectURL(url);
      }, 30000);
      showToast(`📥 ${filename} ডাউনলোড সম্পন্ন!`, 'success');
    } catch (e) {
      showToast('❌ ফাইল ডাউনলোড ব্যর্থ হয়েছে', 'error');
    }
  }

  function sanitizeFilename(name) {
    return (name || 'Document').replace(/[\\/:*?"<>|]+/g, '_').trim() || 'Document';
  }

  // ==================== Multi-Format Exporters ====================
  function exportMarkdown() {
    const filename = `${sanitizeFilename(docTitleInput.value)}.md`;
    triggerDownload(editor.value, filename, 'text/markdown;charset=utf-8');
  }

  async function exportDocx() {
    const title = docTitleInput.value.trim() || 'Document';
    const filename = `${sanitizeFilename(title)}.docx`;

    try {
      const resp = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markdown: editor.value, title: title })
      });

      if (!resp.ok) {
        throw new Error('Server returned ' + resp.status);
      }

      const blob = await resp.blob();
      await triggerDownload(blob, filename, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    } catch (err) {
      console.error('DOCX Export error:', err);
      showToast('❌ DOCX এক্সপোর্টের জন্য Python ব্যাকএন্ড চালু থাকতে হবে।', 'error', 3500);
    }
  }

  function exportTxt() {
    const filename = `${sanitizeFilename(docTitleInput.value)}.txt`;
    const text = previewContent.innerText || editor.value;
    triggerDownload(text, filename, 'text/plain;charset=utf-8');
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
      font-family: 'Hind Siliguri', 'Segoe UI', system-ui, sans-serif;
      max-width: 860px;
      margin: 40px auto;
      padding: 0 24px;
      line-height: 1.75;
      color: #1a1a1a;
      background: #ffffff;
    }
    h1, h2, h3 { font-weight: 700; color: #111; }
    h1 { border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
    table { width: 100%; border-collapse: collapse; margin: 1.5em 0; }
    th, td { border: 1px solid #dfe2e5; padding: 8px 14px; text-align: left; }
    th { background: #f6f8fa; }
    pre { background: #f6f8fa; padding: 14px; border-radius: 6px; overflow-x: auto; font-family: Consolas, monospace; }
    code { background: #f0f0f0; padding: 2px 5px; border-radius: 4px; font-family: Consolas, monospace; }
    blockquote { border-left: 4px solid #0078d4; margin: 0; padding-left: 16px; color: #555; }
  </style>
</head>
<body>
${previewContent.innerHTML}
</body>
</html>`;
    triggerDownload(fullHtml, filename, 'text/html;charset=utf-8');
  }

  async function exportPdf() {
    const title = docTitleInput.value.trim() || 'Document';
    const filename = `${sanitizeFilename(title)}.pdf`;
    showToast('⏳ সরাসরি PDF ফাইল তৈরি করা হচ্ছে...', 'info', 3000);

    try {
      const resp = await fetch('/api/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markdown: editor.value, title: title })
      });

      if (resp.ok) {
        const blob = await resp.blob();
        await triggerDownload(blob, filename, 'application/pdf');
        return;
      }
    } catch (err) {
      console.warn('Backend PDF export failed, fallback to window.print():', err);
    }

    // Fallback to browser print dialog
    showToast('🖨️ ব্রাউজার প্রিন্ট ডায়ালগ খোলা হচ্ছে...', 'info', 1500);
    setTimeout(() => {
      window.print();
    }, 300);
  }

  // ==================== Dedicated Export Modal Controller ====================
  function openExportModal() {
    const filenameInput = document.getElementById('exportFilenameInput');
    if (filenameInput) {
      filenameInput.value = docTitleInput.value.trim() || 'Untitled Document';
    }
    exportModal?.classList.add('active');
  }

  function handleExportModalConfirm() {
    const filenameInput = document.getElementById('exportFilenameInput');
    if (filenameInput && filenameInput.value.trim()) {
      docTitleInput.value = filenameInput.value.trim();
      const activeTab = getActiveTab();
      if (activeTab) activeTab.title = docTitleInput.value;
      renderTabs();
    }

    exportModal?.classList.remove('active');

    switch (selectedExportFormat) {
      case 'docx':
        exportDocx();
        break;
      case 'md':
        exportMarkdown();
        break;
      case 'pdf':
        exportPdf();
        break;
      case 'txt':
        exportTxt();
        break;
      case 'html':
        exportHtml();
        break;
      default:
        exportDocx();
    }
  }

  // ==================== File Conversion & Uploads ====================
  async function convertUploadedFile(file) {
    showToast(`⏳ ফাইল লোড হচ্ছে: ${file.name}...`, 'info', 3000);

    if (window.pywebview && window.pywebview.api && window.pywebview.api.convert_file_content) {
      try {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const b64Data = e.target.result.split(',')[1];
          const markdown = await window.pywebview.api.convert_file_content(file.name, b64Data);
          handleConversionResult(file.name, markdown);
        };
        reader.readAsDataURL(file);
        return;
      } catch (err) {
        console.error("Desktop API convert error:", err);
      }
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const openaiKey = localStorage.getItem('markitdown_openai_key');
      const geminiKey = localStorage.getItem('markitdown_gemini_key');
      const model = localStorage.getItem('markitdown_openai_model');

      if (openaiKey) formData.append('openai_api_key', openaiKey);
      if (geminiKey) formData.append('gemini_api_key', geminiKey);
      if (model) formData.append('model', model);

      const resp = await fetch('/api/convert', { method: 'POST', body: formData });
      const data = await resp.json();

      if (data.success) {
        handleConversionResult(file.name, data.markdown);
      } else {
        showToast(`❌ কনভার্সন ব্যর্থ: ${data.error || 'অজানা সমস্যা'}`, 'error', 4000);
      }
    } catch (e) {
      showToast(`❌ সার্ভার কানেকশন ত্রুটি: Python সার্ভার চালু আছে কি না পরীক্ষা করুন।`, 'error', 4000);
    }
  }

  function handleConversionResult(originalFilename, markdown) {
    let finalMarkdown = markdown;
    if (window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown && window.BijoyToUnicode.isLikelyBijoy(finalMarkdown)) {
      finalMarkdown = window.BijoyToUnicode.convertMarkdown(finalMarkdown);
    }

    const title = originalFilename.replace(/\.[^/.]+$/, "");
    createNewTab(title, finalMarkdown);
    closeAllModals();
    showToast(`✅ "${originalFilename}" সফলভাবে রূপান্তর হয়েছে!`, 'success', 3000);
  }

  // ==================== Image OCR ====================
  async function performImageOcr(file) {
    showToast('🔍 ছবি থেকে বাংলা ও ইংরেজি টেক্সট এক্সট্রাক্ট করা হচ্ছে...', 'info', 4000);

    const formData = new FormData();
    formData.append('image', file);
    const key = localStorage.getItem('markitdown_openai_key');
    if (key) formData.append('openai_api_key', key);

    try {
      const resp = await fetch('/api/ocr', { method: 'POST', body: formData });
      const data = await resp.json();

      if (data.success && data.text) {
        let extracted = data.text;
        if (window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown && window.BijoyToUnicode.isLikelyBijoy(extracted)) {
          extracted = window.BijoyToUnicode.convertMarkdown(extracted);
        }

        const title = file.name.replace(/\.[^/.]+$/, "") + " (OCR)";
        createNewTab(title, extracted);
        closeAllModals();
        showToast('✅ ইমেজ থেকে টেক্সট এক্সট্র্যাক্ট সম্পন্ন!', 'success', 3000);
      } else {
        showToast(`❌ OCR ব্যর্থ: ${data.error || 'কোনো লেখা পাওয়া যায়নি'}`, 'error', 4000);
      }
    } catch (e) {
      showToast('❌ OCR সার্ভার কানেকশন ত্রুটি', 'error', 4000);
    }
  }

  // ==================== Bengali ANSI ⇄ Unicode Actions ====================
  function convertAnsiToUnicodeAction() {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const rawVal = editor.value;
    const hasSelection = start !== end;
    const targetText = hasSelection ? rawVal.substring(start, end) : rawVal;

    if (!targetText.trim()) {
      showToast("কোনো টেক্সট পাওয়া যায়নি।", "warning");
      return;
    }

    pushHistoryState(rawVal);

    // Client-side instantaneous conversion without double toasts
    if (window.BijoyToUnicode && window.BijoyToUnicode.convertMarkdown) {
      try {
        const converted = window.BijoyToUnicode.convertMarkdown(targetText);
        if (hasSelection) {
          editor.value = rawVal.substring(0, start) + converted + rawVal.substring(end);
          editor.setSelectionRange(start, start + converted.length);
        } else {
          editor.value = converted;
        }
        setFontMode('unicode');
        renderMarkdown();
        updateLineNumbers();
        updateStatusBar();
        saveAllTabs();
        showToast('✅ বিজয় ➜ ইউনিকোড রূপান্তর সম্পন্ন!', 'success');
        return;
      } catch (err) {
        console.warn("Client conversion error, trying backend:", err);
      }
    }

    // Backend fallback
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
          setFontMode('unicode');
          renderMarkdown();
          updateLineNumbers();
          updateStatusBar();
          saveAllTabs();
          showToast('✅ বিজয় ➜ ইউনিকোড রূপান্তর সম্পন্ন!', 'success');
        }
      })
      .catch(e => {
        showToast('❌ রূপান্তরে সমস্যা হয়েছে', 'error');
      });
  }

  async function convertUnicodeToAnsiAction() {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const rawVal = editor.value;
    const hasSelection = start !== end;
    const targetText = hasSelection ? rawVal.substring(start, end) : rawVal;

    if (!targetText.trim()) {
      showToast("কোনো টেক্সট পাওয়া যায়নি।", "warning");
      return;
    }

    pushHistoryState(rawVal);

    if (window.BijoyToUnicode && window.BijoyToUnicode.convertUnicodeToBijoyMarkdown) {
      try {
        const converted = window.BijoyToUnicode.convertUnicodeToBijoyMarkdown(targetText);
        if (hasSelection) {
          editor.value = rawVal.substring(0, start) + converted + rawVal.substring(end);
          editor.setSelectionRange(start, start + converted.length);
        } else {
          editor.value = converted;
        }
        setFontMode('bijoy');
        renderMarkdown();
        updateLineNumbers();
        updateStatusBar();
        saveAllTabs();
        showToast('✅ ইউনিকোড ➜ বিজয় (ANSI) রূপান্তর সম্পন্ন!', 'success');
        return;
      } catch (err) {
        console.warn("Client Unicode to ANSI error, trying backend:", err);
      }
    }

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
        setFontMode('bijoy');
        renderMarkdown();
        updateLineNumbers();
        updateStatusBar();
        saveAllTabs();
        showToast('✅ ইউনিকোড ➜ বিজয় (ANSI) রূপান্তর সম্পন্ন!', 'success');
      }
    } catch (e) {
      showToast('❌ রূপান্তরে সমস্যা হয়েছে', 'error');
    }
  }

  // ==================== Editor & Preview Utility Actions ====================
  function selectAllAction() {
    editor.focus();
    editor.setSelectionRange(0, editor.value.length);
    showToast('🔘 সমস্ত টেক্সট সিলেক্ট করা হয়েছে', 'info', 1000);
  }

  function copyMarkdownAction(btn = null) {
    editor.focus();
    navigator.clipboard.writeText(editor.value).then(() => {
      showToast('📋 মূল মার্কডাউন সোর্স কপি সম্পন্ন!', 'success', 1500);
    }).catch(() => {
      showToast('❌ ক্লিপবোর্ডে কপি করতে সমস্যা হয়েছে', 'error');
    });
  }

  function copyPreviewTextAction(btn = null) {
    const text = previewContent.innerText;
    navigator.clipboard.writeText(text).then(() => {
      showToast('📋 প্রিভিউ টেক্সট ক্লিপবোর্ডে কপি সম্পন্ন!', 'success', 1500);
    }).catch(() => {
      showToast('❌ কপি করতে সমস্যা হয়েছে', 'error');
    });
  }

  function copyPreviewHtmlAction(btn = null) {
    const html = previewContent.innerHTML;
    navigator.clipboard.writeText(html).then(() => {
      showToast('🌐 প্রিভিউ এইচটিএমএল কপি সম্পন্ন!', 'success', 1500);
    }).catch(() => {
      showToast('❌ কপি করতে সমস্যা হয়েছে', 'error');
    });
  }

  function clearEditorAction() {
    if (!editor.value.trim()) return;
    showConfirmModal("এডিটর ক্লিয়ার", "আপনি কি বর্তমান ডকুমেন্টের সব লেখা মুছে ফেলতে চান?", () => {
      pushHistoryState(editor.value);
      editor.value = '';
      renderMarkdown();
      updateLineNumbers();
      updateStatusBar();
      saveAllTabs();
      showToast('🗑️ সমস্ত টেক্সট মুছে ফেলা হয়েছে (Undo করতে Ctrl+Z চাপুন)', 'info', 2500);
    });
  }

  function refreshPreviewAction() {
    renderMarkdown();
    showToast('🔄 প্রিভিউ রিফ্রেশ সম্পন্ন!', 'info', 1000);
  }

  // ==================== Formatting Toolbar Helpers ====================
  function insertFormatting(prefix, suffix = '', defaultText = '') {
    editor.focus();
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const val = editor.value;

    pushHistoryState(val);

    const selected = val.substring(start, end) || defaultText;
    const replacement = prefix + selected + suffix;

    editor.value = val.substring(0, start) + replacement + val.substring(end);
    const newCursor = start + prefix.length + selected.length;
    editor.setSelectionRange(newCursor, newCursor);

    renderMarkdown();
    updateLineNumbers();
    updateStatusBar();
    saveAllTabs();
  }

  function insertLinePrefix(prefix) {
    editor.focus();
    const start = editor.selectionStart;
    const val = editor.value;

    pushHistoryState(val);

    const lineStart = val.lastIndexOf('\n', start - 1) + 1;
    editor.value = val.substring(0, lineStart) + prefix + val.substring(lineStart);
    editor.setSelectionRange(start + prefix.length, start + prefix.length);

    renderMarkdown();
    updateLineNumbers();
    updateStatusBar();
    saveAllTabs();
  }

  // ==================== View Modes & Zoom ====================
  function setViewMode(mode) {
    const leftPane = document.getElementById('editorPane');
    const rightPane = document.getElementById('previewPane');
    const resizer = document.getElementById('resizer');

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

  function changeFontSize(delta) {
    if (delta === 0) {
      currentFontSize = 13;
    } else {
      currentFontSize = Math.min(28, Math.max(10, currentFontSize + delta));
    }
    editor.style.fontSize = `${currentFontSize}px`;
    previewContent.style.fontSize = `${currentFontSize}px`;
    if (lineNumbers) lineNumbers.style.fontSize = `${currentFontSize}px`;
    localStorage.setItem('markitdown_studio_font_size', currentFontSize);
    showToast(`ফন্ট সাইজ: ${currentFontSize}px`, 'info', 1000);
  }

  function toggleWordWrap() {
    editor.classList.toggle('no-wrap');
    const isNoWrap = editor.classList.contains('no-wrap');
    showToast(isNoWrap ? 'ওয়ার্ড র্র্যাপ বন্ধ' : 'ওয়ার্ড র্র্যাপ চালু', 'info', 1200);
  }

  // ==================== Find & Replace Actions ====================
  function openFindReplaceModal() {
    const findInput = document.getElementById('findInput');
    const selected = editor.value.substring(editor.selectionStart, editor.selectionEnd);
    if (selected) {
      findInput.value = selected;
    }
    findReplaceModal?.classList.add('active');
    findInput?.focus();
    findInput?.select();
  }

  function findNextText() {
    const term = document.getElementById('findInput').value;
    const statsEl = document.getElementById('findStats');
    if (!term) return;

    const val = editor.value;
    const startPos = editor.selectionEnd;
    let idx = val.indexOf(term, startPos);
    if (idx === -1) {
      idx = val.indexOf(term, 0);
    }

    if (idx !== -1) {
      editor.focus();
      editor.setSelectionRange(idx, idx + term.length);
      statsEl.textContent = `ম্যাচ পাওয়া গেছে (অবস্থান: ${idx})`;
    } else {
      statsEl.textContent = `কোনো মিল পাওয়া যায়নি।`;
    }
  }

  function replaceCurrentText() {
    const term = document.getElementById('findInput').value;
    const replacement = document.getElementById('replaceInput').value;
    if (!term) return;

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.substring(start, end);

    if (selected === term) {
      pushHistoryState(editor.value);
      editor.value = editor.value.substring(0, start) + replacement + editor.value.substring(end);
      editor.setSelectionRange(start, start + replacement.length);
      renderMarkdown();
      updateLineNumbers();
      updateStatusBar();
      findNextText();
    } else {
      findNextText();
    }
  }

  function replaceAllText() {
    const term = document.getElementById('findInput').value;
    const replacement = document.getElementById('replaceInput').value;
    const statsEl = document.getElementById('findStats');
    if (!term) return;

    const val = editor.value;
    const count = val.split(term).length - 1;
    if (count > 0) {
      pushHistoryState(editor.value);
      editor.value = val.split(term).join(replacement);
      renderMarkdown();
      updateLineNumbers();
      updateStatusBar();
      statsEl.textContent = `মোট ${count}টি মিল প্রতিস্থাপন করা হয়েছে!`;
      showToast(`মোট ${count}টি প্রতিস্থাপন সম্পন্ন`, 'success');
    } else {
      statsEl.textContent = `কোনো মিল পাওয়া যায়নি।`;
    }
  }

  // ==================== Document Stats Modal ====================
  function showDocStatsModal() {
    const text = editor.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    const lines = text ? text.split('\n').length : 0;
    const sentences = text ? text.split(/[।!?.\n]+/).filter(s => s.trim().length > 0).length : 0;
    const readingMin = Math.max(1, Math.ceil(words / 200));

    document.getElementById('statWords').textContent = words.toLocaleString();
    document.getElementById('statChars').textContent = chars.toLocaleString();
    document.getElementById('statLines').textContent = lines.toLocaleString();
    document.getElementById('statSentences').textContent = sentences.toLocaleString();
    document.getElementById('statReadingTime').textContent = `${readingMin} মিনিট`;

    statsModal?.classList.add('active');
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
    exportDropdown?.classList.remove('show');
    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
  }

  function toggleSidebar() {
    if (!primarySidebar) return;
    primarySidebar.classList.toggle('collapsed');
    const actBtn = document.getElementById('actBarExplorer');
    if (actBtn) {
      actBtn.classList.toggle('active', !primarySidebar.classList.contains('collapsed'));
    }
  }

  // ==================== Synchronized Scrolling ====================
  function setupScrollSync() {
    let activeScroller = null;
    let scrollResetTimer = null;

    editor.addEventListener('scroll', () => {
      // Sync line numbers scroll immediately
      if (lineNumbers) {
        lineNumbers.scrollTop = editor.scrollTop;
      }

      if (activeScroller && activeScroller !== 'editor') return;
      activeScroller = 'editor';
      if (scrollResetTimer) clearTimeout(scrollResetTimer);
      scrollResetTimer = setTimeout(() => { activeScroller = null; }, 100);

      window.requestAnimationFrame(() => {
        const maxScroll = editor.scrollHeight - editor.clientHeight;
        const pct = maxScroll > 0 ? editor.scrollTop / maxScroll : 0;
        const previewMax = preview.scrollHeight - preview.clientHeight;
        preview.scrollTop = pct * previewMax;
      });
    }, { passive: true });

    preview.addEventListener('scroll', () => {
      if (activeScroller && activeScroller !== 'preview') return;
      activeScroller = 'preview';
      if (scrollResetTimer) clearTimeout(scrollResetTimer);
      scrollResetTimer = setTimeout(() => { activeScroller = null; }, 100);

      window.requestAnimationFrame(() => {
        const previewMax = preview.scrollHeight - preview.clientHeight;
        const pct = previewMax > 0 ? preview.scrollTop / previewMax : 0;
        const editorMax = editor.scrollHeight - editor.clientHeight;
        editor.scrollTop = pct * editorMax;
        if (lineNumbers) {
          lineNumbers.scrollTop = editor.scrollTop;
        }
      });
    }, { passive: true });
  }

  // ==================== Debounced Rendering & Auto-save ====================
  let renderDebounceTimer = null;
  let saveDebounceTimer = null;

  function debouncedRenderMarkdown(delay = 140) {
    if (renderDebounceTimer) clearTimeout(renderDebounceTimer);
    renderDebounceTimer = setTimeout(() => {
      renderMarkdown();
    }, delay);
  }

  function debouncedSaveAllTabs(delay = 400) {
    if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
    saveDebounceTimer = setTimeout(() => {
      saveAllTabs();
    }, delay);
  }

  // ==================== DropZone Setup Helper ====================
  function setupDropZone(dropZoneId, inputId, handler) {
    const dz = document.getElementById(dropZoneId);
    const fi = document.getElementById(inputId);
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

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
  }

  // ==================== Event Listeners ====================
  
  // ==================== Zen Mode & Distraction-Free Controller ====================
  function toggleZenMode() {
    const isZen = document.body.classList.toggle('zen-mode');
    const zenBtn = document.getElementById('toolZenMode');
    if (zenBtn) {
      zenBtn.classList.toggle('active', isZen);
    }
    showToast(isZen ? '🧘 জেন মোড চালু (Esc দিয়ে বের হতে পারেন)' : 'জেন মোড বন্ধ', 'info', 2000);
  }

  // ==================== Built-in Avro Phonetic Controller ====================
  function togglePhoneticMode() {
    if (!window.PhoneticBangla) {
      showToast('⚠️ ফোনেটিক ইঞ্জিন লোড হয়নি', 'warning');
      return;
    }
    const enabled = window.PhoneticBangla.toggle();
    const btn = document.getElementById('toolPhoneticBangla');
    if (btn) {
      btn.classList.toggle('active-phonetic', enabled);
      btn.innerHTML = enabled ? '<span class="tool-icon">অ</span> ফোনেটিক: অন' : '<span class="tool-icon">অ</span> ফোনেটিক: অফ';
    }
    showToast(enabled ? 'অ আ ফোনেটিক বাংলা: চালু (Ctrl+M দিয়ে টগল করুন)' : 'ফোনেটিক বাংলা: বন্ধ', enabled ? 'success' : 'info', 2000);
  }

  // ==================== Smart Editor Productivity Engine ====================
  function initSmartEditor() {
    if (!editor) return;

    editor.addEventListener('keydown', handleEditorKeyDown);
    editor.addEventListener('paste', handleEditorPaste);

    editor.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
      editor.classList.add('dragover');
    });

    editor.addEventListener('dragleave', (e) => {
      e.preventDefault();
      e.stopPropagation();
      editor.classList.remove('dragover');
    });

    editor.addEventListener('drop', handleEditorDrop);
  }

  function handleEditorKeyDown(e) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const val = editor.value;

    // --- 1. Phonetic Typing Handler ---
    if (window.PhoneticBangla && window.PhoneticBangla.isEnabled) {
      if ([' ', 'Enter', 'Tab', ',', '.', ';', '?', '!', ':', '\n'].includes(e.key) && !e.ctrlKey && !e.altKey && !e.metaKey) {
        if (start === end) {
          const textBeforeCursor = val.substring(0, start);
          const match = textBeforeCursor.match(/([a-zA-Z0-9`^]+)$/);
          if (match) {
            const word = match[1];
            const wordStart = start - word.length;
            const converted = window.PhoneticBangla.parse(word);
            if (converted && converted !== word) {
              e.preventDefault();
              pushHistoryState(val);
              const keyToInsert = e.key === 'Enter' ? '\n' : (e.key === 'Tab' ? '    ' : e.key);
              editor.value = val.substring(0, wordStart) + converted + keyToInsert + val.substring(end);
              const newPos = wordStart + converted.length + keyToInsert.length;
              editor.setSelectionRange(newPos, newPos);
              debouncedRenderMarkdown(50);
              updateLineNumbers();
              updateStatusBar();
              debouncedSaveAllTabs(300);
              return;
            }
          }
        }
      }
    }

    // --- 2. Tab & Shift+Tab Indentation ---
    if (e.key === 'Tab') {
      e.preventDefault();
      pushHistoryState(val);

      if (start === end) {
        if (!e.shiftKey) {
          editor.value = val.substring(0, start) + '    ' + val.substring(end);
          editor.setSelectionRange(start + 4, start + 4);
        } else {
          const lineStart = val.lastIndexOf('\n', start - 1) + 1;
          const linePrefix = val.substring(lineStart, lineStart + 4);
          const spacesToRemove = linePrefix.match(/^ {1,4}/);
          if (spacesToRemove) {
            const count = spacesToRemove[0].length;
            editor.value = val.substring(0, lineStart) + val.substring(lineStart + count);
            const newCursor = Math.max(lineStart, start - count);
            editor.setSelectionRange(newCursor, newCursor);
          }
        }
      } else {
        const lineStart = val.lastIndexOf('\n', start - 1) + 1;
        let lineEnd = val.indexOf('\n', end);
        if (lineEnd === -1) lineEnd = val.length;

        const selectedLines = val.substring(lineStart, lineEnd).split('\n');
        let modifiedLines;
        let charsDelta = 0;

        if (!e.shiftKey) {
          modifiedLines = selectedLines.map(l => {
            charsDelta += 4;
            return '    ' + l;
          });
        } else {
          modifiedLines = selectedLines.map(l => {
            const m = l.match(/^ {1,4}/);
            if (m) {
              charsDelta -= m[0].length;
              return l.substring(m[0].length);
            }
            return l;
          });
        }

        editor.value = val.substring(0, lineStart) + modifiedLines.join('\n') + val.substring(lineEnd);
        editor.setSelectionRange(lineStart, Math.max(lineStart, end + charsDelta));
      }

      debouncedRenderMarkdown(50);
      updateLineNumbers();
      updateStatusBar();
      debouncedSaveAllTabs(300);
      return;
    }

    // --- 3. Auto-Pairing & Selection Wrapping ---
    const pairs = {
      '(': ')',
      '[': ']',
      '{': '}',
      '"': '"',
      "'": "'",
      '`': '`',
      '*': '*',
      '_': '_',
      '~': '~'
    };

    if (pairs[e.key] && !e.ctrlKey && !e.altKey && !e.metaKey) {
      const openChar = e.key;
      const closeChar = pairs[openChar];

      if (start !== end) {
        e.preventDefault();
        pushHistoryState(val);
        const selectedText = val.substring(start, end);
        const wrapped = openChar + selectedText + closeChar;
        editor.value = val.substring(0, start) + wrapped + val.substring(end);
        editor.setSelectionRange(start + 1, start + 1 + selectedText.length);
        debouncedRenderMarkdown(50);
        updateLineNumbers();
        updateStatusBar();
        debouncedSaveAllTabs(300);
        return;
      } else {
        const nextChar = val.charAt(start);
        if (Object.values(pairs).includes(openChar) && nextChar === openChar) {
          e.preventDefault();
          editor.setSelectionRange(start + 1, start + 1);
          return;
        }

        if (['(', '[', '{', '`'].includes(openChar)) {
          e.preventDefault();
          pushHistoryState(val);
          editor.value = val.substring(0, start) + openChar + closeChar + val.substring(end);
          editor.setSelectionRange(start + 1, start + 1);
          debouncedRenderMarkdown(50);
          updateLineNumbers();
          updateStatusBar();
          debouncedSaveAllTabs(300);
          return;
        }
      }
    }

    // --- 4. Backspace between empty pairs deletes both ---
    if (e.key === 'Backspace' && start === end && start > 0) {
      const prevChar = val.charAt(start - 1);
      const nextChar = val.charAt(start);
      if (pairs[prevChar] === nextChar) {
        e.preventDefault();
        pushHistoryState(val);
        editor.value = val.substring(0, start - 1) + val.substring(start + 1);
        editor.setSelectionRange(start - 1, start - 1);
        debouncedRenderMarkdown(50);
        updateLineNumbers();
        updateStatusBar();
        debouncedSaveAllTabs(300);
        return;
      }
    }

    // --- 5. Smart List Continuation on Enter ---
    if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
      if (start === end) {
        const lineStart = val.lastIndexOf('\n', start - 1) + 1;
        const currentLine = val.substring(lineStart, start);

        // Task list
        const taskMatch = currentLine.match(/^(\s*)([-*+])\s+\[([ xX])\]\s*(.*)$/);
        if (taskMatch) {
          e.preventDefault();
          pushHistoryState(val);
          const indent = taskMatch[1];
          const marker = taskMatch[2];
          const text = taskMatch[4];

          if (!text.trim()) {
            editor.value = val.substring(0, lineStart) + val.substring(start);
            editor.setSelectionRange(lineStart, lineStart);
          } else {
            const nextItem = '\n' + indent + marker + ' [ ] ';
            editor.value = val.substring(0, start) + nextItem + val.substring(end);
            editor.setSelectionRange(start + nextItem.length, start + nextItem.length);
          }
          debouncedRenderMarkdown(50);
          updateLineNumbers();
          updateStatusBar();
          debouncedSaveAllTabs(300);
          return;
        }

        // Numbered list
        const numMatch = currentLine.match(/^(\s*)(\d+)\.\s*(.*)$/);
        if (numMatch) {
          e.preventDefault();
          pushHistoryState(val);
          const indent = numMatch[1];
          const num = parseInt(numMatch[2], 10);
          const text = numMatch[3];

          if (!text.trim()) {
            editor.value = val.substring(0, lineStart) + val.substring(start);
            editor.setSelectionRange(lineStart, lineStart);
          } else {
            const nextItem = '\n' + indent + (num + 1) + '. ';
            editor.value = val.substring(0, start) + nextItem + val.substring(end);
            editor.setSelectionRange(start + nextItem.length, start + nextItem.length);
          }
          debouncedRenderMarkdown(50);
          updateLineNumbers();
          updateStatusBar();
          debouncedSaveAllTabs(300);
          return;
        }

        // Bullet list
        const bulletMatch = currentLine.match(/^(\s*)([-*+])\s*(.*)$/);
        if (bulletMatch) {
          e.preventDefault();
          pushHistoryState(val);
          const indent = bulletMatch[1];
          const marker = bulletMatch[2];
          const text = bulletMatch[3];

          if (!text.trim()) {
            editor.value = val.substring(0, lineStart) + val.substring(start);
            editor.setSelectionRange(lineStart, lineStart);
          } else {
            const nextItem = '\n' + indent + marker + ' ';
            editor.value = val.substring(0, start) + nextItem + val.substring(end);
            editor.setSelectionRange(start + nextItem.length, start + nextItem.length);
          }
          debouncedRenderMarkdown(50);
          updateLineNumbers();
          updateStatusBar();
          debouncedSaveAllTabs(300);
          return;
        }
      }
    }
  }

  function handleEditorPaste(e) {
    if (!e.clipboardData || !e.clipboardData.items) return;

    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf('image') !== -1) {
        e.preventDefault();
        const file = item.getAsFile();
        if (file) {
          insertImageAsBase64(file);
        }
        return;
      }
    }
  }

  function handleEditorDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    editor.classList.remove('dragover');

    if (!e.dataTransfer || !e.dataTransfer.files) return;
    const files = e.dataTransfer.files;
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.type.startsWith('image/')) {
        insertImageAsBase64(file);
        return;
      }
    }
  }

  function insertImageAsBase64(file) {
    showToast('⏳ ইমেজ প্রসেস করা হচ্ছে...', 'info', 1500);
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64Data = event.target.result;
      const start = editor.selectionStart || editor.value.length;
      const end = editor.selectionEnd || editor.value.length;
      const val = editor.value;

      pushHistoryState(val);
      const imgTag = `\n\n![${file.name || 'Image'}](${base64Data})\n\n`;
      editor.value = val.substring(0, start) + imgTag + val.substring(end);
      editor.setSelectionRange(start + imgTag.length, start + imgTag.length);

      renderMarkdown();
      updateLineNumbers();
      updateStatusBar();
      debouncedSaveAllTabs(300);
      showToast('🖼️ ইমেজ সফলভাবে ইনসার্ট হয়েছে!', 'success', 3000);
    };
    reader.readAsDataURL(file);
  }

  
  // ==================== Batch Convert Controller ====================
  async function batchConvertFiles(files) {
    if (!files || files.length === 0) return;
    const total = files.length;
    showToast(`⏳ ফাইল কনভার্সন হচ্ছে: 1/${total}...`, 'info', 3000);
    const batchId = 'batch_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
    const formData = new FormData();
    formData.append('batch_id', batchId);
    for (let i = 0; i < total; i++) {
      formData.append('files', files[i]);
    }

    const pollTimer = setInterval(async () => {
      try {
        const pResp = await fetch(`/api/batch-progress/${batchId}`);
        if (pResp.ok) {
          const prog = await pResp.json();
          if (prog && prog.total > 0 && prog.current > 0) {
            showToast(`⏳ ফাইল কনভার্সন হচ্ছে: ${prog.current}/${prog.total}...`, 'info', 2000);
          }
        }
      } catch (_) {}
    }, 400);

    try {
      const resp = await fetch('/api/batch-convert', {
        method: 'POST',
        headers: {
          'X-Batch-Id': batchId
        },
        body: formData
      });

      clearInterval(pollTimer);

      if (resp.ok) {
        const blob = await resp.blob();
        await triggerDownload(blob, 'markitdown_batch_converted.zip', 'application/zip');
        closeAllModals();
        showToast(`✅ ${total}টি ফাইলের কনভার্সন সম্পন্ন! ZIP ডাউনলোড হয়েছে।`, 'success', 4000);
      } else {
        const data = await resp.json();
        showToast(`❌ ব্যাচ কনভার্সন ব্যর্থ: ${data.error || 'অজানা ত্রুটি'}`, 'error', 4000);
      }
    } catch (e) {
      clearInterval(pollTimer);
      showToast('❌ ব্যাচ কনভার্সন সার্ভার এরর', 'error', 4000);
    }
  }

  // ==================== Presentation / Slideshow Controller ====================
  let presentationSlides = [];
  let currentSlideIndex = 0;

  function openPresentationMode() {
    const raw = editor.value || '';
    let slides = raw.split(/\n\s*[-*_]{3,}\s*\n/).map(s => s.trim()).filter(Boolean);

    if (slides.length <= 1) {
      const parts = raw.split(/(?=\n# )/);
      if (parts.length > 1) {
        slides = parts.map(s => s.trim()).filter(Boolean);
      }
    }

    if (slides.length === 0) {
      slides = [raw || '# Untitled Slide\n\nType content separated by `---` to create slides.'];
    }

    presentationSlides = slides;
    currentSlideIndex = 0;

    const overlay = document.getElementById('presentationOverlay');
    if (overlay) {
      overlay.classList.add('active');
      renderCurrentSlide();
    }
    showToast('📽️ প্রেজেন্টেশন মোড চালু (Arrow keys বা Space দিয়ে নেভিগেট করুন, Esc দিয়ে এক্সিট)', 'info', 2500);
  }

  function closePresentationMode() {
    const overlay = document.getElementById('presentationOverlay');
    if (overlay) {
      overlay.classList.remove('active');
    }
  }

  function renderCurrentSlide() {
    const contentEl = document.getElementById('presSlideContent');
    const counterEl = document.getElementById('presSlideCounter');
    const progressBar = document.getElementById('presProgressBar');

    if (!contentEl) return;
    const slideText = presentationSlides[currentSlideIndex] || '';

    let html = '';
    if (window.marked) {
      html = marked.parse(slideText, { gfm: true, breaks: true });
    } else {
      html = `<pre>${escapeHtml(slideText)}</pre>`;
    }

    // Restore KaTeX if available
    html = html.replace(/\$\$([\s\S]+?)\$\$/g, (m, f) => {
      try { return katex.renderToString(f, { displayMode: true, throwOnError: false }); }
      catch(e) { return m; }
    });
    html = html.replace(/\$([^\$\n]+?)\$/g, (m, f) => {
      try { return katex.renderToString(f, { displayMode: false, throwOnError: false }); }
      catch(e) { return m; }
    });

    contentEl.innerHTML = html;

    if (counterEl) {
      counterEl.textContent = `Slide ${currentSlideIndex + 1} / ${presentationSlides.length}`;
    }

    if (progressBar) {
      const pct = ((currentSlideIndex + 1) / presentationSlides.length) * 100;
      progressBar.style.width = `${pct}%`;
    }
  }

  function nextSlide() {
    if (currentSlideIndex < presentationSlides.length - 1) {
      currentSlideIndex++;
      renderCurrentSlide();
    }
  }

  function prevSlide() {
    if (currentSlideIndex > 0) {
      currentSlideIndex--;
      renderCurrentSlide();
    }
  }

  // ==================== Visual Table Assistant Controller ====================
  let assistantRows = 3;
  let assistantCols = 3;

  function openTableAssistant() {
    const modal = document.getElementById('tableAssistantModal');
    if (!modal) return;
    renderTableGrid();
    modal.classList.add('active');
  }

  function renderTableGrid() {
    const container = document.getElementById('tableGridContainer');
    if (!container) return;

    let html = '<table class="assistant-table"><thead><tr>';
    for (let c = 0; c < assistantCols; c++) {
      html += `<th><input type="text" class="table-cell-input tbl-header-cell" value="কলাম ${c + 1}" placeholder="Header ${c + 1}"></th>`;
    }
    html += '</tr></thead><tbody>';

    for (let r = 0; r < assistantRows; r++) {
      html += '<tr>';
      for (let c = 0; c < assistantCols; c++) {
        html += `<td><input type="text" class="table-cell-input tbl-data-cell" placeholder="তথ্য ${r + 1},${c + 1}"></td>`;
      }
      html += '</tr>';
    }
    html += '</tbody></table>';
    container.innerHTML = html;
  }

  function insertGeneratedTable() {
    const container = document.getElementById('tableGridContainer');
    if (!container) return;

    const headers = Array.from(container.querySelectorAll('.tbl-header-cell')).map(i => i.value.trim() || 'Col');
    const rows = [];
    const dataInputs = Array.from(container.querySelectorAll('.tbl-data-cell'));

    for (let r = 0; r < assistantRows; r++) {
      const rowVals = [];
      for (let c = 0; c < assistantCols; c++) {
        const val = dataInputs[r * assistantCols + c]?.value.trim() || '-';
        rowVals.push(val);
      }
      rows.push(rowVals);
    }

    let mdTable = '\n\n| ' + headers.join(' | ') + ' |\n';
    mdTable += '| ' + headers.map(() => ':---').join(' | ') + ' |\n';
    rows.forEach(r => {
      mdTable += '| ' + r.join(' | ') + ' |\n';
    });
    mdTable += '\n';

    const start = editor.selectionStart || editor.value.length;
    const end = editor.selectionEnd || editor.value.length;
    const val = editor.value;

    pushHistoryState(val);
    editor.value = val.substring(0, start) + mdTable + val.substring(end);
    editor.setSelectionRange(start + mdTable.length, start + mdTable.length);

    document.getElementById('tableAssistantModal')?.classList.remove('active');
    debouncedRenderMarkdown(50);
    updateLineNumbers();
    updateStatusBar();
    debouncedSaveAllTabs(300);
    showToast('⊞ টেবিল সফলভাবে ইনসার্ট হয়েছে!', 'success', 2500);
  }

  // ==================== Workspace Folder Explorer ====================
  async function openWorkspaceFolder() {
    if (!window.showDirectoryPicker) {
      showToast('⚠️ এই ব্রাউজারে ফোল্ডার এক্সেস অনুমোদিত নয়। Chrome / Edge ব্যবহার করুন।', 'warning', 3000);
      return;
    }

    try {
      const dirHandle = await window.showDirectoryPicker();
      const folderList = document.getElementById('sidebarFolderList');
      if (!folderList) return;

      folderList.innerHTML = '<div style="padding: 6px 12px; font-size: 11px; color: var(--text-secondary);">লোড হচ্ছে...</div>';
      const files = [];

      for await (const entry of dirHandle.values()) {
        if (entry.kind === 'file' && (entry.name.endsWith('.md') || entry.name.endsWith('.txt') || entry.name.endsWith('.markdown'))) {
          files.push(entry);
        }
      }

      if (files.length === 0) {
        folderList.innerHTML = '<div style="padding: 6px 12px; font-size: 11px; color: var(--text-secondary); font-style: italic;">ফোল্ডারে কোনো .md ফাইল পাওয়া যায়নি</div>';
        return;
      }

      folderList.innerHTML = '';
      files.forEach(fileHandle => {
        const item = document.createElement('div');
        item.className = 'sidebar-file-item';
        item.innerHTML = `<span>📄</span> <span style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(fileHandle.name)}</span>`;
        item.addEventListener('click', async () => {
          const file = await fileHandle.getFile();
          const content = await file.text();
          const title = fileHandle.name.replace(/\.[^/.]+$/, '');
          createNewTab(title, content);
          document.querySelectorAll('.sidebar-file-item').forEach(i => i.classList.remove('active'));
          item.classList.add('active');
        });
        folderList.appendChild(item);
      });

      showToast(`📁 "${dirHandle.name}" ফোল্ডার থেকে ${files.length}টি ফাইল লোড হয়েছে!`, 'success', 3000);
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.warn('Directory picker error:', err);
      }
    }
  }

  function setupEventListeners() {
    // Editor inputs (Optimized: 60fps typing with non-blocking debounced rendering)
    editor.addEventListener('input', () => {
      setSaveStatus('dirty');
      updateLineNumbers();
      updateStatusBar();
      debouncedRenderMarkdown(140);
      debouncedSaveAllTabs(400);
    });

    editor.addEventListener('keyup', updateStatusBar);
    editor.addEventListener('click', updateStatusBar);
    editor.addEventListener('select', updateStatusBar);

    // Tab bar additions
    document.getElementById('newTabBtn')?.addEventListener('click', () => createNewTab());
    document.getElementById('sidebarNewDocBtn')?.addEventListener('click', () => createNewTab());

    // Document renaming
    docTitleInput.addEventListener('input', () => {
      const activeTab = getActiveTab();
      if (activeTab) {
        activeTab.title = docTitleInput.value.trim() || 'Untitled Document';
        if (breadcrumbCurrentDoc) {
          breadcrumbCurrentDoc.textContent = `${activeTab.title}.md`;
        }
        updateBranchStatus(true);
        renderTabs();
        debouncedSaveAllTabs(300);
      }
    });

    // Presentation / Slideshow bindings
    document.getElementById('toolSlides')?.addEventListener('click', openPresentationMode);
    document.getElementById('menuToggleSlides')?.addEventListener('click', openPresentationMode);
    document.getElementById('presExitBtn')?.addEventListener('click', closePresentationMode);
    document.getElementById('presNextBtn')?.addEventListener('click', nextSlide);
    document.getElementById('presPrevBtn')?.addEventListener('click', prevSlide);

    // Table Assistant bindings
    document.getElementById('tblApplySizeBtn')?.addEventListener('click', () => {
      assistantRows = Math.max(1, Math.min(20, parseInt(document.getElementById('tblRowsInput').value, 10) || 3));
      assistantCols = Math.max(1, Math.min(10, parseInt(document.getElementById('tblColsInput').value, 10) || 3));
      renderTableGrid();
    });
    document.getElementById('tblAddRowBtn')?.addEventListener('click', () => {
      if (assistantRows < 20) { assistantRows++; renderTableGrid(); }
    });
    document.getElementById('tblDelRowBtn')?.addEventListener('click', () => {
      if (assistantRows > 1) { assistantRows--; renderTableGrid(); }
    });
    document.getElementById('tblAddColBtn')?.addEventListener('click', () => {
      if (assistantCols < 10) { assistantCols++; renderTableGrid(); }
    });
    document.getElementById('tblDelColBtn')?.addEventListener('click', () => {
      if (assistantCols > 1) { assistantCols--; renderTableGrid(); }
    });
    document.getElementById('insertTableToEditorBtn')?.addEventListener('click', insertGeneratedTable);

    // Workspace Folder bindings
    document.getElementById('sidebarOpenFolderBtn')?.addEventListener('click', openWorkspaceFolder);
    document.getElementById('menuOpenFolder')?.addEventListener('click', openWorkspaceFolder);

    // Multi-file batch convert hook on importFileInput
    const importFileInputEl = document.getElementById('importFileInput');
    if (importFileInputEl) {
      importFileInputEl.addEventListener('change', () => {
        if (importFileInputEl.files && importFileInputEl.files.length > 1) {
          batchConvertFiles(importFileInputEl.files);
        }
      });
    }

    // Formatting Toolbar Buttons
    document.getElementById('toolBold')?.addEventListener('click', () => insertFormatting('**', '**', 'bold text'));
    document.getElementById('toolItalic')?.addEventListener('click', () => insertFormatting('*', '*', 'italic text'));
    document.getElementById('toolStrike')?.addEventListener('click', () => insertFormatting('~~', '~~', 'strikethrough'));
    document.getElementById('toolH1')?.addEventListener('click', () => insertLinePrefix('# '));
    document.getElementById('toolH2')?.addEventListener('click', () => insertLinePrefix('## '));
    document.getElementById('toolH3')?.addEventListener('click', () => insertLinePrefix('### '));
    document.getElementById('toolCode')?.addEventListener('click', () => insertFormatting('`', '`', 'code'));
    document.getElementById('toolCodeBlock')?.addEventListener('click', () => insertFormatting('```\n', '\n```', 'code block'));
    document.getElementById('toolQuote')?.addEventListener('click', () => insertLinePrefix('> '));
    document.getElementById('toolUl')?.addEventListener('click', () => insertLinePrefix('- '));
    document.getElementById('toolOl')?.addEventListener('click', () => insertLinePrefix('1. '));
    document.getElementById('toolTask')?.addEventListener('click', () => insertLinePrefix('- [ ] '));
    document.getElementById('toolTable')?.addEventListener('click', openTableAssistant);
    document.getElementById('toolMath')?.addEventListener('click', () => insertFormatting('$$\n', '\n$$', 'E = mc^2'));
    document.getElementById('toolMermaid')?.addEventListener('click', () => insertFormatting('```mermaid\ngraph TD\n    A[শুরু] --> B[শেষ]\n```\n'));

    // Bengali conversion
    document.getElementById('toolAnsiToUnicode')?.addEventListener('click', convertAnsiToUnicodeAction);
    document.getElementById('toolUnicodeToAnsi')?.addEventListener('click', convertUnicodeToAnsiAction);
    document.getElementById('menuAnsiToUnicode')?.addEventListener('click', convertAnsiToUnicodeAction);
    document.getElementById('menuUnicodeToAnsi')?.addEventListener('click', convertUnicodeToAnsiAction);

    // Toolbar utilities
    document.getElementById('toolUndo')?.addEventListener('click', undo);
    document.getElementById('toolRedo')?.addEventListener('click', redo);
    document.getElementById('toolRefresh')?.addEventListener('click', refreshPreviewAction);
    document.getElementById('toolSelectAll')?.addEventListener('click', selectAllAction);
    document.getElementById('toolCopy')?.addEventListener('click', () => copyMarkdownAction());
    document.getElementById('toolClear')?.addEventListener('click', clearEditorAction);

    // Pane Header Buttons
    document.getElementById('editorWordWrapBtn')?.addEventListener('click', toggleWordWrap);
    document.getElementById('paneRefreshBtn')?.addEventListener('click', refreshPreviewAction);

    // Export Dropdown & Modal triggers
    const exportDropdownBtn = document.getElementById('exportDropdownBtn');
    exportDropdownBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      openExportModal();
    });

    // Format selection cards in Export Modal
    document.querySelectorAll('.format-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('.format-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        selectedExportFormat = card.dataset.format || 'docx';
      });
    });

    document.getElementById('confirmExportBtn')?.addEventListener('click', handleExportModalConfirm);

    // Direct export dropdown items
    document.getElementById('exportDocxBtn')?.addEventListener('click', exportDocx);
    document.getElementById('exportMdBtn')?.addEventListener('click', exportMarkdown);
    document.getElementById('exportPdfBtn')?.addEventListener('click', exportPdf);
    document.getElementById('exportTxtBtn')?.addEventListener('click', exportTxt);
    document.getElementById('exportHtmlBtn')?.addEventListener('click', exportHtml);

    // Activity bar buttons
    document.getElementById('actBarExplorer')?.addEventListener('click', toggleSidebar);
    document.getElementById('sidebarCollapseBtn')?.addEventListener('click', toggleSidebar);
    document.getElementById('actBarActions')?.addEventListener('click', openExportModal);
    document.getElementById('actBarBengali')?.addEventListener('click', convertAnsiToUnicodeAction);
    document.getElementById('actBarSettings')?.addEventListener('click', () => settingsModal?.classList.add('active'));
    document.getElementById('actBarHelp')?.addEventListener('click', () => shortcutsModal?.classList.add('active'));
    document.getElementById('actBarProfile')?.addEventListener('click', () => {
      showToast('👤 Contributor & Author: Syed Ariful Islam Emon (syedarifulislamemon2010)', 'info', 3000);
    });

    // Smart Editor Engine initialization
    initSmartEditor();

    // Zen Mode bindings
    document.getElementById('toolZenMode')?.addEventListener('click', toggleZenMode);
    document.getElementById('menuToggleZen')?.addEventListener('click', toggleZenMode);
    document.getElementById('zenExitBtn')?.addEventListener('click', toggleZenMode);

    // Phonetic Bangla bindings
    document.getElementById('toolPhoneticBangla')?.addEventListener('click', togglePhoneticMode);
    document.getElementById('menuTogglePhonetic')?.addEventListener('click', togglePhoneticMode);

    // Top Header Buttons
    document.getElementById('importDocBtn')?.addEventListener('click', () => importModal?.classList.add('active'));
    document.getElementById('ocrImgBtn')?.addEventListener('click', () => ocrModal?.classList.add('active'));
    document.getElementById('themeToggleBtn')?.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
    document.getElementById('settingsBtn')?.addEventListener('click', () => {
      document.getElementById('openaiKeyInput').value = localStorage.getItem('markitdown_openai_key') || '';
      const geminiInput = document.getElementById('geminiKeyInput');
      if (geminiInput) geminiInput.value = localStorage.getItem('markitdown_gemini_key') || '';
      document.getElementById('openaiModelSelect').value = localStorage.getItem('markitdown_openai_model') || 'gpt-4o';
      settingsModal?.classList.add('active');
    });

    document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
      const key = document.getElementById('openaiKeyInput').value.trim();
      const gemini = document.getElementById('geminiKeyInput').value.trim();
      const model = document.getElementById('openaiModelSelect').value;
      localStorage.setItem('markitdown_openai_key', key);
      localStorage.setItem('markitdown_gemini_key', gemini);
      localStorage.setItem('markitdown_openai_model', model);
      closeAllModals();
      showToast('⚙️ সেটিংস ও API Key সফলভাবে সেভ হয়েছে!', 'success');
    });

    // Modal close handlers
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
      btn.addEventListener('click', closeAllModals);
    });

    // Find & Replace
    document.getElementById('findNextBtn')?.addEventListener('click', findNextText);
    document.getElementById('replaceBtn')?.addEventListener('click', replaceCurrentText);
    document.getElementById('replaceAllBtn')?.addEventListener('click', replaceAllText);

    // Dropzones in Modals
    setupDropZone('importDropZone', 'importFileInput', convertUploadedFile);
    setupDropZone('ocrDropZone', 'ocrFileInput', performImageOcr);

    // Global drag & drop
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

    // Menubar Setup
    setupMenuBar();

    // Resizer Divider
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
      const offset = e.clientX - containerRect.left;
      const minWidth = 260;
      const maxWidth = containerRect.width - minWidth;
      if (offset > minWidth && offset < maxWidth) {
        const pct = (offset / containerRect.width) * 100;
        leftPane.style.flex = `0 0 ${pct}%`;
        document.getElementById('previewPane').style.flex = `0 0 ${100 - pct}%`;
      }
    });

    window.addEventListener('mouseup', () => {
      if (isResizing) {
        isResizing = false;
        resizer?.classList.remove('dragging');
      }
    });

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'n' || e.key === 'N') {
          e.preventDefault();
          createNewTab();
        } else if (e.key === 'w' || e.key === 'W') {
          e.preventDefault();
          closeTab(activeTabId);
        } else if (e.key === 'o' || e.key === 'O') {
          e.preventDefault();
          importModal?.classList.add('active');
        } else if (e.key === 's' || e.key === 'S') {
          e.preventDefault();
          exportMarkdown();
        } else if (e.key === 'p' || e.key === 'P') {
          e.preventDefault();
          exportPdf();
        } else if (e.key === 'z' || e.key === 'Z') {
          if (e.shiftKey) {
            e.preventDefault();
            redo();
          } else {
            e.preventDefault();
            undo();
          }
        } else if (e.key === 'y' || e.key === 'Y') {
          e.preventDefault();
          redo();
        } else if (e.key === 'f' || e.key === 'F') {
          e.preventDefault();
          openFindReplaceModal();
        } else if (e.key === 'b' || e.key === 'B') {
          e.preventDefault();
          insertFormatting('**', '**', 'bold text');
        } else if (e.key === 'i' || e.key === 'I') {
          e.preventDefault();
          insertFormatting('*', '*', 'italic text');
        } else if (e.key === '=' || e.key === '+') {
          e.preventDefault();
          changeFontSize(2);
        } else if (e.key === '-' || e.key === '_') {
          e.preventDefault();
          changeFontSize(-2);
        } else if (e.key === '0') {
          e.preventDefault();
          changeFontSize(0);
        } else if (e.key === 'm' || e.key === 'M') {
          e.preventDefault();
          togglePhoneticMode();
        }
      } else if (e.key === 'F10') {
        e.preventDefault();
        openPresentationMode();
      } else if (e.key === 'F11') {
        e.preventDefault();
        toggleZenMode();
      } else if (e.key === 'Escape') {
        const presOverlay = document.getElementById('presentationOverlay');
        if (presOverlay && presOverlay.classList.contains('active')) {
          e.preventDefault();
          closePresentationMode();
        } else if (document.body.classList.contains('zen-mode')) {
          e.preventDefault();
          toggleZenMode();
        }
      } else if (e.key === 'ArrowRight' || e.key === ' ') {
        const presOverlay = document.getElementById('presentationOverlay');
        if (presOverlay && presOverlay.classList.contains('active')) {
          e.preventDefault();
          nextSlide();
        }
      } else if (e.key === 'ArrowLeft') {
        const presOverlay = document.getElementById('presentationOverlay');
        if (presOverlay && presOverlay.classList.contains('active')) {
          e.preventDefault();
          prevSlide();
        }
        if (document.body.classList.contains('zen-mode')) {
          e.preventDefault();
          toggleZenMode();
        }
      } else if (e.key === 'F5') {
        e.preventDefault();
        refreshPreviewAction();
      }
    });

    // Toolbar & Status Bar Font Mode Toggle (Kalpurush Unicode ⇄ Kalpurush ANSI)
    document.getElementById('toolToggleFont')?.addEventListener('click', toggleFontMode);
    document.getElementById('sbFontMode')?.addEventListener('click', toggleFontMode);

    // Dynamic Status Bar Interactive Handlers
    document.getElementById('sbBranch')?.addEventListener('click', () => {
      const activeTab = getActiveTab();
      const name = activeTab ? activeTab.title : 'main';
      showToast(`📂 ওয়ার্কস্পেস: markitdown | ফাইল: ${name}.md`, 'info', 2500);
    });

    document.getElementById('sbSync')?.addEventListener('click', async () => {
      showToast('🔄 ব্যাকএন্ড সার্ভার স্ট্যাটাস যাচাই করা হচ্ছে...', 'info', 1000);
      await checkServerStatus();
      showToast('🟢 লোকাল পাইথন ব্যাকএন্ড সার্ভার সক্রিয় (Port 8080)', 'success', 2000);
    });

    document.getElementById('sbDiagnostics')?.addEventListener('click', () => {
      const diag = updateDiagnostics();
      if (diag.errors > 0 || diag.warnings > 0) {
        showToast(`⚠️ সিনট্যাক্স ডায়াগনস্টিক রিপোর্ট:\n• ${diag.diagnosticNotes.join('\n• ')}`, 'warning', 4000);
      } else {
        showToast('✅ কোনো সিনট্যাক্স ত্রুটি বা সমস্যা নেই!', 'success', 2000);
      }
    });

    document.getElementById('saveStatus')?.addEventListener('click', () => {
      saveAllTabs();
      showToast('💾 লোকাল স্টোরেজে ড্রাফট তৎক্ষণাৎ সংরক্ষণ করা হয়েছে', 'success', 1500);
    });

    document.getElementById('sbLineCol')?.addEventListener('click', () => {
      const lineStr = prompt('কত নম্বর লাইনে যেতে চান? (Go to Line number):');
      if (lineStr !== null) {
        const lineNum = parseInt(lineStr.trim(), 10);
        if (!isNaN(lineNum) && lineNum > 0) {
          scrollToEditorLine(lineNum - 1);
        } else {
          showToast('সঠিক লাইন নম্বর দিন।', 'warning', 1500);
        }
      }
    });

    document.getElementById('sbWordCount')?.addEventListener('click', showDocStatsModal);

    document.getElementById('sbIndent')?.addEventListener('click', toggleIndentation);

    document.getElementById('sbEncoding')?.addEventListener('click', toggleFontMode);

    document.getElementById('sbLineEnding')?.addEventListener('click', toggleLineEnding);

    document.getElementById('sbDocType')?.addEventListener('click', () => {
      showToast('ডকুমেন্ট সিনট্যাক্স: GitHub Flavored Markdown (GFM)', 'info', 2000);
    });

    setupScrollSync();
  }

  // ==================== Menubar Controller ====================
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

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.menubar')) {
        closeAllMenus();
      }
    });

    document.querySelectorAll('.menu-dropdown .dropdown-item').forEach(btn => {
      btn.addEventListener('click', () => closeAllMenus());
    });

    // File Menu bindings
    document.getElementById('menuNewDoc')?.addEventListener('click', () => createNewTab());
    document.getElementById('menuCloseTab')?.addEventListener('click', () => closeTab(activeTabId));
    document.getElementById('menuImportDoc')?.addEventListener('click', () => importModal?.classList.add('active'));
    document.getElementById('menuSaveDocx')?.addEventListener('click', exportDocx);
    document.getElementById('menuSaveMd')?.addEventListener('click', exportMarkdown);
    document.getElementById('menuSaveTxt')?.addEventListener('click', exportTxt);
    document.getElementById('menuSaveHtml')?.addEventListener('click', exportHtml);
    document.getElementById('menuPrintPdf')?.addEventListener('click', exportPdf);
    document.getElementById('menuReload')?.addEventListener('click', () => {
      showConfirmModal("রিলোড", "পৃষ্ঠাটি রিলোড করতে চান? ড্রাফট সংরক্ষিত থাকবে।", () => location.reload());
    });

    // Edit Menu bindings
    document.getElementById('menuUndo')?.addEventListener('click', undo);
    document.getElementById('menuRedo')?.addEventListener('click', redo);
    document.getElementById('menuCut')?.addEventListener('click', () => {
      editor.focus();
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      if (start !== end) {
        pushHistoryState(editor.value);
        navigator.clipboard.writeText(editor.value.substring(start, end)).catch(() => {});
        editor.value = editor.value.substring(0, start) + editor.value.substring(end);
        editor.setSelectionRange(start, start);
        renderMarkdown();
        updateLineNumbers();
        updateStatusBar();
        showToast('✂️ কাট সম্পন্ন', 'info', 1000);
      }
    });
    document.getElementById('menuCopy')?.addEventListener('click', () => copyMarkdownAction());
    document.getElementById('menuPaste')?.addEventListener('click', async () => {
      editor.focus();
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          pushHistoryState(editor.value);
          const start = editor.selectionStart;
          const end = editor.selectionEnd;
          editor.value = editor.value.substring(0, start) + text + editor.value.substring(end);
          editor.setSelectionRange(start + text.length, start + text.length);
          renderMarkdown();
          updateLineNumbers();
          updateStatusBar();
          showToast('📥 পেস্ট সম্পন্ন', 'info', 1000);
        }
      } catch (err) {
        showToast('ক্লিপবোর্ড এক্সেস করার অনুমতি দিন', 'warning');
      }
    });
    document.getElementById('menuSelectAll')?.addEventListener('click', selectAllAction);
    document.getElementById('menuFindReplace')?.addEventListener('click', openFindReplaceModal);
    document.getElementById('menuClear')?.addEventListener('click', clearEditorAction);

    // View Menu bindings
    document.getElementById('menuRefreshPreview')?.addEventListener('click', refreshPreviewAction);
    document.getElementById('menuToggleTheme')?.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
    document.getElementById('menuViewBoth')?.addEventListener('click', () => setViewMode('both'));
    document.getElementById('menuViewEditorOnly')?.addEventListener('click', () => setViewMode('editor'));
    document.getElementById('menuViewPreviewOnly')?.addEventListener('click', () => setViewMode('preview'));
    document.getElementById('menuFontSizeIncrease')?.addEventListener('click', () => changeFontSize(2));
    document.getElementById('menuFontSizeDecrease')?.addEventListener('click', () => changeFontSize(-2));
    document.getElementById('menuFontSizeReset')?.addEventListener('click', () => changeFontSize(0));
    document.getElementById('menuToggleWordWrap')?.addEventListener('click', toggleWordWrap);

    // Tools Menu bindings
    document.getElementById('menuOcr')?.addEventListener('click', () => ocrModal?.classList.add('active'));
    document.getElementById('menuCopyPreviewText')?.addEventListener('click', () => copyPreviewTextAction());
    document.getElementById('menuCopyHtml')?.addEventListener('click', () => copyPreviewHtmlAction());
    document.getElementById('menuDocStats')?.addEventListener('click', showDocStatsModal);

    // Settings & Help Menu bindings
    document.getElementById('menuOpenSettings')?.addEventListener('click', () => settingsModal?.classList.add('active'));
    document.getElementById('menuShortcuts')?.addEventListener('click', () => shortcutsModal?.classList.add('active'));
    document.getElementById('menuSampleDoc')?.addEventListener('click', () => {
      showConfirmModal("নমুনা লোড", "নমুনা ডকুমেন্ট নতুন ট্যাবে খুলতে চান?", () => {
        createNewTab("Sample Document", DEFAULT_WELCOME_MD);
      });
    });
    document.getElementById('menuAbout')?.addEventListener('click', () => aboutModal?.classList.add('active'));
  }

  // ==================== Initialization ====================
  function init() {
    const savedTheme = localStorage.getItem('markitdown_studio_theme') || 'dark';
    setTheme(savedTheme);

    const savedFontSize = parseInt(localStorage.getItem('markitdown_studio_font_size') || '13', 10);
    if (!isNaN(savedFontSize) && savedFontSize >= 10 && savedFontSize <= 28) {
      currentFontSize = savedFontSize;
      editor.style.fontSize = `${currentFontSize}px`;
      previewContent.style.fontSize = `${currentFontSize}px`;
      if (lineNumbers) lineNumbers.style.fontSize = `${currentFontSize}px`;
    }

    if (window.mermaid) {
      mermaid.initialize({
        startOnLoad: false,
        theme: savedTheme === 'light' ? 'default' : 'dark',
        securityLevel: 'loose',
      });
    }

    initTabs();
    setFontMode('unicode', true);
    renderMarkdown();
    updateUndoRedoUI();
    setupEventListeners();
    checkServerStatus();
    updateDiagnostics();
    detectLineEnding();
    detectIndentation();
    updateBranchStatus(false);
    setSaveStatus('saved');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
