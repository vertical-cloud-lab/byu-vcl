#!/bin/bash
# Runner side of a look-only Remote Desktop session to the EZstat Pro's
# Windows 7 PC, made from the CubXL Pi (#231). See pi_rdp_look.sh for the Pi
# side. Needs CUBXL_PI_USERNAME, CUBXL_PI_HOSTNAME, POTENTIOSTAT_PC_USERNAME
# and POTENTIOSTAT_PC_PASSWORD in the environment.
#
#   rdp_look.sh start                 copy the helper to the Pi and connect
#   rdp_look.sh peek OUTDIR           current frame, FreeRDP log and status
#   rdp_look.sh shots OUTDIR N STEP   N frames STEP seconds apart
#   rdp_look.sh stop                  disconnect (kill xfreerdp3) and clean up
#
# The credentials go to the Pi as xfreerdp3 /args-from:stdin lines, built
# with the printf builtin, so they never appear in argv on either machine.
# Logs are redacted (PC username and password, Pi hostname) before display.
# Frames are XWD files: convert them with xwd_to_png.py and redact the
# username with redact_png.py before committing anything.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
state=${RDP_LOOK_STATE:-/tmp/ezrdp}
mkdir -p "$state"

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

fetch() {  # fetch OUTDIR SUBCOMMAND [ARGS...]: run a tar-producing subcommand, unpack
    local out=$1
    shift
    local d
    d=$(cat "$state/pi_dir")
    mkdir -p "$out"
    ssh_pi "bash $d/pi_rdp_look.sh $* " | tar -C "$out" -xf -
    if [ -f "$out/rdp.log" ]; then
        redact < "$out/rdp.log" > "$out/rdp.redacted.log"
        rm "$out/rdp.log"
    fi
}

case "${1:-}" in
start)
    d=$(ssh_pi 'mktemp -d /dev/shm/ezrdp.XXXXXX')
    ssh_pi "cat > $d/pi_rdp_look.sh" < "$here/pi_rdp_look.sh"
    echo "$d" > "$state/pi_dir"
    printf '%s\n' \
        /v:192.168.231.10 \
        "/u:${POTENTIOSTAT_PC_USERNAME}" \
        "/p:${POTENTIOSTAT_PC_PASSWORD}" \
        /sec:nla \
        /cert:tofu \
        /tls:seclevel:0 \
        /size:1280x800 \
        -clipboard \
        -mouse-motion \
        /log-level:INFO |
        ssh_pi "bash $d/pi_rdp_look.sh start $d" 2>&1 | redact
    ;;
peek)
    fetch "$2" peek "$(cat "$state/pi_dir")"
    cat "$2/status"
    ;;
shots)
    fetch "$2" shots "$(cat "$state/pi_dir")" "$3" "$4"
    cat "$2/index"
    ;;
stop)
    d=$(cat "$state/pi_dir")
    ssh_pi "bash $d/pi_rdp_look.sh stop $d" 2>&1 | redact
    ;;
*)
    sed -n '2,20p' "$0"
    exit 2
    ;;
esac
