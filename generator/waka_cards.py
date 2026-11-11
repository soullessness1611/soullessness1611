"""WakaTime cards: overview, AI coding, projects, tools, rhythm. They follow the active card style."""

from __future__ import annotations

import math
from datetime import date

from .theme import P, esc, fit, fmt_num, frame, is_tech, prompt

HALF_W = 495
FULL_W = 1000


def short(text: str | None) -> str:
    """'17 hrs 31 mins' -> '17h 31m'."""
    if not text:
        return "—"
    for a, b in ((" hrs", "h"), (" hr", "h"), (" mins", "m"), (" min", "m"), (" secs", "s"), (" sec", "s")):
        text = text.replace(a, b)
    return text


def _title(*parts: str) -> str:
    return (" // " if is_tech() else " · ").join(parts).upper()


def _t(x, y, s, size=12.0, fill=None, anchor="start", weight=400, extra="") -> str:
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-size:{size}px;font-weight:{weight};'
            f'fill:{fill or P.TEXT}{extra}">{esc(s)}</text>')


def _lbl(x, y, s, fill=None) -> str:
    style = f' style="fill:{fill}"' if fill else ""
    return f'<text class="lbl" x="{x}" y="{y}"{style}>{prompt()}{esc(s.upper())}</text>'


def _bar(x, y, w, pct, color, h=6) -> str:
    r = 0 if is_tech() else h / 2
    fw = max(3.0, w * min(pct, 100) / 100) if pct > 0 else 0
    glow = ' filter="url(#glow)"' if P.family == "cyber" else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{P.GRID}"/>'
            f'<rect class="rise" x="{x}" y="{y}" width="{fw:.1f}" height="{h}" rx="{r}" fill="{color}"{glow}/>')


def _tile(x, y, w, h) -> str:
    rx = 0 if is_tech() else 10
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{P.PANEL}" stroke="{P.TEXT}" stroke-opacity="0.08"/>'


def _day_label(iso: str | None, fmt: str = "%a %b %d") -> str:
    if not iso:
        return "—"
    d = date.fromisoformat(iso[:10])
    return d.strftime(fmt).replace(" 0", " ")


# ---------------------------------------------------------------- overview (always present)
def overview_card(wk: dict | None) -> str:
    w = FULL_W
    if wk is None or "error" in wk:
        h = 150
        if wk is None:
            head, sub = "LINK OFFLINE", "Add a WAKATIME_TOKEN repository secret (OAuth, scopes read_stats + read_summaries) to show coding time here."
        else:
            head, sub = "LINK ERROR", f"WakaTime API refused the request — {fit(wk['error'], 760, 11)}"
        body = (f'<text class="lbl flicker" x="28" y="94" style="fill:{P.MAGENTA};font-size:14px">⚠ {head}</text>'
                f'<text class="sm" x="28" y="118">{esc(sub)}</text>')
        return frame(w, h, _title("WAKATIME", "7 DAYS"), body, tag="TIME.09", accent=P.MAGENTA)

    langs = wk["languages"][:7]
    h = max(250, 96 + len(langs) * 19 + 40)
    o = [_t(32, 116, short(wk["total"]), 44, weight=600, extra=";letter-spacing:1px"),
         _t(34, 140, f"coded over the {wk['range']}", 13, P.MUTED, extra=";letter-spacing:1px")]
    days = wk.get("days") or []
    tiles = []
    if days:
        tiles.append(("today", short(days[-1]["text"]) if days[-1]["seconds"] else "0m", P.MAGENTA))
    tiles.append(("daily average", short(wk["daily_average"]), P.YELLOW))
    if wk.get("best_day"):
        tiles.append(("best day", _day_label(wk["best_day"]["date"]), P.CYAN))
    for i, (k, v, c) in enumerate(tiles):
        x = 32 + i * 140
        o.append(_tile(x, 166, 132, 58))
        o.append(_lbl(x + 12, 186, k))
        o.append(_t(x + 12, 211, v, 16, c, weight=600))
    lx = 470
    o.append(_lbl(lx, 84, "languages"))
    if not langs:
        o.append(_t(lx, 110, "No coding time recorded.", 12, P.MUTED))
    for i, lang in enumerate(langs):
        y = 104 + i * 19
        color = P.ACCENTS[i % len(P.ACCENTS)]
        o.append(_t(lx, y + 5, fit(lang["name"], 100, 12.5), 12.5))
        o.append(_bar(lx + 104, y - 2, 290, lang["percent"], color))
        o.append(_t(lx + 404, y + 5, short(lang["text"]), 11, P.MUTED))
        o.append(_t(w - 32, y + 5, f"{lang['percent']:.1f}%", 11, color, "end"))
    if not wk.get("up_to_date", True):
        o.append(f'<text class="sm" x="{w - 32}" y="{h - 12}" text-anchor="end">* WakaTime is still computing — numbers may lag</text>')
    return frame(w, h, _title("WAKATIME", wk["range"]), "".join(o), tag="TIME.09", accent=P.CYAN)


