# How the estate uses this guide

Checked on 2026-10-05 with an org-wide code search
(`gh search code sqlstyle --owner TransLution`) and by reading `estate.json`.

## No code depends on this repository

No repository builds from it, submodules it, vendors it, or links to the fork's URL.
It has no package, no artefact and no consumers. Changing or archiving it breaks nothing
downstream.

## `translution-wiki` cites the guide, through the public site

All 13 hits are in `TransLution/translution-wiki`, and every one points at the
**public site** (`https://www.sqlstyle.guide/`), never at this fork:

| Wiki page | Role |
|---|---|
| `wiki/sources/sqlstyle-guide-holywell.md` | source summary. Records the author, the licence (CC BY-SA 4.0) and the ingestion date (2026-04-30) |
| `wiki/concepts/sql-style-conventions.md` | **TransLution's SQL house style.** Cites this guide alongside four others |
| `wiki/concepts/database-design-principles.md`, `custom-project-tables.md` | cite it on naming, including the `tbl_` prefix |
| `reference/01-estate/01-repository-map.md` | lists this repo as "not TransLution product code; a fork" |
| `reference/_data/repository-inventory.psv` | inventory row, still showing branch `gh-pages`, pushed 2021-03-10 |

The last row is now stale. The default branch is `main` and the repository was pushed on
2026-10-05. It refreshes the next time the wiki's estate inventory is regenerated; it is
not edited from here.

## Where TransLution's house style departs from this guide

The wiki adopts this guide's **upper-case keywords**, but departs from it on purpose in
at least two places:

- **Keyword alignment.** The guide's "river", with keywords right-aligned to a shared
  boundary (`sqlstyle.guide.md:174`, joins at `sqlstyle.guide.md:257`), is rejected in
  favour of left-aligned keywords.
- **The `tbl_` prefix.** The guide treats it as an anti-pattern. TransLution keeps it for
  custom and legacy tables, for consistency with existing schemas.

The authoritative list is the wiki page itself, not this summary. **Read
`sql-style-conventions.md` before applying anything from this guide to TransLution SQL.**
Where the two disagree, the house style wins.

## Licence

The guide is CC BY-SA 4.0 (`LICENCE:3`). Citing and summarising it, as the wiki does, needs
attribution, and the wiki gives it. Copying substantial text into a TransLution document
makes that document a derivative, which must carry the same licence. Keep house-style
material as TransLution's own words, with links.
