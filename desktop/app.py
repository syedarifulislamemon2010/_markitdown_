# -*- coding: utf-8 -*-
"""
MarkItDown Desktop Application.
Modern, full-featured desktop interface with Drag & Drop,
Batch Conversion, Live Preview, and Multi-threading.
"""

import os
import sys
import json
import threading
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Import GUI libraries with safe fallback for headless / server environments
try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    HAS_GUI = True
except Exception:
    ctk = None
    filedialog = None
    messagebox = None
    HAS_GUI = False

# Import DnD support with fallback
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except Exception:
    HAS_DND = False


# Import core conversion engine
from core.converter import (
    DocumentConverter,
    ConversionResult,
    SUPPORTED_EXTENSIONS,
    format_file_size,
)

# Settings persistence path in user's home directory
CONFIG_FILE = Path.home() / ".markitdown_desktop_config.json"


def load_config() -> dict:
    default_cfg = {
        "appearance_mode": "dark",
        "color_theme": "blue",
        "auto_save": True,
        "output_dir": "",
        "openai_api_key": "",
        "openai_base_url": "",
        "llm_model": "gpt-4o",
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")


def parse_dnd_data(data: str) -> List[str]:
    """Parse dropped file paths on Windows (handles spaces inside curly braces)."""
    pattern = r'\{([^}]+)\}|(\S+)'
    matches = re.findall(pattern, data)
    paths = [m[0] if m[0] else m[1] for m in matches]
    return [p for p in paths if os.path.exists(p)]


# Base class incorporating DnD if available
if not HAS_GUI:
    class AppBase:
        """Fallback empty class when GUI libraries are unavailable in headless CI."""
        def __init__(self, *args, **kwargs):
            pass
elif HAS_DND:
    class AppBase(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self):
            super().__init__()
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:
                pass
else:
    class AppBase(ctk.CTk):
        pass



class MarkItDownDesktopApp(AppBase):
    """Main MarkItDown Desktop Application Window."""

    def __init__(self):
        super().__init__()

        self.config = load_config()
        ctk.set_appearance_mode(self.config.get("appearance_mode", "dark"))
        ctk.set_default_color_theme(self.config.get("color_theme", "blue"))

        # Window settings
        self.title("MarkItDown Desktop - Universal Document Converter")
        self.geometry("1240x820")
        self.minsize(980, 680)

        # Core engine
        self.converter = DocumentConverter(
            openai_api_key=self.config.get("openai_api_key") or None,
            openai_base_url=self.config.get("openai_base_url") or None,
            llm_model=self.config.get("llm_model", "gpt-4o"),
        )

        # Application state
        self.queue: List[Dict] = []  # list of {path, name, size, status, result, card_widget}
        self.active_result: Optional[ConversionResult] = None
        self.is_converting = False
        self._cancel_requested = False

        # Build UI layout
        self._build_layout()
        self._setup_dnd()

    def _build_layout(self):
        """Construct dual-pane layout."""
        # Main Grid: Left panel (Queue & Controls, weight 4), Right panel (Preview, weight 6)
        self.grid_columnconfigure(0, weight=4, minsize=420)
        self.grid_columnconfigure(1, weight=6, minsize=520)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        """Left panel containing header, dropzone, file queue and conversion controls."""
        left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray92", "gray14"))
        left_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        left_frame.grid_rowconfigure(2, weight=1)  # Queue frame expands
        left_frame.grid_columnconfigure(0, weight=1)

        # 1. Header with title and Settings button
        header_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="MarkItDown",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Universal Document to Markdown Converter",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray",
            anchor="w",
        )
        subtitle_label.grid(row=1, column=0, sticky="w")

        settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙ Settings",
            width=85,
            height=30,
            fg_color=("gray80", "gray22"),
            hover_color=("gray70", "gray30"),
            text_color=("black", "white"),
            command=self._open_settings_dialog,
        )
        settings_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(8, 0))

        # 2. Drop Zone / Add Files Section
        self.drop_frame = ctk.CTkFrame(
            left_frame,
            corner_radius=10,
            border_width=2,
            border_color=("gray75", "gray28"),
            fg_color=("gray88", "gray18"),
        )
        self.drop_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        self.drop_frame.grid_columnconfigure((0, 1), weight=1)

        drop_icon = ctk.CTkLabel(
            self.drop_frame,
            text="📄 ➜ 📝",
            font=ctk.CTkFont(size=24),
        )
        drop_icon.grid(row=0, column=0, columnspan=2, pady=(12, 2))

        self.drop_text = ctk.CTkLabel(
            self.drop_frame,
            text="Drag & Drop PDF, Word, Excel, Audio, Images here\n(No file size limit)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray30", "gray70"),
        )
        self.drop_text.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        add_files_btn = ctk.CTkButton(
            self.drop_frame,
            text="Browse Files...",
            command=self._browse_files,
            height=32,
        )
        add_files_btn.grid(row=2, column=0, padx=(12, 6), pady=(0, 12), sticky="ew")

        add_folder_btn = ctk.CTkButton(
            self.drop_frame,
            text="Browse Folder...",
            command=self._browse_folder,
            fg_color=("gray75", "gray28"),
            hover_color=("gray65", "gray35"),
            text_color=("black", "white"),
            height=32,
        )
        add_folder_btn.grid(row=2, column=1, padx=(6, 12), pady=(0, 12), sticky="ew")

        # 3. File Queue Section (Scrollable)
        queue_header = ctk.CTkFrame(left_frame, fg_color="transparent")
        queue_header.grid(row=2, column=0, sticky="new", padx=16, pady=(10, 4))
        queue_header.grid_columnconfigure(0, weight=1)

        self.queue_count_label = ctk.CTkLabel(
            queue_header,
            text="Files Queue (0)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w",
        )
        self.queue_count_label.grid(row=0, column=0, sticky="w")

        clear_btn = ctk.CTkButton(
            queue_header,
            text="Clear List",
            width=70,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color=("red", "#ff6b6b"),
            hover_color=("gray85", "gray22"),
            command=self._clear_queue,
        )
        clear_btn.grid(row=0, column=1, sticky="e")

        self.queue_scroll = ctk.CTkScrollableFrame(
            left_frame,
            fg_color=("gray88", "gray17"),
            corner_radius=8,
        )
        self.queue_scroll.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 8))
        self.queue_scroll.grid_columnconfigure(0, weight=1)

        # Empty queue placeholder
        self.empty_label = ctk.CTkLabel(
            self.queue_scroll,
            text="Queue is empty.\nAdd files to start converting.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray",
        )
        self.empty_label.pack(pady=40)

        # 4. Bottom Controls (Progress bar, status, convert button)
        bottom_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(6, 16))
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(bottom_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            bottom_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(0, 8))

        btn_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)

        self.convert_btn = ctk.CTkButton(
            btn_row,
            text="▶ Convert All Files",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=38,
            command=self._start_conversion,
        )
        self.convert_btn.grid(row=0, column=0, sticky="ew")

    def _build_right_panel(self):
        """Right panel containing preview header, editor/viewer, and action tools."""
        right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray96", "gray11"))
        right_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 1. Preview Header
        header = ctk.CTkFrame(right_frame, fg_color=("gray90", "gray15"), corner_radius=0, height=56)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)

        info_box = ctk.CTkFrame(header, fg_color="transparent")
        info_box.grid(row=0, column=0, sticky="w", padx=16, pady=8)

        self.preview_title = ctk.CTkLabel(
            info_box,
            text="No document selected",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            anchor="w",
        )
        self.preview_title.grid(row=0, column=0, sticky="w")

        self.preview_meta = ctk.CTkLabel(
            info_box,
            text="Select a converted file from the queue to view its Markdown output",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="gray",
            anchor="w",
        )
        self.preview_meta.grid(row=1, column=0, sticky="w")

        # Action Buttons in Preview Header
        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="e", padx=16, pady=8)

        self.copy_btn = ctk.CTkButton(
            btn_box,
            text="📋 Copy",
            width=75,
            height=30,
            command=self._copy_markdown,
        )
        self.copy_btn.pack(side="left", padx=4)

        self.save_btn = ctk.CTkButton(
            btn_box,
            text="💾 Save As .md",
            width=100,
            height=30,
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35"),
            text_color=("black", "white"),
            command=self._save_active_markdown,
        )
        self.save_btn.pack(side="left", padx=4)

        self.open_folder_btn = ctk.CTkButton(
            btn_box,
            text="📂 Folder",
            width=75,
            height=30,
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35"),
            text_color=("black", "white"),
            command=self._open_file_location,
        )
        self.open_folder_btn.pack(side="left", padx=4)

        # 2. Markdown Editor / Output Textbox
        self.preview_text = ctk.CTkTextbox(
            right_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word",
            corner_radius=0,
            fg_color=("white", "gray13"),
            text_color=("gray10", "gray92"),
        )
        self.preview_text.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.preview_text.insert("1.0", "# Welcome to MarkItDown Desktop\n\n- Add your files using the left panel or simply drag & drop them.\n- Supports PDF, DOCX, PPTX, XLSX, HTML, Images, Audio, ZIP and more.\n- Process unlimited file sizes locally with complete privacy.")

        # 3. Bottom status strip for document stats (words, chars)
        strip = ctk.CTkFrame(right_frame, height=26, fg_color=("gray90", "gray14"), corner_radius=0)
        strip.grid(row=2, column=0, sticky="ew")
        self.stats_label = ctk.CTkLabel(
            strip,
            text="Lines: 5  |  Words: 42  |  Characters: 285",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="gray",
        )
        self.stats_label.pack(side="right", padx=16)

    def _setup_dnd(self):
        """Setup Drag and Drop if TkinterDnD is available."""
        if HAS_DND:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", self._on_drop_files)
            except Exception as e:
                print(f"Failed to register DnD: {e}")

    def _on_drop_files(self, event):
        """Handle files dropped from Windows File Explorer."""
        if not event.data:
            return
        paths = parse_dnd_data(event.data)
        self._add_paths(paths)

    def _browse_files(self):
        """File browser dialog."""
        types = [
            ("Supported Documents", "*.pdf;*.docx;*.pptx;*.xlsx;*.xls;*.txt;*.csv;*.tsv;*.json;*.xml;*.html;*.htm;*.epub;*.zip;*.png;*.jpg;*.jpeg;*.wav;*.mp3;*.m4a"),
            ("PDF Documents (*.pdf)", "*.pdf"),
            ("Word Documents (*.docx)", "*.docx"),
            ("PowerPoint (*.pptx)", "*.pptx"),
            ("Excel Spreadsheets (*.xlsx;*.xls;*.csv)", "*.xlsx;*.xls;*.csv"),
            ("Audio Files (*.wav;*.mp3;*.m4a)", "*.wav;*.mp3;*.m4a"),
            ("Image Files (*.png;*.jpg;*.jpeg)", "*.png;*.jpg;*.jpeg"),
            ("All Files (*.*)", "*.*"),
        ]
        files = filedialog.askopenfilenames(
            title="Select Documents to Convert",
            filetypes=types,
        )
        if files:
            self._add_paths(list(files))

    def _browse_folder(self):
        """Folder browser dialog."""
        folder = filedialog.askdirectory(title="Select Folder Containing Documents")
        if folder:
            self._add_paths([folder])

    def _add_paths(self, paths: List[str]):
        """Filter and add files to the queue."""
        added = 0
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_dir():
                for root, _, files in os.walk(path_obj):
                    for f in files:
                        full_f = os.path.join(root, f)
                        if self.converter.is_supported(full_f):
                            if self._append_to_queue(full_f):
                                added += 1
            elif path_obj.is_file():
                if self._append_to_queue(str(path_obj.resolve())):
                    added += 1

        if added > 0:
            self._render_queue()
            self.status_label.configure(text=f"Added {added} file(s) to queue.", text_color="gray")

    def _append_to_queue(self, file_path: str) -> bool:
        """Add a single file if not already in queue."""
        for item in self.queue:
            if item["path"] == file_path:
                return False  # Already in queue

        p = Path(file_path)
        size = p.stat().st_size if p.exists() else 0
        self.queue.append({
            "path": file_path,
            "name": p.name,
            "ext": p.suffix.lower(),
            "size_str": format_file_size(size),
            "status": "Queued",  # Queued, Converting, Done, Error
            "result": None,
            "widget": None,
        })
        return True

    def _clear_queue(self):
        """Clear all queued items."""
        if self.is_converting:
            messagebox.showwarning("In Progress", "Cannot clear queue while conversion is in progress.")
            return
        self.queue.clear()
        self._render_queue()
        self.progress_bar.set(0)
        self.status_label.configure(text="Queue cleared.", text_color="gray")

    def _render_queue(self):
        """Render the list of files in CTkScrollableFrame."""
        for child in self.queue_scroll.winfo_children():
            child.destroy()

        count = len(self.queue)
        self.queue_count_label.configure(text=f"Files Queue ({count})")

        if count == 0:
            self.empty_label = ctk.CTkLabel(
                self.queue_scroll,
                text="Queue is empty.\nAdd files to start converting.",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="gray",
            )
            self.empty_label.pack(pady=40)
            return

        for idx, item in enumerate(self.queue):
            card = ctk.CTkFrame(self.queue_scroll, fg_color=("gray92", "gray22"), corner_radius=6)
            card.pack(fill="x", padx=2, pady=3)
            card.grid_columnconfigure(1, weight=1)

            # Badge indicating file extension
            ext_badge = ctk.CTkLabel(
                card,
                text=item["ext"].replace(".", "").upper() or "FILE",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                width=45,
                height=22,
                corner_radius=4,
                fg_color=("gray80", "gray32"),
            )
            ext_badge.grid(row=0, column=0, padx=6, pady=6, sticky="w")

            # Name and size
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="w", padx=4, pady=4)

            name_lbl = ctk.CTkLabel(
                info_frame,
                text=item["name"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                anchor="w",
            )
            name_lbl.pack(anchor="w")

            meta_lbl = ctk.CTkLabel(
                info_frame,
                text=f"{item['size_str']}  •  {item['status']}",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=self._get_status_color(item["status"]),
                anchor="w",
            )
            meta_lbl.pack(anchor="w")

            # Clickable row to view preview
            card.bind("<Button-1>", lambda e, it=item: self._select_file_for_preview(it))
            name_lbl.bind("<Button-1>", lambda e, it=item: self._select_file_for_preview(it))

            # Action button on the right
            if item["status"] == "Done":
                view_btn = ctk.CTkButton(
                    card,
                    text="View",
                    width=50,
                    height=24,
                    font=ctk.CTkFont(size=11),
                    command=lambda it=item: self._select_file_for_preview(it),
                )
                view_btn.grid(row=0, column=2, padx=6, pady=6, sticky="e")
            elif not self.is_converting:
                remove_btn = ctk.CTkButton(
                    card,
                    text="✕",
                    width=28,
                    height=24,
                    fg_color="transparent",
                    hover_color=("gray80", "gray30"),
                    text_color="gray",
                    command=lambda it=item: self._remove_from_queue(it),
                )
                remove_btn.grid(row=0, column=2, padx=6, pady=6, sticky="e")

            item["widget"] = card

    def _get_status_color(self, status: str) -> str:
        if status == "Done":
            return "#4caf50"
        elif status == "Converting...":
            return "#2196f3"
        elif status == "Error":
            return "#f44336"
        return "gray"

    def _remove_from_queue(self, item: Dict):
        if self.is_converting:
            return
        if item in self.queue:
            self.queue.remove(item)
            self._render_queue()

    def _select_file_for_preview(self, item: Dict):
        """Display the markdown of the chosen file in right panel."""
        res: Optional[ConversionResult] = item.get("result")
        if not res:
            # If not yet converted, prompt to convert
            self.preview_title.configure(text=item["name"])
            self.preview_meta.configure(text=f"Status: {item['status']} - Click 'Convert All' to process.")
            return

        self.active_result = res
        self.preview_title.configure(text=res.file_name)
        if res.success:
            meta_text = f"{res.file_size_str}  •  Converted in {res.duration_seconds:.2f}s  •  Status: Success"
        else:
            meta_text = f"{res.file_size_str}  •  Conversion Error: {res.error_message}"
        self.preview_meta.configure(text=meta_text)

        # Update preview textbox
        self.preview_text.delete("1.0", "end")
        if res.success:
            try:
                from core.bengali import auto_convert_text
                display_text = auto_convert_text(res.markdown)
            except Exception:
                display_text = res.markdown
            self.preview_text.insert("1.0", display_text)
        else:
            self.preview_text.insert("1.0", f"### ⚠️ Error Converting File\n\n```\n{res.error_message}\n```")

        self._update_stats()

    def _update_stats(self):
        """Update line, word, and character count in status strip."""
        content = self.preview_text.get("1.0", "end-1c")
        lines = len(content.splitlines()) if content else 0
        words = len(content.split()) if content else 0
        chars = len(content)
        self.stats_label.configure(text=f"Lines: {lines:,}  |  Words: {words:,}  |  Characters: {chars:,}")

    def _copy_markdown(self):
        """Copy active markdown to clipboard."""
        content = self.preview_text.get("1.0", "end-1c")
        if not content:
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        orig_text = self.copy_btn.cget("text")
        self.copy_btn.configure(text="✅ Copied!")
        self.after(1500, lambda: self.copy_btn.configure(text=orig_text))

    def _save_active_markdown(self):
        """Save currently displayed markdown to a .md file."""
        content = self.preview_text.get("1.0", "end-1c")
        if not content:
            messagebox.showinfo("Empty", "No markdown content to save.")
            return

        initial_name = "converted.md"
        if self.active_result:
            initial_name = f"{Path(self.active_result.file_name).stem}.md"

        target = filedialog.asksaveasfilename(
            title="Save Markdown File",
            defaultextension=".md",
            initialfile=initial_name,
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if target:
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"File saved successfully to:\n{target}")

    def _open_file_location(self):
        """Open the folder containing the current source file in Windows Explorer."""
        if not self.active_result or not self.active_result.file_path:
            return
        p = Path(self.active_result.file_path)
        if p.exists():
            subprocess.run(['explorer', f'/select,"{p.resolve()}"'])  # nosec B603,B607

    def _start_conversion(self):
        """Begin batch conversion in background thread."""
        if not self.queue:
            messagebox.showinfo("Queue Empty", "Please add at least one document to convert.")
            return

        if self.is_converting:
            return

        self.is_converting = True
        self._cancel_requested = False
        self.convert_btn.configure(text="⏳ Converting...", state="disabled")
        self.progress_bar.set(0)

        # Launch worker thread
        threading.Thread(target=self._conversion_worker, daemon=True).start()

    def _conversion_worker(self):
        """Background thread handling document conversions."""
        total = len(self.queue)
        completed = 0

        for idx, item in enumerate(self.queue):
            if self._cancel_requested:
                break

            # Update item status to Converting
            item["status"] = "Converting..."
            self.after(0, lambda it=item, i=idx: self._on_item_converting(it, i, total))

            # Perform conversion using core engine
            res = self.converter.convert_file(item["path"])
            item["result"] = res
            item["status"] = "Done" if res.success else "Error"

            # Auto-save if enabled
            if res.success and self.config.get("auto_save", True):
                self._auto_save_result(res)

            completed += 1
            progress_val = completed / total
            self.after(0, lambda it=item, p=progress_val, c=completed: self._on_item_finished(it, p, c, total))

        self.after(0, self._on_all_finished)

    def _on_item_converting(self, item: Dict, idx: int, total: int):
        self.status_label.configure(
            text=f"Converting ({idx + 1}/{total}): {item['name']}...",
            text_color="#2196f3",
        )
        self._render_queue()

    def _on_item_finished(self, item: Dict, progress: float, completed: int, total: int):
        self.progress_bar.set(progress)
        self.status_label.configure(
            text=f"Progress: {completed}/{total} completed.",
            text_color="gray",
        )
        self._render_queue()

        # If this is the first converted file or active file, show preview
        if not self.active_result or self.active_result.file_name == item["name"]:
            self._select_file_for_preview(item)

    def _on_all_finished(self):
        self.is_converting = False
        self.convert_btn.configure(text="▶ Convert All Files", state="normal")
        self.progress_bar.set(1.0)
        self.status_label.configure(text="All files processed successfully!", text_color="#4caf50")
        self._render_queue()

    def _auto_save_result(self, res: ConversionResult):
        """Auto-save the converted markdown file next to original file or in custom folder."""
        try:
            custom_dir = self.config.get("output_dir", "").strip()
            if custom_dir and os.path.exists(custom_dir):
                target_dir = Path(custom_dir)
            else:
                target_dir = Path(res.file_path).parent

            out_path = target_dir / f"{Path(res.file_name).stem}.md"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(res.markdown)
        except Exception as e:
            print(f"Auto-save error: {e}")

    def _open_settings_dialog(self):
        """Modal dialog for Settings."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Settings - MarkItDown Desktop")
        dialog.geometry("520x460")
        dialog.transient(self)
        dialog.grab_set()

        # Heading
        lbl = ctk.CTkLabel(
            dialog,
            text="Settings & AI Configuration",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
        )
        lbl.pack(padx=20, pady=(20, 10), anchor="w")

        # 1. Output Directory
        dir_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        dir_frame.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(dir_frame, text="Output Directory:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        dir_entry = ctk.CTkEntry(dir_frame, placeholder_text="Default: Same folder as source document")
        dir_entry.insert(0, self.config.get("output_dir", ""))
        dir_entry.pack(side="left", fill="x", expand=True, pady=4)

        def browse_out_dir():
            d = filedialog.askdirectory(title="Select Output Folder")
            if d:
                dir_entry.delete(0, "end")
                dir_entry.insert(0, d)

        ctk.CTkButton(dir_frame, text="Browse", width=70, command=browse_out_dir).pack(side="right", padx=(8, 0))

        # Auto-save checkbox
        auto_save_var = ctk.BooleanVar(value=self.config.get("auto_save", True))
        auto_save_cb = ctk.CTkCheckBox(dialog, text="Automatically save .md file when conversion finishes", variable=auto_save_var)
        auto_save_cb.pack(padx=20, pady=8, anchor="w")

        # 2. OpenAI API Settings for OCR / Image Descriptions
        ai_frame = ctk.CTkFrame(dialog, fg_color=("gray90", "gray17"), corner_radius=8)
        ai_frame.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(
            ai_frame,
            text="Optional: OpenAI Vision / OCR (For Images & Scans)",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(padx=12, pady=(10, 4), anchor="w")

        key_lbl = ctk.CTkLabel(ai_frame, text="OpenAI / Relay API Key (sk-...):", font=ctk.CTkFont(size=11), text_color="gray")
        key_lbl.pack(padx=12, anchor="w")

        key_entry = ctk.CTkEntry(ai_frame, show="•", placeholder_text="Leave empty for free offline conversion")
        key_entry.insert(0, self.config.get("openai_api_key", ""))
        key_entry.pack(fill="x", padx=12, pady=4)

        url_lbl = ctk.CTkLabel(ai_frame, text="API Base URL (Optional for Custom Relay/Ollama):", font=ctk.CTkFont(size=11), text_color="gray")
        url_lbl.pack(padx=12, anchor="w")

        url_entry = ctk.CTkEntry(ai_frame, placeholder_text="https://api.hcnsec.cn/v1 or https://api.openai.com/v1")
        url_entry.insert(0, self.config.get("openai_base_url", ""))
        url_entry.pack(fill="x", padx=12, pady=4)

        model_lbl = ctk.CTkLabel(ai_frame, text="Vision / LLM Model:", font=ctk.CTkFont(size=11), text_color="gray")
        model_lbl.pack(padx=12, anchor="w")

        model_combo = ctk.CTkComboBox(ai_frame, values=["auto", "gpt-4o", "gpt-4o-mini", "DeepSeek-V4-Flash", "qwen3.7-plus"])
        model_combo.set(self.config.get("llm_model", "gpt-4o"))
        model_combo.pack(fill="x", padx=12, pady=(4, 12))

        # 3. Appearance Mode
        theme_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        theme_combo = ctk.CTkComboBox(theme_frame, values=["Dark", "Light", "System"], width=120)
        theme_combo.set(self.config.get("appearance_mode", "Dark").capitalize())
        theme_combo.pack(side="left", padx=12)

        # Save Button
        def save_and_close():
            self.config["output_dir"] = dir_entry.get().strip()
            self.config["auto_save"] = auto_save_var.get()
            self.config["openai_api_key"] = key_entry.get().strip()
            self.config["openai_base_url"] = url_entry.get().strip()
            self.config["llm_model"] = model_combo.get()
            theme_choice = theme_combo.get().lower()
            self.config["appearance_mode"] = theme_choice

            save_config(self.config)

            # Apply runtime changes
            ctk.set_appearance_mode(theme_choice)
            self.converter.update_config(
                openai_api_key=self.config["openai_api_key"] or None,
                openai_base_url=self.config["openai_base_url"] or None,
                llm_model=self.config["llm_model"],
            )
            dialog.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully.")

        ctk.CTkButton(dialog, text="Save Settings", height=34, command=save_and_close).pack(padx=20, pady=16, fill="x")


def main():
    if not HAS_GUI:
        print("Error: Desktop GUI requires customtkinter and tkinter.")
        return
    app = MarkItDownDesktopApp()
    app.mainloop()



if __name__ == "__main__":
    main()
