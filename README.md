# MarkItDown Studio

**MarkItDown Studio** is a full-featured, modern desktop & web markdown workspace and universal document conversion engine developed by **Syed Ariful Islam Emon**.

It integrates multi-format document conversion (PDF, DOCX, XLSX, PPTX, Images, OCR) with a real-time side-by-side Markdown editor, Bengali/English bidirectional typography tools (ANSI ⇄ Unicode), LaTeX / KaTeX mathematical rendering, Mermaid diagrams, and professional multi-format export capabilities.

![MarkItDown Studio](web/img/banner.png)

---

## Key Highlights

- **Universal Document Conversion**:
  - Converts **PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx)**, and HTML to structured Markdown.
  - Multi-engine OCR support for Bengali and English text extraction from scanned documents and images.
- **VS Code Inspired Dark Modern UI**:
  - Activity Bar, collapsible sidebar, multi-document tab system, breadcrumbs, line numbers, and status bar.
  - Live synchronized scrolling between markdown source and rich HTML preview.
- **Zero-Click Bengali Typography & Math Support**:
  - Flawless Bijoy (ANSI / SutonnyMJ) to Unicode conversion without distorting English words, code blocks, or formulas.
  - Bidirectional Unicode to ANSI conversion for publishing and press layouts.
  - Full LaTeX / KaTeX support for inline (`$...$`) and block (`$$...$$`) mathematical formulas.
  - Dynamic Mermaid.js flowcharts and diagrams.
- **Multi-Document Tab System & Auto-Save**:
  - Work across multiple documents simultaneously with `Ctrl+N` tabs.
  - Auto-saves all open tabs and active state locally; zero data loss on browser refresh.
  - Smart Undo / Redo history stacks with dynamic action enabling.
- **Professional Multi-Format Export**:
  - **Microsoft Word (.docx)**: Generates styled Word documents with tables, headings, code blocks, and formatted lists.
  - **PDF (.pdf)**: Clean print-optimized document export.
  - **Plain Text (.txt)**, **Markdown (.md)**, and **HTML (.html)** direct downloads.

---

## Architecture & Project Structure

```
markitdown/
├── core/                   # Core conversion, Bengali NLP, DOCX generation & OCR
│   ├── bengali.py          # Dual-script Bengali ANSI ⇄ Unicode engine
│   ├── converter.py        # Universal document conversion engine
│   ├── docx_exporter.py    # Formatted Word (.docx) export generator
│   ├── gazette_extractor.py# Government gazette & complex layout extractor
│   └── ocr.py              # OCR pipeline for Bengali & English
├── desktop/                # Desktop application layer & local web server
│   ├── run_studio.py       # Standalone desktop window launcher
│   └── server.py           # Local WSGI / REST API server
├── web/                    # Modern VS Code inspired Web UI
│   ├── index.html          # Main application interface
│   ├── css/style.css       # VS Code Dark Modern theme stylesheet
│   ├── js/app.js           # Multi-tab state, editor, and export controller
│   ├── js/bijoy2unicode.js # Client-side Bijoy ⇄ Unicode translation engine
│   └── vendor/             # Bundled libraries (marked, KaTeX, Mermaid)
└── run_desktop.bat         # 1-Click Desktop Launcher
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10 or higher.
- Modern web browser (Chrome, Edge, Firefox) or Microsoft Edge WebView2 for desktop mode.

### 2. Installation
```powershell
# Clone your repository
git clone https://github.com/syedarifulislamemon2010/markitdown.git
cd markitdown

# Setup virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -e packages/markitdown
pip install python-docx
```

### 3. Running MarkItDown Studio

**Option A: Standalone Desktop Window**
```powershell
.\run_desktop.bat
```
or
```powershell
python desktop/run_studio.py
```

**Option B: Web Application Mode**
```powershell
python desktop/server.py
```
Then navigate to `http://127.0.0.1:8080` in your web browser.

---

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + N` | New Document Tab |
| `Ctrl + W` | Close Active Tab |
| `Ctrl + O` | Import Document (PDF / Word / Excel) |
| `Ctrl + S` | Export Markdown (.md) |
| `Ctrl + P` | Print / Save to PDF |
| `Ctrl + Z` | Undo |
| `Ctrl + Y` / `Ctrl + Shift + Z` | Redo |
| `Ctrl + F` | Find & Replace |
| `F5` | Refresh Preview & Diagrams |

---

## Author & Contributor

Developed by **Syed Ariful Islam Emon**
- GitHub: [@syedarifulislamemon2010](https://github.com/syedarifulislamemon2010)
- Email: [syedarifulislamemon201093@gmail.com](mailto:syedarifulislamemon201093@gmail.com)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
