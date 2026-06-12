"""치료(파일 수정) 실행 전, 변경 예정 경로가 프로젝트 폴더 안인지 검사한다 (BACKLOG BL-18).

prescription-protocol 0장(실행 게이트) 4번 "쓰기 경계 확인"을 자동화한 도구다.
스킬과 함께 설치되므로(`~/.claude/skills/project-doctor/tools/`) 치료 실행 직전에 호출할 수 있다.

사용법:
  python check_write_boundary.py <프로젝트_루트> <변경예정_경로> [경로...]

판정: 모든 경로가 프로젝트 루트 안(하위)으로 해석되면 통과(종료 0).
      절대 경로나 상위 폴더 탈출(`../`)로 루트 밖을 가리키는 경로가 하나라도 있으면 미달(종료 1).
이 도구는 '읽기 전용 검사'다 — 어떤 파일도 만들거나 고치지 않는다.
"""
from __future__ import annotations

import sys
from pathlib import Path


def classify(root: Path, raw: str) -> tuple[str, str]:
    """(상태, 메시지) — 상태는 'ok' 또는 'out'."""
    # 절대 경로면 루트 기준이 아니라 그 자체로 해석된다(탈출 위험).
    candidate = Path(raw)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
        return ("ok", f"OK  {raw}")
    except ValueError:
        return ("out", f"밖  {raw}  →  {resolved}")


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) < 3:
        print("사용법: python check_write_boundary.py <프로젝트_루트> <변경예정_경로> [경로...]")
        return 1
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"오류: 프로젝트 루트가 폴더가 아닙니다 - {root}")
        return 1

    outside: list[str] = []
    for raw in argv[2:]:
        status, msg = classify(root, raw)
        print(f"  {msg}")
        if status == "out":
            outside.append(raw)

    print(f"프로젝트 루트: {root}")
    if outside:
        print(f"경계 위반: {len(outside)}건 — 프로젝트 밖 쓰기는 금지입니다. 치료를 중단하세요.")
        return 1
    print(f"경계 검사: {len(argv) - 2}개 경로 전부 프로젝트 안 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
