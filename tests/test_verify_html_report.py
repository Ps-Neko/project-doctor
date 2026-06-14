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


def test_inline_style_external_url(tmp_path):
    r = run_html('<meta charset="utf-8"><div style="background:url(//cdn.evil/x.png)">x</div>', tmp_path)
    assert r.returncode == 1
    assert "HTML-03" in r.stdout


def test_meta_refresh_redirect(tmp_path):
    r = run_html('<meta charset="utf-8"><meta http-equiv="refresh" content="0;url=https://evil.example">', tmp_path)
    assert r.returncode == 1
    assert "HTML-03" in r.stdout


def _load_tool_module():
    spec = importlib.util.spec_from_file_location("verify_html_report", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_css_external_url_bare_scheme(tmp_path):
    r = run_html('<meta charset="utf-8"><style>body{background:url(http:evil.example/x.png)}</style>', tmp_path)
    assert r.returncode == 1
    assert "HTML-03" in r.stdout


def test_inline_style_bare_scheme_url(tmp_path):
    r = run_html('<meta charset="utf-8"><div style="background:url(https:evil.example/x.png)">x</div>', tmp_path)
    assert r.returncode == 1
    assert "HTML-03" in r.stdout


def test_secret_patterns_in_sync_with_md_verifier():
    # 배포본(tools/)은 tests/ 를 import 못 하므로 비밀키 패턴을 자체 보유한다(BL-25 ① 제약).
    # 두 곳이 드리프트하면 HTML 결과지의 비밀키 탐지가 .md 보다 약해지므로 동기화를 테스트로 고정.
    # bare import 가능 이유: pytest 가 테스트 파일 디렉터리(tests/)를 sys.path 에 넣어준다.
    # 도구는 tools/ 에 있지만 verify_report_format 은 tests/ 에 있어 이 import 가 해결된다.
    import verify_report_format as vrf
    tool = _load_tool_module()
    md = [(n, p.pattern) for n, p in vrf.SECRET_PATTERNS]
    html = [(n, p.pattern) for n, p in tool.SECRET_PATTERNS]
    assert html == md, "HTML 검증기와 .md 형식검증기의 비밀키 패턴이 드리프트했습니다"
