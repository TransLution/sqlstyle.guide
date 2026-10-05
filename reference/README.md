# sqlstyle.guide (TransLution fork) — reference

**Start here, not with the source.**

This is TransLution's fork of [Simon Holywell's SQL style guide](https://www.sqlstyle.guide)
(`treffynnon/sqlstyle.guide`). It contains a Jekyll site: one English guide, fifteen
translations, a layout and a stylesheet. TransLution has made **no content changes** to
it. The fork exists so the guide sits inside the estate, beside the repositories whose
SQL it informs.

Documented against `main` at `70b612f` (upstream `gh-pages`, 2026-03-17).

## Read in this order

| Page | What it answers |
|---|---|
| [00-findings.md](00-findings.md) | What is wrong or surprising, ranked — read this first |
| [01-repository/01-fork-and-upstream.md](01-repository/01-fork-and-upstream.md) | Why `main` exists, what the other branches are, and how to sync from upstream |
| [02-site/01-build-and-wiring.md](02-site/01-build-and-wiring.md) | How the site is assembled, and the four places a language is wired |
| [02-site/02-translations.md](02-site/02-translations.md) | How far each translation lags the English source, measured |
| [03-estate/01-translution-usage.md](03-estate/01-translution-usage.md) | Where the estate uses this guide, and where TransLution's house style departs from it |

`navigator.html` is a single-file, offline, browsable copy of everything here. It is
**generated** by `_build/publish.ps1`; never edit it by hand.

## Scope

In scope: the repository, its branches, the build, the language wiring and translation
lag, and the guide's links to the rest of the estate.

Out of scope, on purpose: restating the guide. The English source is
`_includes/sqlstyle.guide.md`; read it there. TransLution's own SQL conventions are in
`translution-wiki`, not here.

## Counts

Every count below is of files git tracks on `main` at `70b612f` and **excludes
`reference/` and the TransLution agent files** (`AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md`,
`.claude/`, `.gitattributes`). Upstream tracks **58** files: 16 guide sources in
`_includes/`, 16 language `index.md` stubs, 11 layout files (6 partials, 2 layouts,
3 inlined assets in `_includes/static/`), 5 files in `static/`, and 10 config, licence
and dev-environment files at the root.

```bash
git ls-files -- . ':!reference' ':!AGENTS.md' ':!CLAUDE.md' ':!CHANGELOG.md' ':!.claude' ':!.gitattributes' | wc -l
```

## Checks

```powershell
_harness\Verify-Reference.ps1      # line anchors resolve, provenance stamp, no hard-coded paths
_harness\Test-LanguageWiring.ps1   # every language: config, include, page, lower-case dir
_build\publish.ps1                 # regenerate navigator.html
_build\Install-Hooks.ps1           # once per clone: the pre-commit hook runs the above
```
