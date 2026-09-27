"""
ui/layout/top_navigation.py — Futuristic Top Navigation Bar for SHINTO — MARK LI.
Features branding, view navigation tabs, global command search, live clock & connection health.
"""
from __future__ import annotations

import time
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame
)

from ui.tokens import C, font_hud, font_tech


class TopNavigation(QWidget):
    """Futuristic Top Bar Header with live clock, nav tabs, and global quick command."""
    nav_tab_changed = pyqtSignal(str)   # "dashboard", "chat", "plugins", "automation", "media", "tools", "settings"
    command_entered = pyqtSignal(str)
    mic_toggled = pyqtSignal()

    def __init__(self, assistant_name: str = "SHINTO", parent: QWidget | None = None):
        super().__init__(parent)
        self._assistant_name = assistant_name
        self.setFixedHeight(58)
        self.setStyleSheet(f"""
            QWidget {{
                background: {C.BG};
                border-bottom: 1px solid {C.BORDER_B};
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        # ── LEFT: Branding & Logo ──────────────────────────────────────────
        brand_box = QWidget()
        brand_lay = QVBoxLayout(brand_box)
        brand_lay.setContentsMargins(0, 0, 0, 0)
        brand_lay.setSpacing(1)

        top_logo = QHBoxLayout()
        top_logo.setSpacing(6)
        logo_icon = QLabel("◈")
        logo_icon.setFont(font_hud(10, bold=True))
        logo_icon.setStyleSheet(f"color: {C.PRI}; border: none; background: transparent;")
        top_logo.addWidget(logo_icon)

        self._title_lbl = QLabel(self._assistant_name.upper())
        self._title_lbl.setFont(font_hud(11, bold=True))
        self._title_lbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent; letter-spacing: 2px;")
        top_logo.addWidget(self._title_lbl)

        sub_tag = QLabel("MARK LI")
        sub_tag.setFont(font_hud(7, bold=True))
        sub_tag.setStyleSheet(f"color: {C.PRI_DIM}; border: 1px solid {C.PRI_DIM}; border-radius: 2px; padding: 1px 4px;")
        top_logo.addWidget(sub_tag)
        top_logo.addStretch()
        brand_lay.addLayout(top_logo)

        tagline = QLabel("THINK • SPEAK • AUTOMATE • BEYOND")
        tagline.setFont(font_tech(6))
        tagline.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent; letter-spacing: 1px;")
        brand_lay.addWidget(tagline)
        lay.addWidget(brand_box)

        lay.addSpacing(16)

        # ── CENTER: Navigation View Tabs ──────────────────────────────────
        self._tabs_box = QWidget()
        tabs_lay = QHBoxLayout(self._tabs_box)
        tabs_lay.setContentsMargins(0, 0, 0, 0)
        tabs_lay.setSpacing(4)

        self._tab_buttons: dict[str, QPushButton] = {}
        tab_defs = [
            ("dashboard",  "DASHBOARD"),
            ("chat",       "AI CHAT"),
            ("plugins",    "PLUGINS"),
            ("automation", "AUTOMATION"),
            ("tools",      "TOOLS"),
            ("settings",   "SETTINGS"),
        ]

        for tab_id, label in tab_defs:
            btn = QPushButton(label)
            btn.setFont(font_hud(7, bold=True))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, t=tab_id: self._on_tab_btn_clicked(t))
            tabs_lay.addWidget(btn)
            self._tab_buttons[tab_id] = btn

        lay.addWidget(self._tabs_box)
        lay.addStretch()

        # ── RIGHT: Global Command + Connection + Live Clock ───────────────
        right_box = QHBoxLayout()
        right_box.setSpacing(10)

        # Global command input box
        self._cmd_input = QLineEdit()
        self._cmd_input.setPlaceholderText("Type a command... [Ctrl+K]")
        self._cmd_input.setFont(font_tech(8))
        self._cmd_input.setFixedWidth(180)
        self._cmd_input.setFixedHeight(28)
        self._cmd_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.PANEL2};
                color: {C.TEXT};
                border: 1px solid {C.BORDER};
                border-radius: 3px;
                padding: 2px 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {C.PRI};
                background: #010E1C;
            }}
        """)
        self._cmd_input.returnPressed.connect(self._on_cmd_enter)
        right_box.addWidget(self._cmd_input)

        # System Status Pill
        stat_box = QWidget()
        stat_lay = QHBoxLayout(stat_box); stat_lay.setContentsMargins(0, 0, 0, 0); stat_lay.setSpacing(4)
        dot = QLabel("●"); dot.setFont(font_tech(7)); dot.setStyleSheet(f"color: {C.GREEN}; border: none;")
        stat_txt = QLabel("SYSTEM ONLINE"); stat_txt.setFont(font_tech(6, bold=True)); stat_txt.setStyleSheet(f"color: {C.GREEN}; border: none;")
        stat_lay.addWidget(dot); stat_lay.addWidget(stat_txt)
        right_box.addWidget(stat_box)

        # Live Clock & Date
        clock_col = QVBoxLayout()
        clock_col.setContentsMargins(0, 0, 0, 0)
        clock_col.setSpacing(1)
        self._clock_lbl = QLabel("00:00:00")
        self._clock_lbl.setFont(font_hud(10, bold=True))
        self._clock_lbl.setStyleSheet(f"color: {C.PRI}; border: none; background: transparent;")
        self._clock_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_col.addWidget(self._clock_lbl)

        self._date_lbl = QLabel("--- -- --- ----")
        self._date_lbl.setFont(font_tech(6))
        self._date_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        self._date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_col.addWidget(self._date_lbl)
        right_box.addLayout(clock_col)

        lay.addLayout(right_box)

        # Clock timer
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._tick_clock)
        self._tmr.start(1000)
        self._tick_clock()

        # Default selection
        self.set_active_tab("dashboard")

    def _tick_clock(self):
        self._clock_lbl.setText(time.strftime("%H:%M:%S"))
        self._date_lbl.setText(time.strftime("%a %d %b %Y"))

    def _on_tab_btn_clicked(self, tab_id: str):
        self.set_active_tab(tab_id)
        self.nav_tab_changed.emit(tab_id)

    def set_active_tab(self, tab_id: str):
        for tid, btn in self._tab_buttons.items():
            is_active = (tid == tab_id)
            btn.setChecked(is_active)
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {C.PRI_GHO};
                        color: {C.PRI};
                        border: 1px solid {C.PRI};
                        border-radius: 3px;
                        padding: 0 10px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {C.TEXT_MED};
                        border: 1px solid transparent;
                        border-radius: 3px;
                        padding: 0 10px;
                    }}
                    QPushButton:hover {{
                        color: {C.WHITE};
                        border: 1px solid {C.BORDER};
                        background: {C.PANEL2};
                    }}
                """)

    def _on_cmd_enter(self):
        t = self._cmd_input.text().strip()
        if t:
            self._cmd_input.clear()
            self.command_entered.emit(t)
