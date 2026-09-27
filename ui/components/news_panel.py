"""
ui/components/news_panel.py — Futuristic Live Teleprompter News Feed for SHINTO — MARK LI.
Features continuous upward-scrolling bullet headlines with channel-specific background colors,
Malayalam news aggregation (Asianet, Manorama, Mathrubhumi, etc.), and interactive category filters.
"""
from __future__ import annotations

import threading
import webbrowser
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.glass_panel import GlassPanel


# Channel-specific background and accent colors
CHANNEL_THEMES: dict[str, dict[str, str]] = {
    # Top Malayalam News Channels
    "asianet": {
        "bg": "rgba(179, 18, 23, 0.28)",
        "border": "#FF4444",
        "badge_bg": "#B31217",
        "badge_text": "#FFFFFF",
        "bullet": "#FF5252",
        "badge": "ASIANET NEWS",
    },
    "manorama": {
        "bg": "rgba(13, 71, 161, 0.30)",
        "border": "#42A5F5",
        "badge_bg": "#0D47A1",
        "badge_text": "#FFFFFF",
        "bullet": "#64B5F6",
        "badge": "MANORAMA",
    },
    "mathrubhumi": {
        "bg": "rgba(0, 105, 92, 0.30)",
        "border": "#00E676",
        "badge_bg": "#00695C",
        "badge_text": "#FFFFFF",
        "bullet": "#69F0AE",
        "badge": "MATHRUBHUMI",
    },
    "24 news": {
        "bg": "rgba(136, 14, 79, 0.30)",
        "border": "#FF4081",
        "badge_bg": "#880E4F",
        "badge_text": "#FFFFFF",
        "bullet": "#FF80AB",
        "badge": "24 NEWS",
    },
    "twentyfour": {
        "bg": "rgba(136, 14, 79, 0.30)",
        "border": "#FF4081",
        "badge_bg": "#880E4F",
        "badge_text": "#FFFFFF",
        "bullet": "#FF80AB",
        "badge": "24 NEWS",
    },
    "madhyamam": {
        "bg": "rgba(0, 96, 100, 0.30)",
        "border": "#00E5FF",
        "badge_bg": "#006064",
        "badge_text": "#FFFFFF",
        "bullet": "#18FFFF",
        "badge": "MADHYAMAM",
    },
    "reporter": {
        "bg": "rgba(191, 54, 12, 0.30)",
        "border": "#FF6E40",
        "badge_bg": "#BF360C",
        "badge_text": "#FFFFFF",
        "bullet": "#FFAB91",
        "badge": "REPORTER TV",
    },
    "mediaone": {
        "bg": "rgba(26, 35, 126, 0.32)",
        "border": "#536DFE",
        "badge_bg": "#1A237E",
        "badge_text": "#FFFFFF",
        "bullet": "#8C9EFF",
        "badge": "MEDIAONE",
    },
    "deshabhimani": {
        "bg": "rgba(106, 27, 154, 0.30)",
        "border": "#E040FB",
        "badge_bg": "#6A1B9A",
        "badge_text": "#FFFFFF",
        "bullet": "#EA80FC",
        "badge": "DESHABHIMANI",
    },
    "kairali": {
        "bg": "rgba(173, 20, 87, 0.30)",
        "border": "#FF80AB",
        "badge_bg": "#AD1457",
        "badge_text": "#FFFFFF",
        "bullet": "#FF4081",
        "badge": "KAIRALI",
    },
    "doolnews": {
        "bg": "rgba(55, 71, 79, 0.35)",
        "border": "#78909C",
        "badge_bg": "#37474F",
        "badge_text": "#ECEFF1",
        "bullet": "#B0BEC5",
        "badge": "DOOLNEWS",
    },
    "vatican": {
        "bg": "rgba(74, 20, 140, 0.30)",
        "border": "#BA68C8",
        "badge_bg": "#4A148C",
        "badge_text": "#FFFFFF",
        "bullet": "#E1BEE7",
        "badge": "VATICAN NEWS",
    },
    "indian express": {
        "bg": "rgba(38, 50, 56, 0.35)",
        "border": "#90A4AE",
        "badge_bg": "#263238",
        "badge_text": "#FFFFFF",
        "bullet": "#CFD8DC",
        "badge": "IE MALAYALAM",
    },
    # World / National
    "bbc": {
        "bg": "rgba(183, 28, 28, 0.30)",
        "border": "#FF1744",
        "badge_bg": "#B71C1C",
        "badge_text": "#FFFFFF",
        "bullet": "#FF5252",
        "badge": "BBC NEWS",
    },
    "cnn": {
        "bg": "rgba(198, 40, 40, 0.30)",
        "border": "#EF5350",
        "badge_bg": "#C62828",
        "badge_text": "#FFFFFF",
        "bullet": "#FF8A80",
        "badge": "CNN",
    },
    "ndtv": {
        "bg": "rgba(230, 81, 0, 0.30)",
        "border": "#FFA726",
        "badge_bg": "#E65100",
        "badge_text": "#FFFFFF",
        "bullet": "#FFCC80",
        "badge": "NDTV",
    },
    "hindu": {
        "bg": "rgba(13, 71, 161, 0.30)",
        "border": "#2979FF",
        "badge_bg": "#0D47A1",
        "badge_text": "#FFFFFF",
        "bullet": "#82B1FF",
        "badge": "THE HINDU",
    },
    "reuters": {
        "bg": "rgba(230, 81, 0, 0.28)",
        "border": "#FF9100",
        "badge_bg": "#E65100",
        "badge_text": "#FFFFFF",
        "bullet": "#FFD180",
        "badge": "REUTERS",
    },
}

