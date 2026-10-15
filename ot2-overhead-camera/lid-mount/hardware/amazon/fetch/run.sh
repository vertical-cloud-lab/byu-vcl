#!/bin/bash
# Start headless chromium with CDP on loopback, run amz.js, always kill chromium afterwards.
# Same pattern as ../../mcmaster/fetch/run.sh, in its own folder and profile.
cd ~/amz || exit 1
mkdir -p out
UA="Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
nice -n 10 chromium --headless --disable-gpu --no-sandbox --disable-dev-shm-usage \
  --user-agent="$UA" --window-size=1400,2400 --user-data-dir=/tmp/amzprof --lang=en-US \
  --remote-debugging-port=9224 --remote-allow-origins='*' about:blank >/dev/null 2>/tmp/amzchr.err &
CP=$!
cleanup() { kill "$CP" 2>/dev/null; for i in 1 2 3 4 5 6; do kill -0 "$CP" 2>/dev/null || break; sleep 0.5; done; kill -9 "$CP" 2>/dev/null; pkill -f '^[^ ]*chrom[^ ]* .*--user-data-dir=/tmp/amzprof' 2>/dev/null; rm -rf /tmp/amzprof; true; }
trap cleanup EXIT
timeout "${CDP_TIMEOUT:-300}" node --experimental-websocket amz.js "$@"
