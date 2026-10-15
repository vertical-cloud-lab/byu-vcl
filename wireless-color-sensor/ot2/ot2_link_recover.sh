#!/usr/bin/env bash
# Recover the USB-Ethernet link between the stream-cam Pi and the OT-2.
#
# Run this ON the Pi that holds the adapter (RPI_STREAM_CAM_HOSTNAME as of
# 2026-09-11), not on a runner. The robot answers only on a link-local address,
# so nothing off that Pi can reach it.
#
#     sudo ./ot2_link_recover.sh            # check, and repair if the robot is silent
#     ./ot2_link_recover.sh --check         # check only; touches nothing, needs no root
#
# ---------------------------------------------------------------------------
# The failure
# ---------------------------------------------------------------------------
#
#     r8152 4-1:1.0 eth1: Stop submitting intr, status -71
#
# -71 is -EPROTO on the adapter's USB interrupt endpoint. Once it fires the
# driver stops polling that endpoint, so /sys/class/net/eth1/carrier freezes at
# whatever it last saw -- normally 1. That is the trap this whole file exists
# for: the interface reports carrier=1, operstate=up and keeps its 169.254/16
# address while not a single packet has crossed it for hours. On 2026-09-10 it
# fired at 15:47 local and the robot was unreachable until past midnight, with
# every cheap indicator still reading healthy.
#
#   *** Judge this link by a ping to the robot. Never by carrier. ***
#
# `ethtool` is no better: after -71 its register reads are garbage. It reported
# "Supported link modes: 10baseT/Half 10baseT/Full" for a gigabit adapter and
# "Link detected: yes" for a link that carried nothing.
#
# ---------------------------------------------------------------------------
# What does NOT work
# ---------------------------------------------------------------------------
#
# `ip link set eth1 down/up`. It issues a USB port reset the wedged adapter
# cannot complete; the driver then reads chip version 0x0000, refuses to bind,
# falls back to USB configuration 2 (CDC) and eth1 disappears altogether:
#
#     r8152-cfgselector 4-1: Unknown version 0x0000
#
# Recovering from that needs everything below anyway, so the down/up only costs
# time and makes the symptom look worse than it is.
#
# ---------------------------------------------------------------------------
# What does work, in the order this script tries it
# ---------------------------------------------------------------------------
#
# 0. Set the NO_LPM usbcore quirk for 0bda:8153 before re-enumerating. The boot
#    log carries `usb 4-1: enable of device-initiated U2 failed.`, and USB 3
#    link power management is the usual source of -EPROTO on this chip.
#    Runtime-only: /sys/module/usbcore/parameters/quirks does not survive a
#    reboot. See the README for making it permanent.
# 1. Unconfigure and reconfigure the USB device. Forces a port reset and a clean
#    driver re-probe. Worked twice on 2026-09-10, then stopped working once the
#    adapter had degraded to `Unknown version 0x0000` on every attempt.
# 2. Cut and restore port power with uhubctl. This is the one that brought it
#    back after five failed config cycles -- it is the closest thing to pulling
#    the plug that software can do.
#
# If all three fail the remaining causes are physical and are printed.

set -uo pipefail

VENDOR=0bda
PRODUCT=8153
ROBOT=${OT2_LINK_ADDR:-169.254.51.252}
PORT=${OT2_LINK_PORT:-31950}
CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

UHUBCTL=$(command -v uhubctl || ls /usr/sbin/uhubctl 2>/dev/null | head -1)

robot_answers() {
    ping -c 3 -W 2 "$ROBOT" >/dev/null 2>&1 || return 1
    curl -s -m 10 -o /dev/null -w '%{http_code}' \
        -H 'Opentrons-Version: 3' "http://$ROBOT:$PORT/health" 2>/dev/null \
        | grep -q 200
}

