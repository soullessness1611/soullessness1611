"""WakaTime stats (last 7 days). Returns None when no API key is configured."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request

STATS_URL = "https://wakatime.com/api/v1/users/current/stats/last_7_days"


def fetch_wakatime(api_key: str | None) -> dict | None:
    if not api_key:
        return None
    auth = base64.b64encode(api_key.encode()).decode()
    req = urllib.request.Request(
        STATS_URL,
        headers={"Authorization": f"Basic {auth}", "User-Agent": "cyberpunk-github-stats"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp).get("data") or {}
    except (urllib.error.URLError, ValueError) as e:
        print(f"[wakatime] fetch failed: {e}")
        return None
    return {
        "range": data.get("human_readable_range") or "Last 7 days",
        "total": data.get("human_readable_total_including_other_language")
        or data.get("human_readable_total")
        or "0 secs",
        "daily_average": data.get("human_readable_daily_average") or "0 secs",
        "best_day": (data.get("best_day") or {}).get("text"),
        "languages": [
            {"name": l["name"], "percent": l.get("percent", 0), "text": l.get("text", "")}
            for l in (data.get("languages") or [])
        ],
        "editors": [e["name"] for e in (data.get("editors") or [])][:3],
        "operating_systems": [o["name"] for o in (data.get("operating_systems") or [])][:3],
        "up_to_date": data.get("is_up_to_date", True),
    }
