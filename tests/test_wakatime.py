import io
import json
import unittest
import urllib.error
from datetime import date
from unittest import mock

from generator import waka_cards
from generator.wakatime import fetch_wakatime, parse_stats, parse_summaries


def http_error(code: int, body: bytes) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://wakatime.com/x", code, "FORBIDDEN", {}, io.BytesIO(body))  # type: ignore[arg-type]


class FetchErrors(unittest.TestCase):
    def test_http_error_returns_reason_from_body(self):
        err = http_error(403, b'{"error": "Requires premium"}')
        with mock.patch("urllib.request.urlopen", side_effect=err):
            wk = fetch_wakatime("waka_key")
        assert wk is not None
        self.assertEqual(wk["error"], "HTTP 403: Requires premium")

    def test_key_whitespace_is_stripped(self):
        with mock.patch("urllib.request.urlopen", side_effect=http_error(401, b"{}")) as m:
            fetch_wakatime("  waka_key\n")
        auth = m.call_args.args[0].get_header("Authorization")
        self.assertEqual(auth, "Basic d2FrYV9rZXk=")  # base64("waka_key")

    def test_oauth_token_uses_bearer_and_wins_over_api_key(self):
        with mock.patch("urllib.request.urlopen", side_effect=http_error(401, b"{}")) as m:
            fetch_wakatime("waka_key", oauth_token=" waka_tok_abc\n")
        self.assertEqual(m.call_args.args[0].get_header("Authorization"), "Bearer waka_tok_abc")

    def test_blank_key_counts_as_missing(self):
        with mock.patch("urllib.request.urlopen") as m:
            self.assertIsNone(fetch_wakatime("  \n", oauth_token=""))
        m.assert_not_called()


STATS = {"data": {
    "human_readable_range": "Last 7 Days", "human_readable_total_including_other_language": "22 hrs 58 mins",
    "total_seconds_including_other_language": 82680, "human_readable_daily_average": "5 hrs 44 mins",
    "best_day": {"date": "2026-11-10", "text": "6 hrs 12 mins"},
    "languages": [{"name": "Markdown", "percent": 47.67, "text": "10 hrs 57 mins", "total_seconds": 39420}],
    "projects": [{"name": "ZeN-Workflow", "percent": 46.2, "text": "10 hrs 37 mins", "total_seconds": 38220}],
    "editors": [{"name": "Claude Code", "percent": 85.72, "text": "19 hrs 41 mins"}],
    "operating_systems": [{"name": "WSL", "percent": 100, "text": "22 hrs 58 mins"}],
    "machines": [{"name": "my-pc", "percent": 100}],
    "ai_additions": 14080, "human_additions": 5, "ai_input_tokens": 546200000, "ai_output_tokens": 1800000,
    "ai_model_total_cost": 156.2, "ai_sessions": 66, "ai_prompt_events_total": 262,
    "ai_model_line_changes": {"Opus": 14080},
}}


class Parsing(unittest.TestCase):
    def test_stats_fields(self):
        wk = parse_stats(STATS)
        self.assertEqual(wk["range"], "last 7 days")
        self.assertEqual(wk["projects"][0]["name"], "ZeN-Workflow")
        self.assertEqual(wk["machines"], 1)  # count only, never the machine name
        self.assertNotIn("my-pc", json.dumps(wk))
        self.assertAlmostEqual(wk["ai"]["ai_percent"], 100 * 14080 / 14085)
        self.assertEqual(wk["ai"]["models"][0], {"name": "Opus", "lines": 14080.0, "percent": 100.0})
        self.assertEqual(wk["best_day"]["date"], "2026-11-10")

    def test_missing_text_is_built_from_seconds(self):
        wk = parse_stats({"data": {"projects": [{"name": "p", "total_seconds": 3900.0}]}})
        self.assertEqual(wk["projects"][0]["text"], "1 hrs 5 mins")

    def test_no_ai_activity_means_no_ai_section(self):
        self.assertIsNone(parse_stats({"data": {"languages": []}})["ai"])

    def test_model_breakdown_as_list(self):
        wk = parse_stats({"data": {"ai_additions": 10, "ai_model_breakdown": [{"name": "Sonnet", "ai_additions": 3}, {"name": "Opus", "ai_additions": 7}]}})
        self.assertEqual([m["name"] for m in wk["ai"]["models"]], ["Opus", "Sonnet"])

    def test_summaries_sorted_by_date(self):
        days = parse_summaries({"data": [
            {"range": {"date": "2026-11-11"}, "grand_total": {"total_seconds": 20220, "text": "5 hrs 37 mins", "ai_additions": 3450}},
            {"range": {"date": "2026-11-05"}, "grand_total": {"total_seconds": 3600, "text": "1 hr", "human_additions": 40}},
        ]})
        self.assertEqual([d["date"] for d in days], ["2026-11-05", "2026-11-11"])
        self.assertEqual(days[1]["ai_additions"], 3450)
        self.assertEqual(days[0]["human_additions"], 40)


class SummariesOptional(unittest.TestCase):
    def test_stats_survive_when_summaries_scope_is_missing(self):
        ok = mock.MagicMock()
        ok.__enter__.return_value = io.BytesIO(json.dumps(STATS).encode())
        with mock.patch("urllib.request.urlopen", side_effect=[ok, http_error(403, b'{"error": "Missing scope read_summaries"}')]) as m:
            wk = fetch_wakatime(None, oauth_token="waka_tok_x", today=date(2026, 11, 11))
        assert wk is not None
        self.assertEqual(wk["total"], "22 hrs 58 mins")
        self.assertIsNone(wk["days"])
        self.assertIn("read_summaries", wk["days_error"])
        self.assertIn("start=2026-11-05&end=2026-11-11", m.call_args_list[1].args[0].full_url)


class ErrorCard(unittest.TestCase):
    def test_card_shows_error_instead_of_add_key_hint(self):
        svg = waka_cards.overview_card({"error": "HTTP 403: Requires premium"})
        self.assertIn("HTTP 403: Requires premium", svg)
        self.assertNotIn("Add a WAKATIME_TOKEN", svg)

    def test_missing_card_asks_for_oauth_token(self):
        self.assertIn("WAKATIME_TOKEN", waka_cards.overview_card(None))


if __name__ == "__main__":
    unittest.main()
