"""check_version.find_version 단위 테스트 — MISSING/BROKEN/정상/깨진-최신 4분기.

find_version은 '마커가 든 첫 줄'에서 판정을 확정한다. CHANGELOG처럼 마커(## v)가 여러 줄에
걸쳐 있을 때, 최신(첫) 헤딩이 깨졌으면 그 아래 과거 정상 헤딩으로 새지 않고 BROKEN으로 잡아야 한다.
"""
from pathlib import Path

import check_version as cv


def _w(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_normal_version(tmp_path: Path) -> None:
    p = _w(tmp_path, "SKILL.md", "스킬 버전: **v2.7.5** — 본문.\n")
    assert cv.find_version(p, "스킬 버전:") == "2.7.5"


def test_missing_marker_is_missing(tmp_path: Path) -> None:
    p = _w(tmp_path, "README.md", "버전 표기가 전혀 없는 문서.\n")
    assert cv.find_version(p, "현재 버전:") is cv.MISSING


def test_missing_file_is_missing(tmp_path: Path) -> None:
    assert cv.find_version(tmp_path / "없는파일.md", "현재 버전:") is cv.MISSING


def test_broken_version_line_is_broken(tmp_path: Path) -> None:
    # 마커는 살아 있는데 vX.Y.Z 파싱 실패 = 가장 위험한 드리프트 → BROKEN.
    p = _w(tmp_path, "README.md", "현재 버전: 미정 (작업 중)\n")
    assert cv.find_version(p, "현재 버전:") is cv.BROKEN


def test_broken_latest_changelog_not_skipped(tmp_path: Path) -> None:
    # 최신(첫) ## v 헤딩이 깨졌으면 그 아래 과거 정상 헤딩(v2.0.0)으로 새지 않고 BROKEN으로 잡는다.
    p = _w(tmp_path, "CHANGELOG.md",
           "# 변경 이력\n\n## v미정 — 작업 중\n- wip\n\n## v2.0.0 — 2026-01-01\n- old\n")
    assert cv.find_version(p, "## v") is cv.BROKEN


def test_latest_changelog_returned(tmp_path: Path) -> None:
    # 정상일 때는 최신(첫) 헤딩의 버전을 돌려준다.
    p = _w(tmp_path, "CHANGELOG.md", "# 변경 이력\n\n## v2.7.5 — x\n\n## v2.7.4 — y\n")
    assert cv.find_version(p, "## v") == "2.7.5"


def _stage_repo(tmp_path: Path, monkeypatch, root_readme: str) -> None:
    """tmp_path에 가짜 레포(SKILL/루트README/스킬README/CHANGELOG)를 깔고 모듈 경로를 그쪽으로 돌린다.
    SKILL은 모듈 로드 시 상수로 고정되므로 ROOT(checks 경로 계산용)와 함께 둘 다 패치한다."""
    _w(tmp_path, "SKILL.md", "스킬 버전: **v9.9.9** — 본문\n")
    _w(tmp_path, "README.md", root_readme)
    sk = tmp_path / "skills" / "project-doctor"
    sk.mkdir(parents=True)
    (sk / "README.md").write_text("현재 버전: v9.9.9\n", encoding="utf-8")
    (sk / "CHANGELOG.md").write_text("## v9.9.9 — x\n", encoding="utf-8")
    # 골든 보고서도 표지에 '스킬 버전:'을 인쇄하고 버전 정합 검사 대상이다(8차 평가 P0) — 가짜 레포에도 깐다.
    gold = tmp_path / "tests" / "golden"
    gold.mkdir(parents=True)
    (gold / "checkup-report.md").write_text("스킬 버전: v9.9.9 · 모드: 건강검진\n", encoding="utf-8")
    (gold / "checkup-report.html").write_text(
        '<p class="meta">스킬 버전: v9.9.9 · 모드: 건강검진</p>\n', encoding="utf-8")
    monkeypatch.setattr(cv, "ROOT", tmp_path)
    monkeypatch.setattr(cv, "SKILL", tmp_path / "SKILL.md")


def test_main_fails_when_core_doc_marker_deleted(tmp_path: Path, monkeypatch) -> None:
    # 핵심문서(루트 README)의 '현재 버전:' 줄을 통째 삭제 → main() 실패(7차 평가 P2a).
    # 마커 줄을 지우면 CI가 통과하던 false-pass 를 막는다.
    _stage_repo(tmp_path, monkeypatch, root_readme="제목만 있고 버전 표기가 없는 문서\n")
    assert cv.main() == 1


def test_main_passes_when_all_markers_present(tmp_path: Path, monkeypatch) -> None:
    # 정상(모든 마커 동일 버전)은 그대로 통과 — MISSING=실패 전환의 false-fail 회귀 방지.
    _stage_repo(tmp_path, monkeypatch, root_readme="현재 버전: **v9.9.9** — 본문\n")
    assert cv.main() == 0
