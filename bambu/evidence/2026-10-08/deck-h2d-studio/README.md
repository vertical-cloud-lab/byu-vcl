# The new deck of the lid camera mount, printed on the H2D (2026-10-08)

The OT-2 lid camera mount's **deck with the 3.5 mm camera bosses**
([why](../../../../ot2-overhead-camera/lid-mount/README.md#the-camera-bosses-2026-10-08)),
asked for as ["print that on the h2d in pla"](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6067524181).
It is the lab's first print on the H2D from CI. It printed in **black** Bambu PLA Basic
(AMS 2 Pro slot A2) on the left nozzle, on the Textured PEI plate. Only the deck was printed:
plate 2's Pi spacers and shims haven't changed since the
[2026-10-01 print](../../2026-10-01/deck-studio/README.md).

**How it was sent.** Bambu Studio ran on a CI runner, logged in to the lab's Bambu account,
and sent the job through Bambu's cloud. That is route 3 of the
[runbook](../../../README.md#2-pre-flight), done as in [`studio/README.md`](../../../studio/README.md).
The runbook's [§11](../../../README.md#11-the-h2d) has what the H2D does differently. Two things
shaped this run:
- **The LAN route was shut.** The H2D's TLS certificate matched `H2D_SERIAL`, but its MQTT
  broker refused `H2D_ACCESS_CODE` ("Not authorized"). So there was no `bambu_lan.py`
  pre-flight and no `watch`. The checks were made on Studio's Device page, and
  `studio/watch_studio.py` logged that page.
- **The nozzles are 0.6 mm.** It was sliced in Studio's GUI for the 0.6 mm left nozzle with
  `0.30mm Standard @BBL H2D 0.6 nozzle`, plus the project's 3 walls, 25 % infill and circle
  compensation. At 0.30 mm layers the deck plate comes out 5.1 mm thick and the camera bosses
  3.3 mm tall (CAD: 5.0 and 3.5 mm).

**Outcome:**
- **Timing:** sent at 19:57:42 UTC and finished at about 20:42:17, 44.6 min later, against Studio's
  41 min 4 s estimate. The start sequence took 7.5 min of that.
- **Health:** no HMS alert and no error dialog. While printing, the Device page read 218–222 °C
  for the left nozzle (target 220), 55 °C for the bed and 26–29 °C for the chamber. These are
  OCR readings, so they're approximate.
- **The part:** the last frame shows a flat deck with its four camera bosses, corner sockets
  and ribbon slot.
- **The go and the login code:** both came from @timothy-commins, who also made the request.

**Video:** https://www.youtube.com/watch?v=nrGHKqr7TO0 (unlisted, 10:48, with chapters). It shows:
- Studio's first run and the H2D's Device page (2×);
- *Sync info*, the import, the settings, the slice and the checks (3×);
- Send (1×);
- the start and layer 1 (8×), then layers 2–22 (24×);
- the finished deck (1×).

Three stretches are cut:
- **The Bambu login, 19:39–19:45 UTC,** because the e-mail address is on screen.
- **The Device page's *Update* tab at 19:47,** because it shows serial numbers.
- **20:41:28–20:51:16.** That's layers 23–28 and the end of the print, about 50 s cut by
  mistake, then Studio's idle, closed live view. The video's description calls the 24× chapter
  "Layers 2-28"; it ends at layer 22.

| File | What |
|---|---|
| `20261008T194651Z_h2d_camera_studio.jpg` | The H2D's camera on Studio's Device page, posted with the request for the go. The printer was idle with no HMS alerts and its heaters off. The white outline on the plate is the Bambu logo printed on it |
| `20261008T195643Z_h2d_camera_studio.jpg` | The fresh check after the go, 59 s before Send. Still idle, plate empty |
| `sent/lid_mount_deck_H2D.3mf` | The file Studio uploaded, taken from `/tmp/bamboo_model` where Studio wrote it at Send. Only `DesignerUserId` is blanked. The plate G-code MD5, `e2aec047217f8f8d6c3194c8d218db2c`, is the same as Studio's slice and as a pre-Send *Export plate sliced file* |
| `print.json` | Settings, Send options, estimates, timeline, the go, the monitor's summary, recording |
| `monitor.jsonl.gz` | Every sample `watch_studio.py` took of the Device page: the temperatures, layer and progress read by OCR, every 10 s |
| `frames/` | Key frames from the H2D's camera as Studio showed it: homed, layers 1, 3, 8, 12, 15, 16 and 17, and the finished deck. Also `montage.jpg` |

**Things the next H2D print should know:**
- **Fix the LAN route first if you can.** With `H2D_ACCESS_CODE` up to date, `bambu_lan.py`
  and `bambu_print.py watch` work as on the A1 mini. Studio's Device page plus OCR is a
  fallback.
- **Check the nozzles with *Sync info*.** These were 0.6 mm, not the 0.4 mm the lid-mount
  project is sliced for.
- **Studio's "Finished" isn't the finish.** Once the remaining time reaches 0 min, the job
  panel shows "Finished" where the finish time was, while still printing. Here that happened
  around layer 21 of 28, about 70 s early. The real end is when the "Printing" label goes.
- **Studio closes the live view** some minutes after a print ends ("Temporarily closed because
  there is no printing for a while"). Press ▶ again for a last frame.
