"""Write the profile section of README.md for whichever style was generated.

Only the text between the two markers is replaced, so the rest of the README is yours.
"""

from __future__ import annotations

from pathlib import Path

START = "<!-- PROFILE:START -->"
END = "<!-- PROFILE:END -->"

# cards shown side by side at half width
PAIRS = [("stats.svg", "streak.svg"), ("languages.svg", "repos.svg"), ("waka-projects.svg", "waka-tools.svg")]
ALT = {
    "header.svg": "GitHub profile header", "stats.svg": "GitHub stats", "streak.svg": "Contribution streak",
    "languages.svg": "Top languages", "repos.svg": "Repositories and stars", "contributions.svg": "Contribution graph",
    "activity.svg": "Commit activity", "skills.svg": "Technology skills", "projects.svg": "Latest projects",
    "waka-overview.svg": "WakaTime coding time", "waka-ai.svg": "AI coding", "waka-projects.svg": "WakaTime projects",
    "waka-tools.svg": "Editors and tools", "waka-rhythm.svg": "Coding rhythm",
}


def section(files: list[str], login: str, assets: str = "assets") -> str:
    lines: list[str] = []
    done: set[str] = set()

    def img(name: str, width: str) -> str:
        return f'<img src="{assets}/{name}" alt="{ALT.get(name, name)}" width="{width}">'

    for name in files:
        if name in done:
            continue
        stem = name.rsplit("-", 1)[0]
        if name.endswith(("-light.svg", "-dark.svg")):  # single-image layout
            light, dark = f"{stem}-light.svg", f"{stem}-dark.svg"
            have_l, have_d = light in files, dark in files
            done.update(n for n in (light, dark) if n in files)
            if have_l and have_d:
                lines.append(
                    f'<p align="center"><picture>'
                    f'<source media="(prefers-color-scheme: dark)" srcset="{assets}/{dark}">'
                    f'<source media="(prefers-color-scheme: light)" srcset="{assets}/{light}">'
                    f'<img src="{assets}/{dark}" alt="{login} GitHub profile" width="100%"></picture></p>'
                )
            else:
                only = light if have_l else dark
                lines.append(f'<p align="center"><img src="{assets}/{only}" alt="{login} GitHub profile" '
                             f'width="{"440" if stem == "receipt" else "100%"}"></p>')
            continue
        pair = next((p for p in PAIRS if name in p), None)
        if pair and all(n in files for n in pair):
            lines.append(f'<p align="center">\n  {img(pair[0], "49%")}\n  {img(pair[1], "49%")}\n</p>')
            done.update(pair)
            continue
        tag = img(name, "100%")
        if name == "projects.svg":
            tag = f'<a href="https://github.com/{login}?tab=repositories">{tag}</a>'
        lines.append(f'<p align="center">\n  {tag}\n</p>')
        done.add(name)
    return "\n\n".join(lines)


def update(readme: Path, body: str) -> bool:
    """Replace the marked section. Returns False (and leaves the file alone) when markers are missing."""
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return False
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{body}\n{END}{tail}"
    if new != text:
        readme.write_text(new, encoding="utf-8")
    return True
