"""Card styles (palettes + frames) and small SVG text helpers.

Card renderers read colours through `P`, the active style. `use(name)` switches it.
Five card styles share the same ten-card layout; each belongs to a frame family:

    cyberpunk  -> "cyber"     neon cut-corner frame, glitch title
    zen-sumi   -> "zen"       ink-black paper, serif, vermilion seal (default)
    zen-washi  -> "zen"       washi paper, sumi ink
    terminal   -> "terminal"  green-phosphor CRT window
    minimal    -> "minimal"   plain GitHub-like panel
"""

from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, field
from xml.sax.saxutils import escape

MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua','Noto Serif',Georgia,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
CJK = "'Yu Mincho','Hiragino Mincho ProN','Noto Serif CJK JP','MS Mincho',serif"

CHAR_W = 0.6  # glyph width relative to font size (monospace; serif/sans are narrower, so this is safe)


@dataclass(frozen=True)
class Style:
    name: str
    family: str
    BG: str
    PANEL: str
    GRID: str
    CYAN: str  # primary accent
    MAGENTA: str  # hot accent
    YELLOW: str
    PURPLE: str
    GREEN: str
    TEXT: str
    MUTED: str
    ACCENTS: list[str] = field(default_factory=list)
    HEAT: list[str] = field(default_factory=list)  # contribution levels NONE -> FOURTH_QUARTILE
    FONT: str = MONO
    SEAL: str = "#b8402f"


STYLES: dict[str, Style] = {
    "cyberpunk": Style(
        "cyberpunk", "cyber", BG="#07070d", PANEL="#0d0d18", GRID="#16162b", CYAN="#00f0ff", MAGENTA="#ff2a6d",
        YELLOW="#f9f002", PURPLE="#b026ff", GREEN="#05ffa1", TEXT="#e2e2f0", MUTED="#7a7a9e",
        ACCENTS=["#00f0ff", "#ff2a6d", "#f9f002", "#b026ff", "#05ffa1", "#ff8a00", "#4d7cff", "#ff4df0"],
        HEAT=["#14142a", "#3b0f63", "#8a1ea8", "#ff2a6d", "#00f0ff"], FONT=MONO),
    "zen-sumi": Style(
        "zen-sumi", "zen", BG="#151412", PANEL="#1d1b18", GRID="#2a2723", CYAN="#9fb7c9", MAGENTA="#d0644c",
        YELLOW="#c9a24a", PURPLE="#a08aa8", GREEN="#8fa86f", TEXT="#e9e2d2", MUTED="#8a8273",
        ACCENTS=["#9fb7c9", "#d0644c", "#c9a24a", "#a08aa8", "#8fa86f", "#b08d6e", "#7fa9ae", "#c48a8a"],
        HEAT=["#24221e", "#3a3b2c", "#5c6a43", "#8ea263", "#c9a24a"], FONT=SERIF, SEAL="#c0503b"),
    "zen-washi": Style(
        "zen-washi", "zen", BG="#f3eee3", PANEL="#ebe4d4", GRID="#ddd5c3", CYAN="#34557a", MAGENTA="#b8402f",
        YELLOW="#a8772a", PURPLE="#6e4a6b", GREEN="#5a7a45", TEXT="#2a2723", MUTED="#857b6c",
        ACCENTS=["#34557a", "#b8402f", "#a8772a", "#6e4a6b", "#5a7a45", "#8a6b4f", "#4f7f86", "#9c5a5a"],
        HEAT=["#e6dfcf", "#cdd6bd", "#a3b68b", "#6f8f57", "#3f5c33"], FONT=SERIF, SEAL="#b8402f"),
    "terminal": Style(
        "terminal", "terminal", BG="#050a05", PANEL="#0b140b", GRID="#0f1f0f", CYAN="#33ff66", MAGENTA="#ffb000",
        YELLOW="#e6ff8a", PURPLE="#1fae4b", GREEN="#66ffcc", TEXT="#b6f5c0", MUTED="#4f8a5a",
        ACCENTS=["#33ff66", "#ffb000", "#e6ff8a", "#1fae4b", "#66ffcc", "#9cff3a", "#ffd866", "#3affc8"],
        HEAT=["#0c180c", "#0f4d1c", "#16852f", "#22c445", "#7dff9a"], FONT=MONO),
    "minimal": Style(
        "minimal", "minimal", BG="#ffffff", PANEL="#f6f8fa", GRID="#eaeef2", CYAN="#0969da", MAGENTA="#bf3989",
        YELLOW="#9a6700", PURPLE="#8250df", GREEN="#1a7f37", TEXT="#1f2328", MUTED="#656d76",
        ACCENTS=["#0969da", "#bf3989", "#9a6700", "#8250df", "#1a7f37", "#bc4c00", "#1b7c83", "#cf222e"],
        HEAT=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"], FONT=SANS),
}
DEFAULT_STYLE = "zen-sumi"


class _Active:
    """Proxy to the active Style so `from .theme import P` keeps working after `use()`."""

    def __init__(self, style: Style):
        self._style = style

    def __getattr__(self, key: str):
        return getattr(self._style, key)

    @property
    def style(self) -> Style:
        return self._style


P = _Active(STYLES[DEFAULT_STYLE])


def use(name: str) -> Style:
    if name not in STYLES:
        raise KeyError(f"unknown card style '{name}' (choose from: {', '.join(STYLES)})")
    P._style = STYLES[name]
    return P._style


# ---------------------------------------------------------------- per-family details used by cards
def prompt() -> str:
    """Prefix for section labels: '> ' (cyber), '$ ' (terminal), nothing for calm styles."""
    return {"cyber": "&gt; ", "terminal": "$ "}.get(P.family, "")


def is_tech() -> bool:
    return P.family in ("cyber", "terminal")


def chip(x: float, y: float, w: float, h: float, cut: float = 6) -> str:
    """Open tag for a chip/tile outline: cut corners for tech styles, rounded rect otherwise."""
    if is_tech():
        return f'<path d="M{x + cut:.1f},{y:.1f} H{x + w:.1f} V{y + h - cut:.1f} L{x + w - cut:.1f},{y + h:.1f} H{x:.1f} V{y + cut:.1f} Z"'
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(h / 2, 10):.1f}"'


