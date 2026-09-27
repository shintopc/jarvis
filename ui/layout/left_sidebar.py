"""
ui/layout/left_sidebar.py — Collapsible Futuristic Navigation Rail for SHINTO — MARK LI.
Supports expanded/collapsed icon modes, cyan holographic glow, and tooltips.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy
)

from ui.tokens import C, font_hud, font_tech


class NavRailButton(QPushButton):
    """Futuristic Sci-Fi Navigation Item with cyan holographic glow when active."""
    def __init__(self, icon_str: str, label_str: str, parent=None):
        super().__init__(parent)
        self._icon_str = icon_str
        self._label_str = label_str
        self._collapsed = False
        self._is_active = False

        self.setCheckable(True)
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(label_str)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 0, 10, 0)
        self._layout.setSpacing(10)

        self._icon_lbl = QLabel(self._icon_str)
        self._icon_lbl.setFont(QFont("Segoe UI Emoji", 11))
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl.setStyleSheet("border: none; background: transparent;")
        self._layout.addWidget(self._icon_lbl)

        self._text_lbl = QLabel(self._label_str.upper())
        self._text_lbl.setFont(font_hud(7, bold=True))
        self._text_lbl.setStyleSheet("border: none; background: transparent;")
        self._layout.addWidget(self._text_lbl, stretch=1)

        self.update_style()

    def set_collapsed(self, collapsed: bool):
        self._collapsed = collapsed
        self._text_lbl.setVisible(not collapsed)
        if collapsed:
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self._layout.setContentsMargins(10, 0, 10, 0)
            self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def set_active(self, active: bool):
        self._is_active = active
        self.setChecked(active)
        self.update_style()

    def update_style(self):
        if self._is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {C.PRI_GHO};
                    border-left: 3px solid {C.PRI};
                    border-top: 1px solid rgba(0, 229, 255, 0.2);
                    border-bottom: 1px solid rgba(0, 229, 255, 0.2);
                    border-right: none;
                    border-radius: 0px;
                }}
            """)
            self._text_lbl.setStyleSheet(f"color: {C.PRI}; font-weight: bold; border: none; background: transparent;")
            self._icon_lbl.setStyleSheet(f"color: {C.PRI}; border: none; background: transparent;")
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                }}
                QPushButton:hover {{
                    background: {C.PANEL2};
                    border-left: 3px solid {C.BORDER_B};
                }}
            """)
            self._text_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
            self._icon_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")


class LeftSidebar(QWidget):
    """Collapsible Left Navigation Rail."""
    item_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._collapsed = False
        self.setFixedWidth(146)
        self.setStyleSheet(f"""
            QWidget {{
                background: {C.BG_ALT};
                border-right: 1px solid {C.BORDER};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.setSpacing(2)

        # Collapse toggle button
        self._toggle_btn = QPushButton("◀")
        self._toggle_btn.setFixedHeight(24)
        self._toggle_btn.setFont(font_tech(7, bold=True))
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setToolTip("Toggle Sidebar Mode")
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_DIM};
                border: none;
            }}
            QPushButton:hover {{ color: {C.PRI}; background: {C.PANEL2}; }}
        """)
        self._toggle_btn.clicked.connect(self.toggle_collapse)
        lay.addWidget(self._toggle_btn)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C.BORDER}; border: none; margin: 4px 0;")
        lay.addWidget(sep)

        # Navigation items (6 real functional views)
        self._buttons: dict[str, NavRailButton] = {}
        items = [
            ("dashboard",  "⊞",  "DASHBOARD"),
            ("chat",       "💬", "AI CHAT"),
            ("plugins",    "🧩", "PLUGINS"),
            ("automation", "⚡", "AUTOMATION"),
            ("tools",      "🛠", "TOOLS"),
            ("settings",   "⚙",  "SETTINGS"),
        ]

        for nav_id, icon_s, label_s in items:
            btn = NavRailButton(icon_s, label_s)
            btn.clicked.connect(lambda _, nid=nav_id: self._on_btn_clicked(nid))
            lay.addWidget(btn)
            self._buttons[nav_id] = btn

        lay.addStretch()
        self.set_active_item("dashboard")

    def toggle_collapse(self):
        self._collapsed = not self._collapsed
        if self._collapsed:
            self.setFixedWidth(46)
            self._toggle_btn.setText("▶")
        else:
            self.setFixedWidth(146)
            self._toggle_btn.setText("◀")

        for btn in self._buttons.values():
            btn.set_collapsed(self._collapsed)

    def _on_btn_clicked(self, nav_id: str):
        self.set_active_item(nav_id)
        self.item_selected.emit(nav_id)

    def set_active_item(self, nav_id: str):
        for nid, btn in self._buttons.items():
            btn.set_active(nid == nav_id)
