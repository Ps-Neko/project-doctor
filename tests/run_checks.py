"""보고서 1건을 채점기·형식 검증기로 한 번에 검사하는 묶음 러너 (E2E 보조).

용도: 신선한 검진 드라이런으로 보고서를 만든 뒤, 이 한 줄로 두 게이트를 함께 통과하는지 확인한다.
  python tests/run_checks.py <보고서.md> <EXPECTED.md>

내부적으로 verify_report_format.py(형식 계약)·compare_report.py(탐지율+오탐 게이트)·
check_location_sampling.py(BL-22 위치 샘플링)를 순서대로 실행하고, 모두 통과해야 종료 코드 0을
반환한다. 정답지 인자를 생략하면 형식 검사만 수행한다(채점·위치는 정답지가 있어야 한다).

검진(Claude 실행) 자체는 자동화 범위 밖이다 — 이 러너는 '산출물'을 검사한다 (BACKLOG BL-16).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, args: list[str]) -> tuple[int, str]:
    """tests/ 안의 검사 스크립트를 현재 파이썬으로 실행하고 (종료코드, 출력)을 돌려준다."""
    proc = subprocess.run(
        [sys.executable, str(HERE / script), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode, (proc.stdout + proc.stderr).rstrip()


def main(argv: list[str]) -> int:
    # Windows 콘솔(cp949)에서도 한글·em-dash가 깨지지 않게 UTF-8로 고정.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) not in (2, 3):
        print("사용법: python tests/run_checks.py <보고서.md> [EXPECTED.md]")
        return 1
    report = argv[1]
    if not Path(report).exists():
        print(f"오류: 보고서를 찾을 수 없습니다 - {report}")
        return 1

    results: list[tuple[str, int]] = []
    total = 3 if len(argv) == 3 else 1

    print("=" * 56)
    print(f"[1/{total}] 형식 검증 (verify_report_format.py)")
    print("-" * 56)
    code, out = run("verify_report_format.py", [report])
    print(out)
    results.append(("형식 검증", code))

    if len(argv) == 3:
        print()
        print("=" * 56)
        print(f"[2/{total}] 탐지율·오탐 채점 (compare_report.py)")
        print("-" * 56)
        code, out = run("compare_report.py", [report, argv[2]])
        print(out)
        results.append(("채점", code))

        print()
        print("=" * 56)
        print(f"[3/{total}] 위치 샘플링 게이트 (check_location_sampling.py · BL-22)")
        print("-" * 56)
        code, out = run("check_location_sampling.py", [report, argv[2]])
        print(out)
        results.append(("위치 샘플링", code))
    else:
        print("\n(정답지 미지정 — 채점·위치 생략, 형식 검사만 수행)")

    print()
    print("=" * 56)
    failed = [name for name, code in results if code != 0]
    for name, code in results:
        print(f"  {name}: {'통과' if code == 0 else '미달'}")
    print(f"종합: {'전부 통과' if not failed else '미달 — ' + ', '.join(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
