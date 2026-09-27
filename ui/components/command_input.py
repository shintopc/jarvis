"""
ui/components/command_input.py — Futuristic Command Input Console for SHINTO — MARK LI.
Supports text command dispatch, speech interruption, mic toggling, and telemetry status.
"""
from __future__ import annotations

import threading
from typing import Callable, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame
)

from ui.tokens import C, font_hud, font_tech


class CommandConsole(QWidget):
    """Futuristic Command Bar with real-time prompt telemetry and action buttons."""
    command_submitted = pyqtSignal(str)
    interrupt_triggered = pyqtSignal()
    mic_toggled = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("CommandConsole")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Telemetry / Status indicator line
        self._status_row = QHBoxLayout()
        self._status_row.setContentsMargins(2, 0, 2, 0)
        self._status_row.setSpacing(4)
        
        self._prompt_icon = QLabel("❯")
        self._prompt_icon.setFont(font_hud(8, bold=True))
        self._prompt_icon.setStyleSheet(f"color: {C.PRI};")
        self._status_row.addWidget(self._prompt_icon)

        self._status_lbl = QLabel("COMMAND READY  [ENTER to execute, ESC to interrupt]")
        self._status_lbl.setFont(font_tech(7))
        self._status_lbl.setStyleSheet(f"color: {C.TEXT_DIM};")
        self._status_row.addWidget(self._status_lbl)
        self._status_row.addStretch()
        lay.addLayout(self._status_row)

        # Input Row
        inp_row = QHBoxLayout()
        inp_row.setContentsMargins(0, 0, 0, 0)
        inp_row.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command or question for SHINTO...")
        self._input.setFont(font_tech(9))
        self._input.setFixedHeight(34)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.DARK};
                color: {C.WHITE};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
                padding: 4px 10px;
                selection-background-color: {C.PRI_GHO};
            }}
            QLineEdit:focus {{
                border: 1px solid {C.PRI};
                background: #010E1C;
            }}
        """)
        self._input.returnPressed.connect(self._on_send)
        inp_row.addWidget(self._input, stretch=1)

        # Send Button
        self._send_btn = QPushButton("SEND  ▸")
        self._send_btn.setFixedHeight(34)
        self._send_btn.setFont(font_hud(8, bold=True))
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL2};
                color: {C.PRI};
                border: 1px solid {C.PRI_DIM};
                border-radius: 4px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {C.PRI};
                color: #000;
                border: 1px solid {C.WHITE};
            }}
            QPushButton:pressed {{
                background: {C.PRI_DIM};
            }}
        """)
        self._send_btn.clicked.connect(self._on_send)
        inp_row.addWidget(self._send_btn)

        lay.addLayout(inp_row)

        # Controls Row (Interrupt & Mic)
        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(0, 0, 0, 0)
        ctrl_row.setSpacing(6)

        self._interrupt_btn = QPushButton("✋  INTERRUPT  [ESC]")
        self._interrupt_btn.setFixedHeight(30)
        self._interrupt_btn.setFont(font_hud(7, bold=True))
        self._interrupt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._interrupt_btn.setStyleSheet(f"""
            QPushButton {{
                background: #1A000A;
                color: {C.RED};
                border: 1px solid {C.RED};
                border-radius: 4px;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background: rgba(255, 56, 100, 0.25);
                border: 1px solid #FFA0B4;
            }}
        """)
        self._interrupt_btn.clicked.connect(self.interrupt_triggered.emit)
        ctrl_row.addWidget(self._interrupt_btn)

        self._mic_btn = QPushButton("🎙  MICROPHONE ACTIVE")
        self._mic_btn.setFixedHeight(30)
        self._mic_btn.setFont(font_hud(7, bold=True))
        self._mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mic_btn.clicked.connect(self.mic_toggled.emit)
        self.set_muted(False)
        ctrl_row.addWidget(self._mic_btn)

        lay.addLayout(ctrl_row)

    def set_muted(self, muted: bool):
        if muted:
            self._mic_btn.setText("🔇  MICROPHONE MUTED")
            self._mic_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #1A000A;
                    color: {C.RED};
                    border: 1px solid {C.RED};
                    border-radius: 4px;
                    padding: 0 10px;
                }}
                QPushButton:hover {{ background: rgba(255, 56, 100, 0.25); }}
            """)
        else:
            self._mic_btn.setText("🎙  MICROPHONE ACTIVE")
            self._mic_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #001A10;
                    color: {C.GREEN};
                    border: 1px solid {C.GREEN};
                    border-radius: 4px;
                    padding: 0 10px;
                }}
                QPushButton:hover {{ background: rgba(0, 245, 160, 0.25); }}
            """)

    def set_processing_status(self, text: str):
        if text:
            self._status_lbl.setText(f"EXECUTING ▸ {text}")
            self._status_lbl.setStyleSheet(f"color: {C.PRI}; font-weight: bold;")
        else:
            self._status_lbl.setText("COMMAND READY  [ENTER to execute, ESC to interrupt]")
            self._status_lbl.setStyleSheet(f"color: {C.TEXT_DIM};")

    def _on_send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.command_submitted.emit(text)
