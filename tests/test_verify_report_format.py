"""verify_report_format.py 블랙박스 테스트 — 임시 파일을 만들어 subprocess로 실행한다."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "verify_report_format.py"


def _checkup_report(
    grade_line: str = "# 🟡 C — 주의가 필요해요",
    finding_block: str | None = None,
    homework_line: str = "숙제: DUP-01",
    found_line: str = "발견ID: DUP-01",
    version_line: str = "스킬 버전: v2.2.0 · 모드: 건강검진",
) -> str:
    if finding_block is None:
        finding_block = (
            "### 🔴 심각 1 [DUP-01] — 같은 코드가 3곳에 복사됨\n"
            "- **무슨 뜻인가요?** 한 곳을 고치면 나머지도 따로 고쳐야 합니다.\n"
            "- **어디?** `a.py`, `b.py`\n"
            "- **고치면?** 한 곳만 고치면 전체에 반영됩니다.\n"
            "- **승인 명령:** \"심각 1 실행해줘\"\n"
        )
    return (
        "# 🏥 프로젝트 건강검진 결과지 — 테스트\n\n"
        "```\n"
        "환자: 테스트 · 검진일: 2026-06-12 · 분석 파일: 3개\n"
        f"{version_line}\n"
        "```\n\n"
        "## 종합 판정\n\n"
        f"{grade_line}\n\n"
        "**의사 소견**: 손볼 곳이 있습니다.\n\n"
        "## 부위별 소견\n\n"
        "| 부위 | 판정 | 소견 |\n|------|------|------|\n"
        "| 구조 | 🟡 주의 (C) | 중복이 있어요 |\n\n"
        "## 오늘의 처방\n\n"
        "진단 결과: 🔴 심각 1건 · 🟡 권장 0건 · ⚪ 참고 0건\n"
        "👉 **당장 1건만 하신다면**: 심각 1\n\n"
        f"{finding_block}\n"
        "## 다음 진료 안내\n"
        "- 다음 검진은 언제쯤이 좋을까요?\n"
        f"{homework_line}\n\n"
        f"{found_line}\n"
    )


def _run(report: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(report)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _write_and_run(tmp_path: Path, text: str,
                   encoding: str = "utf-8") -> subprocess.CompletedProcess[str]:
    report = tmp_path / "report.md"
    report.write_text(text, encoding=encoding)
    return _run(report)


def test_valid_checkup_report_passes(tmp_path: Path) -> None:
    result = _write_and_run(tmp_path, _checkup_report())
    assert result.returncode == 0, result.stdout + result.stderr
    assert "통과" in result.stdout


def test_missing_version_line_fails(tmp_path: Path) -> None:
    result = _write_and_run(
        tmp_path, _checkup_report(version_line="모드: 건강검진"))
    assert result.returncode == 1
    assert "FORM-03" in result.stdout


def test_grade_label_mismatch_fails(tmp_path: Path) -> None:
    """고정표 위반: D인데 '양호해요'라고 적으면 미달."""
    result = _write_and_run(
        tmp_path, _checkup_report(grade_line="# 🔴 D — 양호해요"))
    assert result.returncode == 1
    assert "FORM-07" in result.stdout
    assert "고정표" in result.stdout


def test_last_line_not_id_block_fails(tmp_path: Path) -> None:
    """발견ID 블록이 맨 마지막 줄이 아니면 미달 (9절 계약)."""
    text = _checkup_report() + "\n추신: 좋은 하루 되세요.\n"
    result = _write_and_run(tmp_path, text)
    assert result.returncode == 1
    assert "FORM-05" in result.stdout


def test_malformed_id_fails(tmp_path: Path) -> None:
    result = _write_and_run(
        tmp_path, _checkup_report(found_line="발견ID: dup-1, DUP-01"))
    assert result.returncode == 1
    assert "FORM-06" in result.stdout


def test_four_fields_count_mismatch_fails(tmp_path: Path) -> None:
    """승인 명령 줄이 빠진 발견 항목 = 4요소 개수 불일치."""
    broken = (
        "### 🔴 심각 1 [DUP-01] — 중복\n"
        "- **무슨 뜻인가요?** 설명.\n"
        "- **어디?** `a.py`\n"
        "- **고치면?** 좋아집니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
        "### 🟡 권장 1 [DOC-01] — 문서 없음\n"
        "- **무슨 뜻인가요?** 설명.\n"
        "- **어디?** 프로젝트 루트\n"
        "- **고치면?** 좋아집니다.\n"
    )
    result = _write_and_run(
        tmp_path,
        _checkup_report(finding_block=broken,
                        found_line="발견ID: DUP-01, DOC-01"))
    assert result.returncode == 1
    assert "FORM-09" in result.stdout


def test_secret_value_exposure_fails(tmp_path: Path) -> None:
    """보고서 본문에 키 값을 옮겨 적으면 미달 (절대 규칙 4)."""
    leaky = (
        "### 🔴 심각 1 [SEC-01] — 비밀키 발견\n"
        "- **무슨 뜻인가요?** 키가 코드에 있습니다: AKIAIOSFODNN7EXAMPLE\n"
        "- **어디?** `config.py`\n"
        "- **고치면?** 환경 변수로 옮깁니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
    )
    result = _write_and_run(
        tmp_path,
        _checkup_report(finding_block=leaky, found_line="발견ID: SEC-01"))
    assert result.returncode == 1
    assert "FORM-11" in result.stdout
    # 위반 메시지가 키 전문을 다시 노출하지 않는다 (앞 8자만).
    assert "AKIAIOSFODNN7EXAMPLE" not in result.stdout


def test_missing_homework_fails_for_checkup(tmp_path: Path) -> None:
    result = _write_and_run(
        tmp_path, _checkup_report(homework_line="(숙제 줄 없음)"))
    assert result.returncode == 1
    assert "FORM-10" in result.stdout


def test_intro_chart_passes_without_grade(tmp_path: Path) -> None:
    """초진 차트는 종합 판정 생략 규칙 — 등급 없이도 통과."""
    text = (
        "# 🏥 프로젝트 초진 차트 — 테스트\n\n"
        "```\n"
        "환자: 테스트 · 검진일: 2026-06-12 · 분석 파일: 3개\n"
        "스킬 버전: v2.2.0 · 모드: 초진 차트\n"
        "```\n\n"
        "정밀 등급은 checkup에서 확인하세요.\n\n"
        "## 프로젝트 지도\n\n내용...\n\n"
        "발견ID: (없음)\n"
    )
    result = _write_and_run(tmp_path, text)
    assert result.returncode == 0, result.stdout + result.stderr


def test_zero_findings_skips_four_fields(tmp_path: Path) -> None:
    """발견 0건이면 4요소 라벨이 없어도 통과."""
    result = _write_and_run(
        tmp_path,
        _checkup_report(finding_block="**잘 유지되고 있는 점**: 깔끔합니다.\n",
                        found_line="발견ID: (없음)",
                        homework_line="숙제: (없음)"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_v1_report_without_homework_passes(tmp_path: Path) -> None:
    """숙제 줄은 v2.0부터의 계약 — v1.x 보고서(공개판)는 없어도 통과."""
    result = _write_and_run(
        tmp_path,
        _checkup_report(homework_line="(v1에는 숙제 줄 없음)",
                        version_line="스킬 버전: v1.2.0 · 모드: 건강검진"))
    assert result.returncode == 0, result.stdout + result.stderr


def test_bom_utf8_report_is_readable(tmp_path: Path) -> None:
    """PowerShell 5.1(Set-Content)이 만드는 BOM 붙은 UTF-8 보고서도 검사된다."""
    result = _write_and_run(tmp_path, _checkup_report(), encoding="utf-8-sig")
    assert result.returncode == 0, result.stdout + result.stderr
