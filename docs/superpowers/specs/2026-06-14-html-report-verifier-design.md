# 설계 — HTML 결과지 보안 검증기 (`verify_html_report.py`)

- 작성일: 2026-06-14
- 대상 버전: dev v2.7.7 → **v2.7.8**
- 배경 BL: [BACKLOG.md] BL-31 (보류였으나 사용자가 트리거 전 강행 결정)

## 1. 배경 — 닫으려는 갭

`report-formats.md`는 HTML/PDF 결과지를 **코드가 아니라 모델이 골격을 보고 직접 작성**하게 하고, 신뢰불가 값(분석 대상 프로젝트의 파일명·코드 조각·소견)의 HTML 이스케이프를 **프롬프트 규칙**(§2 절대 준수)으로만 강제한다. `.md` 보고서엔 형식검증기 `verify_report_format.py`(FORM-xx)가 완성본을 자동 검사하지만, **HTML/PDF는 검사 대상 밖**이라 §5가 "사람(Claude)이 직접 대조한다"고 자인한다.

이 비대칭 = 갭. 본 설계는 그 자가 대조를 **코드로** 옮긴다. 위협 시나리오: 악성 파일명 `</style><img src=x onerror=…>.py`가 이스케이프 없이 박히면, 사용자가 `.html`을 더블클릭하거나 PDF 변환(headless 브라우저가 `file://` 로드)할 때 그 마크업이 실행된다.

## 2. 역할 (결정: 스킬 배포 + 실제 보고서 검사)

- 위치: `skills/project-doctor/tools/verify_html_report.py` — **스킬과 함께 배포**되어 실행 중 호출 (`check_write_boundary.py`와 동일한 자리·역할).
- 호출 시점: 스킬이 HTML 결과지를 쓴 직후·저장 전. 위반이 있으면 저장을 멈추고 이스케이프를 고친 뒤 재검사.
- `report-formats.md` §2/§5가 이 호출을 절차로 지시한다(완전 강제는 아님 — 아래 한계 참조).

## 3. 계약 (CLI)

```
python verify_html_report.py <보고서.html>
```

- 종료 코드: **0 = 통과(위반 0건)**, **1 = 미달(위반 ≥1건) 또는 사용법/읽기 오류**.
- 출력: 한국어. 위반마다 `보안 위반: HTML-xx …` 한 줄 + 끝에 `위반: N건` / `판정: 통과|미달`. `verify_report_format.py main()` 출력 형식을 따른다.
- 의존성 **0** (순수 stdlib: `html.parser`, `re`, `sys`). `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 적용.

## 4. 검사 항목 — 허용목록 fail-closed (`HTML-xx`)

| 코드 | 검사 | 판정 근거 |
|------|------|-----------|
| HTML-01 | **허용목록 밖 태그** | `report-formats.md` 골격에 실제로 쓰이는 태그만 허용. 그 외 전부 위반 → 주입된 낯선 태그(script/img/iframe/object/embed/svg/link/base/form/meta-refresh 등)를 모두 잡음 |
| HTML-02 | **이벤트 핸들러 속성** | 어떤 태그든 `on`으로 시작하는 속성(onerror/onload/onclick …) = 위반 |
| HTML-03 | **외부 리소스** | `src=`, 외부 `href=`(http(s):·`//`·기타 외부 스킴), CSS `@import`, `url(http…)`·`url(//…)` = 위반 (자기완결 의무: CDN·웹폰트·외부 이미지·링크 CSS/JS 금지) |
| HTML-04 | **위험 URI 스킴** | 속성값이 `javascript:` 또는 `data:`로 시작 = 위반 |
| HTML-05 | **charset 메타 부재** | `<meta charset="utf-8">`(대소문자·따옴표 변형 허용)가 없으면 위반 |
| HTML-06 | **비밀키 값 노출** | `verify_report_format.SECRET_PATTERNS` 재사용. §5가 HTML/PDF에도 비밀키 자가점검을 요구하나 형식검증기는 .md만 보므로 여기서 코드화 |

### 허용 태그 목록 (HTML-01)

`report-formats.md §2` 골격에서 실제 등장하는 태그:

```
html, head, meta, title, style, body,
p, div, span, h1, h2,
dl, dt, dd, ol, li, ul,
table, thead, tbody, tr, th, td,
code, b, small
```

- `<!doctype html>` 은 `html.parser`의 `handle_decl`로 들어와 태그가 아니므로 검사 대상 외(정상).
- HTML 주석(`<!-- … -->`)은 `handle_comment`로 무시(정상).
- void 태그 `<meta>`는 `handle_starttag`/`handle_startendtag` 양쪽으로 라우팅해 동일 검사.

## 5. 파서 (결정: html.parser, 정규식 보조)

