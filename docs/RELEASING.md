# 이 저장소의 릴리스 점검표 (Releasing)

> 스킬의 `release-check` 모드(사용자 프로젝트 검진)와는 다른 문서 — **이 저장소 자체**를 갱신·태그할 때의 점검표다.

버전을 올리거나 문서를 크게 바꿔 공개하기 전에 확인한다:

1. **버전 정합** — SKILL.md의 `스킬 버전:`이 단일 진실. 루트 README·README.ko·CHANGELOG·골든 보고서 표지가 일치하는지 CI(`tests/check_version.py`)가 강제하지만, 로컬에서 먼저 `python tests/run_checks.py`로 확인.
2. **영/한 README 동기화** — `README.md`(영문)와 `README.ko.md`(한국어)는 내용이 같아야 한다. 한쪽만 고쳤다면 다른 쪽도 같은 내용으로 갱신했는지 눈으로 대조한다(의미 비교는 자동화 불가 — 이 항목이 유일한 방어선).
3. **신선 드라이런** — 이 저장소를 모르는 신선한 에이전트가 **영문 README만 보고** 설치 → `tests/fixtures/messy-project` 검진 → `tests/compare_report.py` 채점 100% + 형식 검증 통과(Claude Code·git 기설치 기준, PowerShell·bash 각 1회). 시간 기준: **설치 복붙부터 설치 확인까지 1분 이내**. 검진 완주 시간은 기록만 한다(정독형 진단이라 10분 이상이 정상 — 2026-07-20 실측 12분).
4. **커밋 저자** — noreply(`207958392+Ps-Neko@users.noreply.github.com`) 확인. 개인 이메일 유입(GH007) 금지.
5. **CI green** — push 후 전체 잡(ubuntu/windows × py3.10–3.12) 통과 확인.
6. **이미지 자산** — README가 참조하는 스크린샷이 실재하고, 총용량이 과하지 않은지(GIF는 3MB 이하·15초 이내, 초과 시 정지 이미지로 대체).
