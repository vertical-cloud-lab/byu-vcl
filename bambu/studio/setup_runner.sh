#!/bin/bash
# Bring Bambu Studio up on a fresh GitHub-hosted runner, LOGGED OUT, so that a
# @claude-print session starts at Studio's home page instead of a bare machine.
#
# This scripts the "Setup" and "First run, in order" sections of the runbook
# (bambu/studio/README.md on PR 234's branch): the apt packages, the AppImage,
# the SSL prompt, the setup wizard, the network plug-in, the Beta prompts and
# the profile-update prompt. It does not log in and reads no secret, so it is
# safe to run in a plain @claude run or before the agent starts.
#
# Timings measured on ubuntu-24.04 x86-64 for issue #314 (2026-11-03):
#   apt packages, no recommends, no man-db trigger   ~90 s cold, ~10 s with
#                                                   the .debs already cached
#   (the runbook's plain apt-get install took 136 s)
#   AppImage download (220 MB) + extract             ~3 s
#   network plug-in (31 MB, Bambu's CDN)             <1 s
#   Studio launch to its home page, no prompts       ~7 s
#
# Why no wizard: Studio runs it only when it has no config or no printers
# (GUI_App::config_wizard_startup), and asks about the SSL store only when
# SSL_CERT_FILE is unset (Http.cpp). So a 20-line BambuStudio.conf, the
# plug-in unzipped into ~/.config/BambuStudio/plugins and SSL_CERT_FILE are
# all it takes. The profile-update prompt still comes up on every launch; it
# is closed here, which is the same as the runbook's Cancel.
#
# Studio's network plug-in is x86-64 only on Linux (Bambu's API offers no arm
# build), so this cannot work on a Raspberry Pi.
#
# Usage:   bash bambu/studio/setup_runner.sh      (idempotent)
# Env:     APT_DEB_CACHE   where apt keeps the .debs, for actions/cache
#                          (default ~/apt-debs)
#          BAMBU_RECORD=1  also start the screen recorder from the runbook,
#                          5 min segments in ~/bambu/recording/
# Result:  Studio maximised on DISPLAY=:99; ~/bambu/setup_timings.json.
#          ~/bambu/squashfs-root is where the runbook's studio.sh looks.
set -euo pipefail

STUDIO_TAG="v02.08.02.61"
STUDIO_ASSET="BambuStudio_ubuntu24.04-v02.08.02.61-20260820225108.AppImage"
STUDIO_SHA256="d501b103fac5424513ec0e8d6bc145fb30719de2c7d94d7320d723740c81a7fd"
STUDIO_VERSION="${STUDIO_TAG#v}"
BAMBU_DIR="$HOME/bambu"
CONF_DIR="$HOME/.config/BambuStudio"
APT_DEB_CACHE="${APT_DEB_CACHE:-$HOME/apt-debs}"
export DISPLAY=:99

T0=$(date +%s.%N)
declare -A TIMES
since() { python3 -c "import sys; print(round(float(sys.argv[1]) - float(sys.argv[2]), 1))" "$(date +%s.%N)" "$1"; }
log() { echo "[setup_runner $(since "$T0") s] $*"; }
# The agent harness blocks a bare `sleep` in its own shell; Python's is fine.
nap() { python3 -c "import sys, time; time.sleep(float(sys.argv[1]))" "$1"; }
window_up() { wmctrl -l 2>/dev/null | grep -q -- "$1"; }

# apt hands a cached .deb of the right size straight to dpkg without checking
# its hash (tested on #314: a tampered wmctrl .deb went to dpkg as is). A
# cache restored from actions/cache runs as root before the login is typed,
# so check every file against the signed index from `apt-get update` and
# delete any that doesn't match; apt downloads those again.
verify_cached_debs() {
  python3 -I - "$APT_DEB_CACHE" <<'PY'
import hashlib, os, subprocess, sys, urllib.parse
cache = sys.argv[1]
debs = {}
for name in os.listdir(cache):
    parts = urllib.parse.unquote(name[:-4]).split("_") if name.endswith(".deb") else []
    if len(parts) == 3:
        debs[name] = parts                     # package, version, architecture
    elif name.endswith(".deb"):
        os.remove(os.path.join(cache, name))
want = {}
if debs:
    out = subprocess.run(["apt-cache", "show", *sorted({f"{p}={v}" for p, v, _ in debs.values()})],
                         capture_output=True, text=True).stdout
    for rec in out.split("\n\n"):
        f = dict(l.split(": ", 1) for l in rec.splitlines() if ": " in l and not l.startswith(" "))
        if "SHA256" in f:
            want[(f.get("Package"), f.get("Version"), f.get("Architecture"))] = f["SHA256"]
kept = dropped = 0
for name, key in debs.items():
    path = os.path.join(cache, name)
    with open(path, "rb") as fh:
        ok = hashlib.sha256(fh.read()).hexdigest() == want.get(tuple(key))
    if ok:
        kept += 1
    else:
        os.remove(path); dropped += 1
print(f"cached .debs: {kept} match the signed index, {dropped} deleted")
PY
}

