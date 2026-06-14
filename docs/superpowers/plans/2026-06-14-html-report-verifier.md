# HTML 결과지 보안 검증기 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** HTML 결과지가 자기완결·무해한지 허용목록 fail-closed로 검사하는 배포 도구 `verify_html_report.py`를 추가한다(report-formats.md §5 갭 코드화).

**Architecture:** `html.parser.HTMLParser`(stdlib)로 태그·속성을 검사하고, CSS 외부 리소스·charset·비밀키는 텍스트 스캔으로 보완한다. 도구는 `skills/project-doctor/tools/`에 배포되어 스킬이 HTML 생성 직후·저장 전에 subprocess로 호출한다. 검사기는 `check_write_boundary.py`와 같은 역할·정직성(사후 검사·완전강제 아님)을 가진다.

**Tech Stack:** Python 3.11, 표준 라이브러리만(html.parser·re·sys), pytest(테스트 러너), 의존성 0.

---

## 파일 구조

- Create: `skills/project-doctor/tools/verify_html_report.py` — 검증기 도구(CLI + verify()).
- Create: `tests/test_verify_html_report.py` — 단위 테스트(subprocess 호출 + 비밀키 패턴 동기 테스트).
- Create: `tests/fixtures/golden-html-report.html` — 안전한 HTML 결과지 골든(모든 허용 태그 포함, 위반 0).
- Modify: `skills/project-doctor/references/report-formats.md` — §2 생성 후 호출 절차, §5 "사람이 직접 대조"를 코드 검사로 갱신.
- Modify: `skills/project-doctor/SKILL.md` — 버전 v2.7.7 → v2.7.8.
- Modify: `skills/project-doctor/README.md`, 루트 `README.md`, `skills/project-doctor/CHANGELOG.md`, `EVALS.md` — 버전 동기화.

---

## Task 1: 검증기 도구 + 골든 픽스처 + 전체 테스트 (test-first 1 red-green)

도구는 작고 응집적이라(verify() 한 함수에 독립 검사 6종) 전체 테스트를 먼저 쓰고 한 번에 green으로 만든다. 단계는 잘게 나눈다.

**Files:**
- Create: `tests/fixtures/golden-html-report.html`
- Create: `tests/test_verify_html_report.py`
- Create: `skills/project-doctor/tools/verify_html_report.py`

- [ ] **Step 1: 안전 골든 HTML 픽스처 작성**

