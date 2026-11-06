#!/bin/bash
# stream-reboot: reboot the Pi at 05:00, 13:00 and 21:00 local, as the other
# stream-cam Pis do (theirs is a root crontab). Every boot starts a fresh
# broadcast, so none runs past YouTube's 12 h archive limit, and the Pi itself
# starts clean.
#
# This Pi is also the OT-2's only link, and jobs that drive the robot run on it,
# so the reboot holds off while
#   - the robot has a maintenance run (something here is moving it: ot2ctl.py,
#     a scan),
#   - the robot's current protocol run has not finished,
#   - something other than the stream holds the camera (a preview or a still), or
#   - a process holds a shutdown "block" inhibitor. To keep the Pi up for any
#     other long job, start it as
#       systemd-inhibit --what=shutdown --why="<what it is>" <command>
# It checks again every 10 min. If it is still held off after 3 h (an 11 h
# broadcast by then), it restarts only the stream, which also starts a fresh
# broadcast, and leaves the reboot for the next slot.
#
# A slot less than an hour after boot is skipped: the broadcast is new anyway,
# and a Pi 5 with no RTC battery boots with the clock it had at shutdown, so the
# first NTP correction after a long power cut makes a slot that passed while it
# was off fire at once.
#
#   stream-reboot.sh --check   # say what it would do now, change nothing

ROBOT=http://169.254.51.252:31950
SERVICE=device.service
RECHECK_SEC=600
GIVE_UP_SEC=10800
MIN_UPTIME_SEC=3600
HIST=/var/lib/stream-reboot/history   # journald on this Pi is volatile; this survives reboots

log() {
    logger -t stream-reboot "$1"; echo "$1"
    mkdir -p "${HIST%/*}"
    echo "$(date -u +%FT%TZ) $1" >> "$HIST"
    tail -n 300 "$HIST" > "$HIST.tmp" && mv "$HIST.tmp" "$HIST"
}

# Print why the reboot should wait, or nothing. A robot that doesn't answer
# (off, or the link is down) is nothing to wait for.
held_by() {
    python3 - "$ROBOT" <<'EOF'
import json, sys, urllib.error, urllib.request

def get(path):
    req = urllib.request.Request(sys.argv[1] + path, headers={"Opentrons-Version": "3"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)

try:
    get("/maintenance_runs/current_run")
    print("the OT-2 has a maintenance run")
    sys.exit()
except urllib.error.HTTPError:
    pass  # 404: there is none
except Exception:
    sys.exit()
try:
    href = get("/runs?pageLength=1").get("links", {}).get("current", {}).get("href")
    if href:
        status = get(href)["data"]["status"]
        if status not in ("idle", "succeeded", "failed", "stopped"):
            print(f"the OT-2's protocol run is {status}")
except Exception:
    pass
EOF
    if ! systemctl is-active --quiet "$SERVICE" && fuser -s /dev/media* /dev/video* 2>/dev/null; then
        echo "the camera is in use outside $SERVICE"
        return
    fi
    if systemd-inhibit --list --no-legend --no-pager 2>/dev/null \
        | awk '$NF == "block" && /shutdown/ { found = 1 } END { exit !found }'; then
        echo "a shutdown inhibitor is held (systemd-inhibit --list)"
    fi
}

up=$(cut -d. -f1 /proc/uptime)
reason=$(held_by)

if [ "${1:-}" = "--check" ]; then
    if [ "$up" -lt "$MIN_UPTIME_SEC" ]; then
        echo "would skip this slot: up only $((up / 60)) min"
    elif [ -n "$reason" ]; then
        echo "would hold off: $reason"
    else
        echo "would reboot now"
    fi
    exit 0
fi

if [ "$up" -lt "$MIN_UPTIME_SEC" ]; then
    log "up only $((up / 60)) min, so the broadcast is already fresh - skipping this slot"
    exit 0
fi

waited=0
while [ -n "$reason" ]; do
    if [ "$waited" -ge "$GIVE_UP_SEC" ]; then
        log "still held off after $((waited / 3600)) h ($reason) - restarting only $SERVICE for a fresh broadcast; the reboot waits for the next slot"
        systemctl try-restart "$SERVICE"
        exit 0
    fi
    log "holding off the reboot: $reason - checking again in $((RECHECK_SEC / 60)) min"
    sleep "$RECHECK_SEC"
    waited=$((waited + RECHECK_SEC))
    reason=$(held_by)
done

health=$(curl -s -m 10 -o /dev/null -w '%{http_code}' -H 'Opentrons-Version: 3' "$ROBOT/health")
log "scheduled reboot (OT-2 /health before it: $health)"
systemctl reboot
