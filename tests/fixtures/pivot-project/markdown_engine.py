"""markdown_engine.py — 마크다운 텍스트를 HTML 조각으로 변환하는 핵심 엔진.

블로그 글이든 보고서든 상관없이 '마크다운 문법 처리'만 담당한다.
외부 라이브러리 없이 정규식 기반으로 동작한다.
"""
import re


def convert_headings(text):
    """# 제목 → <h1>제목</h1> (h1~h3 지원)"""
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)
    return text


def convert_emphasis(text):
    """**굵게** → <strong>, *기울임* → <em>"""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def convert_links(text):
    """[이름](주소) → <a href="주소">이름</a>"""
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)


def convert_lists(text):
    """- 항목 → <ul><li>항목</li></ul> (단순 1단계 목록)"""
    lines = text.split("\n")
    result = []
    in_list = False
    for line in lines:
        if line.startswith("- "):
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append("<li>%s</li>" % line[2:])
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(line)
    if in_list:
        result.append("</ul>")
    return "\n".join(result)


def convert_paragraphs(text):
    """빈 줄로 구분된 일반 문단을 <p>로 감싼다."""
    blocks = text.split("\n\n")
    wrapped = []
    for block in blocks:
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith("<"):
            wrapped.append(stripped)
        else:
            wrapped.append("<p>%s</p>" % stripped)
    return "\n".join(wrapped)


def markdown_to_html(text):
    """마크다운 문자열 → HTML 본문 조각 (페이지 틀은 exporter가 담당)."""
    if not isinstance(text, str):
        raise TypeError("마크다운 입력은 문자열이어야 합니다")
    html = convert_headings(text)
    html = convert_emphasis(html)
    html = convert_links(html)
    html = convert_lists(html)
    html = convert_paragraphs(html)
    return html
