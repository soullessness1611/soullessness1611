"""Deterministic sample data so cards can be previewed/tested without a token."""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone

_LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
_LANGS = [("Python", "#3572A5"), ("TypeScript", "#3178c6"), ("JavaScript", "#f1e05a"), ("Lua", "#000080"),
          ("Jupyter Notebook", "#DA5B0B"), ("CSS", "#563d7c"), ("Shell", "#89e051")]


def _calendar(start: date, end: date, rng: random.Random) -> dict:
    weeks, week = [], []
    d = start - timedelta(days=(start.weekday() + 1) % 7)  # GitHub weeks start on Sunday
    total = 0
    while d <= end:
        c = 0 if rng.random() < 0.35 else rng.choice([1, 1, 2, 3, 4, 6, 9, 14])
        if d < start:
            c = 0
        total += c
        lvl = 0 if c == 0 else min(4, 1 + c // 4)
        week.append({"date": d.isoformat(), "contributionCount": c, "contributionLevel": _LEVELS[lvl],
                     "weekday": (d.weekday() + 1) % 7})
        if len(week) == 7:
            weeks.append({"contributionDays": week})
            week = []
        d += timedelta(days=1)
    if week:
        weeks.append({"contributionDays": week})
    return {"totalContributions": total, "weeks": weeks}


def demo_raw(login: str, today: date) -> dict:
    rng = random.Random(1611)
    rolling = _calendar(today - timedelta(days=364), today, rng)
    years = []
    for y in range(today.year - 2, today.year + 1):
        cal = _calendar(date(y, 1, 1), min(date(y, 12, 31), today), random.Random(y))
        years.append({"year": y, "totalCommitContributions": cal["totalContributions"] * 3 // 4,
                      "restrictedContributionsCount": 0, "totalPullRequestContributions": 12,
                      "totalIssueContributions": 5, "totalPullRequestReviewContributions": 3,
                      "contributionCalendar": cal})
    repos = []
    for i, name in enumerate(["neon-grid-engine", "ZeN-AgentsOS", "StockCryptoDashboard", "nvim-public",
                              "nextjs14-TS-CRUD", "PlotlyDash-Tutorial", "ghost-protocol-cli", "data-shard"]):
        lang, color = _LANGS[i % len(_LANGS)]
        pushed = datetime.now(timezone.utc) - timedelta(days=i * 9 + 1)
        repos.append({
            "name": name, "nameWithOwner": f"{login}/{name}", "url": f"https://github.com/{login}/{name}",
            "description": f"Sample project #{i + 1} — chrome, code and neon.", "isPrivate": False,
            "isArchived": False, "stargazerCount": max(0, 42 - i * 6), "forkCount": max(0, 9 - i),
            "pushedAt": pushed.isoformat().replace("+00:00", "Z"), "createdAt": "2024-01-01T00:00:00Z",
            "primaryLanguage": {"name": lang, "color": color},
            "languages": {"edges": [{"size": 50000 // (i + 1), "node": {"name": lang, "color": color}},
                                    {"size": 8000, "node": {"name": "Shell", "color": "#89e051"}}]},
        })
    commit_times = []
    for _ in range(420):
        hour = int(rng.triangular(0, 24, 15)) % 24
        dt = datetime.now(timezone.utc) - timedelta(days=rng.randint(0, 364), hours=rng.randint(0, 23))
        commit_times.append(dt.replace(hour=hour).isoformat().replace("+00:00", "Z"))
    user = {
        "id": "DEMO", "login": login, "name": "Demo", "createdAt": "2023-04-22T19:29:04Z",
        "followers": {"totalCount": 128}, "following": {"totalCount": 64}, "pullRequests": {"totalCount": 87},
        "issues": {"totalCount": 31}, "repositoriesContributedTo": {"totalCount": 14},
        "contributionsCollection": {"contributionYears": [y["year"] for y in years],
                                    "totalCommitContributions": 0, "restrictedContributionsCount": 0,
                                    "contributionCalendar": rolling},
        "repositories": {"totalCount": len(repos), "nodes": repos},
    }
    return {"user": user, "repos": repos, "years": years, "commit_times": commit_times}


def demo_wakatime(today: date | None = None) -> dict:
    """Sample WakaTime data in the same shape fetch_wakatime returns."""
    from .wakatime import parse_stats

    def item(name: str, pct: float, secs: int) -> dict:
        h, m = divmod(secs // 60, 60)
        return {"name": name, "percent": pct, "total_seconds": secs, "text": f"{h} hrs {m} mins" if h else f"{m} mins"}

    wk = parse_stats({"data": {
        "human_readable_range": "Last 7 Days", "human_readable_total_including_other_language": "31 hrs 12 mins",
        "total_seconds_including_other_language": 112320, "human_readable_daily_average": "4 hrs 27 mins",
        "best_day": {"date": ((today or date.today()) - timedelta(days=2)).isoformat(), "text": "7 hrs 3 mins"},
        "languages": [item(n, p, s) for n, p, s in [("Python", 41.2, 46260), ("TypeScript", 27.5, 30840), ("Lua", 9.8, 10980),
                                                     ("Markdown", 8.1, 9060), ("YAML", 6.3, 7080), ("Bash", 4.0, 4500)]],
        "projects": [item(n, p, s) for n, p, s in [("neon-grid-engine", 38.0, 42680), ("ghost-protocol-cli", 24.0, 26960),
                                                    ("dotfiles", 14.0, 15720), ("data-shard", 9.0, 10110)]],
        "editors": [item("Neovim", 72.0, 80870), item("VS Code", 28.0, 31450)],
        "operating_systems": [item("Linux", 100.0, 112320)], "categories": [item("Coding", 88.0, 98840)],
        "machines": [{"name": "demo-box"}],
        "ai_additions": 5200, "human_additions": 1300, "ai_input_tokens": 41_000_000, "ai_output_tokens": 600_000,
        "ai_model_total_cost": 23.4, "ai_sessions": 18, "ai_prompt_events_total": 96, "ai_model_line_changes": {"Sonnet": 5200},
    }})
    end = today or date.today()
    hours = [3.2, 5.1, 4.4, 0.0, 6.8, 7.1, 4.6]
    wk["days"] = [{"date": (end - timedelta(days=6 - i)).isoformat(), "seconds": h * 3600, "text": f"{h:.1f} hrs",
                   "ai_additions": int(h * 160), "human_additions": int(h * 40)} for i, h in enumerate(hours)]
    return wk
