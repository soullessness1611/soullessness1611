"""Entry point: `python -m generator [--demo] [--out assets]`.

Env:
  GH_TOKEN / GITHUB_TOKEN  GitHub token (required unless --demo)
  WAKATIME_TOKEN           optional OAuth token (scope read_stats); WakaTime card shows "offline" without it
  WAKATIME_API_KEY         legacy fallback — WakaTime now rejects API keys for stats (HTTP 403)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import cards, stats
from .github_api import GitHubError, fetch_commit_times, fetch_profile, fetch_years
from .wakatime import fetch_wakatime

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def collect(cfg: dict, token: str, today: date) -> dict:
    login = cfg["username"]
    print(f"[github] fetching profile for {login} …")
    user = fetch_profile(token, login, cfg.get("include_private_repos", False))
    excluded = {r.lower() for r in cfg.get("exclude_repos", [])}
    repos = [r for r in user["repositories"]["nodes"] if r["name"].lower() not in excluded]
    if not cfg.get("include_private_repos", False):
        repos = [r for r in repos if not r["isPrivate"]]

    coll = user["contributionsCollection"]
    print(f"[github] fetching {len(coll['contributionYears'])} contribution years …")
    years = fetch_years(token, login, coll["contributionYears"])

    names = [r["name"] for r in repos[: cfg.get("commit_activity_repo_limit", 30)]]
    print(f"[github] sampling commit times from {len(names)} repos …")
    commit_times = fetch_commit_times(token, login, user["id"], names)

    return {"user": user, "repos": repos, "years": years, "commit_times": commit_times}


def build(cfg: dict, raw: dict, wakatime: dict | None, today: date) -> dict[str, str]:
    user, repos, years = raw["user"], raw["repos"], raw["years"]
    coll = user["contributionsCollection"]
    rolling = coll["contributionCalendar"]
    days = stats.merge_days(*(y["contributionCalendar"] for y in years), rolling)
    streak = stats.streaks(days, today)
    rs = stats.repo_summary(repos)
    this_year = next((y for y in years if y["year"] == today.year), None)

    github = {
        "stars": rs["stars"],
        "year": today.year,
        "commits_year": (this_year or {}).get("totalCommitContributions", 0)
        + (this_year or {}).get("restrictedContributionsCount", 0),
        "commits_all": sum(y["totalCommitContributions"] + y["restrictedContributionsCount"] for y in years),
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "contributed_to": user["repositoriesContributedTo"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "contributions_all": streak["total"],
    }
    joined = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00")).date()
    activity = stats.commit_activity(raw["commit_times"], days, cfg.get("timezone", "UTC"), today)

    return {
        "header.svg": cards.header_card(
            cfg.get("display_name") or user.get("name") or user["login"], user["login"], cfg.get("tagline", ""), joined
        ),
        "stats.svg": cards.stats_card(github),
        "streak.svg": cards.streak_card(streak),
        "languages.svg": cards.languages_card(
            stats.top_languages(repos, cfg.get("exclude_languages", []), cfg.get("top_languages_count", 8))
        ),
        "repos.svg": cards.repos_card(rs),
        "contributions.svg": cards.contribution_card(rolling),
        "activity.svg": cards.activity_card(activity),
        "skills.svg": cards.skills_card(cfg.get("skills", {})),
        "projects.svg": cards.projects_card(
            stats.latest_projects(repos, cfg.get("latest_projects_count", 6)), today
        ),
        "wakatime.svg": cards.wakatime_card(wakatime),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate CyberPunk GitHub profile SVG cards")
    ap.add_argument("--config", default=str(ROOT / "config.json"))
    ap.add_argument("--out", default=str(ROOT / "assets"))
    ap.add_argument("--demo", action="store_true", help="render with built-in sample data (no token needed)")
    args = ap.parse_args(argv)

    cfg = load_config(Path(args.config))
    today = datetime.now(ZoneInfo(cfg.get("timezone", "UTC"))).date()

    if args.demo:
        from .demo import demo_raw, demo_wakatime

        raw, wk = demo_raw(cfg["username"], today), demo_wakatime()
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            print("error: set GH_TOKEN or GITHUB_TOKEN (or use --demo)", file=sys.stderr)
            return 2
        try:
            raw = collect(cfg, token, today)
        except GitHubError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        wk = fetch_wakatime(os.environ.get("WAKATIME_API_KEY"), os.environ.get("WAKATIME_TOKEN"))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, svg in build(cfg, raw, wk, today).items():
        (out / name).write_text(svg, encoding="utf-8")
        print(f"[svg] wrote {out / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
