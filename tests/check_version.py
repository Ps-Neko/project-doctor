"""버전 정합 검사 (BACKLOG BL-20).

SKILL.md의 버전을 단일 진실로 보고, 나머지 표기처(루트 README·스킬 README·CHANGELOG 최신 항목)가
모두 같은 버전을 가리키는지 확인한다. 하나라도 어긋나면 어디가 틀렸는지 출력하고 종료 코드 1.

이 프로젝트는 "절차의 일관성"이 제품이고 보고서 첫머리에 스킬 버전을 인쇄하므로, 버전 드리프트를
CI에서 실패로 잡는다. (2026-06-12 루트 README 누락 드리프트가 실제로 발생 → 이 검사로 재발 방지)

마커 줄이 살아 있는데 버전 표기만 깨진 경우('현재 버전: 미정' 등)는 '표기 없음'과 구분해 실패로 처리한다 —
그게 가장 흔하고 위험한 드리프트 패턴이기 때문이다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "project-doctor" / "SKILL.md"

# 앞에 글자가 붙은 rev10.20.30·dev1.2.3 등을 잡지 않도록 단어 경계를 둔다.
VER = re.compile(r"(?<![A-Za-z])v(\d+\.\d+\.\d+)")

# 검사 결과 상태
MISSING = object()   # 마커 줄 자체가 없음 — 그 표기처가 이 파일에 없는 것이므로 건너뜀
BROKEN = object()    # 마커 줄은 있으나 vX.Y.Z 파싱 실패 — 위험한 드리프트, 실패로 집계


def find_version(path: Path, marker: str):
    """파일에서 marker가 든 첫 줄을 보고 (truth | MISSING | BROKEN)을 돌려준다."""
    if not path.exists():
        return MISSING
    marker_seen = False
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if marker in line:
            marker_seen = True
            m = VER.search(line)
            if m:
                return m.group(1)
    # 마커는 봤는데 버전 파싱이 안 됐다면 깨진 표기로 본다.
    return BROKEN if marker_seen else MISSING


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    truth = find_version(SKILL, "스킬 버전:")
    if truth is MISSING or truth is BROKEN:
        print(f"오류: SKILL.md에서 '스킬 버전: vX.Y.Z'를 찾지 못했습니다 - {SKILL}")
        return 1

    checks = [
        ("루트 README", ROOT / "README.md", "현재 버전:"),
        ("스킬 README", ROOT / "skills" / "project-doctor" / "README.md", "현재 버전:"),
        ("CHANGELOG 최신", ROOT / "skills" / "project-doctor" / "CHANGELOG.md", "## v"),
    ]

    print(f"기준(SKILL.md): v{truth}")
    failures: list[str] = []
    for name, path, marker in checks:
        got = find_version(path, marker)
        if got is MISSING:
            print(f"  - {name}: (표기 없음 - 건너뜀)")
        elif got is BROKEN:
            print(f"  - {name}: 버전 줄은 있으나 vX.Y.Z 파싱 실패 (X)")
            failures.append(f"{name}=파싱실패")
        elif got == truth:
            print(f"  - {name}: v{got} (일치)")
        else:
            print(f"  - {name}: v{got} (X 기준 v{truth}와 불일치)")
            failures.append(f"{name}=v{got}")

    if failures:
        print(f"버전 불일치: {len(failures)}건 - {', '.join(failures)} (기준 SKILL v{truth})")
        return 1
    print("버전 정합: 전부 일치 (통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
