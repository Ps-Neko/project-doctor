# Spec: Localized README guides

## Objective

Improve the repository's GitHub landing pages for people evaluating Project Doctor for the first time. The English README must show an English report image; the Korean README must show a Korean report image. Both pages should use direct, plain-language copy and include a compact visual that explains the user journey.

## Assumptions

1. The GitHub README is the intended "page"; there is no separate web application to change.
2. Existing report examples are representative and can be used to create static documentation images.
3. The skill's behavior, report contract, and installation commands are out of scope.

## Commands

```powershell
python -m pytest tests/ -v
python tests/check_links.py
```

## Project structure

- `README.md`: English GitHub landing page.
- `README.ko.md`: Korean GitHub landing page.
- `docs/assets/`: README images, named by language and purpose.
- `tests/check_links.py`: validates local Markdown links.

## Content style

- Use the same meaning in both languages; adapt the wording naturally instead of translating word-for-word.
- Lead with the reader's outcome, then provide concise supporting detail.
- Give every image a descriptive alt label in its own language.
- Keep code blocks and safety disclosures technically unchanged unless a wording edit preserves the exact command and meaning.

## Testing strategy

- Verify every new local asset exists and every Markdown link passes `python tests/check_links.py`.
- Review both README files as rendered Markdown to confirm that their screenshots match their surrounding language and that the flow visual remains legible.
- Run the full Python test suite because README/version/link checks are part of CI.

## Boundaries

- Always: preserve bilingual parity, preserve all working commands, and keep the existing safety disclosures.
- Ask first: modify the skill instructions, report templates, CI configuration, or dependencies.
- Never: alter diagnosis logic or falsely present a mocked report as a live product screen.

## Success criteria

1. English and Korean README files each embed a report sample in the same language as their page.
2. Both README files include a simple, localized "how it works" visual.
3. The opening and navigation copy is clearer without changing product claims.
4. Link validation and the full test suite pass.

## Open questions

None. The approved scope is documentation, images, and copy only.
