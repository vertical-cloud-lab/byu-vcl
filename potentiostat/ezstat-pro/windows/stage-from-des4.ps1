# Copies an installer folder that des4 shares over Remote Desktop onto this PC,
# and checks every file against des4's SHA-256 manifest (#231). It copies and
# checks only; it installs nothing.
#
# des4 shares a folder as \\tsclient\ez (FreeRDP /drive:ez,<folder>), holding
# <Name>\ (the unzipped installer) and <Name>.sha256 (sha256sum output, made on
# des4 after checking the zip's own hash). From Win+R or a Command Prompt:
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File \\tsclient\ez\stage-from-des4.ps1
#
# The copy goes to Downloads\ezstat-software\<Name>. Progress and the result
# are written to <Name>.stage.log, both in \\tsclient\ez (so des4 can read
# them) and next to the copy. Exit code 0 only if every file is present and
# matches.
#
# Written for PowerShell 2.0, which Windows 7 ships with.

param(
    [string]$Name = 'NIDAQ970f0',
    [string]$Share = '\\tsclient\ez'
)

$ErrorActionPreference = 'Stop'
$base = Join-Path $env:USERPROFILE 'Downloads\ezstat-software'
$src = Join-Path $Share $Name
$dst = Join-Path $base $Name
$manifest = Join-Path $Share ($Name + '.sha256')
$logs = @((Join-Path $Share ($Name + '.stage.log')), (Join-Path $base ($Name + '.stage.log')))
$rclog = Join-Path $Share ($Name + '.robocopy.log')
[void][IO.Directory]::CreateDirectory($base)

# Not Add-Content: on \\tsclient it silently writes nothing (2026-10-22).
function Log([string]$msg) {
    $line = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') + ' ' + $msg
    foreach ($l in $logs) { try { [IO.File]::AppendAllText($l, $line + "`r`n") } catch { } }
    Write-Host $line
}

Log "copy $src -> Downloads\ezstat-software\$Name"
$t0 = Get-Date
# /E: subfolders, /NP: no percentages in the log, /NDL: no folder lines, so the
# log has one line per file copied and des4 can count them.
& robocopy.exe $src $dst /E /R:2 /W:5 /NP /NDL "/LOG:$rclog" | Out-Null
$rc = $LASTEXITCODE
$secs = [int]((Get-Date) - $t0).TotalSeconds
Log "robocopy exit $rc after $secs s (0-3 = OK, 8 or more = failed)"
if ($rc -ge 8) { Log 'FAILED: copy'; exit 1 }

Log 'checking every file against the manifest'
$sha = [System.Security.Cryptography.SHA256]::Create()
$ok = 0; $bad = 0; $missing = 0; $bytes = 0
$listed = @{}
foreach ($line in [IO.File]::ReadAllLines($manifest)) {
    if ($line -notmatch '^([0-9a-f]{64}) [ *](.+)$') { continue }
    $want = $matches[1]
    $rel = $matches[2] -replace '/', '\'
    $listed[$rel.ToLower()] = $true
    $p = Join-Path $dst $rel
    if (-not [IO.File]::Exists($p)) { $missing++; Log "MISSING $rel"; continue }
    $fs = [IO.File]::OpenRead($p)
    try {
        $hash = ($sha.ComputeHash($fs) | ForEach-Object { $_.ToString('x2') }) -join ''
        $bytes += $fs.Length
    } finally { $fs.Close() }
    if ($hash -eq $want) { $ok++ } else { $bad++; Log "MISMATCH $rel" }
}
$extra = 0
foreach ($f in Get-ChildItem -LiteralPath $dst -Recurse -Force | Where-Object { -not $_.PSIsContainer }) {
    $rel = $f.FullName.Substring($dst.Length + 1)
    if (-not $listed.ContainsKey($rel.ToLower())) { $extra++; Log "NOT IN MANIFEST $rel" }
}
Log "files: $ok match, $bad differ, $missing missing, $extra extra; $bytes bytes checked"
if ($ok -gt 0 -and $bad -eq 0 -and $missing -eq 0 -and $extra -eq 0) {
    Log "OK: $dst"
    exit 0
}
Log 'FAILED: see the lines above'
exit 1
