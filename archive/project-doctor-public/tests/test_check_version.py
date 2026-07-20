"""check_version.main() — 핵심문서 버전 줄 삭제 차단 회귀 (외부 평가 7차 P2a 미러).

dev v2.7.9에서 main()이 MISSING(마커/파일 부재)도 실패로 집계하도록 바뀐 것을 공개판에 반영.
이 파일은 main()의 행동만 검사한다 — find_version 내부는 건드리지 않는다.
"""
from pathlib import Path

import check_version as cv


def _w(d: Path, name: str, text: str) -> None:
    (d / name).write_text(text, encoding="utf-8")


def _stage_repo(tmp_path: Path, monkeypatch, root_readme: str) -> None:
    """tmp_path에 가짜 레포(SKILL/루트README/스킬README/CHANGELOG)를 깔고 모듈 경로를 그쪽으로 돌린다.
    SKILL은 모듈 로드 시 상수로 고정되므로 ROOT(checks 경로 계산용)와 함께 둘 다 패치한다."""
    _w(tmp_path, "SKILL.md", "스킬 버전: **v9.9.9** — 본문\n")
    _w(tmp_path, "README.md", root_readme)
    sk = tmp_path / "skills" / "project-doctor"
    sk.mkdir(parents=True)
    _w(sk, "README.md", "현재 버전: v9.9.9\n")
    _w(sk, "CHANGELOG.md", "## v9.9.9 — x\n")
    monkeypatch.setattr(cv, "ROOT", tmp_path)
    monkeypatch.setattr(cv, "SKILL", tmp_path / "SKILL.md")


def test_main_fails_when_core_doc_marker_deleted(tmp_path: Path, monkeypatch) -> None:
    # 핵심문서(루트 README)의 '현재 버전:' 줄을 통째 삭제 → main() 실패(7차 평가 P2a).
    _stage_repo(tmp_path, monkeypatch, root_readme="제목만 있고 버전 표기가 없는 문서\n")
    assert cv.main() == 1


def test_main_passes_when_all_markers_present(tmp_path: Path, monkeypatch) -> None:
    # 정상(모든 마커 동일 버전)은 그대로 통과 — false-fail 회귀 방지.
    _stage_repo(tmp_path, monkeypatch, root_readme="현재 버전: **v9.9.9** — 본문\n")
    assert cv.main() == 0
