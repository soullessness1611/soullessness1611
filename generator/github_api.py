"""Thin GitHub GraphQL client (stdlib only) and the raw-data fetchers."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

GRAPHQL_URL = "https://api.github.com/graphql"
USER_AGENT = "cyberpunk-github-stats"


class GitHubError(RuntimeError):
    pass


def graphql(token: str, query: str, variables: dict | None = None, retries: int = 3) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.load(resp)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (502, 503, 504) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise GitHubError(f"GitHub API HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from e
        except urllib.error.URLError as e:
            last = e
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise GitHubError(f"GitHub API unreachable: {e}") from e
        if body.get("errors"):
            raise GitHubError("GraphQL errors: " + "; ".join(err.get("message", "?") for err in body["errors"]))
        return body["data"]
    raise GitHubError(f"GitHub API failed: {last}")


PROFILE_QUERY = """
query($login: String!, $cursor: String, $privacy: RepositoryPrivacy) {
  user(login: $login) {
    id login name createdAt
    followers { totalCount }
    following { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, PULL_REQUEST_REVIEW]) { totalCount }
    contributionsCollection {
      contributionYears
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel weekday } }
      }
    }
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false,
                 privacy: $privacy, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name nameWithOwner description url isPrivate isArchived
        stargazerCount forkCount pushedAt createdAt
        primaryLanguage { name color }
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_profile(token: str, login: str, include_private: bool = False) -> dict:
    """User info + every owned non-fork repo (paginated)."""
    repos: list[dict] = []
    cursor = None
    user = None
    privacy = None if include_private else "PUBLIC"
    for _ in range(20):  # hard cap: 2,000 repos
        data = graphql(token, PROFILE_QUERY, {"login": login, "cursor": cursor, "privacy": privacy})
        user = data["user"]
        if user is None:
            raise GitHubError(f"User '{login}' not found")
        page = user["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    assert user is not None
    user["repositories"]["nodes"] = repos
    return user


def fetch_years(token: str, login: str, years: list[int]) -> list[dict]:
    """One contributionsCollection per calendar year (needed for all-time streaks/totals)."""
    now = datetime.now(timezone.utc)
    out = []
    for year in sorted(years):
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = min(datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc), now)
        if start > now:
            continue
        data = graphql(token, YEAR_QUERY, {"login": login, "from": start.isoformat(), "to": end.isoformat()})
        coll = data["user"]["contributionsCollection"]
        coll["year"] = year
        out.append(coll)
    return out


def fetch_commit_times(token: str, owner: str, user_id: str, repo_names: list[str], days: int = 365) -> list[str]:
    """Authored timestamps (ISO, UTC) of the user's commits on default branches of the given repos."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    stamps: list[str] = []
    for i in range(0, len(repo_names), 10):
        chunk = repo_names[i : i + 10]
        parts = []
        for j, name in enumerate(chunk):
            parts.append(
                f'r{j}: repository(owner: {json.dumps(owner)}, name: {json.dumps(name)}) {{'
                "  defaultBranchRef { target { ... on Commit {"
                "    history(first: 100, author: {id: $id}, since: $since) { nodes { authoredDate } }"
                "  } } } }"
            )
        query = "query($id: ID!, $since: GitTimestamp!) {" + "\n".join(parts) + "}"
        try:
            data = graphql(token, query, {"id": user_id, "since": since})
        except GitHubError:
            continue  # one broken/empty repo should not kill the whole card
        for repo in data.values():
            ref = (repo or {}).get("defaultBranchRef") or {}
            hist = (ref.get("target") or {}).get("history") or {}
            stamps.extend(n["authoredDate"] for n in hist.get("nodes", []))
    return stamps
