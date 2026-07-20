"""치료(파일 수정) 실행 전, 변경 예정 경로가 프로젝트 폴더 안인지 검사한다 (BACKLOG BL-18).

prescription-protocol 0장(실행 게이트) 4번 "쓰기 경계 확인"을 자동화한 도구다.
스킬과 함께 설치되므로(`~/.claude/skills/project-doctor/tools/`) 치료 실행 직전에 호출할 수 있다.

사용법:
  python check_write_boundary.py <프로젝트_루트> <변경예정_경로> [경로...]

판정: 모든 경로가 프로젝트 루트 안(하위)으로 해석되면 통과(종료 0).
      절대 경로·상위 폴더 탈출(`../`)·드라이브 상대경로(`C:foo`)·UNC(`\\\\server\\share`)로
      루트 밖을 가리키는 경로가 하나라도 있으면 미달(종료 1).
이 도구는 '읽기 전용 검사'다 — 어떤 파일도 만들거나 고치지 않는다.

## 보안 한계 (호출 측이 반드시 알 것)
- **사전 검사일 뿐이다.** 최종 안전은 이 도구를 호출하는 측(Claude/사람)에 달려 있다 — 완전 강제가 아니다.
- **검사 시점 ≠ 쓰기 시점(TOCTOU).** 심볼릭 링크·정션이 검사 후 루트 밖으로 교체되면 같은 경로로의
  쓰기가 샐 수 있다. 이를 줄이기 위해 통과 경로는 **해석된(canonical) 경로**를 함께 출력한다 —
  **실제 쓰기는 raw 경로가 아니라 출력된 해석 경로로만 하라.**
- 심링크/정션을 통한 우회를 원자적으로 막지는 못한다(검사와 쓰기가 한 동작이 아니므로).
"""
from __future__ import annotations

import sys
from pathlib import Path


def classify(root: Path, raw: str) -> tuple[str, str]:
    """(상태, 메시지) — 상태는 'ok' 또는 'out'."""
    raw_stripped = raw.strip()
    if not raw_stripped:
        return ("out", "밖(빈 경로 — 변경 대상이 비어 있음)")

    candidate = Path(raw)
    # 드라이브 상대경로(예: C:foo — 드라이브는 있는데 루트(\)가 없음)는 OS가 '그 드라이브의
    # 현재 디렉터리' 기준으로 해석한다(비결정적). 루트와 단순 결합하면 안전해 보이지만 실제
    # 쓰기는 프로젝트 밖에 떨어질 수 있으므로 무조건 거부한다.
    if candidate.drive and not candidate.root:
        return ("out", f"밖(드라이브 상대경로 — 위험)  {raw}")

    # 드라이브·루트가 있거나 절대경로면(UNC \\server\share 포함) 루트와 결합하지 않고
    # 그 자체로 해석한다. 그 외(순수 상대경로)만 루트 기준으로 결합한다.
    if candidate.drive or candidate.root or candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root / candidate).resolve()

    try:
        resolved.relative_to(root)
        return ("ok", f"OK  {raw}  ->  {resolved}")
    except ValueError:
        return ("out", f"밖  {raw}  ->  {resolved}")


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
        print(f"경계 위반: {len(outside)}건 - 프로젝트 밖 쓰기는 금지입니다. 치료를 중단하세요.")
        return 1
    print(f"경계 검사: {len(argv) - 2}개 경로 전부 프로젝트 안 (통과)")
    print("주의: 실제 쓰기는 위 'OK' 줄의 해석된 경로로만 하세요 (raw 재해석 시 우회 여지).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
