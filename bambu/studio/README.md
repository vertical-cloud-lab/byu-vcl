# Printing through Bambu Studio's GUI from CI

This is route 3 in the runbook ([`../README.md`](../README.md#2-pre-flight), "Firmware and
authorisation"). With the printer on Bambu's cloud, its firmware accepts control commands
only when Bambu's own apps sign them. Here Bambu Studio itself runs on the runner, logged in to
the lab's Bambu account, and sends the job through Bambu's cloud. It worked the first time
(2026-09-27, the lid mount's fit coupon on the A1 mini;
[evidence](../evidence/2026-09-27/fit-coupon-studio/)). The printer was `RUNNING` 27 s after
Send, where the LAN `start` an hour earlier had been refused with HMS `0500-0500-0001-0007`.
It worked again on 2026-09-29 for the drill template, plate 3
([evidence](../evidence/2026-09-29/drill-template-studio/); see
[the second run](#second-run-the-drill-template-2026-09-29) below), and on 2026-10-01 for
plate 2, the deck ([evidence](../evidence/2026-10-01/deck-studio/README.md); see
[the third run](#third-run-plate-2-2026-10-01)).

Nothing here changes the rules in the runbook. The pre-flight, the person's go and the watching
all still apply. This route skips `bambu_print.py start`, so its gates are applied by hand: a
pre-flight under 15 min old, and a camera frame read before Send.

## Files

| File | What |
|---|---|
| [`studio.sh`](studio.sh) | Starts Studio on display `:99` with software GL and WebKit compositing off (the login and home pages are WebKit views) |
| [`ui.py`](ui.py) | `xdotool` wrapper: smooth pointer moves (they show in a recording), clicks, keys, and `typeenv VAR`, which types a secret from the environment through stdin, so it never appears in argv or a log |
| [`shot.sh`](shot.sh) | Screenshot of `:99`, to find the next thing to click |
| [`wait_code.py`](wait_code.py) | Checks the PR thread (#234, or `PR_NUMBER`) every 2 s for a 6-digit code from someone with write access, then types it into Studio's verification dialog. It never prints the code |

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
if more than a few minutes pass. Ask for the bare digits, without `@claude`: a comment that
mentions it starts another run (2026-10-01; see [the third run](#third-run-plate-2-2026-10-01)).
What the code proves is a person's inbox, so no session can get around it. That is the check
working as intended.

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

## Second run: the drill template (2026-09-29)

The same steps, start to finish, in 18 min from a fresh runner to Send:

| UTC | Step |
|---|---|
| 18:27 | AppImage downloaded and extracted (about 20 s); apt packages installed in the background |
| 18:28 | Read-only pre-flight of plate 3: HUMAN-DECISION, with a camera frame that needed explaining (below) |
| 18:29–18:32 | First run of Studio: certificate prompt, wizard, *Cancel* on the profile update, three Beta prompts, plug-in installed |
| 18:32:42 | *Log In* pressed; Bambu e-mails the code, and the thread is asked for it |
| 18:39:27 | The code is posted; `wait_code.py` typed it 6 s later and it worked. So a code is still good after at least 6 min 45 s |
| 18:39:54 | The go, with the frame explained |
| 18:41 | Plate 3 sliced in the GUI, after the same three settings were set back (below) |
| 18:43:45 | Fresh pre-flight |
| 18:44:46 | *Send*; the printer was `RUNNING` 26 s later |
| 19:37:42 | `FINISH`, 52.9 min after Send (Bambu's estimate: 51 min 26 s). `watch` exited 0 with no error or HMS alert |

What was new:
- **The camera rides on the gantry.** The first frame looked nothing like 2026-09-27's: it looked
  down at the plate from above, with the counter and the room behind the printer, and no
  Safety Zone sticker. The last job, a 125-layer part (`side_bracket`), had left the gantry
  parked high. Once the new print homed, the familiar low view came back. So a high view isn't a
  moved printer, but it does show things behind the bed that the low view hides. A person
  confirmed the bed's path before the go.
- **The GUI reset the same three settings again** (wall loops, sparse infill density, circle
  compensation). After they were set back, the GUI's G-code extruded the same amount on each
  of the 10 layers as the committed plate 3, to 0.01 mm of filament. Only the acceleration
  limits differed, as before, so the estimate was 51 min 26 s instead of 51 min 32 s.
- **The dialog coordinates in `wait_code.py` held.** With Studio maximised on the 1920×1080
  display, the code field and *Confirm* were where they were on 2026-09-27.
- **Layer 6 took 10.8 min.** It's the first solid layer over the infill. That's inside
  `watch`'s 15 min stall limit, but a bigger flat part could exceed it and end the watch
  (exit 20) while nothing is wrong.
- **Recorded from 19:22 only** ([video](https://www.youtube.com/watch?v=M6w4-SVw9tg)). The
  request to record every session came mid-print, so the login, slicing and Send are missing.

## Third run: plate 2 (2026-10-01)

Asked for on [PR #84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-5921915472),
where the record was first committed; it is now in
[`../evidence/2026-10-01/deck-studio/`](../evidence/2026-10-01/deck-studio/README.md), with
the timeline in its `print.json`. Sent at 00:32:54 UTC, `RUNNING` 25 s later, `FINISH` at
01:43:12: 70.3 min, against Bambu's 69 min 16 s. No error or HMS alert.

What was new:
- **A dark lab.** The first pre-flight, at 00:04, found the chamber light on and the frame
  black (mean luma 3.6/255). The session set up Studio and sliced while it waited, and sent
  nothing until the go came at 00:26, by which time the lights were on (mean luma 54.9).
- **Duplicate runs.** The go and the login code were both posted with `@claude`, so each
  started another run. Both stood down without touching the printer, and the running
  session still read the code and typed it 5 s after it was posted.
- **The GUI reset the same three settings again.** After they were set back, the GUI's plate 2
  had the committed plate's 55 layers to Z 11.0, its 43.50 g, temperatures and start G-code.
  Per-layer extrusion differed by at most 0.8 mm of filament on 14 layers, i.e. one retract
  more or fewer.
- **Layer 21 took 8.6 min.** It's the deck's solid top, and the longest layer of the plate:
  inside `watch`'s 15 min stall limit.
- **Recorded from Studio's setup to the finish**
  ([video](https://www.youtube.com/watch?v=1gatV4-JgIA), 7 min 24 s): Studio's setup and
  slicing at 2×, then Send, then the printer camera as a timelapse to the finish. The login
  and a 15 min idle wait for the go were cut, and the room corners of the camera frames
  blurred.

## Recording and keeping the sent file

Rule 8 of the runbook asks for both. What worked on 2026-09-29:

- **Recording.**
  - Start before Studio opens:
    `ffmpeg -f x11grab -framerate 15 -video_size 1920x1080 -i :99.0 -c:v libx264 -preset ultrafast -crf 23 -pix_fmt yuv420p raw.mkv`.
  - Stop it with SIGINT so the file is finalised. 18 min came to 103 MB.
- **People on camera.** The camera rides on the gantry, so whenever the gantry is high it
  sees the room, and people walking past show up at the corners of the frame.
  - Stop Studio's live view (■ under the camera pane) once the print is done.
  - Before uploading, blur the room corners. These boxes are in screen pixels for Studio's
    camera pane: 244 × 341 at (274, 136) and 213 × 274 at (1085, 136). For LAN frames, blur
    (0, 0)–(400, 560) and (1330, 0)–(1680, 450).
- **The login.** Cut everything from *Log In* until the verification dialog closes, because the
  e-mail address is on screen.
- **Uploading.**
  - Use `python youtube/yt_service.py upload VIDEO --title … --description … --privacy unlisted`.
    The script is on `main`.
  - Put a link to the thread's comment in the description, add chapters, then post the
    video's link in the thread.
- **The file that was sent.**
  - The printer keeps the file it ran on the SD card, as `/cache/<job>.3mf`, next to
    `<job>_plate_N.gcode`. A read-only FTPS `RETR` gets it. That copy is what's committed.
  - It carries the lab account's `DesignerUserId` in `3D/3dmodel.model`, so blank that first.
    The plate G-code and its MD5 are untouched by this.
  - Studio's *File → Export → Export plate sliced file* gives the same plate G-code, byte for byte.
- **Metadata.** Commit a `print.json` next to the file. See
  [the drill template's](../evidence/2026-09-29/drill-template-studio/print.json) for the fields.

