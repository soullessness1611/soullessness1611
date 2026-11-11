"""Single-image profile layouts: Zen Garden, Bento, Receipt, Seigaiha, Constellation, Sansui.

Each layout draws the whole profile as one picture. Most have a light and a dark variant;
the README shows the right one through <picture> and GitHub's colour scheme.
"""

from __future__ import annotations

import math
import random
from datetime import date, datetime, timedelta

from . import stats
from .theme import CJK, MONO, SANS, SERIF, esc, fmt_num, stable_int
from .waka_cards import short

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def prepare(raw: dict, cfg: dict, wakatime: dict | None, today: date) -> dict:
    """Everything the layouts draw, computed once."""
    user, repos, years = raw["user"], raw["repos"], raw["years"]
    rolling = user["contributionsCollection"]["contributionCalendar"]
    days = stats.merge_days(*(y["contributionCalendar"] for y in years), rolling)
    this_year = next((y for y in years if y["year"] == today.year), {})
    wk_ok = wakatime if wakatime and "error" not in wakatime else None
    wk = {
        "range": wk_ok["range"] if wk_ok else "last 7 days",
        "total": wk_ok["total"] if wk_ok else "—",
        "daily_average": wk_ok["daily_average"] if wk_ok else "—",
        "best_day": ((wk_ok or {}).get("best_day") or {}).get("text"),
        "languages": wk_ok["languages"] if wk_ok else [],
        "editors": [e["name"] for e in (wk_ok or {}).get("editors", [])][:2] or ["—"],
    }
    return {
        "name": cfg.get("display_name") or user.get("name") or user["login"], "login": user["login"],
        "tagline": cfg.get("tagline", ""), "joined": user["createdAt"][:4], "rolling": rolling, "days": days,
        "streak": stats.streaks(days, today), "repos": stats.repo_summary(repos),
        "langs": stats.top_languages(repos, cfg.get("exclude_languages", []), 6),
        "activity": stats.commit_activity(raw["commit_times"], days, cfg.get("timezone", "UTC"), today),
        "projects": stats.latest_projects(repos, 3), "skills": cfg.get("skills", {}),
        "commits_year": this_year.get("totalCommitContributions", 0) + this_year.get("restrictedContributionsCount", 0),
        "commits_all": sum(y["totalCommitContributions"] + y["restrictedContributionsCount"] for y in years),
        "prs": user["pullRequests"]["totalCount"], "issues": user["issues"]["totalCount"],
        "followers": user["followers"]["totalCount"], "wk": wk, "today": today,
    }


def svg(w, h, body, title, extra_style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{esc(title)}"><title>{esc(title)}</title><style>{extra_style}'
            '.fade{animation:fade 1.4s ease-out both}@keyframes fade{from{opacity:0}to{opacity:1}}'
            '@media (prefers-reduced-motion: reduce){.fade{animation:none}}</style>' + body + "</svg>\n")


