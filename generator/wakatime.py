"""WakaTime stats (last 7 days).

WakaTime only lets plugins use API keys; reading stats needs an OAuth access
token (scope read_stats) sent as a Bearer token. The API-key path is kept for
backwards compatibility but WakaTime now answers it with HTTP 403.

Returns None when no credential is configured, {"error": "..."} when the API
call fails, otherwise the stats dict the card renders.
"""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request

STATS_URL = "https://wakatime.com/api/v1/users/current/stats/last_7_days"


def fetch_wakatime(api_key: str | None, oauth_token: str | None = None) -> dict | None:
    api_key = (api_key or "").strip()
    oauth_token = (oauth_token or "").strip()
    if oauth_token:
        auth = f"Bearer {oauth_token}"
    elif api_key:
        auth = "Basic " + base64.b64encode(api_key.encode()).decode()
    else:
        return None
    req = urllib.request.Request(
        STATS_URL,
        headers={"Authorization": auth, "User-Agent": "cyberpunk-github-stats"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp).get("data") or {}
    except urllib.error.HTTPError as e:
        reason = _error_reason(e.read())
        print(f"[wakatime] fetch failed: HTTP {e.code}: {reason}")
        return {"error": f"HTTP {e.code}: {reason}"}
    except (urllib.error.URLError, ValueError) as e:
        print(f"[wakatime] fetch failed: {e}")
        return {"error": str(e)[:120]}
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
