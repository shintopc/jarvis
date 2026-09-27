"""
ui/overlays/remote_overlay.py — Futuristic Mobile Remote Pairing Modal for SHINTO — MARK LI.
"""
from __future__ import annotations

import time
from io import BytesIO
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)

from ui.tokens import C, font_hud, font_tech
from ui.components.glass_panel import GlassPanel


class RemoteKeyOverlay(QWidget):
    """Floating modal for instant mobile QR scan and encryption session key pairing."""
    closed = pyqtSignal()
    _OW, _OH = 400, 480

    def __init__(self, url: str, key: str, auto_login_url: str = "", manual_url: str = "", expiry_secs: int = 600, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(2, 6, 17, 0.95);")

        self._expiry = time.time() + expiry_secs
        self._on_new_key = None
        self._auto_login_url = auto_login_url
        self._manual_url = manual_url or url

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        modal = GlassPanel(title="REMOTE ENCRYPTED PAIRING", subtitle="AES-256-CBC DASHBOARD BRIDGE")
        modal.setFixedSize(self._OW, self._OH)
        m_lay = modal.content_layout()
        m_lay.setSpacing(6)

        # QR Code Display
        self._qr_lbl = QLabel()
        self._qr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_lbl.setFixedSize(160, 160)
        self._qr_lbl.setStyleSheet("background: white; border-radius: 8px; padding: 4px;")
        qr_row = QHBoxLayout()
        qr_row.addStretch(); qr_row.addWidget(self._qr_lbl); qr_row.addStretch()
        m_lay.addLayout(qr_row)

        self._update_qr(auto_login_url or url)

        hint = QLabel("Scan with your phone to connect instantly via local network")
        hint.setFont(font_tech(7))
        hint.setStyleSheet(f"color: {C.TEXT_DIM};")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_lay.addWidget(hint)

        # Session Key Badge
        self._key_lbl = QLabel(key)
        self._key_lbl.setFont(font_hud(20, bold=True))
        self._key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._key_lbl.setStyleSheet(f"""
            color: {C.ACC};
            background: {C.PANEL2};
            border: 1px solid {C.BORDER_B};
            border-radius: 6px;
            padding: 6px 4px;
            letter-spacing: 6px;
        """)
        m_lay.addWidget(self._key_lbl)

        self._timer_lbl = QLabel()
        self._timer_lbl.setFont(font_tech(7))
        self._timer_lbl.setStyleSheet(f"color: {C.TEXT_MED};")
        self._timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_lay.addWidget(self._timer_lbl)

        btn_row = QHBoxLayout()
        btn_close = QPushButton("DISMISS")
        btn_close.setFixedHeight(32)
        btn_close.setFont(font_hud(8, bold=True))
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px;
            }}
        """)
        btn_close.clicked.connect(self._do_close)
        btn_row.addWidget(btn_close)
        m_lay.addLayout(btn_row)

        lay.addWidget(modal)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

    def set_new_key_callback(self, fn):
        self._on_new_key = fn

    def _update_qr(self, url: str):
        if not url:
            return
        try:
            import qrcode
            qr = qrcode.QRCode(box_size=4, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            px = QPixmap()
            px.loadFromData(buf.getvalue())
            self._qr_lbl.setPixmap(px.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception:
            self._qr_lbl.setText(url[:20])

    def mark_connected(self):
        self._timer.stop()
        self._key_lbl.setText("CONNECTED")
        self._key_lbl.setStyleSheet(f"color: {C.GREEN}; background: {C.GREEN_GHO}; border: 1px solid {C.GREEN}; border-radius: 6px; padding: 6px;")
        self._timer_lbl.setText("Remote client authenticated")

    def _tick(self):
        rem = max(0, int(self._expiry - time.time()))
        m, s = divmod(rem, 60)
        self._timer_lbl.setText(f"Key expires in {m:02d}:{s:02d}")
        if rem == 0:
            self._do_close()

    def _do_close(self):
        self.hide()
        self.closed.emit()
