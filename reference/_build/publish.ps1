<#
.SYNOPSIS
  Regenerate reference/navigator.html from the markdown and _data beside it.

.DESCRIPTION
  The estate's repositories all expose the same entry point name -- publish.ps1 --
  so the shared pre-commit hook can call it without knowing which builder a given
  repository uses. EazySetup's builder fills an HTML template from a database
  schema; this repository (a Jekyll site, markdown only) has no schema and uses the
  generic mknav.py, ported from TransLutionScanner,, which
  discovers every .md under reference/ and every .psv under _data/ and needs no
  template at all. Same name, same contract, different engine underneath.

  Everything resolves from $PSScriptRoot. Do not reintroduce an absolute path:
  publish.ps1 in the sibling repository once read its template from a temporary
  scratchpad that did not survive the session, so it rebuilt whatever happened to
  be in that folder and failed outright on any other machine. Verify-Reference.ps1
  fails the build if an absolute user path reappears under reference/.

.EXAMPLE
  reference\_build\publish.ps1
#>
[CmdletBinding()]
param([string]$Title = 'sqlstyle.guide')

$ErrorActionPreference = 'Stop'

$S = $PSScriptRoot                          # reference/_build
$R = Split-Path $PSScriptRoot -Parent       # reference

if (-not (Test-Path (Join-Path $S 'mknav.py'))) {
    throw "no mknav.py beside this script: $S"
}
if (-not (Test-Path (Join-Path $R 'README.md'))) {
    throw "no reference/README.md -- expected reference/ at $R"
}

# Probe each candidate by RUNNING it, rather than trusting Get-Command. Windows
# ships App Execution Aliases for `python` and `python3` that resolve happily,
# report a Source, and then refuse to execute -- "Python was not found; run
# without arguments to install from the Microsoft Store". A presence test picks
# the stub and the build fails (or, in a script less careful about $LASTEXITCODE,
# silently produces nothing). Asking each candidate for its version is the only
# check that distinguishes a real interpreter from the alias.
$py = $null
foreach ($c in 'python', 'python3', 'py') {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    $probe = (& $cmd.Source '--version' 2>&1)
    if ($LASTEXITCODE -eq 0 -and "$probe" -match 'Python 3') { $py = $cmd.Source; break }
}
if (-not $py) {
    throw 'no working python 3 on PATH (tried python, python3, py -- a Microsoft Store alias is not an interpreter)'
}

& $py (Join-Path $S 'mknav.py') $R --title $Title
if ($LASTEXITCODE -ne 0) { throw "mknav.py failed with exit code $LASTEXITCODE" }

$out = Join-Path $R 'navigator.html'
if (-not (Test-Path $out)) { throw "mknav.py reported success but $out does not exist" }
Write-Output ("navigator.html: {0:N0} bytes" -f (Get-Item $out).Length)
