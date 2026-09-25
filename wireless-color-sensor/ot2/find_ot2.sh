#!/usr/bin/env bash
# Find an OT-2 on a directly-cabled Ubuntu machine, and say why it is missing.
#
# Run this on the Ubuntu computer that has the Ethernet cable from the OT-2,
# when the Opentrons OT-2 App says "No robots found". It answers the three
# questions that matter, in the order they matter:
#
#   1. Does this machine have a link-local (169.254.x.x) address on that cable?
#      Without one there is no route to the robot at all, and every other
#      symptom is downstream of that. Unlike Windows, Ubuntu does NOT
#      self-assign one when DHCP fails -- see the hint this prints.
#   2. Does anything answer mDNS on that link? This is the exact mechanism the
#      app's Devices tab uses, so a silent link explains the app directly.
#   3. Does any candidate address answer GET /health on port 31950? That is the
#      robot's own API, and its reply names the robot.
#
# The robot's link-local address is self-assigned and Opentrons warn it can
# change on reconnect, so nothing here trusts a hard-coded address: --known-ip
# is only tried as one candidate among the ones discovered.
#
# Read-only. It sends pings, an mDNS query and an HTTP GET, and changes no
# settings. No root needed.
#
#   ./find_ot2.sh
#   ./find_ot2.sh --robot-name OT2CEP20210722R13 --known-ip 169.254.51.252
#
# Windows equivalent: find_ot2.ps1

set -u

KNOWN_IP=169.254.51.252          # address this robot has used before; a candidate, not an assumption
ROBOT_NAME=OT2CEP20210722R13     # used for the <name>.local lookup
MDNS_WAIT=6                      # seconds to listen for mDNS replies
PORT=31950

while [ $# -gt 0 ]; do
    case "$1" in
        --known-ip)    KNOWN_IP="$2";   shift 2 ;;
        --robot-name)  ROBOT_NAME="$2"; shift 2 ;;
        --mdns-wait)   MDNS_WAIT="$2";  shift 2 ;;
        -h|--help)     sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

if [ -t 1 ]; then
    C_HEAD=$'\033[36m'; C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_BAD=$'\033[31m'; C_OFF=$'\033[0m'
else
    C_HEAD=''; C_OK=''; C_WARN=''; C_BAD=''; C_OFF=''
fi

section() { printf '\n%s=== %s %s\n' "$C_HEAD" "$1" "$C_OFF"; }
have()    { command -v "$1" >/dev/null 2>&1; }

echo "find_ot2.sh -- $(date -Is)"
echo "host $(uname -srm)  $( [ -r /etc/os-release ] && . /etc/os-release && echo "$PRETTY_NAME" )"

# --- 1. interfaces ----------------------------------------------------------
section 'Network interfaces'

LINK_LOCAL_ADDRS=()
LINK_LOCAL_IFACES=()

while read -r iface addr; do
    [ -n "$iface" ] || continue
    state=$(cat "/sys/class/net/$iface/operstate" 2>/dev/null || echo '?')
    tag=''
    case "$addr" in
        169.254.*) tag="   <-- link-local, this is the robot cable"
                   LINK_LOCAL_ADDRS+=("${addr%%/*}")
                   LINK_LOCAL_IFACES+=("$iface") ;;
    esac
    printf '%-14s %-20s %-8s%s\n' "$iface" "$addr" "$state" "$tag"
done < <(ip -4 -o addr show scope global 2>/dev/null |
         awk '$2 != "lo" { print $2, $4 }')

