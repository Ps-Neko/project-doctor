"""버전 정합 검사 (BACKLOG BL-20).

SKILL.md의 버전을 단일 진실로 보고, 나머지 표기처(루트 README·스킬 README·CHANGELOG 최신 항목)가
모두 같은 버전을 가리키는지 확인한다. 하나라도 어긋나면 어디가 틀렸는지 출력하고 종료 코드 1.

이 프로젝트는 "절차의 일관성"이 제품이고 보고서 첫머리에 스킬 버전을 인쇄하므로, 버전 드리프트를
CI에서 실패로 잡는다. (2026-06-12 루트 README 누락 드리프트가 실제로 발생 → 이 검사로 재발 방지)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "project-doctor" / "SKILL.md"

VER = re.compile(r"v(\d+\.\d+\.\d+)")


def find_version(path: Path, marker: str) -> str | None:
    """파일에서 marker가 든 첫 줄의 vX.Y.Z를 돌려준다 (없으면 None)."""
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if marker in line:
            m = VER.search(line)
            if m:
                return m.group(1)
    return None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    truth = find_version(SKILL, "스킬 버전:")
    if not truth:
        print(f"오류: SKILL.md에서 '스킬 버전: vX.Y.Z'를 찾지 못했습니다 - {SKILL}")
        return 1

    # (이름, 경로, 그 파일에서 버전이 든 줄을 식별하는 marker)
    checks = [
        ("루트 README", ROOT / "README.md", "현재 버전:"),
        ("스킬 README", ROOT / "skills" / "project-doctor" / "README.md", "현재 버전:"),
        ("CHANGELOG 최신", ROOT / "skills" / "project-doctor" / "CHANGELOG.md", "## v"),
    ]

    print(f"기준(SKILL.md): v{truth}")
    mismatches: list[str] = []
    for name, path, marker in checks:
        got = find_version(path, marker)
        if got is None:
            print(f"  - {name}: (표기 없음 — 건너뜀)")
            continue
        if got == truth:
            print(f"  - {name}: v{got} ✓")
        else:
            print(f"  - {name}: v{got} ✗ (기준 v{truth}와 불일치)")
            mismatches.append(f"{name}=v{got}")

    if mismatches:
        print(f"버전 불일치: {len(mismatches)}건 — {', '.join(mismatches)} ≠ SKILL v{truth}")
        return 1
    print("버전 정합: 전부 일치 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
