# 🏥 Project Health Checkup Report — messy-project

```
Patient: messy-project · Checkup date: 2026-06-13 · Files analyzed: 12 (after applying the exclusion list — self-test answer keys excluded)
Skill version: v2.8.0 · Mode: Checkup
```

## Overall Assessment

# 🔴 D — Treatment needed

> How to read the grade: 🟢 A Healthy · 🟢 B Fair · 🟡 C Caution · 🔴 D Treatment needed
> ※ The overall grade is not an average of the areas — it is a **weighted total** of finding counts and severity, so it can be lower than any single area.

**Ship verdict: 🚫 Not ready to ship — treatment recommended.**

**Doctor's note**: A small project with issues spread evenly across the board. Start with the code that calculates order totals, which has been copy-pasted into 3 places (Critical 1) — once that is fixed, the remaining fixes will be easier to handle safely.

## Findings by Area

| Area | Verdict | Note |
|------|------|------|
| Structure | 🟡 Needs attention (C) | The order-total calculation is copy-pasted in 3 places, and one file is over 1,000 lines long |
| Tidiness | 🟡 Needs attention (C) | Backup files, abandoned experiments, and blocks of commented-out code are still lying around |
| Docs | 🟡 Needs attention (C) | There is no README and no list of required packages (requirements.txt) |
| Tests | 🟢 Fair (B) | There are no automated checks (tests), but the project is small enough that this is not urgent |
| Safety | 🟡 Needs attention (C) | A folder path that only exists on one specific computer, and an internal server address, are hard-coded |

## Today's Prescription

Diagnosis: 🔴 Critical 3 · 🟡 Recommended 7 · ⚪ Note 5
👉 **If you fix just one thing today**: Critical 1 (duplicated order-total code) — to approve this fix, say "Fix Critical 1".
📅 **Recommended re-checkup**: 2026-06-27 (per the fixed grade schedule — grade D means 14 days)

> More than 10 findings — the report body lists all Critical items plus the top 5 Recommended; the rest appear one line each in the Appendix at the end.

### 🔴 Critical 1 [DUP-01] — The order-total calculation is copy-pasted into 3 files
- **What does this mean?** The same piece of code (`calc_order_total` — computes the order total including discounts and shipping) exists in 3 places. Fix one copy and you still have to fix the other two; miss one and you have a bug. Because this is core money-handling logic, it is graded Critical.
- **Where?** `main.py:15`, `utils.py:17`, `helpers.py:26`
- **If we fix it?** Keep one copy and have the other two call it. Estimated work: 3 files edited.
- **Approval command:** "Fix Critical 1"

### 🔴 Critical 2 [HARD-01] — A computer-specific folder path is hard-coded
- **What does this mean?** The data-file path is fixed to `C:\Users\kim\Desktop\...`. No other computer has that folder, so the program fails with an error the moment anyone else runs it.
- **Where?** `main.py:12` (`DATA_FILE = r"C:\Users\kim\Desktop\orders\data.csv"`)
- **If we fix it?** Move the path into a config file (config.json) or a relative path inside the project (e.g. `data/orders.csv`) so it runs on any computer. Estimated work: 1–2 files edited.
- **Approval command:** "Fix Critical 2"

### 🔴 Critical 3 [DOC-01] — The project has no README
- **What does this mean?** The only way to learn what this project does, or how to start it, is to read the code. That is hard for other people — and for you, six months from now.
- **Where?** Project root folder (0 README* files found)
- **If we fix it?** Even a one-page README (what it is, how to run it, what it needs) makes hand-over far easier. Estimated work: 1 new file.
- **Approval command:** "Fix Critical 3"

### 🟡 Recommended 1 [DEAD-01] — A function that nothing ever calls
- **What does this mean?** A function was written and is never called from anywhere. It wastes the reader's time and leaves behind the nagging question "is it safe to delete this?"
- **Where?** `utils.py:33` (`legacy_discount` — old membership-tier discount, 0 calls)
- **If we fix it?** Delete it, or if you truly plan to use it again, leave a comment saying so. Estimated work: 1 file edited.
- **Approval command:** "Fix Recommended 1"

