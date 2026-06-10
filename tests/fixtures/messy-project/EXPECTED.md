# EXPECTED.md — messy-project 정답지

이 파일은 "프로젝트 주치의" 스킬 자체 테스트의 정답지로, 검진 시 진단 대상에서 제외된다(SKILL.md 절대 규칙 9).

## 대조 절차

1. 검진 보고서 마지막 줄 `발견ID:` 에서 ID 목록을 추출한다.
2. 다음 명령을 실행한다:
   `python tests/compare_report.py <보고서> <이 파일>` (저장소 루트에서 실행)
3. 탐지율 = (아래 "심은 문제" 중 보고서에 나온 ID 수) ÷ 14.

## 심은 문제 (14건)

| ID | 위치 | 심각도 |
|----|------|--------|
| DUP-01 | calc_order_total() 함수(8줄 이상, 주문 합계 계산)가 main.py / utils.py / helpers.py 3곳에 사실상 동일하게 복사됨 | 🔴 (3곳 + 돈 계산) |
| DEAD-01 | utils.py의 legacy_discount() 함수 — 정의만 있고 어디서도 호출·참조하지 않음 | 🟡 |
| DEAD-02 | helpers.py 안에 주석 처리된 옛 구현 약 15줄 (# 으로 막힌 코드 형태) | ⚪ (10~29줄) |
| BIG-01 | static_data.js — 850줄 이상. 상품 데이터 배열 + 조회 함수가 섞인 코드 파일 (함수 5개 이상 포함, 데이터 전용 아님) | 🟡 |
| BIG-02 | main.py의 process_orders() 함수 약 70줄 (50~99줄 구간) | ⚪ |
| BIG-03 | helpers.py의 flag_risky_orders() — for/if 4단계 초과 중첩 (함수 전체는 약 17줄로 50줄 미만, BIG-02 미발동) | ⚪ |
| HARD-01 | main.py에 하드코딩 절대 경로 r"C:\Users\kim\Desktop\orders\data.csv" 를 실행 경로에 사용 | 🔴 |
| HARD-03 | helpers.py의 ORDERS_API_URL = "http://192.168.0.10/api/orders" — 실제 사용되는 코드 줄(flag_risky_orders가 참조)에 내부 IP 주소 하드코딩 | 🟡 |
| DOC-01 | README 파일 없음 | 🔴 |
| DOC-03 | utils.py가 import requests 를 사용하는데 requirements.txt·pyproject.toml 없음 | 🟡 |
| TEST-01 | 테스트 파일·폴더 0건 | 🟡 |
| TMP-01 | old_main.py.bak (약 30줄, main.py의 옛 사본) | 🟡 |
| STALE-01 | TODO/FIXME 주석 합계 6건 — main.py 3건(TODO 2 + FIXME 1) + helpers.py 3건(TODO 2 + FIXME 1), 임계값 5건 이상 | ⚪ |
| STALE-02 | test123.py (약 12줄 실험 코드, 어떤 파일도 이것을 import·참조하지 않음) | 🟡 |

## 오탐 금지 목록

다음 6개 파일은 정상이다. 이 파일들이 문제로 보고되면 오탐이다:

- order_utils.js (~25줄 깔끔한 모듈 — index.html이 script src로 참조)
- config.json (정상 설정 — webhook_url은 example.com이라 HARD-03 제외 대상)
- 보고서 초안.md (한글 파일명 메모 — 한글 처리 검증용)
- data/orders.csv (소형 샘플 데이터)
- index.html (static_data.js·order_utils.js를 script src로 참조하는 평범한 페이지 — DEAD-03 오탐 방지용 연결 파일)
- package.json (name/version + dependencies에 lodash만 선언 — 기본 검진에서는 문제 아님)

## 추가 보고 허용 (채점 중립)

아래 ID는 카탈로그 기준상 정당한 발견이지만 "심은 문제" 14건에는 포함하지 않는다 — 보고돼도 오탐이 아니고, 빠져도 감점이 없다:

- HARD-02 — DUP-01(3벌 복사)의 부산물로 50000·30000·3000·0.05 가 main.py/utils.py/helpers.py에 각 3회 반복됨
- STRUCT-03 — static_data.js가 데이터 파일 이름인데 조회 함수(로직)를 포함함

## 정밀 검진(--deep) 추가 정답

이 절은 **기본 검진 채점(compare_report.py)에 포함되지 않는다** — compare_report.py는 "## 심은 문제" 표만 읽으므로, 아래 표는 --deep 실행 결과를 사람이 별도로 확인할 때만 쓴다.

| ID | 위치 | 심각도 |
|----|------|--------|
| HIST-01 | main.py — 원본에는 git 이력이 없으므로 기본 상태에서는 측정 불가. tests/fixtures/setup-git-history.ps1 을 "검사용 사본"에 실행한 뒤에만 측정 가능 (첫 커밋 후 main.py만 5회 수정된 핫스팟 이력) | 🟡 |
| DEP-01 | package.json의 dependencies에 선언된 lodash — 코드 어디서도 require·import하지 않음 ("설치만 해두고 안 먹는 약") | 🟡 |

## 통과 기준

- 14건 중 80% 이상 탐지 (12건 이상)
- 오탐 0건 — "심은 문제"·"추가 보고 허용" 어디에도 없는 ID가 보고되면 compare_report.py가 자동으로 미달 처리한다
- 단, 정식 측정은 3회 실행 최저치 기준
- 정밀 검진(--deep) 추가 정답 2건은 위 채점에 포함하지 않는다