# Locate the adapter's USB device directory, e.g. /sys/bus/usb/devices/4-1.
find_usb_path() {
    local d
    for d in /sys/bus/usb/devices/*; do
        [ -e "$d/idVendor" ] || continue
        [ "$(cat "$d/idVendor")" = "$VENDOR" ] || continue
        [ "$(cat "$d/idProduct")" = "$PRODUCT" ] || continue
        echo "$d"
        return 0
    done
    return 1
}

# The net interface belonging to that USB device, whatever the kernel named it.
usb_iface() {
    local n
    [ -n "${USB_PATH:-}" ] || return 0
    for n in "$USB_PATH"/*/net/*; do
        [ -e "$n" ] || continue
        basename "$n"
        return 0
    done
}

report() {
    local iface addr
    USB_PATH=$(find_usb_path) || USB_PATH=""
    iface=$(usb_iface)
    if [ -n "$iface" ]; then
        addr=$(ip -4 -br addr show "$iface" 2>/dev/null | awk '{print $3}')
        echo "  interface : $iface  carrier=$(cat "/sys/class/net/$iface/carrier" 2>/dev/null)" \
             "operstate=$(cat "/sys/class/net/$iface/operstate" 2>/dev/null)  addr=${addr:-none}"
    elif [ -n "$USB_PATH" ]; then
        echo "  interface : ABSENT -- adapter enumerates but the r8152 driver will not bind"
    else
        echo "  interface : ABSENT -- adapter not enumerated at all"
    fi
    echo "  usb path  : ${USB_PATH:-not found}  speed=$(cat "${USB_PATH:-/nonexistent}/speed" 2>/dev/null)"
}

# Wait for the interface to come back and pick up its link-local address.
settle() {
    local iface addr
    for _ in $(seq 1 12); do
        sleep 5
        USB_PATH=$(find_usb_path) || USB_PATH=""
        iface=$(usb_iface)
        [ -n "$iface" ] || continue
        addr=$(ip -4 -br addr show "$iface" 2>/dev/null | awk '{print $3}')
        [ -n "$addr" ] && return 0
    done
    return 1
}

USB_PATH=$(find_usb_path) || USB_PATH=""

echo "== before =="
report
if robot_answers; then
    echo "  robot     : ANSWERS at $ROBOT:$PORT -- nothing to do"
    exit 0
fi
echo "  robot     : SILENT at $ROBOT:$PORT"

if [ "$CHECK_ONLY" = 1 ]; then
    echo "(--check given; stopping without touching the adapter)"
    exit 1
fi
if [ "$(id -u)" != 0 ]; then
    echo "Repair needs root. Re-run with sudo."
    exit 3
fi

echo
echo "== stage 0: NO_LPM quirk for $VENDOR:$PRODUCT =="
echo "$VENDOR:$PRODUCT:k" > /sys/module/usbcore/parameters/quirks 2>/dev/null
echo "  usbcore quirks = $(cat /sys/module/usbcore/parameters/quirks)"

if [ -n "$USB_PATH" ]; then
    echo
    echo "== stage 1: USB configuration cycle on $(basename "$USB_PATH") =="
    echo 0 > "$USB_PATH/bConfigurationValue" 2>/dev/null
    sleep 5
    echo 1 > "$USB_PATH/bConfigurationValue" 2>/dev/null
    echo on > "$USB_PATH/power/control" 2>/dev/null
    settle
    report
    if robot_answers; then
        echo "  robot     : ANSWERS -- recovered by the config cycle"
        exit 0
    fi
    echo "  robot     : still silent"
fi

if [ -n "$UHUBCTL" ]; then
    # Find which root hub the adapter sits on: /sys/bus/usb/devices/4-1 -> hub 4.
    HUB=$(basename "${USB_PATH:-4-1}" | cut -d- -f1)
    echo
    echo "== stage 2: port power cycle, uhubctl hub $HUB port 1 =="
    echo "  (uhubctl also switches the USB 2.0 companion port; that is expected)"
    "$UHUBCTL" -l "$HUB" -p 1 -a cycle -d 6 2>&1 | tail -3
    sleep 10
    "$UHUBCTL" -l "$HUB" -p 1 -a on >/dev/null 2>&1
    settle
    report
    if robot_answers; then
        echo "  robot     : ANSWERS -- recovered by the power cycle"
        curl -s -m 10 -H 'Opentrons-Version: 3' "http://$ROBOT:$PORT/health" | head -c 200
        echo
        exit 0
    fi
    echo "  robot     : still silent"
else
    echo
    echo "== stage 2 skipped: uhubctl not installed (sudo apt-get install -y uhubctl) =="
fi

echo
echo "Software has done what it can. Remaining causes are physical:"
echo "  - the adapter's SuperSpeed link is marginal. -EPROTO on a USB 3 port is"
echo "    the classic RTL8153 symptom; moving the adapter to one of the Pi's"
echo "    USB 2.0 ports (the black ones) forces 480 Mbps and usually ends it."
echo "    480 Mbps is ~48x what this link carries, so nothing is lost."
echo "  - unseat and reseat the adapter, and the ethernet cable at both ends"
echo "  - confirm the OT-2 is powered on"
echo
echo "Last adapter messages:"
dmesg -T 2>/dev/null | grep -iE 'r8152|eth[0-9]' | tail -8
exit 1
