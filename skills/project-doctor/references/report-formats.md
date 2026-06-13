# 보고서 저장 형식 (report-formats)

> 사용자가 보고서 **저장**을 원할 때(저장 의사가 확인된 뒤)만 이 문서를 읽는다.
> 보고서의 **내용**은 형식과 무관하게 동일하다 — 결과지 3블록·ID+4요소·기계 판독 블록 등
> `report-template.md`의 계약이 모든 형식에 그대로 들어간다. 형식은 "겉포장"만 바꾼다.

## 1. 형식 질문 (저장 의사 확인 후 1회만)

> **어떤 형식으로 저장해 드릴까요?** (복수 선택 가능)
> ① **마크다운(.md)** — 기본. 텍스트 편집기·GitHub에서 그대로 읽힙니다.
> ② **HTML 인쇄용(.html)** — 더블클릭하면 브라우저로 열리고, 워드에서도 열 수 있어요.
> ③ **PDF(.pdf)** — 회사 공유·결재용. (이 컴퓨터의 브라우저로 변환합니다 — Windows는 대부분 가능)
> ④ **워드(.docx)** — 이 컴퓨터에 변환 도구(pandoc)가 있을 때만 가능합니다.

규칙:
- 사용자가 형식을 이미 말했으면(예: "PDF로 줘", "워드로 저장") 질문을 생략하고 아래 해석 표를 따른다.
- 답이 없거나 모호하면 **① 마크다운**이 기본값.
- 질문은 한 검진(보고서 1건)에 1회만 — 같은 보고서를 형식만 바꿔 다시 요청하면 질문 없이 바로 저장한다.

| 사용자 표현 | 해석 |
|------------|------|
| "마크다운", "md", "텍스트로" | ① .md |
| "HTML", "웹으로", "브라우저로" | ② .html |
| "PDF로 줘", "PDF 출력" | ③ .html 생성 후 **PDF 직접 변환** (4장 절차) — 변환 수단이 없으면 ②+인쇄 안내로 폴백 |
| "워드", "docx", "문서 파일" | ④ 시도 — pandoc 확인(3장), 없으면 ② + 안내 |
| "둘 다", 복수 언급 | 언급된 형식 전부 (파일명 동일, 확장자만 다름) |

저장 위치·쓰기 경계는 SKILL.md 절대 규칙 7을 따른다 — 같은 보고서의 형식 변형(예: `.md`+`.html`+`.pdf`)은 보고서 1건으로 본다.

## 2. HTML 인쇄용 (.html) — "클리니컬 결과지" 디자인

비개발자가 회사 공유·인쇄·PDF 변환에 쓰는 형식이며 PDF의 원본이기도 하다. 변환 도구 없이 스킬이 직접 작성한다.
디자인 원칙: **종합병원 검진센터 결과지** — 타이포그래피 위계 중심, 가는 괘선, 이모지·아이콘 장식 금지, 색은 판정·심각도에만 최소 사용. 회차가 달라도 같은 모양이 나오도록 아래 골격의 클래스·구조를 그대로 쓴다.

**자기완결 의무 (절대 준수):**
- 파일 하나로 완결 — CSS는 `<style>`로 **인라인**. 외부 리소스(CDN·웹폰트·외부 이미지·링크된 CSS/JS) **금지**.
- `<script>` 태그·이모지 **일절 금지** (보안·전문성 — 받은 사람이 안심하고 열 수 있어야 한다).
- 인코딩: `<meta charset="utf-8">` + 파일은 UTF-8(BOM 없음).
- **신뢰 불가 값 HTML 이스케이프 (절대 준수 — 보안 핵심):** 골격에 끼워 넣는 값 중 **분석 대상 프로젝트에서 온 모든 문자열**(파일명·경로 `.loc`, 발견 내용·소견 `.ft`/`.fd`/`.opinion`, 인용한 코드 조각, 프로젝트 이름이 들어가는 `<title>`·`<h1>`·환자명)은 HTML에 넣기 전 **반드시** 다음 5개 문자를 엔티티로 치환한다: `&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;`, `"`→`&quot;`, `'`→`&#39;` (`&`를 가장 먼저). 골격이 "그대로 복사"인 것은 **CSS·구조**를 말하는 것이고, **삽입하는 데이터는 예외 없이 이스케이프**한다. 이유: 검진 대상이 통제하는 파일명(예: `</style><img src=x onerror=…>.py`)이 raw로 박히면, 사용자가 `.html`을 더블클릭하거나 4장 PDF 변환(headless 브라우저가 `file://`로 로드)할 때 그 마크업이 실행되어 결과지 내용 유출 등으로 이어진다 — "받은 사람이 안심하고 열 수 있어야 한다"는 이 형식의 존재 이유를 깬다. `<script> 금지`(작성 제약)는 이 데이터 경로를 막지 못하므로 이스케이프가 별도로 필요하다.

