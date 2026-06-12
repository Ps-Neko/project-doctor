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

## 2. HTML 인쇄용 (.html) 규칙 — "병원 결과지" 디자인

비개발자가 회사 공유·인쇄·PDF 변환에 쓰는 형식이다. 변환 도구 없이 스킬이 직접 작성한다.
디자인 목표: **병원 건강검진 결과지처럼** — 큰 등급 배지, 신호등 판정 알약(pill), 처방 강조 상자, 심각도별 색 테두리 카드. 회차가 달라도 같은 모양이 나오도록 아래 골격의 클래스·구조를 그대로 쓴다.

**자기완결 의무 (절대 준수):**
- 파일 하나로 완결 — CSS는 `<style>`로 **인라인**. 외부 리소스(CDN·웹폰트·외부 이미지·링크된 CSS/JS) **금지** (오프라인에서도, 사내망에서도 열려야 한다).
- `<script>` 태그 **일절 금지** (보안 — 받은 사람이 안심하고 열 수 있어야 한다).
- 인코딩: `<meta charset="utf-8">` + 파일은 UTF-8(BOM 없음).

**CSS 골격** (그대로 복사해 쓴다 — 임의 변경 금지, 색·클래스가 디자인 계약이다):

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>프로젝트 건강검진 결과지 — <프로젝트 이름></title>
<style>
  * { box-sizing: border-box; }
  body { font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Segoe UI", sans-serif;
         background: #eef1f5; color: #1f2937; margin: 0; line-height: 1.65; }
  .sheet { max-width: 860px; margin: 1.5rem auto; background: #fff;
           box-shadow: 0 2px 14px rgba(0,0,0,.08); border-radius: 10px; overflow: hidden; }
  .band { background: #1e3a5f; color: #fff; padding: 1.4rem 2rem 1.2rem; }
  .band .kind { font-size: .85rem; letter-spacing: .12em; opacity: .85; }
  .band h1 { margin: .15rem 0 0; font-size: 1.55rem; }
  .meta { display: flex; flex-wrap: wrap; gap: .4rem 1.6rem; padding: .7rem 2rem;
          background: #f0f4f8; border-bottom: 1px solid #dbe3ec; font-size: .82rem; color: #475569; }
  .meta b { color: #1f2937; font-weight: 600; }
  .inner { padding: 1.6rem 2rem 2rem; }
  h2 { font-size: 1.05rem; color: #1e3a5f; border-bottom: 2px solid #e2e8f0;
       padding-bottom: .35rem; margin: 2rem 0 .9rem; }
  h2:first-child { margin-top: 0; }
  .verdict { display: flex; gap: 1.4rem; align-items: center; margin: .4rem 0 1rem; }
  .badge { flex: 0 0 auto; width: 118px; height: 118px; border-radius: 50%;
           display: flex; flex-direction: column; align-items: center; justify-content: center;
           font-weight: 800; border: 6px solid; }
  .badge .g { font-size: 3rem; line-height: 1; }
  .badge .w { font-size: .78rem; font-weight: 700; margin-top: .15rem; }
  .grade-a, .grade-b { color: #15803d; border-color: #4ade80; background: #f0fdf4; }
  .grade-c { color: #b45309; border-color: #fbbf24; background: #fffbeb; }
  .grade-d { color: #b91c1c; border-color: #f87171; background: #fef2f2; }
  .verdict .word { font-size: 1.35rem; font-weight: 700; margin: 0 0 .3rem; }
  .legend { font-size: .78rem; color: #6b7280; }
  .opinion { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #1e3a5f;
             border-radius: 6px; padding: .7rem 1rem; margin-top: .9rem; font-size: .95rem; }
  .opinion b { color: #1e3a5f; }
  .chips { display: flex; gap: .5rem; margin: .9rem 0 .2rem; flex-wrap: wrap; }
  .chip { border-radius: 999px; padding: .22rem .85rem; font-size: .85rem; font-weight: 700; }
  .chip.red { background: #fee2e2; color: #b91c1c; }
  .chip.amber { background: #fef3c7; color: #92400e; }
  .chip.gray { background: #f3f4f6; color: #4b5563; }
  table { border-collapse: collapse; width: 100%; margin: .6rem 0; font-size: .92rem; }
  th, td { border: 1px solid #e2e8f0; padding: .5rem .7rem; text-align: left; vertical-align: top; }
  th { background: #f0f4f8; color: #334155; font-size: .85rem; }
  .pill { display: inline-block; white-space: nowrap; border-radius: 999px;
          padding: .1rem .6rem; font-size: .8rem; font-weight: 700; }
  .pill.green { background: #dcfce7; color: #15803d; }
  .pill.amber { background: #fef3c7; color: #92400e; }
  .pill.red { background: #fee2e2; color: #b91c1c; }
  .rx { background: #eff6ff; border: 1px solid #bfdbfe; border-left: 6px solid #1d4ed8;
        border-radius: 6px; padding: .9rem 1.1rem; margin: .8rem 0; }
  .rx .now { font-size: 1.02rem; font-weight: 700; color: #1e3a8a; }
  .rx .next { margin-top: .35rem; font-size: .9rem; color: #374151; }
  .note { font-size: .82rem; color: #6b7280; margin: .5rem 0 0; }
  .card { border: 1px solid #e5e7eb; border-left-width: 6px; border-radius: 6px;
          margin: .85rem 0; padding: .8rem 1rem .6rem; break-inside: avoid; }
  .card.sev-red { border-left-color: #dc2626; }
  .card.sev-amber { border-left-color: #d97706; }
  .card.sev-gray { border-left-color: #9ca3af; }
  .card .head { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; margin-bottom: .45rem; }
  .sev { border-radius: 4px; padding: .08rem .5rem; font-size: .78rem; font-weight: 800; }
  .sev.red { background: #dc2626; color: #fff; }
  .sev.amber { background: #d97706; color: #fff; }
  .sev.gray { background: #6b7280; color: #fff; }
  .idtag { font-family: Consolas, monospace; font-size: .78rem; background: #f3f4f6;
           border: 1px solid #e5e7eb; border-radius: 4px; padding: .05rem .4rem; color: #475569; }
  .card .title { font-weight: 700; font-size: .98rem; }
  .kv { display: grid; grid-template-columns: 7.2rem 1fr; gap: .25rem .6rem; font-size: .9rem; }
  .kv dt { font-weight: 700; color: #1e3a5f; }
  .kv dd { margin: 0; }
  .approve { font-family: Consolas, monospace; background: #f0fdf4; border: 1px dashed #86efac;
             border-radius: 4px; padding: 0 .45rem; color: #166534; }
  .appendix { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
              padding: .7rem 1.1rem; font-size: .88rem; }
  .appendix li { margin: .15rem 0; }
  .machine { color: #9ca3af; font-size: .76rem; margin-top: 2rem;
             border-top: 1px dashed #d1d5db; padding-top: .55rem;
             font-family: Consolas, monospace; word-break: break-all; }
  .howto-pdf { max-width: 860px; margin: .9rem auto 0; background: #eef6ff; border: 1px solid #bfdbfe;
               padding: .6rem .9rem; border-radius: 8px; font-size: .88rem; color: #1e40af; }
  @media print {
    body { background: #fff; }
    .sheet { box-shadow: none; margin: 0; max-width: none; border-radius: 0; }
    .howto-pdf { display: none; }
    .card, .rx, .opinion, table { break-inside: avoid; }
  }
</style>
</head>
```

**본문 구조 (이 순서 그대로 — md 보고서의 절 순서와 동일):**

```html
<body>
<p class="howto-pdf">📄 이 파일을 PDF로 만들려면: 인쇄(Ctrl+P) → 대상에서 "PDF로 저장" 선택. (이 안내 상자는 인쇄물에는 나오지 않습니다)</p>
<div class="sheet">
  <div class="band"><div class="kind">PROJECT DOCTOR · 건강검진 결과지</div><h1>🏥 <프로젝트 이름></h1></div>
  <div class="meta"><span><b>환자</b> …</span><span><b>검진일</b> …</span><span><b>분석 파일</b> …</span><span><b>스킬 버전</b> …</span><span><b>모드</b> …</span></div>
  <div class="inner">
    <h2>종합 판정</h2>
    <div class="verdict">
      <div class="badge grade-d"><span class="g">D</span><span class="w">치료가 필요해요</span></div>
      <div><p class="word">🔴 치료가 필요해요</p><p class="legend">등급 읽는 법 + 합산 설명 (md와 동일 문구)</p></div>
    </div>
    <div class="opinion"><b>의사 소견</b> — …</div>
    <div class="chips"><span class="chip red">🔴 심각 N건</span><span class="chip amber">🟡 권장 N건</span><span class="chip gray">⚪ 참고 N건</span></div>
    <h2>부위별 소견</h2>
    <table> … 판정 칸은 <span class="pill red|amber|green">…</span> … </table>
    <h2>오늘의 처방</h2>
    <div class="rx"><div class="now">👉 당장 1건만 하신다면 — …</div><div class="next">승인 명령 + 📅 재검 권고</div></div>
    <h2>상세 소견</h2>
    <div class="card sev-red">  <!-- 발견 항목마다 카드 1개 -->
      <div class="head"><span class="sev red">심각 1</span><span class="idtag">DUP-01</span><span class="title">제목</span></div>
      <dl class="kv"><dt>무슨 뜻인가요?</dt><dd>…</dd><dt>어디?</dt><dd>…</dd><dt>고치면?</dt><dd>…</dd>
      <dt>승인 명령</dt><dd><span class="approve">"심각 1 실행해줘"</span></dd></dl>
    </div>
    <h2>부록: 나머지 발견 항목</h2>  <!-- 압도 방지 적용 시에만 -->
    <div class="appendix"><ul><li>🟡 <span class="idtag">ID</span> 제목 — 위치</li></ul></div>
    <h2>다음 진료 안내</h2> <ul>…</ul>
    <p class="machine">기계 판독용 — 스킬 버전: vX.Y.Z<br>발견ID: …</p>
  </div>
</div>
</body>
</html>
```

**매핑 규칙:**
- 등급 배지: 종합 등급 → `grade-a/b/c/d` 클래스 + 등급↔표현 고정표의 판정어 그대로 (배지 안 `w`와 옆 `word` 모두).
- 심각도: 🔴=`sev-red`/`sev red`/`pill red`, 🟡=`sev-amber`/`sev amber`/`pill amber`, ⚪=`sev-gray`, 부위 🟢=`pill green`.
- 재검진이면 "지난 검진과 비교" 표는 부위별 소견 다음에 같은 `table`로.
- **기계 판독 줄(`발견ID:` 등 이 버전 보고서 계약에 있는 한 줄들)은 문서 끝 `.machine` 단락에 텍스트 그대로 포함** — 작게 표시하되 생략 금지 (이 파일만 남아도 추적 가능해야 한다).
- 채점·재검진 비교의 정본은 어디까지나 `.md`/채팅 보고서다 — 채점기는 HTML을 읽지 않는다.
- 다른 모드(초진 차트·공개 전 검진 등)도 같은 골격을 쓰되, `band .kind`와 절 구성만 그 모드의 md 구성을 따른다 (예: 초진 차트는 등급 배지 대신 "정밀 등급은 checkup에서" 한 줄).

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
