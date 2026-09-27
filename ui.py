"""
ui.py — Entry point and bridge for the SHINTO — MARK LI Futuristic UI Subsystem.
Re-exports JarvisUI, C, and theme tokens while delegating to the modular ui/ package.
"""
from __future__ import annotations

import sys
from ui.tokens import C, apply_ui_accent, current_palette, DEFAULT_UI_COLOR, _PALETTE_DEFAULTS
from ui.main_window import MainWindow, _SysTelemetry
from ui import JarvisUI

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow("face.png")
    win.show()
    app.exec()