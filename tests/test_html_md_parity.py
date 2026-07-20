"""check_html_md_parity.py — HTML 결과지 ↔ .md 정본 내용 동기화 검사 테스트.

골든 쌍(tests/golden/checkup-report.md ↔ .html)이 같은 발견ID·버전·판정을 담는지,
그리고 한쪽이 어긋나면 미달이 나는지를 블랙박스(subprocess)로 검증한다.
두 골든은 같은 검진 1건의 형식 변형이어야 한다 — 한쪽만 갱신하면 이 회귀가 깨진다.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARITY = HERE / "check_html_md_parity.py"
GOLDEN_MD = HERE / "golden" / "checkup-report.md"
GOLDEN_HTML = HERE / "golden" / "checkup-report.html"
HTML_SECURITY_TOOL = (HERE.parent / "skills" / "project-doctor" / "tools"
                      / "verify_html_report.py")


def run_parity(md: Path, html: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PARITY), str(md), str(html)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def run_parity_with_html_text(md: Path, html_text: str, tmp_path: Path) -> subprocess.CompletedProcess:
    f = tmp_path / "tampered.html"
    f.write_text(html_text, encoding="utf-8")
    return run_parity(md, f)


def test_golden_pair_passes():
    r = run_parity(GOLDEN_MD, GOLDEN_HTML)
    assert r.returncode == 0, r.stdout
    assert "통과" in r.stdout


def test_missing_finding_id_detected(tmp_path):
    # HTML에서 DUP-01 자취를 모두 지우면 정본(.md)이 기대하는 발견ID가 빠진다.
    tampered = GOLDEN_HTML.read_text(encoding="utf-8").replace("DUP-01", "ZZZ-99")
    r = run_parity_with_html_text(GOLDEN_MD, tampered, tmp_path)
    assert r.returncode == 1
    assert "DUP-01" in r.stdout


def test_missing_version_detected(tmp_path):
    tampered = GOLDEN_HTML.read_text(encoding="utf-8").replace("v2.8.0", "v9.9.9")
    r = run_parity_with_html_text(GOLDEN_MD, tampered, tmp_path)
    assert r.returncode == 1
    assert "v2.8.0" in r.stdout


def test_missing_grade_label_detected(tmp_path):
    tampered = GOLDEN_HTML.read_text(encoding="utf-8").replace("치료가 필요해요", "건강해요")
    r = run_parity_with_html_text(GOLDEN_MD, tampered, tmp_path)
    assert r.returncode == 1
    assert "치료가 필요해요" in r.stdout


def test_title_only_value_is_not_counted_as_present(tmp_path):
    # 가시 텍스트 정의: 본문엔 없고 <title>(머리말)에만 있는 값은 '있다'고 판정되면 안 된다.
    # 종합 판정 라벨을 본문에선 다른 라벨로 바꿔 지우고, <title>에만 심은 HTML → 미달이어야 한다.
    # (head/title을 추출에서 제외하지 않던 구버전 추출기에선 이 케이스가 거짓 통과했다.)
    original = GOLDEN_HTML.read_text(encoding="utf-8")
    body_removed = original.replace("치료가 필요해요", "양호해요")
    tampered = body_removed.replace(
        "<title>프로젝트 건강검진 결과지 — messy-project</title>",
        "<title>프로젝트 건강검진 결과지 — messy-project · 치료가 필요해요</title>",
    )
    # 본문에서 라벨이 실제로 사라지고 title로만 옮겨졌는지 확인(테스트 자체의 전제 검증).
    assert "<title>" in tampered and "치료가 필요해요" in tampered
    r = run_parity_with_html_text(GOLDEN_MD, tampered, tmp_path)
    assert r.returncode == 1, r.stdout
    assert "치료가 필요해요" in r.stdout


def test_golden_html_also_passes_security():
    # 정본 쌍 HTML은 내용 충실성(parity)뿐 아니라 보안 검증기(verify_html_report)도 통과해야 한다 —
    # 사용자가 실제로 받아보는 산출물이므로 둘 다 만족해야 의미가 있다.
    r = subprocess.run(
        [sys.executable, str(HTML_SECURITY_TOOL), str(GOLDEN_HTML)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert r.returncode == 0, r.stdout
    assert "통과" in r.stdout


def test_usage_no_args():
    r = subprocess.run([sys.executable, str(PARITY)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 1
    assert "사용법" in r.stdout


def test_read_error_missing_file(tmp_path):
    r = run_parity(GOLDEN_MD, tmp_path / "nope.html")
    assert r.returncode == 1
    assert "읽을 수 없습니다" in r.stdout
