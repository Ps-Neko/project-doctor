"""cli.py — 개인 블로그 생성기 명령행 진입점.

사용 예:
    python cli.py new-post "오늘의 일기"     # 새 블로그 글 마크다운 생성
    python cli.py build                      # posts/ 전체를 블로그 HTML로 빌드
    python cli.py rss                        # RSS 피드(feed.xml) 생성
"""
import argparse
import sys

from posts.post_manager import load_all_posts, create_post_stub
from exporter import export_post
from rss_builder import build_rss


def cmd_new_post(args):
    path = create_post_stub(args.title)
    print("새 블로그 글 생성:", path)


def cmd_build(args):
    posts = load_all_posts()
    titles = [p["title"] for p in posts[:5]]
    for post in posts:
        out = "output/%s.html" % post["slug"]
        export_post(post["body"], post["title"], out,
                    theme_css="themes/%s.css" % args.theme,
                    recent_titles=titles)
        print("빌드 완료:", out)


def cmd_rss(args):
    out = build_rss(load_all_posts(), "output/feed.xml")
    print("RSS 피드 생성:", out)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="myblog", description="개인 블로그 생성기")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new-post", help="새 블로그 글 만들기")
    p_new.add_argument("title")
    p_new.set_defaults(func=cmd_new_post)

    p_build = sub.add_parser("build", help="블로그 전체 빌드")
    p_build.add_argument("--theme", default="default", choices=["default", "dark"])
    p_build.set_defaults(func=cmd_build)

    p_rss = sub.add_parser("rss", help="RSS 피드 생성")
    p_rss.set_defaults(func=cmd_rss)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
