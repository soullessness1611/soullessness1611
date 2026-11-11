import json
import unittest
import xml.dom.minidom
from datetime import date
from pathlib import Path

from generator import cards, stats
from generator.__main__ import build
from generator.demo import demo_raw, demo_wakatime

ROOT = Path(__file__).resolve().parent.parent
TODAY = date(2026, 11, 11)
CARDS = {
    "header.svg", "stats.svg", "streak.svg", "languages.svg", "repos.svg",
    "contributions.svg", "activity.svg", "skills.svg", "projects.svg", "wakatime.svg",
}


def parse(svg: str):
    return xml.dom.minidom.parseString(svg.encode("utf-8"))


class BuildDemo(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

    def test_all_cards_are_valid_svg(self):
        out = build(self.cfg, demo_raw(self.cfg["username"], TODAY), demo_wakatime(), TODAY)
        self.assertEqual(set(out), CARDS)
        for name, svg in out.items():
            with self.subTest(card=name):
                root = parse(svg).documentElement
                assert root is not None
                self.assertEqual(root.tagName, "svg")
                self.assertTrue(root.getAttribute("width") and root.getAttribute("height"))

    def test_wakatime_offline_card(self):
        out = build(self.cfg, demo_raw(self.cfg["username"], TODAY), None, TODAY)
        self.assertIn("LINK OFFLINE", out["wakatime.svg"])
        parse(out["wakatime.svg"])


EMPTY_CAL = {"totalContributions": 0, "weeks": []}


class EmptyAccount(unittest.TestCase):
    """A brand-new account with nothing in it must still render."""

    def test_cards_render_with_no_data(self):
        st = stats.streaks({}, TODAY)
        svgs = [
            cards.stats_card({"stars": 0, "year": 2026, "commits_year": 0, "commits_all": 0, "prs": 0,
                              "issues": 0, "contributed_to": 0, "followers": 0, "contributions_all": 0}),
            cards.streak_card(st),
            cards.languages_card([]),
            cards.repos_card(stats.repo_summary([])),
            cards.contribution_card(EMPTY_CAL),
            cards.activity_card(stats.commit_activity([], {}, "UTC", TODAY)),
            cards.skills_card({}),
            cards.projects_card([], TODAY),
            cards.header_card("x", "x", "", None),
        ]
        for i, svg in enumerate(svgs):
            with self.subTest(i=i):
                parse(svg)


class Escaping(unittest.TestCase):
    def test_special_characters_in_repo_data_stay_valid_xml(self):
        repo = {
            "name": "a&b<c>", "url": "https://github.com/x/a?b=1&c=2", "description": 'He said "hi" & <left>',
            "pushedAt": "2026-11-01T00:00:00Z", "stargazerCount": 1, "forkCount": 0,
            "primaryLanguage": {"name": "C++", "color": "#f34b7d"}, "isArchived": False,
        }
        parse(cards.projects_card([repo], TODAY))
        parse(cards.repos_card(stats.repo_summary([repo])))
        parse(cards.header_card("<Zen & Co>", "z", 'tag "line" & more', TODAY))
        parse(cards.skills_card({"A&B": ["C#", "<html>"]}))


if __name__ == "__main__":
    unittest.main()
