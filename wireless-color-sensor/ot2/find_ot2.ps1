<#
.SYNOPSIS
    Find an OT-2 on a directly-cabled Windows machine, and say why it is missing.
    Ubuntu equivalent: find_ot2.sh.

.DESCRIPTION
    Run this on the Windows computer that has the Ethernet cable from the OT-2,
    when the Opentrons OT-2 App says "No robots found" or
    http://169.254.51.252:31950/health loads nothing. It answers four
    questions, in the order they matter:

      1. Which adapter is the robot cable, and does it have a 169.254.x.x
         address? Only a physical wired adapter counts. Tailscale, Bluetooth
         and Wi-Fi Direct adapters give themselves 169.254 addresses too, and
         none of them is the cable.
      2. Does Windows send robot traffic out of that adapter? Every adapter
         holding a 169.254 address gets its own 169.254.0.0/16 route, and the
         lowest metric wins. Tailscale's adapter reports a 100 Gb/s link, so
         Windows ranks it ahead of a 1 Gb/s Ethernet port, and robot traffic
         disappears into it.
      3. Does the robot answer mDNS on that cable? That is what the app's
         Devices tab relies on. It is asked over IPv6 as well as IPv4, and
         IPv6 works even when the adapter has no IPv4 address, so it can show
         the robot is there before the address problem is fixed.
      4. Does the robot answer GET /health on port 31950, both the way a
         browser would reach it and forced out of the cable's adapter?

    The robot's link-local address is self-assigned and Opentrons warn it can
    change on reconnect, so -KnownIp is only one candidate among those found.

    Read-only: it sends mDNS queries and HTTP requests and changes no
    settings, so it needs no administrator rights. When a setting does need
    changing it prints the exact commands, with this machine's adapter name
    filled in.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File find_ot2.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File find_ot2.ps1 -Adapter "Ethernet 2"
#>

[CmdletBinding()]
param(
    # Address this robot has used before; tried as a candidate, not assumed.
    [string]$KnownIp = '169.254.51.252',
    # Robot name, used for the <name>.local lookup.
    [string]$RobotName = 'OT2CEP20210722R13',
    # Seconds to listen for mDNS replies, per query.
    [int]$MdnsWaitSeconds = 4,
    # The adapter the robot cable is plugged into, if the automatic pick is wrong.
    [string]$Adapter = '',
    # Address the printed fix gives this machine; any unused 169.254.x.x works.
    [string]$StaticIp = '169.254.51.100'
)

$ErrorActionPreference = 'Continue'
$port = 31950
$version = '2026-09-25'

function Write-Section($text) {
    Write-Host ''
    Write-Host "=== $text " -ForegroundColor Cyan
}

# Reads a property that may be absent, from a CIM object or a plain one.
function Get-Prop($obj, [string]$name) {
    if ($null -eq $obj) { return $null }
    $p = $obj.PSObject.Properties[$name]
    if ($p) { return $p.Value }
    return $null
}

function Write-Commands([string[]]$lines) {
    Write-Host ''
    foreach ($l in $lines) { Write-Host "    $l" -ForegroundColor White }
    Write-Host ''
}

# --- 1. adapters ------------------------------------------------------------
Write-Section "Network adapters (find_ot2.ps1 $version)"

try {
    $nics = @(Get-NetAdapter -IncludeHidden -ErrorAction Stop)
} catch {
    Write-Host 'Get-NetAdapter is not available. Run this in Windows PowerShell on' -ForegroundColor Red
    Write-Host 'Windows 10 or 11. Paste the ipconfig output below into the issue instead.'
    if (Get-Command ipconfig -ErrorAction SilentlyContinue) { ipconfig /all | Out-String | Write-Host }
    exit 1
}
$v4     = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue)
$v4If   = @(Get-NetIPInterface -AddressFamily IPv4 -ErrorAction SilentlyContinue)
$ownIps = @($v4 | ForEach-Object { "$($_.IPAddress)" })

# Adapters that hand themselves a 169.254 address without being a cable.
$notCable = 'Tailscale|Wintun|WireGuard|TAP-Windows|OpenVPN|ZeroTier|Hyper-V|vEthernet|' +
            'VMware|VirtualBox|Wi-Fi Direct|Virtual|Loopback|Npcap|AnyConnect|Fortinet|' +
            'Kernel Debug|WAN Miniport'

