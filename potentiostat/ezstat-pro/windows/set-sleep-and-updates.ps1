# Turns off sleep and Windows Update on the EZstat PC for good (#231, runbook
# step 2.7). If the PC sleeps, Remote Desktop stops answering; if it restarts
# for an update mid-run, or freezes, the cell can be left on (manual p. 26).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File set-sleep-and-updates.ps1          report only
#   powershell -NoProfile -ExecutionPolicy Bypass -File set-sleep-and-updates.ps1 -Apply   change, then report
#
# -Apply copies this script to Downloads\ezstat-software, runs that copy as
# administrator (one UAC prompt: Windows PowerShell, Microsoft Windows), and
# waits for it. Its log goes to Downloads\ezstat-software\set-sleep-and-updates.log
# and is printed here afterwards. What it changes:
#
#   Sleep, in every power plan, plugged in and on battery:
#     sleep after: never; hibernate after: never; USB selective suspend: off
#     (so Windows doesn't power down the EZstat's USB board while idle)
#     and hibernation off altogether (powercfg -h off)
#   Windows Update:
#     policy "Configure Automatic Updates" disabled (NoAutoUpdate = 1),
#     no automatic restart with someone logged on, Control Panel setting
#     "Never check for updates" (AUOptions = 1), and the Windows Update
#     service (wuauserv) stopped and disabled.
#
# To undo Windows Update, e.g. to install a .msu by hand (wusa needs the
# service): sc config wuauserv start= demand, then delete the two policy
# values under HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU.
#
# Written for PowerShell 2.0, which Windows 7 ships with.

param(
    [switch]$Apply,
    [switch]$Elevated,
    [string]$Log
)

$base = Join-Path $env:USERPROFILE 'Downloads\ezstat-software'
$sleepAfter = '29f6c1db-86da-48c5-9fdb-f2b67b1f44da'      # STANDBYIDLE
$hibernateAfter = '9d7815a6-7ee4-497e-8888-515a05f02364'  # HIBERNATEIDLE
$usbSub = '2a737441-1930-4402-8d77-b2bebba308a3'
$usbSel = '48e6b7a6-50f5-4782-a5d4-53bb8f07e226'

function Out-Log([string]$msg) {
    $line = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') + ' ' + $msg
    if ($Log) { try { [IO.File]::AppendAllText($Log, $line + "`r`n") } catch { } }
    Write-Host $line
}

function Run([string]$exe, [string[]]$argv) {
    $out = & $exe $argv 2>&1 | Out-String
    Out-Log ("{0} {1} -> exit {2}: {3}" -f $exe, ($argv -join ' '), $LASTEXITCODE, $out.Trim())
}

function Get-Schemes {
    powercfg -list | ForEach-Object {
        if ($_ -match 'GUID: ([0-9a-fA-F-]{36})\s+\((.*)\)(\s*\*)?') {
            New-Object PSObject -Property @{ Guid = $matches[1]; Name = $matches[2]; Active = [bool]$matches[3] }
        }
    }
}

# Windows 7's powercfg -q takes a plan and a subgroup but not a setting ("Invalid
# Parameters"), so read the subgroup and find the setting's AC and DC values in it.
function Get-Setting([string]$scheme, [string]$sub, [string]$setting) {
    $q = powercfg -q $scheme $sub | Out-String
    $pat = '(?s)Power Setting GUID: ' + $setting + '.*?Current AC Power Setting Index:\s*0x([0-9a-fA-F]+)\s*Current DC Power Setting Index:\s*0x([0-9a-fA-F]+)'
    if ($q -match $pat) {
        'AC {0} / DC {1}' -f [Convert]::ToInt64($matches[1], 16), [Convert]::ToInt64($matches[2], 16)
    } else {
        'not found'
    }
}

function Get-Reg([string]$key, [string]$name) {
    try { (Get-ItemProperty -Path $key -Name $name -ErrorAction Stop).$name } catch { '(not set)' }
}

