#!/bin/bash
# Start headless chromium with CDP on loopback, run cdp.js, always kill chromium afterwards.
cd ~/mcm/lid || exit 1
mkdir -p dl
UA="Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
nice -n 10 chromium --headless --disable-gpu --no-sandbox --disable-dev-shm-usage \
  --user-agent="$UA" --window-size=1600,3000 --user-data-dir=/tmp/cprof \
  --remote-debugging-port=9223 --remote-allow-origins='*' about:blank >/dev/null 2>/tmp/chr2.err &
CP=$!
cleanup() { kill "$CP" 2>/dev/null; for i in 1 2 3 4 5 6; do kill -0 "$CP" 2>/dev/null || break; sleep 0.5; done; kill -9 "$CP" 2>/dev/null; pkill -f '^[^ ]*chrom[^ ]* .*--user-data-dir=/tmp/cprof' 2>/dev/null; true; }
trap cleanup EXIT
timeout "${CDP_TIMEOUT:-300}" node --experimental-websocket cdp.js "$@"
