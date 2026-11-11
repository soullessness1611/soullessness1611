import io
import unittest
import urllib.error
from unittest import mock

from generator import cards
from generator.wakatime import fetch_wakatime


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


class ErrorCard(unittest.TestCase):
    def test_card_shows_error_instead_of_add_key_hint(self):
        svg = cards.wakatime_card({"error": "HTTP 403: Requires premium"})
        self.assertIn("HTTP 403: Requires premium", svg)
        self.assertNotIn("Add a WAKATIME_TOKEN", svg)

    def test_missing_card_asks_for_oauth_token(self):
        self.assertIn("WAKATIME_TOKEN", cards.wakatime_card(None))


if __name__ == "__main__":
    unittest.main()