# ---------------------------------------------------------------- AI coding
def ai_card(wk: dict) -> str | None:
    a = wk.get("ai")
    if not a:
        return None
    w, h = FULL_W, 230
    cx, cy, r = 112, 140, 56
    circ = 2 * math.pi * r
    pct = a["ai_percent"]
    cap = "butt" if is_tech() else "round"
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{P.GRID}" stroke-width="9"/>',
         f'<circle class="rise" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{P.YELLOW}" stroke-width="9" stroke-linecap="{cap}" '
         f'stroke-dasharray="{max(circ * pct / 100 - 14, 0.1):.1f} {circ:.1f}" transform="rotate(-80 {cx} {cy})"/>',
         _t(cx, cy + 8, f"{pct:.0f}%", 28, anchor="middle", weight=600),
         _t(cx, cy + 28, "AI-DRIVEN", 10, P.MUTED, "middle", extra=";letter-spacing:2px")]
    total = a["ai_additions"] + a["human_additions"] or 1
    cost = a["cost"]
    tiles = [
        ("ai lines", fmt_num(a["ai_additions"]), P.YELLOW, 100 * a["ai_additions"] / total, None),
        ("human lines", fmt_num(a["human_additions"]), P.GREEN, 100 * a["human_additions"] / total, None),
        ("tokens", fmt_num(a["input_tokens"] + a["output_tokens"]), P.CYAN, None,
         f'{fmt_num(a["input_tokens"])} in · {fmt_num(a["output_tokens"])} out'),
        ("ai spend", (f"${cost:,.0f}" if cost >= 100 else f"${cost:,.2f}"), P.MAGENTA, None, "model usage cost"),
        ("sessions", fmt_num(a["sessions"]), P.PURPLE, None, None),
        ("prompts", fmt_num(a["prompts"]), P.CYAN, None, None),
    ]
    for i, (k, v, c, bar, sub) in enumerate(tiles):
        x = 214 + i * 128
        o.append(_tile(x, 78, 118, 116))
        o.append(_lbl(x + 12, 100, k))
        o.append(_t(x + 12, 140, v, 26, c, weight=600))
        if bar is not None:
            o.append(_bar(x + 12, 158, 94, bar, c, 4))
        if sub:
            o.append(_t(x + 12, 172, fit(sub, 100, 9.5), 9.5, P.MUTED))
    if a["models"]:
        models = " · ".join(f'{m["name"]} {m["percent"]:.0f}%' for m in a["models"][:3])
        o.append(_t(w - 32, h - 14, f"models: {models}", 11, P.MUTED, "end"))
    return frame(w, h, _title("AI CODING", wk["range"]), "".join(o), tag="AI.10", accent=P.YELLOW)


# ---------------------------------------------------------------- projects (half)
def projects_card(wk: dict) -> str | None:
    projects = wk.get("projects") or []
    if not projects:
        return None
    w, h = HALF_W, 260
    mx = max(p["seconds"] for p in projects) or 1
    o = []
    for i, proj in enumerate(projects[:7]):
        y = 86 + i * 24
        color = P.ACCENTS[i % len(P.ACCENTS)]
        o.append(_t(32, y + 5, fit(proj["name"], 140, 12.5), 12.5))
        o.append(_bar(170, y - 2, 220, 100 * proj["seconds"] / mx, color))
        o.append(_t(w - 32, y + 5, short(proj["text"]), 11, P.MUTED, "end"))
    return frame(w, h, _title("PROJECTS"), "".join(o), tag="PROJ.11", accent=P.PURPLE)