`tests/fixtures/golden-html-report.html` (모든 허용 태그를 쓰되 위반 0 — UTF-8, charset 있음, 외부 리소스·이벤트핸들러·비밀키 없음):

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>프로젝트 건강검진 결과지 — 예시</title>
<style>
  body { font-family: "Malgun Gothic", sans-serif; color: #16181d; }
  h1 { font-size: 30px; }
  @media print { .howto { display: none; } }
</style>
</head>
<body>
<div class="doc">
  <div class="masthead"><span class="eyebrow">PROJECT DOCTOR</span></div>
  <h1>프로젝트 건강검진 결과지</h1>
  <p class="patient">환자 <b>예시</b> — 상태 요약.</p>
  <dl class="meta"><dt>검진일</dt><dd>2026-06-14</dd></dl>
  <h2>01 · 종합 판정</h2>
  <p class="opinion">의사 소견은 종합 등급과 같은 방향입니다.</p>
  <h2>02 · 부위별 소견</h2>
  <table>
    <thead><tr><th>부위</th><th>판정</th></tr></thead>
    <tbody><tr><td>구조</td><td>A</td></tr></tbody>
  </table>
  <ul class="applist"><li>참고 항목</li></ul>
  <ol><li>변경 <b>계획</b></li></ol>
  <p class="cmd"><code>"심각 1 실행해줘"</code></p>
  <p><small>안전 약속 — 승인 없이 파일을 고치지 않습니다.</small></p>
</div>
</body>
</html>
```

- [ ] **Step 2: 전체 테스트 작성 (실패 예정)**

`tests/test_verify_html_report.py`:

```python
"""verify_html_report.py (HTML 결과지 보안 검증기) 단위 테스트."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

TOOL = (Path(__file__).resolve().parent.parent
        / "skills" / "project-doctor" / "tools" / "verify_html_report.py")
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "golden-html-report.html"


def run_html(text: str, tmp_path: Path) -> subprocess.CompletedProcess:
    f = tmp_path / "report.html"
    f.write_text(text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(TOOL), str(f)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def run_path(path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_golden_passes():
    r = run_path(GOLDEN)
    assert r.returncode == 0, r.stdout
    assert "통과" in r.stdout


def test_disallowed_tag_script_fails(tmp_path):
    r = run_html('<meta charset="utf-8"><script>alert(1)</script>', tmp_path)
    assert r.returncode == 1
    assert "HTML-01" in r.stdout


def test_filename_injection_img_onerror(tmp_path):
    # 이스케이프 실패한 악성 파일명이 결과지에 raw로 박힌 형태.
    html = ('<meta charset="utf-8"><div class="doc">'
            '<td class="loc"></style><img src=x onerror=alert(1)>.py</td></div>')
    r = run_html(html, tmp_path)
    assert r.returncode == 1
    assert "HTML-01" in r.stdout  # <img> 낯선 태그
    assert "HTML-02" in r.stdout  # onerror 이벤트 핸들러


def test_event_handler_on_allowed_tag(tmp_path):
    r = run_html('<meta charset="utf-8"><span onclick="x()">클릭</span>', tmp_path)
    assert r.returncode == 1
    assert "HTML-02" in r.stdout


def test_css_external_import(tmp_path):
    r = run_html('<meta charset="utf-8"><style>@import url(https://evil.example/x.css);</style>',
                 tmp_path)
    assert r.returncode == 1
    assert "HTML-03" in r.stdout


def test_css_external_url(tmp_path):
    r = run_html('<meta charset="utf-8"><style>body{background:url(//cdn.evil/x.png)}</style>',
                 tmp_path)
    assert r.returncode == 1
    assert "HTML-03" in r.stdout


def test_dangerous_uri_scheme(tmp_path):
    r = run_html('<meta charset="utf-8"><a href="javascript:alert(1)">x</a>', tmp_path)
    assert r.returncode == 1
    assert "HTML-04" in r.stdout  # <a> 는 HTML-01 에도 걸리지만 HTML-04 경로를 확인


def test_missing_charset(tmp_path):
    r = run_html('<html><head><title>x</title></head><body><p>본문</p></body></html>', tmp_path)
    assert r.returncode == 1
    assert "HTML-05" in r.stdout


def test_secret_value_exposed(tmp_path):
    r = run_html('<meta charset="utf-8"><p>키: AKIAIOSFODNN7EXAMPLE 노출</p>', tmp_path)
    assert r.returncode == 1
    assert "HTML-06" in r.stdout


def test_usage_no_args():
    r = subprocess.run([sys.executable, str(TOOL)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 1
    assert "사용법" in r.stdout


def test_read_error_missing_file(tmp_path):
    r = run_path(tmp_path / "nope.html")
    assert r.returncode == 1
    assert "읽을 수 없습니다" in r.stdout


def _load_tool_module():
    spec = importlib.util.spec_from_file_location("verify_html_report", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_secret_patterns_in_sync_with_md_verifier():
    # 배포본(tools/)은 tests/ 를 import 못 하므로 비밀키 패턴을 자체 보유한다(BL-25 ① 제약).
    # 두 곳이 드리프트하면 HTML 결과지의 비밀키 탐지가 .md 보다 약해지므로 동기화를 테스트로 고정.
    import verify_report_format as vrf
    tool = _load_tool_module()
    md = [(n, p.pattern) for n, p in vrf.SECRET_PATTERNS]
    html = [(n, p.pattern) for n, p in tool.SECRET_PATTERNS]
    assert html == md, "HTML 검증기와 .md 형식검증기의 비밀키 패턴이 드리프트했습니다"
```

- [ ] **Step 3: 테스트 실행 → 실패 확인**

Run: `python -m pytest tests/test_verify_html_report.py -v`
Expected: 전부 FAIL (도구 파일 없음 → subprocess가 "can't open file" / sync 테스트는 import 실패).

- [ ] **Step 4: 검증기 도구 작성**

`skills/project-doctor/tools/verify_html_report.py`:

```python
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
# CSS 외부 리소스.
CSS_IMPORT_RE = re.compile(r"(?i)@import\b")
CSS_URL_EXTERNAL_RE = re.compile(r"(?i)url\(\s*['\"]?\s*(?:https?:)?//")
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
    if CSS_URL_EXTERNAL_RE.search(css):
        violations.append("HTML-03 CSS url(...) 외부 리소스 — 자기완결 의무 위반")

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
```

- [ ] **Step 5: 테스트 실행 → 통과 확인**

Run: `python -m pytest tests/test_verify_html_report.py -v`
Expected: 13개 전부 PASS.

- [ ] **Step 6: 커밋**

```bash
git add skills/project-doctor/tools/verify_html_report.py tests/test_verify_html_report.py tests/fixtures/golden-html-report.html
git commit -F <메시지파일>
```

메시지(파일 경유 — 한글):
```
feat(tools): HTML 결과지 보안 검증기 verify_html_report.py (BL-31)

허용목록 fail-closed로 HTML 결과지 검사: HTML-01 낯선 태그·HTML-02 이벤트핸들러·
HTML-03 외부 리소스(CSS 포함)·HTML-04 위험 URI·HTML-05 charset·HTML-06 비밀키.
html.parser(stdlib)·의존성 0. 스킬 배포(tools/), 골든+악성 13테스트.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
```

---

## Task 2: report-formats.md 절차 갱신 (§2 호출 / §5 코드화)

**Files:**
- Modify: `skills/project-doctor/references/report-formats.md`

- [ ] **Step 1: §2 자기완결 의무 끝에 검사 호출 한 줄 추가**

§2의 "신뢰 불가 값 HTML 이스케이프" 항목 **뒤에** 다음 bullet을 추가한다:

```markdown
- **생성 후 자동 검사 (저장 전):** `.html` 파일을 저장하기 직전, 함께 배포된 검사기로 확인한다 — `python "<스킬>/tools/verify_html_report.py" <보고서>.html`. 위반(허용목록 밖 태그·이벤트 핸들러·외부 리소스·위험 URI·charset 부재·비밀키 값)이 나오면 저장을 멈추고 이스케이프를 고친 뒤 다시 검사한다. 이 검사기는 사후 검사이지 완전 강제가 아니므로(검사기 docstring 참조), 통과해도 골격 데이터 이스케이프는 작성 시 지켜야 한다.
```

- [ ] **Step 2: §5 비밀키 자가 점검 문장을 코드 검사로 갱신**

§5의 "저장 전 비밀키 자가 점검" 항목에서 "HTML/PDF는 그 검사 대상이 아니므로 … 사람(Claude)이 직접 대조한다" 부분을 다음으로 바꾼다:

```markdown
- **저장 전 비밀키 자가 점검 (md·HTML·PDF 모두):** md 보고서는 형식 검증기(`verify_report_format.py` FORM-11)가, HTML/PDF는 §2의 `verify_html_report.py`(HTML-06)가 비밀키 값 노출을 검사한다 — 두 검사기의 비밀키 패턴은 동기화돼 있다(단위 테스트가 고정). 다만 두 검사기 모두 알려진 접두 패턴 휴리스틱이므로, 통과가 키 부재를 보증하진 않는다 — 코드 인용에 키 값이 끼지 않았는지 사람이 함께 확인하기를 권한다.
```

- [ ] **Step 3: 커밋**

```bash
git add skills/project-doctor/references/report-formats.md
git commit -F <메시지파일>
```
메시지: `docs(report-formats): §2/§5에 verify_html_report 호출·코드 검사 반영 (BL-31)` + Co-Authored-By 줄.

---

## Task 3: 버전 bump v2.7.8 + 정합 게이트 + 전체 스위트

**Files:**
- Modify: `skills/project-doctor/SKILL.md` (스킬 버전: v2.7.7 → v2.7.8 — 같은 줄의 두 v2.7.7 모두)
- Modify: 루트 `README.md` (`현재 버전:` 줄), `skills/project-doctor/README.md` (`현재 버전:` 줄)
- Modify: `skills/project-doctor/CHANGELOG.md` (맨 위에 `## v2.7.8` 항목 추가)
- Modify: `EVALS.md` (검사기 추가·탐지율 무영향 1행)

- [ ] **Step 1: SKILL.md 버전 갱신**

`skills/project-doctor/SKILL.md`의 `스킬 버전: **v2.7.7** — 모든 보고서 첫머리에 `스킬 버전: v2.7.7`을 인쇄한다.` 줄에서 **두 v2.7.7을 모두 v2.7.8로** 바꾼다.

- [ ] **Step 2: 나머지 표기처 갱신**

각 파일을 Read 한 뒤 마커 줄의 버전을 v2.7.8로 바꾼다:
- 루트 `README.md`: `현재 버전:` 줄
- `skills/project-doctor/README.md`: `현재 버전:` 줄
- `skills/project-doctor/CHANGELOG.md`: 맨 위에 새 항목 추가:
  ```markdown
  ## v2.7.8
  - HTML 결과지 보안 검증기 `tools/verify_html_report.py` 추가 (BL-31) — 허용목록 fail-closed로 낯선 태그·이벤트 핸들러·외부 리소스·위험 URI·charset 부재·비밀키 값 검사. report-formats.md §2/§5가 생성 후 호출. 검사기 추가일 뿐 탐지 카탈로그·채점 무변경.
  ```
- `EVALS.md`: checkup/release 관련 표나 연혁에 한 행 추가 — "v2.7.8: HTML 보안 검증기 추가, 탐지율·채점 무영향(검사기 한정)".

- [ ] **Step 3: 버전 정합 게이트 실행 → 통과 확인**

Run: `python tests/check_version.py`
Expected: `버전 정합: 전부 일치 (통과)` (종료 0). 불일치가 나오면 그 파일을 v2.7.8로 맞춘다.

- [ ] **Step 4: 전체 테스트 스위트 실행 → 통과 확인**

Run: `python -m pytest tests/ -v`
Expected: 기존 테스트 + 신규 13개 전부 PASS.

추가 회귀 확인:
Run: `python tests/check_scoring_regression.py` → 정답지 100%·오탐 0 유지.
Run: `python tests/run_checks.py tests/golden/checkup-report.md tests/fixtures/messy-project/EXPECTED.md` → 골든 E2E 통과(검사기 추가가 기존 산출물에 무영향).

- [ ] **Step 5: 커밋**

```bash
git add skills/project-doctor/SKILL.md README.md skills/project-doctor/README.md skills/project-doctor/CHANGELOG.md EVALS.md
git commit -F <메시지파일>
```
메시지: `chore(release): v2.7.8 — HTML 보안 검증기 추가 반영 + 버전 정합` + Co-Authored-By 줄.

---

## Task 4: 브랜치 마무리

- [ ] **Step 1: 최종 확인**

Run: `git -C <repo> log --oneline feat/html-report-verifier ^main` — 3 커밋(도구·문서·릴리스) 확인.
Run: `python -m pytest tests/ -q && python tests/check_version.py && python tests/check_links.py` — 전부 green.

- [ ] **Step 2: 통합**

`superpowers:finishing-a-development-branch` 스킬로 머지/PR 결정. (공개 레포 머지 시 noreply author·CI 양 OS green 확인 — 메모리 BL-19/BL-21.)

---

## 자가검토 메모 (writing-plans Self-Review)

- **스펙 커버리지**: §2 역할→Task1+2 · §3 계약→Task1(main) · §4 검사 6종→Task1(코드+13테스트) · §5 파서→Task1 · §6 한계→Task1(docstring) · §7 테스트/통합→Task1+CI자동 · §8 문서/버전→Task2+3 · §9 YAGNI(렌더러·run_checks통합·PDF파서 제외)→계획에 미포함 확인 · §10 인수기준→Task3 게이트로 검증. 갭 없음.
- **placeholder**: 없음(버전 파일은 marker 기반 + check_version 게이트로 검증 — 결정적).
- **타입 일관성**: `verify()`·`SECRET_PATTERNS`·`ALLOWED_TAGS`·`_HtmlAuditor` 이름이 도구·테스트에서 일치. 출력 문자열 `HTML-0X`·`사용법`·`읽을 수 없습니다`·`통과`가 테스트 단언과 일치.
