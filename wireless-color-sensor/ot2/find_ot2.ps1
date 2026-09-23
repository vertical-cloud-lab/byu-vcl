<#
.SYNOPSIS
    Find an OT-2 on a directly-cabled Windows machine, and say why it is missing.

.DESCRIPTION
    Run this on the Windows computer that has the Ethernet cable from the OT-2,
    when the Opentrons OT-2 App says "No robots found". It answers the three
    questions that matter, in the order they matter:

      1. Does this machine have a link-local (169.254.x.x) address on that
         cable? Without one there is no route to the robot at all, and every
         other symptom is downstream of that.
      2. Does anything answer mDNS on that link? This is the exact mechanism
         the app's Devices tab uses, so a silent link explains the app
         directly.
      3. Does any candidate address answer GET /health on port 31950? That is
         the robot's own API, and its reply names the robot.

    The robot's link-local address is self-assigned and Opentrons warn it can
    change on reconnect, so nothing here trusts a hard-coded address: -KnownIp
    is only tried as one candidate among the ones discovered.

    Read-only. It sends pings, an mDNS query and an HTTP GET, and changes no
    settings. No administrator rights needed.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File find_ot2.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File find_ot2.ps1 -RobotName OT2CEP20210722R13
#>

[CmdletBinding()]
param(
    # Address this robot has used before; tried as a candidate, not assumed.
    [string]$KnownIp = '169.254.51.252',
    # Robot name, used for the <name>.local mDNS lookup.
    [string]$RobotName = 'OT2CEP20210722R13',
    # Seconds to listen for mDNS replies.
    [int]$MdnsWaitSeconds = 6
)

$ErrorActionPreference = 'Continue'
$port = 31950

function Write-Section($text) {
    Write-Host ''
    Write-Host "=== $text " -ForegroundColor Cyan
}

# --- 1. interfaces ----------------------------------------------------------
Write-Section 'Network adapters'

$linkLocalAddrs = @()
try {
    $addrs = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.InterfaceAlias -notmatch 'Loopback' }
    foreach ($a in $addrs) {
        $status = try { (Get-NetAdapter -InterfaceIndex $a.InterfaceIndex -ErrorAction Stop).Status }
                  catch { 'unknown' }
        $tag = ''
        if ($a.IPAddress -like '169.254.*') {
            $tag = '   <-- link-local, this is the robot cable'
            $linkLocalAddrs += $a.IPAddress
        }
        '{0,-28} {1,-16} /{2,-3} {3}{4}' -f $a.InterfaceAlias, $a.IPAddress,
            $a.PrefixLength, $status, $tag | Write-Host
    }
    # Adapters that are up but hold no IPv4 address at all.
    foreach ($n in (Get-NetAdapter -ErrorAction Stop | Where-Object { $_.Status -eq 'Up' })) {
        if (-not ($addrs | Where-Object { $_.InterfaceIndex -eq $n.ifIndex })) {
            '{0,-28} {1,-16} {2}' -f $n.Name, '(no IPv4)', 'Up   <-- up but unaddressed' | Write-Host
        }
    }
} catch {
    Write-Host 'Get-NetIPAddress unavailable; falling back to ipconfig.' -ForegroundColor Yellow
    if (Get-Command ipconfig -ErrorAction SilentlyContinue) {
        $text = ipconfig /all | Out-String
        Write-Host $text
        $linkLocalAddrs = @([regex]::Matches($text, '169\.254\.\d+\.\d+') |
            ForEach-Object { $_.Value })
    } else {
        Write-Host 'ipconfig not found either -- is this actually Windows?' -ForegroundColor Yellow
    }
}

if (-not $linkLocalAddrs) {
    Write-Host ''
    Write-Host 'NO 169.254.x.x ADDRESS ON THIS MACHINE.' -ForegroundColor Red
    Write-Host 'The robot is link-local, so without one there is no route to it and'
    Write-Host 'the browser test cannot work. Windows only falls back to 169.254.x.x'
    Write-Host 'after DHCP times out, which takes up to 60 s, and nothing on this'
    Write-Host 'cable serves DHCP. Wait a minute and re-run, or give the adapter a'
    Write-Host 'static 169.254.51.100 / 255.255.0.0 with no gateway -- see'
    Write-Host 'opentrons-calibration.md, "When the link itself is the problem".'
}

# --- 2. mDNS ----------------------------------------------------------------
# Query PTR for _http._tcp.local, the record the Opentrons app itself browses.
# Querying from an ephemeral source port makes responders reply by unicast
# (RFC 6762 s6.7), so a plain UdpClient receives them without joining the group.
Write-Section "mDNS query for _http._tcp.local ($MdnsWaitSeconds s)"

function New-MdnsQuery {
    $bytes = New-Object System.Collections.Generic.List[byte]
    $bytes.AddRange([byte[]](0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0))   # header, 1 question
    foreach ($label in @('_http', '_tcp', 'local')) {
        $l = [System.Text.Encoding]::ASCII.GetBytes($label)
        $bytes.Add([byte]$l.Length); $bytes.AddRange($l)
    }
    $bytes.Add(0)                                                    # root label
    $bytes.AddRange([byte[]](0, 12, 0, 1))                           # QTYPE PTR, QCLASS IN
    return $bytes.ToArray()
}

