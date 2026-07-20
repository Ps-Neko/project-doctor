# English Report Template (report-template-en)

> **상태: v2.8.0 신설** — 한국어 정본 `report-template.md`의 영어판 계약. **구조·절 순서·4요소·기계 판독 계약은 정본과 1:1 동일**하며, 이 문서는 영어 표현만 정의한다. 정본과 이 문서가 충돌하면 **구조는 정본, 영어 문장은 이 문서**가 이긴다. 승인된 톤 기준 견본: `tests/golden/checkup-report-en.md`.
> 언어 선택 규칙(언제 영어 결과지를 쓰는가)은 SKILL.md "보고서 공통 의무"를 따른다.

---

## 절대 불변 3가지 (영어 결과지에서도 한국어 원형 유지)

1. **기계 판독 마커**: `비교:` `숙제:` `발견ID:` 줄은 접두사·형식 모두 한국어 원형 그대로 쓴다 (채점기 `compare_report.py`·검증기 `verify_report_format.py`가 이 접두사를 파싱한다).
2. **빈 값 표식**: `(없음)` — 영어로 번역하지 않는다 (`(none)` 금지, `EMPTY_MARK` 계약).
3. **안내문 1줄**: 첫 기계 마커 줄 **바로 위**에 다음 한 줄을 넣는다 (발견ID 줄 아래에는 어떤 내용도 금지 — 맨 마지막 줄 계약):
   `The two lines below are machine-readable grader markers, intentionally kept in Korean.`
   (마커가 발견ID 하나뿐인 보고서에서는 "The line below is a machine-readable grader marker, intentionally kept in Korean."로 단수형.)

## 1) Cover

```markdown
# 🏥 Project Health Checkup Report — <project name>
```

```
Patient: <project name> · Checkup date: <date> · Files analyzed: N (after applying the exclusion list — self-test answer keys excluded)
Skill version: <current version from SKILL.md> · Mode: Checkup <(commit abc1234) if a git project>
```

모드별 표지 제목:

| 모드 | English cover title |
|------|----------|
| 건강검진 | Project Health Checkup Report |
| 초진 차트 | Project Intake Chart |
| 방향전환 | Project Pivot Plan |
| 공개 전 검진 | Pre-release Checkup Report |

재검진 옵션 줄: `Grade trend: May D → today C`

## 2) Overall Assessment

```markdown
## Overall Assessment

# 🔴 D — Treatment needed

> How to read the grade: 🟢 A Healthy · 🟢 B Fair · 🟡 C Caution · 🔴 D Treatment needed
> ※ The overall grade is not an average of the areas — it is a **weighted total** of finding counts and severity, so it can be lower than any single area.

**Ship verdict: 🚫 Not ready to ship — treatment recommended.**

**Doctor's note**: <1–2 sentences, same direction as the grade, pointing naturally at the first prescription item>
```

**등급↔표현 고정표 (영어판 — 이 표 밖 표현 금지)**:

| Grade | Signal | Legend (짧은형 — 등급 읽는 법 줄) | Verdict (긴형 — 판정 줄·부위 칸) |
|------|--------|--------|--------|
| A | 🟢 | Healthy | Healthy |
| B | 🟢 | Fair | Fair |
| C | 🟡 | Caution | Needs attention |
| D | 🔴 | Treatment needed | Treatment needed |

(한국어 정본의 "주의(범례) / 주의가 필요해요(판정)" 이원 구조와 동일. 종합 판정 헤딩 예: `# 🟡 C — Needs attention`)

**출하 판정(Ship verdict) 고정표** — checkup 모드 전용 옵션 줄, 등급에 기계적으로 연동(자유 재량 금지):

| Grade | Ship verdict |
|------|--------|
| A·B | ✅ Ready to ship. |
| C | 🟡 Ship with minor fixes. |
| D | 🚫 Not ready to ship — treatment recommended. |

부위 판정 칸 표현: `🟡 Needs attention (C)` / `🟢 Fair (B)` / `🟢 Healthy (A)` / `🔴 Treatment needed (D)`.

