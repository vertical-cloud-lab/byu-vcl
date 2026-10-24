# Two printed C–CS spacer rings for the lid camera, on the A1 mini (2026-10-23)

A stopgap copy of the 5 mm C–CS ring the lid camera needs
([why](../../../../ot2-overhead-camera/lid-mount/camera/README.md#2026-10-23-2120-utc-a-ccs-ring-fits-and-the-knurled-ring-gives-only-about-5-mm)),
asked for on PR #234 as "model the same spacer and print it on the H2D (if available) with very
high-quality settings". The model is
[`cad/c_cs_spacer.py`](../../../../ot2-overhead-camera/lid-mount/cad/c_cs_spacer.py): ring **A**
(one notch on the rim, tighter threads) and ring **B** (two notches, looser), side by side.
They printed in **black** Bambu PLA Basic from AMS slot A3, on the Textured PEI plate.

**Why the A1 mini.** At 22:59:43 UTC Studio's Device page showed the H2D **paused** at layer
75/1041 of another job, `doser_augers_x25_H2D`, with HMS 0300-801E ("The extrusion motor is
overloaded") ([job panel](20261023T225943Z_h2d_job_panel.png)). Nothing on it was clicked. The
requester then wrote "good to go on A1 mini" and "plate clear". By 23:54 the H2D job was running
again, at layer 81 ([job panel](20261023T235440Z_h2d_job_panel.png)), so someone at the printer
had dealt with it.

**How it was sent.** This was the first print from `claude-print.yml`: Bambu Studio on the CI
runner, logged in with the password and an authenticator code computed on the runner, sending
through Bambu's cloud ([`studio/README.md`](../../../studio/README.md#sixth-run-the-ccs-spacer-rings-on-the-a1-mini-2026-10-23)).
A print run has no tailnet, so there was no LAN pre-flight or `watch`. The checks were made on
Studio's Device page, and `studio/watch_studio.py` (A1 mini layout) logged that page.

**Settings.** The process was `0.08mm High Quality @BBL A1M` with wall loops raised from 2 to 6.
That means 0.08 mm layers after a 0.2 mm first layer, and outer walls at 60 mm/s and 2000 mm/s².
With 6 walls, both rings are solid perimeters. Supports were off. Studio found no slicer warnings.

**Outcome:**
- **Timing:** sent at 23:10:45 UTC. Layer 1 started at 23:21:06, after about 10 min of start-up
  (heating, levelling and flow calibration). 100 % at 23:52:53, which is 42.1 min after Send,
  against Studio's 38 min 24 s.
- **Health:** no HMS alert and no error dialog. While printing, the Device page read 219–220 °C
  for the nozzle and 65 °C for the bed. These are OCR readings, so they're approximate.
- **A gap in the log:** the watcher stopped from 23:43:29 to 23:48:04 (layers 59–81). It had been
  run in the background and hit the session's 30 min limit for background commands. It was
  restarted in the foreground. The recording kept running, and a screenshot at 23:47:54 showed
  layer 81, normal temperatures.
- **The parts:** the [last frame](frames/20261023T235410Z_finished.jpg) shows both rings on the
  plate, threaded ends up, with the bridged roof inside each.

**Before use:** cut the 0.4 mm roof disc out of each ring, then try A before B
([how](../../../../ot2-overhead-camera/lid-mount/camera/README.md#2026-10-23-2310-utc-a-printed-ccs-ring-to-use-until-the-bought-one-arrives)).

**Video:** [`recording/c_cs_spacer_A1mini_2026-10-23.mp4`](recording/c_cs_spacer_A1mini_2026-10-23.mp4)
(10.9 min, with [chapters](recording/c_cs_spacer_A1mini_2026-10-23_chapters.txt)). It isn't on
YouTube yet: a print run has no YouTube token, so a plain `@claude` run has to upload it.
- **What it shows:** Studio's first start (4×), the two printers' Device pages (2×), the camera
  frame and the slicing (2×), the fresh check and Send (real time), start-up (16×), layers
  1–111 (24×) and the finish (2×).
- **What's cut:** the login, 22:57:55–22:59:03 UTC, because the e-mail address is on screen, and
  the sign-out from 23:55:05, because the account name shows.
- **What's blurred:** the camera pane's two upper corners, wherever the A1 mini's camera was
  live. Someone walked past at about 23:48.

| File | What |
|---|---|
| [`sent/c_cs_spacer_A1mini.3mf`](sent/c_cs_spacer_A1mini.3mf) | The 3MF Studio uploaded, copied from `/tmp/bamboo_model` at Send. Its plate G-code (MD5 `348a56c4…`) is byte-identical to the slice. Only `DesignerUserId` is blanked |
| [`print.json`](print.json) | Source and commit, the settings changed in the GUI, the Send options, the estimates, the timeline, the go, and the monitor's summary |
| `20261023T230336Z_a1mini_camera_studio.jpg` | The frame posted with the request for the go |
| `20261023T231006Z_*` | The fresh check before Send: camera and Device page |
| `20261023T225943Z_h2d_*`, `20261023T235440Z_h2d_job_panel.png` | The H2D, paused at 22:59 and running again at 23:54 |
| [`frames/`](frames/) | Key frames from the Device page, with the room blurred, and a [montage](frames/montage.jpg) |
| `watch.jsonl.gz` | The watcher's log: one OCR reading of the Device page every 10 s |
