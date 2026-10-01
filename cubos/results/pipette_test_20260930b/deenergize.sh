#!/bin/bash
U=$(stat -c %U /tmp/run_20260930b); T=/home/$U/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd
$T --deenergize; sleep 1; $T --status --full > /tmp/run_20260930b/tic_status_deenergized.txt 2>&1
chmod a+r /tmp/run_20260930b/tic_status_deenergized.txt
grep -E "VIN|Energized|Operation state" /tmp/run_20260930b/tic_status_deenergized.txt
