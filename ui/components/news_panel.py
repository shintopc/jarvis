"""
ui/components/news_panel.py — Futuristic News Feed Panel for SHINTO — MARK LI.
Aggregates live Malayalam headlines (Asianet, Manorama, Mathrubhumi, Madhyamam, etc.)
alongside World, India, and Tech feeds with interactive cards.
"""
from __future__ import annotations

import threading
import webbrowser
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QButtonGroup
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.glass_panel import GlassPanel


class NewsCard(QFrame):
    """Futuristic News Story Card supporting Malayalam and English typography."""
    def __init__(self, title: str, snippet: str, source: str, url: str, time_str: str = "", parent=None):
        super().__init__(parent)
        self._url = url
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C.PANEL2};
                border: 1px solid {C.BORDER};
                border-radius: 6px;
                padding: 4px;
            }}
            QFrame:hover {{
                border: 1px solid {C.PRI};
                background: #0C1E32;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        # Meta row (Source pill + Timestamp + Arrow)
        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)

        clean_source = (source or "MALAYALAM NEWS").upper()
        src_lbl = QLabel(clean_source)
        src_lbl.setFont(font_hud(7, bold=True))
        src_lbl.setStyleSheet(f"""
            color: {C.PRI};
            background: {C.PRI_GHO};
            border: 1px solid {C.PRI_DIM};
            border-radius: 3px;
            padding: 1px 5px;
        """)
        meta_row.addWidget(src_lbl)

        if time_str:
            time_lbl = QLabel(f"🕒 {time_str}")
            time_lbl.setFont(font_tech(7))
            time_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
            meta_row.addWidget(time_lbl)

        meta_row.addStretch()

        arrow = QLabel("↗")
        arrow.setFont(font_hud(9, bold=True))
        arrow.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        meta_row.addWidget(arrow)
        lay.addLayout(meta_row)

        # Headline
        title_lbl = QLabel(title)
        title_lbl.setFont(font_body(9, bold=True))
        title_lbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent; line-height: 1.3;")
        title_lbl.setWordWrap(True)
        lay.addWidget(title_lbl)

        # Snippet / Meta
        if snippet:
            snip_lbl = QLabel(snippet[:120] + ("..." if len(snippet) > 120 else ""))
            snip_lbl.setFont(font_tech(7))
            snip_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
            snip_lbl.setWordWrap(True)
            lay.addWidget(snip_lbl)

        lay.addStretch()

    def mousePressEvent(self, e):
        if self._url:
            webbrowser.open(self._url)


class NewsPanel(GlassPanel):
    """
    Futuristic News Panel featuring live Malayalam headlines with category filters
    (Malayalam, World, India, Tech).
    """
    _news_loaded_sig = pyqtSignal(list, str)

    CATEGORIES = [
        ("malayalam", "🔴 മലയാളം", "മലയാളം പ്രധാന വാർത്തകൾ (ALL MALAYALAM HEADLINES)"),
        ("world",     "🌐 ലോകം (WORLD)", "GLOBAL HEADLINES"),
        ("india",     "🇮🇳 ഇന്ത്യ (INDIA)", "NATIONAL HEADLINES"),
        ("tech",      "💻 ടെക് (TECH)", "TECHNOLOGY & AI NEWS"),
    ]

    def __init__(self, parent: QWidget | None = None):
        self._current_cat = "malayalam"

        # Right header controls (Category switcher + Refresh)
        header_ctrl = QWidget()
        h_lay = QHBoxLayout(header_ctrl)
        h_lay.setContentsMargins(0, 0, 0, 0)
        h_lay.setSpacing(4)

        self._cat_btns: dict[str, QPushButton] = {}
        for cat_id, cat_label, _ in self.CATEGORIES:
            btn = QPushButton(cat_label)
            btn.setFont(font_tech(7, bold=True))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, cid=cat_id: self.select_category(cid))
            h_lay.addWidget(btn)
            self._cat_btns[cat_id] = btn

        # Refresh button
        self._btn_refresh = QPushButton("⟳")
        self._btn_refresh.setToolTip("Refresh headlines")
        self._btn_refresh.setFont(font_tech(8, bold=True))
        self._btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 3px; padding: 2px 7px;
            }}
            QPushButton:hover {{ background: {C.PRI_GHO}; border-color: {C.PRI}; }}
        """)
        self._btn_refresh.clicked.connect(self.fetch_news)
        h_lay.addWidget(self._btn_refresh)

        super().__init__(
            title="TOP NEWS",
            subtitle="മലയാളം പ്രധാന വാർത്തകൾ (ALL MALAYALAM HEADLINES)",
            show_corners=True,
            parent=parent,
            header_right_widget=header_ctrl
        )

        self._update_cat_button_styles()
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
                background: {C.BG}; height: 5px; border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {C.BORDER_B}; border-radius: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {C.PRI};
            }}
        """)

        self._container = QWidget()
        self._container_layout = QHBoxLayout(self._container)
        self._container_layout.setContentsMargins(2, 2, 2, 2)
        self._container_layout.setSpacing(10)

        # Loading / status indicator
        self._loading_lbl = QLabel("Scanning Malayalam live feeds...")
        self._loading_lbl.setFont(font_tech(8))
        self._loading_lbl.setStyleSheet(f"color: {C.TEXT_MED}; padding: 10px;")
        self._container_layout.addWidget(self._loading_lbl)

        self._scroll.setWidget(self._container)
        self.addWidget(self._scroll)

        # Load initial Malayalam news
        self.fetch_news()

    def _update_cat_button_styles(self):
        for cat_id, btn in self._cat_btns.items():
            is_active = (cat_id == self._current_cat)
            btn.setChecked(is_active)
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {C.PRI_GHO}; color: {C.PRI};
                        border: 1px solid {C.PRI}; border-radius: 3px;
                        padding: 2px 7px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; color: {C.TEXT_MED};
                        border: 1px solid {C.BORDER}; border-radius: 3px;
                        padding: 2px 7px;
                    }}
                    QPushButton:hover {{
                        color: {C.WHITE}; border-color: {C.PRI_DIM}; background: rgba(255,255,255,0.04);
                    }}
                """)

    def select_category(self, cat_id: str):
        if self._current_cat == cat_id:
            return
        self._current_cat = cat_id
        self._update_cat_button_styles()

        # Update subtitle
        for cid, _, sub_text in self.CATEGORIES:
            if cid == cat_id:
                self.set_subtitle(sub_text)
                break

        self.fetch_news()

    def fetch_news(self):
        cat = self._current_cat
        cat_display = "Malayalam live feeds" if cat == "malayalam" else f"{cat.upper()} feeds"
        self._loading_lbl.setText(f"Scanning {cat_display} (Asianet, Manorama, Mathrubhumi...)...")
        self._loading_lbl.show()

        def _worker():
            try:
                items = []
                if cat == "malayalam":
                    from actions.web_search import _fetch_malayalam_news
                    items = _fetch_malayalam_news(max_results=12)
                elif cat == "world":
                    from actions.web_search import _ddg_news
                    items = _ddg_news("top world news today", max_results=8)
                elif cat == "india":
                    from actions.web_search import _ddg_news
                    items = _ddg_news("top national news headlines india today", max_results=8)
                elif cat == "tech":
                    from actions.web_search import _ddg_news
                    items = _ddg_news("latest technology news headlines", max_results=8)

                self._news_loaded_sig.emit(items or [], cat)
            except Exception as e:
                print(f"[NewsPanel] Error fetching {cat} news: {e}")
                self._news_loaded_sig.emit([], cat)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_news_loaded(self, items: list[dict], cat: str):
        # Ignore responses if category switched during fetch
        if cat != self._current_cat:
            return

        # Clear container
        while self._container_layout.count():
            item = self._container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            lbl = QLabel("No news stories available at the moment. Click ⟳ to retry.")
            lbl.setFont(font_tech(8))
            lbl.setStyleSheet(f"color: {C.TEXT_DIM}; padding: 10px;")
            self._container_layout.addWidget(lbl)
            return

        for it in items:
            card = NewsCard(
                title=it.get("title", "News Headline"),
                snippet=it.get("snippet", ""),
                source=it.get("source", "MALAYALAM NEWS"),
                url=it.get("url", ""),
                time_str=it.get("time", "")
            )
            card.setFixedWidth(280)
            self._container_layout.addWidget(card)
        self._container_layout.addStretch()
