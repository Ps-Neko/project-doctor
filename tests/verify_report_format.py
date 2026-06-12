"""보고서가 결과지 형식 계약(report-template.md)을 지켰는지 기계 검사한다.

compare_report.py가 "무엇을 찾았는가"(탐지율·오탐)를 채점한다면,
이 스크립트는 "보고서가 약속된 모양인가"(형식 계약)를 검사한다.

모드 공통 검사: 표지(제목 헤딩·환자 줄·스킬 버전 줄·모드 표기),
  기계 판독 발견ID 블록(맨 마지막 줄)·ID 형식, 비밀키 값 노출 휴리스틱.
건강검진·공개 전 검진 한정: 종합 판정(등급↔표현 고정표 정합),
  부위별 소견·오늘의 처방, 발견이 있으면 4요소 라벨 개수 일치.
건강검진 한정: 숙제 줄 (v2.0부터의 계약 — 보고서의 스킬 버전이 v2 미만이면 건너뜀).
판정 = 형식 위반 0건.
"""
import re
import sys
from pathlib import Path

EMPTY_MARK: str = "(없음)"
ID_RE = re.compile(r"^[A-Z]+-\d{2,}$")
VERSION_RE = re.compile(r"스킬 버전:.*v(\d+)\.\d+\.\d+")

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

# 4요소 라벨 (5절 — 발견 항목마다 4줄)
FOUR_FIELDS: tuple[str, ...] = ("무슨 뜻인가요?", "어디?", "고치면?", "승인 명령:")

# 비밀키 값 노출 휴리스틱 — 위치 보고는 허용, 값을 옮겨 적으면 위반 (절대 규칙 4)
# 오탐을 줄이기 위해 확신 높은 패턴만 사용한다.
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS 액세스 키", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("개인키 블록", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub 토큰", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("Slack 토큰", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("API 시크릿 키", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
)


def read_lines(path: str) -> list[str]:
    # utf-8-sig: PowerShell 5.1 등이 만드는 BOM 붙은 UTF-8도 그대로 읽는다.
    return Path(path).read_text(encoding="utf-8-sig").splitlines()


def detect_major_version(lines: list[str]) -> int | None:
    """표지의 '스킬 버전' 줄에서 주 버전 숫자를 읽는다 (없으면 None)."""
    match = VERSION_RE.search("\n".join(lines))
    return int(match.group(1)) if match else None


def detect_mode(lines: list[str]) -> str | None:
    """표지 제목 헤딩에서 모드를 알아낸다 (없으면 None)."""
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue
        for title, mode in TITLE_TO_MODE.items():
            if title in stripped:
                return mode
    return None


def find_last_content_line(lines: list[str]) -> str:
    for line in reversed(lines):
        if line.strip():
            return line.strip()
    return ""


def parse_found_ids(last_line: str) -> list[str] | None:
    """맨 마지막 줄의 발견ID 블록을 파싱한다. 블록이 아니면 None."""
    if not last_line.startswith("발견ID:"):
        return None
    body = last_line.split(":", 1)[1].strip()
    if not body or body == EMPTY_MARK:
        return []
    return [part.strip() for part in body.split(",")]


def check_cover(lines: list[str], violations: list[str]) -> None:
    text = "\n".join(lines)
    if detect_mode(lines) is None:
        violations.append(
            "FORM-01 표지 제목 헤딩이 없거나 모드 표지 제목(결과지/차트/계획서)이 아닙니다")
    if not any(ln.strip().startswith("환자:") for ln in lines):
        violations.append("FORM-02 표지의 '환자:' 줄이 없습니다")
    if not VERSION_RE.search(text):
        violations.append("FORM-03 '스킬 버전: vX.Y.Z' 줄이 없습니다")
    if not any("모드:" in ln for ln in lines):
        violations.append("FORM-04 표지의 '모드:' 표기가 없습니다")


def check_machine_block(lines: list[str], violations: list[str]) -> list[str]:
    last = find_last_content_line(lines)
    ids = parse_found_ids(last)
    if ids is None:
        violations.append(
            "FORM-05 보고서 맨 마지막 줄이 '발견ID:' 블록이 아닙니다 (9절 계약)")
        return []
    bad = [i for i in ids if not ID_RE.match(i)]
    if bad:
        violations.append(
            f"FORM-06 발견ID 형식 위반 (대문자-두자리 숫자 아님): {', '.join(bad)}")
    return ids


def check_grade(lines: list[str], violations: list[str]) -> None:
    if not any(ln.strip() == "## 종합 판정" for ln in lines):
        violations.append("FORM-07 '## 종합 판정' 절이 없습니다")
        return
    for line in lines:
        match = GRADE_LINE_RE.match(line.strip())
        if not match:
            continue
        light, grade, label = match.groups()
        want_light, want_label = GRADE_TABLE[grade]
        if light != want_light or label != want_label:
            violations.append(
                f"FORM-07 등급↔표현 고정표 위반: {grade}는 "
                f"'{want_light} {grade} — {want_label}'여야 하는데 "
                f"'{light} {grade} — {label}'로 적혔습니다")
        return
    violations.append("FORM-07 종합 판정의 등급 줄(`# 🔴 D — ...`)이 없습니다")


def check_body_sections(lines: list[str], violations: list[str]) -> None:
    text = "\n".join(lines)
    for section in ("## 부위별 소견", "## 오늘의 처방"):
        if section not in text:
            violations.append(f"FORM-08 '{section}' 절이 없습니다")
    if not any(ln.strip().startswith("진단 결과:") for ln in lines):
        violations.append("FORM-08 오늘의 처방의 '진단 결과:' 줄이 없습니다")


def check_four_fields(lines: list[str], ids: list[str],
                      violations: list[str]) -> None:
    if not ids:
        return
    text = "\n".join(lines)
    counts = {field: text.count(field) for field in FOUR_FIELDS}
    missing = [f for f, n in counts.items() if n == 0]
    if missing:
        violations.append(
            f"FORM-09 발견이 있는데 4요소 라벨 누락: {', '.join(missing)}")
        return
    if len(set(counts.values())) != 1:
        pretty = ", ".join(f"{f} {n}개" for f, n in counts.items())
        violations.append(
            f"FORM-09 4요소 라벨 개수 불일치 (본문 항목마다 4줄 의무): {pretty}")


def check_homework(lines: list[str], violations: list[str]) -> None:
    if not any(ln.strip().startswith("숙제:") for ln in lines):
        violations.append("FORM-10 '숙제:' 줄이 없습니다 (8절 기계 판독 계약)")


def check_secrets(lines: list[str], violations: list[str]) -> None:
    text = "\n".join(lines)
    for name, pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            # 위반 메시지에도 값 전체를 다시 옮겨 적지 않는다 (앞 8자만).
            violations.append(
                f"FORM-11 비밀키 값 노출 의심 ({name}): "
                f"'{match.group()[:8]}…' — 보고서에는 위치만 적어야 합니다")


def verify(lines: list[str]) -> list[str]:
    violations: list[str] = []
    mode = detect_mode(lines)
    check_cover(lines, violations)
    ids = check_machine_block(lines, violations)
    if mode in GRADED_MODES:
        check_grade(lines, violations)
        check_body_sections(lines, violations)
        check_four_fields(lines, ids, violations)
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
