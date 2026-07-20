"""저장소 내 Markdown 파일의 상대 링크가 실재하는지 검사한다 (BACKLOG BL-15: CI 문서 링크 검사).

`[텍스트](상대경로)` 형태의 링크 중 외부 URL(http/https/mailto)과 앵커(#...)를 제외한
파일 링크가 실제로 존재하는지 확인한다. 깨진 링크가 하나라도 있으면 종료 코드 1.
이미지 임베드(![alt](...))와 코드펜스(```) 안의 예시 링크는 검사 대상에서 제외한다.

용도: CI에서 문서 링크가 리팩터링으로 깨지지 않았는지 자동 확인.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# (?<!!): 이미지 임베드 ![alt](...)는 제외 (텍스트 링크만).
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
# 검사 대상에서 제외할 디렉터리
SKIP_DIRS = {".git", "node_modules", ".pytest_cache", "__pycache__"}


def iter_markdown() -> list[Path]:
    return [p for p in ROOT.rglob("*.md")
            if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)]


def strip_code_fences(text: str) -> str:
    """코드펜스(```) 블록을 제거한다 — 펜스 안 예시 링크를 검사하지 않기 위함."""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def check_file(md: Path) -> list[str]:
    broken: list[str] = []
    text = strip_code_fences(md.read_text(encoding="utf-8-sig", errors="replace"))
    for target in LINK.findall(text):
        target = target.strip()
        # 마크다운 title 문법 분리: [t](./a.md "설명") → 공백+따옴표 이후를 떼어낸다.
        target = re.split(r'\s+["\']', target, maxsplit=1)[0]
        # 외부 URL·메일·순수 앵커는 검사하지 않는다.
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # 앵커(#)와 쿼리스트링(?)을 떼어 파일 경로만 남긴다.
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        resolved = (md.parent / path_part).resolve()
        # 저장소 밖으로 나가는 상대 링크(../)는 러너 환경에 우연히 파일이 있어도 실패로 본다 —
        # 문서 링크는 저장소 안을 가리켜야 한다(다른 환경에서 깨지거나 의도치 않은 외부 참조).
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            broken.append(f"{md.relative_to(ROOT)} -> {target} (저장소 밖 링크)")
            continue
        if not resolved.exists():
            broken.append(f"{md.relative_to(ROOT)} -> {target}")
    return broken


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    all_broken: list[str] = []
    files = iter_markdown()
    for md in files:
        all_broken.extend(check_file(md))
    print(f"검사한 Markdown 파일: {len(files)}개")
    if all_broken:
        print(f"깨진 링크: {len(all_broken)}건")
        for b in all_broken:
            print(f"  - {b}")
        return 1
    print("깨진 링크: 0건 (통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
