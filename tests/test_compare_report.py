"""compare_report.py 블랙박스 테스트 — 임시 파일을 만들어 subprocess로 실행한다."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "compare_report.py"


def _expected_md(ids: list[str]) -> str:
    rows = "\n".join(f"| {i} | 어딘가 | 🟡 |" for i in ids)
    return (
        "# EXPECTED.md — 테스트용 정답지\n\n"
        '이 파일은 "프로젝트 주치의" 스킬 자체 테스트의 정답지다.\n\n'
        "## 심은 문제 (테스트)\n\n"
        "| ID | 위치 | 심각도 |\n|----|------|--------|\n" + rows + "\n"
    )


def _report_md(found_line: str) -> str:
    return f"# 진단 보고서 — 테스트\n\n본문...\n\n{found_line}\n"


def _run(report: Path, expected: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(report), str(expected)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_pass_at_80_percent(tmp_path: Path) -> None:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01", "A-02", "A-03", "A-04", "A-05"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01, A-02, A-03, A-04"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "80" in result.stdout


def test_fail_below_80_percent(tmp_path: Path) -> None:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01", "A-02", "A-03", "A-04", "A-05"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01, A-02"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 1


def test_none_found(tmp_path: Path) -> None:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: (없음)"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 1


def test_extra_ids_reported_but_not_counted(tmp_path: Path) -> None:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01", "A-02"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01, A-02, Z-99"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0
    assert "Z-99" in result.stdout


def test_utf8_korean_path_and_content(tmp_path: Path) -> None:
    folder = tmp_path / "한글 경로 테스트"
    folder.mkdir()
    expected = folder / "EXPECTED.md"
    expected.write_text(_expected_md(["DUP-01"]), encoding="utf-8")
    report = folder / "보고서.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0
