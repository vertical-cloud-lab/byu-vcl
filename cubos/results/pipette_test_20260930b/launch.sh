#!/bin/bash
# Launch the trio detached on the Pi: camera + plunger-trace harness, Tic polled as root.
set -u
R=/tmp/run_20260930b; cd ~/CubOS
G=$R/cub_xl_ben_pipette_capper.yaml; D=$R/ben_6vials_tiprack.yaml; P=$R/pipette_test.yaml
date -u +%FT%TZ > $R/start_utc.txt
rm -f $R/.stop
PLUNGER_TRACE_OUT=$R/plunger_trace.json PYTHONDONTWRITEBYTECODE=1 setsid nohup .venv/bin/python \
  ~/byu-vcl/cubos/tools/run_with_camera_and_plunger_trace.py \
  --outdir $R/frames --at 2,3,4,8,9,10 --width 1536 --height 864 -- $G $D $P \
  > $R/run_hardware.log 2>&1 < /dev/null &
echo "run pid $!"
