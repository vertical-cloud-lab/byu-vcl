#!/bin/bash
# Runner side of a Remote Desktop session to the EZstat Pro's Windows 7 PC
# that can send keystrokes and clicks, made from the CubXL Pi (#231). See
# pi_drive.sh for the Pi side. Needs CUBXL_PI_USERNAME, CUBXL_PI_HOSTNAME,
# POTENTIOSTAT_PC_USERNAME and POTENTIOSTAT_PC_PASSWORD in the environment.
#
#   drive.sh start [MAX_S]      copy the helper to the Pi and connect
#                               (MAX_S: hard stop, default 1800 s)
#   drive.sh shot NAME          screenshot to $state/png/NAME.png (raw, unredacted)
#   drive.sh x ARGS...          xdotool ARGS on the session, e.g.
#                               `x key alt+f`, `x mousemove 40 30 click 1`
#   drive.sh type < TEXT        type TEXT into the session
#   drive.sh seq NAME < SCRIPT  run a pi_seq.sh step script; frames land in
#                               $state/png/NAME-<shot>.png
#   drive.sh stop               disconnect (kill xfreerdp3) and clean up
#
# The credentials go to the Pi as xfreerdp3 /args-from:stdin lines, built
# with the printf builtin, so they never appear in argv on either machine.
# Output is redacted (PC username and password, Pi hostname) before display.
# Raw PNGs stay under $state; redact with redact_png.py before committing.
# PNG conversion needs numpy and Pillow for $PY (default python3).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
state=${RDP_DRIVE_STATE:-/tmp/ezmap}
mkdir -p "$state/raw" "$state/png"

ssh_pi() {
    ssh -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$state/known_hosts" \
        -o BatchMode=yes -o ConnectTimeout=25 -o ServerAliveInterval=15 \
        "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME" "$@"
}

redact() {
    python3 -c '
import os, re, sys
subs = [("POTENTIOSTAT_PC_PASSWORD", "[PASSWORD]"),
        ("POTENTIOSTAT_PC_USERNAME", "[USERNAME]"),
        ("CUBXL_PI_HOSTNAME", "<pi-host>")]
pats = [(re.compile(re.escape(os.environ[k]), re.I), tag)
        for k, tag in subs if os.environ.get(k)]
for line in sys.stdin:
    for pat, tag in pats:
        line = pat.sub(tag, line)
    sys.stdout.write(line)
'
}

case "${1:-}" in
start)
    max_s=${2:-1800}
    d=$(ssh_pi 'mktemp -d /dev/shm/ezmap.XXXXXX')
    ssh_pi "cat > $d/pi_drive.sh" < "$here/pi_drive.sh"
    echo "$d" > "$state/pi_dir"
    printf '%s\n' \
        /v:192.168.231.10 \
        "/u:${POTENTIOSTAT_PC_USERNAME}" \
        "/p:${POTENTIOSTAT_PC_PASSWORD}" \
        /sec:nla \
        /cert:tofu \
        /tls:seclevel:0 \
        /size:1280x800 \
        /kbd:layout:0x409 \
        -clipboard \
        /log-level:WARN |
        ssh_pi "bash $d/pi_drive.sh start $d $max_s" 2>&1 | redact
    ;;
shot)
    name=$2
    d=$(cat "$state/pi_dir")
    rm -rf "$state/raw/$name"
    mkdir -p "$state/raw/$name"
    ssh_pi "bash $d/pi_drive.sh shot $d" | tar -C "$state/raw/$name" -xf -
    "${PY:-python3}" -I "$here/xwd_to_png.py" "$state/raw/$name/frame.xwd.gz" "$state/png/$name.png"
    rm -f "$state/raw/$name/frame.xwd.gz"
    tr '\n' ' ' < "$state/raw/$name/status"
    echo "-> $state/png/$name.png"
    ;;
x)
    shift
    d=$(cat "$state/pi_dir")
    ssh_pi "bash $d/pi_drive.sh x $d $*" 2>&1 | redact
    ;;
type)
    d=$(cat "$state/pi_dir")
    ssh_pi "bash $d/pi_drive.sh type $d" 2>&1 | redact
    ;;
seq)
    name=$2
    d=$(cat "$state/pi_dir")
    rm -rf "$state/raw/$name"
    mkdir -p "$state/raw/$name"
    ssh_pi "cat > $d/pi_seq.sh" < "$here/pi_seq.sh"
    ssh_pi "bash $d/pi_seq.sh $d" | tar -C "$state/raw/$name" -xf -
    for f in "$state/raw/$name"/*.xwd.gz; do
        [ -e "$f" ] || continue
        b=$(basename "$f" .xwd.gz)
        "${PY:-python3}" -I "$here/xwd_to_png.py" "$f" "$state/png/$name-$b.png"
        rm -f "$f"
    done
    cat "$state/raw/$name/index" 2>/dev/null
    ;;
stop)
    d=$(cat "$state/pi_dir")
    ssh_pi "bash $d/pi_drive.sh stop $d" 2>&1 | redact
    ;;
*)
    sed -n '2,20p' "$0"
    exit 2
    ;;
esac