function Get-AdapterKind($nic) {
    $text = "$($nic.Name) $($nic.InterfaceDescription)"
    if ($text -match 'Bluetooth') { return 'bluetooth' }
    if ($text -match $notCable -or (Get-Prop $nic 'Virtual') -eq $true) { return 'virtual' }
    switch ("$(Get-Prop $nic 'PhysicalMediaType')") {
        '802.3'         { return 'wired' }
        'Native 802.11' { return 'wifi' }
        'Wireless LAN'  { return 'wifi' }
        'BlueTooth'     { return 'bluetooth' }
    }
    # Some USB adapters leave the physical medium unspecified.
    if ("$(Get-Prop $nic 'MediaType')" -eq '802.3' -and (Get-Prop $nic 'HardwareInterface') -eq $true) {
        return 'wired'
    }
    return 'other'
}

function Get-AddrText($ifIndex) {
    $mine = @($v4 | Where-Object { $_.InterfaceIndex -eq $ifIndex })
    if (-not $mine) { return '(no IPv4)' }
    ($mine | ForEach-Object {
        $t = "$($_.IPAddress)/$($_.PrefixLength)"
        if ($_.AddressState -and "$($_.AddressState)" -ne 'Preferred') { $t += " ($($_.AddressState))" }
        $t
    }) -join ', '
}

function Test-HasLinkLocal($ifIndex) {
    [bool]($v4 | Where-Object {
        $_.InterfaceIndex -eq $ifIndex -and "$($_.IPAddress)" -like '169.254.*' -and
        "$($_.AddressState)" -eq 'Preferred' })
}

$kinds = @{}
foreach ($n in $nics) { $kinds[[int]$n.ifIndex] = Get-AdapterKind $n }

$wired   = @($nics | Where-Object { $kinds[[int]$_.ifIndex] -eq 'wired' })
$wiredUp = @($wired | Where-Object { "$($_.Status)" -eq 'Up' })
$robot   = $null
if ($Adapter) {
    $robot = $nics | Where-Object { $_.Name -eq $Adapter } | Select-Object -First 1
    if (-not $robot) {
        Write-Host "No adapter is called '$Adapter'. Run without -Adapter to list them." -ForegroundColor Red
        exit 1
    }
} else {
    # A wired adapter holding a routable address is on a real network, not the robot's cable.
    $pick = @($wiredUp | Where-Object {
        $idx = $_.ifIndex
        -not ($v4 | Where-Object { $_.InterfaceIndex -eq $idx -and "$($_.IPAddress)" -notlike '169.254.*' })
    })
    if ($pick) { $robot = $pick[0] }
}

foreach ($n in ($nics | Sort-Object { "$($_.Status)" -ne 'Up' }, Name)) {
    $idx = [int]$n.ifIndex
    $hasV4 = [bool]($v4 | Where-Object { $_.InterfaceIndex -eq $idx })
    if ((Get-Prop $n 'Hidden') -and -not $hasV4) { continue }   # WAN miniports and the like
    $tag = ''
    if ($robot -and $idx -eq [int]$robot.ifIndex) {
        $tag = '<-- robot cable'
    } elseif ("$($n.Status)" -eq 'Up' -and (Test-HasLinkLocal $idx)) {
        $tag = '<-- not a cable; its 169.254 route competes'
    }
    '{0,-30} {1,-9} {2,-12} {3,-20} {4}' -f $n.Name, $kinds[$idx], $n.Status, (Get-AddrText $idx), $tag |
        Write-Host
}

