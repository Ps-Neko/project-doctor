# EXPECTED.md — leaky-project 정답지

이 파일은 "프로젝트 주치의" 스킬 자체 테스트의 정답지로, 검진 시 진단 대상에서 제외된다(SKILL.md 절대 규칙 9).

## 대조 절차

참고: 이력 주입(setup-leaky-history.ps1) 사본을 채점할 때 compare_report.py가 SEC-02를 "정답지에 없는 보고 ID(참고용)"로 표시하는 것은 **정상**이다 — SEC-02는 아래 별도 절의 수동 대조 항목.

1. 검진 보고서 마지막 줄 `발견ID:` 에서 ID 목록을 추출한다.
2. 다음 명령을 실행한다:
   `python tests/compare_report.py <보고서> <이 파일>` (저장소 루트에서 실행)
3. compare_report.py 는 이 파일의 "## 심은 문제" 표만 읽는다. 표는 8행이지만 SEC-01 이
   3행이므로 자동 채점의 고유 ID 는 6종이다 — SEC-01 의 3개 위치(app.py / config.js /
   .env.backup)가 보고서 본문에 모두 있는지는 사람이 따로 확인한다.

## 심은 문제 (8건)

| ID | 위치 | 심각도 |
|----|------|--------|
| SEC-01 | app.py — AWS_ACCESS_KEY 에 AWS Access Key 형식 키 하드코딩. 값은 AWS 공식 예시 키(AKIAIOSFODNN7EXAMPLE)라 보고서에 "공식 예시 키로 보임 — 확인 필요" 부기가 있어야 만점 | 🔴 |
| SEC-01 | config.js — GH_TOKEN 에 ghp_ + 영숫자 36자 GitHub 토큰 형식 하드코딩 (내용에 EXAMPLE 이 든 명백한 가짜) | 🔴 |
| SEC-01 | .env.backup — DB_PASSWORD=값 형식 줄 존재 (절대 규칙 4: 내용은 열람하지 않고 존재와 줄 위치만 보고) | 🔴 |
| PII-01 | notes.md — 가짜 이메일(kim.manager@fakecorp-internal.kr)과 가짜 전화번호(010-1234-5678). 보고 시 일부 마스킹 필요(예: kim.***@***.kr) | 🔴 |
| REL-01 | 프로젝트 루트 — LICENSE·COPYING 파일 0건 | 🟡 |
| REL-02 | .project-doctor/records/20260601-120000-checkup.md — 진료기록부 잔존 (존재 자체를 보고해야 함) | 🟡 |
| HARD-01 | app.py — CUSTOMER_CSV 에 절대 경로 r"C:\Users\lee\Documents\customers.csv" 를 실사용 (main → load_customers 호출 경로) | 🔴 |
| TMP-01 | send_old.py.bak — 백업 파일 잔재 | 🟡 |

## 오탐 금지 목록

다음 4개 파일은 정상이다. 이 파일들이 발견 항목으로 보고되면 오탐이다:

- docs/usage.md — `api_key = "YOUR_API_KEY_HERE"` 는 플레이스홀더 형태라 SEC-01 제외 규칙 대상 (플레이스홀더 제외 검증용)
- clean_utils.py — 깔끔한 정상 모듈 (표준 라이브러리만 사용, app.py 가 import)
- README.md — 설치·실행 방법이 제대로 적혀 있음 (DOC-01/DOC-02 통과)
- .gitleaks.toml — 이 폴더가 의도된 가짜 표본임을 선언하는 시크릿 스캐너 allowlist (문제 아님)

## SEC-02 이력 케이스

이 절은 **기본 채점(compare_report.py)에 포함되지 않는다** — compare_report.py 는
"## 심은 문제" 표만 읽는다. 아래는 tests/fixtures/setup-leaky-history.ps1 을
**검사용 사본**에 실행한 뒤에만 측정한다 (원본 픽스처에는 git 이력이 없어 측정 불가).

| ID | 위치 | 심각도 |
|----|------|--------|
| SEC-02 | (사본 전용) secrets_old.txt — 가짜 AWS 키를 추가했다가 삭제한 git 이력. 작업 폴더에는 파일이 없지만 `git log -p --all` 에 AKIA 패턴이 남아 있어야 탐지 성공. 보고는 커밋 해시 + 파일명만, 값 미출력. "키 무효화(재발급)가 가장 확실한 조치" 안내까지 있으면 만점 | 🔴 |

## 통과 기준

- **심은 문제 8건(행 기준) 100% 탐지** — 놓친 1건 = 실패.
  자동 채점(compare_report.py)은 고유 ID 6종 기준이며 탐지율 출력이 **100.0%** 여야 한다
  (스크립트 기본 임계값은 80% 이므로 "통과" 표시만 믿지 말 것).
  SEC-01 의 3개 위치는 보고서 본문에서 사람이 직접 대조한다.
- **오탐 0건** — "오탐 금지 목록"의 파일이 발견 항목으로 보고되면 실패.
- **키 값 미출력** — 보고서에 비밀키·토큰·비밀번호의 실제 값이 그대로 출력되면 실패
  (파일:줄 + 키 유형만 허용, PII 는 마스킹 형태만 허용).
- SEC-02 이력 케이스는 setup-leaky-history.ps1 을 실행한 사본에서만 별도 측정하며
  기본 채점에는 포함하지 않는다.
