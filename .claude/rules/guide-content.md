---
paths:
  - "_includes/sqlstyle.guide*.md"
  - "*/index.md"
  - "index.md"
---

# Editing the guide or a translation — stop first

This content is **upstream's**, not TransLution's. Simon Holywell's guide, licensed
CC BY-SA 4.0 (`LICENCE`). The fork carries no content edits of its own, and that is
deliberate: it is what keeps `git merge upstream/gh-pages` a fast-forward.

Before you change anything under this path, decide which of these you are doing:

| You want to… | Do this instead |
|---|---|
| fix a typo, a wrong example, a stale translation | open a PR against `treffynnon/sqlstyle.guide`, then sync the fork |
| record how **TransLution** writes SQL differently | edit `translution-wiki` → `wiki/concepts/sql-style-conventions.md` |
| genuinely diverge the fork's published guide | stop and ask — it ends clean syncs, and under CC BY-SA the result must carry the same licence and attribution |

## If you are editing upstream (in a PR there)

- `_includes/sqlstyle.guide.md` is the English source. Every translation is a full copy,
  not a diff, so a change to English silently leaves 15 translations behind.
  `reference/02-site/02-translations.md` measures that lag.
- **Never put front matter or Liquid into an `_includes/sqlstyle.guide*.md` file.** They are
  pulled in by an `include` tag from each language's `index.md`, which is where the
  front matter belongs.
- A new language needs four pieces that must agree. Run
  `reference\_harness\Test-LanguageWiring.ps1` — Jekyll will not tell you which one is missing.
