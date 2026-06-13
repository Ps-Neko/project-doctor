"""보고서가 결과지 형식 계약(report-template.md)을 지켰는지 기계 검사한다.

compare_report.py가 "무엇을 찾았는가"(탐지율·오탐)를 채점한다면,
이 스크립트는 "보고서가 약속된 모양인가"(형식 계약)를 검사한다.

모드 공통 검사: 표지(제목 헤딩·환자 줄·스킬 버전 줄·모드 표기),
  기계 판독 발견ID 블록(맨 마지막 줄, 정확히 1개)·ID 형식, 비밀키 값 노출 휴리스틱.
건강검진·공개 전 검진 한정: 종합 판정(등급↔표현 고정표 정합),
  부위별 소견·오늘의 처방, 발견이 있으면 발견 항목마다 4요소 라벨.
건강검진 한정: 숙제 줄 (v2.0부터의 계약 — 보고서의 스킬 버전이 v2 미만이면 건너뜀).
판정 = 형식 위반 0건.

코드펜스(```) 처리: 등급·절·4요소 검사는 펜스 안(템플릿 예시 인용)을 무시한다 —
  펜스 안 올바른 예시가 펜스 밖 실제 위반을 가리지 못하게 하기 위함.
"""
import re
import sys
from pathlib import Path

EMPTY_MARK: str = "(없음)"
ID_RE = re.compile(r"^[A-Z]+-\d{2,}$")
VERSION_RE = re.compile(r"v(\d+)\.\d+\.\d+")

# 표지 제목 → 모드 (report-template.md 1절 표)
TITLE_TO_MODE: dict[str, str] = {
    "프로젝트 건강검진 결과지": "checkup",
    "프로젝트 초진 차트": "intro",
    "프로젝트 방향전환 계획서": "pivot",
    "공개 전 검진 결과지": "release-check",
}
GRADED_MODES = {"checkup", "release-check"}  # 종합 판정이 의무인 모드

# 등급↔표현 고정표 (report-template.md 2절 — 이 표 밖의 표현 금지)
GRADE_TABLE: dict[str, tuple[str, str]] = {
    "A": ("🟢", "건강해요"),
    "B": ("🟢", "양호해요"),
    "C": ("🟡", "주의가 필요해요"),
    "D": ("🔴", "치료가 필요해요"),
}
GRADE_LINE_RE = re.compile(r"^#\s*(🟢|🟡|🔴)\s*([ABCD])\s*—\s*(.+?)\s*$")
FINDING_HEAD_RE = re.compile(r"^###\s+(🔴|🟡|⚪)")
# 발견 항목 제목에 든 카탈로그 ID (예: `[DUP-01]`) — report-template 5절은 제목에 ID 필수.
TITLE_ID_RE = re.compile(r"\[[A-Z]+-\d{2,}\]")

# 4요소 라벨 (5절 — 발견 항목마다 4줄)
FOUR_FIELDS: tuple[str, ...] = ("무슨 뜻인가요?", "어디?", "고치면?", "승인 명령:")

