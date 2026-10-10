# Running `onshape_ui.py` in a headed browser on a Raspberry Pi

Onshape's sign-in is friendlier to a real browser on a residential IP than to headless
Chrome on a GitHub runner, so the run of 2026-09-25 put the browser on a Pi and drove it
from the runner:

```
runner:  python onshape_ui.py --cdp http://127.0.0.1:9222
           │  ssh -N -L 127.0.0.1:9222:127.0.0.1:9222   (Tailscale SSH, port 22 only)
Pi:        headed Chromium on a virtual X display (:99), DevTools on 127.0.0.1:9222
```

Playwright on the runner moves the mouse, clicks, drags and types through the tunnel. The
browser, its IP and its session all stay on the Pi. **Nothing is installed system-wide:**
no `apt`, no `sudo`. Everything lives in `~/onshape-ui`, which is where these files came
from.

| File | What it does |
|---|---|
| [`xvfb.sh`](xvfb.sh) | Starts an Xvfb that was unpacked, not installed. Xvfb looks for `xkbcomp` at its compiled-in `/usr/bin`, so the script runs it in a private user+mount namespace with the unpacked `usr/bin` overlaid there. Nothing outside that process sees the overlay. |
| [`chromium.sh`](chromium.sh) | Starts the Pi's own Chromium, headed on `:99`, with DevTools on loopback only and SwiftShader WebGL2. It is niced and pinned to cores 2–3. |
| [`xshot.py`](xshot.py) | Takes a PNG of the whole display using only ctypes, libX11 and zlib. Unlike a page screenshot, it shows the browser's own UI, including native permission prompts. |

## One-time setup, as the Pi's user

```bash
mkdir -p ~/onshape-ui/debs ~/onshape-ui/root && cd ~/onshape-ui/debs
apt-get download -o Acquire::http::Dl-Limit=800 \
  xvfb xserver-common x11-xkb-utils libxfont2 libfontenc1 libunwind8 libxdo3 xdotool   # ~6 MB
for f in *.deb; do dpkg -x "$f" ../root; done && cd .. && rm -rf debs
# then copy xvfb.sh, chromium.sh and xshot.py from this folder into ~/onshape-ui
```

`apt-get download` needs no root. The package list comes from `apt-cache depends` on
Debian 13 (trixie), arm64, with only the packages that weren't already there. Chromium
itself is the Pi's own `/usr/bin/chromium`. User namespaces must be enabled, which is the
default on trixie. Check with `unshare -rm true`.

## A run

On the Pi:

```bash
cd ~/onshape-ui
setsid nohup ./xvfb.sh :99 -screen 0 1600x1000x24 -nolisten tcp > xvfb.log 2>&1 < /dev/null &
mkdir -p profile/Default && echo '{"credentials_enable_service": false,
  "profile": {"password_manager_enabled": false}}' > profile/Default/Preferences   # never save the password
setsid nohup ./chromium.sh about:blank > chromium.log 2>&1 < /dev/null &
```

Then on the runner:

```bash
ssh -N -L 127.0.0.1:9222:127.0.0.1:9222 "$RPI_STREAM_CAM_USERNAME@$RPI_STREAM_CAM_HOSTNAME" &
python onshape/onshape_ui.py --cdp http://127.0.0.1:9222     # ~8 minutes
```

`ONSHAPE_USERNAME` and `ONSHAPE_PASSWORD` are read on the runner and typed into the page
through the tunnel. They never reach the Pi's disk or a command line. To see the whole
screen, including anything outside the page, run `DISPLAY=:99 python3 xshot.py out.png` on
the Pi. To click something outside the page, run
`xdotool mousemove X Y click 1` from `~/onshape-ui/root`.

## Cleanup

Sign out in the browser. Onshape's user menu → *Sign out*; afterwards `/documents`
redirects to `/signin`. Then, on the Pi:

```bash
pkill -f '[u]ser-data-dir=/home/.*/onshape-ui/profile'; pkill -x Xvfb
rm -rf ~/onshape-ui/profile ~/onshape-ui/*.log
```

Write the `pkill` patterns so they can't match the command that runs them. An unbracketed
`pkill -f onshape-ui/...` sent over `ssh` matches the remote shell's own command line and
kills the session halfway through.

## What happened on 2026-09-25

**Which Pi.** The CubXL Pi 5 was the natural choice, but it had dropped off the tailnet at
21:37 UTC. The OT-2 camera Pi is a Zero 2 W and was at ~100 % CPU pushing the YouTube
stream. That left the Pi 5 at `RPI_STREAM_CAM_HOSTNAME`, which runs `cubos.service` and was
at load 0.00 with 3.7 GB free.

That Pi is also the one that reaches the OT-2 at `169.254.51.252` and holds `~/ot2ctl.py`.
The root CLAUDE.md attributes both to `OT2_STREAM_CAM_HOSTNAME`, so the two variables are
worth re-checking there.

**Load.** During the build Chromium used about 0.8 of a core and 1.3 GB, and the load
average peaked at 2.9. Another session was running OT-2 scans from that Pi at the same time
(`~/enclosure-cal/run1`–`run3`, 22:06–22:35 UTC), which is why the browser was niced and
kept to two cores. CubOS stayed `active` throughout.

**What the screen showed that the page didn't.** Chrome raised a native "cad.onshape.com
wants to access other apps and services on this device" prompt, its local-network-access
permission. It is invisible to page screenshots, and it was blocked with `xdotool`.

**Left on the Pi:** `~/onshape-ui/{root/, xvfb.sh, chromium.sh, xshot.py}`, 8.8 MB. The
browser profile, screenshots, logs and `.deb` files were deleted, and the account was
signed out.