FALLBACK_PALETTES = [
    {"bg": "rgba(22, 119, 255, 0.25)", "border": "#1677FF", "badge_bg": "#0D4CB3", "badge_text": "#FFF", "bullet": "#4096FF"},
    {"bg": "rgba(0, 229, 255, 0.20)",  "border": "#00E5FF", "badge_bg": "#0099B8", "badge_text": "#FFF", "bullet": "#00E5FF"},
    {"bg": "rgba(255, 23, 107, 0.20)", "border": "#FF176B", "badge_bg": "#B30F4B", "badge_text": "#FFF", "bullet": "#FF4D8F"},
    {"bg": "rgba(0, 245, 160, 0.20)",  "border": "#00F5A0", "badge_bg": "#00A86B", "badge_text": "#FFF", "bullet": "#00F5A0"},
    {"bg": "rgba(255, 209, 102, 0.20)","border": "#FFD166", "badge_bg": "#B28900", "badge_text": "#FFF", "bullet": "#FFE082"},
    {"bg": "rgba(156, 39, 176, 0.25)", "border": "#AB47BC", "badge_bg": "#7B1FA2", "badge_text": "#FFF", "bullet": "#CE93D8"},
]


def get_channel_style(source_name: str) -> dict[str, str]:
    """Resolve distinct background, border, and badge color per channel."""
    s_lower = (source_name or "").lower().strip()
    for key, style in CHANNEL_THEMES.items():
        if key in s_lower:
            return style

    # Deterministic palette hash for unseen channels
    idx = abs(hash(s_lower)) % len(FALLBACK_PALETTES)
    style = FALLBACK_PALETTES[idx].copy()
    style["badge"] = (source_name.upper() if source_name else "LIVE NEWS")
    return style


class NewsBulletRow(QFrame):
    """
    Sleek horizontal news bullet row with channel-specific background and glow.
    """
    def __init__(
        self,
        title: str,
        source: str,
        url: str,
        time_str: str = "",
        parent: QWidget | None = None
    ):
        super().__init__(parent)
        self._url = url
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        style = get_channel_style(source)
        badge_name = style.get("badge", (source or "NEWS").upper())

        # Channel-specific background styling
        self.setStyleSheet(f"""
            QFrame {{
                background: {style['bg']};
                border: 1px solid {style['border']};
                border-left: 4px solid {style['border']};
                border-radius: 4px;
            }}
            QFrame:hover {{
                border-color: #FFFFFF;
                border-left: 5px solid {style['border']};
                background: rgba(255, 255, 255, 0.12);
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 12, 6)
        lay.setSpacing(8)

        # Bullet marker
        bullet_lbl = QLabel("●")
        bullet_lbl.setFont(font_tech(8, bold=True))
        bullet_lbl.setStyleSheet(f"color: {style['bullet']}; border: none; background: transparent;")
        lay.addWidget(bullet_lbl)

        # Channel Badge Pill
        badge_lbl = QLabel(f" {badge_name} ")
        badge_lbl.setFont(font_hud(7, bold=True))
        badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {style['badge_bg']};
                color: {style['badge_text']};
                border-radius: 3px;
                padding: 1px 5px;
                font-weight: bold;
                border: none;
            }}
        """)
        lay.addWidget(badge_lbl)

        # Timestamp badge (if available)
        if time_str:
            time_lbl = QLabel(f"[{time_str}]")
            time_lbl.setFont(font_tech(7))
            time_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
            lay.addWidget(time_lbl)

        # Headline text
        title_lbl = QLabel(title)
        title_lbl.setFont(font_body(9, bold=True))
        title_lbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_lbl.setWordWrap(False)
        lay.addWidget(title_lbl, stretch=1)

        # Arrow indicator
        arrow = QLabel("↗")
        arrow.setFont(font_hud(8, bold=True))
        arrow.setStyleSheet(f"color: {style['bullet']}; border: none; background: transparent;")
        lay.addWidget(arrow)

    def mousePressEvent(self, e):
        if self._url:
            webbrowser.open(self._url)


