# Implementation plan: Localized README guides

## Overview

Replace the shared report image with language-matched samples, add a small localized journey diagram, and tighten the README entry copy while preserving installation and safety content.

## Architecture decisions

- Store static assets in `docs/assets/` so GitHub renders them without external hosting.
- Use SVG for the journey diagrams: the text remains crisp, the files are reviewable, and no new dependency is needed.
- Use report samples derived from existing repository report content, not AI-generated images.

## Tasks

### Task 1: Add localized documentation visuals

**Acceptance criteria:**
- English and Korean report sample assets are distinct and visibly use the correct language.
- English and Korean journey diagrams state the same four-step workflow in their own language.

**Verification:** Inspect the assets and confirm all four files exist.

**Files:** `docs/assets/report-sample-en.*`, `docs/assets/report-sample-ko.*`, `docs/assets/how-it-works-en.svg`, `docs/assets/how-it-works-ko.svg`.

### Task 2: Refactor README entry sections

**Acceptance criteria:**
- Each README embeds only its language's report image and journey diagram.
- Opening copy, navigation links, and usage introduction are concise and natural in each language.

**Verification:** Render/read both Markdown files; run link validation.

**Files:** `README.md`, `README.ko.md`.

### Checkpoint: Documentation integrity

- [ ] `python tests/check_links.py` passes.
- [ ] Both language pages use matching images and no commands changed.

### Task 3: Run repository regression checks

**Acceptance criteria:** Existing quality checks still pass.

**Verification:** `python -m pytest tests/ -v`.

**Dependencies:** Tasks 1-2.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Image text becomes unreadable on GitHub | Use generous type sizes and SVG for the workflow visual. |
| The two pages drift in meaning | Edit corresponding sections together and compare their structure. |
| Markdown embeds an absent asset | Run the repository link checker and inspect asset paths. |
