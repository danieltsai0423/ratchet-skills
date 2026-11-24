# ratchet-skills installer for Windows PowerShell 5.1 and PowerShell 7+ (Windows, macOS, Linux).
# macOS / Linux shell users can also run install.sh.
# Keep this file ASCII-only: Windows PowerShell 5.1 misreads UTF-8 without a BOM.
[CmdletBinding()]
param(
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Skill,

    [ValidateSet('claude', 'codex', 'devin', 'all')]
    [string]$Agent = 'all',

    [ValidateSet('project', 'user')]
    [string]$Scope = 'user',

    [string]$Project,

    [switch]$Force,

    [switch]$List
)

$ErrorActionPreference = 'Stop'
$src = Join-Path $PSScriptRoot 'skills'
if (-not (Test-Path -LiteralPath $src -PathType Container)) {
    throw "Skills folder not found: $src"
}

$available = @(Get-ChildItem -LiteralPath $src -Directory | Sort-Object Name | ForEach-Object { $_.Name })
if ($List) {
    $available
    exit 0
}

if ($Project) { $Scope = 'project' }
if ($Scope -eq 'user') {
    $base = [Environment]::GetFolderPath('UserProfile')
    if (-not $base) { $base = $HOME }
} else {
    if (-not $Project) { $Project = '.' }
    if (-not (Test-Path -LiteralPath $Project -PathType Container)) {
        throw "Project folder not found: $Project"
    }
    $base = (Resolve-Path -LiteralPath $Project).Path
}

$claudeDir = Join-Path (Join-Path $base '.claude') 'skills'
$agentsDir = Join-Path (Join-Path $base '.agents') 'skills'
switch ($Agent) {
    'claude' { $dests = @($claudeDir) }
    'codex'  { $dests = @($agentsDir) }
    'devin'  { $dests = @($agentsDir) }
    'all'    { $dests = @($claudeDir, $agentsDir) }
}

if (-not $Skill -or $Skill.Count -eq 0) { $Skill = $available }
foreach ($n in $Skill) {
    if (-not (Test-Path -LiteralPath (Join-Path (Join-Path $src $n) 'SKILL.md') -PathType Leaf)) {
        throw "Unknown skill: $n (try -List)"
    }
}

$skipped = $false
foreach ($dest in $dests) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    foreach ($n in $Skill) {
        $target = Join-Path $dest $n
        if (Test-Path -LiteralPath $target) {
            if ($Force) {
                Remove-Item -LiteralPath $target -Recurse -Force
            } else {
                Write-Output "skip     $target (exists; use -Force to replace)"
                $skipped = $true
                continue
            }
        }
        Copy-Item -LiteralPath (Join-Path $src $n) -Destination $target -Recurse
        Write-Output "install  $target"
    }
}

# Always set an explicit exit code; otherwise $LASTEXITCODE keeps a stale value in the caller.
if ($skipped) { exit 1 }
exit 0
