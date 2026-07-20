"""check_links.py 단위 테스트 — 링크 추출·펜스/이미지 제외 로직."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_links  # noqa: E402


def test_text_link_extracted() -> None:
    assert check_links.LINK.findall("[문서](./a.md)") == ["./a.md"]


def test_image_embed_excluded() -> None:
    # ![alt](...) 이미지 임베드는 텍스트 링크가 아니므로 추출하지 않는다.
    assert check_links.LINK.findall("![그림](pic.png)") == []
    # 이미지와 텍스트 링크가 섞이면 텍스트 링크만 잡는다.
    assert check_links.LINK.findall("![i](p.png) 그리고 [t](x.md)") == ["x.md"]


def test_strip_code_fences_removes_block() -> None:
    text = "위\n```\n[안보임](없는것.md)\n```\n아래"
    stripped = check_links.strip_code_fences(text)
    assert "없는것" not in stripped
    assert "위" in stripped and "아래" in stripped


def test_broken_link_detected(tmp_path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("[깨짐](./없는파일.md)\n", encoding="utf-8")
    # check_file은 ROOT 상대 경로로 보고하므로 ROOT를 임시로 바꿔 검사한다.
    original_root = check_links.ROOT
    try:
        check_links.ROOT = tmp_path
        broken = check_links.check_file(md)
    finally:
        check_links.ROOT = original_root
    assert len(broken) == 1


def test_existing_link_passes(tmp_path) -> None:
    (tmp_path / "target.md").write_text("ok", encoding="utf-8")
    md = tmp_path / "doc.md"
    md.write_text("[있음](./target.md) [앵커](./target.md#section) [쿼리](./target.md?x=1)\n",
                  encoding="utf-8")
    original_root = check_links.ROOT
    try:
        check_links.ROOT = tmp_path
        broken = check_links.check_file(md)
    finally:
        check_links.ROOT = original_root
    assert broken == []  # 앵커·쿼리가 붙어도 같은 파일로 해석되어 통과


def test_fenced_broken_link_ignored(tmp_path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("```\n[예시](./존재하지않음.md)\n```\n", encoding="utf-8")
    original_root = check_links.ROOT
    try:
        check_links.ROOT = tmp_path
        broken = check_links.check_file(md)
    finally:
        check_links.ROOT = original_root
    assert broken == []  # 펜스 안 예시 링크는 검사 제외


def test_link_outside_repo_fails(tmp_path) -> None:
    """저장소 밖으로 나가는 상대 링크(../)는 실제 파일이 있어도 실패로 본다 (P3-B)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (tmp_path / "outside.md").write_text("real", encoding="utf-8")  # 저장소 밖 실재 파일
    md = repo / "doc.md"
    md.write_text("[밖으로](../outside.md)\n", encoding="utf-8")
    original_root = check_links.ROOT
    try:
        check_links.ROOT = repo
        broken = check_links.check_file(md)
    finally:
        check_links.ROOT = original_root
    assert len(broken) == 1
    assert "저장소 밖" in broken[0]
