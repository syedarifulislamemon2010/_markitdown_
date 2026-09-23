# -*- coding: utf-8 -*-
"""
Desktop GUI Package for MarkItDown.
"""
try:
    from .app import main
except Exception:
    def main(*args, **kwargs):
        raise RuntimeError("Desktop Tkinter GUI requires customtkinter and tkinter.")

__all__ = ["main"]

