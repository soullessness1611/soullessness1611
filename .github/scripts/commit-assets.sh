#!/usr/bin/env bash
# Commit regenerated cards and push to the branch tip, rebasing onto any newer
# commits first (re-runs of old runs, or two runs racing). Generated SVGs win
# conflicts because they are the freshest data.
set -euo pipefail
branch="${1:-main}"

git add assets/*.svg
if git diff --cached --quiet; then
  echo "No changes"
  exit 0
fi
git commit -q -m "chore(stats): refresh SVG cards [skip ci]"

for attempt in 1 2 3; do
  # in a rebase, -X theirs keeps the commit being replayed (our new cards)
  git pull -q --rebase -X theirs origin "$branch"
  if git push -q origin "HEAD:$branch"; then
    echo "Pushed $(git rev-parse --short HEAD) (attempt $attempt)"
    exit 0
  fi
  sleep $((attempt * 3))
done
echo "push failed after 3 attempts" >&2
exit 1
