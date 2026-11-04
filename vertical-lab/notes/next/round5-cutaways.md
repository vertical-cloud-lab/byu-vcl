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
