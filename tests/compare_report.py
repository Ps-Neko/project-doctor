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
# 채점 중립 줄에서 ID로 인정할 카탈로그 접두사 — ISO-8601·UTF-16·SHA-256 같은
# 비-ID 토큰(정답지 설명문에 등장 가능)을 ID로 오인하지 않도록 화이트리스트로 거른다.
KNOWN_ID_PREFIXES = frozenset({
    "DUP", "DEAD", "BIG", "HARD", "DOC", "TEST", "TMP", "STALE", "STRUCT",
    "SEC", "PII", "REL", "HIST", "DEP", "LINT", "AIGEN",
})


def read_lines(path: str) -> list[str]:
    # utf-8-sig: BOM 흡수. errors=replace: cp949(ANSI) 보고서도 트레이스백 없이 읽는다
    #   (except OSError가 UnicodeDecodeError를 못 잡는 문제 회피).
    return Path(path).read_text(encoding="utf-8-sig", errors="replace").splitlines()


def _is_expected_heading(stripped: str) -> bool:
    """'## 심은 문제' 또는 '## 심은 문제 (14건)'만 정답 절로 인정 ('## 심은 문제 해설' 등 후속 절 차단)."""
    return stripped == EXPECTED_HEADING or stripped.startswith(EXPECTED_HEADING + " (")


def _is_neutral_heading(stripped: str) -> bool:
    return stripped == NEUTRAL_HEADING or stripped.startswith(NEUTRAL_HEADING + " (")


def parse_report_ids(lines: list[str]) -> list[str]:
    """'발견ID:'로 시작하는 마지막 줄에서 쉼표 구분 ID를 추출한다.

    코드펜스(```) 안의 줄은 무시한다 — 템플릿 9절 예시나 부록의 '발견ID:' 예시가
    실제 블록으로 오인되어 채점을 오염시키는 것을 막는다(verify가 '여러 개'를 따로 잡는다).
    """
    found, in_fence = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith(REPORT_PREFIX):
            found.append(stripped)
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


def _cells(stripped: str) -> list[str]:
    """표 행을 셀 리스트로 — 전각 파이프(｜) 정규화 + 셀의 백틱·공백 제거."""
    normalized = stripped.replace("｜", "|")
    return [c.strip().strip("`").strip() for c in normalized.strip("|").split("|")]


def parse_expected_ids(lines: list[str]) -> list[str]:
    """'## 심은 문제' 표의 ID 열을 추출한다(중복 제거, 순서 유지).

    견고성: 전각 파이프·백틱 감싼 셀·'발견 ID'처럼 공백 든 헤더를 허용하고,
    같은 절 안에 표가 둘이면 표가 끊길 때 열 인덱스를 리셋해 둘째 표도 올바로 읽는다.
    """
    ids: list[str] = []
    in_section, id_col = False, -1
    for line in lines:
        stripped = line.strip().replace("｜", "|")
        if stripped.startswith("## "):
            in_section, id_col = _is_expected_heading(stripped), -1
            continue
        if not in_section:
            continue
        if not stripped.startswith("|"):
            id_col = -1  # 표가 끊기면 다음 표를 위해 열 인덱스 리셋
            continue
        cells = _cells(stripped)
        if id_col < 0:
            for i, cell in enumerate(cells):
                if cell.replace(" ", "") in ("ID", "발견ID"):  # 'GUID' 등은 제외(정확 매칭)
                    id_col = i
                    break
            continue
        if id_col >= len(cells) or set(cells[id_col]) <= set("-: "):
            continue  # 구분선(---)이나 빈 셀은 건너뛴다.
        ids.append(cells[id_col])
    return list(dict.fromkeys(ids))


def parse_neutral_ids(lines: list[str]) -> list[str]:
    """'## 추가 보고 허용'(채점 중립) 절에서 줄마다 ID 하나를 추출한다.

    줄에 'ISO-8601'처럼 ID 형식을 닮은 비-ID 토큰이 진짜 ID보다 앞서 와도,
    카탈로그 접두사(KNOWN_ID_PREFIXES)에 속하는 첫 토큰만 ID로 인정한다.
    """
    ids: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = _is_neutral_heading(stripped)
            continue
        if not in_section or not stripped.startswith(("-", "|")):
            continue
        matches = [m.group() for m in ID_PATTERN.finditer(stripped)]
        if not matches:
            continue
        # 카탈로그 접두사에 속하는 첫 토큰을 우선 채택(ISO-8601 등 비-ID 토큰이 앞서도 진짜 ID를
        # 집는다). 알려진 접두사가 하나도 없으면 줄의 첫 매치로 폴백(미래 접두사·테스트 ID 허용).
        known = [m for m in matches if m.split("-", 1)[0] in KNOWN_ID_PREFIXES]
        ids.append(known[0] if known else matches[0])
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
        print("오류: 정답지의 '## 심은 문제' 표에서 ID를 찾지 못했습니다 "
              "(헤더 'ID' 열·표 형식을 확인하세요).")
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