class AutoScrollArea(QScrollArea):
    """
    Vertical scroll area with continuous upward auto-scroll.
    Automatically pauses when hovered so the user can read or click comfortably.
    """
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {C.BG};
                width: 5px;
                border: none;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {C.BORDER_B};
                border-radius: 2px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {C.PRI};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Upward scroll timer (~28 pixels/sec)
        self._paused = False
        self._timer = QTimer(self)
        self._timer.setInterval(35)
        self._timer.timeout.connect(self._scroll_tick)
        self._timer.start()

    def _scroll_tick(self):
        if self._paused:
            return
        sb = self.verticalScrollBar()
        max_val = sb.maximum()
        if max_val <= 0:
            return

        curr = sb.value()
        # Loop infinitely through duplicated list
        if curr >= max_val:
            sb.setValue(0)
        else:
            sb.setValue(curr + 1)

    def enterEvent(self, event):
        # Pause auto-scroll on mouse hover
        self._paused = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Resume auto-scroll on mouse leave
        self._paused = False
        super().leaveEvent(event)

    def toggle_play_pause(self) -> bool:
        """Toggle scroll state. Returns True if now running, False if paused."""
        if self._timer.isActive():
            self._timer.stop()
            return False
        else:
            self._timer.start()
            return True


class NewsPanel(GlassPanel):
    """
    Futuristic World & Malayalam News Panel with continuous upward-scrolling bullet headlines.
    Each channel features a distinct background color and interactive category filters.
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

        # Right header controls (Category switcher + Play/Pause + Refresh)
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

        # Pause / Play toggle button
        self._btn_pause = QPushButton("⏸")
        self._btn_pause.setToolTip("Pause / Resume continuous upward scroll")
        self._btn_pause.setFont(font_tech(8, bold=True))
        self._btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_pause.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_MED};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 2px 6px;
            }}
            QPushButton:hover {{ background: {C.PRI_GHO}; color: {C.PRI}; border-color: {C.PRI}; }}
        """)
        self._btn_pause.clicked.connect(self._on_toggle_scroll)
        h_lay.addWidget(self._btn_pause)

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

        # Continuous Upward Scroll Area
        self._scroll = AutoScrollArea(self)

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(4, 4, 4, 4)
        self._container_layout.setSpacing(6)

        # Placeholder loading state
        self._loading_lbl = QLabel("Scanning Malayalam live feeds (Asianet, Manorama, Mathrubhumi...)...")
        self._loading_lbl.setFont(font_tech(8))
        self._loading_lbl.setStyleSheet(f"color: {C.TEXT_MED}; padding: 10px;")
        self._container_layout.addWidget(self._loading_lbl)

        self._scroll.setWidget(self._container)
        self.addWidget(self._scroll)

        # Initial fetch
        self.fetch_news()

    def _on_toggle_scroll(self):
        is_running = self._scroll.toggle_play_pause()
        self._btn_pause.setText("⏸" if is_running else "▶")

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
                    items = _fetch_malayalam_news(max_results=16)
                elif cat == "world":
                    from actions.web_search import _ddg_news
                    items = _ddg_news("top world news today", max_results=12)
                elif cat == "india":
                    from actions.web_search import _ddg_news
                    items = _ddg_news("top national news headlines india today", max_results=12)
                elif cat == "tech":
                    from actions.web_search import _ddg_news
                    items = _ddg_news("latest technology news headlines", max_results=12)

                self._news_loaded_sig.emit(items or [], cat)
            except Exception as e:
                print(f"[NewsPanel] Error fetching {cat} news: {e}")
                self._news_loaded_sig.emit([], cat)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_news_loaded(self, items: list[dict], cat: str):
        if cat != self._current_cat:
            return

        # Clear existing container rows
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

        # Duplicate items to create an infinite seamless loop
        display_items = items + items

        for it in display_items:
            row = NewsBulletRow(
                title=it.get("title", "News Headline"),
                source=it.get("source", "MALAYALAM NEWS"),
                url=it.get("url", ""),
                time_str=it.get("time", "")
            )
            self._container_layout.addWidget(row)

        # Reset scroll to top
        self._scroll.verticalScrollBar().setValue(0)
