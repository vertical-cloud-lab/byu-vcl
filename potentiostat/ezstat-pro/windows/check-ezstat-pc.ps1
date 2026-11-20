<#
.SYNOPSIS
  Read-only check of a Windows PC for the NuVant EZstat-Pro software stack.

.DESCRIPTION
  Changes nothing on the PC. Prints a short report and copies it to the
  clipboard, so it can be pasted into a comment on the PR.

  It reports: the Windows version, whether this window has admin rights,
  Secure Boot and Memory integrity (both matter for old NI drivers), installed
  NuVant / National Instruments / Watlow software, the LabVIEW Run-Time and
  NI-DAQmx versions, where EZware is installed, any EZware data files
  (*.nuvdt), and any National Instruments USB device that is plugged in.

  Run it from a PowerShell window opened in the folder holding this file:

      powershell -ExecutionPolicy Bypass -File .\check-ezstat-pc.ps1

  Works on Windows PowerShell 2.0 (Windows 7) through 5.1. Searching the disk
  for EZware and data files can take a minute or two.
#>

$ErrorActionPreference = 'SilentlyContinue'
$report = New-Object System.Collections.ArrayList
function Out-Line([string]$s) { [void]$report.Add($s); Write-Host $s }
function Show([object]$v) { if ($null -eq $v -or "$v" -eq '') { 'unknown' } else { "$v" } }

Out-Line '### EZstat PC check'
Out-Line ''
Out-Line ('Run ' + (Get-Date).ToString('yyyy-MM-dd HH:mm') + ' (PC clock)')
Out-Line ''

# --- Windows ---------------------------------------------------------------
$os = Get-WmiObject Win32_OperatingSystem
$cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$release = $cv.DisplayVersion
if (-not $release) { $release = $cv.ReleaseId }
Out-Line ('- Windows: ' + (Show $os.Caption) + ', version ' + (Show $os.Version) +
          ', release ' + (Show $release) + ', ' + (Show $os.OSArchitecture))
Out-Line ('- PowerShell: ' + $PSVersionTable.PSVersion.ToString())

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin = (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
Out-Line ('- This window has admin rights: ' + $isAdmin)

$sb = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\SecureBoot\State').UEFISecureBootEnabled
$hvci = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity').Enabled
Out-Line ('- Secure Boot enabled: ' + (Show $sb) + '; Memory integrity (HVCI) enabled: ' + (Show $hvci) +
          '  (1 = on, 0 = off)')

# --- Installed software ----------------------------------------------------
Out-Line ''
Out-Line '**Installed software matching NuVant / EZware / National Instruments / Watlow:**'
Out-Line ''
$keys = @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
          'HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')
$pattern = 'EZware|NuVant|LabVIEW|NI-DAQ|DAQmx|NI Measurement|Measurement & Automation|NI-VISA|NI-Serial|NI System Configuration|NI-PAL|EZ-ZONE|Watlow'
$apps = Get-ItemProperty $keys | Where-Object { $_.DisplayName -match $pattern } |
        Sort-Object DisplayName, DisplayVersion -Unique
if ($apps) {
    foreach ($a in $apps) {
        $installed = ''
        if ($a.InstallDate) { $installed = ', installed ' + $a.InstallDate }
        Out-Line ('- ' + $a.DisplayName + ' ' + (Show $a.DisplayVersion) + $installed)
    }
} else {
    Out-Line '- none found'
}

# NI keeps its own version keys; on 64-bit Windows they sit under Wow6432Node.
Out-Line ''
foreach ($root in @('HKLM:\SOFTWARE\National Instruments', 'HKLM:\SOFTWARE\Wow6432Node\National Instruments')) {
    $daq = Get-ItemProperty "$root\NI-DAQmx\CurrentVersion"
    if ($daq.Version) { Out-Line ('- NI-DAQmx version (registry): ' + $daq.Version) }
    $rte = Get-ChildItem "$root\LabVIEW Run-Time" | ForEach-Object { $_.PSChildName }
    if ($rte) { Out-Line ('- LabVIEW Run-Time versions (registry): ' + ($rte -join ', ')) }
}

# --- EZware, NI MAX and EZware data files ------------------------------------
Out-Line ''
Out-Line '**Program files and data:**'
Out-Line ''
Write-Host '(searching the disk; this can take a minute or two)'
$programDirs = @($env:ProgramFiles, ${env:ProgramFiles(x86)}) | Where-Object { $_ } | Select-Object -Unique
$exes = foreach ($p in $programDirs) {
    Get-ChildItem -Path $p -Recurse -Include 'EZWare*.exe', 'EZware*.exe', 'NIMax.exe' -ErrorAction SilentlyContinue
}
if ($exes) {
    foreach ($e in ($exes | Sort-Object FullName -Unique)) {
        $ver = $e.VersionInfo.FileVersion
        Out-Line ('- ' + $e.FullName + '  (file version ' + (Show $ver) + ', modified ' +
                  $e.LastWriteTime.ToString('yyyy-MM-dd') + ')')
    }
} else {
    Out-Line '- no EZware*.exe or NIMax.exe under Program Files'
}

$dataRoots = @('C:\Users', 'C:\Documents and Settings') | Where-Object { Test-Path $_ }
$nuvdt = foreach ($r in $dataRoots) {
    Get-ChildItem -Path $r -Recurse -Filter '*.nuvdt' -ErrorAction SilentlyContinue
}
if ($nuvdt) {
    $sorted = $nuvdt | Sort-Object LastWriteTime
    Out-Line ('- ' + @($sorted).Count + ' EZware data files (*.nuvdt). Oldest ' +
              @($sorted)[0].LastWriteTime.ToString('yyyy-MM-dd') + ', newest ' +
              @($sorted)[-1].LastWriteTime.ToString('yyyy-MM-dd') + '. Newest three:')
    foreach ($f in (@($sorted) | Select-Object -Last 3)) { Out-Line ('  - ' + $f.FullName) }
} else {
    Out-Line '- no *.nuvdt files under C:\Users'
}

# --- National Instruments USB devices (vendor ID 3923) -----------------------
Out-Line ''
Out-Line '**National Instruments devices Windows can see now (plug the EZstat in first to include it):**'
Out-Line ''
$devices = Get-WmiObject Win32_PnPEntity | Where-Object {
    $_.DeviceID -like 'USB\VID_3923*' -or $_.Manufacturer -like '*National Instruments*' }
if ($devices) {
    foreach ($d in $devices) {
        $state = 'working'
        if ($d.ConfigManagerErrorCode -ne 0) { $state = 'problem code ' + $d.ConfigManagerErrorCode }
        Out-Line ('- ' + (Show $d.Name) + ' | ' + $d.DeviceID + ' | ' + $state)
    }
} else {
    Out-Line '- none'
}

# --- Copy to clipboard ---------------------------------------------------------
$text = $report -join "`r`n"
$clip = Join-Path $env:SystemRoot 'System32\clip.exe'
if (Test-Path $clip) {
    $text | & $clip
    Write-Host ''
    Write-Host 'The report above is on the clipboard. Paste it into a comment on the PR.'
} else {
    Write-Host ''
    Write-Host 'Copy the report above into a comment on the PR.'
}
