"""
ui/components/ai_core.py — Holographic Neural AI Core for SHINTO — MARK LI.
Multi-layered 60 FPS canvas with neural network nodes, particle physics,
waveform visualizer, and 8 reactive visual states.
"""
from __future__ import annotations

import math
import random
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QRadialGradient,
    QLinearGradient, QConicalGradient, QPainterPath, QFont, QPixmap
)
from PyQt6.QtWidgets import QWidget, QSizePolicy

from ui.tokens import C, qcol, font_hud, font_tech


class AICore(QWidget):
    """
    State-of-the-art Holographic Neural AI Core.
    """
    def __init__(
        self,
        face_path: str = "face.png",
        assistant_name: str = "SHINTO",
        parent: QWidget | None = None
    ):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMinimumSize(280, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._assistant_name = assistant_name
        self._state = "IDLE"  # IDLE, LISTENING, THINKING, PROCESSING, RESPONDING, EXECUTING, SPEAKING, ERROR
        self.muted = False
        self.speaking = False

        # Animation state variables
        self._tick = 0
        self._last_time = time.time()
        self._ring_angles = [0.0, 120.0, 240.0, 45.0]
        self._core_scale = 1.0
        self._target_scale = 1.0
        self._glow_intensity = 0.5
        self._target_glow = 0.5
        self._pulses: list[float] = [0.0, 40.0, 80.0]
        self._particles: list[list[float]] = []  # [x, y, vx, vy, life, max_life, color_type]
        self._neural_nodes: list[tuple[float, float, float]] = []  # [angle, radius_ratio, phase]
        
        # Audio simulation waveform
        self._wave_history: list[float] = [0.0] * 36

        # Initialize neural nodes
        random.seed(42)
        for _ in range(16):
            self._neural_nodes.append((
                random.uniform(0, 2 * math.pi),
                random.uniform(0.35, 0.72),
                random.uniform(0, 2 * math.pi)
            ))
        random.seed()

        # Optional avatar face image
        self._face_px: QPixmap | None = None
        self._load_face(face_path)

        # 60 FPS Render Timer (~16.6ms)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animation_step)
        self._timer.start(16)

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, val: str):
        val = (val or "IDLE").upper()
        if val in ("SLEEPING", "INITIALISING"):
            val = "IDLE"
        self._state = val
        self.speaking = (val == "SPEAKING")
        self.update()

    def _load_face(self, path: str):
        try:
            p = Path(path)
            if not p.exists():
                return
            from PIL import Image, ImageDraw
            import io
            img = Image.open(str(p)).convert("RGBA")
            sz = min(img.size)
            img = img.resize((sz, sz), Image.LANCZOS)
            mk = Image.new("L", (sz, sz), 0)
            ImageDraw.Draw(mk).ellipse((2, 2, sz - 2, sz - 2), fill=255)
            img.putalpha(mk)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            px = QPixmap()
            px.loadFromData(buf.getvalue())
            self._face_px = px
        except Exception:
            self._face_px = None

    def _animation_step(self):
        self._tick += 1
        now = time.time()
        dt = max(0.001, min(0.1, now - self._last_time))
        self._last_time = now

        # Update core scaling and glow targets based on state
        if self._state == "SPEAKING":
            self._target_scale = 1.06 + math.sin(self._tick * 0.25) * 0.08
            self._target_glow = 0.85 + math.sin(self._tick * 0.3) * 0.15
        elif self._state == "LISTENING":
            self._target_scale = 1.02 + math.sin(self._tick * 0.15) * 0.04
            self._target_glow = 0.75 + math.sin(self._tick * 0.2) * 0.1
        elif self._state in ("THINKING", "PROCESSING"):
            self._target_scale = 1.0 + math.sin(self._tick * 0.2) * 0.05
            self._target_glow = 0.7 + math.sin(self._tick * 0.4) * 0.2
        elif self._state == "EXECUTING":
            self._target_scale = 1.04 + math.sin(self._tick * 0.3) * 0.06
            self._target_glow = 0.8
        elif self._state == "ERROR":
            self._target_scale = 1.02 + (1.0 if (self._tick % 20 < 10) else -0.02) * 0.03
            self._target_glow = 0.9
        else:  # IDLE
            self._target_scale = 1.0 + math.sin(self._tick * 0.04) * 0.02
            self._target_glow = 0.45 + math.sin(self._tick * 0.04) * 0.15

        # Smooth interpolation
        lerp_speed = 0.2
        self._core_scale += (self._target_scale - self._core_scale) * lerp_speed
        self._glow_intensity += (self._target_glow - self._glow_intensity) * lerp_speed

        # Ring rotations
        speed_mult = 2.4 if self._state in ("THINKING", "PROCESSING") else (1.8 if self._state == "SPEAKING" else 1.0)
        self._ring_angles[0] = (self._ring_angles[0] + 0.6 * speed_mult) % 360
        self._ring_angles[1] = (self._ring_angles[1] - 0.9 * speed_mult) % 360
        self._ring_angles[2] = (self._ring_angles[2] + 1.4 * speed_mult) % 360
        self._ring_angles[3] = (self._ring_angles[3] - 0.4 * speed_mult) % 360

        # Pulse waves expansion
        fw = min(self.width(), self.height())
        max_pulse = fw * 0.48
        pulse_speed = 3.5 if self._state == "SPEAKING" else (2.0 if self._state == "LISTENING" else 1.2)
        self._pulses = [p + pulse_speed for p in self._pulses if p + pulse_speed < max_pulse]
        if len(self._pulses) < 3 and random.random() < (0.08 if self._state in ("SPEAKING", "LISTENING") else 0.02):
            self._pulses.append(fw * 0.18)

        # Particle generation & physics
        cx, cy = self.width() / 2, self.height() / 2
        if random.random() < (0.6 if self._state in ("THINKING", "SPEAKING", "PROCESSING") else 0.2):
            ang = random.uniform(0, 2 * math.pi)
            init_r = fw * random.uniform(0.15, 0.32)
            spd = random.uniform(0.6, 2.0)
            col_type = "cyan" if self._state != "ERROR" else "red"
            if self._state in ("PROCESSING", "RESPONDING") and random.random() < 0.4:
                col_type = "magenta"
            self._particles.append([
                cx + math.cos(ang) * init_r,
                cy + math.sin(ang) * init_r,
                math.cos(ang) * spd,
                math.sin(ang) * spd,
                1.0,   # life
                1.0,   # max life
                1 if col_type == "cyan" else (2 if col_type == "magenta" else 3)
            ])

        # Step particles
        updated_particles = []
        for p in self._particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 0.02
            if p[4] > 0:
                updated_particles.append(p)
        self._particles = updated_particles

        # Audio waveform update
        for i in range(len(self._wave_history)):
            if self._state == "SPEAKING":
                self._wave_history[i] = 0.2 + 0.8 * abs(math.sin(self._tick * 0.3 + i * 0.45))
            elif self._state == "LISTENING":
                self._wave_history[i] = 0.15 + 0.5 * abs(math.sin(self._tick * 0.18 + i * 0.3))
            else:
                self._wave_history[i] = 0.05 + 0.05 * math.sin(self._tick * 0.05 + i * 0.2)

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), qcol(C.BG))

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        fw = min(w, h)

        # 1. Background Futuristic Tech Grid
        p.setPen(QPen(qcol(C.BORDER, 50), 1))
        grid_step = 32
        for gx in range(int(cx % grid_step), w, grid_step):
            p.drawLine(gx, 0, gx, h)
        for gy in range(int(cy % grid_step), h, grid_step):
            p.drawLine(0, gy, w, gy)

        # 2. Concentric Target Crosshairs
        p.setPen(QPen(qcol(C.PRI, 30), 1, Qt.PenStyle.DashLine))
        p.drawLine(int(cx - fw * 0.46), int(cy), int(cx + fw * 0.46), int(cy))
        p.drawLine(int(cx), int(cy - fw * 0.46), int(cx), int(cy + fw * 0.46))

        # 3. Expanding Energy Pulse Waves
        pulse_col = qcol(C.RED if self._state == "ERROR" else C.PRI)
        for pr in self._pulses:
            alpha = max(0, int(180 * (1.0 - (pr / (fw * 0.48)))))
            pulse_pen = QPen(qcol(pulse_col.name(), alpha), 1.2)
            p.setPen(pulse_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), pr, pr)

        # 4. Outer HUD Ring with Angle Brackets & Ticks
        r_outer = fw * 0.42
        p.setPen(QPen(qcol(C.BORDER_B, 160), 1))
        p.drawEllipse(QPointF(cx, cy), r_outer, r_outer)

        # Draw outer tick marks
        p.setPen(QPen(qcol(C.PRI, 180), 1.5))
        for deg in range(0, 360, 15):
            rad = math.radians(deg + self._ring_angles[3])
            len_tick = 8 if (deg % 45 == 0) else 4
            x1 = cx + math.cos(rad) * (r_outer - len_tick)
            y1 = cy + math.sin(rad) * (r_outer - len_tick)
            x2 = cx + math.cos(rad) * r_outer
            y2 = cy + math.sin(rad) * r_outer
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # 5. Segmented Rotating HUD Arcs
        r_mid1 = fw * 0.36
        arc_pen = QPen(qcol(C.PRI, 200), 2.5)
        p.setPen(arc_pen)
        p.drawArc(
            int(cx - r_mid1), int(cy - r_mid1), int(r_mid1 * 2), int(r_mid1 * 2),
            int((self._ring_angles[0]) * 16), 65 * 16
        )
        p.drawArc(
            int(cx - r_mid1), int(cy - r_mid1), int(r_mid1 * 2), int(r_mid1 * 2),
            int((self._ring_angles[0] + 180) * 16), 65 * 16
        )

        r_mid2 = fw * 0.32
        p.setPen(QPen(qcol(C.SEC if self._state != "ERROR" else C.RED, 180), 1.5, Qt.PenStyle.DashLine))
        p.drawArc(
            int(cx - r_mid2), int(cy - r_mid2), int(r_mid2 * 2), int(r_mid2 * 2),
            int((self._ring_angles[1]) * 16), 110 * 16
        )
        p.drawArc(
            int(cx - r_mid2), int(cy - r_mid2), int(r_mid2 * 2), int(r_mid2 * 2),
            int((self._ring_angles[1] + 180) * 16), 110 * 16
        )

        # 6. Audio Waveform Reactive Ring (Listening / Speaking)
        r_wave = fw * 0.28
        p.setPen(QPen(qcol(C.ACC if self._state == "SPEAKING" else C.PRI, 220), 2.0))
        n_bars = len(self._wave_history)
        for i, val in enumerate(self._wave_history):
            ang = (2 * math.pi / n_bars) * i + math.radians(self._ring_angles[2])
            bar_len = val * (fw * 0.05)
            x1 = cx + math.cos(ang) * (r_wave - bar_len / 2)
            y1 = cy + math.sin(ang) * (r_wave - bar_len / 2)
            x2 = cx + math.cos(ang) * (r_wave + bar_len / 2)
            y2 = cy + math.sin(ang) * (r_wave + bar_len / 2)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # 7. Neural Interconnect Synapses & Nodes
        node_pts = []
        for ang, r_ratio, phase in self._neural_nodes:
            cur_ang = ang + math.sin(self._tick * 0.02 + phase) * 0.2
            cur_r = (fw * r_ratio * 0.38) * self._core_scale
            nx = cx + math.cos(cur_ang) * cur_r
            ny = cy + math.sin(cur_ang) * cur_r
            node_pts.append((nx, ny))

        # Connect nearby nodes with cyan energy lines
        p.setPen(QPen(qcol(C.PRI, 60), 1))
        for i in range(len(node_pts)):
            for j in range(i + 1, len(node_pts)):
                d = math.hypot(node_pts[i][0] - node_pts[j][0], node_pts[i][1] - node_pts[j][1])
                if d < fw * 0.22:
                    line_alpha = int(90 * (1.0 - d / (fw * 0.22)))
                    p.setPen(QPen(qcol(C.PRI, line_alpha), 1))
                    p.drawLine(int(node_pts[i][0]), int(node_pts[i][1]), int(node_pts[j][0]), int(node_pts[j][1]))

        # Draw node points
        for nx, ny in node_pts:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(qcol(C.PRI, 200)))
            p.drawEllipse(QPointF(nx, ny), 2.5, 2.5)

        # 8. Particle Field
        for px, py, _, _, life, _, c_type in self._particles:
            alpha = int(255 * life)
            col = qcol(C.PRI if c_type == 1 else (C.ACC if c_type == 2 else C.RED), alpha)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(col))
            p.drawEllipse(QPointF(px, py), 1.8, 1.8)

        # 9. Central Neural Core (Sphere + Glow)
        r_core = (fw * 0.19) * self._core_scale
        grad = QRadialGradient(cx, cy, r_core * 1.5)
        glow_c = qcol(C.RED if self._state == "ERROR" else (C.ACC if self._state == "RESPONDING" else C.PRI))
        grad.setColorAt(0.0, qcol(glow_c.name(), int(180 * self._glow_intensity)))
        grad.setColorAt(0.5, qcol(C.SEC if self._state != "ERROR" else C.RED, int(100 * self._glow_intensity)))
        grad.setColorAt(1.0, qcol(C.BG, 0))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r_core * 1.5, r_core * 1.5)

        # Inner solid core circle
        p.setPen(QPen(qcol(glow_c.name(), 220), 2))
        p.setBrush(QBrush(qcol(C.PANEL2, 235)))
        p.drawEllipse(QPointF(cx, cy), r_core, r_core)

        # 10. Center Display: SHINTO + Dynamic State Badge
        p.setPen(QPen(qcol(C.WHITE), 1))
        p.setFont(font_hud(11, bold=True))
        p.drawText(
            QRectF(cx - r_core, cy - r_core * 0.45, r_core * 2, r_core * 0.5),
            Qt.AlignmentFlag.AlignCenter,
            self._assistant_name.upper()
        )

        # Dynamic Status Text
        state_text = self._state
        if self.muted:
            state_text = "MUTED"
        elif self._state == "IDLE":
            state_text = "READY"

        status_col = C.RED if (self._state == "ERROR" or self.muted) else (C.ACC if self._state == "SPEAKING" else C.GREEN)
        p.setPen(QPen(qcol(status_col), 1))
        p.setFont(font_tech(7, bold=True))
        p.drawText(
            QRectF(cx - r_core, cy + r_core * 0.05, r_core * 2, r_core * 0.4),
            Qt.AlignmentFlag.AlignCenter,
            f"●  {state_text}"
        )
