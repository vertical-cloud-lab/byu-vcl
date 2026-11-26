# Plate 2 of the lid camera mount, printed on the A1 mini (2026-10-01)

Plate 2 of the OT-2 lid camera mount, sliced in
[`lid_mount_A1mini_PLA.3mf`](https://github.com/vertical-cloud-lab/byu-vcl/blob/aef4436/ot2-overhead-camera/lid-mount/slice/lid_mount_A1mini_PLA.3mf)
on PR #234. The plate holds:
- the deck;
- 4 Pi 5 standoffs;
- 4 deck shims.

It was printed in dark blue Bambu PLA Basic on Textured PEI.

**How it was sent.** The job went from Bambu Studio on a CI runner, logged in to the lab's Bambu account. This is route 3 of the runbook, [`bambu/README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/aef4436/bambu/README.md) on PR #234.

**Outcome:**
- Sent at 00:32:54 UTC; finished at 01:43:12 UTC.
- No print errors and no HMS alerts.
- The go came from @timothy-commins ("plate clear") after a read-only pre-flight. He also relayed Bambu's e-mailed login code.

**Video:** https://www.youtube.com/watch?v=1gatV4-JgIA (unlisted).

| File | What |
|---|---|
| `20261001T000434Z_*` | First read-only pre-flight. The lab was dark and the plate wasn't visible, so it was HUMAN-DECISION. `_camera_stretched.jpg` is the same frame contrast-stretched |
| `20261001T003128Z_*` | The pre-flight 1.5 min before Send. Every automatic check passed, with the lights on |
| `sent/lid_mount_deck_plate2.3mf` | The file the printer ran, read back from its SD card. Only `DesignerUserId` is blanked; the plate G-code MD5 is `ca26bbee2af5975d7f4e730109ed2690` |
| `print.json` | Settings restored in the GUI, Send options, estimates, timeline, the go, watch summary, recording |
| `watch.jsonl.gz` | Every status sample from `bambu_print.py watch`: two runs, exit 10 then exit 0 |
| `frames/` | Key frames from the printer's camera, and `montage.jpg`. Frames from 01:18 on have their room corners blurred |

**Things the next print should know:**
- **Studio resets settings again.** It reset the same three settings on opening the project: walls, infill and circle compensation. Set them back before slicing (see `print.json`).
- **Plate 1 (the base) is still to print.** It takes about 2 h 32 min, so it needs a session that starts early in working hours.
- **Plate 1 colour.** Plate 1 carries the light collar, which the design wants in black PLA. Only dark blue and pink PLA were loaded on 2026-10-01.
- **Don't start replies with `@claude`.** A reply to a running session that mentions `@claude` starts a second run. On 2026-10-01 it stood down without touching the printer.
