"""post_manager.py — posts/ 폴더의 블로그 글(마크다운)을 관리한다.

글 목록 읽기, 날짜순 정렬, 새 글 뼈대 생성 등 블로그 전용 기능.
파일명 규칙: YYYY-MM-DD-슬러그.md
"""
import os
import re

POSTS_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def parse_filename(filename):
    """'2025-03-01-first-post.md' → (날짜, 슬러그) 또는 None."""
    match = FILENAME_PATTERN.match(filename)
    if not match:
        return None
    return match.group(1), match.group(2)


def load_all_posts():
    """posts/ 안의 모든 글을 읽어 최신순 딕셔너리 리스트로 반환."""
    posts = []
    for filename in os.listdir(POSTS_DIR):
        parsed = parse_filename(filename)
        if parsed is None:
            continue
        date, slug = parsed
        path = os.path.join(POSTS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            body = f.read()
        first_line = body.strip().split("\n")[0]
        title = first_line.lstrip("# ").strip() or slug
        posts.append({"date": date, "slug": slug, "title": title, "body": body})
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def create_post_stub(title, date="2026-01-01"):
    """새 블로그 글의 마크다운 뼈대 파일을 만들고 경로를 반환."""
    slug = re.sub(r"[^a-z0-9가-힣]+", "-", title.lower()).strip("-") or "untitled"
    path = os.path.join(POSTS_DIR, "%s-%s.md" % (date, slug))
    stub = "# %s\n\n여기에 본문을 쓰세요.\n" % title
    with open(path, "w", encoding="utf-8") as f:
        f.write(stub)
    return path
