"""BL-22 — 위치 샘플링 게이트.

EXPECTED.md '## 심은 문제' 표의 상위 N개 ID에 대해, 검진 보고서에서 그 ID를
보고한 자리에 정답지의 기대 파일명이 하나라도 등장하는지 확인한다.
ID recall(compare_report.py)은 "DUP-01을 찾았다"까지만 보지만, 이 게이트는
"그 DUP-01이 엉뚱한 파일을 가리키지 않는가"를 가볍게 방어한다.

설계 원칙:
- 보고서의 자유 서술 형식을 강제하지 않는다 — 파일명이 그 발견 구간 어딘가에
  등장하기만 하면 통과('어디?' 줄을 특정 형식으로 못박지 않음).
- 위치 셀에서 파일명을 못 뽑는 항목(예: 'README 파일 없음')은 위치 검사 대상에서 제외.
- BL-17(전면 위치·심각도 채점) 보류의 가벼운 중간안이다(BACKLOG BL-22).

사용: python tests/check_location_sampling.py <보고서.md> <EXPECTED.md>
판정: 표 상위 N개 ID 중 파일명을 가진 항목이 모두 보고서 해당 구간에서
      기대 파일명과 일치하면 통과(종료 0), 하나라도 어긋나면 미달(종료 1).
"""
from __future__ import annotations

import re
import sys

from compare_report import (
    _cells,
    _is_expected_heading,
    outside_fence,
    read_lines,
)

SAMPLE_SIZE: int = 5
# 위치 셀 길이 상한 — 비정상적으로 긴 셀에서 FILENAME_RE 백트래킹 폭주(ReDoS·O(n²))를 막는다.
# 현실 위치 셀은 <100자라 정상 추출엔 무영향(상한 너머의 파일명만 추출에서 빠진다).
MAX_LOC_LEN: int = 2000
# 위치 셀·보고서에서 '파일명'으로 인정할 확장자 (알려진 소스/설정/문서 확장자).
# 파일명은 ASCII 본체 + 확장자로 보고, 확장자 뒤에 영숫자가 이어지면(예: .python)
# 매치하지 않는다. \b 대신 lookahead 를 쓰는 이유: 파이썬 re 의 \w 는 한글도 포함해
# "utils.py의"처럼 확장자에 한글이 바로 붙으면 \b 가 성립하지 않아 추출에 실패한다.
FILENAME_RE = re.compile(
    r"[A-Za-z0-9_./\\-]+\."
    r"(?:py|pyi|js|cjs|mjs|jsx|ts|tsx|json|md|rst|html?|css|scss|less|"
    r"txt|ya?ml|toml|ini|cfg|sh|ps1|bat|cmd|sql|bak)"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)
# 보고서에서 발견 ID 토큰: 대괄호로 감싼 [DUP-01] 형태.
REPORT_ID_RE = re.compile(r"\[([A-Z]+-\d{2,})\]")


def parse_expected_locations(lines: list[str]) -> list[tuple[str, set[str]]]:
    """'## 심은 문제' 표를 (ID, {기대 파일명...}) 목록으로 — 표 등장 순서 유지.

    위치 열의 자유 서술에서 파일명만 정규식으로 추출한다(없으면 빈 집합).
    compare_report.parse_expected_ids 와 같은 표 파싱 계약(전각 파이프·백틱 셀·
    표 끊김 시 열 인덱스 리셋)을 따른다.
    """
    rows: list[tuple[str, set[str]]] = []
    in_section, id_col, loc_col = False, -1, -1
    for line in lines:
        stripped = line.strip().replace("｜", "|")
        if stripped.startswith("## "):
            in_section = _is_expected_heading(stripped)
            id_col, loc_col = -1, -1
            continue
        if not in_section:
            continue
        if not stripped.startswith("|"):
            id_col, loc_col = -1, -1  # 표가 끊기면 다음 표를 위해 리셋
            continue
        cells = _cells(stripped)
        if id_col < 0:
            for i, cell in enumerate(cells):
                key = cell.replace(" ", "")
                if key in ("ID", "발견ID"):
                    id_col = i
                elif key in ("위치", "어디"):
                    loc_col = i
            continue
        if id_col >= len(cells) or set(cells[id_col]) <= set("-: "):
            continue  # 구분선·빈 셀
        the_id = cells[id_col]
        loc = cells[loc_col] if 0 <= loc_col < len(cells) else ""
        files = {m.group(0) for m in FILENAME_RE.finditer(loc[:MAX_LOC_LEN])}
        rows.append((the_id, files))
    return rows


