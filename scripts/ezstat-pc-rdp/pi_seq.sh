#!/bin/bash
# pi_seq.sh DIR < SCRIPT: run a step script against the session in DIR (made
# by pi_drive.sh start), then tar the frames it took to stdout. One step per
# line: `shot NAME`, `sleep S`, `t TEXT` (types TEXT as is), or xdotool args
# (`key Return`, `mousemove X Y click 1`). Xvfb's keymap also has ( and ) on
# spare keycodes that FreeRDP drops, so type those as `key shift+9` / `key shift+0`.
set -u
dir=$1
XDO=${XDO:-$HOME/ezrdp/xdo}
umask 077
t=$(mktemp -d "$dir/seq.XXXXXX")
{ read -r disp; read -r xauth; } < "$dir/display"
export DISPLAY=$disp XAUTHORITY=$xauth LD_LIBRARY_PATH="$XDO/usr/lib/aarch64-linux-gnu"
while IFS= read -r line; do
    verb=${line%% *}
    rest=${line#* }
    [ "$verb" = "$line" ] && rest=""
    case "$verb" in
    '' | '#'*) ;;
    shot)
        cp "$dir/fb/Xvfb_screen0" "$t/$rest.xwd" && gzip -1 "$t/$rest.xwd"
        echo "$rest $(date -u +%T.%3N)" >> "$t/index"
        ;;
    sleep) sleep "$rest" ;;
    t) "$XDO/usr/bin/xdotool" type --delay 50 -- "$rest" < /dev/null ;;
    # shellcheck disable=SC2086  # xdotool args, split on purpose
    *) "$XDO/usr/bin/xdotool" "$verb" $rest < /dev/null ;;
    esac
done
tar -C "$t" -cf - .
rm -rf "$t"
