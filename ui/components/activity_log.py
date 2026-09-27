"""
ui/components/activity_log.py — Futuristic Technical Activity Log for SHINTO — MARK LI.
Supports real-time color-coded terminal messages, unicode/Malayalam text, and HUD controls.
"""
from __future__ import annotations

import html
import time
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame
)

from ui.tokens import C, font_hud, font_tech
from ui.components.glass_panel import GlassPanel


class ActivityLog(GlassPanel):
    """Futuristic Activity Log with live stream badge, clear/copy actions, and syntax colors."""
    def __init__(self, parent: QWidget | None = None):
        # Live status badge
        live_badge = QWidget()
        lb_lay = QHBoxLayout(live_badge); lb_lay.setContentsMargins(0, 0, 0, 0); lb_lay.setSpacing(4)
        dot = QLabel("●"); dot.setFont(font_tech(7)); dot.setStyleSheet(f"color: {C.GREEN};")
        txt = QLabel("LIVE"); txt.setFont(font_tech(7, bold=True)); txt.setStyleSheet(f"color: {C.GREEN};")
        lb_lay.addWidget(dot); lb_lay.addWidget(txt)

        super().__init__(
            title="ACTIVITY LOG",
            subtitle="EVENT STREAM",
            show_corners=True,
            parent=parent,
            header_right_widget=live_badge
        )

        # Toolbar (Clear, Copy)
        tool_bar = QHBoxLayout()
        tool_bar.setContentsMargins(0, 0, 0, 0)
        tool_bar.setSpacing(6)

        self._btn_clear = QPushButton("CLEAR")
        self._btn_clear.setFont(font_tech(6, bold=True))
        self._btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_DIM};
                border: 1px solid {C.BORDER}; border-radius: 2px; padding: 2px 6px;
            }}
            QPushButton:hover {{ color: {C.RED}; border-color: {C.RED}; background: rgba(255, 56, 100, 0.1); }}
        """)
        self._btn_clear.clicked.connect(self.clear_log)
        tool_bar.addStretch()
        tool_bar.addWidget(self._btn_clear)
        self.content_layout().addLayout(tool_bar)

        # Text Console
        self._display = QTextEdit()
        self._display.setReadOnly(True)
        self._display.setFont(font_tech(8))
        self._display.setStyleSheet(f"""
            QTextEdit {{
                background: {C.DARK};
                color: {C.TEXT};
                border: 1px solid {C.BORDER};
                border-radius: 3px;
                padding: 6px 8px;
                line-height: 1.4;
            }}
            QScrollBar:vertical {{
                background: {C.BG}; width: 5px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {C.BORDER_B}; border-radius: 2px; min-height: 14px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0; border: none;
            }}
        """)
        self.addWidget(self._display, stretch=1)

    def append_log(self, raw_text: str):
        """Format and append real-time activity log messages."""
        if not raw_text:
            return

        ts = time.strftime("%H:%M:%S")
        clean_text = raw_text.strip()
        escaped_body = html.escape(clean_text)

        # Determine message styling category
        if clean_text.startswith("You:") or clean_text.startswith("USER:"):
            prefix = "USER"
            color = C.PRI
            body = escaped_body.split(":", 1)[-1].strip() if ":" in escaped_body else escaped_body
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>{prefix} ▸ </span>"
                f"<span style='color:{C.WHITE};'>{body}</span>"
                f"</div>"
            )
        elif any(clean_text.startswith(k) for k in ("JARVIS:", "SHINTO:", "AI:")):
            prefix = "SHINTO"
            color = C.ACC2
            body = escaped_body.split(":", 1)[-1].strip() if ":" in escaped_body else escaped_body
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>{prefix} ◈ </span>"
                f"<span style='color:{C.TEXT};'>{body}</span>"
                f"</div>"
            )
        elif clean_text.startswith("ERR:") or "error" in clean_text.lower() or "failed" in clean_text.lower():
            prefix = "ERROR"
            color = C.RED
            body = escaped_body
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>[ALERT] </span>"
                f"<span style='color:{color};'>{body}</span>"
                f"</div>"
            )
        elif clean_text.startswith("WARN:") or "warning" in clean_text.lower():
            prefix = "WARN"
            color = C.YELLOW
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>[WARN] </span>"
                f"<span style='color:{color};'>{escaped_body}</span>"
                f"</div>"
            )
        elif any(clean_text.startswith(k) for k in ("SUCCESS:", "OK:", "✓")):
            prefix = "SUCCESS"
            color = C.GREEN
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>✓ </span>"
                f"<span style='color:{color};'>{escaped_body}</span>"
                f"</div>"
            )
        elif clean_text.startswith("FILE:"):
            color = C.ACC
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>⇪ FILE ▸ </span>"
                f"<span style='color:{C.TEXT};'>{escaped_body}</span>"
                f"</div>"
            )
        else:  # General System
            color = C.SEC
            html_line = (
                f"<div style='margin-bottom:4px;'>"
                f"<span style='color:{C.TEXT_DIM}; font-size:10px;'>[{ts}]</span> "
                f"<span style='color:{color}; font-weight:bold;'>SYS ▸ </span>"
                f"<span style='color:{C.TEXT_MED};'>{escaped_body}</span>"
                f"</div>"
            )

        self._display.append(html_line)
        self._display.moveCursor(QTextCursor.MoveOperation.End)

    def clear_log(self):
        self._display.clear()
        self.append_log("SYS: Activity log cleared.")
