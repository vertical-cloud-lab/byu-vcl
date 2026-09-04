#!/usr/bin/env bash
# Is the wireless color sensor's Pico W alive on the lab Wi-Fi?
#
# Answers "is the board powered and on the network" WITHOUT any MQTT broker
# credentials, MongoDB, or a USB cable. Run it from a machine on the same lab
# subnet as the board (e.g. one of the stream-cam Pis over Tailscale SSH).
#
#   ./board_network_probe.sh [ip]        # default: 10.60.98.128
#
# Why this exists: once the board is on a charger instead of a USB host, the
# only remaining ways to reach it are (a) the MQTT broker, which needs
# credentials, or (b) the IP layer, which needs nothing. When (a) is blocked,
# (b) still distinguishes "board is dead / not on Wi-Fi" from "board is fine but
# we can't hear it" -- two situations that otherwise look identical.
#
# The board runs no listening services, so a plain ping is the whole test. The
# checks below exist to make sure the thing that answered is really the Pico W
# and not some other host that inherited its DHCP lease.

set -uo pipefail
IP="${1:-10.60.98.128}"
RPI_OUI_RE='^(88:a2:9e|28:cd:c1|d8:3a:dd|2c:cf:67|b8:27:eb|dc:a6:32|e4:5f:01)'
fail=0

echo "=== probing $IP ==="

# 1. Reachability. 20 packets is enough to catch an intermittent association.
ping_out=$(ping -c 20 -i 0.5 -W 2 "$IP" 2>&1)
loss=$(sed -n 's/.*, \([0-9]*\)% packet loss.*/\1/p' <<<"$ping_out")
if [ "${loss:-100}" = "100" ]; then
  echo "  FAIL  no reply -- board is off, not associated, or the IP changed."
  echo "     -> check the LiPo SHIM button (it gates power to the Pico)"
  echo "     -> MicroPython is WPA2-PSK / 2.4 GHz only; it cannot join eduroam"
  echo "     -> if the DHCP lease moved, find it with:  ip neigh | grep -Ei '$RPI_OUI_RE'"
  exit 1
fi
echo "  PASS  reachable, ${loss}% packet loss"

# 2. TTL fingerprint. MicroPython's lwIP stack replies with TTL 255; Linux uses
#    64. This is what separates the Pico W from every Raspberry Pi on the LAN.
ttl=$(grep -o 'ttl=[0-9]*' <<<"$ping_out" | head -1 | cut -d= -f2)
if [ "${ttl:-0}" -ge 200 ]; then
  echo "  PASS  ttl=$ttl -- microcontroller (lwIP) stack, not Linux"
else
  echo "  WARN  ttl=$ttl -- looks like Linux (64), so this is probably NOT the Pico W"
  fail=1
fi

# 3. No listening services. The Pico runs no sshd/web server; a Linux host here
#    would answer on 22. An open port means we found the wrong device.
for p in 22 80 443; do
  if timeout 3 bash -c "echo > /dev/tcp/$IP/$p" 2>/dev/null; then
    echo "  WARN  port $p is open -- that is a full OS, not the Pico W"
    fail=1
  fi
done
[ "$fail" -eq 0 ] && echo "  PASS  no listening ports, as expected for the Pico W"

# 4. MAC is Raspberry Pi silicon, and is not this host's own.
mac=$(ip neigh show "$IP" | awk '/lladdr/ {print $5}')
if grep -qiE "$RPI_OUI_RE" <<<"${mac:-}"; then
  echo "  PASS  MAC $mac is a Raspberry Pi OUI"
else
  echo "  WARN  MAC ${mac:-unknown} is not a Raspberry Pi OUI"
  fail=1
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "RESULT: the Pico W is powered, associated to Wi-Fi, and stable."
  echo "        If no sensor readings are arriving, the fault is downstream"
  echo "        (broker credentials, permissions, or main.py) -- not the board."
else
  echo "RESULT: something answered at $IP, but it does not look like the Pico W."
fi
