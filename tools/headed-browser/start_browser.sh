#!/usr/bin/env bash
# Virtual display + window manager + a plain headed Chrome whose page traffic goes
# through the SOCKS tunnel (tunnel.sh). No WebDriver and no --remote-debugging-port:
# the browser is driven only through X input (hb.py), exactly as a person would.
#
#   tools/headed-browser/start_browser.sh [URL]
#
# Needs: sudo apt-get install -y xdotool xclip imagemagick openbox
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${HB_WORK:-/tmp/hb}
mkdir -p "$WORK"
export DISPLAY=${DISPLAY:-:99}
pgrep -x Xvfb >/dev/null || { setsid -f Xvfb "$DISPLAY" -screen 0 1440x900x24 -nolisten tcp >"$WORK/xvfb.log" 2>&1; sleep 1; }
pgrep -x openbox >/dev/null || { setsid -f openbox >"$WORK/openbox.log" 2>&1; sleep 1; }
PAC="data:application/x-ns-proxy-autoconfig;base64,$(sed "s/127.0.0.1:1080/127.0.0.1:${PORT:-1080}/" "$HERE/proxy.pac" | base64 -w0)"
# TZ matches where the Pi's IP geolocates. The flags after the WebRTC one stop Chrome
# pulling component/model updates through the tunnel.
TZ=${BROWSER_TZ:-America/Denver} LANG=en_US.UTF-8 setsid -f google-chrome \
  --user-data-dir="$WORK/profile" \
  --proxy-pac-url="$PAC" \
  --force-webrtc-ip-handling-policy=disable_non_proxied_udp \
  --disable-background-networking --disable-component-update --disable-sync \
  --no-pings --disable-domain-reliability \
  --disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints,MediaRouter,DialMediaRouteProvider,AutofillServerCommunication,Translate \
  --no-first-run --no-default-browser-check --password-store=basic \
  --lang=en-US --window-position=0,0 --window-size=1440,900 \
  "${1:-about:blank}" >"$WORK/chrome.log" 2>&1
