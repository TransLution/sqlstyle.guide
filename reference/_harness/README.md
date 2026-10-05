# Harness

Executable checks for `reference/`. All of them are read-only, resolve paths from their own
location, and run on stock Windows PowerShell 5.1. Exit 0 = pass.

## `Verify-Reference.ps1`

Three mechanical checks, ported from TransLutionScanner:

1. **Line anchors.** Every `file.ext:NNN` cited in `reference/*.md` still resolves, and the
   file is long enough to contain that line. The extension list covers what this reference
   cites: `.md`, `.yml`, `.html`, `.js`, among others.
2. **Provenance.** The `reference-stamp` in `AGENTS.md` is a commit that is an ancestor of `HEAD`.
3. **Portability.** No script under `reference/` hard-codes an absolute user path.

Anchors match files by **basename**, so cite unique names: `sqlstyle.guide.md:174` works,
but a line in a language `index.md` cannot be cited this way, because 16 files share that name.

## `Test-LanguageWiring.ps1`

The riskiest change in this repository is adding or renaming a language. A language is
four things that must agree, and Jekyll checks none of them:

- the `langs:` key in `_config.yml`
- `_includes/sqlstyle.guide.<code>.md`
- `<dir>/index.md`, with `lang: <code>` and an include of that file
- a directory named in lower case, because `static/scripts.js` lower-cases the URL

The check runs in both directions. It also catches an include, or a page carrying
`lang:`, that the config does not know about.

At `70b612f`: 16/16 languages pass. It has been shown to fail when the wiring breaks.
In a scratch copy (2026-10-05), renaming `pt-br/` to `pt-BR/` gave 1 failure and exit 1,
and setting `de/index.md` to `lang: xx` gave 2 failures and exit 1. The first case matters
because `Test-Path` is case-insensitive on NTFS: an earlier draft passed it, and would
have shipped a 404 to the case-sensitive Pages host. The check now compares the real
directory name, case-sensitively.

## Not covered

- No Jekyll build. There was no Ruby on the machine that wrote this harness, so whether
  `_config.yml`'s `exclude:` block works is asserted, not tested (`00-findings.md`, F-03).
- Translation *content* lag. `02-site/02-translations.md` is a heading-level measurement,
  and its commands are in the page, not here.
