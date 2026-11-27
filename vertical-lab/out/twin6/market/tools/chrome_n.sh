#!/bin/sh
# One more headed Chrome on its own virtual display, same tunnel: chrome_n.sh <display> <cdp-port> <name>
D=$1; PORT=$2; NAME=$3
PROFILE=/tmp/market-rig/profile-$NAME
mkdir -p "$PROFILE/Default"
echo '{"credentials_enable_service": false, "profile": {"password_manager_enabled": false}}' > "$PROFILE/Default/Preferences"
setsid nohup Xvfb "$D" -screen 0 1920x1080x24 -nolisten tcp > /tmp/market-rig/xvfb-$NAME.log 2>&1 < /dev/null &
python3 -c "import time; time.sleep(2)"
DISPLAY=$D setsid nohup google-chrome --user-data-dir="$PROFILE" \
    --remote-debugging-port="$PORT" --remote-debugging-address=127.0.0.1 \
    --proxy-server="socks5://127.0.0.1:1080" \
    --no-first-run --no-default-browser-check --password-store=basic --test-type \
    --window-position=0,0 --window-size=1920,1080 --force-device-scale-factor=1 \
    --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader \
    --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding \
    --disable-features=LocalNetworkAccessChecks,LocalNetworkAccessChecksWebSockets,Translate \
    about:blank > /tmp/market-rig/chrome-$NAME.log 2>&1 < /dev/null &
