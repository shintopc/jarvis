"""
ui/components/system_monitor.py — Futuristic System Monitor for SHINTO — MARK LI.
Features circular HUD gauges, animated sparklines, and hardware telemetry.
"""
from __future__ import annotations

import platform
import threading
import time
from collections import deque

import psutil
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QLinearGradient, QConicalGradient
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QFrame, QSizePolicy
)

from ui.tokens import C, qcol, font_hud, font_tech
from ui.components.glass_panel import GlassPanel


class RadialGauge(QWidget):
    """Futuristic circular HUD gauge with animated needle/arc and percentage."""
    def __init__(
        self,
        label: str,
        color_hex: str = C.PRI,
        unit: str = "%",
        parent: QWidget | None = None
    ):
        super().__init__(parent)
        self.setMinimumSize(64, 70)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._label = label
        self._color = color_hex
        self._unit = unit
        self._val = 0.0
        self._target_val = 0.0
        self._history = deque([0.0] * 18, maxlen=18)

    def set_value(self, val: float):
        self._target_val = max(0.0, val)
        self._history.append(self._target_val)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Smooth value interpolation
        self._val += (self._target_val - self._val) * 0.35

        w, h = self.width(), self.height()
        cx = w / 2.0
        cy = max(24.0, h * 0.44)
        r = max(18.0, min(w * 0.4, (h - 22) * 0.46))

        # Background track arc (240 degrees from 150 to -30)
        start_angle = -210 * 16
        span_angle = -240 * 16
        
        p.setPen(QPen(qcol(C.BORDER, 160), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), start_angle, span_angle)

        # Value active arc
        pct = min(1.0, self._val / 100.0) if self._unit == "%" else min(1.0, self._val / 50.0)
        active_span = int(span_angle * pct)

        active_col = C.RED if self._val > 90 and self._unit == "%" else self._color
        pen = QPen(qcol(active_col), 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), start_angle, active_span)

        # Center value text
        p.setPen(QPen(qcol(C.WHITE), 1))
        p.setFont(font_hud(max(7, int(r * 0.28)), bold=True))
        val_str = f"{int(self._val)}" if self._unit == "%" else f"{self._val:.1f}"
        if self._val < 0:
            val_str = "N/A"
        p.drawText(QRectF(cx - r, cy - r * 0.35, r * 2, r * 0.7), Qt.AlignmentFlag.AlignCenter, val_str)

        p.setPen(QPen(qcol(C.TEXT_DIM), 1))
        p.setFont(font_tech(max(5, int(r * 0.2))))
        p.drawText(QRectF(cx - r, cy + r * 0.2, r * 2, r * 0.5), Qt.AlignmentFlag.AlignCenter, self._unit)

        # Bottom Metric Label
        p.setPen(QPen(qcol(self._color), 1))
        p.setFont(font_hud(7, bold=True))
        p.drawText(QRectF(0, h - 16, w, 14), Qt.AlignmentFlag.AlignCenter, self._label)


