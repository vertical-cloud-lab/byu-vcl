<#
.SYNOPSIS
  Read-only check that NI-DAQmx is installed and has picked up the EZstat's board.

.DESCRIPTION
  Changes nothing on the PC. Prints a short report:

    - when Windows last started, and whether it's still waiting for a restart
    - the NI-DAQmx version, and whether its DLLs are in place: nicaiu.dll (the
      C library) and nilvaiu.dll (the LabVIEW one EZware asks for)
    - each National Instruments USB device, with its Device Manager status
      and driver
    - the devices NI-DAQmx itself lists: name, product type, serial number and
      whether it's simulated

  The last part loads NI-DAQmx's C library and reads system and device
  properties only. Nothing is reset, reserved, self-tested or driven, so the
  EZstat's cell-enable line and outputs are left as they are.

      powershell -ExecutionPolicy Bypass -File .\check-nidaqmx.ps1 [-Out report.txt]

  Written for PowerShell 2.0, which Windows 7 ships with.
#>

param([string]$Out = '')

$ErrorActionPreference = 'SilentlyContinue'
$report = New-Object System.Collections.ArrayList
function Out-Line([string]$s) { [void]$report.Add($s); Write-Host $s }
function Show([object]$v) { if ($null -eq $v -or "$v" -eq '') { 'unknown' } else { "$v" } }

