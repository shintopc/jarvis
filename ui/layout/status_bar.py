"""
ui/layout/status_bar.py — Futuristic Status Bar for SHINTO — MARK LI.
Displays assistant version, dynamic core status, motto, shortcuts, and connection telemetry.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame

from ui.tokens import C, font_hud, font_tech


class StatusBar(QWidget):
    """Futuristic Bottom Status Bar."""
    def __init__(self, assistant_name: str = "SHINTO", parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setStyleSheet(f"""
            QWidget {{
                background: {C.BG};
                border-top: 1px solid {C.BORDER};
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(12)

        # Left: Version + Status
        self._lbl_ver = QLabel(f"{assistant_name.upper()} v1.0.0")
        self._lbl_ver.setFont(font_hud(6, bold=True))
        self._lbl_ver.setStyleSheet(f"color: {C.PRI}; background: transparent; border: none;")
        lay.addWidget(self._lbl_ver)

        self._lbl_state = QLabel("● READY")
        self._lbl_state.setFont(font_tech(6, bold=True))
        self._lbl_state.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
        lay.addWidget(self._lbl_state)

        lay.addStretch()

        # Center: Futuristic Motto
        motto = QLabel("“Intelligence amplifies what you already are.”")
        motto.setFont(font_tech(6))
        motto.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent; border: none;")
        lay.addWidget(motto)

        lay.addStretch()

        # Right: Mic status & Shortcuts
        self._lbl_mic = QLabel("🎙 MIC ACTIVE")
        self._lbl_mic.setFont(font_tech(6, bold=True))
        self._lbl_mic.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
        lay.addWidget(self._lbl_mic)

        shortcuts = QLabel("[Ctrl+K] Command · [F4] Mute · [F11] Fullscreen")
        shortcuts.setFont(font_tech(6))
        shortcuts.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent; border: none;")
        lay.addWidget(shortcuts)

    def set_muted(self, muted: bool):
        if muted:
            self._lbl_mic.setText("🔇 MIC MUTED")
            self._lbl_mic.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")
        else:
            self._lbl_mic.setText("🎙 MIC ACTIVE")
            self._lbl_mic.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")

    def set_state(self, state: str):
        state = (state or "READY").upper()
        if state in ("INITIALISING", "SLEEPING"):
            state = "READY"
        col = C.RED if state in ("ERROR", "MUTED") else (C.ACC if state == "SPEAKING" else C.GREEN)
        self._lbl_state.setText(f"● {state}")
        self._lbl_state.setStyleSheet(f"color: {col}; background: transparent; border: none;")