class SparklineWidget(QWidget):
    """Mini technical history sparkline graph."""
    def __init__(self, color_hex: str = C.PRI, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self._color = color_hex
        self._history = deque([10.0] * 30, maxlen=30)

    def add_value(self, val: float):
        self._history.append(max(0.0, val))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        p.fillRect(self.rect(), qcol(C.PANEL2, 180))

        # Grid lines
        p.setPen(QPen(qcol(C.BORDER, 80), 1, Qt.PenStyle.DotLine))
        p.drawLine(0, int(h / 2), w, int(h / 2))

        if len(self._history) < 2:
            return

        max_v = max(100.0, max(self._history))
        pts = []
        dx = w / (len(self._history) - 1)
        for i, val in enumerate(self._history):
            px = i * dx
            py = h - 2 - (val / max_v) * (h - 4)
            pts.append(QPointF(px, py))

        # Draw filled gradient area
        path = QPainterPath()
        path.moveTo(0, h)
        for pt in pts:
            path.lineTo(pt)
        path.lineTo(w, h)
        path.closeSubpath()

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, qcol(self._color, 80))
        grad.setColorAt(1.0, qcol(self._color, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawPath(path)

        # Draw graph line
        line_pen = QPen(qcol(self._color, 220), 1.5)
        p.setPen(line_pen)
        for i in range(len(pts) - 1):
            p.drawLine(pts[i], pts[i + 1])


class SystemMonitorCard(QWidget):
    """Combines RadialGauge + Sparkline + Technical Telemetry."""
    def __init__(self, label: str, color_hex: str, unit: str = "%", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {C.PANEL_ALT}; border: 1px solid {C.BORDER}; border-radius: 4px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        top_row = QHBoxLayout()
        self.gauge = RadialGauge(label, color_hex, unit)
        top_row.addWidget(self.gauge)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        self.lbl_cur = QLabel("0.0%")
        self.lbl_cur.setFont(font_hud(8, bold=True))
        self.lbl_cur.setStyleSheet(f"color: {C.WHITE}; background: transparent; border: none;")
        info_col.addWidget(self.lbl_cur)

        self.lbl_stat = QLabel("OPTIMAL")
        self.lbl_stat.setFont(font_tech(6, bold=True))
        self.lbl_stat.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
        info_col.addWidget(self.lbl_stat)
        top_row.addLayout(info_col)

        lay.addLayout(top_row)

        self.sparkline = SparklineWidget(color_hex)
        lay.addWidget(self.sparkline)

    def update_metric(self, val: float):
        self.gauge.set_value(val)
        self.sparkline.add_value(val)
        if val < 0:
            self.lbl_cur.setText("N/A")
            self.lbl_stat.setText("OFFLINE")
            self.lbl_stat.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent; border: none;")
        else:
            unit_s = self.gauge._unit
            self.lbl_cur.setText(f"{val:.1f}{unit_s}" if unit_s != "%" else f"{int(val)}%")
            if val > 90:
                self.lbl_stat.setText("CRITICAL")
                self.lbl_stat.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")
            elif val > 75:
                self.lbl_stat.setText("HIGH LOAD")
                self.lbl_stat.setStyleSheet(f"color: {C.YELLOW}; background: transparent; border: none;")
            else:
                self.lbl_stat.setText("OPTIMAL")
                self.lbl_stat.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")


class SystemMonitorPanel(GlassPanel):
    """Complete System Monitor view container with CPU, RAM, Network, GPU, and OS info."""
    def __init__(self, parent: QWidget | None = None):
        super().__init__(title="SYS MONITOR", subtitle="HARDWARE TELEMETRY", parent=parent)

        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(8)

        self.card_cpu = SystemMonitorCard("CPU", C.PRI, "%")
        self.card_ram = SystemMonitorCard("RAM", C.ACC2, "%")
        self.card_net = SystemMonitorCard("NET", C.GREEN, "MB/s")
        self.card_gpu = SystemMonitorCard("GPU", C.ACC, "%")

        self._grid.addWidget(self.card_cpu, 0, 0)
        self._grid.addWidget(self.card_ram, 0, 1)
        self._grid.addWidget(self.card_net, 1, 0)
        self._grid.addWidget(self.card_gpu, 1, 1)

        self.addWidget(QWidget())  # Spacer container
        self.content_layout().addLayout(self._grid)

        # Telemetry info box (Uptime, Procs, OS, Status)
        info_frame = QFrame()
        info_frame.setStyleSheet(f"background: {C.PANEL2}; border: 1px solid {C.BORDER}; border-radius: 4px;")
        info_lay = QGridLayout(info_frame)
        info_lay.setContentsMargins(8, 6, 8, 6)
        info_lay.setSpacing(4)

        def _info_item(lbl_t: str, val_t: str, val_col: str = C.TEXT):
            w = QWidget()
            wl = QVBoxLayout(w); wl.setContentsMargins(0, 0, 0, 0); wl.setSpacing(1)
            t = QLabel(lbl_t); t.setFont(font_tech(6)); t.setStyleSheet(f"color: {C.TEXT_DIM}; border: none;")
            v = QLabel(val_t); v.setFont(font_hud(7, bold=True)); v.setStyleSheet(f"color: {val_col}; border: none;")
            wl.addWidget(t); wl.addWidget(v)
            return w, v

        w_up, self.lbl_uptime = _info_item("UPTIME", "00:00:00", C.GREEN)
        w_pr, self.lbl_procs  = _info_item("PROCESSES", "0", C.PRI)
        os_name = "WIN 11" if platform.system() == "Windows" else platform.system().upper()
        w_os, self.lbl_os     = _info_item("OS ARCH", os_name, C.ACC2)
        w_st, self.lbl_status = _info_item("SYSTEM STATUS", "ALL SYSTEMS STABLE", C.GREEN)

        info_lay.addWidget(w_up, 0, 0)
        info_lay.addWidget(w_pr, 0, 1)
        info_lay.addWidget(w_os, 1, 0)
        info_lay.addWidget(w_st, 1, 1)

        self.addWidget(info_frame)

    def update_telemetry(self, cpu: float, ram: float, net: float, gpu: float, uptime_s: float, procs: int):
        self.card_cpu.update_metric(cpu)
        self.card_ram.update_metric(ram)
        self.card_net.update_metric(net)
        self.card_gpu.update_metric(gpu)

        h = int(uptime_s // 3600)
        m = int((uptime_s % 3600) // 60)
        s = int(uptime_s % 60)
        self.lbl_uptime.setText(f"{h:02d}:{m:02d}:{s:02d}")
        self.lbl_procs.setText(str(procs))
