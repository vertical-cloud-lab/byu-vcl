#!/bin/sh
# Run the unpacked Xvfb (~/onshape-ui/root) without installing it. The server looks for
# xkbcomp at the compiled-in /usr/bin, so run it in a private user+mount namespace with
# the unpacked usr/bin overlaid on /usr/bin. Nothing outside this process sees the overlay.
#
#   setsid nohup nice -n 10 taskset -c 2,3 ./xvfb.sh :99 -screen 0 1600x1000x24 -nolisten tcp > xvfb.log 2>&1 &
R="$HOME/onshape-ui/root"
exec unshare --user --map-root-user --mount sh -c "
  mount -t overlay overlay -o lowerdir=$R/usr/bin:/usr/bin /usr/bin || exit 1
  export LD_LIBRARY_PATH=$R/usr/lib/aarch64-linux-gnu
  exec $R/usr/bin/Xvfb \"\$@\"" xvfb "$@"
