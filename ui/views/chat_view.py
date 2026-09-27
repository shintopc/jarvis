"""
ui/views/chat_view.py — Futuristic AI Chat Screen for SHINTO — MARK LI.
Supports conversation history, visual tool execution steps, code formatting, and markdown.
"""
from __future__ import annotations

import html
import time
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QFrame, QScrollArea
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.glass_panel import GlassPanel


class ChatMessageBubble(QFrame):
    """Futuristic Chat Bubble with sender badge, timestamp, and visual tool indicator."""
    def __init__(self, sender: str, text: str, tools: list[dict] | None = None, parent=None):
        super().__init__(parent)
        is_user = (sender.upper() in ("USER", "YOU"))

        self.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL if is_user else C.PANEL2};
                border: 1px solid {C.PRI_DIM if is_user else C.BORDER_B};
                border-radius: 6px;
                padding: 8px;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(6)

        # Header: Sender + Timestamp
        hdr = QHBoxLayout()
        hdr.setSpacing(6)
        s_lbl = QLabel(sender.upper())
        s_lbl.setFont(font_hud(7, bold=True))
        s_lbl.setStyleSheet(f"color: {C.PRI if is_user else C.ACC2}; border: none; background: transparent;")
        hdr.addWidget(s_lbl)
        hdr.addStretch()

        ts_lbl = QLabel(time.strftime("%H:%M:%S"))
        ts_lbl.setFont(font_tech(6))
        ts_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        hdr.addWidget(ts_lbl)
        lay.addLayout(hdr)

        # Visual Tool Executions if any
        if tools:
            for t in tools:
                t_box = QFrame()
                t_box.setStyleSheet(f"background: {C.DARK}; border: 1px solid {C.GREEN}; border-radius: 3px; padding: 4px;")
                t_lay = QHBoxLayout(t_box); t_lay.setContentsMargins(6, 3, 6, 3); t_lay.setSpacing(6)
                t_ico = QLabel("⚙"); t_ico.setFont(font_tech(8)); t_ico.setStyleSheet(f"color: {C.GREEN}; border: none;")
                t_name = QLabel(f"TOOL: {t.get('name', 'Action').upper()} — ✓ COMPLETED")
                t_name.setFont(font_tech(7, bold=True)); t_name.setStyleSheet(f"color: {C.GREEN}; border: none;")
                t_lay.addWidget(t_ico); t_lay.addWidget(t_name); t_lay.addStretch()
                lay.addWidget(t_box)

        # Message Text Body
        body_lbl = QLabel(text)
        body_lbl.setFont(font_body(9))
        body_lbl.setWordWrap(True)
        body_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body_lbl.setStyleSheet(f"color: {C.WHITE if is_user else C.TEXT}; border: none; background: transparent; line-height: 1.4;")
        lay.addWidget(body_lbl)


class ChatView(QWidget):
    """Dedicated AI Chat Interface."""
    message_sent = pyqtSignal(str)

    def __init__(self, assistant_name: str = "SHINTO", parent: QWidget | None = None):
        super().__init__(parent)
        self._assistant_name = assistant_name
        self.setStyleSheet(f"background: {C.BG};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        # Header Info Panel
        hdr_panel = GlassPanel(title="AI CONVERSATION CHANNEL", subtitle="GEMINI LIVE MULTI-MODAL PIPELINE")
        lay.addWidget(hdr_panel, stretch=0)

        # Scrollable Feed Area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {C.DARK};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
            }}
            QScrollBar:vertical {{
                background: {C.BG}; width: 6px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C.BORDER_B}; border-radius: 3px; min-height: 20px;
            }}
        """)

        self._feed_container = QWidget()
        self._feed_layout = QVBoxLayout(self._feed_container)
        self._feed_layout.setContentsMargins(12, 12, 12, 12)
        self._feed_layout.setSpacing(10)
        self._feed_layout.addStretch()

        self._scroll.setWidget(self._feed_container)
        lay.addWidget(self._scroll, stretch=1)

        # Input Bar
        input_panel = GlassPanel()
        inp_lay = QHBoxLayout()
        inp_lay.setContentsMargins(0, 0, 0, 0)
        inp_lay.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText(f"Ask {self._assistant_name} anything or give a task...")
        self._input.setFont(font_tech(9))
        self._input.setFixedHeight(36)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 4px; padding: 4px 10px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; background: #010E1C; }}
        """)
        self._input.returnPressed.connect(self._on_send)
        inp_lay.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("SEND  ▸")
        self._send_btn.setFixedHeight(36)
        self._send_btn.setFont(font_hud(8, bold=True))
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PRI}; color: #000;
                border: 1px solid {C.WHITE}; border-radius: 4px; padding: 0 16px;
            }}
            QPushButton:hover {{ background: #4DF0FF; }}
        """)
        self._send_btn.clicked.connect(self._on_send)
        inp_lay.addWidget(self._send_btn)

        input_panel.content_layout().addLayout(inp_lay)
        lay.addWidget(input_panel, stretch=0)

        # Welcome message
        self.add_message(self._assistant_name, f"Greetings, Shinto. {self._assistant_name} neural assistant online and ready for tasks.")

    def add_message(self, sender: str, text: str, tools: list[dict] | None = None):
        bubble = ChatMessageBubble(sender, text, tools)
        self._feed_layout.insertWidget(self._feed_layout.count() - 1, bubble)
        # Auto scroll to bottom
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def _on_send(self):
        txt = self._input.text().strip()
        if not txt:
            return
        self._input.clear()
        self.add_message("YOU", txt)
        self.message_sent.emit(txt)
