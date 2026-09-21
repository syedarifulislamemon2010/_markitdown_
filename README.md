# MarkItDown Studio

<div align="center">

# 🚀 MarkItDown Studio
### Universal Markdown Workspace, Document Conversion Engine & Bilingual NLP Suite

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational.svg)](https://github.com/syedarifulislamemon2010/_markitdown_)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Syed%20Ariful%20Islam%20Emon-purple.svg)](https://github.com/syedarifulislamemon2010)
[![Offline](https://img.shields.io/badge/100%25-Offline%20First-success.svg)](#)

</div>

---

## 📌 Overview

**MarkItDown Studio** is a fast, offline-first desktop application and local web workspace engineered by **Syed Ariful Islam Emon**. It converts unstructured documents (**PDF, Word, Excel, PowerPoint, Images**) into clean **GitHub-Flavored Markdown (GFM)** while providing a feature-rich, VS Code-inspired dual-pane editing environment.

With specialized support for bilingual documents, MarkItDown Studio includes built-in **Bijoy (ANSI) ⇄ Unicode** conversion with context-aware English preservation, embedded **Kalpurush** typography, and seamless multi-format exports.

---

## ✨ Key Features

- **📄 Universal Document Conversion**: Convert PDF, DOCX, XLSX, PPTX, and Images (with offline OCR) directly into formatted Markdown tables, headings, and lists.
- **🔤 Native Bengali Typography & NLP**:
  - Pre-configured **Kalpurush** (Unicode) and **Kalpurush ANSI** (Bijoy) fonts.
  - One-click **Bijoy ⇄ Unicode** conversion that preserves English terms, citations, and formulas.
  - Built-in **Avro Phonetic** typing mode (`Ctrl + M`).
- **💻 VS Code-Inspired Studio**:
  - Side-by-side split view with real-time preview and 60fps synchronized scrolling.
  - Dynamic status bar tracking line/col, active document, server health, word count, encoding, and syntax diagnostics.
  - Real-time document outline (`H1`–`H6`) for quick navigation.
  - Multi-tab document workspace with auto-save.
  - Modern Dark and Light themes.
- **📊 Rich Markdown & Visuals**:
  - Mathematical typesetting via **KaTeX** (`$$` display and `$` inline math).
  - Flowcharts and diagrams via **Mermaid.js**.
  - Interactive **GUI Table Assistant** to insert and format tables effortlessly.
- **🖥️ Presentation / Slideshow Mode**: Turn any Markdown document into an interactive presentation.
- **💾 Multi-Format Export**:
  - **Microsoft Word (`.docx`)**: Native Word tables, embedded images, and math formulas.
  - **Print / PDF (`.pdf`)**: Direct headless PDF export or calibrated print dialog.
  - **Standalone HTML (`.html`)**: Complete self-contained file with bundled CSS and math fonts.
  - **Markdown (`.md`)** & **Plain Text (`.txt`)**.
- **🔒 100% Offline & Private**: Everything runs locally on your computer with zero external network dependencies.

---

## ⚡ Quick Start

### 1. Installation

Clone the repository and install the dependencies in a virtual environment:

```powershell
# Clone repository
git clone https://github.com/syedarifulislamemon2010/_markitdown_.git
cd _markitdown_

# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -e packages/markitdown
pip install bottle pywebview python-docx pdfminer.six fonttools requests
```

### 2. Launching the Studio

#### Standalone Desktop App (Recommended)
Double-click `run_desktop.bat` or run:
```powershell
python desktop/run_studio.py
```

#### Local Web Server Mode
```powershell
python desktop/server.py
```
Then open your browser at `http://127.0.0.1:8080`.

#### Command-Line Interface (CLI)
Convert documents directly from your terminal:
```powershell
# Convert PDF to Markdown
markitdown document.pdf -o output.md

# Convert Word document
markitdown report.docx -o report.md
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + N` | Create a new document tab |
| `Ctrl + W` | Close the active tab |
| `Ctrl + S` | Export active document as Markdown (`.md`) |
| `Ctrl + P` | Export / Print as PDF (`.pdf`) |
| `Ctrl + F` | Open Find & Replace modal |
| `Ctrl + Z` / `Ctrl + Y` | Undo / Redo |
| `Ctrl + B` / `Ctrl + I` | Bold / Italic formatting |
| `Ctrl + M` | Toggle Avro Phonetic Bengali mode |
| `F11` | Toggle Zen / Fullscreen mode |
| `F5` | Refresh live preview |

---

## 📁 Project Structure

```
markitdown/
├── core/                  # Conversion, Bengali NLP, OCR & Word exporter modules
│   ├── bengali.py         # Bijoy ANSI ⇄ Unicode conversion engine
│   ├── converter.py       # Universal document converter (PDF, Office, Images)
│   ├── docx_exporter.py   # Word document generator (.docx)
│   └── ocr.py             # Offline OCR engine
├── desktop/               # Native desktop wrapper and local server
│   ├── run_studio.py      # Desktop launcher (PyWebView / WebView2)
│   └── server.py          # Fast multi-threaded local WSGI server
├── packages/              # Modular MarkItDown library packages
│   └── markitdown/        # Core conversion package
├── web/                   # Frontend workspace interface (HTML/CSS/JS)
│   ├── css/               # Styling & typography (Kalpurush fonts)
│   ├── js/                # Editor controller, phonetic typing, exporters
│   └── vendor/            # Bundled offline libraries (KaTeX, Mermaid, fonts)
├── run_desktop.bat        # 1-Click Windows desktop launcher
└── README.md              # Project documentation
```

---

## 👨‍💻 Author

**Syed Ariful Islam Emon**
- **GitHub**: [@syedarifulislamemon2010](https://github.com/syedarifulislamemon2010)
- **Email**: [syedarifulislamemon201093@gmail.com](mailto:syedarifulislamemon201093@gmail.com)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
