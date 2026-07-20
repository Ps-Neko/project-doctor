"""run_checks (E2E 묶음 러너) 종료코드 합성·게이트 선택 테스트.

정답지 유무로 1게이트(형식만)/3게이트(형식+채점+위치)가 갈리고, 하나라도 실패하면
종합이 1이 되는 OR 합성을 검증한다(서브프로세스로 실제 검사기를 돈다).
"""
from pathlib import Path

import run_checks

TESTS = Path(__file__).resolve().parent
GOLDEN = TESTS / "golden" / "checkup-report.md"
LEAKY_GOLDEN = TESTS / "golden" / "leaky-report.md"
MESSY_EXPECTED = TESTS / "fixtures" / "messy-project" / "EXPECTED.md"
LEAKY_EXPECTED = TESTS / "fixtures" / "leaky-project" / "EXPECTED.md"


def test_usage_error_wrong_argc() -> None:
    assert run_checks.main(["prog"]) == 1  # 인자 부족


def test_missing_report_returns_1(tmp_path: Path) -> None:
    assert run_checks.main(["prog", str(tmp_path / "없는보고서.md")]) == 1


def test_format_only_passes_for_golden() -> None:
    # 정답지 없이 보고서만 → 형식 게이트 1개만 실행, golden은 통과 → 0.
    assert run_checks.main(["prog", str(GOLDEN)]) == 0


def test_all_three_gates_pass_for_golden() -> None:
    # 형식+채점+위치 3게이트 모두 golden + 짝 정답지로 통과 → 0.
    assert run_checks.main(["prog", str(GOLDEN), str(MESSY_EXPECTED)]) == 0


def test_partial_failure_returns_1() -> None:
    # golden(=messy 보고서)에 엉뚱한 정답지(leaky) → 채점·위치 게이트 실패 → 종합 1 (OR 합성).
    assert run_checks.main(["prog", str(GOLDEN), str(LEAKY_EXPECTED)]) == 1


def test_leaky_golden_three_gates_pass() -> None:
    # 보안 픽스처(leaky) 골든 — SEC/PII 발견 + 위치(app.py·config.js·notes.md)까지 3게이트 통과(8차 평가 P2).
    assert run_checks.main(["prog", str(LEAKY_GOLDEN), str(LEAKY_EXPECTED)]) == 0
