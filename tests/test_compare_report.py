"""compare_report.py 블랙박스 테스트 — 임시 파일을 만들어 subprocess로 실행한다."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "compare_report.py"


def _expected_md(ids: list[str], neutral_lines: list[str] | None = None) -> str:
    rows = "\n".join(f"| {i} | 어딘가 | 🟡 |" for i in ids)
    text = (
        "# EXPECTED.md — 테스트용 정답지\n\n"
        '이 파일은 "프로젝트 주치의" 스킬 자체 테스트의 정답지다.\n\n'
        "## 심은 문제 (테스트)\n\n"
        "| ID | 위치 | 심각도 |\n|----|------|--------|\n" + rows + "\n"
    )
    if neutral_lines:
        text += ("\n## 추가 보고 허용 (채점 중립)\n\n"
                 + "\n".join(f"- {ln}" for ln in neutral_lines) + "\n")
    return text


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


def test_unknown_extra_id_fails_as_false_positive(tmp_path: Path) -> None:
    """정답지·채점 중립 어디에도 없는 ID 보고 = 오탐 → 탐지율 100%여도 미달."""
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01", "A-02"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01, A-02, Z-99"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 1
    assert "Z-99" in result.stdout
    assert "오탐" in result.stdout
    assert "미달" in result.stdout


def test_neutral_extra_id_passes(tmp_path: Path) -> None:
    """채점 중립 목록에 있는 추가 보고는 허용 — 보고돼도 통과, 빠져도 감점 없음."""
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(
        _expected_md(["A-01", "A-02"], neutral_lines=["Z-99 — 정당한 추가 발견"]),
        encoding="utf-8",
    )
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01, A-02, Z-99"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Z-99" in result.stdout
    assert "통과" in result.stdout


def test_neutral_line_takes_first_id_only(tmp_path: Path) -> None:
    """중립 줄의 설명에 다른 ID가 등장해도 그 줄의 중립 ID는 첫 번째 하나뿐."""
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(
        _expected_md(["A-01"], neutral_lines=["B-02 — A-01(중복)의 부산물로 반복됨"]),
        encoding="utf-8",
    )
    # B-02는 중립이라 통과, 하지만 같은 줄에 언급된 C-03은 중립이 아니므로 오탐.
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01, B-02, C-03"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 1
    assert "C-03" in result.stdout


def test_revisit_lines_parsed_and_printed(tmp_path: Path) -> None:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(
        "# 보고서\n\n## 다음 진료 안내\n비교: 해결 1 / 그대로 12 / 신규 2 / 악화 0\n"
        "숙제: HARD-01\n\n발견ID: A-01\n",
        encoding="utf-8",
    )
    result = _run(report, expected)
    assert result.returncode == 0
    assert "해결 1 / 그대로 12" in result.stdout
    assert "HARD-01" in result.stdout


def test_no_revisit_lines_is_silent(tmp_path: Path) -> None:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0
    assert "재방문 비교" not in result.stdout
    assert "숙제(참고용)" not in result.stdout


def test_bom_utf8_report_is_readable(tmp_path: Path) -> None:
    """PowerShell 5.1(Set-Content)이 만드는 BOM 붙은 UTF-8 보고서도 채점된다."""
    expected = tmp_path / "EXPECTED.md"
    expected.write_text(_expected_md(["A-01"]), encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text(_report_md("발견ID: A-01"), encoding="utf-8-sig")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout + result.stderr


def test_utf8_korean_path_and_content(tmp_path: Path) -> None:
    folder = tmp_path / "한글 경로 테스트"
    folder.mkdir()
    expected = folder / "EXPECTED.md"
    expected.write_text(_expected_md(["DUP-01"]), encoding="utf-8")
    report = folder / "보고서.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0


# --- 코드 리뷰 회귀 테스트 (v1.5.2: 파싱 견고성) ---

def _write_expected(tmp_path: Path, body: str) -> Path:
    expected = tmp_path / "EXPECTED.md"
    expected.write_text("# 정답지\n\n" + body, encoding="utf-8")
    return expected


def test_id_in_second_column(tmp_path: Path) -> None:
    """ID가 1열이 아니어도(위치|ID|심각도) 헤더 위치로 올바로 읽는다."""
    expected = _write_expected(
        tmp_path,
        "## 심은 문제 (테스트)\n\n| 위치 | ID | 심각도 |\n|------|----|--------|\n"
        "| a.py | DUP-01 | 🔴 |\n| b.py | DOC-01 | 🟡 |\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01, DOC-01"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout
    assert "100.0%" in result.stdout


def test_guid_header_not_mistaken_for_id(tmp_path: Path) -> None:
    """헤더에 'GUID' 함정 셀이 있어도 정확히 'ID' 열만 잡는다."""
    expected = _write_expected(
        tmp_path,
        "## 심은 문제 (테스트)\n\n| GUID | ID | 심각도 |\n|------|----|--------|\n"
        "| g-1 | DUP-01 | 🔴 |\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    assert _run(report, expected).returncode == 0


def test_fullwidth_pipe_table(tmp_path: Path) -> None:
    """전각 파이프(｜)로 그린 표도 채점된다 (한국어 환경 손편집)."""
    expected = _write_expected(
        tmp_path,
        "## 심은 문제 (테스트)\n\n｜ ID ｜ 위치 ｜\n｜----｜------｜\n｜ DUP-01 ｜ a.py ｜\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    assert _run(report, expected).returncode == 0


def test_backtick_id_cell(tmp_path: Path) -> None:
    """ID 셀이 백틱(`DUP-01`)으로 감싸여도 채점된다."""
    expected = _write_expected(
        tmp_path,
        "## 심은 문제 (테스트)\n\n| ID | 위치 |\n|----|------|\n| `DUP-01` | a.py |\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    assert _run(report, expected).returncode == 0


def test_space_in_header(tmp_path: Path) -> None:
    """헤더가 '발견 ID'(공백 포함)여도 ID 열로 인식한다."""
    expected = _write_expected(
        tmp_path,
        "## 심은 문제 (테스트)\n\n| 발견 ID | 위치 |\n|---------|------|\n| DUP-01 | a.py |\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    assert _run(report, expected).returncode == 0


def test_two_tables_same_heading(tmp_path: Path) -> None:
    """같은 '## 심은 문제' 절에 표가 둘이어도 둘째 표를 오염 없이 읽는다(id_col 리셋)."""
    expected = _write_expected(
        tmp_path,
        "## 심은 문제 (테스트)\n\n| ID | 위치 |\n|----|------|\n| DUP-01 | a.py |\n\n"
        "설명 문단.\n\n| 위치 | ID |\n|------|----|\n| b.py | DOC-01 |\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01, DOC-01"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout
    assert "100.0%" in result.stdout  # '위치'·'b.py'가 가짜 ID로 분모를 부풀리지 않음


def test_fenced_example_id_ignored(tmp_path: Path) -> None:
    """보고서 끝 코드펜스 예시 발견ID는 채점에서 무시하고 펜스 밖 실제 줄을 쓴다."""
    expected = _write_expected(tmp_path, _expected_md(["DUP-01", "DOC-01"]))
    report = tmp_path / "r.md"
    report.write_text(
        "# 보고서\n발견ID: DUP-01, DOC-01\n\n부록 예시:\n```\n발견ID: 예시-99\n```\n",
        encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout
    assert "100.0%" in result.stdout


def test_empty_expected_table_errors(tmp_path: Path) -> None:
    """정답지 표가 비면 ZeroDivision 없이 친절한 오류로 떨어진다."""
    expected = _write_expected(tmp_path, "## 심은 문제 (테스트)\n\n(표 없음)\n")
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 1
    assert "찾지 못했습니다" in result.stdout


def test_neutral_iso_token_not_mistaken(tmp_path: Path) -> None:
    """채점 중립 줄에 ISO-8601이 앞서 와도 진짜 ID(HARD-02)를 중립으로 인정한다."""
    expected = _write_expected(
        tmp_path,
        _expected_md(["DUP-01"], neutral_lines=["ISO-8601 형식 관련 HARD-02 허용"]))
    report = tmp_path / "r.md"
    report.write_text(_report_md("발견ID: DUP-01, HARD-02"), encoding="utf-8")
    result = _run(report, expected)
    assert result.returncode == 0, result.stdout  # HARD-02가 중립 → 오탐 아님
