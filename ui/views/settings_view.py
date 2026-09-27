"""
ui/views/settings_view.py — Futuristic Settings Command Center for SHINTO — MARK LI.
Configure AI providers, voice/mic devices, themes, autostart, and security credentials securely.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QFrame,
    QScrollArea, QMessageBox
)

from ui.tokens import C, font_hud, font_tech, font_body, apply_ui_accent
from ui.components.glass_panel import GlassPanel

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
API_FILE   = CONFIG_DIR / "api_keys.json"


def _read_config() -> dict:
    try:
        return json.loads(API_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_config(d: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    API_FILE.write_text(json.dumps(d, indent=4), encoding="utf-8")


class SettingsView(QWidget):
    """Futuristic Settings View."""
    settings_updated = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C.BG};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        panel = GlassPanel(title="SETTINGS & SYSTEM CONFIGURATION", subtitle="AI RUNTIME & INTERACTION PREFERENCES")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(4, 4, 4, 4)
        c_lay.setSpacing(14)

        cfg = _read_config()

        # ── 1. AI PROVIDER & API KEYS ─────────────────────────────────────
        sec_ai = self._build_section("AI ENGINE & PROVIDERS", "Configure Gemini Live API Credentials")
        ai_grid = QGridLayout()
        ai_grid.setSpacing(8)

        ai_grid.addWidget(self._field_label("GEMINI API KEY:"), 0, 0)
        self._inp_gemini = QLineEdit(cfg.get("gemini_api_key", ""))
        self._inp_gemini.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_gemini.setFont(font_tech(8))
        self._inp_gemini.setStyleSheet(self._input_qss())
        ai_grid.addWidget(self._inp_gemini, 0, 1)

        ai_grid.addWidget(self._field_label("ASSISTANT NAME:"), 1, 0)
        self._inp_name = QLineEdit(cfg.get("assistant_name", "SHINTO"))
        self._inp_name.setFont(font_hud(8))
        self._inp_name.setStyleSheet(self._input_qss())
        ai_grid.addWidget(self._inp_name, 1, 1)

        sec_ai.content_layout().addLayout(ai_grid)
        c_lay.addWidget(sec_ai)

        # ── 2. APPEARANCE & ACCENT HUE ────────────────────────────────────
        sec_theme = self._build_section("APPEARANCE & THEMES", "Interface Accent & Holographic Glow")
        thm_lay = QHBoxLayout()
        thm_lay.setSpacing(8)

        for col_name, col_hex in [
            ("SHINTO NEON (CYAN)", "#00E5FF"),
            ("ELECTRIC BLUE",      "#1677FF"),
            ("NEON MAGENTA",       "#FF176B"),
            ("EMERALD MATRIX",     "#00F5A0"),
            ("AMBER GOLD",         "#FFD166"),
        ]:
            btn = QPushButton(col_name)
            btn.setFont(font_tech(7, bold=True))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C.PANEL2}; color: {col_hex};
                    border: 1px solid {col_hex}; border-radius: 3px; padding: 6px 10px;
                }}
                QPushButton:hover {{ background: {col_hex}; color: #000; }}
            """)
            btn.clicked.connect(lambda _, h=col_hex: self._set_theme_color(h))
            thm_lay.addWidget(btn)

        sec_theme.content_layout().addLayout(thm_lay)
        c_lay.addWidget(sec_theme)

        # ── 3. SAVE BUTTON ────────────────────────────────────────────────
        btn_save = QPushButton("💾  SAVE CONFIGURATION")
        btn_save.setFixedHeight(38)
        btn_save.setFont(font_hud(8, bold=True))
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {C.PRI}; color: #000;
                border: 1px solid {C.WHITE}; border-radius: 4px;
            }}
            QPushButton:hover {{ background: #4DF0FF; }}
        """)
        btn_save.clicked.connect(self._save_all)
        c_lay.addWidget(btn_save)

        c_lay.addStretch()
        scroll.setWidget(container)
        panel.addWidget(scroll, stretch=1)
        lay.addWidget(panel)

    def _field_label(self, txt: str) -> QLabel:
        l = QLabel(txt)
        l.setFont(font_hud(7, bold=True))
        l.setStyleSheet(f"color: {C.TEXT_MED}; border: none;")
        return l

    def _input_qss(self) -> str:
        return f"""
            QLineEdit {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; background: #010E1C; }}
        """

    def _build_section(self, title: str, subtitle: str) -> GlassPanel:
        return GlassPanel(title=title, subtitle=subtitle, show_corners=False)

    def _set_theme_color(self, hex_val: str):
        apply_ui_accent(hex_val)
        cfg = _read_config()
        cfg["ui_color"] = hex_val
        _save_config(cfg)
        self.settings_updated.emit()

    def _save_all(self):
        cfg = _read_config()
        cfg["gemini_api_key"] = self._inp_gemini.text().strip()
        cfg["assistant_name"] = self._inp_name.text().strip() or "SHINTO"
        _save_config(cfg)
        self.settings_updated.emit()
