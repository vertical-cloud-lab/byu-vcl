# Runs the NI-DAQmx installer that stage-from-des4.ps1 copied onto this PC,
# unattended and with its default features, and waits for it to finish (#231).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File \\tsclient\ez\install-nidaqmx.ps1
#
# Windows asks for administrator approval (UAC) once. The switches are the ones
# NI-DAQmx 9.7's installer documents in its own help text:
#   /qb                  progress bar only, no questions
#   /AcceptLicenses yes  accept NI's licence agreements
#   /r:n                 don't restart; restart afterwards, when it suits
# It doesn't restart the PC. Progress and the exit code go to
# \\tsclient\ez\<Name>.install.log, and to the same file next to the installer
# in Downloads\ezstat-software in case the Remote Desktop share has gone.
#
# Written for PowerShell 2.0, which Windows 7 ships with.

param(
    [string]$Name = 'NIDAQ970f0',
    [string]$Share = '\\tsclient\ez'
)

$ErrorActionPreference = 'Stop'
$base = Join-Path $env:USERPROFILE 'Downloads\ezstat-software'
$dir = Join-Path $base $Name
$setup = Join-Path $dir 'setup.exe'
$logs = @((Join-Path $Share ($Name + '.install.log')), (Join-Path $base ($Name + '.install.log')))

# Not Add-Content: on \\tsclient it silently writes nothing (2026-10-22).
function Log([string]$msg) {
    $line = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') + ' ' + $msg
    foreach ($l in $logs) { try { [IO.File]::AppendAllText($l, $line + "`r`n") } catch { } }
    Write-Host $line
}

if (-not [IO.File]::Exists($setup)) {
    Log "FAILED: $setup not found; run stage-from-des4.ps1 first"
    exit 1
}
$switches = '/qb /AcceptLicenses yes /r:n'
Log "starting $Name\setup.exe $switches (approve the UAC prompt)"
$t0 = Get-Date
$p = Start-Process -FilePath $setup -ArgumentList $switches -WorkingDirectory $dir -Verb RunAs -PassThru
$p.WaitForExit()
$code = $p.ExitCode
if ($code -eq $null) { $code = '(not reported)' }   # PowerShell 2.0 with -Verb RunAs
# In case setup.exe hands over to a second copy of itself and exits early.
while (Get-Process -Name setup -ErrorAction SilentlyContinue) {
    if (((Get-Date) - $t0).TotalMinutes -gt 120) { Log 'still running after 120 min; stopped waiting'; break }
    Start-Sleep -Seconds 15
}
$mins = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
Log "setup.exe exit code $code after $mins min"
$k = 'HKLM:\SOFTWARE\Wow6432Node\National Instruments\NI-DAQmx\CurrentVersion'
if (Test-Path $k) {
    $v = (Get-ItemProperty $k).Version
    Log "NI-DAQmx in the registry: $v"
} else {
    Log 'NI-DAQmx not in the registry yet'
}
Log 'done; restart the PC to finish'
