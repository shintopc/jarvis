"""
ui/views/automation_view.py — Futuristic Automation Center for SHINTO — MARK LI.
Manages automated schedules, morning briefings, background watchdogs, and proactive routines.
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
from memory.config_manager import get_brief_enabled, save_brief_enabled


class AutomationCard(QFrame):
    """Futuristic Automation Task Card with switch and status."""
    def __init__(self, title: str, schedule_str: str, desc: str, initial_on: bool = True, parent=None):
        super().__init__(parent)
        self._is_on = initial_on
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL2};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
                padding: 6px;
            }}
            QFrame:hover {{
                border: 1px solid {C.PRI};
                background: #0D1F33;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        # Header: Icon + Title + Schedule + Toggle
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        ico = QLabel("⚡")
        ico.setFont(QFont("Segoe UI Emoji", 12))
        ico.setStyleSheet("border: none; background: transparent;")
        top_row.addWidget(ico)

        tcol = QVBoxLayout(); tcol.setSpacing(1)
        tlbl = QLabel(title.upper())
        tlbl.setFont(font_hud(8, bold=True))
        tlbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        tcol.addWidget(tlbl)

        slbl = QLabel(f"SCHEDULE: {schedule_str}")
        slbl.setFont(font_tech(6))
        slbl.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        tcol.addWidget(slbl)
        top_row.addLayout(tcol, stretch=1)

        # Toggle Button
        self._btn_toggle = QPushButton("ACTIVE" if self._is_on else "PAUSED")
        self._btn_toggle.setFont(font_tech(6, bold=True))
        self._btn_toggle.setFixedSize(65, 22)
        self._btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        self._btn_toggle.clicked.connect(self._toggle)
        top_row.addWidget(self._btn_toggle)

        lay.addLayout(top_row)

        desc_lbl = QLabel(desc)
        desc_lbl.setFont(font_body(7))
        desc_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
        desc_lbl.setWordWrap(True)
        lay.addWidget(desc_lbl, stretch=1)

    def _update_style(self):
        if self._is_on:
            self._btn_toggle.setText("ACTIVE")
            self._btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {C.GREEN_GHO}; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 2px;
                }}
            """)
        else:
            self._btn_toggle.setText("PAUSED")
            self._btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {C.DARK}; color: {C.TEXT_DIM};
                    border: 1px solid {C.BORDER}; border-radius: 2px;
                }}
            """)

    def _toggle(self):
        self._is_on = not self._is_on
        self._update_style()


class AutomationView(QWidget):
    """Futuristic Automation Command Center."""
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C.BG};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        panel = GlassPanel(title="AUTOMATION & PROACTIVE AGENTS", subtitle="SCHEDULED ROUTINES & WATCHDOGS")

        grid = QGridLayout()
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(10)

        # 1. Morning Briefing
        brief_on = get_brief_enabled()
        card_mb = AutomationCard(
            title="Morning Briefing",
            schedule_str="On First Daily Startup",
            desc="Synthesizes daily weather forecast, top world news, and hardware health into speech.",
            initial_on=brief_on
        )
        grid.addWidget(card_mb, 0, 0)

        # 2. WhatsApp Proactive Monitoring
        card_wa = AutomationCard(
            title="WhatsApp Watchdog",
            schedule_str="Continuous Background Polling",
            desc="Monitors unread WhatsApp messages and notifies SHINTO when urgent keywords trigger.",
            initial_on=True
        )
        grid.addWidget(card_wa, 0, 1)

        # 3. Hardware Thermal & Load Guard
        card_sys = AutomationCard(
            title="Hardware Telemetry Guard",
            schedule_str="Every 5 Seconds",
            desc="Watches CPU, RAM, and GPU spikes (>90%) with voice warnings and mitigation advice.",
            initial_on=True
        )
        grid.addWidget(card_sys, 1, 0)

        # 4. Global News Intelligence Feed
        card_news = AutomationCard(
            title="Global News Digest",
            schedule_str="Hourly Cycle",
            desc="Scrapes breaking world headlines from DuckDuckGo and caches them for quick querying.",
            initial_on=True
        )
        grid.addWidget(card_news, 1, 1)

        panel.content_layout().addLayout(grid)
        lay.addWidget(panel)
