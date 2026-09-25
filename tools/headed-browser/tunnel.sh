#!/usr/bin/env bash
# SOCKS5 proxy on 127.0.0.1:1080 whose egress is a lab Pi's internet connection.
#
#   PI=OT2_STREAM_CAM tools/headed-browser/tunnel.sh   # uses $OT2_STREAM_CAM_USERNAME/_HOSTNAME
#   PI=CUBXL_PI RATE=500000 tools/headed-browser/tunnel.sh
#
# The Pi only relays bytes; nothing is installed on it. RATE caps the Pi -> runner
# direction in bytes/s. The default (~2.4 Mbit/s) sits beside the OT-2 stream cam's
# ~2 Mbit/s livestream without disturbing it. Runs in the foreground; background it
# yourself and kill it when done.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PI=${PI:-OT2_STREAM_CAM}
user_var=${PI}_USERNAME
host_var=${PI}_HOSTNAME
: "${!user_var:?$user_var is not set}" "${!host_var:?$host_var is not set}"
exec ssh -N -D "127.0.0.1:${PORT:-1080}" \
  -o BatchMode=yes -o LogLevel=ERROR -o ExitOnForwardFailure=yes \
  -o StrictHostKeyChecking=accept-new \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=4 \
  -o ProxyCommand="python3 $HERE/ratelimit_pipe.py %h %p ${RATE:-300000}" \
  "${!user_var}@${!host_var}"