def stable_int(text: str) -> int:
    """Deterministic hash (Python's hash() changes per run and would churn the SVGs)."""
    return zlib.crc32(text.encode())


# ---------------------------------------------------------------- text helpers
def esc(value: object) -> str:
    return escape(str(value), {'"': "&quot;"})


def fit(text: str, max_px: float, size: float) -> str:
    """Truncate text so it fits max_px at the given font size."""
    max_chars = max(1, int(max_px / (size * CHAR_W)))
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


def fmt_num(n: float) -> str:
    n = float(n)
    for div, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(n) >= div:
            v = n / div
            return f"{v:.1f}".rstrip("0").rstrip(".") + suffix
    return f"{int(n):,}" if n == int(n) else f"{n:.1f}"


# ---------------------------------------------------------------- frames
def frame(width: int, height: int, title: str, body: str, *, tag: str = "SYS", accent: str | None = None) -> str:
    """Wrap a card body in the active style's frame."""
    builder = {"cyber": _cyber, "zen": _zen, "terminal": _terminal, "minimal": _minimal}[P.family]
    return builder(width, height, title, body, tag, accent or P.CYAN)


def _open(w: int, h: int, title: str) -> str:
    t = esc(title)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{t}">\n'
            f"<title>{t}</title>\n")


def _style_block(title_css: str, flicker: str, rise: str, glow: str, extra_kf: str = "") -> str:
    return f"""<defs>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">{glow}</filter>
</defs>
<style>
  text {{ font-family: {P.FONT}; fill: {P.TEXT}; }}
  .t {{ {title_css} }}
  .lbl {{ font-size: 12px; fill: {P.MUTED}; letter-spacing: 1px; }}
  .val {{ font-size: 13px; font-weight: 700; }}
  .sm {{ font-size: 11px; fill: {P.MUTED}; }}
  .flicker {{ {flicker} }}
  .rise {{ animation: rise {rise}; }}
  {extra_kf}
  @media (prefers-reduced-motion: reduce) {{ .flicker, .sweep, .rise {{ animation: none; }} }}
</style>
"""


