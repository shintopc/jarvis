"""
ui/views/dashboard_view.py — Main AI Command Center Dashboard for SHINTO — MARK LI.
Fully responsive, multi-axis resizable layout using interactive QSplitters and scalable HUD cards.
"""
from __future__ import annotations

import time
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSplitter, QStackedWidget, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QTextEdit
)

from ui.tokens import C, font_hud, font_tech, font_body
from ui.components.ai_core import AICore
from ui.components.system_monitor import SystemMonitorPanel
from ui.components.activity_log import ActivityLog
from ui.components.command_input import CommandConsole
from ui.components.file_uploader import FileUploader
from ui.components.news_panel import NewsPanel
from ui.components.quick_commands import QuickCommandsPanel
from ui.components.glass_panel import GlassPanel


class PipelineStageIndicator(QWidget):
    """Vertical 3-stage AI Pipeline indicator (🎙 LISTEN → 🧠 THINK → ⚙ ACT)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(78)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"background: {C.PANEL2}; border: 1px solid {C.BORDER}; border-radius: 4px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 8, 6, 8)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hdr = QLabel("PIPELINE")
        hdr.setFont(font_hud(6, bold=True))
        hdr.setStyleSheet(f"color: {C.TEXT_DIM}; border: none; background: transparent;")
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(hdr)

        def _stage_box(icon_s: str, label_s: str):
            w = QFrame()
            w.setStyleSheet(f"background: {C.DARK}; border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px;")
            wl = QVBoxLayout(w); wl.setContentsMargins(2, 2, 2, 2); wl.setSpacing(1)
            wl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic = QLabel(icon_s); ic.setFont(QFont("Segoe UI Emoji", 9)); ic.setAlignment(Qt.AlignmentFlag.AlignCenter); ic.setStyleSheet("border: none;")
            lb = QLabel(label_s); lb.setFont(font_hud(6, bold=True)); lb.setAlignment(Qt.AlignmentFlag.AlignCenter); lb.setStyleSheet(f"color: {C.TEXT_MED}; border: none;")
            wl.addWidget(ic); wl.addWidget(lb)
            return w, lb

        self.w_lis, self.lbl_lis = _stage_box("🎙", "LISTEN")
        self.w_thk, self.lbl_thk = _stage_box("🧠", "THINK")
        self.w_act, self.lbl_act = _stage_box("⚙", "ACT")

        lay.addWidget(self.w_lis)
        arrow1 = QLabel("↓"); arrow1.setFont(font_tech(7)); arrow1.setStyleSheet(f"color: {C.TEXT_DIM}; border: none;"); arrow1.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(arrow1)
        lay.addWidget(self.w_thk)
        arrow2 = QLabel("↓"); arrow2.setFont(font_tech(7)); arrow2.setStyleSheet(f"color: {C.TEXT_DIM}; border: none;"); arrow2.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(arrow2)
        lay.addWidget(self.w_act)

        self.set_stage("IDLE")

    def set_stage(self, state: str):
        state = (state or "IDLE").upper()
        # Reset styles
        for w, lb in [(self.w_lis, self.lbl_lis), (self.w_thk, self.lbl_thk), (self.w_act, self.lbl_act)]:
            w.setStyleSheet(f"background: {C.DARK}; border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px;")
            lb.setStyleSheet(f"color: {C.TEXT_MED}; border: none;")

        if state in ("LISTENING", "MUTED"):
            self.w_lis.setStyleSheet(f"background: {C.PRI_GHO}; border: 1px solid {C.PRI}; border-radius: 3px; padding: 4px;")
            self.lbl_lis.setStyleSheet(f"color: {C.PRI}; font-weight: bold; border: none;")
        elif state in ("THINKING", "PROCESSING"):
            self.w_thk.setStyleSheet(f"background: {C.ACC_GHO}; border: 1px solid {C.ACC}; border-radius: 3px; padding: 4px;")
            self.lbl_thk.setStyleSheet(f"color: {C.ACC}; font-weight: bold; border: none;")
        elif state in ("EXECUTING", "RESPONDING", "SPEAKING"):
            self.w_act.setStyleSheet(f"background: {C.GREEN_GHO}; border: 1px solid {C.GREEN}; border-radius: 3px; padding: 4px;")
            self.lbl_act.setStyleSheet(f"color: {C.GREEN}; font-weight: bold; border: none;")


class DashboardView(QWidget):
    """Main Futuristic AI Command Center View with interactive multi-axis resizing."""
    command_submitted = pyqtSignal(str)
    file_selected = pyqtSignal(str)
    interrupt_triggered = pyqtSignal()
    mic_toggled = pyqtSignal()

    def __init__(
        self,
        face_path: str = "face.png",
        assistant_name: str = "SHINTO",
        parent: QWidget | None = None
    ):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C.BG};")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(0)

        # ── 1. Master Horizontal Splitter (Left, Center, Right) ─────────────
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter.setStyleSheet(f"""
            QSplitter::handle:horizontal {{
                background: {C.BORDER};
                width: 4px;
                margin: 2px 2px;
                border-radius: 2px;
            }}
            QSplitter::handle:horizontal:hover {{
                background: {C.PRI};
            }}
            QSplitter::handle:vertical {{
                background: {C.BORDER};
                height: 4px;
                margin: 2px 2px;
                border-radius: 2px;
            }}
            QSplitter::handle:vertical:hover {{
                background: {C.PRI};
            }}
        """)

        # ── LEFT COLUMN: System Monitor + Quick Actions ─────────────────────
        self._left_splitter = QSplitter(Qt.Orientation.Vertical)
        self._left_splitter.setMinimumWidth(240)
        self._left_splitter.setMaximumWidth(500)

        self.sys_monitor = SystemMonitorPanel()
        self.sys_monitor.setMinimumHeight(180)
        self._left_splitter.addWidget(self.sys_monitor)

        self.quick_commands = QuickCommandsPanel()
        self.quick_commands.setMinimumHeight(160)
        self.quick_commands.action_triggered.connect(self.command_submitted.emit)
        self._left_splitter.addWidget(self.quick_commands)

        self._left_splitter.setStretchFactor(0, 3)
        self._left_splitter.setStretchFactor(1, 2)
        self._main_splitter.addWidget(self._left_splitter)

        # ── CENTER COLUMN: AI Core + Briefing + World News ──────────────────
        self._center_splitter = QSplitter(Qt.Orientation.Vertical)
        self._center_splitter.setMinimumWidth(320)

        # Core Area (AI Core Canvas + Side Pipeline Stages)
        core_container = GlassPanel(title="NEURAL AI CORE", subtitle="HOLOGRAPHIC QUANTUM RUNTIME")
        core_container.setMinimumHeight(240)
        core_inner_lay = QHBoxLayout()
        core_inner_lay.setContentsMargins(0, 0, 0, 0)
        core_inner_lay.setSpacing(8)

        self.ai_core = AICore(face_path, assistant_name)
        self.ai_core.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        core_inner_lay.addWidget(self.ai_core, stretch=1)

        self.stage_indicator = PipelineStageIndicator()
        core_inner_lay.addWidget(self.stage_indicator, stretch=0)
        core_container.content_layout().addLayout(core_inner_lay)

        # Live Camera container
        self._cam_cont = QWidget()
        self._cam_cont.setStyleSheet(f"background: {C.DARK}; border: 1px solid {C.PRI}; border-radius: 4px;")
        _cam_v = QVBoxLayout(self._cam_cont); _cam_v.setContentsMargins(0, 0, 0, 0); _cam_v.setSpacing(0)
        _cam_hdr = QHBoxLayout(); _cam_hdr.setContentsMargins(8, 4, 8, 4)
        _cam_title = QLabel("◈  OPTICAL RECOGNITION FEED")
        _cam_title.setFont(font_hud(7, bold=True))
        _cam_title.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        _cam_hdr.addWidget(_cam_title); _cam_hdr.addStretch()
        self._cam_close_btn = QPushButton("✕ CLOSE")
        self._cam_close_btn.setFont(font_tech(6, bold=True))
        self._cam_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cam_close_btn.setStyleSheet(f"color: {C.RED}; background: transparent; border: 1px solid {C.RED}; border-radius: 2px; padding: 2px 6px;")
        _cam_hdr.addWidget(self._cam_close_btn)
        _cam_v.addLayout(_cam_hdr)
        self._cam_live_lbl = QLabel()
        self._cam_live_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cam_live_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        _cam_v.addWidget(self._cam_live_lbl, stretch=1)

        # Stack: 0 = Core container, 1 = Live Camera
        self._core_cam_stack = QStackedWidget()
        self._core_cam_stack.addWidget(core_container)
        self._core_cam_stack.addWidget(self._cam_cont)
        self._center_splitter.addWidget(self._core_cam_stack)

        # Collapsible Briefing Content Panel
        self._content_panel = GlassPanel(title="ഇന്റലിജൻസ് ബ്രീഫിംഗ്", subtitle="തത്സമയ വിവരങ്ങൾ (MALAYALAM BRIEFING)")
        self._content_display = QTextEdit()
        self._content_display.setReadOnly(True)
        self._content_display.setFont(font_body(9))
        self._content_display.setStyleSheet(f"""
            QTextEdit {{
                background: {C.DARK}; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 8px; line-height: 1.4;
            }}
        """)
        self._content_panel.addWidget(self._content_display)
        self._content_panel.hide()
        self._center_splitter.addWidget(self._content_panel)

        # News Panel
        self.news_panel = NewsPanel()
        self.news_panel.setMinimumHeight(140)
        self._center_splitter.addWidget(self.news_panel)

        self._center_splitter.setStretchFactor(0, 5)
        self._center_splitter.setStretchFactor(1, 2)
        self._main_splitter.addWidget(self._center_splitter)

        # ── RIGHT COLUMN: Activity Log + File Upload + Command Console ─────
        self._right_splitter = QSplitter(Qt.Orientation.Vertical)
        self._right_splitter.setMinimumWidth(260)
        self._right_splitter.setMaximumWidth(540)

        self.activity_log = ActivityLog()
        self.activity_log.setMinimumHeight(180)
        self._right_splitter.addWidget(self.activity_log)

        # Bottom container for File Uploader & Command Console
        bottom_right = QWidget()
        br_lay = QVBoxLayout(bottom_right)
        br_lay.setContentsMargins(0, 0, 0, 0)
        br_lay.setSpacing(6)

        self.file_uploader = FileUploader()
        self.file_uploader.file_selected.connect(self.file_selected.emit)
        br_lay.addWidget(self.file_uploader, stretch=1)

        self.command_console = CommandConsole()
        self.command_console.command_submitted.connect(self.command_submitted.emit)
        self.command_console.interrupt_triggered.connect(self.interrupt_triggered.emit)
        self.command_console.mic_toggled.connect(self.mic_toggled.emit)
        br_lay.addWidget(self.command_console, stretch=0)

        self._right_splitter.addWidget(bottom_right)
        self._right_splitter.setStretchFactor(0, 4)
        self._right_splitter.setStretchFactor(1, 3)

        self._main_splitter.addWidget(self._right_splitter)

        # Initial horizontal stretch distribution (Left=3, Center=6, Right=4)
        self._main_splitter.setStretchFactor(0, 3)
        self._main_splitter.setStretchFactor(1, 6)
        self._main_splitter.setStretchFactor(2, 4)

        root_layout.addWidget(self._main_splitter)

    def set_state(self, state: str):
        self.ai_core.state = state
        self.stage_indicator.set_stage(state)

    def set_muted(self, muted: bool):
        self.ai_core.muted = muted
        self.command_console.set_muted(muted)

    def show_content(self, title: str, text: str):
        self._content_panel.set_title(title)
        self._content_display.setPlainText(text)
        self._content_panel.show()
