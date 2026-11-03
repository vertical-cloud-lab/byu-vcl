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
