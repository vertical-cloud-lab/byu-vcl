# Next: fixes from round 4's review (#303)

Stacked on PR #318. Comment `@claude` on this PR to start it. Each item comes from a round-4 notes file. Check first what the "render style and per-instrument fixes" session on PR #318 already changed (the furnace door, the OpenFlexure stage, the PIP).

1. **`instruments.wire_edm()`'s tour cuts a flat plate with a vertical wire.** A vertical wire can only cut parts off
   at their base with the plate on edge, as `alloy_workflow.py` does. Fix the tour clip
   (`notes/alloy_workflow.md`).
2. **`instruments.instron_small()`'s specimen needs about 2.4 kN, over the 68SC-2's 2 kN.** Use a smaller section,
   or show the bar on the 68FM-100 (`notes/alloy_workflow.md`).
3. **Check the bay camera against the arm's poses** with `reach.py`. Neither has been checked against the other yet
   (`notes/services.md`).
4. **Drive the MiR250 at its published 0.3 m/s².** `alloy_workflow.py` drives about twice as fast; check
   `warehouse.py` too.
5. **Hooks in `tour.py` instead of monkeypatches.** `instruments_char.py` and `instruments_lab.py` wrap
   `scene.Scene.overlay`/`step` on import, to draw spectra, curves and per-step camera moves. Give `tour_one` an
   overlay hook, per-step cameras and per-step labels, and drop the wrappers.
6. **A scannable QR code** on the packaging station's jar label (the `qrcode` package), in place of the placeholder
   pattern.
7. **Published figures still to confirm.** Ask the makers; each is listed in its notes file:
   - the S2 PUMA's open-lid height;
   - the VHX-S750E stand's outer size;
   - the electrical ratings of the Aconity MIDI and the glovebox;
   - the MX-Lab's base cabinet.

## Status (2026-11-04, PR #321)

| # | Item | Status |
|---|---|---|
| 1 | Wire EDM tour on edge | Done on #318 in `0cdbaf3`, before this ran. `notes/alloy_workflow.md` no longer lists it as a suggestion |
| 2 | 68SC-2 specimen | Done: a 3 × 1 mm bar (`instruments.SC_BAR`), 1.24–1.38 kN at 412–461 MPa. Tour re-rendered |
| 3 | Bay camera vs the arm | Done on #318 against `reach.py`'s poses (`bay_arm_clearance()`, 197 mm). Here, along the arm's own paths too (`audit_baycam.py`): no contact in the round-1 workflow or alloy chapter 1 |
| 4 | MiR250 at 0.3 m/s² | Done in code for `alloy_workflow.py`, `alloy_atomize.py`, `alloy_print.py` and `warehouse.py` (`props.ramp_secs`/`ramp_frac`, `scene.unease`). The warehouse is re-rendered and audited. Chapters 2–4 still need a render, after #318's collision fixes to their arm moves land |
| 5 | Hooks in `tour.py` | Done: `Instrument.cams`, `.step_labels`, `.overlay`; `Scene.overlays`. Both wrappers are gone, and `fab_tour.tour_one` is `tour.tour_one`. The seven hooked tours render pixel-identical |
| 6 | Scannable QR code | Done: `qrcode`, version 5-L, holding the label's text. zbar and OpenCV decode it from the MP4's frames, and zbar from the GIF's too |
| 7 | Published figures | Searched (nobody was contacted). **Found:** the VHX-S750E's outline (Keyence's own drawing); the PureLab HE's electrical ratings (Inert's manual and data sheet). **Third-party only:** the Aconity MIDI's supply (3Dnatives: 400 V 3-ph, 32 A, 50 Hz). **Still unpublished, to ask:** the S2 PUMA's open-lid height (Bruker) and the MX-Lab's base cabinet (InssTek). Each is in its notes file |
