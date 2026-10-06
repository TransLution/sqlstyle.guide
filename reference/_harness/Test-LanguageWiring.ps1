<#
.SYNOPSIS
  Check that every language the site advertises is wired up end to end.

.DESCRIPTION
  A translation is four things that must agree, and nothing in Jekyll checks
  that they do -- a missing piece produces a broken link or a silently empty
  page, not a build error:

    1. _config.yml        langs.<code> with a local name and an English name
    2. _includes/         sqlstyle.guide.<code>.md  (English: sqlstyle.guide.md)
    3. <dir>/index.md     front matter `lang: <code>` and `{% include` of (2)
    4. the directory      <dir> == lower(<code>), because static/scripts.js builds
                          the language-menu URL as `selected.toLowerCase()`.
                          pt-BR lives in pt-br/, zh-TW in zh-tw/.

  It also checks the reverse: no include, and no page carrying `lang:`, that
  _config.yml does not know about -- layout_partials/languages.html lists every
  page with a `lang` in the menu, so a stray one shows up on the live site.

  Read-only. Resolves everything from $PSScriptRoot. Exit 0 = pass, 1 = fail.

.EXAMPLE
  reference\_harness\Test-LanguageWiring.ps1
#>
[CmdletBinding()]
param([string]$RepoRoot)

$ErrorActionPreference = 'Stop'
if (-not $RepoRoot) { $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }

$fail = 0
function Bad($m) { Write-Output "  FAIL  $m"; $script:fail++ }

# --- 1. language codes from _config.yml -------------------------------------
# Parsed by indentation rather than with a YAML library, so this runs on a bare
# Windows PowerShell 5.1. The block is `langs:` then two-space keys `  <code>:`.
$cfg = Get-Content (Join-Path $RepoRoot '_config.yml') -Encoding UTF8
$codes = @(); $inLangs = $false
foreach ($line in $cfg) {
    if ($line -match '^langs:\s*$') { $inLangs = $true; continue }
    if ($inLangs -and $line -match '^\S') { $inLangs = $false }
    if ($inLangs -and $line -match '^  (?<code>[A-Za-z\-]+):\s*$') { $codes += $Matches['code'] }
}
if ($codes.Count -eq 0) { Bad "_config.yml: no langs block found"; exit 1 }
Write-Output "=== language wiring: $($codes.Count) languages in _config.yml ==="

# --- 2-4. each code is wired end to end --------------------------------------
foreach ($code in $codes) {
    if ($code -eq 'en') {
        $inc = 'sqlstyle.guide.md'; $page = Join-Path $RepoRoot 'index.md'
    } else {
        $inc = "sqlstyle.guide.$code.md"; $page = Join-Path $RepoRoot (Join-Path $code.ToLower() 'index.md')
    }
    if (-not (Test-Path (Join-Path $RepoRoot "_includes\$inc"))) { Bad "$code -- _includes/$inc missing"; continue }
    if (-not (Test-Path $page)) { Bad "$code -- $($code.ToLower())/index.md missing (dir must be lower-case of the code)"; continue }
    # Test-Path is case-insensitive on NTFS, so `pt-BR/` would satisfy it here and
    # 404 on the case-sensitive Linux host that GitHub Pages builds on. Compare the
    # directory's real name, case-sensitively.
    if ($code -ne 'en') {
        $real = (Get-ChildItem $RepoRoot -Directory | Where-Object { $_.Name -eq $code.ToLower() } | Select-Object -First 1).Name
        if ($real -cne $code.ToLower()) { Bad "$code -- directory is '$real', must be '$($code.ToLower())' (scripts.js lower-cases the URL)" }
    }
    $raw = Get-Content $page -Raw -Encoding UTF8
    if ($raw -notmatch "(?m)^lang:\s*$([regex]::Escape($code))\s*$") { Bad "$code -- $page front matter lang: is not '$code'" }
    if ($raw -notmatch [regex]::Escape("include $inc")) { Bad "$code -- $page does not include $inc" }
}

# --- reverse: nothing the config does not know about --------------------------
Get-ChildItem (Join-Path $RepoRoot '_includes') -Filter 'sqlstyle.guide*.md' | ForEach-Object {
    $c = if ($_.Name -eq 'sqlstyle.guide.md') { 'en' } else { $_.Name -replace '^sqlstyle\.guide\.(.+)\.md$', '$1' }
    if ($codes -cnotcontains $c) { Bad "_includes/$($_.Name) has no langs.$c entry in _config.yml" }
}
Get-ChildItem $RepoRoot -Recurse -Filter '*.md' -File |
    Where-Object { $_.FullName -notmatch '\\(reference|_includes|\.git|_site|\.claude)\\' } |
    ForEach-Object {
        $m = Select-String -Path $_.FullName -Pattern '^lang:\s*(\S+)' | Select-Object -First 1
        if ($m) {
            $c = $m.Matches[0].Groups[1].Value
            # Name by parent folder, not by trimming $RepoRoot: an 8.3 short root
            # (C:\Users\GRANTR~1\...) and Get-ChildItem's long names differ in length.
            if ($codes -cnotcontains $c) { Bad "$($_.Directory.Name)/$($_.Name) declares lang: $c, unknown to _config.yml" }
        }
    }

if ($fail -eq 0) { Write-Output "  PASS  every language has config, include, page and lower-case directory"; exit 0 }
Write-Output "=== FAIL: $fail problem(s) ==="
exit 1