## 3) Findings by Area + Today's Prescription

```markdown
## Findings by Area

| Area | Verdict | Note |
|------|------|------|
| Structure | 🟡 Needs attention (C) | ... |

## Today's Prescription

Diagnosis: 🔴 Critical N · 🟡 Recommended N · ⚪ Note N
👉 **If you fix just one thing today**: Critical 1 (...) — to approve this fix, say "Fix Critical 1".
📅 **Recommended re-checkup**: <YYYY-MM-DD> (per the fixed grade schedule — A 90 days / B 60 / C 30 / D 14)
```

- 부위 이름: 구조=Structure · 정리=Tidiness · 문서=Docs · 테스트=Tests · 안전=Safety
- 심각도 3단계: 🔴 심각=**Critical** · 🟡 권장=**Recommended** · ⚪ 참고=**Note**
- `Diagnosis:` 줄은 정본의 `진단 결과:` 줄에 대응 (검증기 영어 패턴 확장 대상)

## 4) (재검진일 때만) Compared with Your Last Checkup

```markdown
## Compared with Your Last Checkup (baseline: <date>, skill <version>)
| Status | Count | ID |
|------|------|-----|
| ✅ Resolved | N | ... |
| ➖ Unchanged | N | ... |
| 🆕 New | N | ... |
| ⬆️ Worse | N | ... |
```

처치 경과 줄: `Treated-area follow-up: [DUP-01] no recurrence` / 재발 시 `recurred`. 0건 행의 ID 칸은 `(없음)`.

## 5) Finding items — ID + four fields

```markdown
### 🔴 Critical 1 [DUP-01] — <plain-English title>
- **What does this mean?** ...
- **Where?** `main.py:15`, ...
- **If we fix it?** ... Estimated work: N files edited.
- **Approval command:** "Fix Critical 1"
```

- 승인 명령 어휘: `"Fix Critical N"` / `"Fix Recommended N"` / `"Fix Note N"` — 사용자가 이 문구를 그대로 말하면 처방 실행(정본의 "심각 N 실행해줘"와 동일 계약)
- 전문 용어 옆 일상 영어 풀이 의무는 정본과 동일

## 6) Zero findings

```markdown
Diagnosis: No problems found 🎉
**What you are doing well** (2–3 items):
```

## 7) 압도 방지 — Appendix

발견 10건 초과 시 부록 헤더: `## Appendix: Remaining findings` (검증기 부록 정규식의 영어 패턴 확장 대상). 나열 기준은 정본과 동일.

## 8) Next Visit

```markdown
## Next Visit
- When would you like the next checkup? (Suggested: <YYYY-MM-DD> — same date as the re-checkup above)
- Also consider: if this project is headed for a public release, try `release-check` (the pre-release checkup).
The two lines below are machine-readable grader markers, intentionally kept in Korean.
비교: 해결 1 / 그대로 12 / 신규 2 / 악화 0
숙제: HARD-01
```

- 첫 검진이면 `비교:` 줄 생략, 그 자리에 예고 1줄: "Starting with the next checkup, this report will show your trend versus today."
- `비교:` `숙제:` 줄의 **값 부분도 한국어 원형 유지** (해결/그대로/신규/악화 — 채점기 파싱 계약)

## 9) 기계 판독용 발견ID 블록 (보고서 맨 마지막 줄)

```
발견ID: DUP-01, BIG-03, DOC-02
```

- 형식·순서·`(없음)` 규칙 전부 정본과 동일. **이 줄 아래에는 아무것도 쓰지 않는다.**

---

## 숫자·날짜·경로 표기

- 날짜는 정본과 동일한 ISO(`YYYY-MM-DD`), 숫자 구분은 쉼표(1,011 lines), 파일 경로·코드 식별자는 원형 그대로.
- 이모지 신호등(🔴🟡🟢⚪)과 절 이모지(🏥👉📅🎉)는 정본과 동일하게 유지 — 언어가 바뀌어도 시각 언어는 같아야 한 제품이다.
