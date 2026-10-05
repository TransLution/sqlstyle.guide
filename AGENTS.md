# AGENTS.md — sqlstyle.guide (TransLution fork)

<!-- reference-stamp: 70b612ffab19522c416c206ee75ab70bff1004a3 -->

The operating contract for anyone, human or agent, working in this repository.
Documented against `main` at `70b612f`. Start with `reference/README.md`.

## What this is

TransLution's fork of Simon Holywell's SQL style guide (`treffynnon/sqlstyle.guide`):
a static Jekyll site with one English guide (`_includes/sqlstyle.guide.md`) and fifteen
translations. The estate uses it as one of five cited sources for the SQL house style in
`translution-wiki` (`wiki/concepts/sql-style-conventions.md`).

## What this is not

- **Not TransLution's SQL style.** That is the wiki page above. Where it and this guide
  disagree (the keyword "river", the `tbl_` prefix), the house style wins.
- **Not TransLution content.** The fork carries no edits to the guide.
- **Not published.** GitHub Pages is off for the fork. The live site is upstream's.
- **Not a dependency.** No repository builds from, submodules or links to this fork
  (org-wide code search, 2026-10-05).

## Invariants

Each of these can be broken this week without anyone noticing.

1. **Do not edit the guide or a translation here.** Fix it upstream with a PR to
   `treffynnon/sqlstyle.guide`, then sync. A content edit in the fork turns every future
   sync into a hand merge. And because of CC BY-SA 4.0 (`LICENCE`), it makes the fork a
   derivative work that must carry the same licence and attribution.
   `.claude/rules/guide-content.md` loads on those files.
2. **TransLution owns only these paths:** `reference/`, `AGENTS.md`, `CLAUDE.md`,
   `CHANGELOG.md`, `.claude/`, `.gitattributes`, the blocks above the upstream marker in
   `.gitignore`, the `exclude:` block at the end of `_config.yml`, and the TransLution
   section at the top of `README.md`. Everything else is upstream's. Keep each of these
   edits contiguous, so a sync conflicts on as few lines as possible.
3. **Keep the `exclude:` block in `_config.yml`.** Without it, GitHub Pages renders the
   files in invariant 2 as public pages and runs Liquid inside them. Jekyll 3 *replaces* its
   default excludes with this list, so do not trim the entries that look redundant.
4. **Do not enable GitHub Pages on the fork** until `CNAME`, `url` and `ga_code` stop
   naming upstream's domain and analytics (`reference/00-findings.md`, F-02).
5. **A language is four things that must agree:** the `langs:` key, the
   `_includes/sqlstyle.guide.<code>.md` file, `<dir>/index.md` with `lang: <code>`, and a
   directory named in lower case. `reference\_harness\Test-LanguageWiring.ps1` must exit 0.
6. **`main` is the working line; `gh-pages` is frozen** at the fork's 2021 state. Nothing
   targets `gh-pages`. Sync upstream into `main` (`reference/01-repository/01-fork-and-upstream.md`).

## Build

```bash
bundle install && bundle exec jekyll serve     # http://localhost:4040
```

Needs Ruby. `flake.nix` gives a Nix shell for direnv users. **Not run when this contract
was written** (no Ruby on that machine). Nobody has yet built the site against `70b612f`
or the `exclude:` block.

## Test

There are no upstream tests. The TransLution checks are read-only PowerShell 5.1 scripts
plus Python 3 for the navigator:

```powershell
reference\_harness\Verify-Reference.ps1      # anchors, provenance stamp, no hard-coded paths
reference\_harness\Test-LanguageWiring.ps1   # 16/16 languages wired at 70b612f
reference\_build\publish.ps1                 # regenerate reference/navigator.html
reference\_build\Install-Hooks.ps1           # once per clone
```

## Where risk concentrates

- `_config.yml`: the language registry, the exclude block, and upstream's domain and analytics.
- `_includes/layout_partials/languages.html`: builds the language menu from any page with `lang:`.
- `static/scripts.js`: lower-cases the language code into a URL.

## Conventions

- Branch from `main`, PR into `main`. Jira keys (`DEV-\d+`) go in the branch name and the
  commit message where there is a ticket.
- Every commit gets a `CHANGELOG.md` entry: date and time, who, Jira keys, and **why**.
- Line endings: the hook must stay LF (`.gitattributes`). Everything else follows upstream.

## Definition of done

- `Verify-Reference.ps1` and `Test-LanguageWiring.ps1` exit 0, and `navigator.html` is regenerated.
- `git ls-files -i -c --exclude-standard` prints nothing.
- No edits to upstream-owned paths beyond invariant 2.
- `CHANGELOG.md` entry written; any new standing caveat added to the `README.md` handover, with a date.
- Anything not run is said to be not run.
