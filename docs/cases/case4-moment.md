# Clinical case 4 — Moment.js: checkup of a retired giant

> **Patient**: [moment/moment](https://github.com/moment/moment) (checkup at commit `18aba13`, 657 files after exclusions) · **Checkup date**: 2026-07-20 · **Skill**: project-doctor v2.8.0, checkup mode, English report
> **Disclaimer**: Moment is one of the most successful libraries in JavaScript history, and its team retired it *on purpose, honestly, and gracefully* — the project status page tells users to pick something newer. This case examines what a legacy-mode codebase looks like on a health chart; it is not criticism of the maintainers. All findings were re-verified by a human-directed second pass (including the duplicated-bundle claim, confirmed at function-body level and across all 137 locale files) before publication.

## The story

For a decade, `moment` *was* how JavaScript handled dates — hundreds of millions of downloads. In 2020 the team did something rare: they declared the project finished and recommended alternatives. What does a health checkup of a deliberately-frozen legend look like?

## Strengths first

- **Tests graded 🟢 A** — an enormous test suite, still passing CI, is exactly why the frozen library keeps working.
- **Safety graded 🟢 A** — no hard-coded paths or secrets anywhere.
- The retirement itself is a model of project honesty: a clear status, clear advice, no silent abandonment.

## What the checkup found

Because the project exceeds the 100-file threshold, the skill's **size guard** engaged automatically: a fast checkup limited to the 11 core catalog items, with that limitation disclosed in the report — the chart never pretends it examined more than it did.

| | |
|---|---|
| **Overall grade** | 🔴 **D — Treatment needed** (Structure D · Tidiness B · Docs B · Tests A · Safety A) |
| **Ship verdict** | 🚫 Not ready to ship (as a codebase to build on — which is precisely what its own maintainers say) |
| Findings | 🔴 2 Critical · 🟡 1 Recommended · ⚪ 2 Note |

- 🔴 **[DUP-01]** Source code is duplicated into checked-in build artifacts: the same functions exist in `src/`, in the committed `moment.js` bundle, and in `min/` bundles — a pattern repeated across all **137 locale files** (`src/locale/` ↔ `locale/`). Edit one copy, and the others silently drift.
- 🔴 **[BIG-01]** Six files exceed 1,500 lines (the largest checked-in artifact reaches 149,292 lines; the largest hand-written test file is 2,919 lines).
- 🟡 **[DOC-02]** The README is a 55-line signpost with no install/usage instructions of its own — fine for a retired project's homepage, hard for a newcomer holding only the repo.
- ⚪ **[DEAD-02]** A commented-out test block; ⚪ **[BIG-02]** fifteen 51–89-line functions in `src/lib`.

## What it means

The D grade is not a scandal — it is **what "finished" looks like from the inside**. Checked-in build bundles and giant files were normal engineering for the pre-bundler era this project was born in. The chart makes the trade-off visible: the tests that keep it alive grade A, while the structure that would make it *evolvable* grades D. Which is exactly why its own team told you to use something newer.

**Full report** (including the size-guard disclosure): [reports/moment-checkup-en.md](./reports/moment-checkup-en.md)