# 1. System packages. --no-install-recommends and skipping man-db's trigger
#    cut the runbook's 136 s to about 90 s; most of what is left is download,
#    which actions/cache on $APT_DEB_CACHE removes.
t=$(date +%s.%N)
PKGS=(libwebkit2gtk-4.1-0 libgstreamer-plugins-base1.0-0 gstreamer1.0-plugins-good
      gstreamer1.0-libav xdotool imagemagick openbox wmctrl ffmpeg)
if ! dpkg -s "${PKGS[@]}" >/dev/null 2>&1; then
  log "apt: installing ${PKGS[*]} (log: $BAMBU_DIR/apt.log)"
  mkdir -p "$BAMBU_DIR" "$APT_DEB_CACHE/partial"
  sudo rm -f /var/lib/man-db/auto-update
  # The cache lives in $HOME, which apt's _apt sandbox user can't write to.
  sudo apt-get update -qq >"$BAMBU_DIR/apt.log" 2>&1
  sudo chown -R "$(id -u):$(id -g)" "$APT_DEB_CACHE"
  log "apt: $(verify_cached_debs)"
  sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_SUSPEND=1 apt-get install -y -qq \
       --no-install-recommends -o APT::Sandbox::User=root \
       -o Dir::Cache::archives="$APT_DEB_CACHE" "${PKGS[@]}" >>"$BAMBU_DIR/apt.log" 2>&1
  sudo chown -R "$(id -u):$(id -g)" "$APT_DEB_CACHE"
fi
TIMES[apt]=$(since "$t"); log "apt: done (${TIMES[apt]} s)"

# 2. The AppImage, checked against the digest GitHub publishes for the asset.
t=$(date +%s.%N)
if [ ! -x "$BAMBU_DIR/squashfs-root/AppRun" ]; then
  mkdir -p "$BAMBU_DIR"
  curl -fsSL --retry 3 -o "$BAMBU_DIR/studio.AppImage" \
       "https://github.com/bambulab/BambuStudio/releases/download/$STUDIO_TAG/$STUDIO_ASSET"
  echo "$STUDIO_SHA256  $BAMBU_DIR/studio.AppImage" | sha256sum -c --quiet -
  chmod +x "$BAMBU_DIR/studio.AppImage"
  (cd "$BAMBU_DIR" && ./studio.AppImage --appimage-extract >/dev/null)
  rm -f "$BAMBU_DIR/studio.AppImage"
fi
TIMES[appimage]=$(since "$t"); log "Studio $STUDIO_VERSION: extracted (${TIMES[appimage]} s)"

# 3. A config that says the wizard is done. Only written if none exists, so it
#    never overwrites a logged-in one.
if [ ! -f "$CONF_DIR/BambuStudio.conf" ]; then
  mkdir -p "$CONF_DIR"
  cat > "$CONF_DIR/BambuStudio.conf" <<EOF
{
    "header": "BambuStudio $STUDIO_VERSION",
    "app": {
        "region": "North America",
        "installed_networking": "1",
        "enable_beta_version_update": false,
        "sync_user_preset": false,
        "privacy_version": "00.00.00.00",
        "version": "$STUDIO_VERSION"
    },
    "firstguide": {"finish": true, "privacyuse": false},
    "models": [
        {"model": "Bambu Lab A1 mini", "nozzle_diameter": "0.2;0.4", "vendor": "BBL"},
        {"model": "Bambu Lab H2D", "nozzle_diameter": "0.2;0.4", "vendor": "BBL"}
    ]
}
EOF
  log "config: seeded (wizard marked done, region North America, Beta prompts off)"
fi

