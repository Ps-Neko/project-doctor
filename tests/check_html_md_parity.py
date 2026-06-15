"""HTML 결과지가 .md 정본과 같은 발견·버전·판정을 담는지 검사한다 (5순위 외부평가).

verify_html_report.py(HTML-xx)가 HTML 결과지의 '안전성'(자기완결·무해)을 본다면,
이 도구는 HTML이 .md 정본과 '내용 동기화'됐는지 본다 — 정본의 ① 발견ID 전부 ② 스킬 버전
③ 종합 판정(등급 라벨)이 HTML 가시 텍스트에 빠짐없이 들어 있는가.

배경: report-formats.md는 채점·재검진 비교의 '정본'을 .md/채팅 보고서로 못박고, 채점기는
  HTML을 읽지 않는다. 그래서 HTML은 보조 사본인데, 사용자가 실제로 받아보는 건 그 HTML이다.
  HTML이 정본에서 발견 항목·버전·판정을 떨어뜨리면 데이터 무결성(.md 단일 출처)은 안 깨져도
  사용자가 받는 사본이 사실과 어긋난다 — 이 도구는 골든 쌍 회귀로 그 어긋남을 잡는다.

사용법:
  python check_html_md_parity.py <보고서.md> <보고서.html>

판정: 누락 0건이면 통과(종료 0). .md 정본의 발견ID·스킬 버전·판정 라벨 중 하나라도 HTML
  텍스트에서 빠지면 미달(종료 1). 이 도구는 읽기 전용이다 — 어떤 파일도 만들거나 고치지 않는다.

한계:
- 가시 텍스트의 '부분문자열 포함'만 본다 — 같은 ID/문구가 엉뚱한 자리에 있어도(위치 정확성)
  잡지 못한다. 위치는 .md 쪽 check_location_sampling.py의 몫이다.
- 골든 쌍(같은 검진 1건의 .md/HTML 변형) 회귀에 맞춰져 있다. 임의 실보고서 범용 게이트로
  넓히려면 HTML 골격 결합 비용(verify_html_report.py docstring 참조)을 먼저 고려할 것.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

# 정본(.md) 파싱은 형식 검증기 본체를 그대로 재사용한다 — 별도 추출 코드를 쓰면 정본 형식이
# 바뀔 때 두 곳이 어긋나(채점기는 통과, 이 도구는 false-fail) 신뢰성이 깨지기 때문.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_report_format import (  # noqa: E402
    GRADE_LINE_RE,
    VERSION_RE,
    collect_found_id_lines,
    cover_block,
    outside_fence,
    parse_found_ids,
    read_lines,
)


class _TextExtractor(HTMLParser):
    """태그를 벗기고 본문 가시 텍스트만 모은다 (엔티티는 convert_charrefs로 복원).

    비가시 영역(head·title·style·script) 안쪽은 텍스트에서 제외한다 — CSS의 클래스명·
    속성값이나 <title>처럼 본문에 안 보이는 값이 '있는 척'(거짓 통과) 하지 못하게. 이 검사가
    보는 것은 사용자가 화면에서 실제로 읽는 가시 텍스트다.

    이 태그들은 서로 중첩되므로(<head> 안에 <title>·<style>) 단일 boolean이 아니라 깊이
    카운터로 추적한다 — boolean이면 <head> 안의 </title>/</style>가 head를 벗어나기도 전에
    skip을 풀어, 그 뒤 head 내용을 본문으로 오인할 수 있다."""

    _SKIP_TAGS = frozenset({"head", "title", "style", "script"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._chunks.append(data)

    def text(self) -> str:
        return " ".join(self._chunks)


def html_visible_text(html_text: str) -> str:
    """HTML에서 태그를 벗긴 가시 텍스트를 돌려준다."""
    extractor = _TextExtractor()
    extractor.feed(html_text)
    extractor.close()
    return extractor.text()


def md_expectations(md_lines: list[str]) -> tuple[list[str] | None, str | None, str | None]:
    """정본(.md)에서 HTML이 반드시 담아야 할 것을 뽑는다.

    돌려주는 것: (발견ID 목록, 스킬 버전 'vX.Y.Z', 종합 판정 라벨).
    - 발견ID: 블록이 아예 없으면 None(형식 이상), '(없음)'이면 [](검사할 발견 없음).
    - 버전·판정 라벨: 없으면 None (비-등급 모드는 판정 라벨이 없을 수 있다)."""
    found = collect_found_id_lines(md_lines)
    ids: list[str] | None = parse_found_ids(found[0]) if found else None

    version: str | None = None
    for line in cover_block(md_lines):
        if line.strip().startswith("스킬 버전:"):
            m = VERSION_RE.search(line)
            if m:
                version = m.group(0)
            break

    label: str | None = None
    for line in outside_fence(md_lines):
        m = GRADE_LINE_RE.match(line.strip())
        if m:
            label = m.group(3)
            break

    return ids, version, label


def find_missing(md_lines: list[str], html_text: str) -> list[str]:
    """정본의 발견ID·버전·판정 라벨 중 HTML 가시 텍스트에 없는 것을 모은다."""
    ids, version, label = md_expectations(md_lines)
    text = html_visible_text(html_text)
    missing: list[str] = []

    if ids is None:
        missing.append("(.md에 '발견ID:' 블록이 없습니다 — 정본 형식을 먼저 확인하세요)")
    else:
        for the_id in ids:
            if the_id not in text:
                missing.append(f"발견ID {the_id}")

    if version is None:
        missing.append("(.md 표지에서 '스킬 버전:' 줄을 찾지 못했습니다)")
    elif version not in text:
        missing.append(f"스킬 버전 {version}")

    # 판정 라벨은 등급 모드에서만 존재한다 — 없으면(비-등급 모드) 검사를 건너뛴다.
    if label is not None and label not in text:
        missing.append(f"종합 판정 '{label}'")

    return missing


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) != 3:
        print("사용법: python check_html_md_parity.py <보고서.md> <보고서.html>")
        return 1
    try:
        md_lines = read_lines(argv[1])
        html_text = Path(argv[2]).read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        print(f"오류: 파일을 읽을 수 없습니다 - {err}")
        return 1

    missing = find_missing(md_lines, html_text)
    for m in missing:
        print(f"정본 불일치: HTML에 {m} 누락")
    print(f"누락: {len(missing)}건")
    print(f"판정: {'통과' if not missing else '미달'} "
          "(기준: .md 정본의 발견ID·스킬 버전·종합 판정이 HTML에 모두 존재)")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
