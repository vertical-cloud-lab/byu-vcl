# Printing through Bambu Studio's GUI from CI

This is route 3 in the runbook ([`../README.md`](../README.md#2-pre-flight), "Firmware and
authorisation"). With the printer on Bambu's cloud, its firmware accepts control commands
only when Bambu's own apps sign them. Here Bambu Studio itself runs on the runner, logged in to
the lab's Bambu account, and sends the job through Bambu's cloud. It worked the first time
(2026-09-27, the lid mount's fit coupon on the A1 mini;
[evidence](../evidence/2026-09-27/fit-coupon-studio/)). The printer was `RUNNING` 27 s after
Send, where the LAN `start` an hour earlier had been refused with HMS `0500-0500-0001-0007`.

Nothing here changes the rules in the runbook. The pre-flight, the person's go and the watching
all still apply. This route skips `bambu_print.py start`, so its gates are applied by hand: a
pre-flight under 15 min old, and a camera frame read before Send.

## Files

| File | What |
|---|---|
| [`studio.sh`](studio.sh) | Starts Studio on display `:99` with software GL and WebKit compositing off (the login and home pages are WebKit views) |
| [`ui.py`](ui.py) | `xdotool` wrapper: smooth pointer moves (they show in a recording), clicks, keys, and `typeenv VAR`, which types a secret from the environment through stdin, so it never appears in argv or a log |
| [`shot.sh`](shot.sh) | Screenshot of `:99`, to find the next thing to click |
| [`wait_code.py`](wait_code.py) | Checks the PR thread every 2 s for a 6-digit code from someone with write access, then types it into Studio's verification dialog. It never prints the code |

## Setup (about 2 min on a runner)

```bash
curl -LO https://github.com/bambulab/BambuStudio/releases/download/v02.08.02.61/BambuStudio_ubuntu24.04-v02.08.02.61-20260820225108.AppImage
chmod +x BambuStudio_*.AppImage && ./BambuStudio_*.AppImage --appimage-extract   # to ~/bambu/squashfs-root
sudo apt-get install -y libwebkit2gtk-4.1-0 libgstreamer-plugins-base1.0-0 gstreamer1.0-plugins-good \
    gstreamer1.0-libav xdotool imagemagick openbox wmctrl ffmpeg
Xvfb :99 -screen 0 1920x1080x24 &  DISPLAY=:99 openbox &
./studio.sh &
```

To record it: `ffmpeg -f x11grab -framerate 15 -video_size 1920x1080 -i :99.0 -c:v libx264 -preset ultrafast -f segment -segment_time 300 raw_%03d.mkv`.
`xdotool` moves the real X pointer, so the pointer shows in the video without an overlay.

## First run, in order

1. **"Use system SSL certificate"**: tick *Remember my choice*, then *Yes*.
2. **Setup wizard**, which appears at every first start:
   - login region *North America*;
   - *Skip* the data-sharing programme;
   - keep the default printers and filaments;
   - leave *Install Bambu Network plug-in* ticked, then *Finish*. The plug-in is about 32 MB
     and lands in `~/.config/BambuStudio/plugins`. Studio can't log in without it.
3. **Pop-ups after the wizard:**
   - Three *Beta available* prompts: *Don't show me Beta updates again*.
   - A *Configuration update* (profile package): **Cancel**. That keeps the profiles bundled with
     the release, the ones `slice_a1mini.py` sliced with.
4. **Login/Register** opens a WebKit page: e-mail, password, *I agree*, *Log In*.
5. **"Synchronise your personal data from Bambu Cloud?"**: *No*. The project brings its own
   presets.

## The e-mail code: a person has to relay it every session

Bambu asks for an e-mailed verification code on every login from a new device, and every CI
runner is a new device. On 2026-09-27:
- **The first code expired unused.** A person posted it 20 min after it was sent, and Bambu
  answered "Code does not exist or has expired".
- **The dialog's *Send verification code* link sends a new one.** The second code was posted a
  minute after it was sent. `wait_code.py` typed it 4 s later, and it worked.

So ask for the code in the thread only when someone is ready to answer, and request a fresh one
if more than a few minutes pass. What the code proves is a person's inbox, so no session can
get around it. That is the check working as intended.

The typed e-mail address shows on screen until the login closes, and the verification dialog
repeats it. So cut that stretch from any recording, mask it in any screenshot that leaves the
runner, and delete the raw recording afterwards.

## The GUI resets a CLI project's changed settings

**Check this before every Send.** When the GUI opened `lid_mount_A1mini_PLA.3mf`, it quietly
used Bambu's stock process preset. No dialog appeared, and the preset showed no *modified*
mark:

| Setting | In the project | In the GUI after loading |
|---|---|---|
| Wall loops | 3 | 2 |
| Sparse infill density | 25 % | 15 % |
| Auto circle contour-hole compensation | on | **off** |
| Machine max acceleration X / Y / travel | 6000 / 6000 / 6000 | 20000 / 20000 / 9000 (Bambu's stock values) |

**The likely cause:** `slice_a1mini.py` writes flattened presets that keep the system preset's
name, and the 3MF's `different_settings_to_system` is empty. So the GUI takes the stock preset
of that name and ignores the rest.

**Circle compensation is the one that matters.** The fit predictions assume it's on. With it
off, holes print 0.2–0.4 mm small.

**How to check.** Studio writes each slice to
`/tmp/bamboo_model/<date>/<time>#<pid>#<n>/Metadata/.<pid>.0.gcode`. Compare its
`; CONFIG_BLOCK` with the committed `plate_N.gcode`. After setting the first three back (the
*Advanced* toggle shows circle compensation under *Quality → Precision*), the two agreed on:
- 2.46 g of filament;
- bed 65 °C;
- Bambu's start G-code, with `M620 S0A` and `M412 S1`;
- a 12.4 mm top.

The acceleration limits were left at Bambu's stock values, which is what any Studio user gets,
so the estimate was 15 min 23 s instead of 15 min 31 s. Two derived keys,
`skeleton_infill_density` and `skin_infill_density`, followed the new infill value in the GUI.

## Sending

- *Print plate* opens *Send print job*. Check each of these:
  - the printer (the A1 mini is "Thumbelina, the A1 Mini");
  - the plate type (PEI);
  - the AMS slot for each filament (A1 is 0-based slot 0);
  - **Timelapse off**;
  - *Auto Bed Leveling* and *Flow Dynamics Calibration* on.
- The job name defaults to `<project>_<plate name>`, and "Fit coupon" put a space in it. A
  space broke the LAN path before (0500-C010), so rename the job with the pencil icon.
- After *Send*, Studio says "Successfully sent" and switches to the Device page. The printer
  was `RUNNING` (heating) 27 s after the click.
- Start `bambu_print.py watch` only once a status read shows `PREPARE` or `RUNNING`. Started on
  an idle printer, it exits at once with "nothing is printing".

## While it prints

- **Stopping.** The Device page has **Pause** (orange) and **Stop** (red) next to the progress
  bar. Studio signs them, so they work where `bambu_print.py stop` is refused. Keep Studio open
  and logged in until the print ends; it is the only stop the session has.
- **Two camera feeds at once.** Studio's live view (the ▶ under the camera pane) played through
  the plug-in on the runner. `watch` kept getting a LAN frame every 30 s at the same time, so
  the camera served both.
