#!/bin/bash
# stream-watchdog: restart device.service when the RTMP stream stalls, or
# when systemd has given up on it.
# Failure modes this catches:
# - ffmpeg/rpicam-vid stay alive but no data reaches YouTube (dead socket,
#   wedged camera pipeline), so systemd's Restart= never fires. Ground
#   truth = bytes ACKed by the RTMP server.
# - device.py exits on every start (e.g. DNS is down, so its Lambda call
#   fails), systemd hits StartLimitBurst and marks the unit failed, and
#   nothing else starts it again until the next scheduled reboot.

STATE=/run/stream-watchdog.state
HIST=/var/lib/stream-watchdog/restarts
SERVICE=device.service
STALL_LIMIT=3   # consecutive failed 1-min checks before restarting
GRACE_SEC=180   # leave a freshly (re)started service alone
RETRY_SEC=600   # leave a freshly failed service alone
NET_CHECK=a.rtmp.youtube.com/1935   # must accept a TCP connection before a failed service is retried

# optional overrides: HEALTHCHECK_URL (dead-man's-switch ping, Healthchecks.io
# etc.) and MAX_RESTARTS_PER_DAY (watchdog restart budget, rolling 24h)
[ -f /etc/default/stream-watchdog ] && . /etc/default/stream-watchdog
MAX_PER_DAY=${MAX_RESTARTS_PER_DAY:-6}

log() { logger -t stream-watchdog "$1"; echo "$1"; }

# rate limit: at most MAX_PER_DAY watchdog restarts per rolling 24h, shared by
# both restart paths below, so a persistent fault can't spawn an endless stream
# of throwaway YouTube broadcasts (each restart runs end->create). Survives
# reboots via /var/lib. Sets $now and $count; fails once the budget is spent.
budget_left() {
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
    [ "$count" -lt "$MAX_PER_DAY" ]
}

now_us=$(awk '{printf "%d", $1*1000000}' /proc/uptime)

if systemctl is-failed --quiet "$SERVICE"; then
    # systemd stopped restarting it (StartLimitBurst). A deliberate
    # `systemctl stop` leaves the unit inactive, not failed, so it is left alone.
    rm -f "$STATE"
    failed_us=$(systemctl show -p InactiveEnterTimestampMonotonic --value "$SERVICE")
    if [ -n "$failed_us" ] && [ "$failed_us" -gt 0 ] && \
       [ $(( (now_us - failed_us) / 1000000 )) -lt "$RETRY_SEC" ]; then
        exit 0
    fi
    # retrying before the network is back would only fail again and spend budget
    if ! timeout 10 bash -c "exec 3<>/dev/tcp/$NET_CHECK" 2>/dev/null; then
        log "$SERVICE has failed and $NET_CHECK is unreachable - waiting for the network"
        exit 0
    fi
    if ! budget_left; then
        log "$SERVICE has failed but restart budget exhausted ($count/$MAX_PER_DAY in 24h) - holding off (fix manually or wait)"
        exit 0
    fi
    log "$SERVICE has failed and $NET_CHECK is reachable - starting it (restart $((count + 1))/$MAX_PER_DAY in 24h)"
    echo "$now" >> "$HIST"
    systemctl reset-failed "$SERVICE"   # also zeroes the start-limit counter
    systemctl start "$SERVICE"
    exit 0
fi

systemctl is-active --quiet "$SERVICE" || { rm -f "$STATE"; exit 0; }

started_us=$(systemctl show -p ActiveEnterTimestampMonotonic --value "$SERVICE")
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
    if ! budget_left; then
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
