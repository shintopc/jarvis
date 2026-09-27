"""
ui/views/tools_view.py — Categorized Futuristic Toolbox for SHINTO — MARK LI.
Provides quick-launch interactive cards for system, browser, dev, and media tools.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.glass_panel import GlassPanel


class ToolActionCard(QFrame):
    """Tool invocation card."""
    triggered = pyqtSignal(str)

    def __init__(self, icon_s: str, title_s: str, category_s: str, prompt_cmd: str, color_hex: str = C.PRI, parent=None):
        super().__init__(parent)
        self._cmd = prompt_cmd
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(84)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL2};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
                padding: 6px;
            }}
            QFrame:hover {{
                border: 1px solid {color_hex};
                background: #0D1F33;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(10)

        ico = QLabel(icon_s)
        ico.setFont(QFont("Segoe UI Emoji", 14))
        ico.setStyleSheet("border: none; background: transparent;")
        lay.addWidget(ico)

        tcol = QVBoxLayout(); tcol.setSpacing(2)
        tlbl = QLabel(title_s.upper())
        tlbl.setFont(font_hud(7, bold=True))
        tlbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        tcol.addWidget(tlbl)

        clbl = QLabel(f"CATEGORY: {category_s.upper()}")
        clbl.setFont(font_tech(6))
        clbl.setStyleSheet(f"color: {color_hex}; border: none; background: transparent;")
        tcol.addWidget(clbl)
        lay.addLayout(tcol, stretch=1)

        arrow = QLabel("▶")
        arrow.setFont(font_hud(7, bold=True))
        arrow.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        lay.addWidget(arrow)

    def mousePressEvent(self, e):
        self.triggered.emit(self._cmd)


class ToolsView(QWidget):
    """Categorized Futuristic Toolbox View."""
    command_triggered = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C.BG};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        panel = GlassPanel(title="COMMAND TOOLBOX", subtitle="DIRECT SYSTEM & AGENT UTILITIES")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(10)

        tools = [
            ("📸", "Capture Screenshot",    "SYSTEM",   "Take a screenshot of the current display", C.PRI),
            ("🔒", "Lock Workstation",      "SYSTEM",   "Lock computer immediately", C.RED),
            ("🔊", "Volume Control",        "SYSTEM",   "Set system volume to 50%", C.ACC2),
            ("🌐", "Web Intelligence",      "BROWSER",  "Search the web for latest AI news", C.SEC),
            ("🎬", "YouTube Media",         "MEDIA",    "Open YouTube and play music", C.ACC),
            ("💬", "WhatsApp Messenger",    "COMM",     "Open WhatsApp and check messages", C.GREEN),
            ("⛅", "Weather Satellite",     "DATA",     "Check local weather forecast", C.ACC2),
            ("💻", "Code Assistant",        "DEV",      "Help me write a Python script", C.PRI),
            ("📂", "File Controller",       "FILES",    "Search my documents folder", C.SEC),
            ("🔍", "Flight Search",         "TRAVEL",   "Find flights to Dubai next weekend", C.ACC),
        ]

        row, col = 0, 0
        for ico, title, cat, cmd, col_hex in tools:
            card = ToolActionCard(ico, title, cat, cmd, col_hex)
            card.triggered.connect(self.command_triggered.emit)
            grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        scroll.setWidget(container)
        panel.addWidget(scroll, stretch=1)
        lay.addWidget(panel)
