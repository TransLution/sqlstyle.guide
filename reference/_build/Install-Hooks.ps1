<#
.SYNOPSIS
  Point this clone's git hooks at the tracked hooks in reference/_build/hooks.

.DESCRIPTION
  .git/hooks is not version-controlled, so a hook committed to the repository
  does nothing until each clone opts in. This sets core.hooksPath, which is
  local config -- it travels with the clone, not with the branch, and every
  developer runs this once.

  core.hooksPath REPLACES the whole hooks directory rather than adding to it.
  If .git/hooks already holds hooks you rely on, this reports them and stops
  rather than quietly disabling them.

.PARAMETER Uninstall
  Unset core.hooksPath and go back to .git/hooks.

.EXAMPLE
  reference\_build\Install-Hooks.ps1
  reference\_build\Install-Hooks.ps1 -Uninstall
#>
[CmdletBinding()]
param([switch]$Uninstall, [switch]$Force)

$ErrorActionPreference = 'Stop'
$repo = (& git rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0) { throw "not inside a git repository" }
$repo = $repo -replace '/', '\'

if ($Uninstall) {
    & git -C $repo config --unset core.hooksPath 2>$null | Out-Null
    Write-Output "core.hooksPath unset -- this clone is back to .git\hooks"
    exit 0
}

$hooks = Join-Path $repo 'reference\_build\hooks'
if (-not (Test-Path (Join-Path $hooks 'pre-commit'))) {
    throw "no pre-commit hook at $hooks -- is reference/ present on this branch?"
}

# Do not silently disable hooks someone already depends on.
$existing = Join-Path $repo '.git\hooks'
if (Test-Path $existing) {
    $live = Get-ChildItem $existing -File | Where-Object { $_.Name -notlike '*.sample' }
    if ($live -and -not $Force) {
        Write-Output "This clone already has active hooks in .git\hooks:"
        $live | ForEach-Object { Write-Output "    $($_.Name)" }
        Write-Output ""
        Write-Output "core.hooksPath replaces the directory, so setting it would disable them."
        Write-Output "Move them into reference\_build\hooks, or re-run with -Force to override."
        exit 1
    }
}

& git -C $repo config core.hooksPath 'reference/_build/hooks'
$set = (& git -C $repo config --get core.hooksPath)
if ($set -ne 'reference/_build/hooks') { throw "failed to set core.hooksPath (got '$set')" }

Write-Output "core.hooksPath = $set"
Write-Output ""
Write-Output "The pre-commit hook will now:"
Write-Output "  - regenerate navigator.html when reference/*.md changes, and stage it"
Write-Output "  - name the reference pages that cite any source file you change"
Write-Output "  - refuse the commit only if Verify-Reference.ps1 finds a real defect"
Write-Output ""
Write-Output "Skip once with: git commit --no-verify"
Write-Output "Disable with:   git config translution.referencehook false"
