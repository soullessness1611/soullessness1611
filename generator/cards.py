"""SVG card renderers. Each function returns a complete standalone SVG string."""

from __future__ import annotations

import math
from datetime import date, datetime

from .theme import (
    ACCENTS, BG, CYAN, GREEN, GRID, HEAT, MAGENTA, MUTED, PANEL, PURPLE, TEXT, YELLOW,
    esc, fit, fmt_num, frame,
)

HALF_W = 495
FULL_W = 1000


def _d(value: date | None) -> str:
    return value.strftime("%d %b %Y").upper() if value else "—"


def _ago(iso: str | None, today: date) -> str:
    if not iso:
        return "—"
    days = (today - datetime.fromisoformat(iso.replace("Z", "+00:00")).date()).days
    if days <= 0:
        return "TODAY"
    if days == 1:
        return "1 DAY AGO"
    if days < 30:
        return f"{days} DAYS AGO"
    if days < 365:
        return f"{days // 30} MO AGO"
    return f"{days // 365} YR AGO"


def _bar(x: float, y: float, w: float, h: float, pct: float, color: str, delay: float = 0) -> str:
    fill_w = max(2.0, w * min(pct, 100) / 100) if pct > 0 else 0
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{GRID}"/>'
        f'<rect class="rise" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{fill_w:.1f}" '
        f'height="{h}" fill="{color}" filter="url(#glow)"/>'
    )


# ---------------------------------------------------------------- header
def header_card(name: str, login: str, tagline: str, joined: date | None) -> str:
    w, h = FULL_W, 170
    since = f"ONLINE SINCE {joined.year}" if joined else "ONLINE"
    body = f"""
<g transform="translate(40,112)">
  <text x="3" y="2" style="font-size:46px;font-weight:800;fill:{MAGENTA};letter-spacing:4px" opacity="0.75">{esc(name.upper())}</text>
  <text x="-2" y="-2" style="font-size:46px;font-weight:800;fill:{CYAN};letter-spacing:4px" opacity="0.75">{esc(name.upper())}</text>
  <text x="0" y="0" class="flicker" style="font-size:46px;font-weight:800;letter-spacing:4px">{esc(name.upper())}</text>
</g>
<text x="42" y="146" class="lbl" style="fill:{YELLOW};font-size:13px">&gt; {esc(tagline)}<tspan class="flicker" style="fill:{CYAN}"> █</tspan></text>
<g transform="translate({w - 40},100)" text-anchor="end">
  <text class="lbl" y="0">@{esc(login)}</text>
  <text class="lbl" y="22" style="fill:{GREEN}">● {since}</text>
</g>"""
    return frame(w, h, "> JACK_IN // GITHUB PROFILE", body, tag="NODE.00", accent=CYAN)


# ---------------------------------------------------------------- github stats
def stats_card(s: dict) -> str:
    w, h = HALF_W, 230
    rows = [
        ("TOTAL STARS", s["stars"], YELLOW),
        (f"COMMITS ({s['year']})", s["commits_year"], CYAN),
        ("TOTAL COMMITS", s["commits_all"], CYAN),
        ("PULL REQUESTS", s["prs"], MAGENTA),
        ("ISSUES", s["issues"], PURPLE),
        ("CONTRIBUTED TO", s["contributed_to"], GREEN),
        ("FOLLOWERS", s["followers"], YELLOW),
    ]
    lines = []
    for i, (label, value, color) in enumerate(rows):
        y = 80 + i * 21
        lines.append(
            f'<g class="rise" style="animation-delay:{i * 0.08:.2f}s">'
            f'<rect x="28" y="{y - 9}" width="4" height="10" fill="{color}"/>'
            f'<text class="lbl" x="40" y="{y}">{label}</text>'
            f'<text class="val" x="300" y="{y}" text-anchor="end" style="fill:{color}">{fmt_num(value)}</text></g>'
        )
    # hexagon gauge with total contributions
    cx, cy, r = 395, 140, 58
    hexa = " ".join(
        f"{cx + r * math.cos(math.radians(60 * k - 30)):.1f},{cy + r * math.sin(math.radians(60 * k - 30)):.1f}"
        for k in range(6)
    )
    body = "\n".join(lines) + f"""
<polygon points="{hexa}" fill="{PANEL}" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>
<polygon points="{hexa}" fill="none" stroke="{MAGENTA}" stroke-width="1" transform="rotate(30 {cx} {cy}) scale(1)" opacity="0.5"/>
<text x="{cx}" y="{cy + 4}" text-anchor="middle" style="font-size:24px;font-weight:800;fill:{CYAN}">{fmt_num(s['contributions_all'])}</text>
<text x="{cx}" y="{cy + 22}" text-anchor="middle" class="sm">CONTRIBS</text>
<text x="{cx}" y="{cy + 78}" text-anchor="middle" class="sm" style="fill:{MAGENTA}">ALL-TIME</text>"""
    return frame(w, h, "GITHUB STATS", body, tag="STAT.01", accent=CYAN)


