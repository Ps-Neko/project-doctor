"""채점기 자체의 회귀 가드 (BACKLOG BL-15, OS 무관 버전).

각 픽스처 정답지의 "## 심은 문제" 표 ID를 그대로 본뜬 합성 보고서를 만들어
compare_report.py가 100%·오탐 0(=통과)을 내는지 확인한다. 탐지 로직이 아니라
'채점기가 깨지지 않았는지'를 보는 가드다. (이전엔 ci.yml의 bash heredoc이었으나
Windows 러너에서 동작하도록 파일로 분리 — BL-21)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
COMPARE = ROOT / "tests" / "compare_report.py"
ID = re.compile(r"[A-Z]+-\d{2,}")


def seeded_ids(expected: Path) -> list[str]:
    """'## 심은 문제' 표의 ID만 순서대로(중복 제거) 추출한다."""
    ids: list[str] = []
    in_section = False
    for line in expected.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if s.startswith("## "):
            in_section = s.startswith("## 심은 문제")
            continue
        if in_section and s.startswith("|"):
            m = ID.search(s)
            if m:
                ids.append(m.group())
    return list(dict.fromkeys(ids))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    fails: list[str] = []
    checked = 0
    for expected in sorted(FIXTURES.glob("*/EXPECTED.md")):
        ids = seeded_ids(expected)
        if not ids:
            continue
        checked += 1
        report = expected.parent / "_ci_synthetic_report.md"
        report.write_text("발견ID: " + ", ".join(ids) + "\n", encoding="utf-8")
        try:
            r = subprocess.run(
                [sys.executable, str(COMPARE), str(report), str(expected)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
        finally:
            report.unlink(missing_ok=True)
        if r.returncode != 0:
            fails.append(f"{expected.parent.name}: {r.stdout.strip()}")

    if fails:
        print("채점 회귀 실패:")
        for f in fails:
            print(f"  {f}")
        return 1
    print(f"자체 픽스처 채점 회귀: {checked}개 정답지 전부 통과 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