# 비밀키 값 노출 휴리스틱 — 위치 보고는 허용, 값을 옮겨 적으면 위반 (절대 규칙 4).
# 확신 높은 접두사 패턴 위주. 한계: 접두사 없는 고엔트로피 시크릿(AWS 시크릿 액세스 키 40자,
# 일반 password= 값 등)은 거짓양성 위험이 커서 다루지 않는다 — '통과'가 키 부재를 보증하진 않는다.
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS 액세스 키 ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("개인키 블록", re.compile(r"-----BEGIN[\sA-Z]{0,40}PRIVATE KEY-----")),
    ("GitHub 토큰", re.compile(r"\bgh[opsru]_[A-Za-z0-9]{36,255}\b")),
    ("GitHub 세분화 PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("Google API 키", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Slack 토큰", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("API 시크릿 키", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
)


def read_lines(path: str) -> list[str]:
    # utf-8-sig: BOM 흡수. errors=replace: cp949(ANSI) 보고서도 트레이스백 없이 읽는다.
    return Path(path).read_text(encoding="utf-8-sig", errors="replace").splitlines()


def outside_fence(lines: list[str]) -> list[str]:
    """코드펜스(```) 밖의 줄만 (원본 그대로) 돌려준다.

    등급·절·4요소 검사는 템플릿 예시 인용(펜스 안)을 검사 대상에서 빼야,
    펜스 안 올바른 예시가 펜스 밖 실제 위반을 가리는 우회를 막을 수 있다.
    """
    result, in_fence = [], False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(line)
    return result


def detect_major_version(lines: list[str]) -> int | None:
    """'스킬 버전:'으로 시작하는 표지 줄에서 주 버전을 읽는다 (없으면 None).

    줄머리 한정이라 본문의 과거 버전 언급('이전 보고서는 스킬 버전: v1.0.0…')에 속지 않는다.
    """
    for line in lines:
        if line.strip().startswith("스킬 버전:"):
            m = VERSION_RE.search(line)
            if m:
                return int(m.group(1))
    return None


def detect_mode(lines: list[str]) -> str | None:
    """표지 제목 헤딩에서 모드를 알아낸다 (펜스 밖 # 헤딩, 없으면 None)."""
    for line in outside_fence(lines):
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue
        for title, mode in TITLE_TO_MODE.items():
            if title in stripped:
                return mode
    return None


def collect_found_id_lines(lines: list[str]) -> list[str]:
    """'발견ID:'로 시작하는 줄을 모은다 (**코드펜스 밖만** — 실제 기계 판독 줄은 raw 한 줄).

    템플릿 9절은 발견ID 블록 예시를 펜스로 감싸 보여주지만, 실제 산출 보고서의
    기계 판독 줄은 펜스 없는 raw line이다. 채점기(compare_report.parse_report_ids)도
    펜스 안을 무시하므로 — 두 검사기의 계약을 일치시킨다(펜스 안 발견ID를 실제 블록으로
    오인하면 verify는 통과시키는데 compare는 0% 처리하는 모순이 생긴다)."""
    out: list[str] = []
    for line in outside_fence(lines):
        stripped = line.strip()
        if stripped.startswith("발견ID:"):
            out.append(stripped)
    return out


def find_last_content_line(lines: list[str]) -> str:
    """마지막 내용 줄을 찾는다 (**코드펜스 밖만** — raw 기계 판독 줄 계약).

    발견ID 블록이 보고서 맨 마지막 줄인지 검사하는 데 쓰인다. 펜스 안 예시 줄은
    실제 내용이 아니므로 마지막 줄 판정에서 제외한다(collect_found_id_lines와 동일 계약)."""
    last = ""
    for line in outside_fence(lines):
        stripped = line.strip()
        if stripped:
            last = stripped
    return last


def parse_found_ids(found_line: str) -> list[str]:
    body = found_line.split(":", 1)[1].strip()
    if not body or body == EMPTY_MARK:
        return []
    return [part.strip() for part in body.split(",")]


def check_cover(lines: list[str], violations: list[str]) -> None:
    # 표지는 코드블록 안에 들어가므로 펜스를 가르지 않고 전체에서 본다.
    if detect_mode(lines) is None:
        violations.append(
            "FORM-01 표지 제목 헤딩이 없거나 모드 표지 제목(결과지/차트/계획서)이 아닙니다")
    if not any(ln.strip().startswith("환자:") for ln in lines):
        violations.append("FORM-02 표지의 '환자:' 줄이 없습니다")
    if not any(ln.strip().startswith("스킬 버전:") for ln in lines):
        violations.append("FORM-03 '스킬 버전: vX.Y.Z' 줄이 없습니다")
    if not any("모드:" in ln for ln in lines):
        violations.append("FORM-04 표지의 '모드:' 표기가 없습니다")


def check_machine_block(lines: list[str], violations: list[str]) -> list[str]:
    found = collect_found_id_lines(lines)
    if not found:
        violations.append("FORM-05 보고서에 '발견ID:' 블록이 없습니다 (9절 계약)")
        return []
    if len(found) > 1:
        violations.append(
            f"FORM-05 '발견ID:' 줄이 여러 개입니다({len(found)}개) — 보고서 끝에 하나만 두세요 "
            "(본문/부록의 예시 발견ID 줄과 실제 블록이 섞이면 채점이 오염됩니다)")
        return []
    if find_last_content_line(lines) != found[0]:
        violations.append(
            "FORM-05 '발견ID:' 블록이 보고서 맨 마지막 줄이 아닙니다 (9절 계약)")
        return []
    ids = parse_found_ids(found[0])
    bad = [i for i in ids if not ID_RE.match(i)]
    if bad:
        violations.append(
            f"FORM-06 발견ID 형식 위반 (대문자-두자리 숫자 아님): {', '.join(bad)}")
    return ids


def check_grade(lines: list[str], violations: list[str]) -> None:
    content = outside_fence(lines)
    if not any(ln.strip().startswith("## 종합 판정") for ln in content):
        violations.append("FORM-07 '## 종합 판정' 절이 없습니다")
        return
    found_grade = False
    for line in content:  # 첫 줄에서 멈추지 않고 펜스 밖 등급 줄을 전수 검사
        match = GRADE_LINE_RE.match(line.strip())
        if not match:
            continue
        found_grade = True
        light, grade, label = match.groups()
        want_light, want_label = GRADE_TABLE[grade]
        if light != want_light or label != want_label:
            violations.append(
                f"FORM-07 등급↔표현 고정표 위반: {grade}는 "
                f"'{want_light} {grade} — {want_label}'여야 하는데 "
                f"'{light} {grade} — {label}'로 적혔습니다")
    if not found_grade:
        violations.append("FORM-07 종합 판정의 등급 줄(`# 🔴 D — ...`)이 없습니다")


def check_body_sections(lines: list[str], violations: list[str]) -> None:
    headings = [ln.strip() for ln in outside_fence(lines)]
    for section in ("## 부위별 소견", "## 오늘의 처방"):
        if not any(h.startswith(section) for h in headings):
            violations.append(f"FORM-08 '{section}' 절이 없습니다")
    if not any(h.startswith("진단 결과:") for h in headings):
        violations.append("FORM-08 오늘의 처방의 '진단 결과:' 줄이 없습니다")


def check_four_fields(lines: list[str], ids: list[str], machine_ok: bool,
                      violations: list[str]) -> None:
    content = outside_fence(lines)
    finding_blocks: list[list[str]] = []
    finding_titles: list[str] = []
    current: list[str] | None = None
    for line in content:
        if FINDING_HEAD_RE.match(line.strip()):
            current = []
            finding_blocks.append(current)
            finding_titles.append(line.strip())
        elif current is not None:
            current.append(line)

    if not ids:
        # 발견ID가 명시적 '(없음)'인데 본문에 발견 항목이 있으면 모순(사람용 본문 ↔ 기계 블록 불일치).
        # 단, 기계 블록이 형식 위반(FORM-05/06)으로 ids를 못 읽은 경우는 그 위반이 이미 보고됐으므로
        # 여기서 중복 보고하지 않는다 (machine_ok가 False면 ids=[]는 '실패'이지 '(없음)'이 아님).
        if machine_ok and finding_blocks:
            violations.append(
                "FORM-09 발견ID는 (없음)인데 본문에 발견 항목(### 🔴/🟡/⚪)이 있습니다")
        return

    if not finding_blocks:
        violations.append(
            "FORM-09 발견이 있는데 본문에 발견 항목(### 🔴/🟡/⚪ ...)이 없습니다")
        return
    # 발견 항목마다 ① 제목에 카탈로그 ID([DUP-01] 형식) ② 4요소 라벨이 그 블록 안에 있는지
    # 항목별로 검사 (전체 개수 합산이 아니라). 제목 ID는 재검진 비교·승인 명령 추적의 토대다.
    for idx, (title, block) in enumerate(zip(finding_titles, finding_blocks), 1):
        if not TITLE_ID_RE.search(title):
            violations.append(
                f"FORM-09 발견 {idx}번 항목 제목에 카탈로그 ID([DUP-01] 형식)가 없습니다: "
                f"{title[:40]}")
        btext = "\n".join(block)
        missing = [f for f in FOUR_FIELDS if f not in btext]
        if missing:
            violations.append(
                f"FORM-09 발견 {idx}번 항목에 4요소 라벨 누락: {', '.join(missing)}")


def check_homework(lines: list[str], violations: list[str]) -> None:
    # 코드펜스 밖만 — 템플릿 예시(펜스 안 `숙제: HARD-01`)가 실제 숙제 줄을 대신하지 못하게 한다.
    content = outside_fence(lines)
    homework = [ln for ln in content if ln.strip().startswith("숙제:")]
    if not homework:
        violations.append("FORM-10 '숙제:' 줄이 없습니다 (8절 기계 판독 계약)")
    elif len(homework) > 1:
        violations.append(
            f"FORM-10 '숙제:' 줄이 여러 개입니다({len(homework)}개) — 8절 계약상 하나만 두세요")


def check_secrets(lines: list[str], violations: list[str]) -> None:
    # 비밀키는 펜스 안이든 밖이든 노출이면 위반 — 전체 텍스트를 본다.
    text = "\n".join(lines)
    for name, pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            violations.append(
                f"FORM-11 비밀키 값 노출 의심 ({name}): "
                f"'{match.group()[:8]}…' — 보고서에는 위치만 적어야 합니다")


def verify(lines: list[str]) -> list[str]:
    violations: list[str] = []
    mode = detect_mode(lines)
    check_cover(lines, violations)
    before = len(violations)
    ids = check_machine_block(lines, violations)
    machine_ok = len(violations) == before  # 발견ID 블록 검사가 위반 없이 통과했는가
    if mode in GRADED_MODES:
        check_grade(lines, violations)
        check_body_sections(lines, violations)
        check_four_fields(lines, ids, machine_ok, violations)
    major = detect_major_version(lines)
    if mode == "checkup" and (major is None or major >= 2):
        check_homework(lines, violations)
    check_secrets(lines, violations)
    return violations


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if len(argv) != 2:
        print("사용법: python verify_report_format.py <보고서.md>")
        return 1
    try:
        lines = read_lines(argv[1])
    except OSError as err:
        print(f"오류: 파일을 읽을 수 없습니다 - {err}")
        return 1
    mode = detect_mode(lines)
    violations = verify(lines)
    print(f"모드: {mode if mode else '식별 불가'}")
    for v in violations:
        print(f"형식 위반: {v}")
    print(f"위반: {len(violations)}건")
    print(f"판정: {'통과' if not violations else '미달'} (기준: 형식 위반 0건)")
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
