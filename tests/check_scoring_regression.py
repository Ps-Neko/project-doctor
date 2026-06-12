"""채점기 자체의 회귀 가드 (BACKLOG BL-15, OS 무관 버전).

각 픽스처 정답지의 "## 심은 문제" 표 ID를 그대로 본뜬 합성 보고서를 만들어
compare_report.py가 100%·오탐 0(=통과)을 내는지 확인한다. 탐지 로직이 아니라
'채점기가 깨지지 않았는지'를 보는 가드다.

설계 메모(코드 리뷰 반영):
- ID 추출은 채점기 본체(compare_report.parse_expected_ids)를 그대로 재사용한다 — 가드가 다른
  추출 코드를 쓰면 채점기와 어긋나 거짓 미달/통과를 낼 수 있기 때문(가드의 신뢰성 근거).
- 합성 보고서는 소스트리가 아니라 OS 임시폴더(tempfile)에 만든다 — 고정 파일명 소스트리 쓰기는
  병렬 실행 레이스·잔존물·동명 실파일 덮어쓰기를 일으킨다.
- '## 심은 문제' 표가 없는 정답지(intro/pivot 스타일)는 채점 대상이 아니므로 명시적으로 건너뛰고,
  출력에 '발견 N개 중 M개 채점'처럼 분모를 드러낸다('전부 통과' 착시 방지).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

# 채점기 본체와 동일한 ID 추출·파일 읽기를 재사용한다.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_report import parse_expected_ids, read_lines  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
COMPARE = ROOT / "tests" / "compare_report.py"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    expecteds = sorted(FIXTURES.glob("*/EXPECTED.md"))
    checkable: list[tuple[Path, list[str]]] = []
    skipped: list[Path] = []
    for expected in expecteds:
        ids = parse_expected_ids(read_lines(str(expected)))
        if ids:
            checkable.append((expected, ids))
        else:
            skipped.append(expected)

    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        for expected, ids in checkable:
            report = Path(td) / f"{expected.parent.name}_synthetic.md"
            report.write_text("발견ID: " + ", ".join(ids) + "\n", encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(COMPARE), str(report), str(expected)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            if r.returncode != 0:
                detail = (r.stdout + r.stderr).strip() or "(출력 없음)"
                fails.append(f"{expected.parent.name}: {detail}")

    for expected in skipped:
        print(f"  {expected.parent.name}: '## 심은 문제' 표 없음 - 채점 대상 아님(건너뜀)")

    if fails:
        print("채점 회귀 실패:")
        for f in fails:
            print(f"  {f}")
        return 1
    print(f"자체 픽스처 채점 회귀: 발견 {len(expecteds)}개 중 "
          f"{len(checkable)}개 채점 가능, 전부 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