if ($robot -and $pick.Count -gt 1) {
    Write-Host ''
    Write-Host ('Several wired adapters could be the robot cable: {0}. Using {1}; re-run with' -f `
        (($pick | ForEach-Object { $_.Name }) -join ', '), $robot.Name) -ForegroundColor Yellow
    Write-Host '-Adapter "<name>" to pick another.' -ForegroundColor Yellow
}

# --- 2. the robot cable, and where 169.254 traffic actually goes ------------
Write-Section 'The robot cable'

$ipv4Off = $false
$myIp    = $null
if (-not $wired) {
    Write-Host 'Windows sees no wired Ethernet adapter at all.' -ForegroundColor Red
} elseif (-not $robot) {
    foreach ($w in $wired) {
        '{0} ({1}): {2}, {3}' -f $w.Name, $w.InterfaceDescription, $w.Status, (Get-AddrText $w.ifIndex) |
            Write-Host
    }
} else {
    $idx     = [int]$robot.ifIndex
    $ipIf    = $v4If | Where-Object { $_.InterfaceIndex -eq $idx } | Select-Object -First 1
    $binding = Get-NetAdapterBinding -Name $robot.Name -ComponentID ms_tcpip -ErrorAction SilentlyContinue
    $ipv4Off = (-not $ipIf) -or ($binding -and -not $binding.Enabled)
    $ll      = @($v4 | Where-Object { $_.InterfaceIndex -eq $idx -and "$($_.IPAddress)" -like '169.254.*' })
    $good    = @($ll | Where-Object { "$($_.AddressState)" -eq 'Preferred' })
    if ($good) { $myIp = "$($good[0].IPAddress)" }

    '{0} -- {1}, {2}, {3}' -f $robot.Name, $robot.InterfaceDescription, $robot.Status, $robot.LinkSpeed |
        Write-Host
    '  IPv4       {0}' -f $(if ($ipv4Off) { 'SWITCHED OFF on this adapter' } else { 'on' }) | Write-Host
    '  address    {0}' -f (Get-AddrText $idx) | Write-Host
    if ($ipIf) {
        '  DHCP       {0}{1}' -f $ipIf.Dhcp, $(if ("$($ipIf.Dhcp)" -eq 'Enabled') {
            ' (nothing on this cable hands out addresses)' } else { '' }) | Write-Host
        '  metric     {0}' -f $ipIf.InterfaceMetric | Write-Host
    }
    foreach ($d in ($ll | Where-Object { "$($_.AddressState)" -eq 'Duplicate' })) {
        Write-Host "  Windows found another device already using $($d.IPAddress)." -ForegroundColor Yellow
    }

    # Windows normally self-assigns 169.254.x.x when DHCP fails; policy can stop that.
    $tcpip = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
    foreach ($key in @($tcpip, "$tcpip\Interfaces\$(Get-Prop $robot 'InterfaceGuid')")) {
        $v = Get-ItemProperty -Path $key -Name IPAutoconfigurationEnabled -ErrorAction SilentlyContinue
        if ($v -and $v.IPAutoconfigurationEnabled -eq 0) {
            Write-Host "  Self-assigned 169.254 addresses are switched off by $key," -ForegroundColor Yellow
            Write-Host '  so Windows will never give this adapter one by itself.' -ForegroundColor Yellow
        }
    }

    # A static address saved on some other adapter is where a hand-made change went.
    $saved = @(Get-NetIPAddress -AddressFamily IPv4 -PolicyStore PersistentStore -ErrorAction SilentlyContinue |
        Where-Object { "$($_.IPAddress)" -like '169.254.*' -and $_.InterfaceIndex -ne $idx })
    foreach ($s in $saved) {
        Write-Host ("  A static {0} is saved on '{1}', not on {2}. If that was set by hand" -f `
            $s.IPAddress, $s.InterfaceAlias, $robot.Name) -ForegroundColor Yellow
        Write-Host ('  it went to the wrong adapter. Undo: netsh interface ipv4 set address "{0}" dhcp' -f `
            $s.InterfaceAlias) -ForegroundColor Yellow
    }
}

Write-Section 'Which adapter Windows sends 169.254.x.x traffic out of'

$connected = @{}
foreach ($i in $v4If) { if ("$($i.ConnectionState)" -eq 'Connected') { $connected[[int]$i.InterfaceIndex] = $i } }
$llRoutes = @(Get-NetRoute -AddressFamily IPv4 -DestinationPrefix '169.254.0.0/16' -ErrorAction SilentlyContinue |
    Where-Object { $connected.ContainsKey([int]$_.InterfaceIndex) } |
    ForEach-Object {
        $m = [int]$connected[[int]$_.InterfaceIndex].InterfaceMetric
        [pscustomobject]@{ Alias = $_.InterfaceAlias; Index = [int]$_.InterfaceIndex
                           Route = [int]$_.RouteMetric; Iface = $m; Total = [int]$_.RouteMetric + $m }
    } | Sort-Object Total)

if (-not $llRoutes) { Write-Host 'No adapter holds a 169.254 route, so robot traffic has nowhere to go.' }
foreach ($r in $llRoutes) {
    $note = if ($r -eq $llRoutes[0]) { '<-- wins' } else { '' }
    '{0,-30} route {1} + interface {2,-3} = {3}  {4}' -f $r.Alias, $r.Route, $r.Iface, $r.Total, $note |
        Write-Host
}

# What the cable's own route totals, or would total once it has an address.
$robotTotal = $null
if ($robot) {
    $own = $llRoutes | Where-Object { $_.Index -eq [int]$robot.ifIndex } | Select-Object -First 1
    if ($own) {
        $robotTotal = $own.Total
    } elseif ($ipIf) {
        $robotTotal = 256 + [int]$ipIf.InterfaceMetric
        Write-Host ("{0} has no 169.254 route yet; with an address it would total {1}." -f `
            $robot.Name, $robotTotal)
    }
}
# Routes on other adapters that beat or tie it: robot traffic would go there instead.
$rivals = @($llRoutes | Where-Object {
    (-not $robot -or $_.Index -ne [int]$robot.ifIndex) -and ($null -eq $robotTotal -or $_.Total -le $robotTotal) })

