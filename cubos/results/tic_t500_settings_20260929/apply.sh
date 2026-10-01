#!/bin/sh
# Write the validated settings file into the Tic's EEPROM (ticcmd reinitializes it afterwards),
# then dump the resulting state. Run as root.
set -u
TIC=/home/$SUDO_USER/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd
D=/home/$SUDO_USER/tic-setup-20260929
date -u +%Y-%m-%dT%H:%M:%SZ > "$D/apply_time.txt"
"$TIC" --settings "$D/intended_settings_fixed.txt" > "$D/apply_output.txt" 2>&1; echo "apply exit=$?" | tee -a "$D/apply_output.txt"
sleep 1
sh "$D/read_state.sh" after
chown "$SUDO_USER:$SUDO_USER" "$D"/*