# ------------------------------------------------------------------ Zen Garden
def garden(d, mode):
    p = dict(sand="#efe9dc", rake="#d8cfbb", ring="#cbbfa6", ink="#2a2723", muted="#857b6c", stone="#4a4640",
             hi="#6d675f", moss="#6f8f57", seal="#b8402f", line="#2a2723") if mode == "light" else \
        dict(sand="#17171b", rake="#26262c", ring="#33333b", ink="#e6e0d2", muted="#8d877a", stone="#a59d8e",
             hi="#cfc7b6", moss="#8fa86f", seal="#c0503b", line="#e6e0d2")
    W, H = 1000, 560
    gx, gy, gw, gh = 50, 150, 900, 196
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{p["sand"]}" stroke="{p["line"]}" stroke-opacity="0.15"/>']
    # title block
    out.append(f'<text x="50" y="74" style="font-family:{SERIF};font-size:40px;font-weight:600;letter-spacing:6px;fill:{p["ink"]}">{esc(d["name"])}</text>')
    out.append(f'<text x="52" y="106" style="font-family:{SERIF};font-size:14px;letter-spacing:3px;fill:{p["muted"]}">{esc(d["tagline"].replace("//", "·").lower())}</text>')
    out.append(f'<rect x="{W - 92}" y="44" width="42" height="42" rx="6" fill="{p["seal"]}"/>'
               f'<text x="{W - 71}" y="74" text-anchor="middle" style="font-family:{CJK};font-size:26px;fill:{p["sand"]}">禅</text>')
    out.append(f'<text x="{W - 104}" y="62" text-anchor="end" style="font-family:{SERIF};font-size:13px;fill:{p["muted"]}">@{esc(d["login"])}</text>'
               f'<text x="{W - 104}" y="82" text-anchor="end" style="font-family:{SERIF};font-size:13px;fill:{p["muted"]}">since {d["joined"]}</text>')
    # raked sand
    out.append(f'<clipPath id="g"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10"/></clipPath><g clip-path="url(#g)">')
    out.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="{p["sand"]}"/>')
    for y in range(gy + 4, gy + gh, 7):
        seg = " ".join(f"Q{gx + 30 * k + 15},{y + (1.3 if k % 2 else -1.3)} {gx + 30 * (k + 1)},{y}" for k in range(gw // 30 + 1))
        out.append(f'<path d="M{gx},{y} {seg}" fill="none" stroke="{p["rake"]}" stroke-width="1.6"/>')
    weeks = d["rolling"]["weeks"][-53:]
    sx, sy = gw / 53, gh / 7
    stones, pebbles = [], []
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            lvl = LEVELS.get(day.get("contributionLevel", "NONE"), 0)
            cx, cy = gx + (wi + 0.5) * sx, gy + (day["weekday"] + 0.5) * sy
            if lvl >= 3:
                stones.append((lvl, cx, cy, day))
            elif lvl:
                pebbles.append((lvl, cx, cy, day))
    for lvl, cx, cy, day in pebbles:
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{1.4 + lvl * 0.7:.1f}" fill="{p["stone"]}" opacity="{0.35 + lvl * 0.15:.2f}">'
                   f'<title>{day["date"]}: {day["contributionCount"]}</title></circle>')
    for lvl, cx, cy, day in sorted(stones):
        rings = 3 if lvl == 4 else 2
        rmax = 6 + rings * 4.5
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rmax + 1:.1f}" fill="{p["sand"]}"/>')
        for k in range(rings, 0, -1):
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{6 + k * 4.5:.1f}" fill="none" stroke="{p["ring"]}" stroke-width="1.4"/>')
        rot = (stable_int(day["date"]) % 60) - 30
        rx = 6.5 if lvl == 4 else 5
        out.append(f'<g class="fade"><ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{rx * 0.72:.1f}" transform="rotate({rot} {cx:.1f} {cy:.1f})" fill="{p["stone"]}">'
                   f'<title>{day["date"]}: {day["contributionCount"]}</title></ellipse>'
                   f'<ellipse cx="{cx - 1.5:.1f}" cy="{cy - 1.6:.1f}" rx="{rx * 0.35:.1f}" ry="{rx * 0.2:.1f}" fill="{p["hi"]}" opacity="0.6"/>'
                   + (f'<path d="M{cx - rx:.1f},{cy + 2:.1f} q{rx * 0.6:.1f},{rx * 0.5:.1f} {rx * 1.3:.1f},{rx * 0.15:.1f}" stroke="{p["moss"]}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.8"/>' if lvl == 4 else "")
                   + "</g>")
    out.append("</g>")
    # month marks
    last = None
    for wi, week in enumerate(weeks):
        m = date.fromisoformat(week["contributionDays"][0]["date"])
        if m.month != last and wi < len(weeks) - 2:
            out.append(f'<text x="{gx + wi * sx:.1f}" y="{gy + gh + 22}" style="font-family:{SERIF};font-size:11px;letter-spacing:1px;fill:{p["muted"]}">{m.strftime("%b").lower()}</text>')
            last = m.month
    # stones of record
    st, rs = d["streak"], d["repos"]
    facts = [
        (fmt_num(d["rolling"]["totalContributions"]), "contributions this year"),
        (str(st["current"]["length"]), f"day streak · longest {st['longest']['length']}"),
        (str(rs["count"]), f"repositories · {rs['stars']} stars"),
        (short(d["wk"]["total"]), "coded last week"),
    ]
    for i, (big, small) in enumerate(facts):
        x = 50 + i * 225
        out.append(f'<text x="{x}" y="430" style="font-family:{SERIF};font-size:34px;font-weight:600;fill:{p["ink"]}">{esc(big)}</text>'
                   f'<text x="{x}" y="454" style="font-family:{SERIF};font-size:13px;letter-spacing:1px;fill:{p["muted"]}">{esc(small)}</text>')
    out.append(f'<rect x="50" y="482" width="{W - 100}" height="1" fill="{p["line"]}" opacity="0.15"/>')
    x = 50
    for lang in d["langs"][:5]:
        label = f'{lang["name"]} {lang["percent"]:.0f}%'
        out.append(f'<circle cx="{x + 5}" cy="{512}" r="4.5" fill="{lang["color"]}"/>'
                   f'<text x="{x + 16}" y="517" style="font-family:{SERIF};font-size:14px;fill:{p["ink"]}">{esc(label)}</text>')
        x += 16 + len(label) * 8.2 + 26
    out.append(f'<text x="{W - 50}" y="517" text-anchor="end" style="font-family:{SERIF};font-size:12px;font-style:italic;fill:{p["muted"]}">one stone for every busy day</text>')
    return svg(W, H, "".join(out), "Zen garden of contributions")


