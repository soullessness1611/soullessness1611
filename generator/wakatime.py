"""WakaTime stats (last 7 days) and per-day summaries.

WakaTime only lets plugins use API keys; reading stats needs an OAuth access
token sent as a Bearer token:
  scope read_stats      -> totals, languages, projects, editors, OS, machines, AI coding
  scope read_summaries  -> per-day totals (the Rhythm card); optional
The API-key path is kept for backwards compatibility, but WakaTime answers it with HTTP 403.

fetch_wakatime returns None when no credential is configured, {"error": "..."} when the
stats call fails, otherwise the dict the WakaTime cards render (see parse_stats).
"""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

API = "https://wakatime.com/api/v1/users/current"
STATS_URL = f"{API}/stats/last_7_days"
SUMMARIES_URL = f"{API}/summaries"


class WakaError(RuntimeError):
    pass


def fetch_wakatime(api_key: str | None, oauth_token: str | None = None, today: date | None = None) -> dict | None:
    api_key = (api_key or "").strip()
    oauth_token = (oauth_token or "").strip()
    if oauth_token:
        auth = f"Bearer {oauth_token}"
    elif api_key:
        auth = "Basic " + base64.b64encode(api_key.encode()).decode()
    else:
        return None
    try:
        stats = parse_stats(_get(STATS_URL, auth))
    except WakaError as e:
        print(f"[wakatime] fetch failed: {e}")
        return {"error": str(e)}
    end = today or date.today()
    query = urllib.parse.urlencode({"start": (end - timedelta(days=6)).isoformat(), "end": end.isoformat()})
    try:
        stats["days"] = parse_summaries(_get(f"{SUMMARIES_URL}?{query}", auth))
    except WakaError as e:  # usually a token without read_summaries
        print(f"[wakatime] summaries unavailable: {e}")
        stats["days"] = None
        stats["days_error"] = str(e)
    return stats


def _get(url: str, auth: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": auth, "User-Agent": "cyberpunk-github-stats"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise WakaError(f"HTTP {e.code}: {_error_reason(e.read())}") from e
    except (urllib.error.URLError, ValueError) as e:
        raise WakaError(str(e)[:120]) from e


def _num(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _hm(seconds: float) -> str:
    h, m = divmod(int(seconds) // 60, 60)
    return f"{h} hrs {m} mins" if h else f"{m} mins"


def _items(rows, limit: int = 10) -> list[dict]:
    return [
        {"name": r.get("name") or "?", "percent": _num(r.get("percent")),
         "text": r.get("text") or _hm(_num(r.get("total_seconds"))), "seconds": _num(r.get("total_seconds"))}
        for r in (rows or [])[:limit]
        if isinstance(r, dict)
    ]


def _models(data: dict) -> list[dict]:
    """AI models with line counts, from whichever breakdown field the API filled in."""
    raw = data.get("ai_model_line_changes") or data.get("ai_model_breakdown") or {}
    out = []
    if isinstance(raw, dict):
        for name, v in raw.items():
            lines = _num(v.get("ai_additions") or v.get("line_changes") or v.get("total")) if isinstance(v, dict) else _num(v)
            out.append({"name": str(name), "lines": lines})
    elif isinstance(raw, list):
        for v in raw:
            if isinstance(v, dict):
                out.append({"name": str(v.get("name") or v.get("model") or "?"),
                            "lines": _num(v.get("ai_additions") or v.get("line_changes") or v.get("total") or v.get("lines"))})
    out.sort(key=lambda m: m["lines"], reverse=True)
    total = sum(m["lines"] for m in out) or 1
    for m in out:
        m["percent"] = 100 * m["lines"] / total
    return out


def parse_stats(body: dict) -> dict:
    data = body.get("data") or {}
    ai_add, hu_add = _num(data.get("ai_additions")), _num(data.get("human_additions"))
    ai = {
        "ai_additions": ai_add, "ai_deletions": _num(data.get("ai_deletions")),
        "human_additions": hu_add, "human_deletions": _num(data.get("human_deletions")),
        "input_tokens": _num(data.get("ai_input_tokens")), "output_tokens": _num(data.get("ai_output_tokens")),
        "cost": _num(data.get("ai_model_total_cost")), "sessions": _num(data.get("ai_sessions")),
        "prompts": _num(data.get("ai_prompt_events_total")), "models": _models(data),
        "ai_percent": 100 * ai_add / (ai_add + hu_add) if (ai_add + hu_add) else 0.0,
    }
    has_ai = any(ai[k] for k in ("ai_additions", "input_tokens", "cost", "sessions"))
    best = data.get("best_day") or {}
    return {
        "range": (data.get("human_readable_range") or "last 7 days").lower(),
        "total": data.get("human_readable_total_including_other_language") or data.get("human_readable_total") or "0 secs",
        "total_seconds": _num(data.get("total_seconds_including_other_language") or data.get("total_seconds")),
        "daily_average": data.get("human_readable_daily_average_including_other_language")
        or data.get("human_readable_daily_average") or "0 secs",
        "best_day": {"date": best.get("date"), "text": best.get("text")} if best.get("date") else None,
        "languages": _items(data.get("languages")),
        "projects": _items(data.get("projects"), 8),
        "editors": _items(data.get("editors"), 4),
        "operating_systems": _items(data.get("operating_systems"), 3),
        "categories": _items(data.get("categories"), 4),
        "machines": len(data.get("machines") or []),
        "ai": ai if has_ai else None,
        "up_to_date": data.get("is_up_to_date", True),
    }


def parse_summaries(body: dict) -> list[dict]:
    days = []
    for row in body.get("data") or []:
        gt = row.get("grand_total") or {}
        day = (row.get("range") or {}).get("date")
        if not day:
            continue
        days.append({
            "date": day,
            "seconds": _num(gt.get("total_seconds")),
            "text": gt.get("text") or "",
            "ai_additions": _num(gt.get("ai_additions")),
            "human_additions": _num(gt.get("human_additions")),
        })
    return sorted(days, key=lambda d: d["date"])


def _error_reason(body: bytes) -> str:
    """WakaTime error bodies look like {"error": "..."} or {"errors": ["..."]}."""
    try:
        data = json.loads(body)
    except ValueError:
        return body.decode(errors="replace").strip()[:120] or "no details"
    if isinstance(data, dict):
        msg = data.get("error") or data.get("errors") or data.get("message")
        if isinstance(msg, list):
            msg = "; ".join(map(str, msg))
        if msg:
            return str(msg)[:120]
    return "no details"
