# Aurora PCL stud camera mounts, all-printed, on the H2D (2026-11-09/10)

Asked for in [issue #336](https://github.com/vertical-cloud-lab/byu-vcl/issues/336): print
both all-printed designs from
[borysgroup/aurora-cloud-infra PR 29](https://github.com/borysgroup/aurora-cloud-infra/pull/29)
(`design/stud-camera-mount/printed/`, commit `bc71e1a`) on the H2D, or one of them on the
A1 mini if the H2D wasn't available. The details are in [`print.json`](print.json).

**Result: paused at layer 4 of 556.** One plate held one complete Pi Zero mount and one
complete HQ mount, 15 parts in all, and was sent at 00:34:37 UTC. Layer 1 looked clean.
From layer 2 (about 01:19), loose curled strands piled up over the parts at the back centre
and right, so the run paused the job at 01:30:02. It did not stop it, and left the decision to
a person at the printer.

## What happened

1. **H2D first** ([frame](20261109T232254Z_h2d_camera_studio.jpg)):
   - Idle, plate empty.
   - HMS: only a lubrication reminder.
   - Nozzles: **0.4 mm standard and 0.6 mm TPU high flow**
     ([Printer Parts](20261109T232300Z_h2d_printer_parts.png)). The 0.6 breaks CLAUDE.md's
     0.2/0.4 mm rule, so the run first fell back to the A1 mini.
2. **A1 mini:**
   - 0.4 mm nozzle ([Printer Parts](20261109T232800Z_a1mini_printer_parts.png)).
   - Its last job, *Bottom (1)*, was probably still on the plate.
   - **Its camera never loaded** (`[2:2]`, 11 tries from 23:24 to 00:06;
     [crop](20261109T233800Z_a1mini_camera_failed.png)), so its plate couldn't be judged.
   - The Pi Zero mount alone was sliced for it
     ([`sliced/aurora_pizero_head_A1mini.gcode.3mf`](sliced/aurora_pizero_head_A1mini.gcode.3mf),
     3 h 47 min, 83 g) and not sent.
3. **sgbaird, 00:14 UTC:** "Assume the one on the left is the 0.4 and run it on the h2d".
   - Studio's *Sync info* confirmed it: left 0.4, right 0.6
     ([dialog](20261110T001900Z_h2d_switch_diameter.png)).
   - Studio prints from one nozzle when the diameters differ, so the job used the left one only.
4. **The plate** ([slice](20261110T002811Z_h2d_slice_result.jpg)):
   - Parts: all 15 printed parts, i.e. yoke, case and back cover for the Pi Zero; yoke, tub,
     HQ retainer, carrier, Pi 5 retainer and Wide nose for the HQ; 2 thumb nuts; 4 tilt screws.
   - Settings: PR 29's, on Bambu's stock `0.20mm Standard @BBL H2D`. That is 0.16 mm layers,
     6 walls, 6 top / 5 bottom, 40 % gyroid, and 100 % rectilinear on the nuts and screws
     (set per object).
   - Filament: black PLA Basic from AMS A2. Textured PEI at 55 °C.
   - 556 layers, 257 g, 10 h 3 min.
5. **The go:**
   - Fresh frames at [00:29:49](20261110T002949Z_h2d_liveview.jpg) and
     [00:33:40](20261110T003340Z_h2d_liveview_presend.jpg), both of an empty plate.
   - The thread was polled from 00:18 to 00:33 with no reply.
   - *Send* at 00:34:37, with timelapse off and levelling and flow calibration on
     ([dialog](20261110T003500Z_h2d_send_dialog.png)).
6. **Start:** layer 1 at about 00:46, after an 11.6 min start-up. The left nozzle held 220 °C
   and the bed 55 °C.
7. **Strands from layer 2:**
   - The [stack](frames/20261110T010546Z-012741Z_back_of_plate_stack.jpg) shows the back of
     the plate from 01:05 to 01:27, and the
     [full-screen frame](frames/20261110T012900Z_L3_strands_fullscreen.jpg) the strands at 01:29.
   - Paused at 01:30:02 ([Device page](20261110T013010Z_h2d_paused_device_page.jpg)).

## Files

| File | What |
|---|---|
| `20261109T2320*`–`232300Z_*` | The H2D at the start: camera, HMS, Printer Parts |
| `20261109T2328*`–`233800Z_*` | The A1 mini: Printer Parts, Device page, its slice, the camera error |
| `20261110T000703Z_h2d_liveview.jpg` | The H2D's live view, posted with the plan |
| `20261110T001900Z_h2d_switch_diameter.png` | Studio's *Switch diameter* dialog: left 0.4 mm, right 0.6 mm |
| `20261110T002811Z_h2d_slice_result.jpg` | Studio's slice of the H2D plate |
| `20261110T002949Z_*`, `20261110T003340Z_*` | The frames before Send |
| `20261110T003500Z_h2d_send_dialog.png`, `20261110T003517Z_h2d_job_panel.png` | Send options; the job on the Device page |
| `20261110T013010Z_h2d_paused_device_page.jpg` | The Device page after the pause |
| [`sent/aurora_camera_mounts_zero_hq_H2D.3mf`](sent/aurora_camera_mounts_zero_hq_H2D.3mf) | The 3MF Studio uploaded, copied from `/tmp/bamboo_model` at Send. Plate G-code MD5 `bb01c4d3…`, the same as the slice. Only `DesignerUserId` is blanked |
| [`sliced/aurora_pizero_head_A1mini.gcode.3mf`](sliced/aurora_pizero_head_A1mini.gcode.3mf) | The A1 mini fallback, sliced, not sent |
| [`frames/`](frames/) | Start-up and layer frames, the back-of-plate stack, the full-screen view of the strands |
| [`print.json`](print.json) | Source and hashes, settings, Send options, the go and replies, timeline, what was watched |
| [`recording/`](recording/) | The cut screen recording (10.8 min) with chapters and its cut plan. It starts after the login, leaves out the idle wait, and blurs the room in the H2D camera pane. Not on YouTube yet: a print run has no YouTube token |
