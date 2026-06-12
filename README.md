# 프로젝트 주치의 (Project Doctor)

[![CI](https://github.com/Ps-Neko/project-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/Ps-Neko/project-doctor/actions/workflows/ci.yml)

**AI로 만들다 엉킨 프로젝트를, 비개발자도 읽을 수 있는 진단 보고서로 바꿔주는 Claude Code 스킬입니다.**
무엇이 문제인지 → 어디를 고치면 되는지 → 무엇부터 승인하면 되는지. 승인한 것만 고치고, 항상 되돌릴 수 있게.

📄 **[3분 데모 — 실제 진단 보고서 보기](./DEMO.md)** · 📊 **[측정 기록 (EVALS)](./EVALS.md)**
🩺 **실제 사례**: [검진→치료→재검진 실치료기 (D→C)](./docs/cases/case1-reactor.md) · [은퇴한 전설 npm `request` 부검](./docs/cases/case2-request.md) · ❓ [FAQ — "그냥 Claude한테 시키면 되잖아요?"](./docs/FAQ.md)

> **현재 버전: v1.5.3** — 전 모드 동작 + 결과지 개편 + 처방 실행 전 전/후 변경 내용 미리보기 + 쓰기 경계 자동 검사 + 보고서를 마크다운/HTML(클리니컬 결과지 디자인)/PDF(내장 브라우저 자동 변환)/워드(변환 도구 있을 때)로 받기. 변경 이력: [CHANGELOG](./skills/project-doctor/CHANGELOG.md) · 라이선스: [MIT](./LICENSE)

## 무엇을 해주나요

| 모드 | 언제 쓰나 | 무엇을 주나 |
|------|----------|------------|
| 🩺 **건강검진** `checkup` | "이 프로젝트가 왠지 마음에 안 들어" | 진단 카탈로그(35종 ID) 기반 문제 진단 → 승인한 항목만 치료 → **되돌리기 한 줄** 보장 |
| 🔬 **정밀 검진** `checkup --deep` | 더 깊게 보고 싶을 때 | + git 이력 핫스팟("이 파일 6회 수정됨") · 의존성 점검 · AI 작업물 문진 |
| 📋 **초진 차트** `intro` | "이게 뭔지부터 모르겠다" / 인수인계 | 프로젝트 지도(핵심 파일 5개) · 실행법 · 만지면 위험한 곳 |
| 🔀 **방향전환** `pivot` | "방향을 바꿀까 고민 중" | 갈림길 비교 → 유지/수정/폐기 분류 → "멈춰도 동작하는" 마일스톤 계획 |
| 🚀 **공개 전 검진** `release-check` | 공유·공개·납품 직전 | 비밀키(git 과거 기록 포함)·개인정보 점검 → 통과/보류 판정 |

모든 보고서는 한국어로, 항목마다 **"무슨 뜻인가요? / 어디? / 고치면? / 승인 명령"** 을 함께 줍니다.

## ⚠️ 사용 전 꼭 알아두세요 (필수 고지)

1. **진단 시 프로젝트 내용이 Claude(Anthropic) 서버로 전송됩니다** (Claude Code의 기본 동작). 회사 기밀·고객 데이터가 포함된 프로젝트라면 회사의 AI 사용 정책을 먼저 확인하세요.
2. **비용**: 검진은 Claude 사용량(토큰)을 소모합니다. 정밀 검진(`--deep`)은 수 배 더 듭니다.
3. **검사 범위와 면책**: 진단 카탈로그에 정의된 알려진 패턴만 검사합니다. 보안 취약점 분석·법적 검토는 범위 밖이며, 결과에 대한 최종 판단과 책임은 사용자에게 있습니다.

## 설치 (Windows PowerShell 기준)

1. 이 저장소를 내려받습니다 (Code → Download ZIP 또는 `git clone`)
2. PowerShell을 열고 받은 폴더로 이동: `cd <받은 폴더 경로>`
3. 아래 명령 실행:

```powershell
New-Item -ItemType Directory -Force ~/.claude/skills
Copy-Item -Recurse -Force skills/project-doctor ~/.claude/skills/
```

4. **Claude Code를 새로 시작**하면 `/project-doctor`가 인식됩니다. (업데이트도 같은 명령을 다시 실행 — 여러 번 실행해도 안전)

macOS/Linux: `mkdir -p ~/.claude/skills && cp -r skills/project-doctor ~/.claude/skills/`

## 사용법

```
/project-doctor                      # 뭘 할지 모르면 — 접수 문진이 안내합니다
/project-doctor checkup "<경로>"      # 건강검진 (한글·공백 경로는 따옴표)
/project-doctor checkup --deep       # 정밀 검진
/project-doctor intro                # 초진 차트 (해설·인수인계)
/project-doctor pivot "<목표>"        # 방향전환 계획
/project-doctor release-check        # 공개 전 검진
```

## 안전장치 (설계 원칙)

1. **진단은 읽기 전용** — 보고서가 나오기 전에는 아무것도 고치지 않습니다
2. **승인한 것만 실행** — 한 번에 하나씩, 실행 전 "무엇이 바뀌는지" 목록 제시
3. **항상 되돌릴 수 있게** — 실행 전 체크포인트(git 또는 백업), 실행 후 되돌리기 명령 한 줄 제공. 되돌릴 방법이 없으면 실행하지 않습니다
4. **이력 기억** — 승인 시 `.project-doctor/`에 진료 기록을 남겨 다음 검진에서 "지난번보다 좋아졌는지" 비교

## 저장소 구성

```
skills/project-doctor/   ← 설치되는 스킬 본체 (SKILL.md + 참조 문서 8개)
tests/                   ← 품질 측정 도구: 채점 스크립트 + pytest
tests/fixtures/          ← 일부러 문제를 심은 테스트 프로젝트 4종 + 정답지
```

> ⚠️ `tests/fixtures/`의 비밀키·개인정보는 **전부 실존하지 않는 가짜**입니다 (스킬의 탐지 능력을 측정하기 위한 표본 — [tests/fixtures/README.md](./tests/fixtures/README.md) 참고).

## 품질 근거

- 검진 탐지율: **내부 표본(픽스처) 기준** — 독립 세션 측정에서 정답지 14건 대비 3회 연속 100% (합격선: 3회 최저치 80%)
- 비밀키 탐지: **내부 표본 기준** — 가짜 키 표본 3회 연속 100% + 오탐 0건 (합격선: 100% — 놓친 1건이 곧 사고)
- 모든 측정은 사람의 "감"이 아닌 **정답지(EXPECTED.md) ↔ 보고서 ID 기계 대조**로 수행 (오탐도 자동 미달 처리)

> ⚠️ 위 수치는 **이 저장소의 테스트 프로젝트(정답을 알고 만든 표본) 기준이며, 실제 프로젝트에서의 성능을 보증하지 않습니다.** 단일 모델·단일 시점 측정이고 외부 사용자 검증은 진행 전입니다 — 자세한 한계는 [EVALS.md](./EVALS.md)를 보세요.
