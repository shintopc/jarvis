"""
ui/components/glass_panel.py — Futuristic Glassmorphic HUD Panel Container
Features subtle backdrop blur styling, tech corner brackets, and cyan accent borders.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame

from ui.tokens import C, qcol, font_hud, font_tech


class GlassPanel(QFrame):
    """
    Futuristic HUD panel container with corner tech brackets, subtle gradient background,
    and optional header.
    """
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        show_corners: bool = True,
        parent: QWidget | None = None,
        header_right_widget: QWidget | None = None
    ):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._show_corners = show_corners
        self._header_right = header_right_widget
        self._glow_intensity = 0.0

        self.setObjectName("GlassPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Layout
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(12, 10, 12, 10)
        self._root_layout.setSpacing(8)

        # Optional built-in header
        if self._title:
            self._header_widget = QWidget()
            hdr_lay = QHBoxLayout(self._header_widget)
            hdr_lay.setContentsMargins(0, 0, 0, 0)
            hdr_lay.setSpacing(6)

            # Tech icon marker
            marker = QLabel("◈")
            marker.setFont(font_hud(8, bold=True))
            marker.setStyleSheet(f"color: {C.PRI}; background: transparent;")
            hdr_lay.addWidget(marker)

            # Title
            title_lbl = QLabel(self._title.upper())
            title_lbl.setFont(font_hud(8, bold=True))
            title_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent; letter-spacing: 1px;")
            hdr_lay.addWidget(title_lbl)

            self._sub_lbl = QLabel(f"// {self._subtitle}" if self._subtitle else "")
            self._sub_lbl.setFont(font_tech(7))
            self._sub_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
            hdr_lay.addWidget(self._sub_lbl)

            hdr_lay.addStretch()

            if self._header_right:
                hdr_lay.addWidget(self._header_right)

            self._root_layout.addWidget(self._header_widget)

            # Subtle divider
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {C.BORDER}; margin: 0; border: none;")
            self._root_layout.addWidget(sep)

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(6)
        self._root_layout.addLayout(self._content_layout, stretch=1)

    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    def addWidget(self, widget: QWidget, stretch: int = 0):
        self._content_layout.addWidget(widget, stretch)

    def set_subtitle(self, text: str):
        self._subtitle = text
        if hasattr(self, "_sub_lbl") and self._sub_lbl:
            self._sub_lbl.setText(f"// {text}" if text else "")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)

        # Panel Background
        p.fillRect(self.rect(), qcol(C.PANEL, 220))

        # Thin tech border
        pen = QPen(qcol(C.BORDER, 180), 1)
        p.setPen(pen)
        p.drawRect(rect)

        # Draw Tech Corner Brackets if enabled
        if self._show_corners:
            corner_len = min(12.0, w / 4, h / 4)
            corner_pen = QPen(qcol(C.PRI, 220), 1.5)
            p.setPen(corner_pen)

            # Top-Left
            p.drawLine(1, 1, int(1 + corner_len), 1)
            p.drawLine(1, 1, 1, int(1 + corner_len))

            # Top-Right
            p.drawLine(int(w - 1), 1, int(w - 1 - corner_len), 1)
            p.drawLine(int(w - 1), 1, int(w - 1), int(1 + corner_len))

            # Bottom-Left
            p.drawLine(1, int(h - 1), int(1 + corner_len), int(h - 1))
            p.drawLine(1, int(h - 1), 1, int(h - 1 - corner_len))

            # Bottom-Right
            p.drawLine(int(w - 1), int(h - 1), int(w - 1 - corner_len), int(h - 1))
            p.drawLine(int(w - 1), int(h - 1), int(w - 1), int(h - 1 - corner_len))