# ---------------------------------------------------------------- tools (half)
def tools_card(wk: dict) -> str:
    w, h = HALF_W, 260
    o = [_lbl(32, 86, "editors")]
    editors = wk.get("editors") or []
    x, total_w = 32.0, w - 64
    colors = [P.MAGENTA, P.GREEN, P.CYAN, P.YELLOW]
    shown = [e for e in editors if e["percent"] >= 1][:3] or editors[:1]
    for i, ed in enumerate(shown):
        bw = total_w * ed["percent"] / 100
        o.append(f'<rect class="rise" x="{x:.1f}" y="96" width="{max(bw - 2, 2):.1f}" height="10" rx="{0 if is_tech() else 5}" fill="{colors[i]}"/>')
        x += bw
    for i, ed in enumerate(shown[:2]):
        ax, anc = (32, "start") if i == 0 else (w - 32, "end")
        o.append(_t(ax, 126, f'{fit(ed["name"], 160, 12.5)} · {ed["percent"]:.0f}%', 12.5, colors[i], anc, 600))
        o.append(_t(ax, 142, short(ed["text"]), 11, P.MUTED, anc))
    ai = wk.get("ai") or {}
    rows = [("operating system", " · ".join(f'{x["name"]} {x["percent"]:.0f}%' for x in (wk.get("operating_systems") or [])[:2]) or "—")]
    if ai.get("models"):
        rows.append(("ai model", " · ".join(f'{m["name"]} {m["percent"]:.0f}%' for m in ai["models"][:2])))
    if wk.get("categories"):
        top = wk["categories"][0]
        rows.append(("top category", f'{top["name"]} {top["percent"]:.0f}%'))
    rows.append(("machines", f'{wk.get("machines", 0)} workstation' + ("s" if wk.get("machines", 0) != 1 else "")))
    for i, (k, v) in enumerate(rows[:4]):
        y = 176 + i * 22
        o.append(_lbl(32, y, k))
        o.append(_t(w - 32, y, fit(v, 230, 12.5), 12.5, anchor="end"))
    return frame(w, h, _title("TOOLS"), "".join(o), tag="TOOL.12", accent=P.GREEN)


# ---------------------------------------------------------------- rhythm (needs read_summaries)
def rhythm_card(wk: dict) -> str | None:
    days = wk.get("days")
    if not days:
        return None
    w, h = FULL_W, 250
    use_ai = any(d["ai_additions"] for d in days)
    o = [_lbl(32, 84, "ai vs human lines by day" if use_ai else "coding time by day")]
    vals = [d["ai_additions"] if use_ai else d["seconds"] / 3600 for d in days]
    mx = max(vals) or 1
    bx, by, bh = 40, 200, 100
    step = min(74, 520 / max(len(days), 1))
    for i, (d, v) in enumerate(zip(days, vals)):
        x = bx + i * step
        vh = bh * v / mx
        o.append(f'<rect class="rise" x="{x:.1f}" y="{by - vh:.1f}" width="34" height="{max(vh, 1.5):.1f}" '
                 f'rx="{0 if is_tech() else 4}" fill="{P.YELLOW}" opacity="{0.95 if v else 0.3}"/>')
        o.append(_t(f"{x + 17:.1f}", by + 18, _day_label(d["date"], "%b %d"), 11, P.MUTED, "middle"))
        if v:
            o.append(_t(f"{x + 17:.1f}", f"{by - vh - 6:.1f}", fmt_num(v) if use_ai else f"{v:.1f}h", 10.5, anchor="middle"))
        if use_ai and d["human_additions"]:
            o.append(f'<rect x="{x + 38:.1f}" y="{by - 3}" width="8" height="3" rx="1.5" fill="{P.GREEN}"/>'
                     + _t(f"{x + 42:.1f}", by - 8, fmt_num(d["human_additions"]), 9.5, P.GREEN, "middle"))
    legend = [(P.YELLOW, "AI additions"), (P.GREEN, "human additions")] if use_ai else [(P.YELLOW, "hours coded")]
    for i, (c, s) in enumerate(legend):
        o.append(f'<circle cx="{44 + i * 106}" cy="{h - 18}" r="4" fill="{c}"/>' + _t(54 + i * 106, h - 14, s, 11, P.MUTED))
    wx = 600
    o.append(_lbl(wx, 84, "hours by weekday"))
    hours = [0.0] * 7
    for d in days:
        hours[date.fromisoformat(d["date"]).weekday()] += d["seconds"] / 3600
    wmx = max(hours) or 1
    for i, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        y = 102 + i * 18
        o.append(_t(wx, y + 8, name, 11.5))
        o.append(_bar(wx + 44, y, 270, 100 * hours[i] / wmx, P.MAGENTA if hours[i] == wmx and hours[i] else P.CYAN))
        o.append(_t(w - 32, y + 8, f"{hours[i]:.1f}h" if hours[i] else "—", 11, P.MUTED, "end"))
    return frame(w, h, _title("RHYTHM", wk["range"]), "".join(o), tag="BEAT.13", accent=P.MAGENTA)


def waka_cards(wk: dict | None) -> dict[str, str]:
    """All WakaTime cards that have data, in display order."""
    out = {"waka-overview.svg": overview_card(wk)}
    if wk is None or "error" in wk:
        return out
    for name, fn in (("waka-ai.svg", ai_card), ("waka-projects.svg", projects_card),
                     ("waka-tools.svg", tools_card), ("waka-rhythm.svg", rhythm_card)):
        svg = fn(wk)
        if svg:
            out[name] = svg
    return out
