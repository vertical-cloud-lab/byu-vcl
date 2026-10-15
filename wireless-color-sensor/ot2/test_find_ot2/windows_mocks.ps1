# Windows NetTCPIP/NetAdapter cmdlets for find_ot2.ps1, faked from the lab Windows 11
# machine's adapter list as pasted on PR #202, 2026-09-25. FT_SCENARIO picks a variant.
# Names are FT_-prefixed: PowerShell variables are case-insensitive and dynamically
# scoped, so a mock reading $S would see the script's own $s.
# Ethernet 2 is backed by a real veth (FT_E2_INDEX / FT_E2_V6) whose far end is robot_sim.py,
# so mDNS and /health go over real sockets; only the Windows queries are faked.
$FT_E2   = [int]$env:FT_E2_INDEX
$FT_E2v6 = $env:FT_E2_V6

function New-Nic($name, $desc, $idx, $status, $phys, $media = '802.3', $hw = $true, $virt = $false, $hidden = $false) {
    [pscustomobject]@{ Name = $name; InterfaceDescription = $desc; ifIndex = $idx; InterfaceIndex = $idx
        Status = $status; LinkSpeed = '1 Gbps'; PhysicalMediaType = $phys; MediaType = $media
        HardwareInterface = $hw; Virtual = $virt; Hidden = $hidden; InterfaceGuid = "{guid-$idx}" }
}
function New-Addr($alias, $idx, $ip, $len, $state = 'Preferred') {
    [pscustomobject]@{ InterfaceAlias = $alias; InterfaceIndex = $idx; IPAddress = $ip; PrefixLength = $len; AddressState = $state }
}
function New-If($alias, $idx, $metric, $conn = 'Connected', $dhcp = 'Enabled') {
    [pscustomobject]@{ InterfaceAlias = $alias; InterfaceIndex = $idx; InterfaceMetric = $metric; ConnectionState = $conn; Dhcp = $dhcp }
}
function New-Route($alias, $idx, $prefix = '169.254.0.0/16') {
    [pscustomobject]@{ InterfaceAlias = $alias; InterfaceIndex = $idx; DestinationPrefix = $prefix; RouteMetric = 256; NextHop = '0.0.0.0' }
}

$FT_e2Status = if ($env:FT_SCENARIO -eq 'unplugged') { 'Disconnected' } else { 'Up' }
$FT_NICS = @(
    (New-Nic 'Local Area Connection* 2' 'Microsoft Wi-Fi Direct Virtual Adapter #2' 21 'Disconnected' 'Native 802.11' '802.3' $false $true $true)
    (New-Nic 'Bluetooth Network Connection' 'Bluetooth Device (Personal Area Network)' 22 'Disconnected' 'BlueTooth')
    (New-Nic 'Local Area Connection* 1' 'Microsoft Wi-Fi Direct Virtual Adapter' 23 'Disconnected' 'Native 802.11' '802.3' $false $true $true)
    (New-Nic 'Wi-Fi' 'Intel(R) Wi-Fi 6E AX211 160MHz' 24 'Up' 'Native 802.11')
    (New-Nic 'Tailscale' 'Tailscale Tunnel' 25 'Up' 'Unspecified' 'IP' $false)
    (New-Nic 'WAN Miniport (IP)' 'WAN Miniport (IP)' 30 'Up' 'Unspecified' '802.3' $false $false $true)
)
if ($env:FT_SCENARIO -ne 'nowired') { $FT_NICS += New-Nic 'Ethernet 2' 'Realtek USB GbE Family Controller' $FT_E2 $FT_e2Status '802.3' }
if ($env:FT_SCENARIO -eq 'wrongadapter') { $FT_NICS += New-Nic 'Ethernet' 'Intel(R) Ethernet Connection (16) I219-LM' 26 'Disconnected' '802.3' }

