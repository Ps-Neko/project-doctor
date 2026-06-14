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
