---
paths:
  - "_config.yml"
  - "_layouts/**"
  - "_includes/layout_partials/**"
  - "static/**"
---

# Site configuration and layout

## `_config.yml` carries the fork's only upstream-file edit

The `exclude:` block at the bottom of `_config.yml` is TransLution's. It keeps
`reference/`, `AGENTS.md`, `CLAUDE.md`, `CHANGELOG.md` and `.claude/` out of the Jekyll
build. Without it, GitHub Pages renders those markdown files as pages (it turns on
jekyll-optional-front-matter by default), runs Liquid inside them, and publishes the
agent contract on the public site.

- Keep it as **one contiguous block at the end of the file**, so an upstream sync
  conflicts on, at most, those lines.
- Jekyll 3 (which `github-pages` pins) **replaces** its default exclude list with yours.
  That is why `Gemfile`, `Gemfile.lock`, `vendor/` and the Nix files are listed too.
  If you remove an entry because "Jekyll ignores that anyway", it won't.
- Nobody has run a Jekyll build against this block. There is no Ruby on the machine that
  wrote it. See the README handover.

## Language wiring is spread across four files

`langs:` in `_config.yml`, `_includes/sqlstyle.guide.<code>.md`, `<dir>/index.md` and
the directory name. `static/scripts.js` builds the menu URL with `toLowerCase()`, so the
directory is always the lower-case of the code (`pt-BR` lives in `pt-br/`).
`_includes/layout_partials/languages.html` lists **every page with a `lang` front-matter
key** in the language menu, so a stray `lang:` anywhere puts a phantom language on the site.

```powershell
reference\_harness\Test-LanguageWiring.ps1   # must exit 0
```

## `ga_code` and `CNAME` are upstream's

`_config.yml` carries upstream's Google Analytics id and `CNAME` names `www.sqlstyle.guide`.
If the fork is ever published with GitHub Pages, both must change first, or the fork
claims upstream's domain and reports into upstream's analytics.
