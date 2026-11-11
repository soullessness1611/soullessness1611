import json
import unittest
import xml.dom.minidom
from datetime import date
from pathlib import Path

from generator import cards, layouts, readme, stats, theme
from generator.__main__ import ALL_STYLES, build
from generator.demo import demo_raw, demo_wakatime

ROOT = Path(__file__).resolve().parent.parent
TODAY = date(2026, 11, 11)
CARDS = {
    "header.svg", "stats.svg", "streak.svg", "languages.svg", "repos.svg",
    "contributions.svg", "activity.svg", "skills.svg", "projects.svg",
    "waka-overview.svg", "waka-ai.svg", "waka-projects.svg", "waka-tools.svg", "waka-rhythm.svg",
}


def parse(svg: str):
    return xml.dom.minidom.parseString(svg.encode("utf-8"))


class BuildDemo(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

    def test_every_style_renders_valid_svg(self):
        raw, wk = demo_raw(self.cfg["username"], TODAY), demo_wakatime(TODAY)
        for style in ALL_STYLES:
            out = build(self.cfg, raw, wk, TODAY, style)
            if style in theme.STYLES:
                self.assertEqual(set(out), CARDS, style)
            else:
                self.assertTrue(out and all(n.startswith(style + "-") for n in out), style)
            for name, svg in out.items():
                with self.subTest(style=style, card=name):
                    root = parse(svg).documentElement
                    assert root is not None
                    self.assertEqual(root.tagName, "svg")
                    self.assertTrue(root.getAttribute("width") and root.getAttribute("height"))
                    self.assertNotIn("JACK_IN", svg)

    def test_output_is_deterministic(self):
        raw, wk = demo_raw(self.cfg["username"], TODAY), demo_wakatime(TODAY)
        for style in ("terminal", "garden", "constellation"):
            self.assertEqual(build(self.cfg, raw, wk, TODAY, style), build(self.cfg, raw, wk, TODAY, style), style)

    def test_wakatime_offline_and_error(self):
        raw = demo_raw(self.cfg["username"], TODAY)
        off = build(self.cfg, raw, None, TODAY, "zen-sumi")
        self.assertIn("LINK OFFLINE", off["waka-overview.svg"])
        self.assertNotIn("waka-ai.svg", off)
        err = build(self.cfg, raw, {"error": "HTTP 401: Unauthorized."}, TODAY, "zen-sumi")
        self.assertIn("HTTP 401", err["waka-overview.svg"])
        for style in layouts.LAYOUTS:
            for svg in build(self.cfg, raw, None, TODAY, style).values():
                parse(svg)

    def test_rhythm_card_needs_daily_data(self):
        wk = demo_wakatime(TODAY)
        wk["days"] = None
        out = build(self.cfg, demo_raw(self.cfg["username"], TODAY), wk, TODAY, "zen-sumi")
        self.assertNotIn("waka-rhythm.svg", out)
        self.assertIn("waka-ai.svg", out)


class Readme(unittest.TestCase):
    def test_cards_pair_up_and_layouts_use_picture(self):
        body = readme.section(["header.svg", "stats.svg", "streak.svg", "projects.svg"], "me")
        self.assertIn('assets/stats.svg" alt="GitHub stats" width="49%"', body)
        self.assertIn("https://github.com/me?tab=repositories", body)
        pic = readme.section(["sansui-light.svg", "sansui-dark.svg"], "me")
        self.assertIn('<source media="(prefers-color-scheme: dark)" srcset="assets/sansui-dark.svg">', pic)
        self.assertEqual(pic.count("<picture>"), 1)

    def test_image_urls_carry_content_version(self):
        v = {"header.svg": "aaa111", "sansui-light.svg": "bbb222", "sansui-dark.svg": "ccc333"}
        body = readme.section(["header.svg"], "me", versions=v)
        self.assertIn('src="assets/header.svg?v=aaa111"', body)
        pic = readme.section(["sansui-light.svg", "sansui-dark.svg"], "me", versions=v)
        self.assertIn('srcset="assets/sansui-dark.svg?v=ccc333"', pic)
        self.assertIn('srcset="assets/sansui-light.svg?v=bbb222"', pic)
        self.assertIn('src="assets/sansui-dark.svg?v=ccc333"', pic)

    def test_version_is_a_short_content_hash(self):
        self.assertEqual(readme.version("<svg/>"), readme.version("<svg/>"))
        self.assertNotEqual(readme.version("<svg>a</svg>"), readme.version("<svg>b</svg>"))
        self.assertRegex(readme.version("<svg/>"), r"^[0-9a-f]{8}$")

    def test_update_only_touches_marked_section(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "README.md"
            f.write_text(f"intro\n{readme.START}\nold\n{readme.END}\noutro\n", encoding="utf-8")
            self.assertTrue(readme.update(f, "NEW"))
            self.assertEqual(f.read_text(encoding="utf-8"), f"intro\n{readme.START}\nNEW\n{readme.END}\noutro\n")
            g = Path(d) / "plain.md"
            g.write_text("no markers", encoding="utf-8")
            self.assertFalse(readme.update(g, "NEW"))
            self.assertEqual(g.read_text(encoding="utf-8"), "no markers")


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