NO_GLOW = '<feMerge><feMergeNode in="SourceGraphic"/></feMerge>'


def _cyber(w: int, h: int, title: str, body: str, tag: str, accent: str) -> str:
    c = 18  # cut-corner size
    outline = f"M{c},1 H{w - 1} V{h - c} L{w - c},{h - 1} H1 V{c} Z"
    t = esc(title)
    return _open(w, h, title) + f"""<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{P.GRID}" stroke-width="1"/>
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
    <stop offset="1" stop-color="{P.MAGENTA if accent != P.MAGENTA else P.CYAN}"/>
  </linearGradient>
  <clipPath id="cut"><path d="{outline}"/></clipPath>
</defs>
<style>
  text {{ font-family: {P.FONT}; fill: {P.TEXT}; }}
  .t {{ font-size: 18px; font-weight: 700; letter-spacing: 2px; }}
  .lbl {{ font-size: 12px; fill: {P.MUTED}; letter-spacing: 1px; }}
  .val {{ font-size: 13px; font-weight: 700; }}
  .sm {{ font-size: 11px; fill: {P.MUTED}; }}
  .flicker {{ animation: flicker 6s infinite; }}
  .sweep {{ animation: sweep 7s linear infinite; }}
  .rise {{ animation: rise .9s ease-out both; }}
  @keyframes flicker {{ 0%,92%,96%,100% {{ opacity: 1; }} 94% {{ opacity: .35; }} }}
  @keyframes sweep {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY({h + 40}px); }} }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ .flicker, .sweep, .rise {{ animation: none; }} }}
</style>
<g clip-path="url(#cut)">
  <rect width="{w}" height="{h}" fill="{P.BG}"/>
  <rect width="{w}" height="{h}" fill="url(#grid)"/>
  <rect width="{w}" height="{h}" fill="url(#scan)"/>
  <rect class="sweep" x="0" y="0" width="{w}" height="38" fill="{accent}" opacity="0.035"/>
</g>
<path d="{outline}" fill="none" stroke="url(#edge)" stroke-width="2"/>
<path d="M1,{c + 30} V{c} L{c},1 H{c + 60}" fill="none" stroke="{accent}" stroke-width="4" filter="url(#glow)"/>
<path d="M{w - 1},{h - c - 30} V{h - c} L{w - c},{h - 1} H{w - c - 60}" fill="none" stroke="{P.MAGENTA}" stroke-width="4" filter="url(#glow)"/>
<g transform="translate(28,38)" class="flicker">
  <text class="t" x="2" y="1" style="fill:{P.MAGENTA}" opacity="0.7">{t}</text>
  <text class="t" x="-1.5" y="-1" style="fill:{P.CYAN}" opacity="0.7">{t}</text>
  <text class="t" x="0" y="0">{t}</text>
</g>
<text class="sm" x="{w - 24}" y="34" text-anchor="end" style="fill:{accent}">// {esc(tag)}</text>
<rect x="28" y="50" width="{w - 56}" height="1" fill="{accent}" opacity="0.35"/>
{body}
</svg>
"""