### 🟡 Recommended 2 [BIG-01] — A file over 1,000 lines long
- **What does this mean?** One file is 1,011 lines. Think of a 1,011-page book chapter with no table of contents — hard to search, hard to edit safely.
- **Where?** `static_data.js` (1,011 lines — over the 800-line threshold; data arrays and lookup functions are mixed together)
- **If we fix it?** Split data (the product list) and logic (the lookup functions) into 2 files, so price edits and feature edits stop stepping on each other. Estimated work: 1 new file, 1 file edited.
- **Approval command:** "Fix Recommended 2"

### 🟡 Recommended 3 [HARD-03] — An internal server address (IP) is written directly in the code
- **What does this mean?** The server address is hard-coded. If the address changes you must edit the code, and an internal address could leak outside.
- **Where?** `helpers.py:3` (`ORDERS_API_URL = "http://192.168.0.10/api/orders"`)
- **If we fix it?** Move the address into a config file such as config.json. Estimated work: 2 files edited.
- **Approval command:** "Fix Recommended 3"

### 🟡 Recommended 4 [DOC-03] — No list of required packages
- **What does this mean?** The code uses the external package `requests`, but there is no file (requirements.txt) saying what must be installed. On a new computer, someone has to find out by trial and error.
- **Where?** Project root folder (0 requirements.txt / pyproject.toml files)
- **If we fix it?** A one-line `requirements.txt` (`requests`) solves it. Estimated work: 1 new file.
- **Approval command:** "Fix Recommended 4"

### 🟡 Recommended 5 [TEST-01] — No automated checks (tests) at all
- **What does this mean?** There is no safety net that automatically confirms "it still works" after a change. Right now every change means a human has to re-run everything by hand.
- **Where?** Whole project (0 tests/ folders, test_*.py files, etc.)
- **If we fix it?** Start with one test for the money-calculation function — then the de-duplication work (Critical 1) can proceed with confidence too. Estimated work: 1 new file.
- **Approval command:** "Fix Recommended 5"

## Appendix: Remaining findings

- 🟡 [TMP-01] Leftover temp/backup files — `old_main.py.bak` (an old copy of main.py, ~23 lines)
- 🟡 [STALE-02] An abandoned experiment file — `test123.py` (~9 lines, referenced by nothing)
- ⚪ [DEAD-02] A block of commented-out code — ~15 lines inside `helpers.py`
- ⚪ [BIG-02] An oversized function — `process_orders` in `main.py`, ~70 lines
- ⚪ [BIG-03] Deep nesting — `flag_risky_orders` in `helpers.py` (more than 4 levels)
- ⚪ [HARD-02] Repeated magic numbers — 50000 · 30000 · 3000 · 0.05, each appearing 3 times (a by-product of the duplication in Critical 1)
- ⚪ [STALE-01] Fossilized TODO/FIXME notes — 6 in total (3 in main.py + 3 in helpers.py)

> How the grade is computed: catalog-weighted total (🔴 3 pts · 🟡 1 pt · ⚪ 0.5 pt) — overall 18.5 pts (D). Never graded "by feel".

## Next Visit
- When would you like the next checkup? (Suggested: 2026-06-27 — same date as the re-checkup above)
- Also consider: if this project is headed for company sharing or a public GitHub release, try `release-check` (the pre-release checkup).
- Starting with the next checkup, this report will show your trend versus today (better / unchanged / worse).

The two lines below are machine-readable grader markers, intentionally kept in Korean.
숙제: DUP-01

발견ID: DUP-01, DEAD-01, DEAD-02, BIG-01, BIG-02, BIG-03, HARD-01, HARD-02, HARD-03, DOC-01, DOC-03, TEST-01, TMP-01, STALE-01, STALE-02
