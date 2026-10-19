#!/bin/bash
# Set up the OT-2 lid camera YouTube stream on the Pi 5. Run ON THE PI as the
# normal user, from a copy of this directory, with the sudo password on stdin:
#   bash install.sh < <(printenv RPI_STREAM_CAM_PASSWORD)   # or interactively
# Idempotent: re-running updates the files and restarts nothing by itself.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PICAM="$HOME/ac-training-lab/src/ac_training_lab/picam"
read -r -s SUDO_PW
sudo_() { printf '%s\n' "$SUDO_PW" | sudo -S -p '' "$@"; }

echo "1/6 packages"
sudo_ sh -c 'apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg git python3-venv'

echo "2/6 picam client (upstream checkout, device.py replaced by the lab's patched copy)"
if [ ! -d "$HOME/ac-training-lab" ]; then
  git clone -q --filter=blob:none --sparse https://github.com/AccelerationConsortium/ac-training-lab "$HOME/ac-training-lab"
  (cd "$HOME/ac-training-lab" && git sparse-checkout set src/ac_training_lab/picam)
fi
cp "$HERE/device.py" "$PICAM/device.py"
[ -d "$PICAM/venv" ] || python3 -m venv "$PICAM/venv"
"$PICAM/venv/bin/pip" install -q requests
"$PICAM/venv/bin/python" -m py_compile "$PICAM/device.py"

echo "3/6 my_secrets.py"
if [ ! -f "$PICAM/my_secrets.py" ]; then
  install -m 600 "$HERE/my_secrets_example.py" "$PICAM/my_secrets.py"
  echo "   wrote $PICAM/my_secrets.py from the example: set LAMBDA_FUNCTION_URL before starting"
fi
chmod 600 "$PICAM/my_secrets.py"

echo "4/6 systemd units"
sed -e "s|@USER@|$(id -un)|g" -e "s|@HOME@|$HOME|g" "$HERE/device.service.in" > /tmp/device.service
sudo_ install -m 644 /tmp/device.service /etc/systemd/system/device.service
for s in stream-watchdog.sh stream-reboot.sh; do
  sudo_ install -m 755 "$HERE/$s" /usr/local/bin/$s
done
for u in stream-watchdog.service stream-watchdog.timer stream-reboot.service stream-reboot.timer; do
  sudo_ install -m 644 "$HERE/$u" /etc/systemd/system/$u
done
sudo_ install -m 644 "$HERE/stream-reboot-inhibit.rules" /etc/polkit-1/rules.d/50-stream-reboot-inhibit.rules
rm -f /tmp/device.service
# stream-reboot replaced stream-rotate (a restart of the stream only) on 2026-10-19
if [ -f /etc/systemd/system/stream-rotate.timer ]; then
  sudo_ systemctl disable --now stream-rotate.timer >/dev/null 2>&1 || true
  sudo_ rm -f /etc/systemd/system/stream-rotate.timer /etc/systemd/system/stream-rotate.service
fi

echo "5/6 NetworkManager (campus Wi-Fi ARP conflicts; Wi-Fi power save)"
sudo_ install -m 644 "$HERE/no-ipv4-acd.conf" /etc/NetworkManager/conf.d/no-ipv4-acd.conf
sudo_ install -m 644 "$HERE/wifi-powersave-off.conf" /etc/NetworkManager/conf.d/wifi-powersave-off.conf
sudo_ nmcli general reload conf

echo "6/6 enable"
sudo_ systemctl daemon-reload
sudo_ systemctl enable stream-watchdog.timer stream-reboot.timer device.service >/dev/null 2>&1
echo "done. Start with: sudo systemctl start stream-watchdog.timer stream-reboot.timer device.service"