# ------------------------------------------------------------------ Bento
def bento(d, mode):
    p = dict(tile="#f6f8fa", edge="#d0d7de", fg="#1f2328", muted="#656d76", a="#0969da", b="#bf3989", c="#1a7f37",
             d="#9a6700", heat=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"], track="#eaeef2") if mode == "light" else \
        dict(tile="#161b22", edge="#30363d", fg="#e6edf3", muted="#8d96a0", a="#4493f8", b="#f778ba", c="#3fb950",
             d="#d29922", heat=["#1f242c", "#0e4429", "#006d32", "#26a641", "#39d353"], track="#21262d")
    W, G = 1000, 12
    out = []

    def tile(x, y, w, h):
        out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="18" fill="{p["tile"]}" stroke="{p["edge"]}"/>')

    def t(x, y, s, size=13, fill=None, weight=400, anchor="start", extra=""):
        out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-family:{SANS};font-size:{size}px;font-weight:{weight};fill:{fill or p["fg"]}{extra}">{esc(s)}</text>')

    st, rs = d["streak"], d["repos"]
    # row 1
    y = 0
    tile(0, y, 580, 170)
    t(28, y + 42, f"@{d['login']}", 13, p["muted"])
    t(28, y + 96, d["name"], 44, weight=700, extra=";letter-spacing:-1px")
    t(28, y + 130, d["tagline"].replace(" // ", " · ").title().replace("Dev", "Dev"), 15, p["muted"])
    t(552, y + 42, f"since {d['joined']}", 12, p["muted"], anchor="end")
    tile(592, y, 196, 170)
    t(616, y + 36, "Current streak", 12, p["muted"])
    t(616, y + 112, str(st["current"]["length"]), 64, p["b"], 700, extra=";letter-spacing:-2px")
    t(616 + 18 + len(str(st["current"]["length"])) * 36, y + 112, "days", 15, p["muted"])
    t(616, y + 146, f"Longest {st['longest']['length']} days", 12, p["muted"])
    tile(800, y, 200, 170)
    t(824, y + 36, "Repositories", 12, p["muted"])
    t(824, y + 112, str(rs["count"]), 64, p["a"], 700, extra=";letter-spacing:-2px")
    t(824, y + 146, f"{rs['stars']} stars · {rs['forks']} forks", 12, p["muted"])
    # row 2 heatmap
    y = 170 + G
    tile(0, y, W, 176)
    t(28, y + 40, fmt_num(d["rolling"]["totalContributions"]), 34, weight=700)
    t(28, y + 62, "contributions", 13, p["muted"])
    t(28, y + 80, "in the last year", 13, p["muted"])
    t(28, y + 140, f"{fmt_num(d['commits_all'])} commits all-time", 12, p["muted"])
    weeks = d["rolling"]["weeks"][-53:]
    hx, hy, step = 196, y + 22, 14.6
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            lvl = LEVELS.get(day.get("contributionLevel", "NONE"), 0)
            out.append(f'<rect x="{hx + wi * step:.1f}" y="{hy + day["weekday"] * step:.1f}" width="11.5" height="11.5" rx="3" fill="{p["heat"][lvl]}">'
                       f'<title>{day["date"]}: {day["contributionCount"]}</title></rect>')
    last = None
    for wi, week in enumerate(weeks):
        m = date.fromisoformat(week["contributionDays"][0]["date"])
        if m.month != last and wi < len(weeks) - 2:
            t(f"{hx + wi * step:.1f}", hy + 7 * step + 16, m.strftime("%b"), 11, p["muted"])
            last = m.month
    # row 3
    y += 176 + G
    tile(0, y, 330, 230)
    t(24, y + 34, "Top languages", 12, p["muted"])
    cx, cy, r = 92, y + 130, 58
    ang = -90.0
    for lang in d["langs"]:
        sweep = 360 * lang["percent"] / 100
        a0, a1 = math.radians(ang), math.radians(ang + max(sweep - 1.5, 0.5))
        large = 1 if sweep > 180 else 0
        out.append(f'<path d="M{cx + r * math.cos(a0):.1f},{cy + r * math.sin(a0):.1f} A{r},{r} 0 {large} 1 {cx + r * math.cos(a1):.1f},{cy + r * math.sin(a1):.1f}" '
                   f'fill="none" stroke="{lang["color"]}" stroke-width="20"/>')
        ang += sweep
    t(cx, cy + 6, f'{d["langs"][0]["percent"]:.0f}%', 20, weight=700, anchor="middle")
    for i, lang in enumerate(d["langs"][:6]):
        ly = y + 72 + i * 24
        out.append(f'<circle cx="190" cy="{ly - 4}" r="5" fill="{lang["color"]}"/>')
        t(202, ly, lang["name"], 13)
        t(306, ly, f'{lang["percent"]:.1f}%', 12, p["muted"], anchor="end")
    tile(342, y, 330, 230)
    wk = d["wk"]
    t(366, y + 34, f"WakaTime · {wk['range']}", 12, p["muted"])
    t(366, y + 86, short(wk["total"]), 40, p["c"], 700, extra=";letter-spacing:-1px")
    t(366, y + 110, f"avg {short(wk['daily_average'])} / day · best {short(wk['best_day'])}", 12, p["muted"])
    for i, lang in enumerate(wk["languages"][:4]):
        ly = y + 140 + i * 22
        t(366, ly + 9, lang["name"], 12)
        out.append(f'<rect x="460" y="{ly}" width="150" height="10" rx="5" fill="{p["track"]}"/>'
                   f'<rect x="460" y="{ly}" width="{max(6, 150 * lang["percent"] / 100):.1f}" height="10" rx="5" fill="{p["c"]}"/>')
        t(648, ly + 9, short(lang["text"]), 11, p["muted"], anchor="end")
    tile(684, y, 316, 230)
    a = d["activity"]
    t(708, y + 34, "When I commit", 12, p["muted"])
    mx = max(a["hours"]) or 1
    for i, v in enumerate(a["hours"]):
        bh = 110 * v / mx
        out.append(f'<rect x="{708 + i * 11:.1f}" y="{y + 160 - bh:.1f}" width="8" height="{max(bh, 2):.1f}" rx="3" '
                   f'fill="{p["b"] if i == a["peak_hour"] else p["a"]}" opacity="{1 if v else 0.25}"/>')
    for i in (0, 6, 12, 18):
        t(708 + i * 11 + 4, y + 178, f"{i:02d}", 10, p["muted"], anchor="middle")
    peak = f"{a['peak_hour']:02d}:00" if a["peak_hour"] is not None else "—"
    t(708, y + 208, f"Peak {peak} · {(a['persona'] or '').title()}", 12, p["muted"])
    # row 4
    y += 230 + G
    tile(0, y, 658, 160)
    t(24, y + 34, "Latest projects", 12, p["muted"])
    for i, repo in enumerate(d["projects"]):
        ly = y + 70 + i * 32
        lang = repo.get("primaryLanguage") or {}
        out.append(f'<circle cx="30" cy="{ly - 5}" r="5" fill="{lang.get("color") or p["muted"]}"/>')
        t(44, ly, repo["name"], 14, weight=600)
        desc = (repo.get("description") or "").strip()
        desc = desc if desc.isascii() else ""
        t(300, ly, (desc[:44] + "…") if len(desc) > 45 else desc, 12, p["muted"])
        pushed = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00")).date()
        ago = (d["today"] - pushed).days
        t(634, ly, "today" if ago <= 0 else f"{ago}d ago" if ago < 60 else f"{ago // 30}mo ago", 12, p["muted"], anchor="end")
    tile(670, y, 330, 160)
    nums = [("Commits " + str(d["today"].year), d["commits_year"]), ("Pull requests", d["prs"]),
            ("Issues", d["issues"]), ("Followers", d["followers"])]
    for i, (label, v) in enumerate(nums):
        nx, ny = 694 + (i % 2) * 154, y + 62 + (i // 2) * 64
        t(nx, ny, fmt_num(v), 26, weight=700)
        t(nx, ny + 20, label, 12, p["muted"])
    H = y + 160
    return svg(W, H, "".join(out), "Bento profile")


# ------------------------------------------------------------------ Receipt
def receipt(d, mode):
    paper, ink, faint = "#fbfaf6", "#26241f", "#8c877c"
    W, cw, lh = 440, 7.8, 21
    cols = 48
    left = (W - cols * cw) / 2
    lines = []  # (text, kind)

    def row(a, b="", fill="."):
        gap = cols - len(a) - len(b)
        lines.append((a + (" " + fill * (gap - 2) + " " if gap > 2 else " " * max(gap, 1)) + b, "row"))

    def center(s, kind="row"):
        lines.append((s.center(cols), kind))

    def rule(ch="-"):
        lines.append((ch * cols, "rule"))

    today = d["today"]
    st, rs, wk = d["streak"], d["repos"], d["wk"]
    center(d["name"].upper(), "big")
    center("DEV SUPPLY CO. · EST. " + d["joined"])
    center(f"github.com/{d['login']}")
    rule("=")
    row(f"DATE {today.isoformat()}", today.strftime('%A').upper(), " ")
    row(f"ORDER #{d['login'][-4:]}", "TERMINAL 01", " ")
    rule()
    row("QTY ITEM", "PCT", " ")
    for lang in d["langs"][:6]:
        row(f"1x  {lang['name'].upper()}", f"{lang['percent']:.1f}%")
    rule()
    row(f"COMMITS {today.year}", fmt_num(d["commits_year"]))
    row("PULL REQUESTS", str(d["prs"]))
    row("ISSUES OPENED", str(d["issues"]))
    row("REPOSITORIES", str(rs["count"]))
    row("STARS EARNED", str(rs["stars"]))
    rule()
    row("SUBTOTAL CONTRIBUTIONS 1Y", fmt_num(d["rolling"]["totalContributions"]))
    row("STREAK BONUS", f"{st['current']['length']} DAYS")
    row("LONGEST RUN ON RECORD", f"{st['longest']['length']} DAYS")
    row("WAKATIME LAST WEEK", short(wk["total"]).upper())
    rule("=")
    lines.append(("TOTAL".ljust(cols - 12) + f"{fmt_num(d['commits_all'])} COMMITS".rjust(12), "total"))
    rule("=")
    row("PAID WITH", "CAFFEINE + CURIOSITY", " ")
    row("SERVED BY", " · ".join(wk["editors"]).upper(), " ")
    lines.append(("", "row"))
    center("THANK YOU FOR SHIPPING")
    center("KEEP THE STREAK ALIVE · COME BACK TOMORROW")

    top = 40
    out = []
    body_h = top + len(lines) * lh + 150
    H = int(body_h)
    zig = " ".join(f"L{x},{8 if (x // 10) % 2 else 0}" for x in range(0, W + 10, 10))
    zig_b = " ".join(f"L{x},{H - 8 if (x // 10) % 2 else H}" for x in range(W, -10, -10))
    out.append(f'<path d="M0,8 {zig} L{W},{H - 8} {zig_b} Z" fill="{paper}"/>')
    y = top
    for text, kind in lines:
        y += lh
        if kind == "big":
            out.append(f'<text x="{W / 2}" y="{y}" text-anchor="middle" style="font-family:{MONO};font-size:20px;font-weight:800;letter-spacing:2px;fill:{ink}">{esc(text.strip())}</text>')
            continue
        if kind == "total":
            out.append(f'<text x="{left}" y="{y}" xml:space="preserve" style="font-family:{MONO};font-size:13px;font-weight:800;fill:{ink}">{esc(text)}</text>')
            continue
        fill = faint if kind == "rule" else ink
        out.append(f'<text x="{left}" y="{y}" xml:space="preserve" style="font-family:{MONO};font-size:13px;fill:{fill}">{esc(text)}</text>')
    # barcode from the last 84 days
    by = y + 26
    days = [d["days"].get(today - timedelta(days=k), 0) for k in range(83, -1, -1)]
    mx = max(days) or 1
    x = (W - 84 * 4) / 2
    for c in days:
        wbar = 1 if c == 0 else 2 if c < mx * 0.34 else 3
        out.append(f'<rect x="{x:.1f}" y="{by}" width="{wbar}" height="58" fill="{ink}" opacity="{0.35 if c == 0 else 1}"/>')
        x += 4
    out.append(f'<text x="{W / 2}" y="{by + 78}" text-anchor="middle" style="font-family:{MONO};font-size:10px;letter-spacing:2px;fill:{faint}">LAST 84 DAYS OF CONTRIBUTIONS</text>')
    return svg(W, H, "".join(out), "Developer receipt")



def smooth(pts):
    """Catmull-Rom through pts -> cubic Bézier path data (starting with M)."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def title_block(p, d, x=56, y=78, size=38):
    return (f'<text x="{x}" y="{y}" style="font-family:{SERIF};font-size:{size}px;font-weight:600;letter-spacing:5px;fill:{p["ink"]}">{esc(d["name"])}</text>'
            f'<text x="{x + 2}" y="{y + 28}" style="font-family:{SERIF};font-size:13px;letter-spacing:4px;fill:{p["muted"]}">GITHUB PROFILE · @{esc(d["login"]).upper()}</text>')


def seal(p, x, y, s=40, ch="禅"):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="5" fill="{p["seal"]}"/>'
            f'<text x="{x + s / 2}" y="{y + s * 0.72}" text-anchor="middle" style="font-family:{CJK};font-size:{s * 0.62:.0f}px;fill:{p["bg"]}">{ch}</text>')


def facts_row(p, d, y, x0=56, gap=222):
    st, rs = d["streak"], d["repos"]
    facts = [(fmt_num(d["rolling"]["totalContributions"]), "contributions · 1 year"),
             (f'{st["current"]["length"]} / {st["longest"]["length"]}', "streak now / longest"),
             (str(rs["count"]), "public repositories"),
             (short(d["wk"]["total"]), "coded last week")]
    out = []
    for i, (big, small) in enumerate(facts):
        x = x0 + i * gap
        out.append(f'<text x="{x}" y="{y}" style="font-family:{SERIF};font-size:28px;font-weight:600;fill:{p["ink"]}">{esc(big)}</text>'
                   f'<text x="{x}" y="{y + 22}" style="font-family:{SERIF};font-size:12px;letter-spacing:1.5px;fill:{p["muted"]}">{esc(small)}</text>')
    return "".join(out)


def lang_row(p, d, y, x=56, n=5, size=13):
    out = []
    for lang in d["langs"][:n]:
        label = f'{lang["name"]} {lang["percent"]:.0f}%'
        out.append(f'<circle cx="{x + 5}" cy="{y - 5}" r="4.5" fill="{lang["color"]}"/>'
                   f'<text x="{x + 16}" y="{y}" style="font-family:{SERIF};font-size:{size}px;fill:{p["ink"]}">{esc(label)}</text>')
        x += 16 + len(label) * size * 0.56 + 24
    return "".join(out)


# ------------------------------------------------------------------ Seigaiha 青海波
def seigaiha(d, mode):
    p = dict(bg="#f4efe4", ink="#1d2b44", muted="#7d7769", line="#1d2b44", seal="#b8402f",
             fill=["none", "#c9d3e3", "#8ea3c4", "#4e6a98", "#1f3a68"], empty="#d6d0c2") if mode == "light" else \
        dict(bg="#0e1626", ink="#e8e4da", muted="#8c93a3", line="#e8e4da", seal="#c0503b",
             fill=["none", "#22385e", "#36568b", "#5d84c2", "#a9c3ea"], empty="#26324a")
    W, H = 1000, 470
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{p["bg"]}" stroke="{p["line"]}" stroke-opacity="0.15"/>',
           title_block(p, d), seal(p, W - 96, 46)]
    weeks = d["rolling"]["weeks"][-53:]
    r, step = 9.2, 16.8
    ox, oy = 56 + r, 196
    cells = []
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            row = day["weekday"]
            cx = ox + wi * step + (step / 2 if row % 2 else 0)
            cy = oy + row * (r * 1.45)
            cells.append((cy, cx, LEVELS.get(day.get("contributionLevel", "NONE"), 0), day))
    # draw top row first so lower rows overlap it, like real seigaiha
    for cy, cx, lvl, day in sorted(cells, key=lambda c: (c[0], c[1])):
        arcs = []
        for k, rr in enumerate((r, r * 0.72, r * 0.46, r * 0.22)):
            fill = p["fill"][lvl] if (k == 0 and lvl) else (p["bg"] if k == 0 else "none")
            stroke = p["ink"] if lvl >= 3 and k else (p["line"] if lvl else p["empty"])
            op = 0.9 if lvl else 1
            arcs.append(f'<path d="M{cx - rr:.1f},{cy:.1f} A{rr:.1f},{rr:.1f} 0 0 1 {cx + rr:.1f},{cy:.1f} Z" fill="{fill}" '
                        f'stroke="{stroke if k else (p["line"] if lvl else p["empty"])}" stroke-width="{1.1 if k else 1.2}" stroke-opacity="{op if k else (0.55 if lvl else 1)}"/>')
            if k == 0 and lvl >= 3:
                pass
        out.append(f'<g><title>{day["date"]}: {day["contributionCount"]}</title>{"".join(arcs)}</g>')
    # month marks
    last = None
    for wi, week in enumerate(weeks):
        m = date.fromisoformat(week["contributionDays"][0]["date"])
        if m.month != last and wi < len(weeks) - 2:
            out.append(f'<text x="{ox + wi * step - r:.1f}" y="{oy + 7 * r * 1.45 + 14:.1f}" style="font-family:{SERIF};font-size:11px;letter-spacing:1px;fill:{p["muted"]}">{m.strftime("%b").lower()}</text>')
            last = m.month
    out.append(f'<text x="{W - 56}" y="{oy - 22}" text-anchor="end" style="font-family:{SERIF};font-size:12px;font-style:italic;fill:{p["muted"]}">every wave is a day · deeper indigo, more commits</text>')
    out.append(f'<rect x="56" y="{H - 128}" width="{W - 112}" height="1" fill="{p["line"]}" opacity="0.15"/>')
    out.append(facts_row(p, d, H - 86))
    out.append(lang_row(p, d, H - 30))
    return svg(W, H, "".join(out), "Seigaiha contributions")


# ------------------------------------------------------------------ Constellation
def constellation(d, mode):
    p = dict(bg0="#0d1430", bg1="#04060f", ink="#eef0f8", muted="#8b93b3", star="#fff6dc", gold="#f2c879", line="#9fb0e8", seal="#c0503b", bg="#04060f")
    W, H = 1000, 540
    rnd = random.Random(1611)
    out = ['<defs><radialGradient id="sky" cx="70%" cy="10%" r="95%"><stop offset="0" stop-color="#1a2350"/>'
           f'<stop offset="0.55" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></radialGradient>'
           '<radialGradient id="halo"><stop offset="0" stop-color="#fff6dc" stop-opacity="0.9"/><stop offset="1" stop-color="#fff6dc" stop-opacity="0"/></radialGradient>'
           '<filter id="soft"><feGaussianBlur stdDeviation="0.6"/></filter></defs>',
           f'<rect width="{W}" height="{H}" rx="16" fill="url(#sky)"/>']
    for _ in range(260):  # dust
        out.append(f'<circle cx="{rnd.uniform(8, W - 8):.1f}" cy="{rnd.uniform(8, H - 8):.1f}" r="{rnd.choice((0.4, 0.5, 0.7, 0.9))}" fill="#ffffff" opacity="{rnd.uniform(0.15, 0.55):.2f}"/>')
    # milky way band
    out.append(f'<path d="M-20,{H * 0.82:.0f} C{W * 0.3:.0f},{H * 0.45:.0f} {W * 0.6:.0f},{H * 0.62:.0f} {W + 20},{H * 0.18:.0f}" stroke="#9fb0e8" stroke-width="90" fill="none" opacity="0.05" stroke-linecap="round"/>')
    # moon
    mx, my = W - 110, 92
    out.append(f'<circle cx="{mx}" cy="{my}" r="34" fill="url(#halo)" opacity="0.35"/><circle cx="{mx}" cy="{my}" r="22" fill="#f6efd9"/>'
               f'<circle cx="{mx + 9}" cy="{my - 5}" r="20" fill="#0f1840"/>')
    out.append(title_block(dict(ink=p["ink"], muted=p["muted"]), d))
    # stars: days in last year
    weeks = d["rolling"]["weeks"][-53:]
    gx, gy, gw, sky_bottom = 70, 175, 860, 380
    first = date.fromisoformat(weeks[0]["contributionDays"][0]["date"])
    span = (d["today"] - first).days or 1
    counts = [x["contributionCount"] for w in weeks for x in w["contributionDays"]]
    cmax = math.log2(max(counts) + 1) or 1
    pos = {}
    for week in weeks:
        for day in week["contributionDays"]:
            lvl = LEVELS.get(day.get("contributionLevel", "NONE"), 0)
            if not lvl:
                continue
            dt = date.fromisoformat(day["date"])
            j = random.Random(day["date"])
            x = gx + gw * (dt - first).days / span
            y = sky_bottom - 26 - (sky_bottom - gy - 40) * math.log2(day["contributionCount"] + 1) / cmax + j.uniform(-9, 9)
            pos[dt] = (x, y, lvl, day)
    sx = gw / 53
    # constellations: link consecutive active days
    runs, cur = [], []
    for dt in sorted(pos):
        if cur and dt - cur[-1] == timedelta(days=1):
            cur.append(dt)
        else:
            if len(cur) > 1:
                runs.append(cur)
            cur = [dt]
    if len(cur) > 1:
        runs.append(cur)
    longest = max(runs, key=len) if runs else []
    for run in runs:
        pts = " ".join(f"{pos[t][0]:.1f},{pos[t][1]:.1f}" for t in run)
        is_long = run is longest
        out.append(f'<polyline points="{pts}" fill="none" stroke="{p["gold"] if is_long else p["line"]}" stroke-width="{1.1 if is_long else 0.8}" opacity="{0.75 if is_long else 0.35}"/>')
    for dt, (x, y, lvl, day) in pos.items():
        tip = f'<title>{day["date"]}: {day["contributionCount"]}</title>'
        if lvl >= 3:
            s = 7 if lvl == 4 else 5
            out.append(f'<g>{tip}<circle cx="{x:.1f}" cy="{y:.1f}" r="{s * 1.8:.1f}" fill="url(#halo)" opacity="0.5"/>'
                       f'<path d="M{x:.1f},{y - s:.1f} L{x + s * 0.18:.1f},{y - s * 0.18:.1f} L{x + s:.1f},{y:.1f} L{x + s * 0.18:.1f},{y + s * 0.18:.1f} '
                       f'L{x:.1f},{y + s:.1f} L{x - s * 0.18:.1f},{y + s * 0.18:.1f} L{x - s:.1f},{y:.1f} L{x - s * 0.18:.1f},{y - s * 0.18:.1f} Z" fill="{p["star"]}"/></g>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.2 + lvl * 0.6:.1f}" fill="{p["star"]}" opacity="{0.55 + lvl * 0.15:.2f}">{tip}</circle>')
    if longest:
        lx, ly = pos[longest[len(longest) // 2]][:2]
        ly = min(pos[t][1] for t in longest)
        out.append(f'<text x="{lx:.1f}" y="{gy - 22}" text-anchor="middle" style="font-family:{SERIF};font-size:12px;font-style:italic;fill:{p["gold"]}">'
                   f'the long run · {len(longest)} nights · {longest[0].strftime("%b %d").lower()}</text>'
                   f'<line x1="{lx:.1f}" y1="{gy - 16}" x2="{lx:.1f}" y2="{ly - 12:.1f}" stroke="{p["gold"]}" stroke-width="0.6" stroke-dasharray="2 3" opacity="0.7"/>')
    # horizon months
    hy = sky_bottom + 8
    out.append(f'<line x1="{gx - 10}" y1="{hy}" x2="{gx + 53 * sx}" y2="{hy}" stroke="{p["line"]}" stroke-opacity="0.25"/>')
    last = None
    for wi, week in enumerate(weeks):
        m = date.fromisoformat(week["contributionDays"][0]["date"])
        if m.month != last and wi < len(weeks) - 2:
            out.append(f'<line x1="{gx + wi * sx:.1f}" y1="{hy - 4}" x2="{gx + wi * sx:.1f}" y2="{hy + 4}" stroke="{p["line"]}" stroke-opacity="0.4"/>'
                       f'<text x="{gx + wi * sx + 4:.1f}" y="{hy + 18}" style="font-family:{SERIF};font-size:11px;letter-spacing:1px;fill:{p["muted"]}">{m.strftime("%b").lower()}</text>')
            last = m.month
    out.append(facts_row(dict(ink=p["ink"], muted=p["muted"]), d, H - 60))
    return svg(W, H, "".join(out), "Constellation of contributions")


# ------------------------------------------------------------------ Sansui 山水
def sansui(d, mode):
    p = dict(bg="#f2ede2", ink="#26241f", muted="#7d7668", mist="#f2ede2", sun="#c4472f", seal="#b8402f", far="#8f8a80", mid="#59554d", near="#26241f") if mode == "light" else \
        dict(bg="#121214", ink="#ebe5d6", muted="#8a8478", mist="#121214", sun="#d0644c", seal="#c0503b", far="#3a3a3f", mid="#5e5c5b", near="#a39d90")
    W, H = 1000, 540
    out = [f'<defs>'
           + "".join(f'<linearGradient id="wash{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/>'
                     f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>'
                     for k, c, o in (("far", p["far"], 0.55), ("mid", p["mid"], 0.75), ("near", p["near"], 0.92)))
           + '<filter id="brush"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7"/>'
             '<feDisplacementMap in="SourceGraphic" scale="5"/></filter></defs>',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{p["bg"]}" stroke="{p["ink"]}" stroke-opacity="0.15"/>']
    st = d["streak"]
    # sun
    out.append(f'<circle cx="{W - 190}" cy="150" r="{34 + min(st["current"]["length"], 30) * 1.2:.0f}" fill="{p["sun"]}" opacity="0.9"/>')
    out.append(title_block(p, d))
    base = 400
    # far ridge: 12 months
    months = d["activity"]["months"]
    mmax = max(m["count"] for m in months) or 1
    fx = [40 + i * (W - 80) / 11 for i in range(12)]
    far = [(x, base - 70 - 150 * m["count"] / mmax) for x, m in zip(fx, months)]
    far = [(0, far[0][1] + 6)] + far + [(W, far[-1][1] + 6)]
    # mid ridge: weekly totals (53)
    weeks = d["rolling"]["weeks"][-53:]
    wt = [sum(x["contributionCount"] for x in w["contributionDays"]) for w in weeks]
    wmax = max(wt) or 1
    mid = [(20 + i * (W - 40) / 52, base - 30 - 120 * (v / wmax) ** 0.8) for i, v in enumerate(wt)]
    mid = [(0, mid[0][1] + 4)] + mid + [(W, mid[-1][1] + 4)]
    # near ridge: gentle hills from 30-day rolling sum, low
    days = d["days"]
    today = d["today"]
    roll = []
    for i in range(0, 365, 14):
        dt = today - timedelta(days=364 - i)
        roll.append(sum(days.get(dt + timedelta(days=k), 0) for k in range(-15, 15)))
    rmax = max(roll) or 1
    near = [(i * W / (len(roll) - 1), base + 40 - 70 * v / rmax) for i, v in enumerate(roll)]
    for key, pts, bottom in (("far", far, base + 60), ("mid", mid, base + 80), ("near", near, H - 64)):
        path = smooth(pts) + f" L{pts[-1][0]:.1f},{bottom} L{pts[0][0]:.1f},{bottom} Z"
        out.append(f'<path d="{path}" fill="url(#wash{key})" filter="url(#brush)"/>')
        out.append(f'<path d="{smooth(pts)}" fill="none" stroke="{p[key]}" stroke-width="{1.2 if key != "near" else 2}" opacity="0.8" filter="url(#brush)"/>')
    # mist bands
    out.insert(1, '<linearGradient id="mistg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
                  '<stop offset="0.5" stop-color="%s" stop-opacity="0.85"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % ((p["mist"],) * 3))
    for y, hgt in ((base - 34, 56), (base + 34, 44)):
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{hgt}" fill="url(#mistg)"/>')
    out.append(f'<rect x="0" y="{H - 66}" width="{W}" height="66" fill="{p["bg"]}"/>')
    # peak annotation on the far ridge
    pk = max(range(12), key=lambda i: months[i]["count"])
    px, py = far[pk]
    out.append(f'<line x1="{px:.1f}" y1="{py - 6:.1f}" x2="{px:.1f}" y2="{py - 46:.1f}" stroke="{p["ink"]}" stroke-width="0.7" opacity="0.6"/>'
               f'<text x="{px - 6:.1f}" y="{py - 40:.1f}" text-anchor="end" style="font-family:{SERIF};font-size:12px;font-style:italic;fill:{p["ink"]}">'
               f'highest peak · {months[pk]["label"].lower()} {months[pk]["year"]} · {months[pk]["count"]} contributions</text>')
    # birds = streak days (max 5)
    for i in range(min(max(st["current"]["length"], 1), 5)):
        bx, by = W - 330 + i * 26, 120 + (i % 2) * 14
        out.append(f'<path d="M{bx},{by} q5,-5 9,0 q4,-5 9,0" fill="none" stroke="{p["ink"]}" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(f'<text x="{W - 330}" y="170" style="font-family:{SERIF};font-size:12px;font-style:italic;fill:{p["muted"]}">{st["current"]["length"]}-day streak in flight</text>')
    out.append(seal(p, W - 96, 46))
    # footer on the near ridge
    footer = (f'{fmt_num(d["rolling"]["totalContributions"])} contributions · {d["repos"]["count"]} repositories · '
              f'{short(d["wk"]["total"])} last week · longest streak {st["longest"]["length"]} days')
    out.append(f'<text x="{W / 2}" y="{H - 30}" text-anchor="middle" style="font-family:{SERIF};font-size:15px;letter-spacing:1.5px;fill:{p["muted"]}">{esc(footer)}</text>')
    return svg(W, H, "".join(out), "Sansui mountains of contributions")



# name -> (renderer, variants). "light"/"dark" variants become <picture> sources in the README.
LAYOUTS = {
    "garden": (garden, ("light", "dark")),
    "bento": (bento, ("light", "dark")),
    "receipt": (receipt, ("light",)),
    "seigaiha": (seigaiha, ("light", "dark")),
    "constellation": (constellation, ("dark",)),
    "sansui": (sansui, ("light", "dark")),
}


def render(name: str, d: dict) -> dict[str, str]:
    fn, variants = LAYOUTS[name]
    return {f"{name}-{v}.svg": fn(d, v) for v in variants}