# The interface Windows would use for an address, i.e. what the browser gets.
function Get-Egress([string]$ip) {
    $res = @(Find-NetRoute -RemoteIPAddress $ip -ErrorAction SilentlyContinue)
    $route = $res | Where-Object { Get-Prop $_ 'DestinationPrefix' } | Select-Object -First 1
    if (-not $route) { return $null }
    [pscustomobject]@{ Alias = $route.InterfaceAlias; Index = [int]$route.InterfaceIndex
                       Prefix = $route.DestinationPrefix }
}

# --- 3. mDNS ----------------------------------------------------------------
# PTR for _http._tcp.local, the record the Opentrons app itself browses.
# Querying from an ephemeral port makes responders reply by unicast (RFC 6762
# s6.7), so the socket hears them without joining the group.
Write-Section "mDNS query for _http._tcp.local ($MdnsWaitSeconds s each)"

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

function Invoke-MdnsQuery([System.Net.IPAddress]$from, [System.Net.IPAddress]$group, [int]$ifIndex) {
    $heard = @()
    $udp = $null
    $query = New-MdnsQuery
    try {
        $udp = New-Object System.Net.Sockets.UdpClient((New-Object System.Net.IPEndPoint($from, 0)))
        # Pin the query to the cable; the route table would pick the lowest metric.
        if ($from.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetworkV6) {
            $udp.Client.SetSocketOption([System.Net.Sockets.SocketOptionLevel]::IPv6,
                [System.Net.Sockets.SocketOptionName]::MulticastInterface, $ifIndex)
        } else {
            $udp.Client.SetSocketOption([System.Net.Sockets.SocketOptionLevel]::IP,
                [System.Net.Sockets.SocketOptionName]::MulticastInterface, $from.GetAddressBytes())
        }
        $udp.Client.ReceiveTimeout = 700
        $null = $udp.Send($query, $query.Length, (New-Object System.Net.IPEndPoint($group, 5353)))
        Write-Host "queried from $from"
        $deadline = (Get-Date).AddSeconds($MdnsWaitSeconds)
        while ((Get-Date) -lt $deadline) {
            $remote = New-Object System.Net.IPEndPoint($from, 0)
            try {
                $reply = $udp.Receive([ref]$remote)
                if ($heard -notcontains $remote.Address) {
                    $heard += $remote.Address
                    $named = if ([System.Text.Encoding]::ASCII.GetString($reply) -match [regex]::Escape($RobotName)) {
                        "  names $RobotName" } else { '' }
                    Write-Host ("  reply from {0}{1}" -f $remote.Address, $named) -ForegroundColor Green
                }
            } catch {
                # receive timeout; keep listening until the deadline
            }
        }
    } catch {
        Write-Host ("  could not query from {0}: {1}" -f $from, $_.Exception.Message) -ForegroundColor Yellow
    } finally {
        if ($udp) { $udp.Close() }
    }
    return $heard
}