# Interfaces that have carrier but no IPv4 address at all. On Ubuntu this is the
# normal resting state of a cable with no DHCP server on it -- and it is exactly
# the state in which nothing can reach the robot.
for path in /sys/class/net/*; do
    iface=$(basename "$path")
    [ "$iface" = lo ] && continue
    [ "$(cat "$path/operstate" 2>/dev/null)" = up ] || continue
    if ! ip -4 -o addr show dev "$iface" scope global 2>/dev/null | grep -q .; then
        printf '%-14s %-20s %-8s%s\n' "$iface" '(no IPv4)' 'up' \
            "   <-- up but unaddressed"
    fi
done

if have nmcli; then
    echo
    echo 'NetworkManager:'
    nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status 2>/dev/null |
        awk -F: '$2 != "loopback" { printf "  %-12s %-10s %-14s %s\n", $1, $2, $3, $4 }'
fi

if [ ${#LINK_LOCAL_ADDRS[@]} -eq 0 ]; then
    cat <<EOF

${C_BAD}NO 169.254.x.x ADDRESS ON THIS MACHINE.${C_OFF}
The robot is link-local, so without one there is no route to it and the browser
test cannot work. Ubuntu does not do this for you: NetworkManager's
ipv4.link-local defaults to "auto", which means a link-local address is assigned
only when ipv4.method is itself link-local. A wired connection left on DHCP with
no DHCP server on the cable simply ends up with no IPv4 address -- unlike
Windows, there is no APIPA fallback to wait for. Fix it explicitly:

  nmcli device status                       # find the wired device, e.g. enp0s31f6
  nmcli -g GENERAL.CONNECTION device show enp0s31f6    # its connection name
  sudo nmcli connection modify "Wired connection 1" ipv4.method link-local
  sudo nmcli connection up "Wired connection 1"

then re-run this script. See opentrons-calibration.md, "When the link itself is
the problem".
EOF
fi

# --- 2. mDNS ----------------------------------------------------------------
# Query PTR for _http._tcp.local, the record the Opentrons app itself browses.
# Querying from an ephemeral source port makes responders reply by unicast
# (RFC 6762 s6.7), so a plain UDP socket receives them without joining the group.
section "mDNS query for _http._tcp.local (${MDNS_WAIT}s)"

RESPONDERS=()
AVAHI_IPS=()

# avahi-daemon is Ubuntu's own mDNS responder and is running by default on
# Desktop. It resolves each service to an address, which the raw query below
# cannot, so anything it finds becomes a candidate.
if have avahi-browse; then
    echo 'avahi-browse -rpt _http._tcp:'
    avahi_out=$(timeout "$MDNS_WAIT" avahi-browse -rpt _http._tcp 2>/dev/null |
                awk -F';' '$1 == "=" && $3 == "IPv4" { print $4 "\t" $8 "\t" $9 }' | sort -u)
    if [ -n "$avahi_out" ]; then
        printf '%s\n' "$avahi_out" |
            awk -F'\t' '{ printf "  %-28s %-16s port %s\n", $1, $2, $3 }'
        mapfile -t AVAHI_IPS < <(printf '%s\n' "$avahi_out" | awk -F'\t' '$3 == 31950 { print $2 }')
    else
        echo '  (nothing -- no responder, or avahi-daemon is not running:'
        echo '   check with "systemctl is-active avahi-daemon")'
    fi
else
    echo 'avahi-browse not installed (sudo apt install avahi-utils) -- raw query only.'
fi

if have python3; then
    mapfile -t RESPONDERS < <(
        MDNS_WAIT="$MDNS_WAIT" SOURCES="$(IFS=' '; echo "${LINK_LOCAL_ADDRS[*]:-}")" python3 - <<'PY'
import os, socket, struct, sys, time

def query(name):
    """A minimal DNS query packet: one question, QTYPE PTR, QCLASS IN."""
    pkt = struct.pack('>HHHHHH', 0, 0, 1, 0, 0, 0)
    for label in name.split('.'):
        pkt += bytes([len(label)]) + label.encode('ascii')
    return pkt + b'\x00' + struct.pack('>HH', 12, 1)

wait = float(os.environ.get('MDNS_WAIT', '6'))
sources = [s for s in os.environ.get('SOURCES', '').split() if s] or ['0.0.0.0']
pkt = query('_http._tcp.local')
seen, notes = [], []

for src in sources:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((src, 0))
        # Pin multicast egress to this interface; the route table would
        # otherwise pick whichever interface owns the default multicast route.
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                     socket.inet_aton(src))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        s.settimeout(0.7)
        s.sendto(pkt, ('224.0.0.251', 5353))
        notes.append('queried from %s' % src)
        deadline = time.time() + wait
        while time.time() < deadline:
            try:
                _, addr = s.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError as exc:
                notes.append('  receive failed: %s' % exc)
                break
            if addr[0] not in seen:
                seen.append(addr[0])
                notes.append('  reply from %s' % addr[0])
    except OSError as exc:
        notes.append('  could not query from %s: %s' % (src, exc))
    finally:
        try:
            s.close()
        except Exception:
            pass

print('\n'.join(notes), file=sys.stderr)
for ip in seen:
    print(ip)
PY
    )
else
    echo 'python3 not found -- skipping the raw mDNS query.'
fi

if [ ${#RESPONDERS[@]} -eq 0 ] && [ ${#AVAHI_IPS[@]} -eq 0 ]; then
    cat <<EOF
No mDNS replies. This is what the app sees too -- it browses the same record.
Either nothing is on the cable, or UDP 5353 is not getting through. On Ubuntu
the firewall is usually the least likely cause (ufw is inactive by default);
check it with "sudo ufw status" and, if active, "sudo ufw allow 5353/udp".
EOF
fi

# --- 3. name lookup and HTTP ------------------------------------------------
section 'Candidate addresses'

CANDIDATES=("${RESPONDERS[@]:-}" "${AVAHI_IPS[@]:-}")
[ -n "$KNOWN_IP" ] && CANDIDATES+=("$KNOWN_IP")

# <name>.local through the system resolver. On Ubuntu this needs libnss-mdns
# (installed by default on Desktop, part of the avahi stack) and an "mdns4"
# entry in /etc/nsswitch.conf.
name_ips=$(getent ahostsv4 "$ROBOT_NAME.local" 2>/dev/null | awk '{print $1}' | sort -u)
if [ -n "$name_ips" ]; then
    while read -r ip; do
        printf '%s%s.local resolves to %s%s\n' "$C_OK" "$ROBOT_NAME" "$ip" "$C_OFF"
        CANDIDATES+=("$ip")
    done <<< "$name_ips"
else
    echo "$ROBOT_NAME.local did not resolve (not fatal -- mDNS name lookup is"
    echo "separate from service discovery, and needs libnss-mdns to be installed)."
fi

# Anything the neighbour table already learned on a link-local subnet.
while read -r ip; do
    [ -n "$ip" ] && CANDIDATES+=("$ip")
done < <(ip -4 neigh show 2>/dev/null |
         awk '$1 ~ /^169\.254\./ && $NF != "FAILED" { print $1 }')

mapfile -t CANDIDATES < <(printf '%s\n' "${CANDIDATES[@]:-}" | grep -E '^[0-9]' | sort -u)
if [ ${#CANDIDATES[@]} -eq 0 ]; then
    echo '(none)'
else
    printf '%s\n' "${CANDIDATES[@]}" | sed 's/^/  /'
fi

section "GET /health on port $PORT"

FOUND=()
for ip in "${CANDIDATES[@]:-}"; do
    [ -n "$ip" ] || continue
    if ping -c 1 -W 1 "$ip" >/dev/null 2>&1; then reach=yes; else reach=no; fi
    body=$(curl -s --max-time 5 "http://${ip}:${PORT}/health" 2>/dev/null)
    if [ -n "$body" ]; then
        read -r rname rapi < <(printf '%s' "$body" | python3 -c \
            'import json,sys; d=json.load(sys.stdin); print(d.get("name","?"), d.get("api_version","?"))' \
            2>/dev/null || echo '? ?')
        printf '%s%-18s ping=%-5s HTTP 200  name=%s  api=%s%s\n' \
            "$C_OK" "$ip" "$reach" "$rname" "$rapi" "$C_OFF"
        FOUND+=("$ip")
    else
        printf '%-18s ping=%-5s no answer on %s\n' "$ip" "$reach" "$PORT"
    fi
done
[ ${#CANDIDATES[@]} -eq 0 ] && echo '(nothing to try)'

# --- verdict ----------------------------------------------------------------
section 'Verdict'

if [ ${#FOUND[@]} -gt 0 ]; then
    printf '%sThe robot is reachable at %s. The link is fine.%s\n\n' "$C_OK" "${FOUND[0]}" "$C_OFF"
    cat <<EOF
In the Opentrons OT-2 App: gear icon (bottom-left) -> Advanced ->
Connect to a Robot via IP Address -> Set up connection -> ${FOUND[0]} -> Add.
That bypasses discovery entirely and is remembered.
EOF
elif [ ${#LINK_LOCAL_ADDRS[@]} -gt 0 ]; then
    printf '%sThis machine has a link-local address but nothing answered.%s\n' "$C_WARN" "$C_OFF"
    cat <<EOF
Check, in this order: the robot is powered on and finished booting (give it
~3 minutes); the Ethernet cable is in the robot and in this machine's adapter;
the adapter is in a black USB 2.0 port, not a blue USB 3 one. Then re-run.
EOF
else
    printf '%sThis machine has no link-local address, so nothing above could have%s\n' "$C_WARN" "$C_OFF"
    echo 'worked. Fix that first -- see the message in the interfaces section.'
fi

echo
echo 'Paste this whole output into the GitHub issue if it is still stuck.'
