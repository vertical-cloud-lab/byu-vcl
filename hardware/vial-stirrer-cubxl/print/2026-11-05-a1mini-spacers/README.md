# Two spacers on the A1 mini (requested 2026-11-05, printed 2026-11-06)

@benwhitney5463
[asked](https://github.com/vertical-cloud-lab/byu-vcl/pull/269#issuecomment-6671877169) on
PR #269, with `@claude-print`, for two of his Onshape *Stir module spacer* printed at once.
This is the spacer that goes under the vial on the stirrer
([README](../../README.md#tested-2026-11-05-a-spacer-and-washers-under-the-vial)).

**Outcome: printed, with no pause, dialog or HMS alert.** Two Ø15 × 4.6 mm spacers
([`spacer_d15_h4.6_onshape.stl`](../../stl/spacer/spacer_d15_h4.6_onshape.stl), the file Ben
named in his [2026-11-06 request](https://github.com/vertical-cloud-lab/byu-vcl/pull/269#issuecomment-6694380432))
were sent at 20:37:06 UTC in white PETG Basic. **The camera gave no picture at any point**, so
the plate was never seen from here: the run sent on Ben's reply that the plate was clear,
given after the run said it couldn't see it ([below](#2026-11-06-printed-on-bens-reply-with-no-camera-frame)).
The printer reached layer 23/23 at 20:50:33 and showed 100 % *Finished* by 20:51:29, 14 min 23 s
after Send against Studio's 11 min 59 s. The parts were left on the plate.

## 2026-11-05: the print run held, then ended

The print run logged in to Bambu Studio and opened the A1 mini's Device page at 23:13 UTC.

- **The printer:** idle. Its last job, *Base*, had finished. There were no HMS alerts, the
  nozzle was 0.4 mm stainless, and white PETG Basic was in AMS Lite A4. The files below are
  from 23:19 UTC.
- **The camera:** from 23:14 UTC, Studio's live view failed on every try with *"Loading failed.
  Please check the network and try again. [2:2]"*. So there was no frame of the plate.
- **The spacer file:** print runs have no Onshape credentials, and the document isn't public.
  The run asked Ben whether the plate was clear, and for the file or the spacer's shape.

The run ended at about 23:21 UTC without an answer, so nothing was sent.

| File | What |
|---|---|
| [`20261105T231920Z_device_page.jpg`](20261105T231920Z_device_page.jpg) | Studio's Device page, with the failed live view |
| [`20261105T231934Z_printer_parts.png`](20261105T231934Z_printer_parts.png) | The nozzle, read off the printer |
| [`20261105T231946Z_hms.png`](20261105T231946Z_hms.png) | The empty HMS list |

## 2026-11-06: prepared in a plain `@claude` run

Ben [replied](https://github.com/vertical-cloud-lab/byu-vcl/pull/269#issuecomment-6691989614)
at 18:11 UTC: *"the plate is clear and it is a plain 10mm diameter, 4.6mm tall cylinder."*
The reply started a plain `@claude` run, which can't log in to the Bambu account. That run
made the files, checked the printer over the LAN, and stopped there.

### The spacer: Ben's Onshape part is Ø15 mm, not Ø10

The run read Ben's document over the API with the lab's key and changed nothing in it.
Its one part, *Stir Module Spacer*, is a plain cylinder **15.000 mm across** and 4.600 mm
tall. Onshape gives its volume as 812.887 mm³, which is π × 7.5² × 4.6. A Ø10 × 4.6 mm
cylinder would be 361.3 mm³. Ben last changed the document on 2026-11-05 at 23:02 UTC.

Ben has described the spacer as Ø10 mm twice, on 11-05 and 11-06, but his request asked
for the Onshape file. So both are here, and the print run should print the one he names:

| STL | Shape | From | MD5 |
|---|---|---|---|
| [`stl/spacer/spacer_d10_h4.6.stl`](../../stl/spacer/spacer_d10_h4.6.stl) | Ø10 × 4.6 mm, plain cylinder | Ben's description; written by [`make_spacer.py`](make_spacer.py) | `0fdeab17f144ef0ab7f9e0efafc440f5` |
| [`stl/spacer/spacer_d15_h4.6_onshape.stl`](../../stl/spacer/spacer_d15_h4.6_onshape.stl) | Ø15 × 4.6 mm, plain cylinder | Ben's Onshape part as exported, byte for byte ([record](onshape_spacer_20261106.json)) | `67c2c89a8585a23a98e9cc5527673011` |

[`make_spacer.py`](make_spacer.py) checks both files: each is watertight, stands on z = 0,
and has every vertex on its circle and on z = 0 or 4.6 ([output](make_spacer_output.txt)).
The export took about 12 API calls, including a first try that lost its authentication on
Onshape's redirect. Following the redirect by hand, as `build_onshape.py` does, fixed it.

Either size drops past the cup's fingers (Ø25.8 mm at their tips) to the floor
(Ø27.6 mm). Neither is centred by anything, so the vial will rest on it wherever it lies.

### The printer at 18:14 UTC, over the LAN

Read through the CubXL Pi with `bambu_lan.py preflight --printer A1_MINI --via CUBXL_PI`
(`bambu/` on [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)'s branch,
`042975e`). It only reads: `pushall`, `get_version` and the camera stream.

| | |
|---|---|
| Identity | TLS CN matches the A1 mini's serial |
| State | `FINISH` after *Base* (60/60 layers). `print_error` 0, **no HMS alerts** |
| Heaters | off; nozzle 22 °C, bed 22 °C |
| Nozzle | **0.4 mm**, stainless steel |
| AMS Lite | A1 PLA Basic, dark blue · A2 empty · A3 PLA Basic, black · **A4 PETG Basic, white** |
| Camera | **No frame.** The stream's port takes the connection and the login, then sends nothing. It timed out three times, after 20, 45 and 45 s ([log](20261106_camera_retries.txt)) |
| Other | SD card present, Wi-Fi −53 dBm, chamber light on, firmware 01.08.01.00, build-plate marker detection on |

Studio failed the same way on 11-05, and on 10-30 this tool got a frame on its first try with
the same camera settings. So the camera looks stuck at the printer, not at either client.
**Switching the printer off and on again** at its power switch is the usual fix. It should
first be idle, and someone at the printer has to do it. The printer's build-plate marker
check is on, and it may use the same camera, so a stuck camera could also stop a print
when it starts.

**The plate:** the run has no frame, so it only has Ben's word that the plate is clear.

### Settings for the print run

The same as the stirrer's other PETG parts:

| | |
|---|---|
| Printer | A1 mini, 0.4 mm nozzle, Textured PEI |
| Parts | Two copies of the STL Ben names, side by side, flat face down as in the STL |
| Filament | Bambu PETG Basic, white (`GFG00`), AMS Lite A4 (0-based slot 3). 245 °C nozzle, 70 °C bed |
| Process | `0.20mm Standard @BBL A1M` with `BUILD.md`'s changes: 4 walls, 30 % infill, 0.15 mm elephant-foot compensation. No supports, no brim |
| Height | 4.6 mm is 23 layers of 0.20 mm, first layer included, so it should slice to exactly 4.6 mm. The G-code's last layer should be at z = 4.6 |
| Expect | about 15–20 min from Send, more than half of it the printer's preparation, and 1–2 g |

## 2026-11-06: printed on Ben's reply, with no camera frame

Ben [asked again](https://github.com/vertical-cloud-lab/byu-vcl/pull/269#issuecomment-6694380432)
at 20:10:18 UTC, naming the file: *"print two of
hardware/vial-stirrer-cubxl/stl/spacer/spacer_d15_h4.6_onshape.stl from branch
claude/issue-169-20261009-2151 on the A1 mini, side by side, white PETG Basic from A4, with
BUILD.md's settings. The plate is clear."* The print run was approved and started at 20:10:47.
Bambu Studio 02.08.02.61 ran on the runner. It logged in with the password and an
authenticator code from `bambu-totp`, and Bambu asked for nothing else.

### The plate check: no frame, so a person's reply

Under the 2026-10-23 rule the run reads the plate itself from a fresh frame. If it can't tell,
it says what it sees and waits for a person; that is the one case that needs a reply.

- **The Device page, 20:27:29.** The printer was idle after *Base* (100 %, *Finished*). Nozzle
  21 °C and bed 21 °C, heaters off, no HMS alerts ([HMS tab](20261106T203005Z_hms_empty.png),
  20:30:05). The nozzle was 0.4 mm stainless, standard flow
  ([Printer Parts](20261106T202950Z_printer_parts.png), 20:29:50). AMS Lite: A1 PLA dark
  blue, A2 empty, A3 PLA black, A4 PETG white.
- **No frame.** The live view failed at 20:28 and at 20:29 with *"Loading failed. Please check
  the network and try again. [2:2]"* ([Device page](20261106T202811Z_device_page.jpg),
  [second try](20261106T202950Z_live_view_failed_again.png)). That is the same failure as on
  11-05, and the LAN check at 18:14 got no frame either.
- **20:30:51, posted** at the top of the tracking comment: the Device page, the state, the file
  and printer, and the read of the plate, *"I can't see it"*. It asked someone at the printer
  either to switch it off and on, or to reply that the plate was clear right then. Ben's
  request had said the plate was clear, but that was before the run started.
- **20:35:26, Ben's reply:** *"the plate is clear right now"*
  ([comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/269#issuecomment-6694912778)).
  The thread was polled every 20 s from 20:31:10, and nothing else was posted.
- **20:35:58, one more try at the camera before Send:** *"Video Stopped"*, no picture
  ([Device page](20261106T203636Z_device_page_before_send.jpg)).
- **20:37:06, Send,** 6 min 15 s after the post and 1 min 40 s after Ben's reply.

### The slice

| | |
|---|---|
| Parts | The STL imported twice (*Clone*, then *Arrange*), side by side near the middle of the plate. Centres at (118.05, 87.04) and (133.95, 92.96) mm, 2 mm apart |
| Printer | Bambu Lab A1 mini 0.4 nozzle (set by *Sync info*; the empty project had started as an A1), Textured PEI Plate |
| Filament | Bambu PETG Basic @BBL A1M 0.4 nozzle, white: project filament 1 set to the AMS's A4 entry. 245 °C nozzle, 70 °C bed |
| Process | `0.20mm Standard @BBL A1M` with `BUILD.md`'s changes: wall loops 2 → 4, sparse infill 15 → 30 %, elephant-foot compensation 0 → 0.15 mm. Supports off and auto brim left as they were; no brim was generated |
| Checked in the slice's `CONFIG_BLOCK` | `wall_loops = 4`, `sparse_infill_density = 30%`, `elefant_foot_compensation = 0.15`, `enable_support = 0`, `curr_bed_type = Textured PEI Plate`, `filament_settings_id = Bambu PETG Basic @BBL A1M 0.4 nozzle`, `printer_settings_id = Bambu Lab A1 mini 0.4 nozzle` |
| Studio's estimate | 23 layers to 4.60 mm, 0.49 m, 1.48 g, 11 min 59 s, of which 5 min 37 s is the model |
| The discs in the G-code | [`check_slice.py`](check_slice.py) ([output](check_slice_output.txt)): each disc's outer wall runs on a 14.58 mm centreline from layer 2 to layer 23, so Ø15.00 mm outside with 0.42 mm lines. Layer 1 is 14.20 mm with 0.5 mm lines, Ø14.70 mm: the 0.15 mm compensation |
| Send | Job `spacers_d15_x2` (Studio offered `spacer_d15_h4.6_onshape`). Thumbelina, the A1 Mini, PEI, PETG → A4, timelapse off, bed levelling and flow dynamics calibration on ([dialog](20261106T203700Z_send_dialog.png)) |
| Sent file | [`spacers_d15_x2.gcode.3mf`](spacers_d15_x2.gcode.3mf), the 3MF Studio wrote at Send, with the account's `DesignerUserId` blanked. Its plate G-code (MD5 `015fe05f86b497214c4e7aea52b7733e`) is byte-identical to Studio's slice |

### Watching it

The camera was out, so the print was watched by reading Studio's Device page every 10 s:
the job panel's layer and percentage, the nozzle and bed temperatures, and any new window, such
as a warning. [`watch_a1mini_nocam.py`](watch_a1mini_nocam.py) is `bambu/studio/watch_studio.py`
from PR #234's branch without the blank-camera stop, with the job panel where it sits when the
live view isn't playing, and with PETG's limits. [`watch_monitor.jsonl`](watch_monitor.jsonl)
is its log.

| UTC | |
|---|---|
| 20:37:06 | *Send* |
| 20:38:42 | `spacers_d15_x2` on the printer, layer 0/23: nozzle 246 °C heading to 250, then 270 for the PETG flush |
| 20:40:22–20:44:27 | Preparation: the nozzle cooled to about 140 °C for bed levelling, then back to 245 °C; the bed reached 70 °C; the job panel went from 7 to 46 % at layer 0 |
| 20:45:00 | **Layer 1**, 7 min 54 s after Send. The build-plate marker check, on according to the 11-06 LAN read, didn't stop the print without a camera |
| 20:45:00–20:50:33 | Layers 1 to 23, about 11 s each; layer 10 to 11 took 44 s |
| 20:50:56 | Bed heater off; nozzle heater off at 20:51:07 |
| 20:51:29 | **100 %, layer 23/23, *Finished*** ([Device page](20261106T205246Z_device_page_finished.jpg) at 20:52:46). 14 min 23 s after Send, against Studio's 11 min 59 s |
| 20:52:55 | No HMS alerts ([HMS tab](20261106T205255Z_hms_empty_after.png)) |

No dialog, pause or warning appeared at any point. The watcher stopped itself at 20:52:36 on an
OCR misread of the cooling nozzle (641 °C, a frame after 168 °C), after the print had finished.
It never saw its own finish condition, because OCR read the panel's "100 %" as "100" without the
sign; the Device page was checked by eye instead. Nobody has reported on the parts yet, and the
camera can't show them.

## Files

| File | What |
|---|---|
| [`spacers_d15_x2.gcode.3mf`](spacers_d15_x2.gcode.3mf) | The file the printer ran, account ID blanked |
| [`check_slice.py`](check_slice.py), [`check_slice_output.txt`](check_slice_output.txt) | Where the two discs print and how big, read from that file's G-code |
| [`print.json`](print.json) | The 2026-11-06 print: request, plate check, slice, Send, timeline and outcome |
| `20261106T2028*`–`20261106T2052*` | The Device page, the camera's failures, the nozzle, the HMS list before and after, the Send dialog, and the finished job |
| [`watch_a1mini_nocam.py`](watch_a1mini_nocam.py), [`watch_monitor.jsonl`](watch_monitor.jsonl), `panels/` | The Device-page watcher, its log, and the job panel at each layer |
| [`recording/`](recording/) | The session's screen recording, cut by wall-clock time ([`cut_plan.json`](recording/cut_plan.json), `cut_recording.py` from PR #234's branch): 6.1 min with [chapters](recording/spacers_d15_x2_A1mini_2026-11-06_chapters.txt). The login and the sign-out are not in it. Not uploaded: print runs have no YouTube token |
| [`make_spacer.py`](make_spacer.py), [`make_spacer_output.txt`](make_spacer_output.txt) | Writes the Ø10 STL and checks both |
| [`onshape_spacer_20261106.json`](onshape_spacer_20261106.json) | The Onshape read: document, part, volume, the export's options and MD5 |
| [`20261106T181410Z_preflight.json`](20261106T181410Z_preflight.json) | The LAN pre-flight's summary and checks. The verdict is NO-GO because of the camera alone |
| [`20261106T181410Z_report_redacted.json`](20261106T181410Z_report_redacted.json) | The printer's full status report, with the IP, serial, access code and network details taken out |
| [`20261106_camera_retries.txt`](20261106_camera_retries.txt) | The three camera attempts |
