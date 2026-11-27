# Stub holder plate (Top + Bottom) on the A1 mini, 2026-11-02: printed, with no camera

@ronnie-guymon asked for this print on PR #95
([request](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-6589992268)): the SEM stub
holder plate from [digital-alloy-lab PR #174](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/174),
`stub-holder/stub_holder_A1mini_blackPLA.gcode.3mf` at `9566ee1`, on the A1 mini in black PLA Basic. It was
sent from Bambu Studio on the runner (route 3 of the runbook, `bambu/README.md` on PR 234's branch) at
23:49:37 UTC. It reached 100 % at layer 90/90 by 00:44:18 UTC. The last layer was done and both heaters
were set to 0 at 00:42:41, 53.1 min after Send; Studio estimated 53 min 32 s. There was no HMS alert or
dialog at any point.

**No camera frame, at any point.** Studio's live view of the A1 mini never started. Every attempt, from
23:24 to 00:45 UTC and across two Studio restarts, ended with *"Loading failed. Please check the network and
try again. [2:2]"* ([screenshot](20261102T234817Z_a1mini_liveview_failed.png)). In Studio 02.08.02.61's
`MediaPlayCtrl.cpp`, code 2 means no video arrived within 15 s. The problem looked like the printer's camera,
not the runner:
- outbound UDP from the runner worked (STUN replies in 5 ms);
- the printer's Storage tab loaded over the same cloud tunnel;
- Studio's player never got as far as decoding.

The earlier `@claude-print` runs on 23 and 28 October got live frames from this printer through the same
route.

**How it was sent without a frame.** Under the 2026-10-23 plate rule a run that can't tell whether the
plate is empty doesn't send; it says what it sees and waits for a person. The run posted that at 23:33:37 UTC.
It asked anyone with the camera open in Bambu Handy or Studio to close it, or else to power-cycle the
printer. @ronnie-guymon (write access) replied at 23:46:33 UTC:
[*"Ignore the camera frame, the plate is clear"*](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-6591420981).
The run then:
- posted a send notice at 23:47:45 with a 90 s window to object;
- tried the camera once more at 23:47:56, which failed the same way;
- found no replies by 23:49:35 and sent.

Because the camera was down, the print was followed only on Studio's Device page (temperatures, layer,
dialogs) and the thread was asked for someone near the printer to look at the first layer. The part itself
was never imaged by this run.

**Checks before Send:**
- **Printer:** idle, heaters off, Assistant (HMS) tab empty.
- **Nozzle:** 0.4 mm stainless, standard flow, read from Printer Parts
  ([screenshot](20261102T233008Z_a1mini_printer_parts.png)).
- **Filament:** black PLA in AMS lite A3.
- **File:** plate G-code MD5 `4809e115…` equals the stored and requested MD5. The A1 mini 0.4 profile, Textured
  PEI at 65 °C, `M620 S0A` + `M412 S1`, an 18 mm part and only the expected timelapse warning.

**Studio re-sliced it, and circle compensation had to be turned back on.** Opening the CLI-made project in
the GUI gave Bambu's stock process values, which switched `enable_circle_compensation` from 1 to 0 (the
known reset, `bambu/studio/README.md` on PR 234's branch). The request said to keep it on. So *Auto circle
contour-hole compensation* was ticked again (Quality → Precision) and the plate re-sliced. The sent G-code
then matched the requested one ([`gcode_check.json`](gcode_check.json)):
- 90 layers and 30.90 g;
- total extrusion 10172.03 mm against 10171.88 mm, and at most 0.16 mm on any layer;
- only Studio's stock acceleration limits differ, as on every earlier GUI run.

**Send options:** Thumbelina, the A1 Mini (0.4 mm); PEI plate; PLA → A3; Timelapse off; Auto Bed Leveling
on; Flow Dynamics Calibration on. The job was renamed to `stub_holder_A1mini_blackPLA` to drop the spaces
and `+` of the default name ([Send dialog](20261102T234935Z_send_dialog.png)).

## What was new

- **The camera failed for the whole session, printer-side.** See above. If it happens again, check first
  whether someone has the camera open in Bambu Handy. This printer's liveview is single-viewer. Failing
  that, power-cycle the printer. A run without a frame needs a person's in-person read of the plate before
  it sends, and someone at the printer for the first layer.
- **Studio's first start hung.** Right after the setup wizard installed the network plug-in, Studio's main
  thread spun at 100 % CPU inside a modal loop and stopped repainting. Three *Software Update* dialogs
  showed stale pixels. The config had already been saved (region, `installed_networking: 1`), so killing it
  and starting it again cost about a minute. The restart showed the Beta and profile-update prompts again
  and painted them normally.
- **`pkill -f bambu-studio` kills the shell running it** (exit 144), the same trap the runbook notes for
  `ffmpeg`. Kill Studio by PID: `pgrep -x bambustu_main`.
- **`GH_TOKEN` in a `@claude-print` session is the 1-hour App token.** The runbook (§4.1) says it is the job's
  own token and lasts the whole job. Here `gh` calls with it failed with 401 at 00:12:22, exactly 60 min
  after the step started. Poll the thread with `DEFAULT_WORKFLOW_TOKEN`, which kept working, or with the
  re-minted `/tmp/.ghtok`.
- **Opening a CLI `.gcode.3mf` doesn't let Studio send it as sliced.** The *Print plate* button stayed grey
  until the GUI re-sliced it, so the reset settings have to be checked every time. Here that meant circle
  compensation.
- **The job panel's layout depends on the camera.** With the live view not playing, the job panel sits
  higher than `watch_studio.py`'s `job` region expects, so its OCR saw only "Estimated finish time" and never
  the layer. `(270, 765, 1300, 935)` on the 1920×1080 screen covers the panel in this layout.
- **`cut_recording.py` takes one day.** This session crossed midnight UTC, so a copy was patched to accept
  full `YYYY-MM-DDTHH:MM:SS` times for the parts after 00:00.

## Files

| File | What |
|---|---|
| [`sent/stub_holder_A1mini_blackPLA.3mf`](sent/stub_holder_A1mini_blackPLA.3mf) | The 3MF Studio uploaded, copied from `/tmp/bamboo_model` at Send. Its plate G-code (MD5 `a1f716d1…`) is byte-identical to the slice; only `DesignerUserId` is blanked |
| [`gcode_check.json`](gcode_check.json) | The requested file's checks, the settings Studio's re-slice changed, and the requested-vs-sent comparison |
| [`print.json`](print.json) | Source and commit, printer state, send options, the plate check (no frame; the go and the wait), the timeline and the monitor's summary |
| `20261102T232953Z_a1mini_hms_empty.png`, `20261103T004511Z_a1mini_hms_after.png` | Assistant (HMS) tab, empty before and after |
| `20261102T233008Z_a1mini_printer_parts.png` | The nozzle read off the printer: 0.4 mm stainless, standard flow |
| `20261102T234817Z_a1mini_liveview_failed.png` | The live view failing, `[2:2]` |
| `20261102T234935Z_send_dialog.png` | The Send dialog as sent |
| `20261102T235637Z_a1mini_device_printing.png`, `20261103T004418Z_a1mini_device_finished.png` | Device page at layer 1 and at 100 % |
| `watch.jsonl.gz` | One OCR reading of the Device page every ~10 s, 23:50 to 00:42 UTC |
| [`recording/`](recording/) | The cut screen recording (13.3 min) with chapters and its cut plan. The login, the Update tab (serial numbers), the restart's home page and the sign-out (account name) are cut. Nothing is blurred, because the camera pane only ever showed Studio's placeholder |
