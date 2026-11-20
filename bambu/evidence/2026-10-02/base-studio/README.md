# Plate 1 of the lid camera mount, printed on the A1 mini (2026-10-02)

Plate 1 of the OT-2 lid camera mount: **the base, with its four 96 mm posts** (the "pillars"
in the [request](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5959041505)).
It was sliced in
[`lid_mount_A1mini_PLA.3mf`](https://github.com/vertical-cloud-lab/byu-vcl/blob/b5bb799/ot2-overhead-camera/lid-mount/slice/lid_mount_A1mini_PLA.3mf)
(as of `b5bb799`) and printed in **black** Bambu PLA Basic (AMS Lite slot A3, 0-based 2) on
Textured PEI. Black is what the design asks for, so the light collar blocks room light.

**How it was sent.** The job went from Bambu Studio on a CI runner, logged in to the lab's
Bambu account. This is route 3 of the [runbook](../../../README.md#2-pre-flight), done as in
[`studio/README.md`](../../../studio/README.md).

**Outcome:** 
- Sent at 18:56:41 UTC; finished at 21:22:39 UTC, 146.0 min later against Studio's estimate of 2 h 29 min 41 s.
- No print errors and no HMS alerts. While printing, the nozzle stayed at 218.2–221.5 °C and the bed at 64.5–65.5 °C.
- The go came from @timothy-commins ("plate clear") after a read-only pre-flight, and the same person relayed Bambu's e-mailed login code.

**Video:** https://www.youtube.com/watch?v=inpbxJkVpe8 (unlisted). It covers Studio's setup, the settings restored, the slice,
Send and the export of the sent file at 2×, then the printer camera as a timelapse
(one frame per 30–60 s), then Studio's Device page at the finish. The Bambu login
(18:51–18:53 UTC, e-mail on screen) is cut. The room corners of every camera view are blurred.

| File | What |
|---|---|
| `20261002T184657Z_*` | First read-only pre-flight. Every automatic check passed (HUMAN-DECISION: plate and plate type are always a person's call). This frame went to the thread with the request for the go |
| `20261002T185547Z_*` | The pre-flight 54 s before Send. Every automatic check passed; the frame was unchanged |
| `sent/lid_mount_base_plate1.3mf` | The file Studio sent, exported from Studio during the print (*File → Export → Export plate sliced file*). Only `DesignerUserId` is blanked; the plate G-code MD5 is `d67427660746751fc181933881fecbc1`, the same as Studio's own slice |
| `print.json` | Settings restored in the GUI, Send options, estimates, timeline, the go, watch summary, recording |
| `watch.jsonl.gz` | Every status sample from `bambu_print.py watch`, all runs |
| `frames/` | Key frames from the printer's camera, room corners blurred, and `montage.jpg` |

**Things the next print should know:**
- **Request to Send in 12 min.** The go and the login code came within 40 s of being asked
  for, from the person who made the request. That is the fastest Studio run so far.
- **Studio picked black by itself.** The project's filament is black, and Send mapped it to
  slot A3, the black PLA Basic, without being asked. Check the mapping anyway.
- **Studio resets settings again.** It reset the same three settings on opening the project:
  walls, infill and circle compensation. Set them back before slicing (see `print.json`).
- **The sent file can be exported mid-print.** *Export plate sliced file* doesn't touch the
  printer, and its plate G-code was byte-identical to the slice Send used. That saves reading
  it back from the SD card after the print, when the session's clock is short.
- **The session clock.** Bambu's 2 h 30 min estimate plus 12 min of setup left about
  22 min of the 180 min job after the finish.
