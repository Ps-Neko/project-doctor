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


def test_fenced_only_found_id_is_not_a_machine_line(tmp_path: Path) -> None:
    """발견ID를 코드펜스로만 감싸면(raw 줄 없음) 실제 기계 판독 줄로 인정되지 않아 FORM-05.

    이전에는 fenced 발견ID를 통과시켰으나, 채점기(compare_report)는 펜스 안을 무시해
    같은 보고서를 0% 처리하던 계약 불일치가 있었다. 실제 산출 보고서는 raw line이므로
    verify도 raw-only로 통일한다(P1-A)."""
    result = _write_and_run(
        tmp_path, _checkup_report(found_line="```\n발견ID: DUP-01\n```"))
    assert result.returncode == 1
    assert "FORM-05" in result.stdout


def test_finding_title_without_catalog_id_fails(tmp_path: Path) -> None:
    """발견 항목 제목에 카탈로그 [ID]가 없으면 미달 (5절 계약 — 재검진·승인 명령 추적의 토대)."""
    block = (
        "### 🔴 심각 1 — 같은 코드가 3곳에 복사됨\n"
        "- **무슨 뜻인가요?** 한 곳을 고치면 나머지도 따로 고쳐야 합니다.\n"
        "- **어디?** `a.py`, `b.py`\n"
        "- **고치면?** 한 곳만 고치면 전체에 반영됩니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
    )
    result = _write_and_run(tmp_path, _checkup_report(finding_block=block))
    assert result.returncode == 1
    assert "FORM-09" in result.stdout


def test_fenced_homework_does_not_satisfy_contract(tmp_path: Path) -> None:
    """코드펜스 안 예시 숙제 줄은 실제 숙제 줄을 대신하지 못한다 (FORM-10, P2-B)."""
    result = _write_and_run(
        tmp_path, _checkup_report(homework_line="```\n숙제: DUP-01\n```"))
    assert result.returncode == 1
    assert "FORM-10" in result.stdout


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


# --- 코드 리뷰 회귀 테스트 (v1.5.2: 펜스 우회·비밀키·표지·인코딩) ---

def test_fenced_grade_example_does_not_mask_violation(tmp_path: Path) -> None:
    """펜스 안 올바른 등급 예시가 펜스 밖 잘못된 실제 등급을 가리지 못한다."""
    grade = "```markdown\n# 🟢 A — 건강해요\n```\n# 🔴 D — 양호해요"
    result = _write_and_run(tmp_path, _checkup_report(grade_line=grade))
    assert result.returncode == 1
    assert "FORM-07" in result.stdout


def test_multiple_found_id_lines_fail(tmp_path: Path) -> None:
    """실제 발견ID 줄 + 부록 펜스 예시 발견ID = 2개 → FORM-05."""
    text = _checkup_report() + "\n부록:\n```\n발견ID: DUP-01\n```\n"
    result = _write_and_run(tmp_path, text)
    assert result.returncode == 1
    assert "FORM-05" in result.stdout


def test_github_token_variable_length_caught(tmp_path: Path) -> None:
    """36자가 아닌 GitHub 토큰(40자)도 비밀키 노출로 잡는다."""
    leaky = (
        "### 🔴 심각 1 [SEC-01] — 토큰\n"
        "- **무슨 뜻인가요?** 토큰: ghp_" + "a" * 40 + "\n"
        "- **어디?** `c.py`\n- **고치면?** 옮깁니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
    )
    result = _write_and_run(
        tmp_path, _checkup_report(finding_block=leaky, found_line="발견ID: SEC-01"))
    assert result.returncode == 1
    assert "FORM-11" in result.stdout


def test_google_api_key_caught(tmp_path: Path) -> None:
    """Google API 키(AIza...)도 비밀키 노출로 잡는다."""
    leaky = (
        "### 🔴 심각 1 [SEC-01] — 키\n"
        "- **무슨 뜻인가요?** 키: AIza" + "B" * 35 + "\n"
        "- **어디?** `c.py`\n- **고치면?** 옮깁니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
    )
    result = _write_and_run(
        tmp_path, _checkup_report(finding_block=leaky, found_line="발견ID: SEC-01"))
    assert result.returncode == 1
    assert "FORM-11" in result.stdout


def test_missing_body_section_fails(tmp_path: Path) -> None:
    """부위별 소견 절을 제거하면 FORM-08."""
    text = _checkup_report().replace(
        "## 부위별 소견\n\n"
        "| 부위 | 판정 | 소견 |\n|------|------|------|\n"
        "| 구조 | 🟡 주의 (C) | 중복이 있어요 |\n\n", "")
    result = _write_and_run(tmp_path, text)
    assert result.returncode == 1
    assert "FORM-08" in result.stdout


