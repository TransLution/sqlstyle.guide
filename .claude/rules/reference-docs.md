---
paths:
  - "reference/**"
---

# Working on the reference

## What this reference is for

This repository is a **fork of someone else's style guide**. `reference/` documents the
fork — what it is, how the site builds, how far the translations lag, and how TransLution
uses the guide. It does **not** restate the guide. Link to `_includes/sqlstyle.guide.md`
by line instead; a paraphrase will drift from the source the moment upstream edits it.

TransLution's own SQL house style lives in `translution-wiki`
(`wiki/concepts/sql-style-conventions.md`), not here. Record where the house style
departs from this guide by linking to that page, never by copying its tables.

## Every number comes from a command

Not from memory, not from a previous version of the page. Each figure in `reference/`
names the command that produced it, so the next person can re-run it. If a figure
surprises you, derive it a second way before writing it down.

Count what git tracks (`git ls-files`), never what is on disk — a local `jekyll build`
writes `_site/`, and that is a contamination bug, not a finding. Exclude `reference/`
itself from any count describing the site.

## Never put Liquid in a page that Jekyll can render

GitHub Pages' Jekyll renders `.md` files **without** front matter (jekyll-optional-front-matter
is on by default). `_config.yml` excludes `reference/` and the root agent files for exactly
this reason. If you remove that exclusion, a page here that quotes a Liquid tag will
*execute* it and can break the site build. Describe tags in prose, or in a fenced block
with the braces separated (`{ % include … % }`).

## Findings

Shape, without exception: **claim → evidence (`file:line`) → consequence → fix.**
Ids (`F-01` …) are stable identifiers, not ranks. Do not renumber.
A finding about upstream content is fixed **upstream**, by a PR to `treffynnon/sqlstyle.guide`,
not by editing the fork — see `AGENTS.md`, invariant 1.

## Corrections must be visible

If something here turns out to be wrong, correct it in place with a note saying what was
wrong. Do not quietly delete a row.

## Run before you commit

```powershell
reference\_harness\Verify-Reference.ps1      # anchors, provenance, portability
reference\_harness\Test-LanguageWiring.ps1   # every language wired end to end
reference\_build\publish.ps1                 # regenerate navigator.html
```

`reference/navigator.html` is generated. Never hand-edit it. A stale navigator is worse
than none. The pre-commit hook (`reference\_build\Install-Hooks.ps1`, once per clone)
rebuilds it for you.

## Diagrams

Use ```mermaid fenced blocks. Build every edge from evidence and say so in the caption.
**Avoid `#` in mermaid labels** — it is special and truncates silently.
