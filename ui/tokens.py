"""
ui/tokens.py — Design system tokens and styling constants for SHINTO — MARK LI.
Futuristic AI Command Center theme with dark glassmorphism, electric cyan, and neon magenta.
"""
from __future__ import annotations

import colorsys
from PyQt6.QtGui import QColor, QFont

class C:
    """Design System Color Palette (SHINTO NEON default)"""
    # Backgrounds
    BG          = "#020611"
    BG_ALT      = "#030817"
    BG_SURFACE  = "#050B14"
    
    # Panels & Glass
    PANEL       = "#07111F"
    PANEL_ALT   = "#081525"
    PANEL_GLASS = "rgba(7, 17, 31, 0.78)"
    PANEL2      = "#0A1628"
    DARK        = "#030A14"
    BAR_BG      = "#040D1A"
    
    # Borders
    BORDER      = "#0E2A47"
    BORDER_B    = "#164972"
    BORDER_A    = "#00E5FF"
    BORDER_GLOW = "rgba(0, 229, 255, 0.4)"
    
    # Primary & Secondary Neon
    PRI         = "#00E5FF"   # Electric Cyan
    PRI_DIM     = "#0099B8"
    PRI_GHO     = "rgba(0, 229, 255, 0.08)"
    PRI_GLOW    = "rgba(0, 229, 255, 0.25)"
    
    SEC         = "#1677FF"   # Electric Blue
    SEC_DIM     = "#0D4CB3"
    SEC_GHO     = "rgba(22, 119, 255, 0.08)"
    
    # Accent & Energy
    ACC         = "#FF176B"   # Neon Magenta
    ACC_DIM     = "#B30F4B"
    ACC_GHO     = "rgba(255, 23, 107, 0.12)"
    ACC2        = "#FFD166"   # Electric Gold / Amber
    
    # Status Colors
    GREEN       = "#00F5A0"   # Active / Online / Success
    GREEN_D     = "#00A86B"
    GREEN_GHO   = "rgba(0, 245, 160, 0.12)"
    
    YELLOW      = "#FFD166"   # Warning
    RED         = "#FF3864"   # Error / Critical
    MUTED_C     = "#FF3864"
    
    # Typography
    TEXT        = "#E8F7FF"   # Primary High-contrast
    TEXT_MED    = "#7FA9C7"   # Secondary Technical
    TEXT_DIM    = "#47647C"   # Muted / Meta
    WHITE       = "#FFFFFF"


_HUE_LINKED = (
    "BG", "BG_ALT", "BG_SURFACE", "PANEL", "PANEL_ALT", "PANEL2",
    "BORDER", "BORDER_B", "BORDER_A",
    "PRI", "PRI_DIM", "TEXT", "TEXT_DIM", "TEXT_MED",
    "WHITE", "DARK", "BAR_BG",
)
_PALETTE_DEFAULTS: dict[str, str] = {k: getattr(C, k) for k in _HUE_LINKED}
DEFAULT_UI_COLOR = _PALETTE_DEFAULTS["PRI"]


def apply_ui_accent(accent_hex: str) -> bool:
    """Recalculate dynamic theme palette based on accent hue shift."""
    accent_hex = (accent_hex or "").strip().lower()
    if not (accent_hex.startswith("#") and len(accent_hex) == 7):
        return False
    try:
        int(accent_hex[1:], 16)
    except ValueError:
        return False

    def _hsv(h: str) -> tuple[float, float, float]:
        r = int(h[1:3], 16) / 255
        g = int(h[3:5], 16) / 255
        b = int(h[5:7], 16) / 255
        return colorsys.rgb_to_hsv(r, g, b)

    base_h = _hsv(_PALETTE_DEFAULTS["PRI"])[0]
    acc_h, acc_s, _ = _hsv(accent_hex)
    dh = acc_h - base_h
    grey = acc_s < 0.08

    for key, hex0 in _PALETTE_DEFAULTS.items():
        h, s, v = _hsv(hex0)
        if grey:
            s *= 0.15
        r, g, b = colorsys.hsv_to_rgb((h + dh) % 1.0, s, v)
        setattr(C, key, "#{:02x}{:02x}{:02x}".format(
            int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)))
    return True


def current_palette() -> dict[str, str]:
    return {k: getattr(C, k) for k in _HUE_LINKED}


def qcol(h: str, a: int = 255) -> QColor:
    c = QColor(h)
    c.setAlpha(a)
    return c


# Font helpers
def _resolve_font(
    candidates: list[str],
    size: int,
    bold: bool = False,
    monospace: bool = False,
    min_size: int = 8,
) -> QFont:
    """Resolve the first available font from candidates with legibility scaling."""
    # Scale up micro sizes (< 9) so text isn't microscopic on modern high-DPI displays
    effective_size = max(min_size, size + 1 if size <= 8 else size)
    for fam in candidates:
        f = QFont(fam, effective_size)
        if monospace:
            f.setStyleHint(QFont.StyleHint.Monospace)
        else:
            f.setStyleHint(QFont.StyleHint.SansSerif)
        f.setBold(bold)
        if f.exactMatch():
            return f

    # Fallback to system default with style hint
    f = QFont(candidates[0], effective_size)
    if monospace:
        f.setStyleHint(QFont.StyleHint.Monospace)
    else:
        f.setStyleHint(QFont.StyleHint.SansSerif)
    f.setBold(bold)
    return f


def font_hud(size: int = 9, bold: bool = True) -> QFont:
    """Tactical HUD / header font: crisp, geometric, highly legible."""
    return _resolve_font(
        candidates=["Bahnschrift", "Segoe UI", "Rajdhani", "Arial"],
        size=size,
        bold=bold,
        monospace=False,
        min_size=8,
    )


def font_tech(size: int = 9, bold: bool = False) -> QFont:
    """Technical / telemetry / code monospace: sharp character distinctions."""
    return _resolve_font(
        candidates=["Cascadia Code", "Consolas", "Cascadia Mono", "JetBrains Mono", "Segoe UI"],
        size=size,
        bold=bold,
        monospace=True,
        min_size=8,
    )


def font_body(size: int = 10, bold: bool = False) -> QFont:
    """Primary UI body / label font: ergonomic, clear reading flow."""
    return _resolve_font(
        candidates=["Segoe UI", "Inter", "Roboto", "Arial"],
        size=size,
        bold=bold,
        monospace=False,
        min_size=9,
    )

