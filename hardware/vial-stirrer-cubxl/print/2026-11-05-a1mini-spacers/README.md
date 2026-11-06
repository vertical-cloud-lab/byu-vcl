# Two spacers on the A1 mini: not sent yet (requested 2026-11-05, prepared 2026-11-06)

@benwhitney5463
[asked](https://github.com/vertical-cloud-lab/byu-vcl/pull/269#issuecomment-6671877169) on
PR #269, with `@claude-print`, for two of his Onshape *Stir module spacer* printed at once.
This is the spacer that goes under the vial on the stirrer
([README](../../README.md#tested-2026-11-05-a-spacer-and-washers-under-the-vial)). **Nothing has
been sent to a printer.**

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

## Files

| File | What |
|---|---|
| [`make_spacer.py`](make_spacer.py), [`make_spacer_output.txt`](make_spacer_output.txt) | Writes the Ø10 STL and checks both |
| [`onshape_spacer_20261106.json`](onshape_spacer_20261106.json) | The Onshape read: document, part, volume, the export's options and MD5 |
| [`20261106T181410Z_preflight.json`](20261106T181410Z_preflight.json) | The LAN pre-flight's summary and checks. The verdict is NO-GO because of the camera alone |
| [`20261106T181410Z_report_redacted.json`](20261106T181410Z_report_redacted.json) | The printer's full status report, with the IP, serial, access code and network details taken out |
| [`20261106_camera_retries.txt`](20261106_camera_retries.txt) | The three camera attempts |
