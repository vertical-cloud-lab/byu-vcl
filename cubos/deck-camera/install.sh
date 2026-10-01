#!/bin/sh
# Install or update deckcam as a systemd service. Run on the CubXL Pi:
#
#   sudo ./install.sh
#
# The service runs as the user who invoked sudo, from ~/deckcam, and listens on
# 127.0.0.1:8743 only. To remove it:
#
#   sudo systemctl disable --now deckcam && sudo rm /etc/systemd/system/deckcam.service
set -eu
user=${SUDO_USER:?run this with sudo, as the Pi user the service should run as}
group=$(id -gn "$user")
home=$(getent passwd "$user" | cut -d: -f6)
here=$(cd "$(dirname "$0")" && pwd)
dest="$home/deckcam"

id -nG "$user" | grep -qw video || echo "warning: $user is not in the video group, so cannot open the camera" >&2

install -d -o "$user" -g "$group" "$dest"
install -o "$user" -g "$group" -m 755 "$here/deckcam.py" "$dest/deckcam.py"
sed -e "s|@USER@|$user|g" -e "s|@DEST@|$dest|g" "$here/deckcam.service" \
    > /etc/systemd/system/deckcam.service
systemctl daemon-reload
systemctl enable deckcam
systemctl restart deckcam
systemctl --no-pager --lines=0 status deckcam
