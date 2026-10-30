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
[the third run](#third-run-plate-2-2026-10-01)), and on 2026-10-02 for plate 1, the base
([evidence](../evidence/2026-10-02/base-studio/README.md); see
[the fourth run](#fourth-run-plate-1-the-base-2026-10-02)).

Nothing here changes the rules in the runbook. The pre-flight, the plate check (a Device-page
frame posted first, then 5 minutes for anyone to object; no `plate clear` reply) and the
watching all still apply. This route skips `bambu_print.py start`, so its gates are applied by
hand: a pre-flight under 15 min old, and a fresh camera frame read before Send. The runs below
predate 2026-10-23, so they still wait for a person's `plate clear`.

## Files

| File | What |
|---|---|
| [`studio.sh`](studio.sh) | Starts Studio on display `:99` with software GL and WebKit compositing off (the login and home pages are WebKit views) |
| [`ui.py`](ui.py) | `xdotool` wrapper: smooth pointer moves (they show in a recording), clicks, keys, and `typeenv VAR`, which types a secret from the environment through stdin, so it never appears in argv or a log |
| [`shot.sh`](shot.sh) | Screenshot of `:99`, to find the next thing to click |
| `bambu-totp` | Not in this folder: `claude-print.yml` installs it on the runner. Writes the account's current authenticator code to stdout, for piping into `xdotool` (see [Logging in](#logging-in-password-plus-an-authenticator-code)) |
| [`watch_studio.py`](watch_studio.py) | Watches a print from Studio's Device page when the LAN route is shut (the H2D, 2026-10-08; any printer in a `@claude-print` run): reads temperatures and layer by OCR every 10 s, saves camera frames, stops on a new dialog, a hard limit, a stall or a blank camera. `WATCH_LAYOUT=a1mini BED_TARGET=65` for the A1 mini's page |
| [`cut_recording.py`](cut_recording.py) | Builds the video to publish from the recorder's 5 min segments, by wall-clock time and speed per part, so the login is never in it; blurs the camera pane's upper corners where the room shows, and writes YouTube chapters |

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
4. **Login/Register** opens a WebKit page: e-mail, password, *Log In*, then the authenticator
   code. See [Logging in](#logging-in-password-plus-an-authenticator-code).
5. **"Synchronise your personal data from Bambu Cloud?"**: *No*. The project brings its own
   presets.

## Logging in: password plus an authenticator code

Since 2026-10-15 the lab account has authenticator-app 2-step verification, and only an
approved `@claude-print` run can log in. That run is [`claude-print.yml`](../../.github/workflows/claude-print.yml);
see "Printing on the lab's Bambu Lab printers" in [CLAUDE.md](../../CLAUDE.md). Plain `@claude`
runs no longer get `BAMBU_USERNAME` or `BAMBU_PASSWORD`, so they can prepare a print but not
send it.

1. Type the e-mail address and password from the environment, never as arguments:
   `python ui.py typeenv BAMBU_USERNAME`, then `python ui.py typeenv BAMBU_PASSWORD`, and press
   *Log In*. The runs up to 2026-10-08 also ticked *I agree*; on 2026-10-15 the page had no such
   box. With Studio maximised, the Login window (648 × 819) opened centred, and these held:
   e-mail field (960, 246), password field (930, 296), *Log In* (960, 374).
2. Bambu then shows **Identity Verification**: "Please enter the 6-digit verification code from
   the identity authentication app (Such as Google Authenticator, Duo Mobile)"
   ([screenshot](../evidence/2026-10-15/login-test/authenticator-dialog.png)). Click the first
   box, (751, 551), and type the current code with
   `bambu-totp | DISPLAY=:99 xdotool type --delay 90 --file -`. Then click *Confirm*, (960, 632).
   Inside the last 5 s of a 30 s window, `bambu-totp` waits for the next one, so the code can't
   expire between typing and confirming.
   - The six boxes are about 42 px square, centred on y 551 at x 751, 835, 918, 1002, 1086 and
     1169. One `xdotool type` fills all six: each digit moves the focus on.
   - It doesn't submit itself. *Confirm* spans x 713–1206, y 612–651. The ✕ is at (1198, 455).
   - The dialog is drawn inside the Login window, so `wmctrl -l` still lists only *Login*.
     Behind it, the e-mail address stays readable through the grey.
3. If Bambu asks for an **e-mailed** code instead, stop and say so in the thread. **Never ask
   anyone to post an e-mailed code, and never post one.** Bambu accepts the account's e-mail
   address plus a current e-mailed code as a complete login, with no password, even with 2-step
   verification on
   ([robot-arms PR 10](https://github.com/vertical-cloud-lab/robot-arms/pull/10#issuecomment-6140001145),
   [ha-bambulab PR 2058](https://github.com/greghesp/ha-bambulab/pull/2058)). A code posted in
   this thread is the account until it expires.

The runs up to 2026-10-08 logged in with that e-mailed code: a person posted it here and
`wait_code.py` typed it. The run logs below still describe that. `wait_code.py` has been
deleted, but it is in git history.

The typed e-mail address shows on screen until the login closes. So cut that stretch from any
recording, mask it in any screenshot that leaves the runner, and delete the raw recording
afterwards.

**The first login this way, 2026-10-15** ([issue #281](https://github.com/vertical-cloud-lab/byu-vcl/issues/281),
a login test with no print). Bambu asked for the authenticator code, not an e-mailed one, and the
first code worked: *Log In* at 17:01:05 UTC, the code typed at 17:01:36, *Confirm* at 17:01:45.
Five seconds later the Login window had closed and the *Synchronise* prompt was up. What else it
found:

- **Studio selects a printer by itself.** Once logged in, it picks the account's last-selected
  printer (or else the first on the list), here the A1 mini, and connects to it through Bambu's
  cloud, with no click (`DeviceManager::load_last_machine`; it lands in
  `app.user_last_selected_machine` in `~/.config/BambuStudio/BambuStudio.conf`). The printer is
  selected before anyone opens the Device page.
- **The Device page fetches a camera still by itself.** In 02.08.02.61, showing the Device page
  makes Studio download a "Printer Preview" still from the selected printer's camera, by LAN and
  then the cloud (`MediaPlayCtrl::on_show_hide` → `start_device_image_flow`, if the printer's
  firmware sets bit 42 of `cfg`). The live video still waits for ▶. So a run told not to open a
  camera shouldn't open the Device page. This one didn't.
- **After login, `BambuStudio.conf` holds the printers' LAN access codes**: an
  `access_code.<serial>` entry for each printer on the account. Never upload or commit
  `~/.config/BambuStudio`, for example as a job artifact. Those keys are also how this run
  confirmed both printers are on the account without opening the Device page: there was one for
  `H2D_SERIAL` and one for `A1_MINI_SERIAL`, matched without printing either.
- **The sidebar shows the account's name** (`user_` and digits), not the e-mail address. It's
  masked in the [signed-in screenshot](../evidence/2026-10-15/login-test/signed-in-home-masked.png)
  all the same.

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

## Fourth run: plate 1, the base (2026-10-02)

Asked for on [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5959041505)
as "the pillars": the four posts are part of the base, plate 1. The record is in
[`../evidence/2026-10-02/base-studio/`](../evidence/2026-10-02/base-studio/README.md).

| UTC | Step |
|---|---|
| 18:44:24 | Request |
| 18:46:57 | Read-only pre-flight: idle, no errors, black PLA Basic in slot A3 |
| 18:47:47 | Frame posted, go and hand-off asked for |
| 18:48:07 | Recording started, then Studio's first run (wizard, *Cancel* on the profile update, Beta prompts, plug-in) |
| 18:51:37 | *Log In* pressed |
| 18:52:03 | The go (`plate clear`) |
| 18:52:31 | Login code typed, 6 s after it was posted |
| 18:54:55 | Plate 1 sliced in the GUI, after the same three settings were set back |
| 18:55:47 | Fresh pre-flight |
| 18:56:41 | *Send*; `RUNNING` by 18:57:26 |
| 19:03:48 | Layer 1, 7.1 min for the whole 112 mm footprint |
| 21:22:39 | `FINISH`, 146.0 min after Send (Studio's estimate: 2 h 29 min 41 s). `watch` exited 0 with no error or HMS alert |

What was new:
- **Black PLA is loaded now** (slot A3, 0-based 2), and Send mapped the project's black
  filament to it by itself.
- **The camera pane changes size.** Studio first showed the live view letterboxed in the
  pane, then filling it. The room-corner boxes above fit the second layout. For a recording
  that spans both, blur the union: 296 × 341 at (274, 136) and 258 × 274 at (1040, 136).
- **The sent file was exported mid-print**, at 19:02, with *File → Export → Export plate
  sliced file*. Its plate G-code had the same MD5 as Studio's slice in `/tmp/bamboo_model`.
  Nothing has to be read back from the SD card after the print.
- **The GUI reset the same three settings again.** After they were set back, the GUI's plate 1
  matched the committed plate layer for layer: 511 layers to Z 102.2, 81.12 g, and no layer's
  extrusion more than 0.05 mm off. Studio's estimate was 2 h 29 min 41 s against the CLI's
  2 h 32 min 12 s, from the stock acceleration limits.
- **The clock.** A 2.5 h print fits in a 180 min job only if Send comes early. This one was
  sent 12 min into the session. It finished 22 min before the job's 180 min limit.

## Fifth run: the new deck on the H2D (2026-10-08)

Asked for on [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6067524181)
as "print that on the h2d in pla": the deck with the 3.5 mm camera bosses. The record is in
[`../evidence/2026-10-08/deck-h2d-studio/`](../evidence/2026-10-08/deck-h2d-studio/README.md),
and the H2D's differences are in the runbook's [§11](../README.md#11-the-h2d).

| UTC | Step |
|---|---|
| 19:32:00 | Request |
| 19:36 | LAN status read: the TLS certificate matches `H2D_SERIAL`, but the access code is refused |
| 19:36:38 | Recording started, then Studio's first run |
| 19:40:10 | *Log In* pressed |
| 19:44:45 | Login code typed, 6 s after it was posted |
| 19:46 | Device page: H2D idle, no HMS alerts, heaters off; camera frame posted, go asked for |
| 19:49–19:53 | *Sync info* (0.6 mm nozzles), `deck.stl` imported, 3 walls, 25 % infill and circle compensation set, sliced |
| 19:56:17 | The go (`plate clear`) |
| 19:56:43 | Fresh Device-page check and frame |
| 19:57:42 | *Send*; uploaded through Bambu's cloud, and the printer was homing by 19:58:29 |
| 20:05 | Layer 1 |
| 20:41:44 | Layer 28 (from the recording) |
| 20:42:17 | Finished: 100 % and the "Printing" label gone, 44.6 min after Send (estimate: 41 min 4 s). No HMS alert or dialog |

What was new:
- **A new project, not the CLI's 3MF.** The deck was imported from
  `ot2-overhead-camera/lid-mount/exports/deck.stl` into an empty project after *Sync info* had
  set the printer to the H2D. The project's three settings were set on Bambu's
  `0.30mm Standard @BBL H2D 0.6 nozzle`.
- **The sent file is in `/tmp/bamboo_model`.** At *Send*, Studio wrote the 3MF it uploaded
  next to its slice, as `.<pid>.0.3mf`. Its plate G-code was byte-identical to the slice and to
  a pre-Send *Export plate sliced file*. So the sent file can be committed without opening a
  dialog mid-print.
- **The Send dialog defaults to timelapse *On*** for the H2D, and to *Auto* for levelling and
  flow calibration. Set timelapse *Off* and the other two *On*.
- **Studio's slice had no warnings at all**, not even the timelapse one every A1 mini file
  carries.
- **"Finished" shows before the finish.** When the remaining time reaches 0 min, the job panel
  writes "Finished" where the estimated finish time was, while the label on the left still
  says "Printing". Here that came around layer 21 of 28, about 70 s early. `watch_studio.py`
  now waits for 100 % and the "Printing" label to go.
- **Studio closes the live view** a few minutes after the print ends ("Temporarily closed
  because there is no printing for a while"). Press ▶ again for the last frame.
- **The recording is bigger with the camera playing:** 3.4 GB for 75 min at 15 fps, against
  103 MB for 18 min on 2026-09-29. There's room on the runner, but cut segments from it as the
  print goes rather than all at the end.
- **Stop the recorder with `pkill -INT -x ffmpeg`, not `pkill -f <its command line>`.** The `-f`
  pattern also matched the shell running `pkill` and ended it, though the recording was saved.
- **[Recording](https://www.youtube.com/watch?v=nrGHKqr7TO0)** (10:48). The login and the
  *Update* tab, which shows serial numbers, are cut. The 24× chapter ends at layer 22, so
  layers 23–28 and the end of the print, about 50 s, aren't in it.

## Sixth run: the C–CS spacer rings on the A1 mini (2026-10-23)

Asked for on [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6376202869)
as "model the same spacer and print it on the H2D (if available) with very high-quality
settings". It was the first print from [`claude-print.yml`](../../.github/workflows/claude-print.yml),
the run that holds the login. The record is in
[`../evidence/2026-10-23/c-cs-spacer-studio/`](../evidence/2026-10-23/c-cs-spacer-studio/README.md).

| UTC | Step |
|---|---|
| 22:42:14 | Request; the run was approved and started at 22:43:27 |
| 22:51:35 | Recording started, then Studio's first run (wizard, plug-in, *Cancel* on the profile update) |
| 22:57:55–22:58:47 | Login: e-mail and password, then Bambu asked for the authenticator code, and the first `bambu-totp` code worked |
| 22:59:43 | Device page, H2D: **paused** at layer 75/1041 of another job with HMS 0300-801E, so not used |
| 23:00:54 | Device page, A1 mini: idle, no HMS alert, heaters off |
| 23:04:25 | Camera frame posted, go asked for |
| 23:05:37 | The go (`plate clear`), after "good to go on A1 mini" from the requester |
| 23:05–23:09 | *Sync info*, both STLs imported, `0.08mm High Quality @BBL A1M` with 6 walls, black PLA from A3, sliced |
| 23:10:06 | Fresh Device-page check and frame |
| 23:10:45 | *Send* |
| 23:21:06 | Layer 1, after about 10 min of start-up (heating, levelling, flow calibration) |
| 23:41:20 | Layer 57: the roof bridged across both bores |
| 23:43:29–23:48:04 | No watcher samples: run in the background, it hit the session's 30 min limit for background commands; restarted in the foreground (the recording ran throughout) |
| 23:52:53 | Finished: 100 %, layer 111/111, 42.1 min after Send (estimate: 38 min 24 s). No HMS alert or dialog |
| 23:54:40 | Device page, H2D: its job running again, at layer 81 |
| 23:55:05 | Signed out of the Bambu account, then Studio closed and its config deleted |

What was new:
- **No LAN route in a print run.** `claude-print.yml` has no Tailscale step and no `*_IP` or
  `*_ACCESS_CODE` secrets, so `bambu_lan.py` and `bambu_print.py` can't run there. The pre-flight
  and the watching happened in Studio, as on the H2D (runbook §11). `watch_studio.py` gained an
  A1 mini layout for this (`WATCH_LAYOUT=a1mini BED_TARGET=65`): the page has one nozzle line
  and no chamber line.
- **The login took under a minute**, from *Login/Register* to the *Synchronise* prompt, with the
  click positions in [Logging in](#logging-in-password-plus-an-authenticator-code). Nobody had
  to post anything.
- **A paused printer shows its error dialog as soon as it's selected.** Picking the H2D on the
  Device page popped up *Warning: The extrusion motor is overloaded … [0300-801E]*, with
  *Resume (problem solved)* and *Check Assistant*. Both act on someone else's print, so neither
  was clicked. Moving the window aside (`wmctrl -r Warning -e 0,1480,860,-1,-1`) and selecting
  the A1 mini hid it; the job panel's *Clear* wasn't touched either.
- **The Prepare page started on "Bambu Lab A1", not the mini,** even with the A1 mini selected
  on the Device page. *Sync info* fixed it (a dialog asks to sync the preset to the connected
  printer). Press it before importing anything.
- **Importing:** *Ctrl+I*, then *Ctrl+L* in the file dialog, type the path, *Return*. The
  second *Ctrl+I* did nothing until the canvas was clicked first.
- **The AMS sync dialog** (the icon right of the filament list) maps the project's filament to
  an AMS slot by colour and type. Untick *Add unused AMS filaments to filaments list* to keep a
  single filament.
- **OCR on the A1 mini page** reads the bed's "41 /65" as "41 165". The watcher's hard limits
  now use the current temperature only, and the target is just a note.
- **No YouTube token in a print run either,** so the cut recording is committed with the
  evidence, and a plain `@claude` run can upload it.
  [`cut_recording.py`](cut_recording.py) makes it from the recorder's segments by wall-clock
  time, so the login can't slip in, and blurs the camera pane's upper corners where the room
  shows.

## Seventh run: six more C–CS rings, sliced but not sent (2026-10-28)

Asked for on [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6474970526):
"get at least 5 more sizes spaced a bit bigger". The record is in
[`../evidence/2026-10-28/c-cs-spacer-sizes-studio/`](../evidence/2026-10-28/c-cs-spacer-sizes-studio/README.md).
It was the first print run under the 2026-10-23 plate rule (frame first, no `plate clear`), and
it stopped without sending, because the plate was never clear.

| UTC | Step |
|---|---|
| 16:43:53 | Request; the run was approved and started by 16:45 |
| 16:52:32 | Recording started, then Studio's first run |
| 16:55:10–16:56:10 | Login: password, then the first `bambu-totp` code worked |
| 16:57:04 | First frame from the Device page: the A1 mini idle, but the previous job's print still on the plate |
| 16:58:04 | Frame posted in the tracking comment; part removal asked for |
| 16:58–17:08 | Rings C–H modelled; the 23 Oct G-code checked against the model |
| 17:08–17:12 | Sliced: *Sync info*, one STL with six bodies, `0.08mm High Quality @BBL A1M`, 6 walls, AMS sync to A3 |
| 17:16–18:55 | Waiting: the thread polled every 20 s, a frame every 3–4 min, no change on the plate |
| 17:32 | The sliced plate exported (*Export plate sliced file*) and committed, ready to send |
| 17:43:50 | The H2D checked read-only: busy, with warning 0700-8010 |
| 18:55:20 | Stopped at the cutoff stated in the thread; signed out at 18:55:45, Studio closed, its config deleted |

What was new:
- **An occupied plate, and nobody to tell.** The run can only edit its tracking comment, and
  GitHub sends no notification for an edit. So a request to clear the plate made there reaches
  only someone who happens to look at the thread. The person who triggers the run should be ready
  to check the printer, or say who will.
- **Studio's live view closes itself** after a few minutes with nothing printing ("Temporarily
  closed because there is no printing for a while"). Press ▶ again before each frame. When it's
  closed, the green ▶ sits at (294, 732); while playing, the pane is taller and the button is at
  (294, 814).
- **Catching a change on the plate without a reply.** The mean absolute difference between a
  frame's plate region and the first frame's stayed at 1.5–1.9 of 255 all session. A part being
  removed would move it far more.
- **One STL with six bodies** imports as one object, centred on the plate, with no prompt. Its
  layout then fixes which ring is where, which helps tell the rings apart afterwards.
- **The token re-mint works in a print run.** `claude-print.yml` has `id-token: write`, and
  `scripts/refresh_github_app_token.py` (on `main`) re-minted at 17:32, 18:19 and 19:10.
- **The recorder's segments keep running timestamps.** Without `-reset_timestamps 1`, a
  Matroska segment reports its end time as its duration (600 s for the second 5 min segment).
  `cut_recording.py` now subtracts the start time; before, its pieces overlapped and the first cut
  came out three times too long.

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

