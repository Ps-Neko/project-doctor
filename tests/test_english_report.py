"""English report contract regression tests."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERIFY = HERE / "verify_report_format.py"
COMPARE = HERE / "compare_report.py"
KO_GOLDEN = HERE / "golden" / "checkup-report.md"
EN_GOLDEN = HERE / "golden" / "checkup-report-en.md"
EXPECTED = HERE / "fixtures" / "messy-project" / "EXPECTED.md"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def _found_ids(path: Path) -> list[str]:
    found = [
        line.strip().split(":", 1)[1].strip()
        for line in _lines(path)
        if line.strip().startswith("발견ID:")
    ]
    assert found, f"{path} has no machine ID line"
    if found[-1] == "(없음)":
        return []
    return [part.strip() for part in found[-1].split(",")]


def _grade(path: Path) -> str:
    for line in _lines(path):
        stripped = line.strip()
        if stripped.startswith("# ") and " — " in stripped:
            for part in stripped.split():
                if part in {"A", "B", "C", "D"}:
                    return part
    raise AssertionError(f"{path} has no grade heading")


def test_english_golden_verify_report_format_passes() -> None:
    result = _run([str(VERIFY), str(EN_GOLDEN)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "위반: 0건" in result.stdout


def test_english_golden_scores_messy_expected_at_100_percent() -> None:
    result = _run([str(COMPARE), str(EN_GOLDEN), str(EXPECTED)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "탐지율: 100.0% (14/14)" in result.stdout
    assert "오탐 ID(정답지·채점 중립에 없음): (없음)" in result.stdout


def test_english_report_rejects_homework_alias(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(
        EN_GOLDEN.read_text(encoding="utf-8").replace(
            "숙제: DUP-01", "숙제(Homework): DUP-01"
        ),
        encoding="utf-8",
    )

    result = _run([str(VERIFY), str(report)])

    assert result.returncode == 1
    assert "FORM-10" in result.stdout


def test_english_report_rejects_none_alias(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text(
        EN_GOLDEN.read_text(encoding="utf-8").replace(
            "발견ID: DUP-01, DEAD-01, DEAD-02, BIG-01, BIG-02, BIG-03, "
            "HARD-01, HARD-02, HARD-03, DOC-01, DOC-03, TEST-01, TMP-01, "
            "STALE-01, STALE-02",
            "발견ID: (none)",
        ),
        encoding="utf-8",
    )

    result = _run([str(VERIFY), str(report)])

    assert result.returncode == 1
    assert "FORM-06" in result.stdout or "FORM-09" in result.stdout


@pytest.mark.parametrize(
    ("path", "required"),
    [
        (
            KO_GOLDEN,
            [
                "환자:",
                "## 종합 판정",
                "## 부위별 소견",
                "## 오늘의 처방",
                "## 부록",
                "## 다음 진료 안내",
            ],
        ),
        (
            EN_GOLDEN,
            [
                "Patient:",
                "## Overall Assessment",
                "## Findings by Area",
                "## Today's Prescription",
                "## Appendix",
                "## Next Visit",
            ],
        ),
    ],
)
def test_golden_reports_have_expected_sections(path: Path, required: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for marker in required:
        assert marker in text


def test_english_and_korean_golden_reports_have_structural_parity() -> None:
    assert _found_ids(EN_GOLDEN) == _found_ids(KO_GOLDEN)
    assert _grade(EN_GOLDEN) == _grade(KO_GOLDEN) == "D"