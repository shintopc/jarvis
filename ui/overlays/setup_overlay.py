"""
ui/overlays/setup_overlay.py — First-launch & Reconfiguration Setup Overlay for SHINTO — MARK LI.
"""
from __future__ import annotations

import platform
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QFrame
)

from ui.tokens import C, font_hud, font_tech
from ui.components.glass_panel import GlassPanel


class SetupOverlay(QWidget):
    """Futuristic Setup Modal for API Key configuration."""
    done = pyqtSignal(str, str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: rgba(2, 6, 17, 0.92);")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        modal = GlassPanel(title="SYSTEM INITIALIZATION", subtitle="CREDENTIAL AUTHENTICATION")
        modal.setFixedSize(440, 320)

        m_lay = modal.content_layout()
        m_lay.setSpacing(10)

        info = QLabel("Enter your Google Gemini API key to activate SHINTO neural services.")
        info.setFont(font_tech(8))
        info.setStyleSheet(f"color: {C.TEXT_MED};")
        info.setWordWrap(True)
        m_lay.addWidget(info)

        m_lay.addWidget(QLabel("GEMINI API KEY:"))
        self._key_input = QLineEdit()
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setPlaceholderText("AIzaSy...")
        self._key_input.setFont(font_tech(8))
        self._key_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 4px; padding: 6px 10px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; }}
        """)
        m_lay.addWidget(self._key_input)

        m_lay.addWidget(QLabel("OPERATING SYSTEM:"))
        self._os_combo = QComboBox()
        self._os_combo.addItems(["windows", "darwin", "linux"])
        cur_os = platform.system().lower()
        if cur_os in ("windows", "darwin", "linux"):
            self._os_combo.setCurrentText(cur_os)
        self._os_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 4px; padding: 4px 8px;
            }}
        """)
        m_lay.addWidget(self._os_combo)

        btn_init = QPushButton("INITIALIZE SYSTEM  ▸")
        btn_init.setFixedHeight(36)
        btn_init.setFont(font_hud(8, bold=True))
        btn_init.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_init.setStyleSheet(f"""
            QPushButton {{
                background: {C.PRI}; color: #000;
                border: 1px solid {C.WHITE}; border-radius: 4px;
            }}
            QPushButton:hover {{ background: #4DF0FF; }}
        """)
        btn_init.clicked.connect(self._on_init)
        m_lay.addWidget(btn_init)

        lay.addWidget(modal)

    def _on_init(self):
        k = self._key_input.text().strip()
        os_s = self._os_combo.currentText().strip()
        if k:
            self.done.emit(k, os_s)
