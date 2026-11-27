#!/bin/sh
# rig.sh's Chrome (49677cf), with background-tab throttling off so several tabs can each read at a person's pace.
PROFILE=/tmp/market-rig/profile
DISPLAY=:99 setsid nohup google-chrome --user-data-dir="$PROFILE" \
    --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 \
    --proxy-server="socks5://127.0.0.1:1080" \
    --no-first-run --no-default-browser-check --password-store=basic --test-type \
    --window-position=0,0 --window-size=1920,1080 --force-device-scale-factor=1 \
    --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader \
    --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding \
    --disable-features=LocalNetworkAccessChecks,LocalNetworkAccessChecksWebSockets,Translate,CalculateNativeWinOcclusion \
    about:blank > /tmp/market-rig/chrome.log 2>&1 < /dev/null &
