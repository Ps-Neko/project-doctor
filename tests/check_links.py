"""저장소 내 Markdown 파일의 상대 링크가 실재하는지 검사한다 (BACKLOG BL-15).

`[텍스트](상대경로)` 형태의 링크 중 외부 URL(http/https/mailto)과 앵커(#...)를 제외한
파일 링크가 실제로 존재하는지 확인한다. 깨진 링크가 하나라도 있으면 종료 코드 1.

용도: CI에서 문서 링크가 리팩터링으로 깨지지 않았는지 자동 확인.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# 검사 대상에서 제외할 디렉터리
SKIP_DIRS = {".git", "node_modules", ".pytest_cache", "__pycache__"}


def iter_markdown() -> list[Path]:
    return [p for p in ROOT.rglob("*.md")
            if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)]


def check_file(md: Path) -> list[str]:
    broken: list[str] = []
    text = md.read_text(encoding="utf-8-sig", errors="replace")
    for target in LINK.findall(text):
        target = target.strip()
        # 외부 URL·메일·순수 앵커는 검사하지 않는다.
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # 앵커가 붙은 경우 파일 경로만 분리.
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (md.parent / path_part).resolve()
        if not resolved.exists():
            broken.append(f"{md.relative_to(ROOT)} → {target}")
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
            print(f"  ✗ {b}")
        return 1
    print("깨진 링크: 0건 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
