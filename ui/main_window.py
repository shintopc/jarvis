"""
ui/main_window.py — Master Application Window for SHINTO — MARK LI.
Hosts the futuristic command center shell, view transitions, telemetry threads, and global shortcuts.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QPixmap, QImage
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QSizePolicy, QMessageBox
)

from ui.tokens import (
    C, font_hud, font_tech, apply_ui_accent,
    DEFAULT_UI_COLOR
)
from ui.layout.top_navigation import TopNavigation
from ui.layout.left_sidebar import LeftSidebar
from ui.layout.status_bar import StatusBar

from ui.views.dashboard_view import DashboardView
from ui.views.chat_view import ChatView
from ui.views.plugins_view import PluginsView
from ui.views.automation_view import AutomationView
from ui.views.tools_view import ToolsView
from ui.views.settings_view import SettingsView

from ui.overlays.setup_overlay import SetupOverlay
from ui.overlays.customize_overlay import CustomizeOverlay
from ui.overlays.remote_overlay import RemoteKeyOverlay

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
API_FILE   = CONFIG_DIR / "api_keys.json"

def _read_config() -> dict:
    try:
        return json.loads(API_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── Windows GPU via NVML DLL (ctypes zero-subprocess) ─────────────────────────
_nvml_lib: object = None
_nvml_ok:  object = None

def _nvml_gpu_windows() -> float:
    global _nvml_lib, _nvml_ok
    if _nvml_ok is False:
        return -1.0
    try:
        import ctypes
        class _Util(ctypes.Structure):
            _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]
        if _nvml_lib is None:
            for dll_name in ("nvml", r"C:\Windows\System32\nvml.dll"):
                try:
                    lib = ctypes.WinDLL(dll_name)
                    lib.nvmlInit_v2()
                    _nvml_lib = lib
                    break
                except Exception:
                    continue
        if _nvml_lib is None:
            import pynvml
            pynvml.nvmlInit()
            h = pynvml.nvmlDeviceGetHandleByIndex(0)
            _nvml_ok = True
            return float(pynvml.nvmlDeviceGetUtilizationRates(h).gpu)

        dev = ctypes.c_void_p()
        _nvml_lib.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(dev))
        util = _Util()
        _nvml_lib.nvmlDeviceGetUtilizationRates(dev, ctypes.byref(util))
        _nvml_ok = True
        return float(util.gpu)
    except Exception:
        _nvml_ok = False
        return -1.0


class _SysTelemetry:
    def __init__(self):
        self.cpu = 0.0
        self.mem = 0.0
        self.net = 0.0
        self.gpu = -1.0
        self._lock = threading.Lock()
        self._last_net = psutil.net_io_counters()
        self._last_t = time.time()
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self._running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory().percent
                now = time.time()
                dt = max(0.001, now - self._last_t)
                nc = psutil.net_io_counters()
                net_mb = ((nc.bytes_sent - self._last_net.bytes_sent) + (nc.bytes_recv - self._last_net.bytes_recv)) / (dt * 1024 * 1024)
                self._last_net = nc
                self._last_t = now

                gpu = _nvml_gpu_windows() if platform.system() == "Windows" else -1.0
                with self._lock:
                    self.cpu = cpu
                    self.mem = mem
                    self.net = max(0.0, net_mb)
                    self.gpu = gpu
            except Exception:
                pass
            time.sleep(1.5)

    def snapshot(self) -> tuple[float, float, float, float]:
        with self._lock:
            return self.cpu, self.mem, self.net, self.gpu


_telemetry = _SysTelemetry()


class MainWindow(QMainWindow):
    """Futuristic Sci-Fi HUD AI Operating System Window."""
    _log_sig        = pyqtSignal(str)
    _state_sig      = pyqtSignal(str)
    _content_sig    = pyqtSignal(str, str)
    _reconfig_sig   = pyqtSignal()
    _camera_sig     = pyqtSignal(bytes)
    _cam_stream_sig = pyqtSignal(bool)
    _cam_frame_sig  = pyqtSignal(bytes)

    def __init__(self, face_path: str = "face.png"):
        super().__init__()
        self._face_path = face_path

        # Read config
        cfg = _read_config()
        self._assistant_name = (cfg.get("assistant_name") or "SHINTO").strip()
        ui_color = (cfg.get("ui_color") or "").strip()
        if ui_color:
            apply_ui_accent(ui_color)

        self.setWindowTitle(f"{self._assistant_name.upper()} — MARK LI")
        self.setMinimumSize(1080, 720)
        self.resize(1280, 800)

        # Center on screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

        # Public callback hooks for JarvisLive
        self.on_text_command   = None
        self.on_remote_clicked = None
        self.on_interrupt      = None
        self.get_plugins       = None

        self._muted = False
        self._ready = self._check_config()
        self._start_time = time.time()
        self._setup_overlay: SetupOverlay | None = None
        self._remote_overlay: RemoteKeyOverlay | None = None

        # Build Main Frame
        central = QWidget()
        central.setStyleSheet(f"background: {C.BG};")
        self.setCentralWidget(central)

        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # 1. Top Navigation
        self.top_nav = TopNavigation(self._assistant_name)
        self.top_nav.nav_tab_changed.connect(self._switch_view_by_tab)
        self.top_nav.command_entered.connect(self._dispatch_command)
        root_lay.addWidget(self.top_nav)

        # 2. Middle Body: Left Sidebar + Stacked View Area
        body_lay = QHBoxLayout()
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        self.sidebar = LeftSidebar()
        self.sidebar.item_selected.connect(self._switch_view_by_nav)
        body_lay.addWidget(self.sidebar, stretch=0)

        # Stacked Views
        self.stack = QStackedWidget()
        self.view_dashboard  = DashboardView(face_path, self._assistant_name)
        self.view_chat       = ChatView(self._assistant_name)
        self.view_plugins    = PluginsView()
        self.view_automation = AutomationView()
        self.view_tools      = ToolsView()
        self.view_settings   = SettingsView()

        # Wire view signals
        self.view_dashboard.command_submitted.connect(self._dispatch_command)
        self.view_dashboard.interrupt_triggered.connect(self._dispatch_interrupt)
        self.view_dashboard.mic_toggled.connect(self._toggle_mute)
        self.view_dashboard._cam_close_btn.clicked.connect(self.stop_camera_stream)

        self.view_chat.message_sent.connect(self._dispatch_command)
        self.view_tools.command_triggered.connect(self._dispatch_command)
        self.view_settings.settings_updated.connect(self._on_settings_updated)

        self.stack.addWidget(self.view_dashboard)   # 0
        self.stack.addWidget(self.view_chat)        # 1
        self.stack.addWidget(self.view_plugins)     # 2
        self.stack.addWidget(self.view_automation)  # 3
        self.stack.addWidget(self.view_tools)       # 4
        self.stack.addWidget(self.view_settings)    # 5

        body_lay.addWidget(self.stack, stretch=1)
        root_lay.addLayout(body_lay, stretch=1)

        # 3. Status Bar
        self.status_bar = StatusBar(self._assistant_name)
        root_lay.addWidget(self.status_bar)

        # Thread signals
        self._log_sig.connect(self._on_log)
        self._state_sig.connect(self._on_state)
        self._content_sig.connect(self._on_content)
        self._reconfig_sig.connect(self._show_setup)
        self._camera_sig.connect(self._on_camera_frame)
        self._cam_stream_sig.connect(self._on_cam_stream)
        self._cam_frame_sig.connect(self._on_cam_frame)

        # Telemetry Timer (2s)
        self._metric_timer = QTimer(self)
        self._metric_timer.timeout.connect(self._tick_metrics)
        self._metric_timer.start(2000)

        # Global Keyboard Shortcuts
        self._setup_shortcuts()

        # Initial check
        if not self._ready:
            QTimer.singleShot(100, self._show_setup)

    def _setup_shortcuts(self):
        # ESC -> Interrupt
        QShortcut(QKeySequence("Escape"), self, self._dispatch_interrupt)
        # F4 -> Mute
        QShortcut(QKeySequence("F4"), self, self._toggle_mute)
        # F11 -> Fullscreen
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)
        # Ctrl+K -> Global Command Input
        QShortcut(QKeySequence("Ctrl+K"), self, lambda: self.top_nav._cmd_input.setFocus())
        # Ctrl+L -> Chat
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.top_nav.select_tab("chat"))
        # Ctrl+P -> Plugins
        QShortcut(QKeySequence("Ctrl+P"), self, lambda: self.top_nav.select_tab("plugins"))
        # Ctrl+, -> Settings
        QShortcut(QKeySequence("Ctrl+,"), self, lambda: self.top_nav.select_tab("settings"))

    def _check_config(self) -> bool:
        if not API_FILE.exists():
            return False
        try:
            d = json.loads(API_FILE.read_text(encoding="utf-8"))
            return bool(d.get("gemini_api_key"))
        except Exception:
            return False

    def _show_setup(self):
        self._ready = False
        ov = SetupOverlay(self.centralWidget())
        ov.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
        ov.done.connect(self._on_setup_done)
        ov.show()
        self._setup_overlay = ov

    def _on_setup_done(self, key: str, os_name: str):
        cfg = _read_config()
        cfg["gemini_api_key"] = key
        cfg["os_system"] = os_name
        os.makedirs(CONFIG_DIR, exist_ok=True)
        API_FILE.write_text(json.dumps(cfg, indent=4), encoding="utf-8")
        self._ready = True
        if self._setup_overlay:
            self._setup_overlay.hide()
            self._setup_overlay = None
        self._on_log(f"SYS: Authentication configured. {self._assistant_name} online.")

    def _switch_view_by_tab(self, tab_id: str):
        mapping = {
            "dashboard": 0,
            "chat": 1,
            "plugins": 2,
            "automation": 3,
            "tools": 4,
            "settings": 5,
        }
        idx = mapping.get(tab_id, 0)
        self.stack.setCurrentIndex(idx)
        self.sidebar.set_active_item(tab_id)

    def _switch_view_by_nav(self, nav_id: str):
        mapping = {
            "dashboard": 0,
            "chat": 1,
            "plugins": 2,
            "automation": 3,
            "tools": 4,
            "settings": 5,
        }
        idx = mapping.get(nav_id, 0)
        self.stack.setCurrentIndex(idx)
        self.top_nav.set_active_tab(nav_id)

    def _dispatch_command(self, text: str):
        if not text:
            return
        self.view_dashboard.activity_log.append_log(f"You: {text}")
        self.view_dashboard.command_console.set_processing_status(text[:36])
        self._on_state("THINKING")

        # Sync user query to Chat View if not already originated there
        if getattr(self.view_chat, "_last_sent_user_msg", None) != text:
            self.view_chat.add_message("YOU", text)
        self.view_chat._last_sent_user_msg = None

        if self.on_text_command:
            threading.Thread(target=self.on_text_command, args=(text,), daemon=True).start()

    def _dispatch_interrupt(self):
        self.view_dashboard.activity_log.append_log("SYS: Interrupt requested [ESC].")
        self.view_dashboard.command_console.set_processing_status("")
        if self.on_interrupt:
            try:
                self.on_interrupt()
            except Exception as e:
                print(f"[MainWindow] Interrupt error: {e}")

    def _toggle_mute(self):
        self._muted = not self._muted
        self.view_dashboard.set_muted(self._muted)
        self.status_bar.set_muted(self._muted)
        if self._muted:
            self._on_state("MUTED")
            self.view_dashboard.activity_log.append_log("SYS: Microphone muted.")
        else:
            self._on_state("LISTENING")
            self.view_dashboard.activity_log.append_log("SYS: Microphone active.")

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _tick_metrics(self):
        cpu, mem, net, gpu = _telemetry.snapshot()
        upt = time.time() - self._start_time
        try:
            procs = len(psutil.pids())
        except Exception:
            procs = 0
        self.view_dashboard.sys_monitor.update_telemetry(cpu, mem, net, gpu, upt, procs)

    def _on_log(self, text: str):
        self.view_dashboard.activity_log.append_log(text)
        if ":" in text:
            prefix, msg = text.split(":", 1)
            prefix_up = prefix.strip().upper()
            msg = msg.strip()
            if prefix_up in (self._assistant_name.upper(), "JARVIS", "SHINTO"):
                self.view_chat.add_message(self._assistant_name, msg)
                self.view_dashboard.command_console.set_processing_status("")
            elif prefix_up in ("YOU", "USER"):
                if getattr(self.view_chat, "_last_sent_user_msg", None) != msg:
                    self.view_chat.add_message("YOU", msg)
                self.view_chat._last_sent_user_msg = None
        elif any(k in text.lower() for k in ("interrupt", "error", "err:")):
            self.view_dashboard.command_console.set_processing_status("")

    def _on_state(self, state: str):
        self.view_dashboard.set_state(state)
        self.status_bar.set_state(state)

    def _on_content(self, title: str, text: str):
        self.view_dashboard.show_content(title, text)

    def _on_camera_frame(self, img_bytes: bytes):
        pass

    def _on_cam_stream(self, active: bool):
        if active:
            self.view_dashboard._core_cam_stack.setCurrentIndex(1)
        else:
            self.view_dashboard._core_cam_stack.setCurrentIndex(0)

    def _on_cam_frame(self, img_bytes: bytes):
        try:
            px = QPixmap()
            px.loadFromData(img_bytes)
            self.view_dashboard._cam_live_lbl.setPixmap(
                px.scaled(
                    self.view_dashboard._cam_live_lbl.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation
                )
            )
        except Exception:
            pass

    def start_camera_stream(self):
        self._cam_stream_sig.emit(True)

    def stop_camera_stream(self):
        self._cam_stream_sig.emit(False)

    def notify_phone_connected(self):
        if self._remote_overlay and self._remote_overlay.isVisible():
            self._remote_overlay.mark_connected()

    def _on_settings_updated(self):
        cfg = _read_config()
        self._assistant_name = (cfg.get("assistant_name") or "SHINTO").strip()
        self.setWindowTitle(f"{self._assistant_name.upper()} — MARK LI")
        self.top_nav._title_lbl.setText(self._assistant_name.upper())
        self.status_bar._lbl_ver.setText(f"{self._assistant_name.upper()} v1.0.0")
        self.view_dashboard.ai_core._assistant_name = self._assistant_name
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._setup_overlay and self._setup_overlay.isVisible():
            self._setup_overlay.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