$FT_V4 = @(
    (New-Addr 'Local Area Connection* 2' 21 '169.254.122.180' 16 'Tentative')
    (New-Addr 'Bluetooth Network Connection' 22 '169.254.12.51' 16 'Tentative')
    (New-Addr 'Local Area Connection* 1' 23 '169.254.44.45' 16 'Tentative')
    (New-Addr 'Wi-Fi' 24 '10.37.98.242' 16)
    (New-Addr 'Tailscale' 25 '169.254.83.107' 16)
)
$FT_fixed = @('static-only', 'fixed') -contains $env:FT_SCENARIO
if ($FT_fixed) { $FT_V4 += New-Addr 'Ethernet 2' $FT_E2 '169.254.51.100' 16 }

$FT_e2Metric = if ($env:FT_SCENARIO -eq 'fixed') { 1 } else { 25 }
$FT_IFS = @(
    (New-If 'Local Area Connection* 2' 21 25 'Disconnected'); (New-If 'Bluetooth Network Connection' 22 65 'Disconnected')
    (New-If 'Local Area Connection* 1' 23 25 'Disconnected'); (New-If 'Wi-Fi' 24 30)
    (New-If 'Tailscale' 25 5)
)
if (@('nowired', 'ipv4off') -notcontains $env:FT_SCENARIO) {
    $FT_IFS += New-If 'Ethernet 2' $FT_E2 $FT_e2Metric $(if ($env:FT_SCENARIO -eq 'unplugged') { 'Disconnected' } else { 'Connected' }) $(if ($FT_fixed) { 'Disabled' } else { 'Enabled' })
}

function Get-NetAdapter { [CmdletBinding()] param([switch]$IncludeHidden, $InterfaceIndex)
    $FT_NICS | Where-Object { $IncludeHidden -or -not $_.Hidden } }
function Get-NetIPAddress { [CmdletBinding()] param($AddressFamily, $InterfaceIndex, $PolicyStore)
    if ($PolicyStore -eq 'PersistentStore') {
        if ($env:FT_SCENARIO -eq 'wrongadapter') { New-Addr 'Ethernet' 26 '169.254.51.100' 16 }
        return
    }
    if ($AddressFamily -eq 'IPv6') {
        if ($InterfaceIndex -eq $FT_E2 -and $env:FT_SCENARIO -ne 'nowired') { New-Addr 'Ethernet 2' $FT_E2 "$FT_E2v6%$FT_E2" 64 }
        return
    }
    $FT_V4 | Where-Object { $null -eq $InterfaceIndex -or $_.InterfaceIndex -eq $InterfaceIndex } }
function Get-NetIPInterface { [CmdletBinding()] param($AddressFamily, $InterfaceIndex) $FT_IFS }
function Get-NetAdapterBinding { [CmdletBinding()] param($Name, $ComponentID)
    [pscustomobject]@{ Name = $Name; ComponentID = $ComponentID; Enabled = ($env:FT_SCENARIO -ne 'ipv4off') } }
function Get-NetRoute { [CmdletBinding()] param($AddressFamily, $DestinationPrefix)
    New-Route 'Local Area Connection* 2' 21; New-Route 'Local Area Connection* 1' 23; New-Route 'Tailscale' 25
    if ($FT_fixed) { New-Route 'Ethernet 2' $FT_E2 } }
function Find-NetRoute { [CmdletBinding()] param($RemoteIPAddress)
    if ($env:FT_SCENARIO -eq 'fixed') { New-Addr 'Ethernet 2' $FT_E2 '169.254.51.100' 16; New-Route 'Ethernet 2' $FT_E2 }
    else { New-Addr 'Tailscale' 25 '169.254.83.107' 16; New-Route 'Tailscale' 25 } }
function Get-NetNeighbor { [CmdletBinding()] param($InterfaceIndex, $AddressFamily)
    [pscustomobject]@{ IPAddress = '169.254.255.255'; State = 'Permanent' }
    [pscustomobject]@{ IPAddress = 'ff02::fb'; State = 'Permanent' } }