# ---------------------------------------------------------------- streak
def streak_card(st: dict) -> str:
    w, h = HALF_W, 230
    cur, lng = st["current"], st["longest"]
    cx, cy, r = w / 2, 128, 46
    circ = 2 * math.pi * r
    ratio = cur["length"] / lng["length"] if lng["length"] else 0
    dash = circ * min(ratio, 1)

    def col(x: float, value: str, label: str, sub: str, color: str) -> str:
        return (
            f'<text x="{x}" y="128" text-anchor="middle" style="font-size:26px;font-weight:800;fill:{color}">{value}</text>'
            f'<text x="{x}" y="152" text-anchor="middle" class="lbl">{label}</text>'
            f'<text x="{x}" y="200" text-anchor="middle" class="sm">{sub}</text>'
        )

    cur_range = f"{_d(cur['start'])} → {_d(cur['end'])}" if cur["length"] else "START A NEW RUN"
    body = f"""
{col(82, fmt_num(st['total']), 'TOTAL', 'SINCE ' + _d(st['first_day']), YELLOW)}
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PANEL}" stroke="{GRID}" stroke-width="7"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MAGENTA}" stroke-width="7" stroke-linecap="square"
  stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})" filter="url(#glow)"/>
<text x="{cx}" y="{cy + 9}" text-anchor="middle" style="font-size:30px;font-weight:800;fill:{MAGENTA}" class="flicker">{cur['length']}</text>
<text x="{cx}" y="{cy + 66}" text-anchor="middle" class="lbl" style="fill:{TEXT}">CURRENT STREAK</text>
<text x="{cx}" y="{cy + 84}" text-anchor="middle" class="sm" style="font-size:9.5px">{cur_range}</text>
{col(w - 82, str(lng['length']), 'LONGEST', '', CYAN)}
<text x="{w - 82}" y="170" text-anchor="middle" class="sm" style="font-size:9.5px">{_d(lng['start'])}</text>
<text x="{w - 82}" y="184" text-anchor="middle" class="sm" style="font-size:9.5px">→ {_d(lng['end'])}</text>
<line x1="160" y1="75" x2="160" y2="205" stroke="{GRID}"/>
<line x1="{w - 160}" y1="75" x2="{w - 160}" y2="205" stroke="{GRID}"/>"""
    return frame(w, h, "STREAK", body, tag="LOOP.02", accent=MAGENTA)


