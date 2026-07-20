# Clinical case 3 — left-pad: the 11 lines that broke the internet

> **Patient**: [left-pad](https://github.com/left-pad/left-pad) (checkup at commit `2fca615`, 11 files) · **Checkup date**: 2026-07-20 · **Skill**: project-doctor v2.8.0, checkup mode, English report
> **Disclaimer**: this is a respectful post-mortem of a famous, archived open-source project — not a judgment of its authors. The 2016 incident was an npm registry policy event, not a code-quality failure. All findings below were re-verified by a human-directed second pass against the actual files before publication.

## The story

In March 2016, an 11-line utility that pads strings was unpublished from npm — and builds broke across the industry, from Babel to React tooling. left-pad became the symbol of "the whole internet stands on tiny packages". So: if we give those famous 11 lines an actual health checkup today, what does the chart say?

## Strengths first

- **The core is genuinely healthy.** README, license, `package.json`, type definitions, and tests are all present. Docs, tests, and tidiness all graded 🟢 A.
- The library does exactly one thing, in one small file — the kind of single-responsibility shape most projects should envy.

## What the checkup found

| | |
|---|---|
| **Overall grade** | 🟢 **B — Fair** (weighted total 1.5 pts) |
| **Ship verdict** | ✅ Ready to ship |
| Findings | 🟡 1 Recommended · ⚪ 1 Note |

- 🟡 **[DUP-01]** The same 10-line input-normalization block is copy-pasted between two benchmark scripts (`perf/O(n).js:1-10` ↔ `perf/es6Repeat.js:1-10`).
- ⚪ **[HARD-02]** Repeated magic values in the benchmark harness (`perf/perf.js` — `'abcd'` ×3 and a 100-character digit string ×3), plus two unused variables.

## What it means

The code that "broke the internet" is, by the chart, **fit to ship** — its only findings live in the benchmark folder, not the library. The 2016 outage was never about this code's health; it was about how much weight the ecosystem had stacked on it. A checkup can tell those two stories apart in one page.

**Full report**: [reports/leftpad-checkup-en.md](./reports/leftpad-checkup-en.md)