Out-Line '### NI-DAQmx check'
Out-Line ''
Out-Line ('Run ' + (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss') + ' UTC (PC clock)')
Out-Line ''

# --- Restart state ---------------------------------------------------------
$os = Get-WmiObject Win32_OperatingSystem
if ($os) {
    $boot = [Management.ManagementDateTimeConverter]::ToDateTime($os.LastBootUpTime)
    Out-Line ('- Windows last started: ' + $boot.ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss') + ' UTC')
}
$pending = @()
$sm = Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager'
if ($sm.PendingFileRenameOperations) { $pending += 'files to replace at the next start (PendingFileRenameOperations)' }
if (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending') { $pending += 'Windows servicing' }
if (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired') { $pending += 'Windows Update' }
if ($pending.Count -gt 0) {
    Out-Line ('- Waiting for a restart: yes: ' + ($pending -join '; '))
} else {
    Out-Line '- Waiting for a restart: no'
}

# --- NI-DAQmx install --------------------------------------------------------
Out-Line ''
Out-Line '**NI-DAQmx:**'
Out-Line ''
foreach ($root in @('HKLM:\SOFTWARE\National Instruments', 'HKLM:\SOFTWARE\Wow6432Node\National Instruments')) {
    $v = (Get-ItemProperty "$root\NI-DAQmx\CurrentVersion").Version
    if ($v) { Out-Line ('- Version (registry, ' + $root.Substring(6) + '): ' + $v) }
}
$keys = @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
          'HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')
$apps = @(Get-ItemProperty $keys | Where-Object { $_.DisplayName -match '^NI-DAQmx' } |
          Sort-Object DisplayName, DisplayVersion -Unique)
Out-Line ('- Installed packages named NI-DAQmx*: ' + $apps.Count)
foreach ($a in $apps) {
    Out-Line ('  - ' + $a.DisplayName + ' ' + (Show $a.DisplayVersion) + ', installed ' + (Show $a.InstallDate))
}

# A 32-bit PowerShell sees SysWOW64 as System32; Sysnative is the real one.
$sys64 = Join-Path $env:windir 'System32'
if ([IntPtr]::Size -eq 4 -and (Test-Path (Join-Path $env:windir 'Sysnative'))) {
    $sys64 = Join-Path $env:windir 'Sysnative'
}
$dirs = @{ '64-bit' = $sys64; '32-bit (EZware is 32-bit)' = (Join-Path $env:windir 'SysWOW64') }
foreach ($bits in ($dirs.Keys | Sort-Object)) {
    foreach ($dll in @('nicaiu.dll', 'nilvaiu.dll')) {
        $p = Join-Path $dirs[$bits] $dll
        if (Test-Path $p) {
            Out-Line ('- ' + $dll + ', ' + $bits + ': file version ' + (Show (Get-Item $p).VersionInfo.FileVersion))
        } else {
            Out-Line ('- ' + $dll + ', ' + $bits + ': missing')
        }
    }
}

# --- What Windows sees -------------------------------------------------------
Out-Line ''
Out-Line '**National Instruments devices in Device Manager:**'
Out-Line ''
$devices = @(Get-WmiObject Win32_PnPEntity | Where-Object {
    $_.DeviceID -like 'USB\VID_3923*' -or $_.Manufacturer -like '*National Instruments*' })
$drivers = @(Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceID -like 'USB\VID_3923*' })
if ($devices.Count -eq 0) { Out-Line '- none' }
foreach ($d in $devices) {
    $state = 'working'
    if ($d.ConfigManagerErrorCode -ne 0) { $state = 'problem code ' + $d.ConfigManagerErrorCode }
    Out-Line ('- ' + (Show $d.Name) + ' | ' + $d.DeviceID + ' | ' + $state + ' | driver service ' + (Show $d.Service))
    foreach ($drv in ($drivers | Where-Object { $_.DeviceID -eq $d.DeviceID })) {
        Out-Line ('  - driver ' + (Show $drv.DriverVersion) + ' from ' + (Show $drv.DriverProviderName) +
                  ', ' + (Show $drv.InfName) + ', signed ' + (Show $drv.IsSigned))
    }
}

# --- What NI-DAQmx sees ------------------------------------------------------
Out-Line ''
Out-Line '**Devices NI-DAQmx lists (property reads only):**'
Out-Line ''
$src = @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class NiDaqmxCheck {
    [DllImport("nicaiu.dll")]
    public static extern int DAQmxGetSysNIDAQMajorVersion(out uint v);
    [DllImport("nicaiu.dll")]
    public static extern int DAQmxGetSysNIDAQMinorVersion(out uint v);
    [DllImport("nicaiu.dll", CharSet = CharSet.Ansi)]
    public static extern int DAQmxGetSysDevNames(StringBuilder buf, uint size);
    [DllImport("nicaiu.dll", CharSet = CharSet.Ansi)]
    public static extern int DAQmxGetDevProductType(string dev, StringBuilder buf, uint size);
    [DllImport("nicaiu.dll", CharSet = CharSet.Ansi)]
    public static extern int DAQmxGetDevProductNum(string dev, out uint v);
    [DllImport("nicaiu.dll", CharSet = CharSet.Ansi)]
    public static extern int DAQmxGetDevSerialNum(string dev, out uint v);
    [DllImport("nicaiu.dll", CharSet = CharSet.Ansi)]
    public static extern int DAQmxGetDevIsSimulated(string dev, out uint v);
    [DllImport("nicaiu.dll", CharSet = CharSet.Ansi)]
    public static extern int DAQmxGetErrorString(int code, StringBuilder buf, uint size);
}
'@
function DaqError([int]$code) {
    $sb = New-Object System.Text.StringBuilder 2048
    [void][NiDaqmxCheck]::DAQmxGetErrorString($code, $sb, 2048)
    'error ' + $code + ' (' + $sb.ToString() + ')'
}
try {
    $ErrorActionPreference = 'Stop'
    Add-Type -TypeDefinition $src
    $major = [uint32]0
    $minor = [uint32]0
    [void][NiDaqmxCheck]::DAQmxGetSysNIDAQMajorVersion([ref]$major)
    [void][NiDaqmxCheck]::DAQmxGetSysNIDAQMinorVersion([ref]$minor)
    Out-Line ('- nicaiu.dll loaded (' + (8 * [IntPtr]::Size) + '-bit); it reports NI-DAQmx ' + $major + '.' + $minor)
    $sb = New-Object System.Text.StringBuilder 4096
    $rc = [NiDaqmxCheck]::DAQmxGetSysDevNames($sb, 4096)
    if ($rc -lt 0) { Out-Line ('- listing devices failed: ' + (DaqError $rc)) }
    $names = @($sb.ToString().Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($rc -ge 0 -and $names.Count -eq 0) { Out-Line '- no devices' }
    foreach ($n in $names) {
        $type = New-Object System.Text.StringBuilder 256
        $num = [uint32]0
        $serial = [uint32]0
        $sim = [uint32]0
        $r1 = [NiDaqmxCheck]::DAQmxGetDevProductType($n, $type, 256)
        $r2 = [NiDaqmxCheck]::DAQmxGetDevProductNum($n, [ref]$num)
        $r3 = [NiDaqmxCheck]::DAQmxGetDevSerialNum($n, [ref]$serial)
        $r4 = [NiDaqmxCheck]::DAQmxGetDevIsSimulated($n, [ref]$sim)
        $line = '- ' + $n + ': ' + $type.ToString() + ', product number 0x' + $num.ToString('X') +
                ', serial number 0x' + $serial.ToString('X') + ', simulated ' + ($sim -ne 0)
        foreach ($r in @($r1, $r2, $r3, $r4)) { if ($r -lt 0) { $line += '; ' + (DaqError $r) } }
        Out-Line $line
    }
} catch {
    Out-Line ('- NI-DAQmx C library not usable: ' + $_.Exception.Message)
}
$ErrorActionPreference = 'SilentlyContinue'

if ($Out) { [IO.File]::WriteAllLines($Out, [string[]]$report.ToArray()) }
