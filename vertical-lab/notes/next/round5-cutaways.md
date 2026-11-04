# Next: round 2's equipment doing its job in cutaway; tray D's array and trays G–I in the scenes (#303)

Stacked on PR #318. Comment `@claude` on this PR to start it. What to do:

1. **Tour clips with the insides showing**, using the `instruments.Instrument` pieces/joints/actions pattern in a new
   module that `tour.MODULES` loads, for the round-2 equipment that has no clip yet:
   - Opentrons OT-2: the gantry and pipette moving over the deck. The vendor STEP loads as one mesh, so split the
     moving head out by its bounding box, or model the head separately.
   - Bambu Lab H2D and A1 mini: the bed and toolhead moving, a part growing.
   - CubXL, liquid-handling set-up: the pipette over the rack.
   - The multi-doser: its own `layout.placements(State(...))`, with the dose in cutaway.
   - Leave the Aconity MIDI and the rePowder alone. The "charge cups in the alloy workflow" session on PR #318 is
     doing the atomize, sieve and print chapters.

   Fade out what is around each process, as `alloy_workflow.py` does.
2. **Tray D's OpenFlexure array in the line scene.** Set `line.TRAY_LOADS["D"]` to the array at (792, -148) in place
   of `openflexure_v7` and `openflexure_delta`, then re-render `vlm_line`. `setup_lab.py` already does this swap.
3. **Trays G–I in the set-up scene.** Add `fab_trays.py`'s trays G, H and I to `setup_lab.py` (`NEW_TRAYS`,
   `ROUND4_TRAY`), check them with `python3 setup_lab.py fit`, then re-render.
4. Upload the new videos, unlisted, with `youtube/yt_service.py`.

## Status (2026-11-04)

Checked against PR #318's branch at `dc50de4`: none of the four items had been done there or was in progress, so
all four were done on [PR #320](https://github.com/vertical-cloud-lab/byu-vcl/pull/320), on top of that branch.

1. **Done.** [`instruments_round2.py`](../../instruments_round2.py), loaded by `tour.MODULES`, has the OT-2, the H2D,
   the A1 mini, the CubXL set up for liquid handling, and the multi-doser. The doser plays through `TOURS` with its own
   `layout.placements(State(...))`. The README's
   [section](../../README.md#round-5-next-round-2s-equipment-at-work-with-the-insides-showing) has what each clip shows
   and what is assumed.
2. **Done.** `line.TRAY_LOADS["D"]` has the array at (792, -148), and `vlm_line` is re-rendered (70 s).
   `setup_lab.py` no longer adds the array itself, which would have placed it twice.
3. **Done.** Trays G-I are in `setup_lab.py`, and `fit` passes for every item. The 3950 mm unit's six slots are full,
   so this scene alone assumes a 4450 mm unit: G and I take new top slots, and H the front column under the opening.
   The scene is re-rendered (2 min 22 s).
4. **Done.** Every new video is uploaded unlisted (`youtube_upload.py`) and recorded in `out/youtube.json`. The OT-2
   clip and the join were uploaded a second time after the OT-2 got a close-up on the trash.

Left over:
- `services.TRAY_ITEMS["D"]` (tray D's power list) still names the two freestanding OpenFlexures.
- `services.add_cameras` puts no cameras on trays G-I.

