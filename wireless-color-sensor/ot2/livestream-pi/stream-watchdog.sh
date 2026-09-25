#!/bin/bash
# stream-watchdog: restart device.service when the RTMP stream stalls.
# Failure mode this catches: ffmpeg/rpicam-vid stay alive but no data
# reaches YouTube (dead socket, wedged camera pipeline), so systemd's
# Restart= never fires. Ground truth = bytes ACKed by the RTMP server.

STATE=/run/stream-watchdog.state
HIST=/var/lib/stream-watchdog/restarts
SERVICE=device.service
STALL_LIMIT=3   # consecutive failed 1-min checks before restarting
GRACE_SEC=180   # leave a freshly (re)started service alone

# optional overrides: HEALTHCHECK_URL (dead-man's-switch ping, Healthchecks.io
# etc.) and MAX_RESTARTS_PER_DAY (watchdog restart budget, rolling 24h)
[ -f /etc/default/stream-watchdog ] && . /etc/default/stream-watchdog
MAX_PER_DAY=${MAX_RESTARTS_PER_DAY:-6}

log() { logger -t stream-watchdog "$1"; echo "$1"; }

systemctl is-active --quiet "$SERVICE" || { rm -f "$STATE"; exit 0; }

started_us=$(systemctl show -p ActiveEnterTimestampMonotonic --value "$SERVICE")
now_us=$(awk '{printf "%d", $1*1000000}' /proc/uptime)
if [ -n "$started_us" ] && [ "$started_us" -gt 0 ] && \
   [ $(( (now_us - started_us) / 1000000 )) -lt "$GRACE_SEC" ]; then
    rm -f "$STATE"
    exit 0
fi

bytes=$(ss -Htin state established '( dport = :1935 )' \
        | grep -oE 'bytes_acked:[0-9]+' | cut -d: -f2 | sort -n | tail -1)

prev_bytes=""; fails=0
[ -f "$STATE" ] && read -r prev_bytes fails < "$STATE"

if [ -n "$bytes" ] && [ "$bytes" != "$prev_bytes" ]; then
    # data is moving (a lower count than last time just means a new socket)
    fails=0
    if [ -n "$HEALTHCHECK_URL" ]; then
        curl -fsS -m 10 --retry 2 -o /dev/null "$HEALTHCHECK_URL" || true
    fi
else
    fails=$((fails + 1))
    log "no RTMP progress (check $fails/$STALL_LIMIT, bytes_acked=${bytes:-no-socket})"
fi

if [ "$fails" -ge "$STALL_LIMIT" ]; then
    # rate limit: at most MAX_PER_DAY watchdog restarts per rolling 24h, so a
    # persistent stall can't spawn an endless stream of throwaway YouTube
    # broadcasts (each restart runs end->create). Survives reboots via /var/lib.
    mkdir -p "$(dirname "$HIST")"
    now=$(date +%s)
    recent=""
    if [ -f "$HIST" ]; then
        while read -r ts; do
            [ -n "$ts" ] && [ $((now - ts)) -lt 86400 ] && recent="$recent$ts
"
        done < "$HIST"
    fi
    printf '%s' "$recent" > "$HIST"
    count=$(grep -c . "$HIST")  # grep -c prints 0 itself when empty
    if [ "$count" -ge "$MAX_PER_DAY" ]; then
        log "stream stalled but restart budget exhausted ($count/$MAX_PER_DAY in 24h) - holding off (fix manually or wait)"
        # keep fails pinned at the limit so we retry once budget frees up
        echo "${bytes:-$prev_bytes} $STALL_LIMIT" > "$STATE"
        exit 0
    fi
    log "stream stalled for $STALL_LIMIT consecutive checks - restarting $SERVICE (restart $((count + 1))/$MAX_PER_DAY in 24h)"
    echo "$now" >> "$HIST"
    rm -f "$STATE"
    systemctl restart "$SERVICE"
    exit 0
fi

echo "${bytes:-$prev_bytes} $fails" > "$STATE"
