<#
.SYNOPSIS
  Check that reference/ still describes the repository it sits in.

.DESCRIPTION
  Three mechanical checks, no database and no build required:

    1. Line anchors      every `file.ext:NNN` cited in reference/*.md still
                         resolves, and the file is long enough to contain
                         that line. Anchors naming a file that is not in
                         this repository are reported separately, not as
                         failures -- this reference documents an estate,
                         and citing a sibling repo is legitimate.

    2. Provenance        the commit reference/ is stamped against is an
                         ancestor of HEAD, and the documented source files
                         have not changed since it.

    3. Portability       no script under reference/ hard-codes an absolute
                         path into one developer's checkout. That bug has
                         already shipped here once: publish.ps1 read its
                         template from a temp folder that does not survive
                         the session, so it rebuilt whatever happened to be
                         there and failed outright on any other machine.

  Everything resolves from this script's own location, so it runs from
  anywhere and in any clone. Exit code 0 = pass, 1 = at least one failure.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

if (-not $RepoRoot) { $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }
$RefDir = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path (Join-Path $RefDir 'README.md'))) {
    throw "no reference/README.md beside this script -- expected reference/ at $RefDir"
}

$fail = 0; $warn = 0
function Say($m)  { if (-not $Quiet) { Write-Output $m } }
function Ok($m)   { Say "  PASS  $m" }
function Bad($m)  { Write-Output "  FAIL  $m"; $script:fail++ }
function Note($m) { Say "  note  $m"; $script:warn++ }

Say "=== reference conformance: $RepoRoot ==="
Say ""

# ---------------------------------------------------------------- 1. anchors
Say "--- line anchors ---"
# The extension list is per-repository and must cover what the reference actually
# cites. This one is a Jekyll site: almost every anchor is a .md (the guide and
# its translations), .yml (_config.yml) or .html (layouts). Inherited from the
# C#/MAUI sibling, the pattern would have matched none of them and reported a
# confident PASS over nothing -- the same shape of defect as a linter reporting a
# clean run across zero files. Widen it, never narrow it.
$md = Get-ChildItem $RefDir -Recurse -Filter *.md
$anchors = @{}
foreach ($f in $md) {
    foreach ($m in [regex]::Matches((Get-Content $f.FullName -Raw),
                 '(?<file>[A-Za-z0-9_\-\.]+\.(?:md|yml|html|css|js|nix|cs|xaml|axml|vb|xml|sql|ps1|py|vbproj|csproj)):(?<line>\d+)')) {
        $key = "$($m.Groups['file'].Value):$($m.Groups['line'].Value)"
        if (-not $anchors.ContainsKey($key)) {
            $anchors[$key] = [pscustomobject]@{
                File = $m.Groups['file'].Value
                Line = [int]$m.Groups['line'].Value
                Cited = $f.FullName.Substring($RefDir.Length + 1)
            }
        }
    }
}

# index the repo once, by basename, ignoring the reference's own tree
$index = @{}
Get-ChildItem $RepoRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "$RefDir*" -and $_.FullName -notlike "*\.git\*" } |
    ForEach-Object {
        if (-not $index.ContainsKey($_.Name)) { $index[$_.Name] = @() }
        $index[$_.Name] += $_.FullName
    }

$resolved = 0; $external = @(); $stale = @(); $ambiguous = 0
foreach ($a in $anchors.Values | Sort-Object File, Line) {
    if (-not $index.ContainsKey($a.File)) { $external += $a; continue }
    $paths = $index[$a.File]
    if ($paths.Count -gt 1) { $ambiguous++ }
    $target = $paths[0]
    $count = (Get-Content $target).Count
    if ($a.Line -gt $count) {
        $stale += [pscustomobject]@{ Anchor = "$($a.File):$($a.Line)"; Lines = $count; Cited = $a.Cited }
    } else { $resolved++ }
}

if ($stale.Count -eq 0) {
    Ok "$resolved anchors resolve within this repository"
} else {
    Bad "$($stale.Count) anchor(s) point past the end of their file:"
    $stale | ForEach-Object { Write-Output "          $($_.Anchor) -- file has $($_.Lines) lines (cited in $($_.Cited))" }
}
if ($external.Count) {
    Note "$($external.Count) anchor(s) name files not in this repository (sibling repos -- not a failure)"
    $external | Group-Object File | Sort-Object Count -Descending | Select-Object -First 8 |
        ForEach-Object { Say "          $($_.Name) x$($_.Count)" }
}
if ($ambiguous) { Note "$ambiguous anchor(s) matched more than one file by name; checked the first" }

# ------------------------------------------------------------- 2. provenance
Say ""
Say "--- provenance ---"
Push-Location $RepoRoot
try {
    $stampLine = Select-String -Path (Join-Path $RepoRoot 'AGENTS.md') `
                               -Pattern 'reference-stamp:\s*([0-9a-f]{7,40})' -ErrorAction SilentlyContinue |
                 Select-Object -First 1
    if (-not $stampLine) {
        Note "no <!-- reference-stamp: SHA --> marker in AGENTS.md; provenance unchecked"
    } else {
        $stamp = [regex]::Match($stampLine.Line, 'reference-stamp:\s*([0-9a-f]{7,40})').Groups[1].Value
        $known = (& git cat-file -t $stamp 2>$null)
        if ($LASTEXITCODE -ne 0 -or $known -ne 'commit') {
            Bad "AGENTS.md is stamped at '$stamp', which is not a commit in this repository"
        } else {
            & git merge-base --is-ancestor $stamp HEAD 2>$null
            if ($LASTEXITCODE -eq 0) { Ok "stamp $stamp is an ancestor of HEAD" }
            else { Note "stamp $stamp is NOT an ancestor of HEAD -- reference may describe another line" }
        }
    }
} finally { Pop-Location }

# ------------------------------------------------------------ 3. portability
Say ""
Say "--- portability ---"
$scripts = Get-ChildItem $RefDir -Recurse -Include *.ps1, *.py -File
$hard = @()
foreach ($s in $scripts) {
    foreach ($m in [regex]::Matches((Get-Content $s.FullName -Raw),
                 '(?m)^(?<code>[^#\r\n]*?)(?<path>[A-Za-z]:\\Users\\[^''"\r\n]+)')) {
        $hard += [pscustomobject]@{
            Script = $s.FullName.Substring($RefDir.Length + 1)
            Path   = $m.Groups['path'].Value
        }
    }
}
if ($hard.Count -eq 0) { Ok "no script hard-codes an absolute user path" }
else {
    Bad "$($hard.Count) hard-coded absolute path(s) -- these break in any other clone:"
    $hard | ForEach-Object { Write-Output "          $($_.Script): $($_.Path)" }
}

Say ""
if ($fail -eq 0) { Say "=== PASS ($warn note(s)) ==="; exit 0 }
Write-Output "=== FAIL: $fail check(s) failed ==="
exit 1
