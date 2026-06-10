# EXPECTED.md — handover-project 정답지

이 파일은 "프로젝트 주치의" 스킬 자체 테스트의 정답지로, 초진 차트(intro-chart) 작성·검진 시 진단 대상에서 제외된다.

## 픽스처 개요

- 콘셉트: "재고 알림 미니 도구" — **문서가 전혀 없지만(README 없음) 실제로 동작하는** 소형 프로젝트.
- 용도: intro-chart(해설 차트)가 코드만 보고 ①핵심 파일 지도 ②실행 방법 ③위험 구역 ④미완성 구간을 맞히는지 검증.
- 주의: README 없음은 **의도적으로 심은 상태**다. 차트가 "문서 없음"을 지적하는 것은 정상이며 오탐이 아니다.

## 정답

### ① 핵심 파일과 역할 (전부 5개)

| 순서 | 파일 | 역할 (일상 언어) |
|------|------|-----------------|
| 1부터 보세요 | inventory.py | 프로그램의 시작점 — settings.json을 읽고, data/stock.csv를 읽고, 임계값 미만 품목을 콘솔에 출력하는 전체 흐름 |
| 2 | stock_rules.py | 품목별 "이 숫자 미만이면 부족" 기준표(ITEM_THRESHOLDS). inventory.py가 import |
| 3 | settings.json | 기본 임계값(default_threshold=10)·CSV 경로·인코딩 설정 |
| 4 | notify.py | 알림 전송 모듈 — 함수 2개 전부 TODO 스텁(미구현). inventory.py가 import만 하고 호출은 안 함 |
| 5 | data/stock.csv | 샘플 재고 데이터 7행 (item/quantity/unit) |

### ② 실행 명령 정답

- `python inventory.py` (프로젝트 루트에서 실행, 표준 라이브러리만 사용 — 별도 설치 불필요)
- 정상 실행 시 출력: 전체 7개 품목 중 4개가 부족 — A4용지(12<20), 토너(3<5), 스테이플러(8<10), 포스트잇(6<10)

### ③ 위험 구역 정답 (2곳)

| 위치 | 왜 위험한가 |
|------|------------|
| settings.json | JSON 형식이 깨지거나(쉼표·따옴표 실수) 필수 키(default_threshold, csv_path, csv_encoding)가 빠지면 실행 자체가 즉시 중단된다 |
| stock_rules.py의 ITEM_THRESHOLDS | 품목별 임계값 숫자 — 잘 모르고 바꾸면 알림이 과다하게 울리거나 부족을 놓친다. 에러 없이 조용히 잘못 동작하는 유형 |

### ④ 미완성 구간 정답

- notify.py 전체 — send_email_alert / send_messenger_alert 둘 다 TODO 스텁(NotImplementedError만 던짐)
- inventory.py의 `# TODO: notify.send_email_alert(...) 연결` 주석 — 알림 연결이 보류된 흔적

## 판정 기준

1. **실행 도달**: 제3자가 작성된 해설 차트만 보고(코드를 열지 않고) `python inventory.py` 실행까지 도달할 수 있어야 한다.
2. **실행 명령 일치**: 차트에 적힌 실행 명령이 정답(`python inventory.py`)과 일치해야 한다. intro-chart는 정적 추정만 하므로 "(추정 — 직접 실행해 확인한 것은 아님)" 표기는 허용.
3. (보조 가점) 위험 구역에 settings.json 포함 + 미완성 구간에 notify.py 포함이면 가점. 핵심 파일 지도에 위 5개가 모두 등장하면 만점.