def report_segments(lines: list[str]) -> dict[str, str]:
    """보고서를 'ID 토큰 등장' 기준으로 잘라 {ID: 그 ID 구간 텍스트}.

    코드펜스 밖만 본다(템플릿 예시 [DUP-01] 등 오염 방지). 한 ID 토큰부터 다음
    ID 토큰 직전까지가 한 구간 — 본문의 '### … [DUP-01] …' 블록이든 부록의
    '- [TMP-01] …' 한 줄이든 그 ID 설명이 들어간 범위를 담는다. 같은 ID가 여러 번
    나오면 모두 이어 붙인다.
    """
    clean = outside_fence(lines)
    id_at: list[tuple[int, str]] = []
    for i, line in enumerate(clean):
        for m in REPORT_ID_RE.finditer(line):
            id_at.append((i, m.group(1)))
    segments: dict[str, str] = {}
    for k, (idx, the_id) in enumerate(id_at):
        end = id_at[k + 1][0] if k + 1 < len(id_at) else len(clean)
        chunk = "\n".join(clean[idx:end])
        segments[the_id] = (
            segments[the_id] + "\n" + chunk if the_id in segments else chunk
        )
    return segments


def evaluate(
    report_lines: list[str], expected_lines: list[str]
) -> tuple[list[tuple[str, set[str]]], list[tuple[str, set[str]]], list[tuple[str, set[str]]]]:
    """(검사한 항목, 일치, 위치오진)를 돌려준다 — 각 원소는 (ID, 기대 파일명집합)."""
    rows = parse_expected_locations(expected_lines)
    segments = report_segments(report_lines)
    checked: list[tuple[str, set[str]]] = []
    hits: list[tuple[str, set[str]]] = []
    misses: list[tuple[str, set[str]]] = []
    for the_id, files in rows[:SAMPLE_SIZE]:
        if not files:
            continue  # 파일명 없는 항목(예: 'README 없음')은 위치 검사 N/A
        checked.append((the_id, files))
        seg = segments.get(the_id, "")
        if any(f in seg for f in files):
            hits.append((the_id, files))
        else:
            misses.append((the_id, files))
    return checked, hits, misses


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) != 3:
        print("사용법: python tests/check_location_sampling.py <보고서.md> <EXPECTED.md>")
        return 1
    try:
        report_lines = read_lines(argv[1])
        expected_lines = read_lines(argv[2])
    except OSError as err:
        print(f"오류: 파일을 읽을 수 없습니다 - {err}")
        return 1
    checked, hits, misses = evaluate(report_lines, expected_lines)
    if not checked:
        print("위치 검사 대상 없음 (상위 ID 중 파일명을 가진 항목이 없음) — 건너뜀(통과).")
        return 0
    for the_id, files in checked:
        mark = "OK " if (the_id, files) in hits else "오진"
        print(f"  [{mark}] {the_id}: 기대 파일명 {{{', '.join(sorted(files))}}}")
    passed = not misses
    print(
        f"위치 샘플링: {len(hits)}/{len(checked)} 일치 "
        f"(상위 {SAMPLE_SIZE}개 중 파일명 보유 항목 대상)"
    )
    for the_id, files in misses:
        print(
            f"위치 오진: {the_id} — 보고서의 해당 구간에 기대 파일명"
            f"({', '.join(sorted(files))}) 중 어느 것도 없음"
        )
    print(f"판정: {'통과' if passed else '미달'} (위치 오진 0건 기준)")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
