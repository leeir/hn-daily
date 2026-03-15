#!/usr/bin/env python3
"""Generate a beautiful HTML page from HN stories JSON and write to docs/index.html + docs/YYYY-MM-DD.html"""

import json
import sys
import os
from datetime import datetime

WEEKDAY_CN = ["周一","周二","周三","周四","周五","周六","周日"]

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta property="og:title" content="{title}">
<meta property="og:description" content="今日 Hacker News Top {count} · 中英双语">
<meta property="og:type" content="website">
<style>
  :root {{
    --bg: #0f0f0f;
    --card: #1a1a1a;
    --border: #2a2a2a;
    --accent: #ff6600;
    --accent2: #ff8c42;
    --text: #e8e8e8;
    --muted: #888;
    --zh: #b0d4ff;
    --tag-bg: #2a2a2a;
    --score: #ff6600;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", sans-serif;
    line-height: 1.6;
    padding: 0 16px 60px;
    max-width: 780px;
    margin: 0 auto;
  }}

  /* Header */
  header {{
    padding: 36px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
  }}
  .logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
  }}
  .logo-icon {{
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 900; color: white;
    flex-shrink: 0;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
  }}
  .subtitle {{
    font-size: 13px;
    color: var(--muted);
    margin-top: 4px;
  }}
  .date-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--muted);
    margin-top: 12px;
  }}

  /* Story list */
  .story {{
    display: grid;
    grid-template-columns: 44px 1fr;
    gap: 0 14px;
    padding: 18px 0;
    border-bottom: 1px solid var(--border);
    transition: background .15s;
  }}
  .story:last-child {{ border-bottom: none; }}
  .story:hover {{ background: rgba(255,255,255,.02); border-radius: 8px; padding-left: 8px; padding-right: 8px; margin: 0 -8px; }}

  .rank {{
    font-size: 18px;
    font-weight: 700;
    color: var(--border);
    text-align: right;
    padding-top: 2px;
    user-select: none;
    font-variant-numeric: tabular-nums;
  }}
  .story:nth-child(-n+3) .rank {{ color: var(--accent); }}

  .content {{ min-width: 0; }}

  .title-en {{
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    line-height: 1.4;
    margin-bottom: 4px;
    text-decoration: none;
    display: block;
  }}
  .title-en:hover {{ color: var(--accent2); }}

  .title-zh {{
    font-size: 14px;
    color: var(--zh);
    margin-bottom: 8px;
    line-height: 1.4;
  }}

  .meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px 10px;
    align-items: center;
    font-size: 12px;
    color: var(--muted);
  }}
  .score {{
    color: var(--score);
    font-weight: 600;
  }}
  .domain {{
    background: var(--tag-bg);
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 11px;
  }}
  .meta a {{
    color: var(--muted);
    text-decoration: none;
  }}
  .meta a:hover {{ color: var(--accent2); }}

  /* Archive nav */
  .archive {{
    margin-top: 40px;
    padding: 16px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
  }}
  .archive h3 {{
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: .5px;
  }}
  .archive-links {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .archive-links a {{
    font-size: 12px;
    color: var(--muted);
    background: var(--tag-bg);
    border-radius: 6px;
    padding: 4px 10px;
    text-decoration: none;
    border: 1px solid var(--border);
  }}
  .archive-links a:hover {{ color: var(--accent2); border-color: var(--accent2); }}
  .archive-links a.active {{
    color: var(--accent);
    border-color: var(--accent);
  }}

  footer {{
    margin-top: 40px;
    text-align: center;
    font-size: 12px;
    color: var(--muted);
  }}
  footer a {{ color: var(--muted); }}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">Y</div>
    <h1>HN 每日精选</h1>
  </div>
  <div class="subtitle">Hacker News Top {count} · 中英双语每日精选</div>
  <div class="date-badge">📅 {date_full}</div>
</header>

<main>
{stories_html}
</main>

{archive_html}

<footer>
  <p>数据来源 <a href="https://news.ycombinator.com" target="_blank">Hacker News</a> · 由 OpenClaw 自动生成</p>
</footer>

</body>
</html>
"""

STORY_TMPL = """<div class="story">
  <div class="rank">{rank}</div>
  <div class="content">
    <a class="title-en" href="{url}" target="_blank" rel="noopener">{title_en}</a>
    <div class="title-zh">{title_zh}</div>
    <div class="meta">
      <span class="score">▲ {score}</span>
      <span>💬 <a href="{hn_url}" target="_blank">{comments} 条讨论</a></span>
      <span class="domain">{domain}</span>
    </div>
  </div>
</div>"""


def domain_of(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.", "") or "news.ycombinator.com"
    except Exception:
        return "news.ycombinator.com"


def build_page(stories: list, date_str: str, archive_dates: list, active_date: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAY_CN[dt.weekday()]
    date_full = f"{date_str} {weekday}"

    stories_html = "\n".join(
        STORY_TMPL.format(
            rank=s["rank"],
            url=s["url"],
            title_en=s["title_en"].replace("<","&lt;").replace(">","&gt;"),
            title_zh=s["title_zh"].replace("<","&lt;").replace(">","&gt;") if s.get("title_zh") else s["title_en"],
            score=s["score"],
            hn_url=s["hn_url"],
            comments=s["comments"],
            domain=domain_of(s["url"]),
        )
        for s in stories
    )

    if archive_dates:
        links = "\n".join(
            f'<a href="{d}.html" class="{"active" if d == active_date else ""}">{d}</a>'
            for d in sorted(archive_dates, reverse=True)
        )
        archive_html = f'<div class="archive"><h3>📚 历史存档</h3><div class="archive-links">{links}</div></div>'
    else:
        archive_html = ""

    return TEMPLATE.format(
        title=f"HN 每日精选 · {date_full}",
        count=len(stories),
        date_full=date_full,
        stories_html=stories_html,
        archive_html=archive_html,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: generate.py <stories.json> [docs_dir]", file=sys.stderr)
        sys.exit(1)

    stories_file = sys.argv[1]
    docs_dir = sys.argv[2] if len(sys.argv) > 2 else "docs"
    os.makedirs(docs_dir, exist_ok=True)

    with open(stories_file) as f:
        data = json.load(f)

    stories = data["stories"]
    today = datetime.now().strftime("%Y-%m-%d")

    # Find existing archive dates
    archive_dates = [today]
    for fname in os.listdir(docs_dir):
        if fname.endswith(".html") and fname != "index.html" and len(fname) == 15:
            archive_dates.append(fname[:-5])
    archive_dates = sorted(set(archive_dates), reverse=True)[:30]  # keep latest 30

    html = build_page(stories, today, archive_dates, today)

    # Write dated page
    dated_path = os.path.join(docs_dir, f"{today}.html")
    with open(dated_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Write index (latest)
    index_path = os.path.join(docs_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(json.dumps({
        "date": today,
        "count": len(stories),
        "dated_file": dated_path,
        "index_file": index_path,
    }))


if __name__ == "__main__":
    main()
