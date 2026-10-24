#!/bin/sh
# The recording rig for onshape_ui.py: a virtual display, a headed Chrome on it with
# DevTools on loopback, and a SOCKS tunnel so that Chrome's traffic leaves through a Pi
# rather than the runner's datacenter IP. record_ui_build.py attaches to the Chrome and
# records the display.
#
#   ./rig.sh start     # Xvfb, then the tunnel, then Chrome
#   ./rig.sh check     # where the tunnel exits (ASN and org only), and a screenshot of the display
#   ./rig.sh stop      # stop all three and delete the browser profile
#
# The Pi only relays traffic: nothing is installed or written there. It defaults to the
# CubXL Pi (CUBXL_PI_USERNAME / CUBXL_PI_HOSTNAME); set PI_USER and PI_HOST for another.
set -eu

REC_DIR=${REC_DIR:-/tmp/onshape-rec}
DISP=${DISP:-:99}
SIZE=${SIZE:-1920x1080}
SOCKS_PORT=${SOCKS_PORT:-1080}
CDP_PORT=${CDP_PORT:-9222}
CHROME=${CHROME:-google-chrome}
PI_USER=${PI_USER:-${CUBXL_PI_USERNAME:-}}
PI_HOST=${PI_HOST:-${CUBXL_PI_HOSTNAME:-}}
PROFILE=$REC_DIR/profile

start() {
    mkdir -p "$REC_DIR" "$PROFILE/Default"
    # Never offer to save the Onshape password.
    echo '{"credentials_enable_service": false, "profile": {"password_manager_enabled": false}}' \
        > "$PROFILE/Default/Preferences"

    setsid nohup Xvfb "$DISP" -screen 0 "${SIZE}x24" -nolisten tcp > "$REC_DIR/xvfb.log" 2>&1 < /dev/null &
    sleep_s 2

    [ -n "$PI_USER" ] && [ -n "$PI_HOST" ] || { echo "set PI_USER and PI_HOST (or the CUBXL_PI_* variables)"; exit 1; }
    setsid nohup ssh -N -D "127.0.0.1:$SOCKS_PORT" -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
        -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$PI_USER@$PI_HOST" \
        > "$REC_DIR/tunnel.log" 2>&1 < /dev/null &
    sleep_s 4

    # SwiftShader gives WebGL2 without a GPU; Chrome 137+ needs the "unsafe" flag to use it.
    # Local Network Access checks are off because Onshape probes a loopback port for a
    # 3Dconnexion mouse driver, and that raises a native permission prompt that would sit
    # on top of the recording. Nothing listens there, so the probe just fails.
    W=${SIZE%x*}; H=${SIZE#*x}
    DISPLAY=$DISP setsid nohup "$CHROME" --user-data-dir="$PROFILE" \
        --remote-debugging-port="$CDP_PORT" --remote-debugging-address=127.0.0.1 \
        --proxy-server="socks5://127.0.0.1:$SOCKS_PORT" \
        --no-first-run --no-default-browser-check --password-store=basic --test-type \
        --window-position=0,0 --window-size="$W,$H" --force-device-scale-factor=1 \
        --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader \
        --disable-features=LocalNetworkAccessChecks,LocalNetworkAccessChecksWebSockets,Translate \
        about:blank > "$REC_DIR/chrome.log" 2>&1 < /dev/null &
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        sleep_s 2
        curl -sf "http://127.0.0.1:$CDP_PORT/json/version" > "$REC_DIR/version.json" && break
    done
    python3 -c 'import json,sys; print("chrome:", json.load(open(sys.argv[1]))["Browser"])' "$REC_DIR/version.json"
}

check() {
    curl -s --max-time 20 --socks5-hostname "127.0.0.1:$SOCKS_PORT" https://ipinfo.io/json \
        | python3 -c 'import json,sys; d=json.load(sys.stdin); print("tunnel exits via:", d.get("org"), "|", d.get("region"), d.get("country"))'
    python3 "$(dirname "$0")/../pi/xshot.py" "$REC_DIR/display.png"
}

stop() {
    pkill -f "[u]ser-data-dir=$PROFILE" || true
    pkill -f "[s]sh -N -D 127.0.0.1:$SOCKS_PORT" || true
    pkill -f "[X]vfb $DISP" || true
    sleep_s 2
    rm -rf "$PROFILE"
}

# `sleep` without the shell builtin, which some agent harnesses block.
sleep_s() { python3 -c "import time; time.sleep($1)"; }

case "${1:-}" in
    start) start ;;
    check) DISPLAY=$DISP check ;;
    stop) stop ;;
    *) echo "usage: $0 start|check|stop"; exit 2 ;;
esac
