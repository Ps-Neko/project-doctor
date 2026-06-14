"""HTML 결과지가 안전한지 기계 검사한다 (report-formats.md §2/§5, BACKLOG BL-31).

verify_report_format.py(FORM-xx)가 .md 보고서의 형식 계약을 검사한다면, 이 도구는 HTML
결과지가 자기완결·무해한지(허용목록 fail-closed) 검사한다. 스킬과 함께 설치되므로
(`~/.claude/skills/project-doctor/tools/`) HTML 생성 직후·저장 전에 호출할 수 있다.

사용법:
  python verify_html_report.py <보고서.html>

판정: 위반 0건이면 통과(종료 0). 허용목록 밖 태그·이벤트 핸들러 속성·외부 리소스·위험 URI
  스킴·charset 메타 부재·비밀키 값 노출이 하나라도 있으면 미달(종료 1).
이 도구는 '읽기 전용 검사'다 — 어떤 파일도 만들거나 고치지 않는다.

## 보안 한계 (호출 측이 반드시 알 것)
- **사후 검사일 뿐이다.** HTML 생성은 여전히 모델이 한다. 이 도구는 이스케이프 실패의
  *증상*(허용목록 밖 태그·이벤트 핸들러·외부 리소스)을 잡지, 삽입된 모든 문자열이
  이스케이프됐음을 보증하지 않는다. 최종 안전은 호출 측(Claude/사람)에 달려 있다.
- **허용목록 태그만 쓰는 무해 주입**(예: 텍스트에 `<b>`)은 잡지 않는다 — 무해하므로.
- **RCDATA 한계**: <title> 안의 비-탈출(`</title>` 없이) 마크업은 브라우저도 텍스트로 보므로
  무해하고, 여기서도 검출하지 않는다. 탈출형(`</title><script>`)은 태그가 되어 HTML-01로 잡힌다.
- **골격 결합.** report-formats.md의 HTML 골격이 새 태그를 얻으면 이 ALLOWED_TAGS도 같은
  작업에서 갱신해야 한다 — 안 그러면 정상 보고서가 false-fail 한다.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser

# report-formats.md §2 HTML 골격에 실제로 쓰이는 태그만 허용 (fail-closed).
# 골격이 바뀌면 이 집합도 같은 작업에서 갱신할 것 (docstring 한계 참조).
ALLOWED_TAGS: frozenset[str] = frozenset({
    "html", "head", "meta", "title", "style", "body",
    "p", "div", "span", "h1", "h2",
    "dl", "dt", "dd", "ol", "li", "ul",
    "table", "thead", "tbody", "tr", "th", "td",
    "code", "b", "small",
})

# 외부 리소스로 보는 URL(자기완결 의무 위반): 스킴 있는 절대 URL·프로토콜 상대(//).
EXTERNAL_URL_RE = re.compile(r"(?i)(?:https?:)?//|(?:https?|ftp|ftps):")
# 위험 URI 스킴.
DANGEROUS_URI_RE = re.compile(r"(?i)^\s*(?:javascript|data|vbscript):")
# 외부 리소스를 가질 수 있는 속성.
URL_ATTRS = frozenset({"src", "href", "background", "poster", "srcset", "data"})
# CSS @import / url(). 골격(report-formats.md §2)은 url()을 전혀 쓰지 않고 외부·인라인 리소스를
# 금지하므로, 스킴을 가리지 않고 url( 자체를 위반으로 본다(fail-closed). 스킴 한정 정규식은
# url(file:·data:·blob:·behavior:)를 놓쳤다(7차 평가 P1a) — 전면금지가 그 갭을 닫는다.
# 골격이 언젠가 url()을 쓰게 되면 이 규칙을 같은 작업에서 갱신할 것(docstring 골격 결합 참조).
CSS_IMPORT_RE = re.compile(r"(?i)@import\b")
CSS_URL_RE = re.compile(r"(?i)url\(")
# charset 메타 (대소문자·따옴표 변형 허용).
CHARSET_RE = re.compile(r"(?i)<meta[^>]*charset\s*=\s*['\"]?\s*utf-8")

# 비밀키 값 노출 휴리스틱 — verify_report_format.SECRET_PATTERNS 와 동기화(tests 가 검사).
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS 액세스 키 ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("개인키 블록", re.compile(r"-----BEGIN[\sA-Z]{0,40}PRIVATE KEY-----")),
    ("GitHub 토큰", re.compile(r"\bgh[opsru]_[A-Za-z0-9]{36,255}\b")),
    ("GitHub 세분화 PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("Google API 키", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Slack 토큰", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("API 시크릿 키", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
)


class _HtmlAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.violations: list[str] = []
        self._in_style = False
        self.style_text: list[str] = []

    def _check_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t not in ALLOWED_TAGS:
            self.violations.append(
                f"HTML-01 허용목록 밖 태그 <{t}> — 골격에 없는 태그입니다 (주입된 마크업일 수 있습니다)")
        for raw_name, raw_value in attrs:
            n = (raw_name or "").lower()
            v = raw_value or ""
            if n.startswith("on"):
                self.violations.append(
                    f"HTML-02 이벤트 핸들러 속성 {n}= (<{t}>) — 스크립트 실행 벡터입니다")
            if n == "style" and (CSS_IMPORT_RE.search(v) or CSS_URL_RE.search(v)):
                self.violations.append(
                    f"HTML-03 인라인 style 의 @import/url() (<{t}>) — 자기완결 의무 위반(리소스 로드 금지)")
            if t == "meta" and n == "http-equiv" and v.strip().lower() == "refresh":
                self.violations.append(
                    "HTML-03 메타 새로고침 외부 이동 (<meta http-equiv=refresh>) — 자기완결 의무 위반")
            if DANGEROUS_URI_RE.search(v):
                self.violations.append(
                    f"HTML-04 위험 URI 스킴 {n}=\"{v[:40]}\" (<{t}>)")
            elif n in URL_ATTRS and EXTERNAL_URL_RE.search(v):
                self.violations.append(
                    f"HTML-03 외부 리소스 {n}=\"{v[:40]}\" (<{t}>) — 자기완결 의무 위반")

    def handle_starttag(self, tag, attrs):
        self._check_tag(tag, attrs)
        if tag.lower() == "style":
            self._in_style = True

    def handle_startendtag(self, tag, attrs):
        self._check_tag(tag, attrs)

    def handle_endtag(self, tag):
        if tag.lower() == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_style:
            self.style_text.append(data)


def verify(html_text: str) -> list[str]:
    auditor = _HtmlAuditor()
    auditor.feed(html_text)
    auditor.close()
    violations = list(auditor.violations)

    css = "\n".join(auditor.style_text)
    if CSS_IMPORT_RE.search(css):
        violations.append("HTML-03 CSS @import — 외부 스타일 가져오기 금지 (자기완결 의무)")
    if CSS_URL_RE.search(css):
        violations.append("HTML-03 CSS url(...) — 골격 밖 리소스 로드 금지 (자기완결 의무)")

    if not CHARSET_RE.search(html_text):
        violations.append('HTML-05 <meta charset="utf-8"> 가 없습니다 (인코딩 계약)')

    for name, pattern in SECRET_PATTERNS:
        m = pattern.search(html_text)
        if m:
            violations.append(
                f"HTML-06 비밀키 값 노출 의심 ({name}): '{m.group()[:8]}…' "
                "— 보고서엔 위치만 적어야 합니다")
    return violations


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) != 2:
        print("사용법: python verify_html_report.py <보고서.html>")
        return 1
    try:
        with open(argv[1], encoding="utf-8", errors="replace") as f:
            html_text = f.read()
    except OSError as err:
        print(f"오류: 파일을 읽을 수 없습니다 - {err}")
        return 1
    violations = verify(html_text)
    for v in violations:
        print(f"보안 위반: {v}")
    print(f"위반: {len(violations)}건")
    print(f"판정: {'통과' if not violations else '미달'} (기준: 보안 위반 0건)")
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
