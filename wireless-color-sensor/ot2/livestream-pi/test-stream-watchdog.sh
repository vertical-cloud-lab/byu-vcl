#!/bin/bash
# Exercise stream-watchdog.sh against a throwaway systemd unit, never the real
# device.service. Needs root and systemd, and takes about a minute. The unit
# lives in /run/systemd/system and everything else in a temp dir, all removed
# on exit, so it is safe to run on the livestream Pi itself; its log lines go
# under their own tag, stream-watchdog-selftest.
#
#   sudo ./test-stream-watchdog.sh [path/to/stream-watchdog.sh]

set -u
[ "$(id -u)" = 0 ] || { echo "run as root: it creates a systemd unit" >&2; exit 2; }

SRC=${1:-"$(dirname "$0")/stream-watchdog.sh"}
UNIT=stream-watchdog-selftest.service
UNIT_FILE=/run/systemd/system/$UNIT
TMP=$(mktemp -d)
NET_PORT=18935   # stands in for a.rtmp.youtube.com:1935; "network up" = a listener here
LISTENER=
failures=0

# shellcheck disable=SC2317  # called by the trap
cleanup() {
    systemctl stop "$UNIT" 2>/dev/null
    systemctl reset-failed "$UNIT" 2>/dev/null
    rm -f "$UNIT_FILE"
    systemctl daemon-reload
    [ -n "$LISTENER" ] && kill "$LISTENER" 2>/dev/null
    rm -rf "$TMP"
}
trap cleanup EXIT

# The watchdog under test, pointed at the throwaway unit and scratch state,
# with its waits shortened. Its stall check watches a port nothing uses.
sed -e "s|^SERVICE=.*|SERVICE=$UNIT|" \
    -e "s|^STATE=.*|STATE=$TMP/state|" \
    -e "s|^HIST=.*|HIST=$TMP/restarts|" \
    -e "s|^GRACE_SEC=[0-9]*|GRACE_SEC=2|" \
    -e "s|^RETRY_SEC=[0-9]*|RETRY_SEC=5|" \
    -e "s|^NET_CHECK=[^ ]*|NET_CHECK=127.0.0.1/$NET_PORT|" \
    -e "s|/etc/default/stream-watchdog|$TMP/default|g" \
    -e "s|logger -t stream-watchdog |logger -t stream-watchdog-selftest |" \
    -e "s|dport = :1935|dport = :9|" \
    "$SRC" > "$TMP/wd.sh"
# refuse to run if any substitution missed, rather than touch device.service
for want in "^SERVICE=$UNIT\$" "^STATE=$TMP/state\$" "^HIST=$TMP/restarts\$" \
            "^RETRY_SEC=5 " "^NET_CHECK=127.0.0.1/$NET_PORT " "stream-watchdog-selftest" "dport = :9 "; do
    grep -q -- "$want" "$TMP/wd.sh" || { echo "could not rewrite $SRC ($want)" >&2; exit 2; }
done
if grep -v '^[[:space:]]*#' "$TMP/wd.sh" | grep -q 'device\.service'; then
    echo "$SRC still names device.service outside a comment" >&2; exit 2
fi
# a copy whose network check can only time out, for the last test
sed "s|^NET_CHECK=[^ ]*|NET_CHECK=192.0.2.1/1935|" "$TMP/wd.sh" > "$TMP/wd-blackhole.sh"

# The fake device.py: runs while $TMP/ok exists, otherwise exits 1 at once.
# Same start limit as device.service.
cat > "$UNIT_FILE" <<EOF
[Unit]
Description=stream-watchdog self-test (safe to delete)
StartLimitIntervalSec=3600
StartLimitBurst=3

[Service]
ExecStart=/bin/sh -c 'test -f $TMP/ok && exec sleep infinity; exit 1'
Restart=always
RestartSec=1
EOF
systemctl daemon-reload