- 태그·속성 검사: `html.parser.HTMLParser` 서브클래스 — `handle_starttag(tag, attrs)`·`handle_startendtag`에서 HTML-01/02/03/04 판정. 줄바꿈 속성·따옴표 변형을 안전 처리(정규식 파싱의 취약점 회피).
- CSS 내부 외부 리소스(`@import`, `url(...)`): `<style>` 본문(`handle_data`) + raw 텍스트 보조 스캔(정규식). 골격 CSS엔 외부 리소스가 0이므로 골든은 통과.
- 비밀키(HTML-06): raw 텍스트 전체 대상 정규식(`SECRET_PATTERNS`).

## 6. 보안 한계 (docstring에 정직하게 — `check_write_boundary` 방식)

1. **사후 검사일 뿐.** 생성은 여전히 모델이 한다. 이 도구는 이스케이프 실패의 *증상*(낯선 태그·속성·리소스)을 잡지, 모든 문자열의 이스케이프를 보증하지 않는다. 최종 안전은 호출 측(Claude)에 달려 있다 — 완전 강제가 아니다.
2. **허용목록 태그만 쓰는 무해 주입**(예: `<b>` 텍스트)은 잡지 않으나 무해하므로 무방.
3. **골격 결합.** `report-formats.md` 골격이 새 태그를 얻으면 허용목록도 **동시 갱신**해야 한다(안 하면 정상 보고서가 false-fail). 카탈로그 '동시 갱신' 규율과 동일.

## 7. 테스트·통합

- `tests/test_verify_html_report.py` (pytest, 인라인 HTML 문자열):
  - 안전 골든 HTML → 통과(exit 0, 위반 0).
  - 악성 케이스별 위반 트리거: ① 파일명 주입 `</style><img src=x onerror=alert(1)>.py` (HTML-01 낯선 태그 + HTML-02 이벤트핸들러) ② `<script>` 주입 (HTML-01) ③ CSS 외부 리소스 `@import url(https://…)`·`url(https://…)` (HTML-03 — 허용 태그 `<style>` 안이라 HTML-01과 독립으로 HTML-03을 단독 검증); 외부 `<link href="https://…">`는 HTML-01로 걸림(별도 케이스) ④ 허용 태그에 단독 이벤트핸들러 (HTML-02) ⑤ `javascript:`/`data:` URI (HTML-04) ⑥ charset 누락 (HTML-05) ⑦ 비밀키 값 `AKIA…`/`sk-…` (HTML-06).
  - 참고: `src`/외부 `href`를 가진 태그는 대개 HTML-01(허용목록 밖)에도 걸린다 — HTML-03은 그 방어심층 + CSS 벡터(허용 태그 `<style>` 내부)를 위한 독립 검사다.
  - 사용법/읽기 오류 → exit 1.
- 안전 골든 HTML 픽스처 1개 → `tests/fixtures/` (골격 최소 유효본, 모든 허용 태그 포함).
- CI: 기존 `ci.yml`이 `tests/test_*.py`를 pytest로 자동 실행 → 별도 step 추가 없이 포함(양 OS 매트릭스). 새 검사기는 `run_checks.py`에 즉시 통합하지 않는다(인자로 HTML이 올 때만 작동하는 통합은 후속 작은 단계 — YAGNI).
- `SECRET_PATTERNS` 공유: 가능하면 `verify_report_format`에서 import해 단일 출처 유지. 단 `tools/`(배포본)에서 `tests/`를 import할 수 없으므로(`check_write_boundary`가 `tests/_common`을 못 쓰는 BL-25 ①과 동일 제약), **배포본은 패턴을 자체 보유**하고 `tests/`의 단위테스트가 두 곳의 패턴이 일치하는지 검사(동기화 보증). 단일출처가 막히면 '동기화 테스트'로 대신한다.

## 8. 문서·버전

- `report-formats.md` §2: HTML 생성 후 `verify_html_report.py` 호출 절차 추가. §5: "사람이 직접 대조"를 "이 도구로 검사(+여전히 사람 확인 권장)"로 갱신.
- 버전 bump **v2.7.7 → v2.7.8**: `SKILL.md` 단일 출처 + `CHANGELOG`·`EVALS`·README(루트·스킬) 동기화(`check_version.py` 게이트 통과). EVALS엔 "검사기 추가, 탐지율 무영향" 1행.
- 공개판(v1.x) 미러는 **이번 범위 밖**(백로그 선별 미러 관행) — 별도 결정.

## 9. 범위 밖 (YAGNI)

- 결정적 렌더러(코드가 HTML 생성) — BL-31에서 3번째 기각, 본 작업은 검증기만.
- `run_checks.py` HTML 통합 — 후속 선택.
- 모든 문자열 이스케이프의 완전 증명 — 불가(증상 검출로 대체).
- PDF 자체 검사 — PDF는 동일 HTML이 원본이므로 HTML 검사로 커버(별도 PDF 파서 불필요).

## 10. 완료 기준 (인수)

- `verify_html_report.py`가 §4 6개 검사를 구현, exit 0/1 계약 준수.
- 골든 HTML 통과 + 7개 악성 케이스 전부 검출(테스트 green).
- `report-formats.md` §2/§5 갱신, v2.7.8 버전 정합(`check_version.py` 통과), CI 양 OS green.
- `check_write_boundary` 수준의 보안 한계 docstring 포함.