function Report {
    Out-Log '=== sleep (seconds; 0 = never)'
    foreach ($s in Get-Schemes) {
        $tag = ''
        if ($s.Active) { $tag = ' [active]' }
        Out-Log ("{0}{1}: sleep after {2}; hibernate after {3}; USB selective suspend {4} (0 = off)" -f `
            $s.Name, $tag, (Get-Setting $s.Guid SUB_SLEEP $sleepAfter), `
            (Get-Setting $s.Guid SUB_SLEEP $hibernateAfter), (Get-Setting $s.Guid $usbSub $usbSel))
    }
    Out-Log ('hibernation enabled: ' + (Get-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\Power' 'HibernateEnabled'))
    $bat = @(Get-WmiObject Win32_Battery -ErrorAction SilentlyContinue)
    Out-Log ('batteries: ' + $bat.Count + ' (0 = a desktop, so no lid setting to change)')
    Out-Log '--- powercfg -a'
    Out-Log ((powercfg -a | Out-String).Trim())

    Out-Log '=== Windows Update'
    $au = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
    $cpl = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update'
    Out-Log ('policy NoAutoUpdate: ' + (Get-Reg $au 'NoAutoUpdate'))
    Out-Log ('policy AUOptions: ' + (Get-Reg $au 'AUOptions'))
    Out-Log ('policy NoAutoRebootWithLoggedOnUsers: ' + (Get-Reg $au 'NoAutoRebootWithLoggedOnUsers'))
    Out-Log ('Control Panel AUOptions (1 never, 2 notify, 3 download, 4 install): ' + (Get-Reg $cpl 'AUOptions'))
    Out-Log ('last successful install: ' + (Get-Reg "$cpl\Results\Install" 'LastSuccessTime'))
    Out-Log ('last successful check: ' + (Get-Reg "$cpl\Results\Detect" 'LastSuccessTime'))
    $svc = Get-WmiObject Win32_Service -Filter "Name='wuauserv'"
    Out-Log ('service wuauserv: start mode ' + $svc.StartMode + ', state ' + $svc.State)
    Out-Log ('restart pending for updates: ' + (Test-Path "$cpl\RebootRequired"))
    Out-Log ('restart pending for components: ' + (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'))
    $dl = @(Get-ChildItem 'C:\Windows\SoftwareDistribution\Download' -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer })
    $mb = 0
    if ($dl.Count -gt 0) { $mb = [math]::Round((($dl | Measure-Object Length -Sum).Sum) / 1MB, 1) }
    Out-Log ('downloaded updates waiting: ' + $dl.Count + ' files, ' + $mb + ' MB')
}

if ($Elevated) {
    Out-Log 'running as administrator; before:'
    Report
    Out-Log '=== changing sleep'
    foreach ($s in Get-Schemes) {
        foreach ($mode in '-setacvalueindex', '-setdcvalueindex') {
            Run 'powercfg' @($mode, $s.Guid, 'SUB_SLEEP', 'STANDBYIDLE', '0')
            Run 'powercfg' @($mode, $s.Guid, 'SUB_SLEEP', 'HIBERNATEIDLE', '0')
            Run 'powercfg' @($mode, $s.Guid, $usbSub, $usbSel, '0')
        }
        if ($s.Active) { Run 'powercfg' @('-setactive', $s.Guid) }
    }
    Run 'powercfg' @('-h', 'off')
    Out-Log '=== changing Windows Update'
    $pol = 'HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
    Run 'reg' @('add', $pol, '/v', 'NoAutoUpdate', '/t', 'REG_DWORD', '/d', '1', '/f')
    Run 'reg' @('add', $pol, '/v', 'NoAutoRebootWithLoggedOnUsers', '/t', 'REG_DWORD', '/d', '1', '/f')
    Run 'reg' @('add', 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update', '/v', 'AUOptions', '/t', 'REG_DWORD', '/d', '1', '/f')
    Run 'sc.exe' @('stop', 'wuauserv')
    Run 'sc.exe' @('config', 'wuauserv', 'start=', 'disabled')
    Out-Log 'after:'
    Report
    Out-Log 'done'
    exit 0
}

if ($Apply) {
    if (-not (Test-Path $base)) { New-Item -ItemType Directory -Path $base | Out-Null }
    $local = Join-Path $base 'set-sleep-and-updates.ps1'
    $logFile = Join-Path $base 'set-sleep-and-updates.log'
    if ($MyInvocation.MyCommand.Path -ne $local) { Copy-Item $MyInvocation.MyCommand.Path $local -Force }
    if (Test-Path $logFile) { Remove-Item $logFile -Force }
    Write-Host 'approve the UAC prompt (Windows PowerShell, Microsoft Windows)'
    $argList = '-NoProfile -ExecutionPolicy Bypass -File "' + $local + '" -Elevated -Log "' + $logFile + '"'
    $p = Start-Process -FilePath powershell.exe -ArgumentList $argList -Verb RunAs -PassThru
    $p.WaitForExit()
    if (Test-Path $logFile) { Get-Content $logFile } else { Write-Host 'FAILED: no log; was the UAC prompt declined?' }
    exit 0
}

Report
