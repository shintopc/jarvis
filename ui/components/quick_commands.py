"""
ui/components/quick_commands.py — Quick Action and Command Cards for SHINTO — MARK LI.
Directly invokes real backend actions (App launcher, Screenshot, Lock PC, Weather, YouTube, WhatsApp).
"""
from __future__ import annotations

import subprocess
import threading
from typing import Callable
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame
)

from ui.tokens import C, font_hud, font_tech
from ui.components.glass_panel import GlassPanel


class QuickButton(QPushButton):
    """Futuristic Sci-Fi HUD Action Button with hover glow."""
    def __init__(self, icon: str, title: str, subtitle: str, color_hex: str = C.PRI, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self._color = color_hex

        self.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
                text-align: left;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                border: 1px solid {self._color};
                background: #0C1E33;
            }}
            QPushButton:pressed {{
                background: #071526;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(8)

        # Icon box
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 12))
        icon_lbl.setStyleSheet("border: none; background: transparent;")
        lay.addWidget(icon_lbl)

        # Text col
        tcol = QVBoxLayout()
        tcol.setSpacing(1)
        t_lbl = QLabel(title.upper())
        t_lbl.setFont(font_hud(7, bold=True))
        t_lbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        tcol.addWidget(t_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(font_tech(6))
        sub_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        tcol.addWidget(sub_lbl)
        lay.addLayout(tcol, stretch=1)


class QuickCommandsPanel(GlassPanel):
    """Panel featuring quick actions (Screenshot, Lock, Weather, YouTube, WhatsApp)."""
    action_triggered = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(title="QUICK COMMANDS", subtitle="DIRECT EXECUTION", show_corners=True, parent=parent)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        # 1. Screenshot
        btn_scr = QuickButton("📸", "SCREENSHOT", "Capture active display", C.PRI)
        btn_scr.clicked.connect(self._do_screenshot)
        grid.addWidget(btn_scr, 0, 0)

        # 2. Lock PC
        btn_lock = QuickButton("🔒", "LOCK PC", "Secure workstation", C.RED)
        btn_lock.clicked.connect(self._do_lock)
        grid.addWidget(btn_lock, 0, 1)

        # 3. Open YouTube
        btn_yt = QuickButton("▶", "OPEN YOUTUBE", "Launch media stream", C.ACC)
        btn_yt.clicked.connect(lambda: self._trigger_command("Open YouTube in browser"))
        grid.addWidget(btn_yt, 1, 0)

        # 4. Check Weather
        btn_wtr = QuickButton("⛅", "WEATHER", "Local atmospheric report", C.ACC2)
        btn_wtr.clicked.connect(lambda: self._trigger_command("What is the current weather?"))
        grid.addWidget(btn_wtr, 1, 1)

        # 5. Open WhatsApp
        btn_wa = QuickButton("💬", "WHATSAPP", "Launch messaging client", C.GREEN)
        btn_wa.clicked.connect(lambda: self._trigger_command("Open WhatsApp"))
        grid.addWidget(btn_wa, 2, 0)

        # 6. Web Search
        btn_ws = QuickButton("🔍", "SEARCH WEB", "Global intelligence lookup", C.SEC)
        btn_ws.clicked.connect(lambda: self._trigger_command("Search the web for latest technology news"))
        grid.addWidget(btn_ws, 2, 1)

        self.content_layout().addLayout(grid)

    def _trigger_command(self, cmd_text: str):
        self.action_triggered.emit(cmd_text)

    def _do_screenshot(self):
        def _worker():
            try:
                from actions.screen_processor import _capture_screen
                _capture_screen()
                self._trigger_command("[SCREENSHOT_TAKEN] Display captured successfully.")
            except Exception as e:
                print(f"[QuickCommands] Screenshot error: {e}")
        threading.Thread(target=_worker, daemon=True).start()

    def _do_lock(self):
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        except Exception:
            self._trigger_command("Lock computer")