def test_missing_title_fails(tmp_path: Path) -> None:
    """표지 제목 헤딩이 모드 제목이 아니면 FORM-01."""
    text = _checkup_report().replace(
        "# 🏥 프로젝트 건강검진 결과지 — 테스트\n\n", "# 무언가\n\n")
    result = _write_and_run(tmp_path, text)
    assert result.returncode == 1
    assert "FORM-01" in result.stdout


def test_findings_present_but_id_none_fails(tmp_path: Path) -> None:
    """본문에 발견 항목이 있는데 발견ID:(없음)이면 모순 → FORM-09."""
    result = _write_and_run(
        tmp_path, _checkup_report(found_line="발견ID: (없음)",
                                  homework_line="숙제: (없음)"))
    assert result.returncode == 1
    assert "FORM-09" in result.stdout


def test_non_utf8_report_no_traceback(tmp_path: Path) -> None:
    """cp949(비UTF-8, 한국어 Windows 기본)로 저장된 보고서도 트레이스백 없이 처리한다."""
    report = tmp_path / "report.md"
    report.write_bytes("# 프로젝트 건강검진 결과지\n환자: 테스트\n발견ID: (없음)\n".encode("cp949"))
    result = _run(report)
    assert "Traceback" not in (result.stdout + result.stderr)
    assert result.returncode in (0, 1)  # 미달일 수 있으나 크래시는 아님


# --- FORM-12: 사람용 본문/부록 ↔ 기계 발견ID 블록 양방향 ID 일치 (9절 line 164 계약) ---

def test_machine_id_not_in_body_fails(tmp_path: Path) -> None:
    """발견ID 줄에 있으나 본문·부록 어디에도 발견 항목이 없는 ID는 FORM-12 (9절 — 모든 발견 ID 빠짐없이).

    발견ID: DUP-01, DUP-02 인데 본문에는 [DUP-01] 항목만 있으면, DUP-02는 사람이 읽을
    근거가 어디에도 없는데 채점기(compare_report)는 '찾았다'고 집계하게 되는 불일치다."""
    result = _write_and_run(
        tmp_path, _checkup_report(found_line="발견ID: DUP-01, DUP-02"))
    assert result.returncode == 1
    assert "FORM-12" in result.stdout
    assert "DUP-02" in result.stdout


def test_body_id_not_in_machine_fails(tmp_path: Path) -> None:
    """본문 발견 항목 제목에 있으나 발견ID 줄에서 누락된 ID는 FORM-12.

    본문에 [DUP-01]·[DOC-01] 두 항목이 있는데 발견ID 줄이 DUP-01만 담으면, 채점기는
    DOC-01을 '안 찾음'으로 처리해 탐지율이 실제보다 낮게 나온다."""
    two = (
        "### 🔴 심각 1 [DUP-01] — 중복\n"
        "- **무슨 뜻인가요?** 설명.\n"
        "- **어디?** `a.py`\n"
        "- **고치면?** 좋아집니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
        "### 🔴 심각 2 [DOC-01] — 문서 없음\n"
        "- **무슨 뜻인가요?** 설명.\n"
        "- **어디?** 프로젝트 루트\n"
        "- **고치면?** 좋아집니다.\n"
        "- **승인 명령:** \"심각 2 실행해줘\"\n"
    )
    result = _write_and_run(
        tmp_path, _checkup_report(finding_block=two, found_line="발견ID: DUP-01"))
    assert result.returncode == 1
    assert "FORM-12" in result.stdout
    assert "DOC-01" in result.stdout


def test_appendix_id_satisfies_machine_block(tmp_path: Path) -> None:
    """부록(## 부록...)에 한 줄로 나열된 발견 ID도 발견ID 줄과 정합하면 FORM-12를 내지 않는다.

    압도 방지(7절): 발견 10건 초과 시 본문엔 일부만 ### 항목으로 싣고 나머지는 부록에
    'ID·제목 한 줄'로 나열한다. 발견ID 줄은 본문·부록 구분 없이 전부 담으므로(9절),
    부록에만 있는 ID도 본문 집합의 일부로 인정돼야 한다 — 거짓양성 방어."""
    block = (
        "### 🔴 심각 1 [DUP-01] — 중복\n"
        "- **무슨 뜻인가요?** 설명.\n"
        "- **어디?** `a.py`\n"
        "- **고치면?** 좋아집니다.\n"
        "- **승인 명령:** \"심각 1 실행해줘\"\n"
        "\n## 부록: 나머지 발견 항목\n"
        "- ⚪ [BIG-02] 거대 함수 — `main.py`의 process_orders 약 70줄\n"
    )
    result = _write_and_run(
        tmp_path,
        _checkup_report(finding_block=block, found_line="발견ID: DUP-01, BIG-02"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FORM-12" not in result.stdout
