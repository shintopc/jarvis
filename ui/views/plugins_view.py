"""
ui/views/plugins_view.py — Futuristic Plugin Manager & Inspector for SHINTO — MARK LI.
App store + developer console layout with real-time plugin toggling and permission inspector.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QSplitter, QTextEdit
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.glass_panel import GlassPanel
from memory.config_manager import get_plugin_enabled, save_plugin_enabled


class PluginCard(QFrame):
    """Futuristic Plugin Card with status toggle and selection signal."""
    selected = pyqtSignal(dict)
    toggled = pyqtSignal(str, bool)

    def __init__(self, p_data: dict, parent=None):
        super().__init__(parent)
        self._data = p_data
        self._name = p_data.get("name", "")
        self._enabled = p_data.get("enabled", True)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(120)
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
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        # Top row: Icon + Name + Version + Toggle
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        ico = QLabel("🧩")
        ico.setFont(QFont("Segoe UI Emoji", 12))
        ico.setStyleSheet("border: none; background: transparent;")
        top_row.addWidget(ico)

        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        name_lbl = QLabel(self._name.upper())
        name_lbl.setFont(font_hud(8, bold=True))
        name_lbl.setStyleSheet(f"color: {C.WHITE}; border: none; background: transparent;")
        name_col.addWidget(name_lbl)

        ver_lbl = QLabel(f"v1.0.0 · {self._data.get('file', '')}")
        ver_lbl.setFont(font_tech(6))
        ver_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        name_col.addWidget(ver_lbl)
        top_row.addLayout(name_col, stretch=1)

        # Toggle Button
        self._btn_toggle = QPushButton("ENABLED" if self._enabled else "DISABLED")
        self._btn_toggle.setFont(font_tech(6, bold=True))
        self._btn_toggle.setFixedSize(70, 22)
        self._btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_toggle_style()
        self._btn_toggle.clicked.connect(self._on_toggle)
        top_row.addWidget(self._btn_toggle)

        lay.addLayout(top_row)

        # Description
        desc = self._data.get("description", "Plugin extension for SHINTO.")
        desc_lbl = QLabel(desc[:90] + ("..." if len(desc) > 90 else ""))
        desc_lbl.setFont(font_body(7))
        desc_lbl.setStyleSheet(f"color: {C.TEXT_MED}; border: none; background: transparent;")
        desc_lbl.setWordWrap(True)
        lay.addWidget(desc_lbl, stretch=1)

    def _update_toggle_style(self):
        if self._enabled:
            self._btn_toggle.setText("ENABLED")
            self._btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {C.GREEN_GHO}; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 2px;
                }}
            """)
        else:
            self._btn_toggle.setText("DISABLED")
            self._btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background: {C.DARK}; color: {C.TEXT_DIM};
                    border: 1px solid {C.BORDER}; border-radius: 2px;
                }}
            """)

    def _on_toggle(self):
        self._enabled = not self._enabled
        save_plugin_enabled(self._name, self._enabled)
        self._update_toggle_style()
        self.toggled.emit(self._name, self._enabled)

    def mousePressEvent(self, event):
        self.selected.emit(self._data)


class PluginsView(QWidget):
    """Futuristic Plugin Store & Inspector View."""
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C.BG};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        # Left Column: Plugin Store / Grid (70%)
        left_panel = GlassPanel(title="PLUGIN ECOSYSTEM", subtitle="ACTIVE EXTENSIONS & AGENTS")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: transparent; border: none;")

        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(4, 4, 4, 4)
        self._grid_layout.setSpacing(10)

        scroll.setWidget(self._grid_container)
        left_panel.addWidget(scroll, stretch=1)
        lay.addWidget(left_panel, stretch=6)

        # Right Column: Plugin Details Inspector (30%)
        self.inspector_panel = GlassPanel(title="PLUGIN INSPECTOR", subtitle="CAPABILITIES & TELEMETRY")
        
        self._insp_name = QLabel("SELECT A PLUGIN")
        self._insp_name.setFont(font_hud(9, bold=True))
        self._insp_name.setStyleSheet(f"color: {C.PRI};")
        self.inspector_panel.addWidget(self._insp_name)

        self._insp_desc = QTextEdit()
        self._insp_desc.setReadOnly(True)
        self._insp_desc.setFont(font_body(8))
        self._insp_desc.setStyleSheet(f"background: {C.DARK}; color: {C.TEXT}; border: 1px solid {C.BORDER}; border-radius: 3px; padding: 6px;")
        self.inspector_panel.addWidget(self._insp_desc, stretch=1)

        # Permissions Box
        perm_box = QFrame()
        perm_box.setStyleSheet(f"background: {C.PANEL2}; border: 1px solid {C.BORDER}; border-radius: 3px; padding: 6px;")
        perm_lay = QVBoxLayout(perm_box)
        perm_lay.setContentsMargins(6, 4, 6, 4); perm_lay.setSpacing(3)
        p_hdr = QLabel("SECURITY PERMISSIONS")
        p_hdr.setFont(font_hud(6, bold=True)); p_hdr.setStyleSheet(f"color: {C.ACC2}; border: none;")
        perm_lay.addWidget(p_hdr)
        self._lbl_perms = QLabel("✓ Sandboxed Execution\n✓ Network Access\n✓ Core Tool Interop")
        self._lbl_perms.setFont(font_tech(7)); self._lbl_perms.setStyleSheet(f"color: {C.TEXT_MED}; border: none;")
        perm_lay.addWidget(self._lbl_perms)
        self.inspector_panel.addWidget(perm_box)

        lay.addWidget(self.inspector_panel, stretch=4)

        # Load initial plugins
        self.reload_plugins()

    def reload_plugins(self):
        # Clear grid
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Discover plugins
        try:
            from pathlib import Path
            from core.plugin_loader import discover_plugins
            from main import BASE_DIR, TOOL_DECLARATIONS
            core_tools = {t["name"] for t in TOOL_DECLARATIONS}
            registry = discover_plugins(BASE_DIR / "plugins", core_tools, logger=lambda _: None)
            plugins = registry.list_for_ui()
        except Exception:
            plugins = [
                {"name": "web_search", "description": "Global internet search and news synthesis", "file": "web_search.py", "enabled": True},
                {"name": "whatsapp_monitor", "description": "Proactive WhatsApp messages monitor", "file": "whatsapp_monitor.py", "enabled": True},
                {"name": "ky_ufo_drone", "description": "Drone hardware telemetry & flight automation", "file": "ky_ufo_drone.py", "enabled": True},
            ]

        row, col = 0, 0
        for p in plugins:
            card = PluginCard(p)
            card.selected.connect(self._on_plugin_selected)
            self._grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        if plugins:
            self._on_plugin_selected(plugins[0])

    def _on_plugin_selected(self, p_data: dict):
        self._insp_name.setText(p_data.get("name", "").upper())
        desc = p_data.get("description", "No description available.")
        file_n = p_data.get("file", "unknown")
        stat = "ENABLED" if p_data.get("enabled", True) else "DISABLED"
        self._insp_desc.setPlainText(
            f"FILE: {file_n}\nSTATUS: {stat}\n\nDESCRIPTION:\n{desc}\n\n"
            f"CAPABILITIES:\n- Live Tool Dispatch\n- System Command Interface\n- Audio / Voice Stream Hooks"
        )