**CSS 골격** (그대로 복사해 쓴다 — 임의 변경 금지, 이 색·클래스가 디자인 계약이다):

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>프로젝트 건강검진 결과지 — <프로젝트 이름></title>
<style>
  * { box-sizing: border-box; }
  :root {
    --ink: #16181d; --sub: #5c6470; --faint: #9aa1ac; --line: #e3e6ea; --hair: #eef0f3;
    --navy: #1c3d6e; --red: #c4332d; --amber: #b97509; --green: #2e7d4f;
  }
  body { font-family: "Pretendard", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
         background: #fff; color: var(--ink); margin: 0; line-height: 1.6;
         font-size: 14px; -webkit-font-smoothing: antialiased; }
  .doc { max-width: 880px; margin: 0 auto; padding: 48px 40px 56px; }
  .num { font-variant-numeric: tabular-nums; }
  .rule-top { border-top: 5px solid var(--ink); }
  .masthead { display: flex; justify-content: space-between; align-items: baseline; padding: 14px 0 0; }
  .eyebrow { font-size: 11px; font-weight: 700; letter-spacing: .22em; color: var(--navy); }
  .issue { font-size: 11.5px; color: var(--faint); letter-spacing: .04em; }
  h1 { font-size: 30px; font-weight: 800; letter-spacing: -.02em; margin: 10px 0 4px; }
  .patient { font-size: 14.5px; color: var(--sub); margin-bottom: 22px; }
  .patient b { color: var(--ink); font-weight: 700; }
  .meta { display: grid; grid-template-columns: repeat(5, 1fr);
          border-top: 1.5px solid var(--ink); border-bottom: 1px solid var(--line); }
  .meta div { padding: 10px 14px 12px; border-right: 1px solid var(--hair); }
  .meta div:last-child { border-right: none; }
  .meta dt { font-size: 10.5px; font-weight: 700; letter-spacing: .14em; color: var(--faint); }
  .meta dd { margin: 2px 0 0; font-size: 14px; font-weight: 700; }
  .meta .s { font-size: 11px; color: var(--faint); font-weight: 400; }
  h2 { font-size: 12px; font-weight: 800; letter-spacing: .18em; color: var(--navy);
       margin: 40px 0 14px; padding-bottom: 8px; border-bottom: 1px solid var(--line); }
  h2 .ko { letter-spacing: .06em; }
  .verdict { display: grid; grid-template-columns: 200px 1fr; gap: 36px; align-items: center; }
  .grade { text-align: center; }
  .grade .letter { width: 124px; height: 124px; margin: 0 auto; border: 3px solid;
                   border-radius: 50%; display: flex; align-items: center; justify-content: center;
                   font-size: 64px; font-weight: 900; letter-spacing: -.02em; }
  .g-d { border-color: var(--red); color: var(--red); }
  .g-c { border-color: var(--amber); color: var(--amber); }
  .g-a, .g-b { border-color: var(--green); color: var(--green); }
  .grade .word { margin-top: 12px; font-size: 16px; font-weight: 800; }
  .grade .scale { margin-top: 6px; font-size: 11px; color: var(--faint); letter-spacing: .06em; }
  .stats { display: flex; border-bottom: 1px solid var(--line); }
  .stat { flex: 1; padding: 2px 0 14px; }
  .stat + .stat { border-left: 1px solid var(--hair); padding-left: 22px; }
  .stat .k { font-size: 12px; font-weight: 700; color: var(--sub); }
  .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px; }
  .dot.r { background: var(--red); } .dot.a { background: var(--amber); } .dot.g { background: #b8bfc9; }
  .stat .n { font-size: 30px; font-weight: 800; letter-spacing: -.02em; }
  .stat .n small { font-size: 14px; font-weight: 600; color: var(--sub); }
  .opinion { margin-top: 16px; font-size: 14.5px; }
  .opinion .lbl { font-weight: 800; color: var(--navy); margin-right: 8px; }
  .calcnote { margin-top: 8px; font-size: 12px; color: var(--faint); }
  .rx { border: 1.5px solid var(--ink); display: grid; grid-template-columns: 1.1fr 1fr; }
  .rx .main { padding: 18px 22px; }
  .rx .side { border-left: 1px solid var(--line); padding: 18px 22px; background: #fafbfc; }
  .rx .tag { font-size: 10.5px; font-weight: 800; letter-spacing: .2em; color: var(--red); }
  .rx .id { font-family: "Consolas", monospace; font-weight: 700; font-size: 13px;
            border: 1px solid var(--red); color: var(--red); padding: 1px 8px; margin-left: 8px; }
  .rx .title { font-size: 18px; font-weight: 800; margin: 8px 0 6px; letter-spacing: -.01em; }
  .rx .desc { font-size: 13.5px; color: var(--sub); }
  .rx .cmd { font-family: "Consolas", monospace; font-size: 12.5px; color: var(--ink);
             background: var(--hair); padding: 1px 7px; }
  .flow { font-size: 12.5px; color: var(--sub); }
  .flow .t { font-size: 10.5px; font-weight: 800; letter-spacing: .18em; color: var(--navy); margin-bottom: 10px; }
  .flow ol { margin: 0; padding: 0; list-style: none; counter-reset: st; }
  .flow li { counter-increment: st; padding: 4px 0 4px 30px; position: relative; }
  .flow li:before { content: counter(st); position: absolute; left: 0; top: 5px;
                    width: 19px; height: 19px; border: 1px solid var(--navy); border-radius: 50%;
                    font-size: 10.5px; font-weight: 700; color: var(--navy);
                    display: flex; align-items: center; justify-content: center; }
  .flow b { color: var(--ink); font-weight: 700; }
  .recheck { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line);
             font-size: 13px; font-weight: 700; }
  .recheck span { color: var(--red); }
  table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
  thead th { font-size: 11px; font-weight: 800; letter-spacing: .1em; color: var(--faint);
             text-align: left; padding: 0 12px 8px; border-bottom: 1.5px solid var(--ink); }
  tbody td { padding: 10px 12px; border-bottom: 1px solid var(--hair); vertical-align: top; }
  tbody tr:last-child td { border-bottom: 1px solid var(--line); }
  .gcell { white-space: nowrap; font-weight: 800; }
  .gcell.d { color: var(--red); } .gcell.c { color: var(--amber); }
  .gcell.b, .gcell.a { color: var(--green); }
  .pname { font-weight: 700; white-space: nowrap; }
  td.fid { font-family: "Consolas", monospace; font-weight: 700; white-space: nowrap; }
  td.fid.r { color: var(--red); } td.fid.a { color: var(--amber); }
  .sev { font-size: 11px; font-weight: 800; letter-spacing: .08em; white-space: nowrap; }
  .sev.r { color: var(--red); } .sev.a { color: var(--amber); } .sev.g { color: var(--faint); }
  td .ft { font-weight: 700; }
  td .fd { color: var(--sub); font-size: 12.5px; margin-top: 2px; }
  td.loc { font-family: "Consolas", monospace; font-size: 11.5px; color: var(--sub); }
  td.cmd { white-space: nowrap; }
  td.cmd code { font-family: "Consolas", monospace; font-size: 11.5px; background: var(--hair); padding: 1px 6px; }
  .cols { display: grid; grid-template-columns: 1.4fr 1fr; gap: 40px; }
  .applist { margin: 0; padding: 0; list-style: none; font-size: 13px; }
  .applist li { padding: 7px 0; border-bottom: 1px solid var(--hair); display: flex; gap: 10px; }
  .applist .aid { font-family: "Consolas", monospace; font-weight: 700; min-width: 84px; }
  .applist .aid.a { color: var(--amber); } .applist .aid.g { color: var(--faint); }
  .next dt { font-size: 11px; font-weight: 800; letter-spacing: .14em; color: var(--faint); margin-top: 14px; }
  .next dt:first-child { margin-top: 0; }
  .next dd { margin: 2px 0 0; font-size: 14.5px; font-weight: 700; }
  .next .s { font-size: 12px; color: var(--sub); font-weight: 400; }
  .machine { margin-top: 36px; border-top: 1px solid var(--line); padding-top: 12px; }
  .machine .t { font-size: 10.5px; font-weight: 800; letter-spacing: .18em; color: var(--faint); }
  .machine .mono { font-family: "Consolas", monospace; font-size: 11.5px; color: var(--sub);
                   word-break: break-all; margin-top: 6px; }
  .machine .warn { font-size: 11px; color: var(--faint); margin-top: 4px; }
  .foot { margin-top: 28px; border-top: 5px solid var(--ink); padding-top: 12px;
          display: flex; justify-content: space-between; font-size: 11.5px; color: var(--sub); }
  .foot b { color: var(--ink); }
  .howto-pdf { max-width: 880px; margin: 14px auto 0; padding: 9px 40px; font-size: 12.5px;
               color: var(--navy); background: #f3f6fb; }
  @media print {
    .howto-pdf { display: none; }
    .doc { padding: 24px 0 32px; }
    .rx, table, .verdict { break-inside: avoid; }
  }
</style>
</head>
```

**본문 구조 (이 순서 그대로 — md 보고서의 절 순서와 동일):**

```html
<body>
<p class="howto-pdf">PDF로 저장: 인쇄(Ctrl+P) → 대상에서 "PDF로 저장" 선택 — 이 안내줄은 인쇄물에 나오지 않습니다.</p>
<div class="rule-top"></div>
<div class="doc">
  <div class="masthead"><span class="eyebrow">PROJECT DOCTOR · 건강검진 결과지</span><span class="issue num">발급 YYYY-MM-DD · 스킬 vX.Y.Z</span></div>
  <h1>프로젝트 건강검진 결과지</h1>
  <p class="patient">환자 <b>이름</b> — 이 결과지는 프로젝트의 현재 상태를 비개발자도 읽을 수 있게 정리한 문서입니다.</p>
  <dl class="meta num"> 환자/검진일/분석 범위/검진 모드/스킬 버전 5칸 </dl>
  <h2>01 · <span class="ko">종합 판정</span></h2>
  <div class="verdict">
    <div class="grade"><div class="letter g-d">D</div><div class="word g-d">치료가 필요해요</div><div class="scale num">A 건강 · B 양호 · C 주의 · D 치료 필요</div></div>
    <div>
      <div class="stats num"> 심각/권장/참고 3칸 (.dot r/a/g + 건수) </div>
      <p class="opinion"><span class="lbl">의사 소견</span>…</p>
      <p class="calcnote">합산 점수 설명 (md와 동일 문구)</p>
    </div>
  </div>
  <h2>02 · <span class="ko">오늘의 처방</span></h2>
  <div class="rx">
    <div class="main"><span class="tag">우선 1건</span><span class="id">DUP-01</span><div class="title">제목</div><p class="desc">…<span class="cmd">"심각 1 실행해줘"</span>…</p><div class="recheck num">재검 권고일 <span>YYYY-MM-DD</span></div></div>
    <div class="side flow"><div class="t">치료는 이렇게 진행됩니다</div><ol><li><b>변경 계획</b> — 전/후 미리보기</li><li><b>체크포인트</b> — 안전 백업</li><li><b>수정 실행</b> — 한 번에 하나</li><li><b>검증·비교</b> — 전/후 확인</li><li><b>완료 보고</b> — 되돌리기 안내</li></ol></div>
  </div>
  <h2>03 · <span class="ko">부위별 소견</span></h2>
  <table> 부위/판정(.gcell d|c|b|a)/소견 </table>
  <!-- 재검진이면 여기에 "지난 검진과 비교" 표를 같은 table로 -->
  <h2>04 · <span class="ko">상세 소견</span></h2>
  <table> ID(.fid r|a)/구분(.sev r|a|g)/발견 내용(.ft+.fd)/어디?(.loc)/고치면?/승인 명령(.cmd code) </table>
  <div class="cols">
    <div><h2>05 · 나머지 발견 항목</h2><ul class="applist">…</ul></div>  <!-- 압도 방지 적용 시에만 -->
    <div><h2>06 · 다음 진료 안내</h2><dl class="next">…</dl></div>
  </div>
  <p class="machine"><span class="t">기계 판독용 · 변경 금지</span><span class="mono">스킬 버전 · 비교: · 숙제: · 발견ID: …</span><span class="warn">다음 검진 비교용 — 수정 금지 안내</span></p>
  <div class="foot"><span><b>안전 약속</b> — 승인 없이 파일을 절대 수정하지 않습니다. 변경 전 체크포인트를 만들고, 언제든 되돌릴 수 있습니다.</span><span class="num">Project Doctor vX.Y.Z</span></div>
</div>
</body>
</html>
```

**매핑 규칙:**
- 등급: `.letter`와 `.word`에 `g-a/g-b/g-c/g-d` 클래스 + 등급↔표현 고정표의 판정어 그대로.
- 심각도: 🔴=`r`(빨강), 🟡=`a`(호박), ⚪=`g`(회색) — `.dot`·`.fid`·`.sev`·`.applist .aid`에 일관 적용.
- 재검진이면 표지 `.issue`에 `등급 추이 5월 D → 오늘 C`를 덧붙이고, "지난 검진과 비교" 표는 03 다음에 같은 표 골격으로.
- **기계 판독 줄(`비교:`·`숙제:`·`발견ID:`)은 `.machine`의 `.mono`에 텍스트 그대로 포함** — 생략 금지 (이 파일만 남아도 추적 가능해야 한다).
- 채점·재검진 비교의 정본은 어디까지나 `.md`/채팅 보고서다 — 채점기는 HTML을 읽지 않는다.
- 다른 모드(초진 차트·공개 전 검진 등)도 같은 골격을 쓰되 절 구성만 그 모드의 md 구성을 따른다 (예: 초진 차트는 등급 원 대신 "정밀 등급은 checkup에서" 한 줄, 공개 전 검진은 통과/보류 판정 블록을 02 자리에).

## 3. 워드 (.docx) — 변환 도구가 있을 때만

1. 사용자가 워드를 원하면 먼저 조용히 확인: `pandoc --version` (프로젝트 코드 실행이 아니므로 승인 불필요, 부산물 없음).
2. **있으면**: `.md`를 먼저 저장한 뒤 변환 — `pandoc <보고서>.md -o <보고서>.docx`. 변환 실패 시 오류를 숨기지 말고 ② HTML로 폴백 제안.
3. **없으면**: 설치를 권하지 않는다. 대신:
   > 이 컴퓨터에는 워드 변환 도구가 없어요. 대신 **HTML 인쇄용**으로 드릴게요 — 워드에서 "파일 → 열기"로 이 HTML을 열면 편집 가능한 문서로 읽힙니다.

## 4. PDF (.pdf) — 내장 브라우저로 직접 변환

PDF는 ② HTML을 원본으로 **이 컴퓨터에 이미 있는 브라우저**가 변환한다. 별도 설치를 유도하지 않는다.

1. **변환기 감지 (조용히, 프로젝트 코드 실행 아님)** — Windows 기준 순서대로 첫 번째 것:
   - Edge: 레지스트리 `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe`의 기본값
   - Chrome: 같은 위치의 `chrome.exe`
   - (macOS/Linux면 `google-chrome`/`chromium` PATH 검색)
2. **변환 실행**: 먼저 ② 규칙으로 `.html`을 저장한 뒤 —
   ```
   & "<브라우저 경로>" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="<보고서 절대경로>.pdf" "file:///<보고서 절대경로>.html"
   ```
3. **검증**: `.pdf` 파일이 생성되고 크기가 0보다 큰지 확인. 실패하면 오류를 숨기지 말고 폴백 안내.
4. **폴백 (변환기 없음/실패)**:
   > PDF 자동 변환을 못 했어요. 대신 방금 저장한 `.html`을 더블클릭해 브라우저로 열고 → 인쇄(Ctrl+P) → "PDF로 저장"을 고르면 똑같은 PDF가 됩니다.
5. PDF를 만들면 원본 `.html`도 함께 남는다 — 같은 보고서 1건의 형식 변형이므로 쓰기 경계 위반이 아니다 (절대 규칙 7).

## 5. 공통 마무리

- **저장 전 비밀키 자가 점검 (md·HTML·PDF 모두):** 어떤 형식으로 내보내든, 저장 직전 보고서에 비밀키·토큰 **값**이 섞이지 않았는지(위치만 적혔는지) md와 동일 기준으로 확인한다. md 보고서는 형식 검증기(`verify_report_format.py` FORM-11)가 자동으로 잡아주지만 **HTML/PDF는 그 검사 대상이 아니므로**(채점기는 HTML을 읽지 않는다), 형식 변환 과정에서 코드 인용 등에 키 값이 끼어들지 않았는지 사람(Claude)이 직접 대조한다 — md가 깨끗해도 변환물이 깨끗함이 자동 보증되지는 않는다.
- 저장 후 보고: 만든 파일 경로 전부 + 형식별 한 줄 용도 안내 ("md는 보관용, html은 공유·인쇄용, pdf는 결재·전달용").
- 진료기록부(`.project-doctor/records/`) 기록은 형식 선택과 무관하게 기존 절차(record-format.md) 그대로 — 기록부는 항상 md.
