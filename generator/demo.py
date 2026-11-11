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


def demo_wakatime() -> dict:
    return {
        "range": "Last 7 days", "total": "31 hrs 12 mins", "daily_average": "4 hrs 27 mins",
        "best_day": "7 hrs 3 mins",
        "languages": [{"name": n, "percent": p, "text": t} for n, p, t in [
            ("Python", 41.2, "12 hrs 51 mins"), ("TypeScript", 27.5, "8 hrs 34 mins"), ("Lua", 9.8, "3 hrs 3 mins"),
            ("Markdown", 8.1, "2 hrs 31 mins"), ("YAML", 6.3, "1 hr 58 mins"), ("Bash", 4.0, "1 hr 15 mins")]],
        "editors": ["Neovim", "VS Code"], "operating_systems": ["Linux", "WSL"], "up_to_date": True,
    }
