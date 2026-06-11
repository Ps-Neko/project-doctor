"""보고서의 발견 ID를 EXPECTED.md 정답과 비교해 탐지율을 채점한다."""
import sys
from pathlib import Path

PASS_THRESHOLD: float = 80.0
REPORT_PREFIX: str = "발견ID:"
EXPECTED_HEADING: str = "## 심은 문제"
EMPTY_MARK: str = "(없음)"


def read_lines(path: str) -> list[str]:
    return Path(path).read_text(encoding="utf-8").splitlines()


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


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) != 3:
        print("사용법: python compare_report.py <보고서.md> <EXPECTED.md>")
        return 1
    try:
        report_ids = parse_report_ids(read_lines(argv[1]))
        expected_ids = parse_expected_ids(read_lines(argv[2]))
    except OSError as err:
        print(f"오류: 파일을 읽을 수 없습니다 - {err}")
        return 1
    if not expected_ids:
        print("오류: 정답지의 '## 심은 문제' 표에서 ID를 찾지 못했습니다.")
        return 1
    missed = [i for i in expected_ids if i not in set(report_ids)]
    extra = [i for i in dict.fromkeys(report_ids)
             if i not in set(expected_ids)]
    n_found = len(expected_ids) - len(missed)
    rate = n_found / len(expected_ids) * 100
    passed = rate >= PASS_THRESHOLD
    print(f"탐지율: {rate:.1f}% ({n_found}/{len(expected_ids)})")
    print(f"놓친 ID: {', '.join(missed) if missed else EMPTY_MARK}")
    print(f"정답지에 없는 보고 ID(참고용): {', '.join(extra) if extra else EMPTY_MARK}")
    print(f"판정: {'통과' if passed else '미달'} (기준 {PASS_THRESHOLD:.0f}%)")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
