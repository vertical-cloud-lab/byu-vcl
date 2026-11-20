## Refining the Mastersizer 3000 + Aero S against Malvern's footage (#303)

The model was drawn from Malvern's brochure photos. It is now a parametric model, `MS3000` and `_ms3000` in
[`instruments.py`](../instruments.py), registered to video frames with [`register.py`](../register.py) as the polisher
was. The view files are in [`refs/mastersizer/`](../refs/mastersizer/) and the overlays in
[`out/register/mastersizer/`](../out/register/mastersizer/). The published sizes stay fixed and set the scale: the
bench is 690 W × 300 D × 450 H mm and the Aero S 260 × 180 × 380 mm. The fit sets the proportions Malvern doesn't
publish.

### Sources

All frames were fetched through the stream-cam Pi with `frames.py`: five storyboards and 12 frames.

| View | Frame | What it shows |
|---|---|---|
| `aero_demo_0001` | [iaHJ8QEwJ-I at 0:01](https://youtu.be/iaHJ8QEwJ-I?t=1), Malvern, "Mastersizer 3000 Aero Demo" | the bench and the Aero S from the front right, as connected in the lab |
| `metal_cell_0300` | [6ZuKAAHb_20 at 3:00](https://youtu.be/6ZuKAAHb_20?t=180), Malvern, "Measuring metal powders with the Mastersizer 3000" | the bench's long right part, close up from the front right, with the cell's cassette half out of the bay |
| `metal_photo_0018` | [6ZuKAAHb_20 at 0:18](https://youtu.be/6ZuKAAHb_20?t=18), the same video's product photo | the left end, the bay and the lid, from low on the left. It has its own `"camera"` group, since it isn't the video's camera |

These frames were looked at but not registered:
- [iaHJ8QEwJ-I at 0:52](https://youtu.be/iaHJ8QEwJ-I?t=52) ("Adjust Hopper"): the clear cover is lifted off by hand,
  not hinged, and the hopper's ring is turned.
- [iaHJ8QEwJ-I from 1:55 to 2:17](https://youtu.be/iaHJ8QEwJ-I?t=115): cleaning. The hopper comes off and the tray
  lifts out of its U-shaped carrier.
- [sQq9MwG0rhI from 0:21 to 0:54](https://youtu.be/sQq9MwG0rhI?t=21): Malvern's "Dry Measurement Demo". Sample goes
  in with a spatula, then the captions run "SOP starts by enabling the compressed air ... and aligning", "the
  background signal is then measured", and "the feed is enabled and the sample starts to flow".
- [XAklcalCW-8 at 0:07](https://youtu.be/XAklcalCW-8?t=7) and
  [2:16 to 2:30](https://youtu.be/XAklcalCW-8?t=136): an AZoNetwork copy of Malvern's video. It shows the top deck's
  layout, and the hopper filled with an orange spatula and its gap scale.
- [c2iZH7ddPdc](https://youtu.be/c2iZH7ddPdc), a lab's own clip: the tray in its carrier, close up.

### What changed, and why

- **The bench's layout was wrong.** The old model had a black top and a black left end, a cell bay cut into the
  front, and a dark dome on it. The frames show something else:
  - The whole body is satin silver-grey under a charcoal deck. The deck's front edge runs straight across both
    panels.
  - The bay is narrow, 102 mm, with its left edge 186 mm from the left end. It holds the cell's cassette. Its front
    plate, lettered AERO, carries a green LED and the hose fitting (264 mm up). A lower block sits under it, with a
    blue LED strip at the foot.
  - Both panels' lower edges sweep down from the bay to the ends, over a dark plinth set back underneath. The sweep
    leaves the bay at 69 mm, so the plinth peaks under the bay. In both close views the edge is straight to within
    6 px.
  - A darker grey end cap, 24 mm, closes the right end and stands about 10 mm above the deck.
  - The top: a round light-grey lid over the cell, with a dark handle, at the published 450 mm. A raised oval tail
    runs right from the lid to 541 mm from the left end, and a blue-lit oval sits left of the lid. The deck itself is
    at 381 mm.
  - Small chrome feet.
- **The Aero S stood in the wrong place, with the wrong parts.** It stood in front of the bay with a "venturi" box
  reaching into the bench. It now stands in front of the left panel, centred 152 mm from the left end and 138 mm in
  front of the bench:
  - A dark base and core. The silver shell sweeps down to the corner nearest the bay, along the boundary in the frame.
    The blue LED wraps that corner of the base.
  - Under the clear cover: a U-shaped carrier holding the vibrating tray, the black hopper with its gap ring over one
    end, and the venturi at the other.
  - A black hose runs from the venturi to the cassette's fitting.
  - The powder leaves the cell downwards. The extract hose now runs from under the bay, back under the bench, to the
    extractor. Before, it crossed the front, where no frame shows a hose.
- **The motion follows the demos.**
  1. The cover lifts off (a path, not a hinge). A vial is carried from the bench to the hopper.
  2. The hopper's gap is set and the cover goes back on.
  3. Air on, then the background. The tray vibrates (a zig-zag path), and the grains follow the tray, the hose and the
     cell through the laser, drawn see-through.
  4. The extractor draws the powder away.
  The vial is no longer a prop, so the hero still no longer shows it poking through the closed cover.
- **Fixed in passing:** the extractor's body and head both ended at 480 mm and z-fought.

### The fit

The anchors are `mastersizer_anchors(p, pose)`. 15 free parameters are fitted, listed in `FREE["mastersizer"]`, and
the checks in `CHECKS["mastersizer"]` keep the model buildable. The result is in
[`refs/mastersizer/fit.json`](../refs/mastersizer/fit.json), and the dict holds the fitted values.

| View | rms, camera only → joint fit | Focal length | Worst picks |
|---|---|---|---|
| `aero_demo_0001` | 4.25 → 4.18 px | 1564 px | top front left 9.4, swoosh tip 7.9, cut at bay right 6.9 |
| `metal_cell_0300` | 2.95 → 2.59 px | 1914 px | swoosh tip 5.6, top front right 3.5 |
| `metal_photo_0018` | 3.11 → 2.95 px | 1080 px | cut at bay left 6.5, bottom front left 6.1 |

Two picks were dropped from the product photo:
- "bay right top" (11 px): the cassette plate there may be recessed, so it is unclear which edge is which.
- "swoosh tip": the tip is soft and seen very obliquely from that low angle.

### Still uncertain

- **The Aero S is placed and fitted from one view, on two points:** its LED and the hopper's top. In that frame it
  seems turned a little towards the camera. Its side facing the bay doesn't show, though in the model it does. It may
  stand anywhere along the hose, so its place and angle in the lab are a layout choice. Its sculpted shell (the sweep
  of the silver over the dark) is approximate.
- **What the 260 and 180 mm run along is inferred.** The model puts the 260 mm along the bench. The front view
  ([6ZuKAAHb_20 at 0:33](https://youtu.be/6ZuKAAHb_20?t=33)) shows it in profile at a scale that fits 260 mm, not
  180 mm. Its height and the cover's are as published.
- **The extractor isn't in any frame.** It is the old generic unit, on the bench to the right. Malvern's own
  extractor usually stands on the floor.
- **The detail is guessed from close-ups:** the cassette's interior, the cell's windows, the beam's height and the
  layout inside the cover. The lid's dome shape was compared by eye only. It has no anchor besides its top.
- **The cassette is drawn but doesn't move.** At 3:00 of 6ZuKAAHb_20 it lifts out of the bay under the lid.
- **The cleaning step isn't animated:** the hopper off and the tray out, from 1:55 of iaHJ8QEwJ-I.
