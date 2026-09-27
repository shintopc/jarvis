"""
ui/components/file_uploader.py — Futuristic Drag-and-Drop File Upload Panel for SHINTO — MARK LI.
Supports multi-format files, drag-and-drop visuals, file metadata badges, and removal.
"""
from __future__ import annotations

import os
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QProgressBar
)

from ui.tokens import C, font_hud, font_tech
from ui.components.glass_panel import GlassPanel

_FILE_ICONS = {
    "image":    ("🖼", "IMAGE"),
    "audio":    ("🎵", "AUDIO"),
    "video":    ("🎬", "VIDEO"),
    "pdf":      ("📄", "PDF"),
    "document": ("📝", "DOCUMENT"),
    "code":     ("💻", "CODE"),
    "archive":  ("📦", "ARCHIVE"),
    "data":     ("📊", "DATA"),
    "unknown":  ("📁", "FILE"),
}

def _file_category(p: Path) -> str:
    ext = p.suffix.lower().lstrip(".")
    if ext in ("png", "jpg", "jpeg", "webp", "gif", "bmp", "svg", "ico"):
        return "image"
    if ext in ("mp3", "wav", "ogg", "flac", "m4a", "aac"):
        return "audio"
    if ext in ("mp4", "mkv", "avi", "mov", "webm"):
        return "video"
    if ext == "pdf":
        return "pdf"
    if ext in ("txt", "md", "docx", "doc", "rtf", "odt"):
        return "document"
    if ext in ("py", "js", "ts", "html", "css", "json", "c", "cpp", "rs", "go", "java", "sh"):
        return "code"
    if ext in ("zip", "tar", "gz", "7z", "rar"):
        return "archive"
    if ext in ("csv", "xlsx", "xls", "parquet", "sqlite", "db"):
        return "data"
    return "unknown"

def _fmt_size(n_bytes: int) -> str:
    if n_bytes < 1024:
        return f"{n_bytes} B"
    if n_bytes < 1024 * 1024:
        return f"{n_bytes / 1024:.1f} KB"
    return f"{n_bytes / (1024 * 1024):.1f} MB"


class FileUploader(GlassPanel):
    """Futuristic File Upload drop-zone with file inspector card."""
    file_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(
            title="FILE UPLOAD",
            subtitle="DRAG & DROP CONSOLE",
            show_corners=True,
            parent=parent
        )
        self.setAcceptDrops(True)
        self._current_file: str | None = None

        # Drop Target Box
        self._drop_box = QFrame()
        self._drop_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self._drop_box.setStyleSheet(f"""
            QFrame {{
                background: {C.DARK};
                border: 1px dashed {C.PRI_DIM};
                border-radius: 4px;
                padding: 10px;
            }}
            QFrame:hover {{
                border: 1px dashed {C.PRI};
                background: {C.PRI_GHO};
            }}
        """)
        db_lay = QVBoxLayout(self._drop_box)
        db_lay.setContentsMargins(8, 8, 8, 8)
        db_lay.setSpacing(4)
        db_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._upload_icon = QLabel("⇪")
        self._upload_icon.setFont(font_hud(14, bold=True))
        self._upload_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._upload_icon.setStyleSheet(f"color: {C.PRI}; border: none; background: transparent;")
        db_lay.addWidget(self._upload_icon)

        self._upload_txt = QLabel("DRAG & DROP FILES HERE\nOR CLICK TO BROWSE")
        self._upload_txt.setFont(font_hud(7, bold=True))
        self._upload_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._upload_txt.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
        db_lay.addWidget(self._upload_txt)

        self._drop_box.mousePressEvent = lambda _: self._browse_file()
        self.addWidget(self._drop_box)

        # Loaded File Inspector Card
        self._file_card = QFrame()
        self._file_card.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL2};
                border: 1px solid {C.BORDER_B};
                border-radius: 4px;
                padding: 6px;
            }}
        """)
        self._file_card.hide()
        fc_lay = QHBoxLayout(self._file_card)
        fc_lay.setContentsMargins(6, 4, 6, 4)
        fc_lay.setSpacing(8)

        self._fc_icon = QLabel("📄")
        self._fc_icon.setFont(QFont("Segoe UI Emoji", 14))
        self._fc_icon.setStyleSheet("border: none; background: transparent;")
        fc_lay.addWidget(self._fc_icon)

        meta_col = QVBoxLayout()
        meta_col.setSpacing(1)
        self._fc_name = QLabel("document.pdf")
        self._fc_name.setFont(font_hud(7, bold=True))
        self._fc_name.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        meta_col.addWidget(self._fc_name)

        self._fc_meta = QLabel("2.4 MB · READY")
        self._fc_meta.setFont(font_tech(6))
        self._fc_meta.setStyleSheet(f"color: {C.GREEN}; border: none; background: transparent;")
        meta_col.addWidget(self._fc_meta)
        fc_lay.addLayout(meta_col, stretch=1)

        self._fc_remove = QPushButton("✕")
        self._fc_remove.setFixedSize(22, 22)
        self._fc_remove.setFont(font_hud(7, bold=True))
        self._fc_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fc_remove.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_DIM};
                border: 1px solid {C.BORDER}; border-radius: 2px;
            }}
            QPushButton:hover {{ color: {C.RED}; border-color: {C.RED}; background: rgba(255, 56, 100, 0.15); }}
        """)
        self._fc_remove.clicked.connect(self.clear_file)
        fc_lay.addWidget(self._fc_remove)

        self.addWidget(self._file_card)

    def current_file(self) -> str | None:
        return self._current_file

    def clear_file(self):
        self._current_file = None
        self._file_card.hide()
        self._drop_box.show()

    def set_file(self, path: str):
        if not path or not os.path.exists(path):
            return
        self._current_file = path
        p = Path(path)
        cat = _file_category(p)
        icon, cat_name = _FILE_ICONS.get(cat, _FILE_ICONS["unknown"])
        size = _fmt_size(p.stat().st_size)

        self._fc_icon.setText(icon)
        self._fc_name.setText(p.name[:28])
        self._fc_meta.setText(f"{cat_name} · {size} · READY")
        self._drop_box.hide()
        self._file_card.show()
        self.file_selected.emit(path)

    def _browse_file(self):
        fn, _ = QFileDialog.getOpenFileName(
            self,
            "Select File for SHINTO",
            str(Path.home()),
            "All Files (*.*);;Images (*.png *.jpg *.jpeg *.webp);;Documents (*.pdf *.txt *.docx *.md);;Code (*.py *.js *.json *.html)"
        )
        if fn:
            self.set_file(fn)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._drop_box.setStyleSheet(f"""
                QFrame {{
                    background: {C.PRI_GHO};
                    border: 2px solid {C.PRI};
                    border-radius: 4px;
                }}
            """)

    def dragLeaveEvent(self, e):
        self._drop_box.setStyleSheet(f"""
            QFrame {{
                background: {C.DARK};
                border: 1px dashed {C.PRI_DIM};
                border-radius: 4px;
            }}
        """)

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path and os.path.isfile(path):
                self.set_file(path)
        e.acceptProposedAction()
