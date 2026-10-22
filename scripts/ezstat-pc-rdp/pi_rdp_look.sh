#!/bin/bash
# Look-only Remote Desktop session to the EZstat Pro's Windows 7 PC (#231),
# run on the CubXL Pi, which is cabled to the PC. Copied to a mktemp dir in
# /dev/shm by rdp_look.sh on the runner; each subcommand is its own SSH call.
#
#   pi_rdp_look.sh start DIR < ARGS   ARGS: one xfreerdp3 argument per line,
#                                     credentials included. Held in memory
#                                     only, never in argv or on disk.
#   pi_rdp_look.sh peek DIR           tar on stdout: frame.xwd.gz, rdp.log, status
#   pi_rdp_look.sh shots DIR N STEP   tar on stdout: N frames STEP s apart,
#                                     identical consecutive frames dropped
#   pi_rdp_look.sh keys DIR < SCRIPT  send keystrokes into the session with
#                                     pi_rdp_keys.py (keyboard only; see there)
#   pi_rdp_look.sh stop DIR           kill xfreerdp3 (a disconnect, never a
#                                     log-off), report, delete DIR
#
# Screenshots come from Xvfb's -fbdir framebuffer file (XWD format), so
# nothing has to be installed beyond freerdp3-x11 and xvfb. The XWD header
# holds the Pi's hostname: convert to PNG before publishing, never commit it.
#
# Safety net: the whole session is wrapped in `timeout`, so if nobody comes
# back to run `stop`, xfreerdp3 and Xvfb are killed after SESSION_MAX_S and
# DIR is deleted.
set -u
cmd=$1
dir=$2
umask 077
W=1280
H=800
SESSION_MAX_S=${SESSION_MAX_S:-360}

case "$cmd" in
start)
    IFS= read -r -d '' args || true
    mkdir -p "$dir/fb"
    date +%s > "$dir/t0"
    printf '%s' "$args" | setsid -f bash "$dir/pi_rdp_look.sh" supervise "$dir" \
        > "$dir/supervise.log" 2>&1
    unset args
    for _ in $(seq 1 60); do
        [ -s "$dir/rdp.pid" ] && [ -e "$dir/fb/Xvfb_screen0" ] && break
        sleep 0.25
    done
    echo "rdp pid: $(cat "$dir/rdp.pid" 2>/dev/null || echo none)"
    echo "framebuffer: $([ -e "$dir/fb/Xvfb_screen0" ] && echo ok || echo missing)"
    ;;

supervise)
    # stdin is the argument stream: keep it on fd 7 for xfreerdp3 alone.
    # (xvfb-run uses fd 3 itself and closes it for the command.)
    exec 7<&0 0</dev/null
    timeout -k 10 "$SESSION_MAX_S" xvfb-run -a \
        -s "-screen 0 ${W}x${H}x24 -fbdir $dir/fb -noreset" \
        bash "$dir/pi_rdp_look.sh" inner "$dir"
    echo "xvfb-run exit $?"
    exec 7<&-
    [ -e "$dir/stop-requested" ] || rm -rf "$dir"
    ;;

inner)
    # For pi_rdp_keys.py: xvfb-run picks the display and its auth file.
    echo "$DISPLAY" > "$dir/display"
    echo "$XAUTHORITY" > "$dir/xauth"
    xfreerdp3 /args-from:stdin <&7 7<&- > "$dir/rdp.log" 2>&1 &
    pid=$!
    exec 7<&-
    echo "$pid" > "$dir/rdp.pid"
    wait "$pid"
    echo "xfreerdp3 exit $?" >> "$dir/rdp.log"
    ;;

peek)
    t=$(mktemp -d "$dir/peek.XXXXXX")
    cp "$dir/fb/Xvfb_screen0" "$t/frame.xwd" && gzip -1 "$t/frame.xwd"
    pid=$(cat "$dir/rdp.pid" 2>/dev/null)
    {
        echo "utc $(date -u +%FT%TZ)"
        echo "elapsed_s $(( $(date +%s) - $(cat "$dir/t0") ))"
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "xfreerdp3 running"
        else
            echo "xfreerdp3 not-running"
        fi
    } > "$t/status"
    cp "$dir/rdp.log" "$t/rdp.log" 2>/dev/null
    tar -C "$t" -cf - .
    rm -rf "$t"
    ;;

shots)
    n=$3
    step=$4
    t=$(mktemp -d "$dir/shots.XXXXXX")
    prev=""
    for i in $(seq 0 $((n - 1))); do
        ts=$(date -u +%FT%T.%3NZ)
        cp "$dir/fb/Xvfb_screen0" "$t/cur.xwd"
        if [ -n "$prev" ] && cmp -s "$t/cur.xwd" "$t/prev.xwd"; then
            echo "$i $ts $prev" >> "$t/index"
        else
            gzip -1 -c "$t/cur.xwd" > "$t/f$i.xwd.gz"
            mv "$t/cur.xwd" "$t/prev.xwd"
            prev="f$i"
            echo "$i $ts $prev" >> "$t/index"
        fi
        [ "$i" -lt $((n - 1)) ] && sleep "$step"
    done
    rm -f "$t/cur.xwd" "$t/prev.xwd"
    tar -C "$t" -cf - .
    rm -rf "$t"
    ;;

keys)
    python3 -I "$dir/pi_rdp_keys.py" "$dir"
    ;;

stop)
    touch "$dir/stop-requested"
    pid=$(cat "$dir/rdp.pid" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill -TERM "$pid"
        for _ in $(seq 1 40); do kill -0 "$pid" 2>/dev/null || break; sleep 0.25; done
        if kill -0 "$pid" 2>/dev/null; then
            echo "xfreerdp3 still running after TERM: sending KILL"
            kill -KILL "$pid"
        fi
    else
        echo "xfreerdp3 was not running"
    fi
    for _ in $(seq 1 80); do
        pgrep -f "pi_rdp_look.sh supervise $dir" > /dev/null || break
        sleep 0.25
    done
    echo "--- rdp.log (last 40 lines)"
    tail -n 40 "$dir/rdp.log" 2>/dev/null
    echo "--- supervise.log"
    cat "$dir/supervise.log" 2>/dev/null
    rm -rf "$dir"
    echo "--- left behind"
    pgrep -a xfreerdp3 || echo "no xfreerdp3"
    pgrep -a Xvfb || echo "no Xvfb"
    pgrep -af xvfb-run || echo "no xvfb-run"
    echo "deckcam: $(systemctl is-active deckcam)"
    ;;

*)
    echo "unknown subcommand: $cmd" >&2
    exit 2
    ;;
esac