# ---------------------------------------------------------------- top languages
def languages_card(langs: list[dict]) -> str:
    w, h = HALF_W, 260
    if not langs:
        return frame(w, h, "TOP LANGUAGES", f'<text x="28" y="100" class="lbl">NO SIGNAL</text>', tag="LANG.03")
    x, parts = 28.0, []
    total_w = w - 56
    for lang in langs:
        seg = total_w * lang["percent"] / 100
        parts.append(f'<rect x="{x:.1f}" y="70" width="{max(seg, 1):.1f}" height="12" fill="{lang["color"]}"/>')
        x += seg
    rows = []
    for i, lang in enumerate(langs):
        col, row = divmod(i, (len(langs) + 1) // 2)
        bx = 28 + col * (total_w / 2 + 10)
        by = 112 + row * 34
        bar_w = total_w / 2 - 20
        rows.append(
            f'<g class="rise" style="animation-delay:{i * 0.07:.2f}s">'
            f'<rect x="{bx}" y="{by - 9}" width="9" height="9" fill="{lang["color"]}" transform="rotate(45 {bx + 4.5} {by - 4.5})"/>'
            f'<text class="val" x="{bx + 16}" y="{by}" style="font-size:12px">{esc(fit(lang["name"], bar_w - 60, 12))}</text>'
            f'<text class="sm" x="{bx + bar_w}" y="{by}" text-anchor="end">{lang["percent"]:.1f}%</text>'
            f"</g>{_bar(bx, by + 7, bar_w, 4, lang['percent'], lang['color'], i * 0.07)}"
        )
    body = (
        f'<rect x="27" y="69" width="{total_w + 2}" height="14" fill="none" stroke="{CYAN}" opacity="0.5"/>'
        + "".join(parts)
        + "".join(rows)
    )
    return frame(w, h, "TOP LANGUAGES", body, tag="LANG.03", accent=YELLOW)


# ---------------------------------------------------------------- repositories & stars
def repos_card(rs: dict) -> str:
    w, h = HALF_W, 260
    tiles = [("REPOS", rs["count"], CYAN), ("STARS", rs["stars"], YELLOW), ("FORKS", rs["forks"], MAGENTA)]
    tw = (w - 56 - 20) / 3
    out = []
    for i, (label, value, color) in enumerate(tiles):
        x = 28 + i * (tw + 10)
        out.append(
            f'<rect x="{x}" y="66" width="{tw}" height="62" fill="{PANEL}" stroke="{color}" stroke-opacity="0.6"/>'
            f'<rect x="{x}" y="66" width="{tw}" height="3" fill="{color}" filter="url(#glow)"/>'
            f'<text x="{x + tw / 2}" y="104" text-anchor="middle" style="font-size:24px;font-weight:800;fill:{color}">{fmt_num(value)}</text>'
            f'<text x="{x + tw / 2}" y="120" text-anchor="middle" class="sm">{label}</text>'
        )
    out.append(f'<text class="lbl" x="28" y="152" style="fill:{CYAN}">&gt; TOP REPOSITORIES</text>')
    for i, repo in enumerate(rs["top"][:4]):
        y = 176 + i * 21
        lang = repo.get("primaryLanguage") or {}
        out.append(
            f'<g class="rise" style="animation-delay:{0.2 + i * 0.08:.2f}s">'
            f'<circle cx="33" cy="{y - 4}" r="4" fill="{lang.get("color") or MUTED}"/>'
            f'<text class="val" x="44" y="{y}" style="font-size:12px">{esc(fit(repo["name"], 290, 12))}</text>'
            f'<text class="sm" x="{w - 90}" y="{y}" text-anchor="end" style="fill:{YELLOW}">★ {fmt_num(repo["stargazerCount"])}</text>'
            f'<text class="sm" x="{w - 28}" y="{y}" text-anchor="end" style="fill:{MAGENTA}">⑂ {fmt_num(repo["forkCount"])}</text></g>'
        )
    return frame(w, h, "REPOSITORIES & STARS", "".join(out), tag="REPO.04", accent=YELLOW)


# ---------------------------------------------------------------- contribution graph
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def contribution_card(calendar: dict) -> str:
    w, h = FULL_W, 230
    cell, step, ox, oy = 13, 17, 62, 82
    weeks = calendar["weeks"][-53:]
    rects, months = [], []
    last_month = None
    for wi, week in enumerate(weeks):
        for d in week["contributionDays"]:
            lvl = LEVELS.get(d.get("contributionLevel", "NONE"), 0)
            x, y = ox + wi * step, oy + d["weekday"] * step
            glow = ' filter="url(#glow)"' if lvl == 4 else ""
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{HEAT[lvl]}"{glow}>'
                f'<title>{d["date"]}: {d["contributionCount"]}</title></rect>'
            )
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and wi < len(weeks) - 2:
            months.append(f'<text class="sm" x="{ox + wi * step}" y="{oy - 10}">{first.strftime("%b").upper()}</text>')
            last_month = first.month
    day_labels = "".join(
        f'<text class="sm" x="{ox - 10}" y="{oy + i * step + 10}" text-anchor="end">{n}</text>'
        for i, n in ((1, "MON"), (3, "WED"), (5, "FRI"))
    )
    legend_x = w - 200
    legend = "".join(
        f'<rect x="{legend_x + 40 + i * 17}" y="{h - 26}" width="13" height="13" fill="{c}"/>' for i, c in enumerate(HEAT)
    )
    body = (
        "".join(months) + day_labels + "".join(rects)
        + f'<text class="lbl" x="{ox}" y="{h - 15}"><tspan style="fill:{CYAN};font-weight:700">{fmt_num(calendar["totalContributions"])}</tspan> CONTRIBUTIONS IN THE LAST YEAR</text>'
        + f'<text class="sm" x="{legend_x + 32}" y="{h - 15}" text-anchor="end">LOW</text>{legend}'
        + f'<text class="sm" x="{legend_x + 40 + 5 * 17 + 4}" y="{h - 15}">HIGH</text>'
    )
    return frame(w, h, "CONTRIBUTION GRAPH", body, tag="GRID.05", accent=PURPLE)