def _zen(w: int, h: int, title: str, body: str, tag: str, accent: str) -> str:
    r = min(h * 0.36, 88)
    cx, cy = w - r - 34, h / 2 + 8
    a0, a1 = math.radians(-60), math.radians(255)
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    enso = (f'<path d="M{p0[0]:.1f},{p0[1]:.1f} A{r:.1f},{r:.1f} 0 1 1 {p1[0]:.1f},{p1[1]:.1f}" fill="none" '
            f'stroke="{P.TEXT}" stroke-width="9" stroke-linecap="round" opacity="0.05"/>'
            f'<path d="M{p0[0]:.1f},{p0[1]:.1f} A{r - 3:.1f},{r - 3:.1f} 0 1 1 {p1[0]:.1f},{p1[1]:.1f}" fill="none" '
            f'stroke="{P.TEXT}" stroke-width="2" stroke-linecap="round" opacity="0.06"/>')
    return (_open(w, h, title)
            + _style_block("font-size: 17px; font-weight: 600; letter-spacing: 5px;", "", "1.1s ease-out both", NO_GLOW,
                           "@keyframes rise { from { opacity: 0; } to { opacity: 1; } }")
            + f"""<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{P.BG}" stroke="{P.TEXT}" stroke-opacity="0.18"/>
{enso}
<text class="t" x="32" y="40">{esc(title)}</text>
<rect x="{w - 50}" y="20" width="24" height="24" rx="4" fill="{P.SEAL}"/>
<text x="{w - 38}" y="38" text-anchor="middle" style="font-size:15px;fill:{P.BG};font-family:{CJK}">禅</text>
<circle cx="32" cy="53" r="2" fill="{P.SEAL}"/>
<rect x="40" y="52.5" width="{w - 72}" height="1" fill="{P.TEXT}" opacity="0.14"/>
{body}
</svg>
""")


def _terminal(w: int, h: int, title: str, body: str, tag: str, accent: str) -> str:
    slug = esc(title.lower().replace(" · ", "_").replace(" ", "_"))
    return (_open(w, h, title)
            + _style_block("font-size: 16px; font-weight: 700; letter-spacing: 1px;",
                           "animation: blink 1.1s steps(1) infinite;", ".9s ease-out both",
                           '<feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
                           "@keyframes blink { 50% { opacity: 0; } } "
                           "@keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }")
            + f"""<defs><pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#000" opacity="0.35"/></pattern>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient></defs>
<rect width="{w}" height="{h}" rx="6" fill="{P.BG}"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="6" fill="none" stroke="{P.CYAN}" stroke-opacity="0.55"/>
<rect x="1" y="1" width="{w - 2}" height="27" rx="5" fill="{P.PANEL}"/>
<line x1="1" y1="28" x2="{w - 1}" y2="28" stroke="{P.CYAN}" stroke-opacity="0.4"/>
<text class="sm" x="14" y="19" style="fill:{P.CYAN}">┌─[ {slug} ]</text>
<text class="sm" x="{w - 14}" y="19" text-anchor="end">pid {stable_int(tag) % 9000 + 1000} · tty1</text>
<text class="t" x="28" y="48" filter="url(#glow)"><tspan style="fill:{P.CYAN}">$ </tspan>{esc(title)}<tspan class="flicker" style="fill:{P.CYAN}"> ▌</tspan></text>
{body}
<rect width="{w}" height="{h}" rx="6" fill="url(#scan)" pointer-events="none"/>
<rect width="{w}" height="{h}" rx="6" fill="url(#vig)" pointer-events="none"/>
</svg>
""")


def _minimal(w: int, h: int, title: str, body: str, tag: str, accent: str) -> str:
    nice = " ".join(word if word in ("AI", "·") else word.capitalize() for word in title.split())
    nice = nice.replace("Github", "GitHub").replace("Wakatime", "WakaTime")
    return (_open(w, h, title)
            + _style_block("font-size: 16px; font-weight: 600;", "", "1.1s ease-out both", NO_GLOW,
                           "@keyframes rise { from { opacity: 0; } to { opacity: 1; } }")
            + f"""<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="{P.BG}" stroke="#d0d7de"/>
<text class="t" x="28" y="40">{esc(nice)}</text>
<rect x="28" y="52" width="{w - 56}" height="1" fill="#d8dee4"/>
{body}
</svg>
""")
