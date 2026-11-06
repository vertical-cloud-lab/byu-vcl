#!/bin/bash
# Remote Desktop session to the EZstat Pro's Windows 7 PC (#231) that can be
# driven with keystrokes and clicks, run on the CubXL Pi (des4), which is
# cabled to the PC. Copied to a mktemp dir in /dev/shm by drive.sh on the
# runner; each subcommand is its own SSH call.
#
#   pi_drive.sh start DIR MAX_S < ARGS  ARGS: one xfreerdp3 argument per line,
#                                       credentials included. Held in memory
#                                       only, never in argv or on disk.
#   pi_drive.sh shot DIR                tar on stdout: frame.xwd.gz, status
#   pi_drive.sh x DIR ARGS...           xdotool ARGS on the session's display
#   pi_drive.sh type DIR < TEXT         type TEXT (from stdin) into the session
#   (step scripts with screenshots: see pi_seq.sh)
#   pi_drive.sh stop DIR                kill xfreerdp3 (a disconnect, never a
#                                       log-off), report, delete DIR
#
# Screenshots come from Xvfb's -fbdir framebuffer file (XWD). Its header holds
# the Pi's hostname: convert to PNG before publishing, never commit the XWD.
# xdotool isn't installed on des4; it's unpacked (no sudo) in ~/ezrdp/xdo.
#
# Safety net: the session runs under `timeout MAX_S`, so if nobody runs
# `stop`, xfreerdp3 and Xvfb are killed and DIR is deleted.
set -u
cmd=$1
dir=$2
umask 077
W=1280
H=800
XDO=${XDO:-$HOME/ezrdp/xdo}

case "$cmd" in
start)
    max_s=$3
    IFS= read -r -d '' args || true
    mkdir -p "$dir/fb"
    date +%s > "$dir/t0"
    printf '%s' "$args" | setsid -f bash "$dir/pi_drive.sh" supervise "$dir" "$max_s" \
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
    timeout -k 10 "$3" xvfb-run -a \
        -s "-screen 0 ${W}x${H}x24 -fbdir $dir/fb -noreset" \
        bash "$dir/pi_drive.sh" inner "$dir"
    echo "xvfb-run exit $?"
    exec 7<&-
    [ -e "$dir/stop-requested" ] || rm -rf "$dir"
    ;;

inner)
    # Remember which display xvfb-run picked, for `x`.
    printf '%s\n%s\n' "$DISPLAY" "${XAUTHORITY:-}" > "$dir/display"
    xfreerdp3 /args-from:stdin <&7 7<&- > "$dir/rdp.log" 2>&1 &
    pid=$!
    exec 7<&-
    echo "$pid" > "$dir/rdp.pid"
    wait "$pid"
    echo "xfreerdp3 exit $?" >> "$dir/rdp.log"
    ;;

shot)
    t=$(mktemp -d "$dir/shot.XXXXXX")
    cp "$dir/fb/Xvfb_screen0" "$t/frame.xwd" && gzip -1 "$t/frame.xwd"
    pid=$(cat "$dir/rdp.pid" 2>/dev/null)
    {
        echo "utc $(date -u +%FT%T.%3NZ)"
        echo "elapsed_s $(( $(date +%s) - $(cat "$dir/t0") ))"
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "xfreerdp3 running"
        else
            echo "xfreerdp3 not-running"
        fi
    } > "$t/status"
    tar -C "$t" -cf - .
    rm -rf "$t"
    ;;

x)
    shift 2
    { read -r disp; read -r xauth; } < "$dir/display"
    DISPLAY=$disp XAUTHORITY=$xauth LD_LIBRARY_PATH="$XDO/usr/lib/aarch64-linux-gnu" \
        "$XDO/usr/bin/xdotool" "$@"
    ;;

type)
    { read -r disp; read -r xauth; } < "$dir/display"
    DISPLAY=$disp XAUTHORITY=$xauth LD_LIBRARY_PATH="$XDO/usr/lib/aarch64-linux-gnu" \
        "$XDO/usr/bin/xdotool" type --delay 60 --file -
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
        pgrep -f "pi_drive.sh supervise $dir" > /dev/null || break
        sleep 0.25
    done
    echo "--- rdp.log (last 25 lines)"
    tail -n 25 "$dir/rdp.log" 2>/dev/null
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
