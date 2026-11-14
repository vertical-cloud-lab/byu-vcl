#!/usr/bin/env bash
# One-time setup for the OT-2 overhead camera test Pi (RPi OS Lite / Bookworm).
# Run after flashing the OS and completing the Tailscale steps in SETUP.md.
set -euo pipefail

echo ">>> Updating package lists..."
sudo apt-get update

echo ">>> Installing picamera2, libcamera apps, and numpy (system packages)..."
# picamera2 pulls in the libcamera Python bindings; rpicam-apps gives the
# rpicam-hello / rpicam-still CLI tools used for a quick camera sanity check.
sudo apt-get install -y python3-picamera2 rpicam-apps python3-numpy

echo ">>> Quick camera check (5 s preview frames, no window on Lite)..."
# Confirms the camera is detected. On headless Lite there is no display, so
# --nopreview just verifies frames are captured without error.
rpicam-hello --nopreview --timeout 2000 || {
    echo "!! Camera not detected. Check the ribbon cable orientation and that"
    echo "   the CSI connector latch is fully seated, then re-run this script."
    exit 1
}

echo ">>> Done. Next: 'python3 preview_server.py' to focus, then"
echo "    'python3 capture_still.py' to grab a full-res still."
