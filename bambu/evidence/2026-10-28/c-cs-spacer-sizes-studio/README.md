# Six more C–CS spacer rings, C to H, for the A1 mini (2026-10-28): sliced, not sent

Asked for on PR #234 by @sgbaird as "get at least 5 more sizes spaced a bit bigger to try to make
sure we get this in the next shot"
([comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6474970526)), after
@timothy-commins found both 23 Oct rings, A and B, too small on both ends
([comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-6453257144)). The
rings and how to test them are in the
[camera README](../../../../ot2-overhead-camera/lid-mount/camera/README.md#2026-10-28-six-more-printed-rings-c-to-h-bigger-on-both-ends).

**Not sent: the A1 mini's plate was never clear.** From the first frame at 16:57:04 UTC to the last,
a large black print stood on the front-left half of the textured plate: the printer's previous
job, "Mounting Plate" (2 h 52 min, 67 g, someone else's), showing 100 % *Finished*. Under the
2026-10-23 plate rule an occupied plate needs a person, so the run posted the frame, asked for the
part to be removed, and waited. Nobody replied, and the plate region never changed: the mean
absolute difference from the first frame stayed at 1.5–1.9 of 255 in every frame. One likely
reason nobody saw the request: the run can only edit its tracking comment, and GitHub doesn't
notify anyone of edits.

**The H2D wasn't free either.** At 17:43:50 UTC it was printing someone's "Part 1" at 79 %
(layer 391/457, about 38 min left) with warning 0700-8010, "The AMS assist motor is overloaded",
on Studio's screen ([job panel](20261028T174417Z_h2d_job_panel.png),
[warning](20261028T174417Z_h2d_warning.png)). Nothing on it was clicked. It also had 0.6 mm
nozzles when last checked, and this repo prints with 0.2 or 0.4 mm only.

**Ready to send.** [`sliced/c_cs_spacer_sizes_C-H_A1mini.gcode.3mf`](sliced/c_cs_spacer_sizes_C-H_A1mini.gcode.3mf)
is Studio's own export of the slice (*File → Export → Export plate sliced file*), with only the
lab account's `DesignerUserId` blanked. Its plate G-code is byte-identical to the slice (MD5
`b38feb9e…`). A later `@claude-print` run can open it and send plate 1 once the plate is clear:
- **Printer and plate:** A1 mini, Textured PEI.
- **Process:** `0.08mm High Quality @BBL A1M` with 6 walls; circle compensation off, as for A and B.
- **Filament:** black PLA Basic, mapped to AMS A3.
- **Estimate:** 111 layers, 10.63 g, 1 h 34 min 40 s. The 23 Oct rings took 10 % longer than estimated.

Check the GUI didn't reset the 6 walls when it opens the file
([why](../../../studio/README.md#the-gui-resets-a-cli-projects-changed-settings)).

**The slice was checked against the model.**
[`slice/c_cs_gcode_check.py`](../../../../ot2-overhead-camera/lid-mount/slice/c_cs_gcode_check.py)
rebuilds each ring's outer-wall paths and compares their radius round the ring's own centre with
the model's thread. All six rings came out within 0.007 mm of the model, at the 5th, 50th and
95th percentile, on every threaded layer, and it found 3 to 8 rim notches where the letters put
them ([`gcode_check.json`](gcode_check.json)). The same check on the 23 Oct G-code gave the same
result for A and B ([`../../2026-10-23/c-cs-spacer-studio/gcode_check.json`](../../2026-10-23/c-cs-spacer-studio/gcode_check.json)),
so their misfit came from printing, not slicing.

| File | What |
|---|---|
| `20261028T165704Z_a1mini_camera_studio.jpg` | The first frame, posted at 16:58:04 UTC before any prep; the plate is occupied |
| `20261028T165704Z_a1mini_device_page.jpg`, `20261028T165750Z_a1mini_printer_parts.png` | The Device page at the same moment (idle, 22 °C / 21 °C, last job 100 % *Finished*) and the nozzle read off the printer: 0.4 mm stainless, standard flow |
| `20261028T171553Z_a1mini_hms_empty.png` | The Assistant (HMS) tab: no alerts |
| `20261028T171353Z_*`, `20261028T174120Z_*`, `20261028T180037Z_*` | Later frames, unchanged; the frames were taken every 3–4 min throughout |
| `20261028T174417Z_h2d_*` | The H2D, busy and showing a warning |
| [`sliced/`](sliced/) | The sliced plate, ready to send |
| [`gcode_check.json`](gcode_check.json) | The slice against the model, ring by ring |
| [`print.json`](print.json) | Source and commit, presets, slice checks, the plate check and the timeline |
| `recording/` | The cut screen recording, with chapters. The login and the sign-out are cut, and the camera pane's upper corners are blurred where the room shows |
