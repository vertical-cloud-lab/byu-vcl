#!/usr/bin/env bash
# Regression test for ../find_ot2.ps1, runnable on Linux with pwsh and sudo.
#
# The Windows queries (Get-NetAdapter, Find-NetRoute, ...) are faked by
# windows_mocks.ps1 from the lab machine's real adapter list, including the
# logged-out Tailscale adapter holding 169.254.83.107 that stole robot traffic.
# Everything else is real: "Ethernet 2" is a veth whose far end sits in a
# network namespace running robot_sim.py, so the mDNS queries and GET /health
# probes go over real IPv4 and IPv6 sockets.
#
#   ./run.sh              every scenario
#   ./run.sh tim fixed    just these
#
# Touches only a veth pair, netns ot2sim, routing table 151 and a rule for
# 169.254.51.100, all removed on exit. Nothing is added for 169.254.0.0/16 as a
# whole, so cloud metadata at 169.254.169.254 is unaffected.
set -u
cd "$(dirname "$0")"
SCRIPT=$(realpath "${FIND_OT2:-../find_ot2.ps1}")   # FIND_OT2=path tests another copy
LOG=$(mktemp -d)
nap() { python3 -c "import time; time.sleep($1)"; }

# Scenario -> a line its verdict must contain.
declare -A EXPECT=(
    [tim]="Ethernet 2 is the robot cable and has a link, but no IPv4 address."
    [wrongadapter]="A static 169.254.51.100 is saved on 'Ethernet', not on Ethernet 2."
    [ipv4off]="Enable-NetAdapterBinding -Name 'Ethernet 2' -ComponentID ms_tcpip"
    [unplugged]="No wired adapter has a link."
    [nowired]="Windows sees no wired Ethernet adapter."
    [static-only]="The robot answers at 169.254.51.252, but only when forced out of Ethernet 2."
    [fixed]="The robot is reachable at 169.254.51.252. The link is fine."
)
# ...and, for some, a second line that must be there too.
declare -A ALSO=(
    [tim]="Set-NetIPInterface -InterfaceAlias 'Ethernet 2' -AddressFamily IPv4 -InterfaceMetric 1"
    [ipv4off]="answered over IPv6"
    [static-only]="Set-NetIPInterface -InterfaceAlias 'Ethernet 2' -AddressFamily IPv4 -InterfaceMetric 1"
    [fixed]="out of Ethernet 2"
)

v4() {   # none | policy (only traffic bound to .100 reaches the robot) | full
    sudo ip addr del 169.254.51.100/32 dev ot2h 2>/dev/null
    sudo ip rule del from 169.254.51.100 lookup 151 2>/dev/null
    sudo ip route flush table 151 2>/dev/null
    sudo ip route del 169.254.51.252/32 dev ot2h 2>/dev/null
    [ "$1" = none ] && return
    sudo ip addr add 169.254.51.100/32 dev ot2h
    sudo ip rule add from 169.254.51.100 lookup 151 priority 151
    sudo ip route add 169.254.51.252/32 dev ot2h src 169.254.51.100 table 151
    [ "$1" = full ] && sudo ip route add 169.254.51.252/32 dev ot2h src 169.254.51.100
}

teardown() {
    v4 none 2>/dev/null
    [ -f "$LOG/sim.pid" ] && sudo kill "$(cat "$LOG/sim.pid")" 2>/dev/null
    sudo ip netns del ot2sim 2>/dev/null
    sudo ip link del ot2h 2>/dev/null
}
trap teardown EXIT
teardown

sudo ip netns add ot2sim
sudo ip link add ot2h type veth peer name ot2r
sudo ip link set ot2r netns ot2sim
sudo ip -n ot2sim link set lo up
sudo ip -n ot2sim link set ot2r up
sudo ip -n ot2sim addr add 169.254.51.252/16 dev ot2r
sudo ip link set ot2h up
nap 3   # IPv6 duplicate-address detection on both ends
sudo ip netns exec ot2sim sh -c "echo \$\$ > '$LOG/sim.pid'; exec python3 -u robot_sim.py ot2r 169.254.51.252" \
    > "$LOG/sim.log" 2>&1 &
nap 2
grep -q ready "$LOG/sim.log" || { echo "robot_sim.py did not start:"; cat "$LOG/sim.log"; exit 1; }

export FT_E2_INDEX=$(cat /sys/class/net/ot2h/ifindex)
export FT_E2_V6=$(ip -6 -j addr show dev ot2h scope link |
    python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["addr_info"][0]["local"])')

fail=0
for s in ${@:-tim wrongadapter ipv4off unplugged nowired static-only fixed}; do
    case $s in static-only) v4 policy ;; fixed) v4 full ;; *) v4 none ;; esac
    FT_SCENARIO=$s timeout 150 pwsh -NoProfile -NonInteractive \
        -Command ". ./windows_mocks.ps1; & '$SCRIPT' -MdnsWaitSeconds 2" > "$LOG/$s.txt" 2>&1
    if grep -qF -- "${EXPECT[$s]}" "$LOG/$s.txt" && { [ -z "${ALSO[$s]:-}" ] || grep -qF -- "${ALSO[$s]}" "$LOG/$s.txt"; }; then
        echo "PASS  $s"
    else
        echo "FAIL  $s -- full output:"; sed 's/^/      /' "$LOG/$s.txt"; fail=1
    fi
done
echo "outputs in $LOG"
exit $fail
