"""CyberPunk palette and the shared SVG frame every card is drawn in."""

from __future__ import annotations

from xml.sax.saxutils import escape

BG = "#07070d"
PANEL = "#0d0d18"
GRID = "#16162b"
CYAN = "#00f0ff"
MAGENTA = "#ff2a6d"
YELLOW = "#f9f002"
PURPLE = "#b026ff"
GREEN = "#05ffa1"
TEXT = "#e2e2f0"
MUTED = "#7a7a9e"

ACCENTS = [CYAN, MAGENTA, YELLOW, PURPLE, GREEN, "#ff8a00", "#4d7cff", "#ff4df0"]

# Heatmap ramp: NONE -> FOURTH_QUARTILE
HEAT = ["#14142a", "#3b0f63", "#8a1ea8", "#ff2a6d", "#00f0ff"]

FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

CHAR_W = 0.6  # monospace glyph width relative to font size


def esc(value: object) -> str:
    return escape(str(value), {'"': "&quot;"})


def fit(text: str, max_px: float, size: float) -> str:
    """Truncate text so it fits max_px at the given monospace font size."""
    max_chars = max(1, int(max_px / (size * CHAR_W)))
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


def fmt_num(n: float) -> str:
    n = float(n)
    for div, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(n) >= div:
            v = n / div
            return f"{v:.1f}".rstrip("0").rstrip(".") + suffix
    return f"{int(n):,}" if n == int(n) else f"{n:.1f}"


def frame(width: int, height: int, title: str, body: str, *, tag: str = "SYS", accent: str = CYAN) -> str:
    """Wrap card body in the neon cut-corner frame with grid, scanlines and glitch title."""
    c = 18  # cut-corner size
    w, h = width, height
    outline = f"M{c},1 H{w - 1} V{h - c} L{w - c},{h - 1} H1 V{c} Z"
    title_e = esc(title)
    tag_e = esc(tag)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title_e}">
<title>{title_e}</title>
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{GRID}" stroke-width="1"/>
  </pattern>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#ffffff" opacity="0.025"/>
  </pattern>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{accent}"/>
    <stop offset="1" stop-color="{MAGENTA if accent != MAGENTA else CYAN}"/>
  </linearGradient>
  <clipPath id="cut"><path d="{outline}"/></clipPath>
</defs>
<style>
  text {{ font-family: {FONT}; fill: {TEXT}; }}
  .t {{ font-size: 18px; font-weight: 700; letter-spacing: 2px; }}
  .lbl {{ font-size: 12px; fill: {MUTED}; letter-spacing: 1px; }}
  .val {{ font-size: 13px; font-weight: 700; }}
  .sm {{ font-size: 11px; fill: {MUTED}; }}
  .big {{ font-size: 34px; font-weight: 800; }}
  .flicker {{ animation: flicker 6s infinite; }}
  .sweep {{ animation: sweep 7s linear infinite; }}
  .rise {{ animation: rise .9s ease-out both; }}
  @keyframes flicker {{ 0%,92%,96%,100% {{ opacity: 1; }} 94% {{ opacity: .35; }} }}
  @keyframes sweep {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY({h + 40}px); }} }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ .flicker, .sweep, .rise {{ animation: none; }} }}
</style>
<g clip-path="url(#cut)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <rect width="{w}" height="{h}" fill="url(#grid)"/>
  <rect width="{w}" height="{h}" fill="url(#scan)"/>
  <rect class="sweep" x="0" y="0" width="{w}" height="38" fill="{accent}" opacity="0.035"/>
</g>
<path d="{outline}" fill="none" stroke="url(#edge)" stroke-width="2"/>
<path d="M1,{c + 30} V{c} L{c},1 H{c + 60}" fill="none" stroke="{accent}" stroke-width="4" filter="url(#glow)"/>
<path d="M{w - 1},{h - c - 30} V{h - c} L{w - c},{h - 1} H{w - c - 60}" fill="none" stroke="{MAGENTA}" stroke-width="4" filter="url(#glow)"/>
<g transform="translate(28,38)" class="flicker">
  <text class="t" x="2" y="1" style="fill:{MAGENTA}" opacity="0.7">{title_e}</text>
  <text class="t" x="-1.5" y="-1" style="fill:{CYAN}" opacity="0.7">{title_e}</text>
  <text class="t" x="0" y="0">{title_e}</text>
</g>
<text class="sm" x="{w - 24}" y="34" text-anchor="end" style="fill:{accent}">// {tag_e}</text>
<rect x="28" y="50" width="{w - 56}" height="1" fill="{accent}" opacity="0.35"/>
{body}
</svg>
"""
