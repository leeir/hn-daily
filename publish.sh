#!/bin/bash
# publish.sh — fetch HN, generate HTML, push to GitHub Pages
set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/hacker-news-daily"
REPO_DIR="$HOME/.openclaw/workspace/hn-daily-repo"
STORIES_TMP="/tmp/hn_stories_$(date +%Y%m%d).json"

# 1. Clone or pull repo
if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR" && git pull --rebase --quiet
else
  git clone https://github.com/leeir/hn-daily.git "$REPO_DIR"
  cd "$REPO_DIR"
fi

# 2. Fetch stories
python3 "$SKILL_DIR/scripts/fetch_hn.py" 30 > "$STORIES_TMP"

# 3. Generate HTML
python3 "$REPO_DIR/generate.py" "$STORIES_TMP" "$REPO_DIR/docs"

# 4. Commit & push
cd "$REPO_DIR"
git add docs/
git diff --cached --quiet || git commit -m "📰 HN Daily $(date +%Y-%m-%d)"
git push origin main

# 5. Output GitHub Pages URL
TODAY=$(date +%Y-%m-%d)
echo "https://leeir.github.io/hn-daily/"
