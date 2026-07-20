"""exporter.py — 변환된 HTML 본문을 '블로그 페이지' 모양으로 감싸 파일로 내보낸다.

블로그 전용 요소(사이드바, 이전/다음 글 링크, 댓글 영역, 테마 CSS)가
페이지 틀에 박혀 있다.
"""
import os

from markdown_engine import markdown_to_html

BLOG_TITLE = "나의 일상 블로그"
DEFAULT_THEME = "themes/default.css"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{post_title} - {blog_title}</title>
<link rel="stylesheet" href="{theme_css}">
</head>
<body>
<header class="blog-header">
  <h1>{blog_title}</h1>
  <nav><a href="index.html">홈</a> | <a href="archive.html">글 목록</a> | <a href="feed.xml">RSS</a></nav>
</header>
<aside class="sidebar">
  <h3>최근 글</h3>
  {recent_posts}
</aside>
<main class="post-body">
{body}
</main>
<footer class="post-nav">
  <a href="{prev_link}">← 이전 글</a>
  <a href="{next_link}">다음 글 →</a>
  <div class="comments">댓글 기능은 준비 중입니다.</div>
</footer>
</body>
</html>
"""


def render_recent_list(titles):
    """사이드바에 들어갈 최근 글 목록 HTML."""
    items = ["<li>%s</li>" % t for t in titles]
    return "<ul>" + "".join(items) + "</ul>"


def export_post(markdown_text, post_title, out_path,
                theme_css=DEFAULT_THEME, recent_titles=(),
                prev_link="#", next_link="#"):
    """마크다운 글 1편 → 블로그 페이지 HTML 파일."""
    body = markdown_to_html(markdown_text)
    page = PAGE_TEMPLATE.format(
        post_title=post_title,
        blog_title=BLOG_TITLE,
        theme_css=theme_css,
        recent_posts=render_recent_list(recent_titles),
        body=body,
        prev_link=prev_link,
        next_link=next_link,
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return out_path