# 4. The network plug-in, from the same endpoint and with the same headers
#    Studio's wizard uses (GUI_App::get_plugin_url: first 9 chars + "00").
t=$(date +%s.%N)
if [ ! -f "$CONF_DIR/plugins/libbambu_networking.so" ]; then
  api="https://api.bambulab.com/v1/iot-service/api/slicer/resource?slicer/plugins/cloud=${STUDIO_VERSION:0:9}00"
  url=$(curl -fsS --retry 3 -H "X-BBL-Client-Type: slicer" -H "X-BBL-Client-Name: BambuStudio" \
             -H "X-BBL-Client-Version: $STUDIO_VERSION" -H "X-BBL-OS-Type: linux" "$api" |
        python3 -c 'import json, sys; print(json.load(sys.stdin)["resources"][0]["url"])')
  case "$url" in
    https://public-cdn.bblmw.com/*) ;;
    *) echo "unexpected plug-in URL: $url" >&2; exit 1 ;;
  esac
  tmp=$(mktemp -d)
  curl -fsSL --retry 3 -o "$tmp/plugin.zip" "$url"
  log "plug-in: $(basename "$url") sha256 $(sha256sum "$tmp/plugin.zip" | cut -c1-16)…"
  mkdir -p "$CONF_DIR/plugins"
  python3 -I -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' \
          "$tmp/plugin.zip" "$CONF_DIR/plugins"
  rm -rf "$tmp"
fi
TIMES[plugin]=$(since "$t"); log "plug-in: installed (${TIMES[plugin]} s)"

# 5. Virtual display and window manager, then the optional recorder.
if ! xdotool getdisplaygeometry >/dev/null 2>&1; then
  (Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &)
  for _ in $(seq 50); do xdotool getdisplaygeometry >/dev/null 2>&1 && break; nap 0.1; done
fi
pgrep -x openbox >/dev/null || (openbox >/dev/null 2>&1 &)
if [ "${BAMBU_RECORD:-0}" = 1 ] && ! pgrep -f "[x]11grab" >/dev/null; then
  mkdir -p "$BAMBU_DIR/recording"
  (cd "$BAMBU_DIR/recording" && nohup ffmpeg -loglevel error -f x11grab -framerate 15 \
     -video_size 1920x1080 -i :99.0 -c:v libx264 -preset ultrafast -f segment \
     -segment_time 300 raw_%03d.mkv >/dev/null 2>&1 &)
  log "recorder: started in $BAMBU_DIR/recording"
fi

# 6. Studio itself, as the runbook's studio.sh starts it, plus SSL_CERT_FILE.
t=$(date +%s.%N)
if ! pgrep -x bambustu_main >/dev/null; then
  (SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt GDK_BACKEND=x11 LIBGL_ALWAYS_SOFTWARE=1 \
   WEBKIT_DISABLE_COMPOSITING_MODE=1 WEBKIT_DISABLE_DMABUF_RENDERER=1 NO_AT_BRIDGE=1 \
   nohup "$BAMBU_DIR/squashfs-root/AppRun" > "$BAMBU_DIR/studio.log" 2>&1 &)
fi
for _ in $(seq 120); do window_up "Untitled" && break; nap 0.5; done
window_up "Untitled" || { echo "Studio's main window did not appear within 60 s" >&2; exit 1; }
TIMES[studio]=$(since "$t"); log "Studio: main window up (${TIMES[studio]} s)"

# The profile-update prompt arrives with or just after the main window.
# Closing it keeps the profiles bundled with the release, like Cancel.
# Watch for up to 10 s, or 2 s after the last prompt closed.
seen_prompt=0; quiet=0
for _ in $(seq 20); do
  closed=0
  for title in "Configuration update" "Software Update"; do
    if window_up "$title"; then
      wmctrl -c "$title"; log "closed: $title"; closed=1; seen_prompt=1
    fi
  done
  if [ "$closed" = 1 ]; then quiet=0; else quiet=$((quiet + 1)); fi
  if [ "$seen_prompt" = 1 ] && [ "$quiet" -ge 4 ]; then break; fi
  nap 0.5
done
wmctrl -r "Untitled" -b add,maximized_vert,maximized_horz || true

TIMES[total]=$(since "$T0")
python3 - "$BAMBU_DIR/setup_timings.json" "$STUDIO_VERSION" \
  "${TIMES[apt]}" "${TIMES[appimage]}" "${TIMES[plugin]}" "${TIMES[studio]}" "${TIMES[total]}" <<'PY'
import json, sys
path, version, *t = sys.argv[1:]
keys = ["apt_s", "appimage_s", "plugin_s", "studio_window_s", "total_s"]
json.dump({"studio": version, **{k: float(v) for k, v in zip(keys, t)}}, open(path, "w"), indent=1)
PY
log "READY: Studio is on DISPLAY=:99, logged out. Timings in $BAMBU_DIR/setup_timings.json"
