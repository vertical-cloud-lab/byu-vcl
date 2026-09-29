#!/bin/sh
# Read-only: dump Tic status and settings. Run as root (native USB interface needs it
# without a udev rule). Usage: read_state.sh <label>
set -u
TIC=/home/$SUDO_USER/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd
D=/home/$SUDO_USER/tic-setup-20260929
L=${1:-state}
date -u +%Y-%m-%dT%H:%M:%SZ > "$D/${L}_time.txt"
"$TIC" --status --full > "$D/${L}_status_full.txt" 2>&1; echo "status exit=$?"
"$TIC" --get-settings "$D/${L}_settings.txt" 2>&1; echo "get-settings exit=$?"
chown "$SUDO_USER:$SUDO_USER" "$D"/*
