"""보고서의 발견 ID를 EXPECTED.md 정답과 비교해 탐지율을 채점한다.

판정 = 탐지율(기준 80% 이상) + 오탐 0건.
오탐 = 정답지의 "## 심은 문제"에도 "## 추가 보고 허용"(채점 중립)에도 없는 보고 ID.
"""
import re
import sys
from pathlib import Path

PASS_THRESHOLD: float = 80.0
REPORT_PREFIX: str = "발견ID:"
EXPECTED_HEADING: str = "## 심은 문제"
NEUTRAL_HEADING: str = "## 추가 보고 허용"
EMPTY_MARK: str = "(없음)"
ID_PATTERN = re.compile(r"[A-Z]+-\d{2,}")


def read_lines(path: str) -> list[str]:
    # utf-8-sig: PowerShell 5.1 등이 만드는 BOM 붙은 UTF-8도 그대로 읽는다.
    # errors="replace": cp949(ANSI)로 저장된 보고서가 와도 UnicodeDecodeError로 죽지 않고
    #   깨진 문자만 치환해 채점을 계속한다(except OSError가 UnicodeDecodeError를 못 잡는 문제 회피).
    return Path(path).read_text(encoding="utf-8-sig", errors="replace").splitlines()


def parse_report_ids(lines: list[str]) -> list[str]:
    """'발견ID:'로 시작하는 마지막 줄에서 쉼표 구분 ID를 추출한다."""
    found = [ln.strip() for ln in lines
             if ln.strip().startswith(REPORT_PREFIX)]
    if not found:
        return []
    body = found[-1].split(":", 1)[1].strip()
    if not body or body == EMPTY_MARK:
        return []
    return [part.strip() for part in body.split(",") if part.strip()]


def parse_revisit_lines(lines: list[str]) -> dict[str, str]:
    """v2 재방문 기계 판독 줄('비교:', '숙제:')을 추출한다 (없으면 빈 dict)."""
    extras: dict[str, str] = {}
    for prefix, key in (("비교:", "comparison"), ("숙제:", "homework")):
        found = [ln.strip() for ln in lines if ln.strip().startswith(prefix)]
        if found:
            extras[key] = found[-1].split(":", 1)[1].strip()
    return extras


def parse_expected_ids(lines: list[str]) -> list[str]:
    """'## 심은 문제' 표의 ID 열을 추출한다(중복 제거, 순서 유지)."""
    ids: list[str] = []
    in_section, id_col = False, -1
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section, id_col = stripped.startswith(EXPECTED_HEADING), -1
            continue
        if not in_section or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if id_col < 0:
            if "ID" in cells:
                id_col = cells.index("ID")
            continue
        if id_col >= len(cells) or set(cells[id_col]) <= set("-: "):
            continue  # 구분선(---)이나 빈 셀은 건너뛴다.
        ids.append(cells[id_col])
    return list(dict.fromkeys(ids))


def parse_neutral_ids(lines: list[str]) -> list[str]:
    """'## 추가 보고 허용'(채점 중립) 절에서 줄마다 첫 ID 하나를 추출한다.

    줄 뒷부분의 설명에 다른 ID가 등장해도(예: "HARD-02 — DUP-01의 부산물")
    그 줄의 중립 ID는 첫 번째 것 하나뿐이다.
    """
    ids: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.startswith(NEUTRAL_HEADING)
            continue
        if not in_section or not stripped.startswith(("-", "|")):
            continue
        match = ID_PATTERN.search(stripped)
        if match:
            ids.append(match.group())
    return list(dict.fromkeys(ids))


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) != 3:
        print("사용법: python compare_report.py <보고서.md> <EXPECTED.md>")
        return 1
    try:
        report_lines = read_lines(argv[1])
        expected_lines = read_lines(argv[2])
    except OSError as err:
        print(f"오류: 파일을 읽을 수 없습니다 - {err}")
        return 1
    report_ids = parse_report_ids(report_lines)
    expected_ids = parse_expected_ids(expected_lines)
    neutral_ids = parse_neutral_ids(expected_lines)
    if not expected_ids:
        print("오류: 정답지의 '## 심은 문제' 표에서 ID를 찾지 못했습니다.")
        return 1
    missed = [i for i in expected_ids if i not in set(report_ids)]
    unique_report = list(dict.fromkeys(report_ids))
    neutral_hits = [i for i in unique_report
                    if i in set(neutral_ids) and i not in set(expected_ids)]
    false_positives = [i for i in unique_report
                       if i not in set(expected_ids) | set(neutral_ids)]
    n_found = len(expected_ids) - len(missed)
    rate = n_found / len(expected_ids) * 100
    passed = rate >= PASS_THRESHOLD and not false_positives
    print(f"탐지율: {rate:.1f}% ({n_found}/{len(expected_ids)})")
    print(f"놓친 ID: {', '.join(missed) if missed else EMPTY_MARK}")
    print(f"채점 중립 ID(허용): {', '.join(neutral_hits) if neutral_hits else EMPTY_MARK}")
    print(f"오탐 ID(정답지·채점 중립에 없음): "
          f"{', '.join(false_positives) if false_positives else EMPTY_MARK}")
    revisit = parse_revisit_lines(report_lines)
    if "comparison" in revisit:
        print(f"재방문 비교(참고용): {revisit['comparison']}")
    if "homework" in revisit:
        print(f"숙제(참고용): {revisit['homework']}")
    print(f"판정: {'통과' if passed else '미달'} "
          f"(기준: 탐지율 {PASS_THRESHOLD:.0f}% 이상 + 오탐 0건)")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
