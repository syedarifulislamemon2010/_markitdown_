# -*- coding: utf-8 -*-
"""
Desktop GUI Package for MarkItDown.
"""
def main(*args, **kwargs):
    """Lazy launcher for Tkinter GUI to prevent importing GUI toolkit on server/headless use."""
    from .app import main as _app_main
    return _app_main(*args, **kwargs)

__all__ = ["main"]

