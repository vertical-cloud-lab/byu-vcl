#!/bin/sh
# Headed Chromium on the virtual display, with DevTools on 127.0.0.1:9222 only.
# SwiftShader gives WebGL2 without a GPU (Xvfb has none); Chrome 137+ needs the
# "unsafe" flag to fall back to it. Niced and pinned to two cores, to leave the
# other two to whatever the Pi is really for.
#
#   setsid nohup ./chromium.sh about:blank > chromium.log 2>&1 &
export DISPLAY=:99
exec nice -n 10 taskset -c 2,3 chromium --user-data-dir="$HOME/onshape-ui/profile" \
  --remote-debugging-port=9222 --no-first-run --no-default-browser-check --password-store=basic \
  --window-position=0,0 --window-size=1600,1000 \
  --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader "$@"