$responders = @()
$v6ll = $null
if ($robot) {
    $idx = [int]$robot.ifIndex
    if ($myIp) {
        $responders += @(Invoke-MdnsQuery ([System.Net.IPAddress]::Parse($myIp)) `
            ([System.Net.IPAddress]::Parse('224.0.0.251')) $idx)
    } else {
        Write-Host "No IPv4 query: $($robot.Name) has no usable 169.254 address."
    }
    $six = Get-NetIPAddress -AddressFamily IPv6 -InterfaceIndex $idx -ErrorAction SilentlyContinue |
        Where-Object { "$($_.IPAddress)" -like 'fe80*' -and "$($_.AddressState)" -eq 'Preferred' } |
        Select-Object -First 1
    if ($six) {
        $v6ll = [System.Net.IPAddress]::Parse(("$($six.IPAddress)" -split '%')[0])
        $v6ll.ScopeId = $idx
        $group6 = [System.Net.IPAddress]::Parse('ff02::fb')
        $group6.ScopeId = $idx
        $responders += @(Invoke-MdnsQuery $v6ll $group6 $idx)
    } else {
        Write-Host "No IPv6 query: $($robot.Name) has no IPv6 link-local address."
    }
} else {
    Write-Host 'Skipped: no adapter looks like the robot cable.'
}
if (-not $responders) {
    Write-Host 'No mDNS replies. This is what the app sees too: it browses the same record.'
}

# --- 4. candidates and /health ----------------------------------------------
Write-Section 'Candidate addresses'

$cand4 = @()
$cand6 = @()
if ($KnownIp) { $cand4 += $KnownIp }
foreach ($a in $responders) {
    if ($a.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetworkV6) { $cand6 += $a }
    else { $cand4 += "$a" }
}

# <name>.local via the OS resolver, which does mDNS on Windows 10 1703 and later.
try {
    $named = @([System.Net.Dns]::GetHostAddresses("$RobotName.local"))
    foreach ($ip in $named) {
        Write-Host "$RobotName.local resolves to $ip" -ForegroundColor Green
        if ($ip.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetworkV6) { $cand6 += $ip }
        else { $cand4 += "$ip" }
    }
    if (-not $named) { Write-Host "$RobotName.local resolved to nothing." }
} catch {
    Write-Host "$RobotName.local did not resolve (not fatal: name lookup is separate from discovery)."
}

# Whatever the neighbour table has learned on the cable itself.
if ($robot) {
    foreach ($nb in @(Get-NetNeighbor -InterfaceIndex ([int]$robot.ifIndex) -ErrorAction SilentlyContinue)) {
        $s = "$($nb.IPAddress)"
        if (@('Unreachable', 'Permanent', 'Incomplete') -contains "$($nb.State)") { continue }
        if ($s -like '169.254.*') { $cand4 += $s }
        elseif ($s -like 'fe80*') {
            $a = [System.Net.IPAddress]::Parse(($s -split '%')[0]); $a.ScopeId = [int]$robot.ifIndex; $cand6 += $a
        }
    }
}

$cand4 = @($cand4 | Where-Object { $_ -and $ownIps -notcontains $_ -and $_ -ne '169.254.255.255' } |
    Select-Object -Unique)
$seen6 = @{}
$cand6 = @(foreach ($a in $cand6) {
    if ($a -and -not ($v6ll -and $a.Equals($v6ll)) -and -not $seen6.ContainsKey("$a")) { $seen6["$a"] = 1; $a }
})
foreach ($c in $cand4) { Write-Host "  $c" }
foreach ($c in $cand6) { Write-Host "  $c" }

# A raw GET rather than Invoke-RestMethod, so it can be forced out of one adapter.
function Invoke-HealthProbe($ip, [string]$from) {
    $client = $null
    try {
        $target = if ($ip -is [System.Net.IPAddress]) { $ip } else { [System.Net.IPAddress]::Parse($ip) }
        if ($from) {
            $client = New-Object System.Net.Sockets.TcpClient(
                (New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Parse($from), 0)))
        } else {
            $client = New-Object System.Net.Sockets.TcpClient($target.AddressFamily)
        }
        $pending = $client.BeginConnect($target, $port, $null, $null)
        if (-not $pending.AsyncWaitHandle.WaitOne(3000)) {
            return [pscustomobject]@{ Ok = $false; Alive = $false; Text = 'no answer' }
        }
        $client.EndConnect($pending)
        $stream = $client.GetStream()
        $stream.ReadTimeout = 5000
        $hostHeader = if ($target.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetworkV6) {
            "[$(("$target" -split '%')[0])]" } else { "$target" }
        $request = "GET /health HTTP/1.0`r`nHost: ${hostHeader}:$port`r`nOpentrons-Version: 3`r`n`r`n"
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($request)
        $stream.Write($bytes, 0, $bytes.Length)
        $reply = (New-Object System.IO.StreamReader($stream)).ReadToEnd()
        if ($reply -match '^HTTP/\S+ (\d{3})') { $code = $Matches[1] } else {
            return [pscustomobject]@{ Ok = $false; Alive = $true; Text = 'answered, but not with HTTP' }
        }
        $name = if ($reply -match '"name"\s*:\s*"([^"]*)"') { $Matches[1] } else { '?' }
        $api  = if ($reply -match '"api_version"\s*:\s*"([^"]*)"') { $Matches[1] } else { '?' }
        return [pscustomobject]@{ Ok = ($code -eq '200'); Alive = $true
                                  Text = "HTTP $code  name=$name  api=$api" }
    } catch {
        $e = $_.Exception
        while ($e -and -not ($e -is [System.Net.Sockets.SocketException])) { $e = $e.InnerException }
        if ($e -and "$($e.SocketErrorCode)" -eq 'ConnectionRefused') {
            return [pscustomobject]@{ Ok = $false; Alive = $true; Text = 'refused: a host is there, port 31950 closed' }
        }
        $why = if ($e) { "$($e.SocketErrorCode)" } else { $_.Exception.Message }
        return [pscustomobject]@{ Ok = $false; Alive = $false; Text = "no answer ($why)" }
    } finally {
        if ($client) { $client.Close() }
    }
}

Write-Section "GET /health on port $port"

$viaRoute = @()   # answered the way a browser would reach it
$viaCable = @()   # answered only when forced out of the robot cable
$alive6   = $null
foreach ($ip in $cand4) {
    $egress = Get-Egress $ip
    $out = if ($egress) { "out of $($egress.Alias)" } else { 'no route' }
    $p = Invoke-HealthProbe $ip
    '{0,-18} as a browser would, {1,-22} {2}' -f $ip, $out, $p.Text | Write-Host
    if ($p.Ok) { $viaRoute += $ip }
    # Only worth forcing when the route table sends it somewhere else.
    if ($myIp -and -not $p.Ok -and (-not $egress -or $egress.Index -ne [int]$robot.ifIndex)) {
        $q = Invoke-HealthProbe $ip $myIp
        '{0,-18} forced out of {1,-22} {2}' -f '', $robot.Name, $q.Text | Write-Host
        if ($q.Ok) { $viaCable += $ip }
    }
}
foreach ($ip in $cand6) {
    $p = Invoke-HealthProbe $ip
    '{0} over IPv6: {1}' -f $ip, $p.Text | Write-Host
    if ($p.Alive -and -not $alive6) { $alive6 = $ip }
}
if (-not $cand4 -and -not $cand6) { Write-Host '(no candidates)' }
if (-not $alive6) {
    $v6resp = @($cand6 | Where-Object { $responders -contains $_ })
    if ($v6resp) { $alive6 = $v6resp[0] }
}

# --- verdict ----------------------------------------------------------------
Write-Section 'Verdict'

$admin = "Open PowerShell as administrator (Start, type PowerShell, right-click it,`n" +
         '"Run as administrator") and paste these lines:'
$metricFix = if ($robot) { "Set-NetIPInterface -InterfaceAlias '$($robot.Name)' -AddressFamily IPv4 -InterfaceMetric 1" }

function Write-Undo {
    Write-Host 'To undo, when this adapter is next used on a normal network:'
    Write-Commands @("netsh interface ipv4 set address `"$($robot.Name)`" dhcp",
                     "Set-NetIPInterface -InterfaceAlias '$($robot.Name)' -AddressFamily IPv4 -AutomaticMetric Enabled")
}

function Write-RivalNote {
    if (-not $rivals) { return }
    $r = $rivals[0]
    $score = if ($null -ne $robotTotal) { " ($($r.Total) against $robotTotal; lower wins)" } else { '' }
    Write-Host ("{0} also holds a 169.254 address, and Windows prefers its route over" -f $r.Alias) -ForegroundColor Yellow
    Write-Host ("{0}'s{1}, so robot traffic goes into {2} and is lost." -f $robot.Name, $score, $r.Alias) -ForegroundColor Yellow
    Write-Host 'The Set-NetIPInterface line below puts the cable first.' -ForegroundColor Yellow
}

if ($viaRoute) {
    Write-Host "The robot is reachable at $($viaRoute[0]). The link is fine." -ForegroundColor Green
    Write-Host ''
    Write-Host "Browser: http://$($viaRoute[0]):$port/health should show JSON. If it still loads nothing,"
    Write-Host 'the browser is going through a proxy: Settings > Network & internet > Proxy.'
    Write-Host 'App: if Devices still says "No robots found" after a minute, add it by address:'
    Write-Host "gear icon (bottom-left) > Advanced > Connect to a Robot via IP Address > $($viaRoute[0]) > Add."
} elseif (-not $wired) {
    Write-Host 'Windows sees no wired Ethernet adapter.' -ForegroundColor Yellow
    Write-Host 'If the robot is on a USB-Ethernet adapter, Windows has not recognised it: try another'
    Write-Host 'USB port, then look in Device Manager under "Network adapters".'
} elseif (-not $wiredUp) {
    Write-Host 'No wired adapter has a link.' -ForegroundColor Yellow
    Write-Host 'Nothing is answering at the other end of the cable. Check that the robot is on and'
    Write-Host 'that the cable is pushed fully into the robot and into this machine.'
} elseif (-not $robot) {
    Write-Host 'Every wired adapter with a link already has a normal network address, so none of' -ForegroundColor Yellow
    Write-Host 'them looks like the robot cable. If one of them IS, re-run with -Adapter "<its name>".'
} elseif ($ipv4Off -or -not $myIp) {
    if ($ipv4Off) {
        Write-Host "$($robot.Name) is the robot cable and has a link, but IPv4 is switched off on it." -ForegroundColor Red
    } else {
        Write-Host "$($robot.Name) is the robot cable and has a link, but no IPv4 address." -ForegroundColor Red
    }
    Write-Host 'With no address on that cable, Windows cannot send anything to the robot, so the'
    Write-Host 'browser and the app both fail even if the robot is fine.'
    if ($alive6) {
        Write-Host "The robot IS on this cable: $alive6 answered over IPv6." -ForegroundColor Green
    }
    Write-RivalNote
    Write-Host ''
    Write-Host $admin
    $lines = @()
    if ($ipv4Off) { $lines += "Enable-NetAdapterBinding -Name '$($robot.Name)' -ComponentID ms_tcpip" }
    $lines += "netsh interface ipv4 set address `"$($robot.Name)`" static $StaticIp 255.255.0.0"
    if ($rivals) { $lines += $metricFix }
    Write-Commands $lines
    Write-Host "Then open http://${KnownIp}:$port/health in a browser, or run this script again."
    Write-Undo
} elseif ($viaCable -or $rivals) {
    $ip = if ($viaCable) { $viaCable[0] } else { $KnownIp }
    if ($viaCable) {
        Write-Host "The robot answers at $ip, but only when forced out of $($robot.Name)." -ForegroundColor Red
    } else {
        Write-Host "Windows sends 169.254 traffic out of $($rivals[0].Alias), not $($robot.Name)." -ForegroundColor Red
    }
    Write-RivalNote
    # A rival already at metric 0 or 1 cannot be outranked; a /32 beats any /16.
    $hostRoute = "New-NetRoute -DestinationPrefix '$ip/32' -InterfaceAlias '$($robot.Name)' -NextHop 0.0.0.0 -PolicyStore ActiveStore"
    $lines = if (-not $rivals) { @($hostRoute) }
             elseif ($rivals[0].Iface -le 1) { @($metricFix, $hostRoute) }
             else { @($metricFix) }
    Write-Host ''
    Write-Host $admin
    Write-Commands $lines
    Write-Host 'Then run this script again.'
    if ($lines -contains $hostRoute) { Write-Host 'The New-NetRoute line lasts until Windows restarts.' }
    Write-Undo
} else {
    Write-Host "$($robot.Name) has $myIp, but nothing answered on port $port." -ForegroundColor Yellow
    if ($alive6) {
        Write-Host "The robot is on this cable ($alive6 answered over IPv6), so its IPv4 address is"
        Write-Host "probably no longer $KnownIp. Plug the cable into the Pi for two minutes and ask"
        Write-Host 'there, or read Robot Settings > Networking in the app once it connects any way.'
    } else {
        Write-Host 'Check, in this order: the robot is on and finished booting (give it ~3 minutes);'
        Write-Host "the cable is pushed fully into the robot and into this machine's adapter; the"
        Write-Host 'adapter is in a black USB 2.0 port, not a blue USB 3 one. Then re-run.'
    }
}

Write-Host ''
Write-Host 'Paste this whole output into the GitHub issue if it is still stuck.'
