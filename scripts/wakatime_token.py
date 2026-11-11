"""Get a long-lived WakaTime OAuth token (scopes read_stats, read_summaries) for the WAKATIME_TOKEN secret.

WakaTime no longer accepts API keys for reading stats. Run this once:

    python3 scripts/wakatime_token.py | gh secret set WAKATIME_TOKEN -R <owner>/<repo>

Prompts go to the terminal (stderr); only the access token is written to stdout,
so piping into `gh secret set` never shows the token on screen.

Before running, create an app at https://wakatime.com/apps and set its
Authorized Redirect URI to https://localhost (or pass --redirect-uri).
Tokens from the authorization-code flow are valid for 100 years.
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

AUTHORIZE_URL = "https://wakatime.com/oauth/authorize"
TOKEN_URL = "https://wakatime.com/oauth/token"


def ask(prompt: str) -> str:
    sys.stderr.write(prompt)
    sys.stderr.flush()
    return sys.stdin.readline().strip()


def authorize_url(client_id: str, redirect_uri: str) -> str:
    query = urllib.parse.urlencode(
        {"client_id": client_id, "response_type": "code", "redirect_uri": redirect_uri, "scope": "read_stats,read_summaries"}
    )
    return f"{AUTHORIZE_URL}?{query}"


def extract_code(pasted: str) -> str:
    """Accept either the bare code or the full redirect URL (…?code=XYZ&state=…)."""
    if "code=" in pasted:
        query = urllib.parse.urlparse(pasted).query or pasted.split("?", 1)[-1]
        return urllib.parse.parse_qs(query).get("code", [""])[0]
    return pasted.strip()


def parse_token_response(body: bytes) -> dict:
    """WakaTime answers JSON or form-encoded depending on the Accept header."""
    text = body.decode()
    try:
        return json.loads(text)
    except ValueError:
        return {k: v[0] for k, v in urllib.parse.parse_qs(text).items()}


def exchange(client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict:
    data = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code": code,
        }
    ).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, headers={"Accept": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return parse_token_response(resp.read())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--redirect-uri", default="https://localhost")
    args = ap.parse_args()

    client_id = ask("WakaTime App ID: ")
    client_secret = getpass.getpass("WakaTime App Secret (hidden): ", stream=sys.stderr).strip()
    sys.stderr.write(
        "\n1) Open this URL, log in and click Authorize:\n\n   "
        + authorize_url(client_id, args.redirect_uri)
        + "\n\n2) The browser lands on a page that may not load — copy its whole address.\n"
    )
    code = extract_code(ask("Paste the redirect URL (or just the code): "))
    if not code:
        sys.stderr.write("error: no code found\n")
        return 1
    try:
        token = exchange(client_id, client_secret, args.redirect_uri, code)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"error: HTTP {e.code}: {e.read().decode(errors='replace')[:300]}\n")
        return 1
    access = token.get("access_token")
    if not access:
        sys.stderr.write(f"error: no access_token in response (keys: {', '.join(token)})\n")
        return 1
    sys.stderr.write(f"\nOK — scope: {token.get('scope', '?')}, expires: {token.get('expires_at', '?')}\n")
    print(access)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
