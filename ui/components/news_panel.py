"""
ui/components/news_panel.py — Futuristic World News Panel for SHINTO — MARK LI.
Connects to real DuckDuckGo / Gemini news backend with interactive news cards.
"""
from __future__ import annotations

import threading
import webbrowser
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.glass_panel import GlassPanel


class NewsCard(QFrame):
    """Futuristic News Story Card."""
    def __init__(self, title: str, snippet: str, source: str, url: str, parent=None):
        super().__init__(parent)
        self._url = url
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL2};
                border: 1px solid {C.BORDER};
                border-radius: 4px;
                padding: 6px;
            }}
            QFrame:hover {{
                border: 1px solid {C.PRI};
                background: #0D1F33;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(3)

        # Meta row (Source + Arrow)
        meta_row = QHBoxLayout()
        src_lbl = QLabel(source.upper() if source else "GLOBAL NEWS")
        src_lbl.setFont(font_hud(6, bold=True))
        src_lbl.setStyleSheet(f"color: {C.PRI}; border: none; background: transparent;")
        meta_row.addWidget(src_lbl)
        meta_row.addStretch()

        arrow = QLabel("↗")
        arrow.setFont(font_hud(8, bold=True))
        arrow.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        meta_row.addWidget(arrow)
        lay.addLayout(meta_row)

        # Headline
        title_lbl = QLabel(title)
        title_lbl.setFont(font_body(8, bold=True))
        title_lbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        title_lbl.setWordWrap(True)
        lay.addWidget(title_lbl)

        # Snippet
        if snippet:
            snip_lbl = QLabel(snippet[:120] + ("..." if len(snippet) > 120 else ""))
            snip_lbl.setFont(font_tech(7))
            snip_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
            snip_lbl.setWordWrap(True)
            lay.addWidget(snip_lbl)

    def mousePressEvent(self, e):
        if self._url:
            webbrowser.open(self._url)


class NewsPanel(GlassPanel):
    """Futuristic World News panel that populates real-time stories from backend."""
    _news_loaded_sig = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = None):
        # Header Refresh button
        self._btn_refresh = QPushButton("⟳ REFRESH")
        self._btn_refresh.setFont(font_tech(6, bold=True))
        self._btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 2px; padding: 2px 6px;
            }}
            QPushButton:hover {{ background: {C.PRI_GHO}; border-color: {C.PRI}; }}
        """)

        super().__init__(
            title="NEWS",
            subtitle="TOP WORLD HEADLINES",
            show_corners=True,
            parent=parent,
            header_right_widget=self._btn_refresh
        )
        self._btn_refresh.clicked.connect(self.fetch_news)
        self._news_loaded_sig.connect(self._on_news_loaded)

        # Scroll Area for News Cards
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:horizontal {{
                background: {C.BG}; height: 4px; border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {C.BORDER_B}; border-radius: 2px;
            }}
        """)

        self._container = QWidget()
        self._container_layout = QHBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(8)

        # Placeholder loading state
        self._loading_lbl = QLabel("Fetching world intelligence...")
        self._loading_lbl.setFont(font_tech(7))
        self._loading_lbl.setStyleSheet(f"color: {C.TEXT_DIM};")
        self._container_layout.addWidget(self._loading_lbl)

        self._scroll.setWidget(self._container)
        self.addWidget(self._scroll)

        # Initial background fetch
        self.fetch_news()

    def fetch_news(self):
        self._loading_lbl.setText("Scanning global feeds...")
        self._loading_lbl.show()

        def _worker():
            try:
                from actions.web_search import _ddg_news
                items = _ddg_news("top world news today", max_results=6)
                if items:
                    self._news_loaded_sig.emit(items)
            except Exception as e:
                print(f"[NewsPanel] Error fetching news: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def _on_news_loaded(self, items: list[dict]):
        # Clear container
        while self._container_layout.count():
            item = self._container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            lbl = QLabel("No news stories available.")
            lbl.setFont(font_tech(7))
            lbl.setStyleSheet(f"color: {C.TEXT_DIM};")
            self._container_layout.addWidget(lbl)
            return

        for it in items:
            card = NewsCard(
                title=it.get("title", "News Headline"),
                snippet=it.get("snippet", ""),
                source=it.get("source", "WORLD NEWS"),
                url=it.get("url", "")
            )
            card.setFixedWidth(240)
            self._container_layout.addWidget(card)
        self._container_layout.addStretch()
