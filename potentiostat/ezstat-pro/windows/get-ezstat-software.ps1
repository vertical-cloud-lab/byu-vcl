<#
.SYNOPSIS
  Download the EZstat-Pro software set and check every file's SHA-256.

.DESCRIPTION
  Downloads only; it installs nothing. Files go to Downloads\ezstat-software
  unless -Dest says otherwise. A file that is already there with the right
  hash is not downloaded again, so the script can be re-run after a failure.

  Which NI-DAQmx it fetches depends on the Windows version (-DAQmx auto):
    Windows 7 or 8.0          -> NI-DAQmx 9.7.0, the version in NuVant's manual
    Windows 8.1, 10 or 11     -> NI-DAQmx 14.5.1, the newest that still
                                 supports LabVIEW 2011 programs like EZware
  Use -DAQmx 9.7 or -DAQmx 14.5.1 to choose, or -DAQmx both.

  About 2 GB in total. If the lab PC has no internet, run this on any Windows
  laptop and carry the folder over on a USB stick.

      powershell -ExecutionPolicy Bypass -File .\get-ezstat-software.ps1

  The hashes were taken from copies downloaded on 2026-10-20; see README.md.
#>
param(
    [ValidateSet('auto', '9.7', '14.5.1', 'both')]
    [string]$DAQmx = 'auto',
    [string]$Dest = (Join-Path $env:USERPROFILE 'Downloads\ezstat-software')
)

$ErrorActionPreference = 'Stop'

$runtime = @{
    Name   = 'LabVIEW 2011 SP1 Run-Time Engine (32-bit)'
    File   = 'LVRTE2011SP1std.exe'
    Url    = 'https://download.ni.com/support/softlib/labview/labview_runtime/2011%20SP1/LVRTE2011SP1std.exe'
    Bytes  = 224373344
    Sha256 = 'b31615048274ec23c6b181a7a93b786828738f18a7cf8c784a3eec251cbcf29c'
}
$daqmx97 = @{
    Name   = 'NI-DAQmx 9.7.0'
    File   = 'NIDAQ970f0.zip'
    Url    = 'https://download.ni.com/support/softlib/multifunction_daq/nidaqmx/9.7.0/NIDAQ970f0.zip'
    Bytes  = 1673463452
    Sha256 = '2bbf32fd84a5f593a872c1571f02aba8b03de5b638777e429da9447f854f084f'
}
$daqmx1451 = @{
    Name   = 'NI-DAQmx 14.5.1'
    File   = 'NIDAQ1451f1.zip'
    Url    = 'https://download.ni.com/support/softlib/multifunction_daq/nidaqmx/14.5.1/NIDAQ1451f1.zip'
    Bytes  = 1748101421
    Sha256 = '0e3cba22e4b6cac59cd7d16e45158eabdb51c384810dff343607ed0d1f43708d'
}
$ezware = @{
    Name   = 'EZware-2013 v7.1.16.1025 (NuVant; Wayback Machine copy of nuvant.com/downloads)'
    File   = 'Ins EZware-2013 v.7.1.16.1025.exe'
    Url    = 'https://web.archive.org/web/20190517053447id_/http://nuvant.com/downloads/Ins%20EZware-2013%20v.7.1.16.1025.exe'
    Bytes  = 14491458
    Sha256 = '5f8e8cd4e28f8443441ea05ac530949988a82f2856bded73c28af7ca93349101'
}

if ($DAQmx -eq 'auto') {
    $v = [Environment]::OSVersion.Version
    # 6.1 = Windows 7, 6.2 = Windows 8.0, 6.3 = Windows 8.1, 10.0 = Windows 10 and 11
    if ($v.Major -eq 6 -and $v.Minor -le 2) { $DAQmx = '9.7' } else { $DAQmx = '14.5.1' }
    Write-Host ('Windows version ' + $v + ': using NI-DAQmx ' + $DAQmx)
}
$files = @($runtime)
if ($DAQmx -eq '9.7' -or $DAQmx -eq 'both') { $files += $daqmx97 }
if ($DAQmx -eq '14.5.1' -or $DAQmx -eq 'both') { $files += $daqmx1451 }
$files += $ezware

function Get-Sha256([string]$path) {
    # Get-FileHash needs PowerShell 4; this works on 2.0 (Windows 7) too.
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($path)
    try { $hash = $sha.ComputeHash($stream) } finally { $stream.Close() }
    return ([BitConverter]::ToString($hash) -replace '-', '').ToLower()
}

# download.ni.com and web.archive.org need TLS 1.2 (3072), which older
# PowerShell does not turn on by itself.
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor 3072
} catch {
    Write-Warning 'Could not enable TLS 1.2. If downloads fail, use the browser links in README.md.'
}

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$failed = 0
foreach ($f in $files) {
    $path = Join-Path $Dest $f.File
    Write-Host ''
    Write-Host ($f.Name + ' -> ' + $path)
    if ((Test-Path $path) -and ((Get-Item $path).Length -eq $f.Bytes) -and ((Get-Sha256 $path) -eq $f.Sha256)) {
        Write-Host '  already downloaded, hash OK'
        continue
    }
    Write-Host ('  downloading {0:N0} MB ...' -f ($f.Bytes / 1MB))
    try {
        (New-Object System.Net.WebClient).DownloadFile($f.Url, $path)
    } catch {
        Write-Warning ('  download failed: ' + $_.Exception.Message)
        $failed++
        continue
    }
    $len = (Get-Item $path).Length
    $sum = Get-Sha256 $path
    if ($len -eq $f.Bytes -and $sum -eq $f.Sha256) {
        Write-Host '  hash OK'
    } else {
        Write-Warning ('  MISMATCH: got ' + $len + ' bytes, SHA-256 ' + $sum + '. Do not run this file.')
        $failed++
    }
}

Write-Host ''
if ($failed -eq 0) {
    Write-Host ('All files downloaded and checked, in ' + $Dest)
    Write-Host 'Install in this order with the EZstat USB cable unplugged (manual p. 40):'
    Write-Host '  1. LVRTE2011SP1std.exe, default options, then restart'
    Write-Host '  2. unzip the NI-DAQmx zip, run setup.exe inside, default options, then restart'
    Write-Host '  3. Ins EZware-2013 v.7.1.16.1025.exe (no restart needed)'
    Write-Host 'Then plug in the EZstat as in step 2 of README.md.'
} else {
    Write-Warning ($failed.ToString() + ' file(s) failed. Re-run the script, or use the browser links in README.md.')
    exit 1
}
