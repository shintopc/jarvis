"""
ui/overlays/customize_overlay.py — Floating Customization Overlay for SHINTO — MARK LI.
"""
from __future__ import annotations

import math
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QConicalGradient
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame
)

from ui.tokens import C, qcol, font_hud, font_tech, DEFAULT_UI_COLOR
from ui.components.glass_panel import GlassPanel


class HueWheel(QWidget):
    """Circular Hue Wheel Color Picker."""
    hue_picked = pyqtSignal(str)
    hue_committed = pyqtSignal(str)
    _RING = 16

    def __init__(self, initial_hex: str = DEFAULT_UI_COLOR, parent=None):
        super().__init__(parent)
        self.setFixedSize(148, 148)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hue = 0.53
        self._drag = False
        self.set_color(initial_hex)

    def color(self) -> str:
        return QColor.fromHsvF(self._hue, 1.0, 1.0).name()

    def set_color(self, hex_str: str):
        c = QColor((hex_str or "").strip())
        if c.isValid() and c.hsvHueF() >= 0:
            self._hue = c.hsvHueF()
            self.update()

    def _ring_rect(self) -> QRectF:
        m = self._RING / 2 + 3
        return QRectF(self.rect()).adjusted(m, m, -m, -m)

    def _hue_from_pos(self, pos: QPointF) -> float:
        c = QRectF(self.rect()).center()
        dx = pos.x() - c.x()
        dy = c.y() - pos.y()
        ang = math.atan2(dy, dx)
        return (ang / (2 * math.pi)) % 1.0

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self._ring_rect()
        center = rect.center()

        grad = QConicalGradient(center, 0)
        for i in range(0, 361, 20):
            grad.setColorAt(i / 360.0, QColor.fromHsvF((i % 360) / 360.0, 1.0, 1.0))
        p.setPen(QPen(QBrush(grad), self._RING))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect)

        # Center Preview
        preview = QColor.fromHsvF(self._hue, 1.0, 1.0)
        inner = rect.adjusted(30, 30, -30, -30)
        p.setPen(QPen(qcol(C.BORDER_B), 1))
        p.setBrush(QBrush(preview))
        p.drawEllipse(inner)

        # Handle
        r = rect.width() / 2
        ang = self._hue * 2 * math.pi
        hx = center.x() + r * math.cos(ang)
        hy = center.y() - r * math.sin(ang)
        p.setPen(QPen(QColor("#00060A"), 2))
        p.setBrush(QBrush(QColor("#FFFFFF")))
        p.drawEllipse(QPointF(hx, hy), 7.5, 7.5)

    def mousePressEvent(self, e):
        self._drag = True
        self._hue = self._hue_from_pos(e.position())
        self.update()
        self.hue_picked.emit(self.color())

    def mouseMoveEvent(self, e):
        if self._drag:
            self._hue = self._hue_from_pos(e.position())
            self.update()
            self.hue_picked.emit(self.color())

    def mouseReleaseEvent(self, e):
        if self._drag:
            self._drag = False
            self.hue_committed.emit(self.color())


class CustomizeOverlay(QWidget):
    """Customization overlay for theme colors and assistant persona name."""
    saved = pyqtSignal(str, str, str)
    _OW, _OH = 400, 500

    def __init__(self, assistant_name="SHINTO", user_name="", ui_color=DEFAULT_UI_COLOR, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(2, 6, 17, 0.94);")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        modal = GlassPanel(title="CUSTOMIZE SHINTO", subtitle="PERSONA & NEON SPECTRUM")
        modal.setFixedSize(self._OW, self._OH)
        m_lay = modal.content_layout()
        m_lay.setSpacing(8)

        m_lay.addWidget(QLabel("ASSISTANT NAME:"))
        self._name_input = QLineEdit(assistant_name)
        self._name_input.setFont(font_hud(8))
        self._name_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
        """)
        m_lay.addWidget(self._name_input)

        m_lay.addWidget(QLabel("USER CALLSIGN / NAME:"))
        self._user_input = QLineEdit(user_name)
        self._user_input.setPlaceholderText("e.g. Shinto / Boss")
        self._user_input.setFont(font_tech(8))
        self._user_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
        """)
        m_lay.addWidget(self._user_input)

        # Hue wheel
        self._wheel = HueWheel(ui_color)
        w_row = QHBoxLayout()
        w_row.addStretch(); w_row.addWidget(self._wheel); w_row.addStretch()
        m_lay.addLayout(w_row)

        self._wheel.hue_picked.connect(lambda h: self._hex_input.setText(h))
        self._wheel.hue_committed.connect(lambda h: self._set_color(h))

        self._hex_input = QLineEdit(ui_color)
        self._hex_input.setFont(font_tech(8))
        self._hex_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C.DARK}; color: {C.WHITE};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
        """)
        m_lay.addWidget(self._hex_input)

        btn_row = QHBoxLayout()
        btn_apply = QPushButton("APPLY CHANGES  ▸")
        btn_apply.setFixedHeight(34)
        btn_apply.setFont(font_hud(8, bold=True))
        btn_apply.setStyleSheet(f"""
            QPushButton {{
                background: {C.PRI}; color: #000;
                border: 1px solid {C.WHITE}; border-radius: 3px;
            }}
        """)
        btn_apply.clicked.connect(self._save)
        btn_row.addWidget(btn_apply)

        btn_cancel = QPushButton("CANCEL")
        btn_cancel.setFixedHeight(34)
        btn_cancel.setFont(font_tech(8))
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_MED};
                border: 1px solid {C.BORDER}; border-radius: 3px;
            }}
        """)
        btn_cancel.clicked.connect(self.hide)
        btn_row.addWidget(btn_cancel)
        m_lay.addLayout(btn_row)

        lay.addWidget(modal)

    def _set_color(self, h: str):
        self._hex_input.setText(h)

    def _save(self):
        aname = self._name_input.text().strip() or "SHINTO"
        uname = self._user_input.text().strip()
        uicol = self._hex_input.text().strip() or DEFAULT_UI_COLOR
        self.saved.emit(aname, uname, uicol)
        self.hide()
