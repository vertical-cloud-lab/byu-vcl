# The fan under the deck, so the deck is the spacer (mock-up, 2026-11-19)

Asked by @benwhitney5463 on [PR #348](https://github.com/vertical-cloud-lab/byu-vcl/pull/348):
the 4.6 mm spacer isn't enough for steady stirring, and a bigger one puts the vial even higher.
Could the fan go under the deck and use the 9 mm deck as the spacer? The vial would then stand on
the deck, held by a holder that isn't under it.

**Status: a mock-up to discuss.** Nothing is printed, measured or checked for printing. The
magnet numbers come from the same model as
[`../analysis/coupling_vs_height.py`](../analysis/coupling_vs_height.py), calibrated on the same
observations.

![Section: today's stack on the 4.6 mm spacer, and the under-deck mock-up](../img/under_deck_section.png)

![The mock-up on the deck, from below, and exploded](../img/under_deck_views.png)

## The idea

Two new printed parts. Everything else is today's compact stirrer, unchanged.

- **Collar, on the deck (new).** The 9-vial holder's cup (the 2 mm ring, the four spring fingers
  up to 17 mm, the 3° pocket), with **no floor**. The vial goes through it and stands on the deck.
  Two bars, 12 mm wide and 3 mm thick, carry four Cubware pill keys (9.8 × 24.8 mm) that go 3 mm into four deck
  slots. Nothing of it is under the vial.
- **The deck is the spacer.** The vial stands between four slots, so it is on solid polycarbonate.
  The nearest slot edge is 14.5 mm from its axis, and the vial's radius is 13.75 mm. In deck
  coordinates that is X ≈ 149.2 + 25n, Y ≈ 67.5 + 45m: midway between two slot columns, like
  today's stirrer, but also midway between two rows.
- **Frame, under the deck (new).** It replaces the vial holder. It is the compact holder's flange
  up to its recess ceiling (stirrer z 20 → 23.83), with the cup and the 1.2 mm floor gone, so its
  top face sits against the deck's underside. It has:
  - a Ø20.6 bore for the carrier;
  - the Hall sensor's pocket at −X (r 10.2–13.4), open to the deck, so the sensor sits exactly
    where it does today relative to the magnets, with a groove for its leads;
  - counterbores for the same four M3 × 20 screws that hold it and the fan to the base;
  - four half-pill bosses that go 5 mm up into the same slots as the collar's keys.
- **Reused as they are:** the compact base, the fan, the magnet carrier and magnets, the Hall
  sensor, the junction board, the cable and the four M3 × 20 screws. The frame goes on where the
  holder went.
- **Clamp.** Four M3 × 12 screws go in from the top, through the collar's bars and keys, into
  heat-set inserts in the frame's bosses, at (±12.5, ±28) mm. Each slot holds a key and a boss,
  1 mm apart, so the screws squeeze the deck between the collar and the frame. Because keys and
  bosses sit in the same slots, the magnets line up with the vial to within the slots'
  0.1 mm a side. Being screwed down, the collar can't come up with a cap when the capper pulls it
  ([risk 3](../README.md#risks-and-open-questions) goes away). The screws are 31 mm from the axis,
  against 8.1 mm for the magnets' outer edge. Even so, use non-magnetic ones (A4/316 or brass).

`build_under_deck.py` draws the two parts from `vial_stirrer.fs`'s numbers, through
`compact/build_compact.py`. They are [`step/under-deck/collar.step`](../step/under-deck/collar.step) and
[`frame.step`](../step/under-deck/frame.step), with STLs in [`stl/under-deck/`](../stl/under-deck).

## What the deck does to the coupling

g is the gap from the drive magnets' top faces to the vial's outside bottom. "Pull" is the
magnets' pull on the bar, relative to where the fan stalled on 11-04 (vial 3 mm up). It sets the
friction under the bar and the thrust on the fan's bearing, which is what the fan has to beat. The
earlier analysis aimed for about 0.5. Ranges are over the four guessed bar cores. The output is in
[`coupling_through_deck_output.txt`](coupling_through_deck_output.txt).

| 15 × 6 mm bar | g, mm | pull | pull-out torque, mN·m |
|---|---:|---:|---:|
| today's holder, vial seated | 2.4 | 2.63–2.76 | 0.29–1.07 |
| vial 3 mm up: the 11-04 stall | 5.4 | 1.00 | 0.14–0.52 |
| on the 4.6 mm spacer (now) | 7.0 | 0.62–0.63 | 0.10–0.37 |
| **under a 9 mm deck** | **10.2** | **0.26–0.28** | **0.05–0.19** |
| under a 9 mm deck, two magnets stacked per pocket | 10.2 | 0.44–0.47 | 0.09–0.34 |
| under a 10 mm deck (Cubware's STEP) | 11.2 | 0.21–0.22 | 0.04–0.16 |

The water drag on the bar is at most 0.019 mN·m at 600 rpm and 0.075 mN·m at 1200 rpm (an upper
bound, with the water held still).

- **The pull drops to about 0.27,** from 0.62 on the spacer: well under half the friction, and
  under the 0.5 aimed for. That is what should let it start from rest every time and hold speed.
- **The coupling holds at 600 rpm** with 2.6–10× margin over the drag bound. **At 1200 rpm** the
  weakest guessed core (0.65×) would slip. Stacking two of today's magnets in each pocket fixes
  that: 1.1–4.5× at 1200 rpm, with the pull still at 0.45. That takes a carrier 1.6 mm thicker,
  and a frame 1.6 mm thicker to keep the gap. Under the deck there is room for both; they aren't
  drawn.
- **The Hall signal gets cleaner.** The bar is further from the sensor, so the smaller peak is
  17.6–19.5 mT (15.9–19.1 on the spacer, 11.7–18.3 seated). The US1881 needs 9.5.
- **The rotor is pulled up less** (the same 0.27×), so the carrier's 1.1 mm gap under the deck is
  less likely to close.
- **Limits:** the same static model as before, calibrated on Ben's ~3 mm by eye. The bar's core,
  the friction and the fan's torque are not known.

## Heights

| | vial bottom, mm above the deck | rim, mm above the deck | rim, CubOS deck Z |
|---|---:|---:|---:|
| 9-vial holder (vial_2) | 18.0 | 75 | 56 |
| stirrer on the 4.6 mm spacer (vial_1) | 29.6 | 87 | 66 (taught) |
| **under-deck mock-up** | **0** | **57** | **≈ 38** |

- **The tip clears a capped vial by much more.** It travels at deck Z 87 with a tip on, and the cap
  is now 28–30 mm lower than on the spacer. The "vial sits too high" problem goes away.
- **CubOS can reach it.** In the G-code from the 11-18 run, decap went to gantry Z = rim − 1 (Z55
  for vial_2, Z65 for vial_1). Here that is Z37. Aspirating at −35 puts the pipette at Z38 (tip end
  at deck Z 3), and blowout at −20 at Z53. All of these are inside the working volume (z_min 0).
- **But the head comes 18 mm lower than it has gone on this deck so far**, 28 mm lower than for
  vial_1 today. While the capper decaps this vial with a tip on, the tip end is at about deck Z 2,
  55 mm +X and 11 mm +Y of the vial (the pipette's offset). Nothing taller than about 20 mm may
  stand there. Check with a mock run and `cubos/tools/capped_vial_keepout.py`, and jog slowly the
  first time.

## What it costs

- **Room under the deck.** The base hangs 23.8 mm below the deck's underside, over a 49 × 72 mm
  frame, plus the cable. I don't know what is under the CubXL deck.
- **Four slots instead of two.** The collar is 37 × 71 mm on the deck and uses two columns of two
  rows.
- **It stays put.** Moving it means four screws from the top while holding the drive underneath.
- **Liquid:** the vial stands on solid deck, and the drive is under 9 mm of polycarbonate, away from
  anything spilled on the deck.
- **Cable:** it runs under the deck, out of the gantry's way.
- **Printing isn't worked out.** The frame prints bosses up with no supports. The collar's keys
  hang under its bars. Either print them with supports, or make them separate press-fit keys like
  today's, cut to 3 mm.

## Questions for Ben

1. What is under the deck where the stirrer would go? It needs about 25 mm of clear height below
   the deck's underside over 50 × 72 mm, and a way out for the cable. A photo would settle it.
2. Is the deck 9.0 mm there? At 10 mm the gap is 11.2 mm, which still couples at 600 rpm.
3. Is anything within about 55 mm +X and 11 mm +Y of that spot taller than about 20 mm? The
   pipette tip passes there while the capper works this vial.
4. Should the collar keep the 9-vial holder's spring fingers? They are what holds the vial while the
   capper twists the cap, so the mock-up keeps them.

## Run

```bash
pip install cadquery magpylib trimesh shapely networkx matplotlib pyvista    # PIP_TIMEOUT=600 PIP_RETRIES=2
python under-deck/build_under_deck.py                              # stl/under-deck/, step/under-deck/
python under-deck/coupling_through_deck.py > under-deck/coupling_through_deck_output.txt
python under-deck/render_under_deck.py section                     # img/under_deck_section.png
xvfb-run -a python under-deck/render_under_deck.py views           # img/under_deck_views.png
```

Run from `hardware/vial-stirrer-cubxl`.
