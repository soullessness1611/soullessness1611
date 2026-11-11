"""Turn raw API payloads into the numbers the cards display. Pure functions — no I/O."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def merge_days(*calendars: dict) -> dict[date, int]:
    """Merge contributionCalendar payloads into {date: count} (later payloads win on overlap)."""
    days: dict[date, int] = {}
    for cal in calendars:
        for week in cal.get("weeks", []):
            for d in week["contributionDays"]:
                days[date.fromisoformat(d["date"])] = d["contributionCount"]
    return days


def streaks(days: dict[date, int], today: date) -> dict:
    """Current and longest streak. A streak is still 'current' if today has no contribution yet."""
    active = sorted(d for d, c in days.items() if c > 0 and d <= today)
    longest: dict = {"length": 0, "start": None, "end": None}
    prev: date | None = None
    run_start: date = today
    for d in active:
        if prev is None or d - prev != timedelta(days=1):
            run_start = d
        length = (d - run_start).days + 1
        if length > longest["length"]:
            longest = {"length": length, "start": run_start, "end": d}
        prev = d

    current = {"length": 0, "start": None, "end": None}
    cursor = today if days.get(today, 0) > 0 else today - timedelta(days=1)
    if days.get(cursor, 0) > 0:
        end = cursor
        while days.get(cursor, 0) > 0:
            cursor -= timedelta(days=1)
        start = cursor + timedelta(days=1)
        current = {"length": (end - start).days + 1, "start": start, "end": end}

    total = sum(c for d, c in days.items() if d <= today)
    first = min(days) if days else today
    return {"current": current, "longest": longest, "total": total, "first_day": first}


def top_languages(repos: list[dict], exclude: list[str], limit: int) -> list[dict]:
    sizes: Counter[str] = Counter()
    colors: dict[str, str] = {}
    excluded = {e.lower() for e in exclude}
    for repo in repos:
        for edge in (repo.get("languages") or {}).get("edges", []):
            name = edge["node"]["name"]
            if name.lower() in excluded:
                continue
            sizes[name] += edge["size"]
            colors[name] = edge["node"].get("color") or "#888888"
    total = sum(sizes.values()) or 1
    top = sizes.most_common(limit)
    return [{"name": n, "size": s, "percent": s * 100 / total, "color": colors[n]} for n, s in top]


def repo_summary(repos: list[dict]) -> dict:
    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)
    ranked = sorted(repos, key=lambda r: (r["stargazerCount"], r["forkCount"], r["pushedAt"] or ""), reverse=True)
    return {
        "count": len(repos),
        "stars": stars,
        "forks": forks,
        "archived": sum(1 for r in repos if r.get("isArchived")),
        "top": ranked[:5],
    }


def latest_projects(repos: list[dict], limit: int) -> list[dict]:
    live = [r for r in repos if not r.get("isArchived")]
    return sorted(live, key=lambda r: r["pushedAt"] or "", reverse=True)[:limit]


def commit_activity(commit_times: list[str], days: dict[date, int], tz: str, today: date) -> dict:
    """Hour-of-day and weekday distributions + last-12-months totals."""
    zone = ZoneInfo(tz)
    hours = [0] * 24
    weekday = [0] * 7
    for stamp in commit_times:
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(zone)
        hours[dt.hour] += 1
        weekday[dt.weekday()] += 1
    source = "commits"
    if not commit_times:  # fall back to calendar data for weekday split
        source = "calendar"
        for d, c in days.items():
            if today - d <= timedelta(days=365):
                weekday[d.weekday()] += c

    months: list[dict] = []
    y, m = today.year, today.month
    for _ in range(12):
        total = sum(c for d, c in days.items() if d.year == y and d.month == m)
        months.append({"label": date(y, m, 1).strftime("%b"), "year": y, "count": total})
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    months.reverse()

    peak_hour = max(range(24), key=lambda h: hours[h]) if any(hours) else None
    peak_day = max(range(7), key=lambda d: weekday[d]) if any(weekday) else None
    return {
        "hours": hours,
        "weekday": weekday,
        "months": months,
        "commits_sampled": len(commit_times),
        "peak_hour": peak_hour,
        "peak_day": WEEKDAYS[peak_day] if peak_day is not None else None,
        "persona": persona(hours) if any(hours) else None,
        "source": source,
    }


def persona(hours: list[int]) -> str:
    buckets = {
        "MORNING RUNNER": sum(hours[5:12]),
        "DAYLIGHT HACKER": sum(hours[12:18]),
        "EVENING CODER": sum(hours[18:23]),
        "NIGHT OWL": sum(hours[23:]) + sum(hours[:5]),
    }
    return max(buckets, key=lambda k: buckets[k])
