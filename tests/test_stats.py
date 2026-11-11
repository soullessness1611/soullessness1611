import unittest
from datetime import date, timedelta

from generator import stats


def cal(entries: dict[str, int]) -> dict:
    return {"weeks": [{"contributionDays": [{"date": d, "contributionCount": c} for d, c in entries.items()]}]}


def run(start: date, n: int, count: int = 1) -> dict[date, int]:
    return {start + timedelta(days=i): count for i in range(n)}


TODAY = date(2026, 11, 11)


class MergeDays(unittest.TestCase):
    def test_later_calendar_wins_on_overlap(self):
        days = stats.merge_days(cal({"2026-01-01": 1, "2026-01-02": 2}), cal({"2026-01-02": 5}))
        self.assertEqual(days, {date(2026, 1, 1): 1, date(2026, 1, 2): 5})


class Streaks(unittest.TestCase):
    def test_current_streak_includes_today(self):
        days = run(TODAY - timedelta(days=4), 5)
        st = stats.streaks(days, TODAY)
        self.assertEqual(st["current"]["length"], 5)
        self.assertEqual(st["current"]["end"], TODAY)

    def test_streak_still_current_when_today_is_empty(self):
        days = run(TODAY - timedelta(days=3), 3)  # ends yesterday
        days[TODAY] = 0
        st = stats.streaks(days, TODAY)
        self.assertEqual(st["current"]["length"], 3)
        self.assertEqual(st["current"]["end"], TODAY - timedelta(days=1))

    def test_gap_of_two_days_breaks_current_streak(self):
        days = run(TODAY - timedelta(days=5), 3)  # ends 3 days ago
        st = stats.streaks(days, TODAY)
        self.assertEqual(st["current"]["length"], 0)
        self.assertEqual(st["longest"]["length"], 3)

    def test_longest_streak_picks_longest_run(self):
        days = {**run(date(2026, 1, 1), 10), **run(date(2026, 3, 1), 4)}
        st = stats.streaks(days, TODAY)
        self.assertEqual(st["longest"], {"length": 10, "start": date(2026, 1, 1), "end": date(2026, 1, 10)})
        self.assertEqual(st["total"], 14)

    def test_future_days_are_ignored(self):
        days = {TODAY + timedelta(days=1): 9, TODAY: 1}
        st = stats.streaks(days, TODAY)
        self.assertEqual(st["total"], 1)
        self.assertEqual(st["longest"]["length"], 1)

    def test_no_contributions(self):
        st = stats.streaks({}, TODAY)
        self.assertEqual(st["current"]["length"], 0)
        self.assertEqual(st["longest"]["length"], 0)
        self.assertEqual(st["total"], 0)


def lang(name: str, size: int, color: str | None = "#111111") -> dict:
    return {"size": size, "node": {"name": name, "color": color}}


class Languages(unittest.TestCase):
    def test_sums_sizes_across_repos_and_excludes(self):
        repos = [
            {"languages": {"edges": [lang("Python", 300), lang("HTML", 100)]}},
            {"languages": {"edges": [lang("Python", 100), lang("Lua", 100, None)]}},
            {"languages": None},
        ]
        out = stats.top_languages(repos, ["html"], 8)
        self.assertEqual([l["name"] for l in out], ["Python", "Lua"])
        self.assertAlmostEqual(out[0]["percent"], 80.0)
        self.assertEqual(out[1]["color"], "#888888")

    def test_limit(self):
        repos = [{"languages": {"edges": [lang(f"L{i}", 10 + i) for i in range(5)]}}]
        self.assertEqual(len(stats.top_languages(repos, [], 3)), 3)

    def test_empty(self):
        self.assertEqual(stats.top_languages([], [], 8), [])


def repo(name: str, stars: int = 0, pushed: str | None = "2026-01-01T00:00:00Z", archived: bool = False) -> dict:
    return {"name": name, "stargazerCount": stars, "forkCount": 0, "pushedAt": pushed, "isArchived": archived}


class Repos(unittest.TestCase):
    def test_summary_counts_and_ranks_by_stars(self):
        rs = stats.repo_summary([repo("a", 1), repo("b", 5, archived=True), repo("c", 3)])
        self.assertEqual((rs["count"], rs["stars"], rs["archived"]), (3, 9, 1))
        self.assertEqual([r["name"] for r in rs["top"]], ["b", "c", "a"])

    def test_latest_projects_skips_archived_and_handles_null_push(self):
        repos = [
            repo("old", pushed="2025-01-01T00:00:00Z"),
            repo("new", pushed="2026-10-01T00:00:00Z"),
            repo("gone", pushed="2026-11-01T00:00:00Z", archived=True),
            repo("never", pushed=None),
        ]
        self.assertEqual([r["name"] for r in stats.latest_projects(repos, 2)], ["new", "old"])


class Activity(unittest.TestCase):
    def test_commit_hours_use_configured_timezone(self):
        # 20:30 UTC on a Monday is 03:30 Tuesday in Bangkok (UTC+7)
        a = stats.commit_activity(["2026-11-09T20:30:00Z"], {}, "Asia/Bangkok", TODAY)
        self.assertEqual(a["hours"][3], 1)
        self.assertEqual(a["peak_day"], "Tue")
        self.assertEqual(a["persona"], "NIGHT OWL")
        self.assertEqual(a["source"], "commits")

    def test_falls_back_to_calendar_without_commit_times(self):
        days = {date(2026, 11, 9): 4, date(2024, 1, 1): 100}  # Monday; second is > 1 year old
        a = stats.commit_activity([], days, "UTC", TODAY)
        self.assertEqual(a["source"], "calendar")
        self.assertEqual(a["weekday"][0], 4)
        self.assertEqual(sum(a["weekday"]), 4)
        self.assertIsNone(a["persona"])

    def test_twelve_months_ending_this_month(self):
        days = {date(2026, 11, 1): 2, date(2026, 11, 10): 3, date(2025, 12, 5): 7, date(2025, 11, 30): 50}
        a = stats.commit_activity([], days, "UTC", TODAY)
        self.assertEqual(len(a["months"]), 12)
        self.assertEqual((a["months"][0]["label"], a["months"][0]["year"], a["months"][0]["count"]), ("Dec", 2025, 7))
        self.assertEqual((a["months"][-1]["label"], a["months"][-1]["count"]), ("Nov", 5))


class Persona(unittest.TestCase):
    def test_buckets(self):
        hours = [0] * 24
        hours[9] = 5
        self.assertEqual(stats.persona(hours), "MORNING RUNNER")
        hours[23] = 3
        hours[2] = 3
        self.assertEqual(stats.persona(hours), "NIGHT OWL")


if __name__ == "__main__":
    unittest.main()
