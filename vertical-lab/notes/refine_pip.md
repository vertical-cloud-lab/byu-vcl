# Refining the PIP (Plastometrex PLX-Benchtop) against Plastometrex's footage (#303)

## Sources

- "Next Generation Mechanical Testing - Introducing the PLX-Benchtop", Plastometrex:
  [1:09](https://youtu.be/w7OZsrru9AI?t=69) (whole machine, front: the registered view),
  [0:00](https://youtu.be/w7OZsrru9AI?t=0) and [0:13](https://youtu.be/w7OZsrru9AI?t=13) (front, closer),
  [0:49](https://youtu.be/w7OZsrru9AI?t=49) (crosshead from the front left, sample by hand),
  [1:01](https://youtu.be/w7OZsrru9AI?t=61) (the profilometer's arm, shaft and pick-up from the front left).
- "Plastometrex Benchtop Indentation Plastometer Demonstration":
  [0:36](https://youtu.be/1qGM3JY2tFM?t=36) labels the load cell, indenter and profilometer;
  [0:55](https://youtu.be/1qGM3JY2tFM?t=55) shows the same arm moved about 50 mm towards the indenter.
- "How a PIP test works!" (Plastometrex's animation): [0:01](https://youtu.be/wL5z5wjLI1U?t=1) (whole
  machine, front right), [0:05](https://youtu.be/wL5z5wjLI1U?t=5) (indent),
  [0:09](https://youtu.be/wL5z5wjLI1U?t=9) (the pick-up under the indenter, on the indent),
  [0:10](https://youtu.be/wL5z5wjLI1U?t=10) (a rotation drawn at the arm's foot),
  [0:14](https://youtu.be/wL5z5wjLI1U?t=14) (left side).
- No published dimensions (search of Plastometrex's and Illinois MRL's pages), so the 500 mm width stays the scale.

## What changed and why

- **Profilometer.** It is not on a column. A slotted aluminium arm hangs from a carriage under the right of the
  crosshead and leans outwards. At the arm's foot a short shaft points to the front and carries the black stylus
  pick-up (1qGM3JY2tFM 0:36/0:55, w7OZsrru9AI 1:01). Parked, the stylus is about 110 mm right of the indenter's
  axis, outside the platen, at the sample's height. The scale for that is the platen's diameter in the 0:36
  close-up. Between 0:36 and 0:55 the whole arm moves sideways, top and foot alike, so it runs on a carriage and
  does not swing. The model's carriage runs along x. With the indenter lifted, the pick-up passes under it to the
  indent (animation 0:09), drops about 3 mm, traces across along x, then lifts and runs back out.
- **Load string.** It is a pancake load cell set into the floor, with eight posts and a plain stainless platen
  disc on top. Before, it was a small cell under a disc.
- **Indenter.** It comes down out of a stainless cylinder (about 40 mm across) under the crosshead and has a dark
  tip holder and a 1 mm-radius ball. Only this ram moves. The crosshead stays fixed.
- **Body.**
  - Matte black housing with rounded top edges. A silver trim runs round the waist, with a lozenge on each side.
  - Silver plinth on four feet.
  - Two columns with louvres on their inner faces.
  - The crosshead is a dark cowl between the columns: its lower front edge is bevelled, it has a raised middle
    panel and two yellow hazard labels, and there are silver blocks at its ends.
  - The front panel is framed by a U of blue LEDs.
  - The red e-stop on the right side has no yellow collar, and it sits about halfway up the LED arms, not below
    the waist.
- **Tour camera.** It is now low and nearly frontal, as the videos show the machine. From the old high camera, the
  crosshead hid the indenter and the profilometer.

## Fit (register.py, refs/pip/)

One view, `intro_0109_front` (w7OZsrru9AI 1:09). Picks: 13 points and 3 curves. **rms 6.3 px** (10.3 with the
start values). f = 1481 px, which fits a zoomed promo shot.

Fitted values, now in `PIP`:

- Overall: H 689, base_h 43, col_w 104, top_z0 (the waist) 387.
- LED U: half-width 172, from 52 to 196 mm above the waist.
- Crosshead: z 184-369, labels at x = +-126.
- Platen: top 56 mm above the floor, diameter 154.
- E-stop: 79 mm above the waist.

Worst picks are 10-12 px: the bay's bottom-left corner, the e-stop, the bay's top-right corner and the left
column's foot.

## Still uncertain

- **Depth D (560 mm) is not fitted.** A near-frontal view can't separate it from H: freed, it ran to its bound.
  It is roughly consistent with the animation's side view (0:14). A registered side or three-quarter view (that
  frame, or w7OZsrru9AI 0:50) is the next step. With it, yc (the indenter's depth in the bay) and estop_y could be
  fitted too.
- **The scale is still the 500 mm width estimate (+-20 %).** A known part, for example the load cell's model from
  its loadcellshop.co.uk label or the 40 mm e-stop head, could fix it.
- **How the stylus is lowered onto the surface and what drives the trace.** The animation draws a rotation about
  the shaft at the arm's foot. The model uses a small drop and a linear trace along x.
- **The back of the bay.** It is modelled as a light grey panel. The footage only shows light grey there.