$responders = @()
$query = New-MdnsQuery
$sources = if ($linkLocalAddrs) { $linkLocalAddrs } else { @([System.Net.IPAddress]::Any.ToString()) }

foreach ($src in $sources) {
    $udp = $null
    try {
        $udp = New-Object System.Net.Sockets.UdpClient(
            (New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Parse($src), 0)))
        $udp.Client.ReceiveTimeout = 700
        $null = $udp.Send($query, $query.Length, '224.0.0.251', 5353)
        Write-Host "queried from $src"

        $deadline = (Get-Date).AddSeconds($MdnsWaitSeconds)
        while ((Get-Date) -lt $deadline) {
            $remote = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Any, 0)
            try {
                $null = $udp.Receive([ref]$remote)
                if ($responders -notcontains $remote.Address.ToString()) {
                    $responders += $remote.Address.ToString()
                    Write-Host ("  reply from {0}" -f $remote.Address) -ForegroundColor Green
                }
            } catch [System.Net.Sockets.SocketException] {
                # receive timeout; keep waiting until the deadline
            }
        }
    } catch {
        Write-Host ("  could not query from {0}: {1}" -f $src, $_.Exception.Message) -ForegroundColor Yellow
    } finally {
        if ($udp) { $udp.Close() }
    }
}

if (-not $responders) {
    Write-Host 'No mDNS replies. This is what the app sees too -- it browses the'
    Write-Host 'same record. Either nothing is on the cable, or UDP 5353 is being'
    Write-Host 'blocked (Windows Firewall classifies a new wired network as Public).'
}

# --- 3. name lookup and HTTP ------------------------------------------------
Write-Section "Candidate addresses"

$candidates = @()
$candidates += $responders
if ($KnownIp) { $candidates += $KnownIp }

# <name>.local via the OS resolver, which does mDNS on Windows 10 1703+.
try {
    $entry = [System.Net.Dns]::GetHostEntry("$RobotName.local")
    foreach ($ip in $entry.AddressList) {
        if ($ip.AddressFamily -eq 'InterNetwork') {
            Write-Host "$RobotName.local resolves to $ip" -ForegroundColor Green
            $candidates += $ip.ToString()
        }
    }
} catch {
    Write-Host "$RobotName.local did not resolve (not fatal -- mDNS name lookup is separate from service discovery)."
}

# Anything the ARP table already learned on a link-local subnet.
try {
    $candidates += (Get-NetNeighbor -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.IPAddress -like '169.254.*' -and $_.State -ne 'Unreachable' } |
        Select-Object -ExpandProperty IPAddress)
} catch {
    if (Get-Command arp -ErrorAction SilentlyContinue) {
        $candidates += ([regex]::Matches((arp -a | Out-String), '169\.254\.\d+\.\d+') |
            ForEach-Object { $_.Value })
    }
}

$candidates = $candidates | Where-Object { $_ } | Select-Object -Unique
if (-not $candidates) { Write-Host '(none)' }

Write-Section "GET /health on port $port"

$found = @()
foreach ($ip in $candidates) {
    $reach = Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue
    try {
        $health = Invoke-RestMethod -Uri "http://${ip}:${port}/health" -TimeoutSec 5
        Write-Host ("{0,-18} ping={1,-5} HTTP 200  name={2}  api={3}" -f `
            $ip, $reach, $health.name, $health.api_version) -ForegroundColor Green
        $found += $ip
    } catch {
        Write-Host ("{0,-18} ping={1,-5} no answer on {2}" -f $ip, $reach, $port)
    }
}

# --- verdict ----------------------------------------------------------------
Write-Section 'Verdict'

if ($found) {
    Write-Host "The robot is reachable at $($found[0]). The link is fine." -ForegroundColor Green
    Write-Host ''
    Write-Host 'In the Opentrons OT-2 App: gear icon (bottom-left) -> Advanced ->'
    Write-Host "Connect to a Robot via IP Address -> Set up connection -> $($found[0]) -> Add."
    Write-Host 'That bypasses discovery entirely and is remembered.'
} elseif ($linkLocalAddrs) {
    Write-Host 'This machine has a link-local address but nothing answered.' -ForegroundColor Yellow
    Write-Host 'Check, in this order: the robot is powered on and finished booting'
    Write-Host '(give it ~3 minutes); the Ethernet cable is in the robot and in this'
    Write-Host "machine's adapter; the adapter is in a black USB 2.0 port, not a blue"
    Write-Host 'USB 3 one. Then re-run.'
} else {
    Write-Host 'This machine has no link-local address, so nothing above could have' -ForegroundColor Yellow
    Write-Host 'worked. Fix that first -- see the message in the adapters section.'
}

Write-Host ''
Write-Host 'Paste this whole output into the GitHub issue if it is still stuck.'
