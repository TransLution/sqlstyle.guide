# Changelog

One entry per commit, newest first: date and time, who, Jira keys, and **why**.
`git log` already records the date, the author and the files changed. Each entry here exists
for the reasoning the diff cannot show. There is no commit hash in the heading: a file cannot
contain the hash of the commit that contains it.

## 2026-10-05 16:45 — Grant Rodger <grodger@translutionsoftware.com>

docs(reference): bootstrap the reference pattern onto main

Jira: none
Files: `reference/`, `AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md`, `.claude/rules/`,
`.gitattributes`, `.gitignore`, `_config.yml`, `README.md`

Rolled the estate's reference pattern out to the fork. The audit scored it PARTIAL, 2/10.
No reference existed on any branch, so this is a bootstrap, not a consolidation.

There was no `main`. The default was `gh-pages`, frozen at `44f5e91` (2021-03-10) and 27
commits behind upstream, with nothing of its own (`git rev-list --count
upstream/gh-pages..44f5e91` = 0). So `main` was created from `upstream/gh-pages` (`70b612f`)
as a pure fast-forward and made the default branch. That catches up eight translations and
two English-guide fixes, and loses nothing. Before this PR, `main` was pushed and the
default switched directly; both were agreed with Grant beforehand. `gh-pages` and the seven
inherited branches were left in place on purpose.

The one upstream file edited for behaviour is `_config.yml`, which gains an `exclude:`
block. GitHub Pages renders front-matter-less markdown and runs Liquid in it, so without
the block the agent contract and `reference/` would publish on the site. The block was
**not** exercised by a Jekyll build, because this machine has no Ruby. That is recorded in
the README handover and in finding F-03. `.gitignore` gains the estate's
`[Bb]in/` / `[Oo]bj/` build-output rule (modelled on TransLutionServices) and an editor/tool
block, both above an upstream marker. `README.md` gains a TransLution section above
upstream's unchanged text.

Ruled out: restating the guide in `reference/`. It would drift from upstream, and the
estate cites the public site, not the fork. TransLution's house style stays in
`translution-wiki`. An org-wide code search found no repository that depends on this fork.

`Test-LanguageWiring.ps1` is new. The first draft passed a `pt-BR/` directory because
`Test-Path` is case-insensitive on NTFS; it now compares names case-sensitively. Both
failure modes were shown to fail in a scratch copy.
