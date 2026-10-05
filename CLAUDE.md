@AGENTS.md

## Claude-only notes

- Path-scoped rules in `.claude/rules/` load when you touch the guide sources
  (`guide-content.md`), the site config and layouts (`site-config.md`), or `reference/`
  (`reference-docs.md`). Read them; they carry the reasons behind the invariants.
- If asked to "fix" something in the guide, the answer is almost always an upstream PR,
  not an edit here. Say so before editing (`AGENTS.md`, invariant 1).
- If asked what TransLution's SQL style is, point to `translution-wiki`
  (`wiki/concepts/sql-style-conventions.md`). This guide is one input to it.
- On Windows, Git Bash mangles `rev:path` arguments such as `git show origin/main:.gitignore`.
  Use PowerShell for those.
