# Findings

Ranked by consequence × likelihood. Ids are stable: never renumber.
Every finding is **claim → evidence → consequence → fix**.

| Id | Finding | Severity | Confidence |
|---|---|---|---|
| F-01 | The fork lagged upstream by 27 commits for five years | Medium | High |
| F-02 | Publishing the fork as-is would claim upstream's domain and analytics | Medium | High |
| F-03 | Jekyll would publish the agent files and run Liquid in `reference/` | Medium | Medium |
| F-04 | Four translations are missing a section; Italian is missing two | Low | High |
| F-05 | Seven branches are inherited upstream debris | Low | High |

---

## F-01 — The fork lagged upstream by 27 commits for five years

**Claim.** Until 2026-10-05 the fork's default branch, `gh-pages`, sat at `44f5e91`
(2021-03-10). Upstream had moved on 27 commits to `70b612f` (2026-03-17). Those commits
add eight translations (Arabic, French, Korean, Polish, Spanish, Turkish, Ukrainian,
Vietnamese; the fork had seven), plus a documented join exception and an ISO-8601 date
fix in the English guide.

**Evidence.**
```bash
git rev-list --count 44f5e91..upstream/gh-pages      # 27
git rev-list --count upstream/gh-pages..44f5e91      # 0 -- the fork had nothing of its own
```

**Consequence.** Anyone reading the fork read a 2021 guide. This mattered little only
because the estate cites the public site (`https://www.sqlstyle.guide/`), not the fork
(see [03-estate](03-estate/01-translution-usage.md)).

**Fix (done).** `main` was created from `upstream/gh-pages` as a pure fast-forward and
made the default branch. A fork that holds no content changes should keep syncing. The
procedure is in [01-fork-and-upstream.md](01-repository/01-fork-and-upstream.md).

---

## F-02 — Publishing the fork as-is would claim upstream's domain and analytics

**Claim.** `CNAME` names `www.sqlstyle.guide`. `_config.yml:5` sets upstream's Google
Analytics id, and `_config.yml:7` sets `url: https://www.sqlstyle.guide`.

**Consequence.** If GitHub Pages were switched on for this fork, it would try to serve
upstream's custom domain, and visits would be reported into Simon Holywell's analytics
property. Pages is **off** today (`gh api repos/TransLution/sqlstyle.guide/pages` → 404),
so nothing is happening yet.

**Fix.** Do not enable Pages on this fork unless `CNAME`, `url` and `ga_code` are changed
first. That is a content divergence from upstream; record it in `AGENTS.md` if it is ever made.

---

## F-03 — Jekyll would publish the agent files and run Liquid in `reference/`

**Claim.** The `github-pages` gem (`Gemfile`) enables jekyll-optional-front-matter by
default, so `.md` files with no front matter are rendered as pages and Liquid inside
them is executed. That includes every page in `reference/`, `AGENTS.md`, `CLAUDE.md` and
`CHANGELOG.md`.

**Consequence.** The agent contract and this reference would appear on the public site,
and any page quoting an include tag would pull the whole guide in, or break the build.

**Fix (done, unverified).** `_config.yml` now ends with an `exclude:` block (from
`_config.yml:84`) listing those paths. **Confidence is Medium** because no Jekyll build has
been run against it: the machine this was written on has no Ruby. The pages here also
avoid literal Liquid braces as a second line of defence. To clear this, run
`bundle exec jekyll build` and confirm `_site/` contains no `reference/`, `AGENTS`,
`CLAUDE` or `CHANGELOG` output.

---

## F-04 — Four translations are missing a section; Italian is missing two

**Claim.** The English guide has 6 `##` and 18 `###` headings. German, Japanese,
Portuguese (BR) and Russian have 17 `###`, with no counterpart to *Column data types*.
Italian has 5 `##` and 17 `###`, with no *Overview* heading and no *Preferred formalisms*
section. See [02-translations.md](02-site/02-translations.md) for the full table.

**Consequence.** A reader of those languages gets a shorter guide than an English reader,
with nothing on the page to say so.

**Fix.** Upstream's to make (`AGENTS.md`, invariant 1). Raise it with
`treffynnon/sqlstyle.guide` if TransLution relies on a translation; today it relies on none.

---

## F-05 — Seven branches are inherited upstream debris

**Claim.** `master` (2016), `nl-translation` (2017), `patch-1` to `patch-4` (2017) and
`robertopauletto-gh-pages` (2020) were copied when the repository was forked.
`robertopauletto-gh-pages` is fully contained in `main`. The others carry 1–29 commits
that upstream never merged.

**Consequence.** None. They are inert. They are listed so nobody mistakes them for
TransLution work.

**Fix.** Deliberately left in place (decision 2026-10-05). Delete only if someone confirms
nothing on them is wanted.