# ---------------------------------------------------------------- commit activity
def activity_card(a: dict) -> str:
    w, h = FULL_W, 280
    out = []
    # --- 24h histogram
    px, py, pw, ph = 28, 84, 430, 140
    out.append(f'<text class="lbl" x="{px}" y="{py - 8}" style="fill:{CYAN}">&gt; HOUR OF DAY</text>')
    mx = max(a["hours"]) or 1
    bw = pw / 24
    for i, v in enumerate(a["hours"]):
        bh = ph * v / mx
        color = MAGENTA if i == a["peak_hour"] else CYAN
        out.append(
            f'<rect class="rise" style="animation-delay:{i * 0.03:.2f}s" x="{px + i * bw + 2:.1f}" y="{py + ph - bh + 6:.1f}" '
            f'width="{bw - 4:.1f}" height="{max(bh, 1):.1f}" fill="{color}" opacity="{0.45 + 0.55 * v / mx:.2f}"><title>{i:02d}:00 — {v}</title></rect>'
        )
        if i % 3 == 0:
            out.append(f'<text class="sm" x="{px + i * bw + bw / 2:.1f}" y="{py + ph + 22}" text-anchor="middle">{i:02d}</text>')
    out.append(f'<line x1="{px}" y1="{py + ph + 7}" x2="{px + pw}" y2="{py + ph + 7}" stroke="{CYAN}" opacity="0.4"/>')
    if not a["commits_sampled"]:
        out.append(f'<text class="sm" x="{px + pw / 2}" y="{py + ph / 2}" text-anchor="middle">NO COMMIT SAMPLES</text>')

    # --- weekday bars
    wx, wy = 500, 84
    out.append(f'<text class="lbl" x="{wx}" y="{wy - 8}" style="fill:{MAGENTA}">&gt; WEEKDAY</text>')
    wmax = max(a["weekday"]) or 1
    for i, (name, v) in enumerate(zip(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], a["weekday"])):
        y = wy + 8 + i * 21
        out.append(f'<text class="sm" x="{wx}" y="{y + 9}">{name}</text>')
        out.append(_bar(wx + 38, y, 150, 10, v * 100 / wmax, MAGENTA if v == wmax else PURPLE, i * 0.06))
        out.append(f'<text class="sm" x="{wx + 196}" y="{y + 9}">{v}</text>')

    # --- monthly sparkline
    mx0, my0, mw, mh = 750, 84, 222, 120
    out.append(f'<text class="lbl" x="{mx0}" y="{my0 - 8}" style="fill:{YELLOW}">&gt; LAST 12 MONTHS</text>')
    counts = [m["count"] for m in a["months"]]
    mmax = max(counts) or 1
    step = mw / (len(counts) - 1)
    pts = [(mx0 + i * step, my0 + 10 + mh - mh * c / mmax) for i, c in enumerate(counts)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    area = path + f" L{pts[-1][0]:.1f},{my0 + 10 + mh} L{pts[0][0]:.1f},{my0 + 10 + mh} Z"
    out.append(f'<path d="{area}" fill="{YELLOW}" opacity="0.08"/>')
    out.append(f'<path d="{path}" fill="none" stroke="{YELLOW}" stroke-width="2" filter="url(#glow)"/>')
    for (x, y), m in zip(pts, a["months"]):
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{BG}" stroke="{YELLOW}"><title>{m["label"]} {m["year"]}: {m["count"]}</title></circle>')
    for i in (0, 3, 6, 9, 11):
        out.append(f'<text class="sm" x="{pts[i][0]:.1f}" y="{my0 + mh + 28}" text-anchor="middle">{a["months"][i]["label"].upper()}</text>')

    # --- footer readout
    peak = f"{a['peak_hour']:02d}:00" if a["peak_hour"] is not None else "—"
    readout = (
        f'PEAK HOUR <tspan style="fill:{MAGENTA};font-weight:700">{peak}</tspan>   '
        f'PEAK DAY <tspan style="fill:{MAGENTA};font-weight:700">{(a["peak_day"] or "—").upper()}</tspan>   '
        f'MODE <tspan style="fill:{GREEN};font-weight:700">{a["persona"] or "UNKNOWN"}</tspan>   '
        f'SAMPLE <tspan style="fill:{CYAN}">{a["commits_sampled"]} COMMITS</tspan>'
    )
    out.append(f'<text class="lbl" x="28" y="{h - 16}">{readout}</text>')
    return frame(w, h, "COMMIT ACTIVITY", "".join(out), tag="PULSE.06", accent=CYAN)


# ---------------------------------------------------------------- technology skills
def skills_card(skills: dict[str, list[str]]) -> str:
    w = FULL_W
    out, y = [], 84
    for gi, (group, items) in enumerate(skills.items()):
        color = ACCENTS[gi % len(ACCENTS)]
        out.append(f'<text class="lbl" x="28" y="{y + 15}" style="fill:{color}">{esc(fit(group, 170, 12))}</text>')
        x = 210
        for item in items:
            cw = len(item) * 12 * 0.6 + 26
            if x + cw > w - 28:
                x, y = 210, y + 34
            out.append(
                f'<g class="rise" style="animation-delay:{gi * 0.12:.2f}s">'
                f'<path d="M{x + 6},{y} H{x + cw} V{y + 16} L{x + cw - 6},{y + 22} H{x} V{y + 6} Z" '
                f'fill="{PANEL}" stroke="{color}" stroke-opacity="0.75"/>'
                f'<text x="{x + cw / 2:.1f}" y="{y + 15}" text-anchor="middle" style="font-size:12px">{esc(item)}</text></g>'
            )
            x += cw + 10
        y += 40
    h = y + 16
    return frame(w, h, "TECHNOLOGY SKILLS", "".join(out), tag="CHIP.07", accent=GREEN)


# ---------------------------------------------------------------- latest projects
def projects_card(projects: list[dict], today: date) -> str:
    w = FULL_W
    cols, tw, th = 2, (FULL_W - 56 - 16) / 2, 82
    rows = max(1, math.ceil(len(projects) / cols))
    h = 72 + rows * (th + 12) + 12
    out = []
    if not projects:
        out.append(f'<text class="lbl" x="28" y="100">NO PUBLIC PROJECTS FOUND</text>')
    for i, repo in enumerate(projects):
        r, c = divmod(i, cols)
        x, y = 28 + c * (tw + 16), 68 + r * (th + 12)
        lang = repo.get("primaryLanguage") or {}
        color = ACCENTS[i % len(ACCENTS)]
        desc = repo.get("description") or "No description."
        out.append(
            f'<a href="{esc(repo["url"])}"><g class="rise" style="animation-delay:{i * 0.08:.2f}s">'
            f'<path d="M{x + 10},{y} H{x + tw} V{y + th - 10} L{x + tw - 10},{y + th} H{x} V{y + 10} Z" fill="{PANEL}" stroke="{color}" stroke-opacity="0.7"/>'
            f'<rect x="{x}" y="{y + 10}" width="3" height="{th - 20}" fill="{color}" filter="url(#glow)"/>'
            f'<text class="val" x="{x + 16}" y="{y + 24}" style="fill:{color};font-size:14px">{esc(fit(repo["name"], tw - 150, 14))}</text>'
            f'<text class="sm" x="{x + tw - 14}" y="{y + 24}" text-anchor="end">{_ago(repo.get("pushedAt"), today)}</text>'
            f'<text class="sm" x="{x + 16}" y="{y + 46}" style="fill:{TEXT};opacity:.8">{esc(fit(desc, tw - 32, 11))}</text>'
            f'<circle cx="{x + 21}" cy="{y + 65}" r="4" fill="{lang.get("color") or MUTED}"/>'
            f'<text class="sm" x="{x + 31}" y="{y + 69}">{esc(lang.get("name") or "—")}</text>'
            f'<text class="sm" x="{x + tw - 14}" y="{y + 69}" text-anchor="end">'
            f'<tspan style="fill:{YELLOW}">★ {fmt_num(repo["stargazerCount"])}</tspan>  '
            f'<tspan style="fill:{MAGENTA}">⑂ {fmt_num(repo["forkCount"])}</tspan></text>'
            f"</g></a>"
        )
    return frame(w, h, "LATEST PROJECTS", "".join(out), tag="DECK.08", accent=MAGENTA)


# ---------------------------------------------------------------- wakatime
def wakatime_card(wk: dict | None) -> str:
    w = FULL_W
    if wk is None:
        h = 150
        body = (
            f'<text class="lbl flicker" x="28" y="94" style="fill:{MAGENTA};font-size:14px">⚠ LINK OFFLINE</text>'
            f'<text class="sm" x="28" y="118">Add a WAKATIME_API_KEY repository secret to stream coding-time telemetry here.</text>'
        )
        return frame(w, h, "WAKATIME // 7 DAYS", body, tag="TIME.09", accent=MAGENTA)
    if "error" in wk:
        h = 150
        body = (
            f'<text class="lbl flicker" x="28" y="94" style="fill:{MAGENTA};font-size:14px">⚠ LINK ERROR</text>'
            f'<text class="sm" x="28" y="118">WakaTime API refused the request — {esc(fit(wk["error"], 760, 11))}</text>'
        )
        return frame(w, h, "WAKATIME // 7 DAYS", body, tag="TIME.09", accent=MAGENTA)

    langs = wk["languages"][:6]
    h = max(220, 96 + len(langs) * 26 + 20)
    out = []
    tiles = [
        ("TOTAL", wk["total"], CYAN),
        ("DAILY AVG", wk["daily_average"], MAGENTA),
        ("BEST DAY", wk["best_day"] or "—", YELLOW),
    ]
    for i, (label, value, color) in enumerate(tiles):
        y = 80 + i * 40
        out.append(f'<text class="sm" x="28" y="{y}">{label}</text>')
        out.append(f'<text class="val" x="28" y="{y + 18}" style="fill:{color};font-size:15px">{esc(fit(value, 250, 15))}</text>')
    meta_y = 80 + 3 * 40
    if wk["editors"]:
        out.append(f'<text class="sm" x="28" y="{meta_y}">EDITOR  <tspan style="fill:{GREEN}">{esc(" · ".join(wk["editors"]))}</tspan></text>')
    if wk["operating_systems"]:
        out.append(f'<text class="sm" x="28" y="{meta_y + 18}">OS      <tspan style="fill:{GREEN}">{esc(" · ".join(wk["operating_systems"]))}</tspan></text>')

    lx = 330
    if not langs:
        out.append(f'<text class="lbl" x="{lx}" y="100">NO CODING TIME RECORDED</text>')
    for i, lang in enumerate(langs):
        y = 74 + i * 26
        color = ACCENTS[i % len(ACCENTS)]
        out.append(f'<text class="val" x="{lx}" y="{y + 10}" style="font-size:12px">{esc(fit(lang["name"], 130, 12))}</text>')
        out.append(_bar(lx + 140, y, 330, 10, lang["percent"], color, i * 0.07))
        out.append(f'<text class="sm" x="{lx + 480}" y="{y + 10}">{esc(lang["text"])}</text>')
        out.append(f'<text class="sm" x="{w - 28}" y="{y + 10}" text-anchor="end" style="fill:{color}">{lang["percent"]:.1f}%</text>')
    if not wk.get("up_to_date", True):
        out.append(f'<text class="sm" x="{w - 28}" y="{h - 14}" text-anchor="end">* WakaTime is still computing — numbers may lag</text>')
    return frame(w, h, "WAKATIME // " + wk["range"].upper(), "".join(out), tag="TIME.09", accent=CYAN)
