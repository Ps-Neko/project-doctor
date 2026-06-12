# 보고서 저장 형식 (report-formats)

> 사용자가 보고서 **저장**을 원할 때(저장 의사가 확인된 뒤)만 이 문서를 읽는다.
> 보고서의 **내용**은 형식과 무관하게 동일하다 — 결과지 3블록·ID+4요소·기계 판독 블록 등
> `report-template.md`의 계약이 모든 형식에 그대로 들어간다. 형식은 "겉포장"만 바꾼다.

## 1. 형식 질문 (저장 의사 확인 후 1회만)

> **어떤 형식으로 저장해 드릴까요?** (복수 선택 가능)
> ① **마크다운(.md)** — 기본. 텍스트 편집기·GitHub에서 그대로 읽힙니다.
> ② **HTML 인쇄용(.html)** — 더블클릭하면 브라우저로 열립니다. 인쇄(Ctrl+P)에서 "PDF로 저장"을 고르면 그대로 **PDF**가 되고, 워드에서도 열 수 있어요.
> ③ **워드(.docx)** — 이 컴퓨터에 변환 도구(pandoc)가 있을 때만 가능합니다.

규칙:
- 사용자가 형식을 이미 말했으면(예: "PDF로 줘", "워드로 저장") 질문을 생략하고 아래 해석 표를 따른다.
- 답이 없거나 모호하면 **① 마크다운**이 기본값.
- 질문은 한 검진(보고서 1건)에 1회만 — 같은 보고서를 형식만 바꿔 다시 요청하면 질문 없이 바로 저장한다.

| 사용자 표현 | 해석 |
|------------|------|
| "마크다운", "md", "텍스트로" | ① .md |
| "HTML", "웹으로", "브라우저로" | ② .html |
| "PDF로 줘" | ② .html 저장 + PDF 저장 방법 1줄 안내 (아래 4장) — 직접 PDF 생성은 변환 도구가 필요해 약속하지 않는다 |
| "워드", "docx", "문서 파일" | ③ 시도 — pandoc 확인(아래 3장), 없으면 ② + 안내 |
| "둘 다", 복수 언급 | 언급된 형식 전부 (파일명 동일, 확장자만 다름) |

저장 위치·쓰기 경계는 SKILL.md 절대 규칙 7을 따른다 — 같은 보고서의 형식 변형(예: `.md`+`.html`)은 보고서 1건으로 본다.

## 2. HTML 인쇄용 (.html) 규칙

비개발자가 회사 공유·인쇄·PDF 변환에 쓰는 형식이다. 변환 도구 없이 스킬이 직접 작성한다.

**자기완결 의무 (절대 준수):**
- 파일 하나로 완결 — CSS는 `<style>`로 **인라인**. 외부 리소스(CDN·웹폰트·외부 이미지·링크된 CSS/JS) **금지** (오프라인에서도, 사내망에서도 열려야 한다).
- `<script>` 태그 **일절 금지** (보안 — 받은 사람이 안심하고 열 수 있어야 한다).
- 인코딩: `<meta charset="utf-8">` + 파일은 UTF-8(BOM 없음).

**골격** (이대로 시작해 본문만 채운다):

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>프로젝트 건강검진 결과지 — <프로젝트 이름></title>
<style>
  body { font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
         max-width: 800px; margin: 2rem auto; padding: 0 1rem;
         color: #222; line-height: 1.6; }
  h1 { border-bottom: 3px solid #333; padding-bottom: .3rem; }
  .grade { font-size: 2.2rem; font-weight: bold; margin: .5rem 0; }
  .grade.green { color: #1a7f37; } .grade.yellow { color: #b58900; } .grade.red { color: #c0392b; }
  table { border-collapse: collapse; width: 100%; margin: .8rem 0; }
  th, td { border: 1px solid #ccc; padding: .4rem .6rem; text-align: left; }
  th { background: #f5f5f5; }
  code { background: #f2f2f2; padding: .1rem .3rem; border-radius: 3px; }
  blockquote { border-left: 4px solid #ddd; margin: .8rem 0; padding: .2rem .8rem; color: #555; }
  .machine { color: #999; font-size: .8rem; margin-top: 2rem;
             border-top: 1px dashed #ccc; padding-top: .5rem; }
  .howto-pdf { background: #eef6ff; padding: .6rem .8rem; border-radius: 6px; font-size: .9rem; }
  @media print { .howto-pdf { display: none; } body { margin: 0; } }
</style>
</head>
<body>
<p class="howto-pdf">📄 이 파일을 PDF로 만들려면: 인쇄(Ctrl+P) → 대상에서 "PDF로 저장" 선택. (이 안내 상자는 인쇄물에는 나오지 않습니다)</p>
<!-- 여기에 보고서 본문: 결과지 3블록 → 발견 항목(ID+4요소) → 다음 진료 안내 -->
<p class="machine">기계 판독용 — 발견ID: DUP-01, …</p>
</body>
</html>
```

**내용 매핑 규칙:**
- 종합 판정 등급은 `.grade` + 색상 클래스(A·B=green / C=yellow / D=red) — 등급↔표현 고정표의 판정어 그대로.
- 표(부위별 소견·비교표)는 `<table>`로, 발견 항목의 4요소는 굵은 라벨 그대로 옮긴다.
- **기계 판독 줄(`비교:`·`숙제:`·`발견ID:`)도 문서 끝 `.machine` 단락에 텍스트 그대로 포함** — 작게 표시하되 생략 금지 (이 파일만 남아도 추적 가능해야 한다).
- 채점·재검진 비교의 정본은 어디까지나 `.md`/채팅 보고서다 — 채점기는 HTML을 읽지 않는다.

## 3. 워드 (.docx) 규칙 — 변환 도구가 있을 때만

1. 사용자가 워드를 원하면 먼저 조용히 확인: `pandoc --version` (프로젝트 코드 실행이 아니므로 승인 불필요, 부산물 없음).
2. **있으면**: `.md`를 먼저 저장한 뒤 변환 — `pandoc <보고서>.md -o <보고서>.docx`. 변환 실패 시 오류를 숨기지 말고 ② HTML로 폴백 제안.
3. **없으면**: 설치를 권하지 않는다(스킬이 사용자 PC에 도구 설치를 유도하지 않는다). 대신:
   > 이 컴퓨터에는 워드 변환 도구가 없어요. 대신 **HTML 인쇄용**으로 드릴게요 — 워드에서 "파일 → 열기"로 이 HTML을 열면 편집 가능한 문서로 읽힙니다.

## 4. PDF 안내 문안 (직접 생성하지 않는다)

PDF 직접 생성은 추가 도구가 필요해 환경마다 결과가 달라진다. 항상 HTML 경유로 안내한다:

> PDF는 이렇게 만드세요: 방금 저장한 `.html` 파일을 더블클릭해 브라우저로 열고 → 인쇄(Ctrl+P) → 대상에서 "PDF로 저장"을 고르면 끝입니다.

## 5. 공통 마무리

- 저장 후 보고: 만든 파일 경로 전부 + 형식별 한 줄 용도 안내 ("md는 보관용, html은 공유·인쇄용").
- 진료기록부(`.project-doctor/records/`) 기록은 형식 선택과 무관하게 기존 절차(record-format.md) 그대로 — 기록부는 항상 md.
