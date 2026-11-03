# Dummy `@claude-print` run for a lab demo (2026-11-02, issue 313)

Asked for in [issue 313](https://github.com/vertical-cloud-lab/byu-vcl/issues/313): "don't actually
print anything, but download bambu studio and slice something from this repo or powder-doser,
then show the render and the image of the build plate." **Nothing was sent to a printer.**

The slice and render worked. The build plate camera frame didn't: Studio's live view never
delivered a frame from the A1 mini, and the H2D was offline.

## Timeline (UTC)

| UTC | Step |
|---|---|
| 23:35 | Issue opened with `@claude-print`; run approved, session started 23:36:47 |
| 23:37 | Bambu Studio 02.08.02.61 AppImage (230 MB) downloaded and extracted; apt packages from the runbook |
| 23:38–23:40 | First run: certificate prompt, wizard (North America, data sharing skipped), network plug-in, *Cancel* on the profile update, three Beta prompts |
| 23:41:06 | *Log In* pressed |
| 23:41:21 | Bambu asked for the authenticator code; the first `bambu-totp` code worked. No e-mailed code was asked for |
| 23:41:47 | Device page: Studio picked the A1 mini by itself. Idle, no HMS alert, nozzle and bed 21 °C, last job `compact_stirrer_parts_2` Finished |
| 23:42–23:47 | Live view: *"Loading failed. Please check the network and try again. [2:2]"* on every try. GStreamer `plugins-bad` added and Studio restarted, which kept the login, so no second code was needed. No change |
| 23:48 | H2D ("BYU VCL H2D - Théoden") selected: *"Failed to connect to the printer"* |
| ~23:49 | Someone else's job, `stub_holder_A1mini_blackPLA` (90 layers, 53 min 32 s, 30.90 g), started on the A1 mini. Not from this run |
| 23:53 | Prepare page: *Sync info* switched the preset from "Bambu Lab A1" to the A1 mini and read a 0.4 mm nozzle |
| 23:54:24 | `tube_rack_2x8.stl` sliced (Ctrl+R; *Print plate* never pressed) |
| 23:56–00:06 | Live view retried 20 more times, with a note in the thread asking anyone watching the A1 mini's camera to close it. Never a frame. The Storage tab listed the SD card's timelapses through the same cloud tunnel |
| 00:07:09 | Signed out of the Bambu account |
| 00:07:37 | Studio closed without saving; `~/.config/BambuStudio` and `/tmp/bamboo_model` deleted |

## The slice

| | |
|---|---|
| Model | `alloy-corrosion/bom/cad/tube_rack_2x8.stl` (branch `claude/issue-213-20261013-2132`), 96 × 34 × 30 mm, 13 642 triangles |
| Printer, nozzle, plate | Bambu Lab A1 mini, 0.4 mm (from *Sync info*), Textured PEI Plate |
| Process, filament | `0.20mm Standard @BBL A1M` unchanged (2 walls, 15 % sparse infill, no supports), PLA Basic |
| Result | 150 layers to 30.00 mm; 19.67 g, 6.49 m; 53 min 55 s total (45 min 57 s model, plus 5 min 58 s prepare and 1 min 58 s timelapse) |
| Warning | *"It seems object tube_rack_2x8.stl has floating cantilever. Please re-orient the object or enable support generation."* Needs supports or a different orientation before a real print |

## Files

| File | What |
|---|---|
| `20261102T235257Z_device_page_a1mini.png` | Device page while the other job started: printer state, AMS, the camera pane stuck on Studio's placeholder |
| `20261102T235420Z_prepare_render.png` | The render: the rack on the A1 mini's plate, Prepare page |
| `20261102T235449Z_sliced_preview.png` | Sliced, with Studio's slicing result and warning |
| `20261102T235530Z_sliced_layer88.png` | The same, cut at layer 88 (17.6 mm) |
| `20261103T000648Z_device_page_a1mini.png` | Device page at the end: the other job at layer 11/90, the camera still stopped |

The blurred picture behind the Bambu Lab logo in the camera pane is not the printer's camera.
It is `resources/images/liveview_bg.png`, bundled with Studio.

## Why there's no camera frame

- **`[2:2]` is Studio's 15 s first-frame timeout.** In 02.08.02.61's
  `src/slic3r/GUI/MediaPlayCtrl.cpp`, `SetMachineObject` stops a live view that is still loading
  15 s after *Play*, sets failed code 2 and shows exactly this message. The bracket is
  `[state:code]`, so `[2:2]` reads "still loading, timed out". The stream URL came back and the
  tunnel connected, since the plug-in logged about 165 `BambuTunnel::GetMsg` calls per try. But
  no video frame arrived within 15 s.
- **Not GStreamer, it seems.** `GST_DEBUG=2` logged nothing during the tries, and adding
  `gstreamer1.0-plugins-bad` changed nothing. This build ships its own `libavcodec`.
- **Not the runner's network.** UDP to public STUN servers answered in 9–51 ms, and the
  Storage tab listed the A1 mini's SD card through the same cloud tunnel while the stream
  failed.
- **Not the plug-in.** Its files are dated 14 Aug, the same as in the runs that got frames on
  2026-10-23 and 2026-10-28.
- **Most likely: another viewer.** Studio's source has, for the A1 mini's error code 1:
  "Multi-device/client simultaneous liveview is not supported. Please close the liveview on
  other devices/clients and try again." This run was a live demo in the lab, and a print
  started on the A1 mini mid-run. Someone watching its camera in Bambu Handy or Studio would
  hold the only slot. Studio might then have reported code 1 rather than a timeout, so this
  is a guess, not a finding.
- **No fallback still.** Studio's "Printer Preview" (`start_device_image_flow`) needs
  `is_support_liveview_preview`. No preview with its watermark appeared, so the A1 mini either
  lacks it or the download failed.

Next time, close every other view of the printer's camera before the run starts. In a `@claude`
run, a LAN frame from a Pi doesn't depend on Bambu's cloud stream at all.
