"""check_write_boundary.py (쓰기 경계 검사 도구) 단위 테스트."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = (Path(__file__).resolve().parent.parent
        / "skills" / "project-doctor" / "tools" / "check_write_boundary.py")


def run(root, *paths) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), str(root), *map(str, paths)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def test_inside_paths_pass(tmp_path):
    (tmp_path / "src").mkdir()
    r = run(tmp_path, "src/a.py", "README.md", "src/nested/b.js")
    assert r.returncode == 0, r.stdout
    assert "전부 프로젝트 안" in r.stdout


def test_parent_escape_fails(tmp_path):
    r = run(tmp_path, "../outside.py")
    assert r.returncode == 1
    assert "경계 위반" in r.stdout


def test_absolute_path_outside_fails(tmp_path, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    r = run(tmp_path, str(other / "x.py"))
    assert r.returncode == 1
    assert "경계 위반" in r.stdout


def test_mixed_reports_only_violation(tmp_path):
    r = run(tmp_path, "ok.py", "../../etc/passwd", "sub/ok2.py")
    assert r.returncode == 1
    assert "1건" in r.stdout  # 위반은 1건만


def test_absolute_inside_root_passes(tmp_path):
    # 루트 내부를 절대경로로 가리키면 통과해야 한다.
    inside = tmp_path / "data" / "f.csv"
    r = run(tmp_path, str(inside))
    assert r.returncode == 0, r.stdout


def test_no_args_usage(tmp_path):
    r = run(tmp_path)  # 경로 인자 없음
    assert r.returncode == 1
    assert "사용법" in r.stdout


def test_root_not_dir_errors(tmp_path):
    missing = tmp_path / "nope"
    r = run(missing, "a.py")
    assert r.returncode == 1
    assert "폴더가 아닙니다" in r.stdout


def test_empty_path_rejected(tmp_path):
    # 빈/공백 경로는 인자 실수 신호 — 침묵 통과 금지.
    r = run(tmp_path, "   ")
    assert r.returncode == 1
    assert "경계 위반" in r.stdout


@pytest.mark.skipif(os.name != "nt", reason="드라이브 상대경로/UNC는 Windows 전용 위험")
def test_drive_relative_path_rejected(tmp_path):
    # C:foo — 드라이브 상대경로. OS가 'C: 드라이브의 cwd' 기준으로 해석하므로 루트 밖으로 샐 수 있다.
    r = run(tmp_path, "C:foo")
    assert r.returncode == 1, r.stdout
    assert "경계 위반" in r.stdout


@pytest.mark.skipif(os.name != "nt", reason="UNC 경로는 Windows 전용")
def test_unc_path_rejected(tmp_path):
    r = run(tmp_path, r"\\server\share\evil.txt")
    assert r.returncode == 1, r.stdout
    assert "경계 위반" in r.stdout