wd() { unset HEALTHCHECK_URL MAX_RESTARTS_PER_DAY; bash "${1:-$TMP/wd.sh}"; }
state() { systemctl show -p ActiveState --value "$UNIT"; }
restarts() { local n; n=$(grep -c . "$TMP/restarts" 2>/dev/null); echo "${n:-0}"; }
wait_for() { # wait_for <ActiveState> [seconds]
    for _ in $(seq "${2:-30}"); do [ "$(state)" = "$1" ] && return 0; sleep 1; done
    return 1
}
check() { # check <description> <command...>
    local what=$1; shift
    if "$@"; then echo "  PASS  $what"; else echo "  FAIL  $what"; failures=$((failures + 1)); fi
}
net_up() {
    python3 -c 'import socket, sys, time
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", int(sys.argv[1]))); s.listen(8); time.sleep(600)' "$NET_PORT" &
    LISTENER=$!
    sleep 1
}
fail_unit() { # stop, clear, and start it with no ok file, so it burns its 3 starts
    systemctl stop "$UNIT"; systemctl reset-failed "$UNIT" 2>/dev/null
    rm -f "$TMP/ok"
    systemctl start "$UNIT"
    wait_for failed 30
}

echo "1. a service that exits at every start"
fail_unit
check "systemd marks it failed after 3 starts" [ "$(state)" = failed ]

echo "2. freshly failed"
out=$(wd)
check "left alone, nothing logged" [ -z "$out" ]
check "still failed, no restart spent" [ "$(state)/$(restarts)" = failed/0 ]

echo "3. RETRY_SEC later, network still down"
sleep 6
out=$(wd)
check "logs that it is waiting for the network" grep -q 'unreachable - waiting for the network' <<<"$out"
check "still failed, no restart spent" [ "$(state)/$(restarts)" = failed/0 ]

echo "4. network back"
touch "$TMP/ok"; net_up
out=$(wd)
check "starts it, as restart 1/6" grep -q 'reachable - starting it (restart 1/6 in 24h)' <<<"$out"
check "running" wait_for active 10
check "one restart spent" [ "$(restarts)" = 1 ]

echo "5. stall path, unchanged apart from sharing the budget"
sleep 3
echo "5000 0" > "$TMP/state"   # as if the stream had been sending, then stopped
wd >/dev/null; wd >/dev/null; out=$(wd)
check "third missed check restarts it, as restart 2/6" grep -q 'stalled for 3 consecutive checks - restarting .* (restart 2/6 in 24h)' <<<"$out"
check "running" wait_for active 10
check "two restarts spent" [ "$(restarts)" = 2 ]

echo "6. budget spent"
fail_unit
now=$(date +%s); printf '%s\n' "$now" "$now" "$now" "$now" "$now" "$now" > "$TMP/restarts"
sleep 6; touch "$TMP/ok"
out=$(wd)
check "holds off" grep -q 'has failed but restart budget exhausted (6/6 in 24h)' <<<"$out"
check "still failed, no seventh restart" [ "$(state)/$(restarts)" = failed/6 ]

echo "7. restarts older than 24 h stop counting"
old=$((now - 90000)); printf '%s\n' "$old" "$old" "$old" "$old" "$old" "$old" > "$TMP/restarts"
out=$(wd)
check "starts it, as restart 1/6" grep -q 'starting it (restart 1/6 in 24h)' <<<"$out"
check "running" wait_for active 10
check "old entries pruned" [ "$(restarts)" = 1 ]
echo "7b. stall with the budget spent"
printf '%s\n' "$now" "$now" "$now" "$now" "$now" "$now" > "$TMP/restarts"
sleep 3
echo "5000 0" > "$TMP/state"
wd >/dev/null; wd >/dev/null; out=$(wd)
check "holds off" grep -q 'stream stalled but restart budget exhausted (6/6 in 24h)' <<<"$out"
check "failure count pinned at the limit" grep -qx '5000 3' "$TMP/state"
check "still running, no seventh restart" [ "$(state)/$(restarts)" = active/6 ]

echo "8. a deliberate stop"
systemctl stop "$UNIT"; : > "$TMP/restarts"
sleep 6
out=$(wd)
check "left alone, nothing logged" [ -z "$out" ]
check "still inactive, no restart spent" [ "$(state)/$(restarts)" = inactive/0 ]

echo "9. a network check that can only time out"
fail_unit
sleep 6
t0=$(date +%s); out=$(wd "$TMP/wd-blackhole.sh"); t1=$(date +%s)
check "gives up and waits" grep -q 'unreachable - waiting for the network' <<<"$out"
check "within 15 s (took $((t1 - t0)) s)" [ $((t1 - t0)) -le 15 ]
check "still failed, no restart spent" [ "$(state)/$(restarts)" = failed/0 ]

echo
[ "$failures" = 0 ] && echo "all passed" || echo "$failures failed"
exit $(( failures > 0 ))
