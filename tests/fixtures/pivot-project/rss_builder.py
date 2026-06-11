"""rss_builder.py — 블로그 글 목록으로 RSS 2.0 피드(feed.xml)를 만든다.

구독자가 새 글을 받아보게 하는 블로그 전용 기능이다.
"""
import os

FEED_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>나의 일상 블로그</title>
<link>https://example.com/blog</link>
<description>일상과 개발 이야기를 담는 개인 블로그</description>
"""

FEED_FOOTER = """</channel>
</rss>
"""

ITEM_TEMPLATE = """<item>
<title>{title}</title>
<link>https://example.com/blog/{slug}.html</link>
<pubDate>{date}</pubDate>
<description>{summary}</description>
</item>
"""


def build_item(post):
    summary = post["body"].strip().split("\n")[0][:80]
    return ITEM_TEMPLATE.format(
        title=post["title"],
        slug=post["slug"],
        date=post["date"],
        summary=summary,
    )


def build_rss(posts, out_path="output/feed.xml"):
    """글 목록(딕셔너리 리스트) → RSS XML 파일 경로 반환."""
    items = [build_item(p) for p in posts]
    xml = FEED_HEADER + "".join(items) + FEED_FOOTER
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    return out_path
