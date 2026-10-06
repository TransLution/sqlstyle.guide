# Translations — measured lag

Every translation is a **full copy** of the guide, not a diff. When upstream edits the
English source (`_includes/sqlstyle.guide.md`), nothing marks the fifteen copies as
behind. This page measures how far behind they are.

Measured at `70b612f`. The English source has had 44 commits; its last change was
`d1c856a` (2024-02-27, the join exception). It has **6 `##` and 18 `###` headings**.

| Language | Include | Last changed | English commits since | `##` / `###` | Missing vs English |
|---|---|---|---|---|---|
| Arabic | `sqlstyle.guide.ar.md` | 2026-02-24 | 0 | 6 / 18 | — |
| Spanish | `sqlstyle.guide.es.md` | 2026-03-17 | 0 | 6 / 18 | — |
| French | `sqlstyle.guide.fr.md` | 2024-02-27 | 1 | 6 / 18 | — |
| Japanese | `sqlstyle.guide.ja.md` | 2024-02-27 | 1 | 6 / 17 | Column data types |
| Polish | `sqlstyle.guide.pl.md` | 2024-02-27 | 1 | 6 / 18 | — |
| Portuguese (BR) | `sqlstyle.guide.pt-BR.md` | 2024-02-27 | 1 | 6 / 17 | Column data types |
| Turkish | `sqlstyle.guide.tr.md` | 2024-02-27 | 1 | 6 / 18 | — |
| Ukrainian | `sqlstyle.guide.ua.md` | 2024-02-27 | 1 | 6 / 18 | — |
| Vietnamese | `sqlstyle.guide.vn.md` | 2024-02-27 | 1 | 6 / 18 | — |
| German | `sqlstyle.guide.de.md` | 2024-02-27 | 2 | 6 / 17 | Column data types |
| Italian | `sqlstyle.guide.it.md` | 2024-02-27 | 2 | 5 / 17 | Overview heading; Preferred formalisms |
| Korean | `sqlstyle.guide.ko.md` | 2024-02-27 | 2 | 6 / 18 | — |
| Russian | `sqlstyle.guide.ru.md` | 2024-02-27 | 2 | 6 / 17 | Column data types |
| Simplified Chinese | `sqlstyle.guide.zh.md` | 2024-02-27 | 4 | 6 / 18 | — |
| Traditional Chinese | `sqlstyle.guide.zh-TW.md` | 2024-02-27 | 4 | 6 / 18 | — |

**How to read "English commits since".** It counts commits to the English file after the
translation's own last commit. Many translations were last touched by the same 2024-02-27
whitespace sweep, so a low number is **not** proof the content is current. It bounds the
lag from below; it does not measure it. Missing sections were found by comparing heading
counts, then reading the `###` lists side by side. A translation can match on headings and
still lag inside a section.

```bash
f=_includes/sqlstyle.guide.de.md
last=$(git log -1 --format=%H -- $f)
git log --oneline $last..HEAD -- _includes/sqlstyle.guide.md | wc -l   # English commits since
grep -c '^## ' $f; grep -c '^### ' $f                                 # heading counts
```

These are upstream's to fix ([F-04](../00-findings.md)). TransLution uses none of the translations.
