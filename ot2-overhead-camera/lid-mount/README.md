# OT-2 lid camera mount

A mount that holds the **Raspberry Pi HQ Camera + Waveshare 8–50 mm C-mount zoom**
pointing straight down through the OT-2's top window ("the plexiglass"), with the
**Raspberry Pi 5** riding on top. It tapes down first, so you can position and test it
without cutting anything, and later bolts through four holes next to a small lens cutout.

![Mount on the OT-2 over slot 5](renders/ot2_context.png)

| Assembly | Section through the optical axis | Simulated camera view, f = 25 mm |
|---|---|---|
| ![Assembly](renders/assembly.png) | ![Section](renders/section.png) | ![Simulated view](renders/camera_view_sim.png) |

It was built along two paths, as requested in
[#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84):

| Path | What | Status |
|---|---|---|
| **A: programmatic CAD** | [`cad/lid_mount.py`](cad/lid_mount.py), a parametric CadQuery model with automated clearance checks; [`cad/ot2_context.py`](cad/ot2_context.py), which checks it against Opentrons' own OT-2 model; renders; a 1:1 drill template | Built, checked, exported |
| **B: Onshape** | [`onshape/onshape_api.py`](onshape/onshape_api.py) (REST API: native sketch/extrude features plus a STEP import) and [`onshape/onshape_ui.py`](onshape/onshape_ui.py) (Playwright, working the Part Studio with mouse clicks, drags and typed dimensions) | Written, but **not run past the sign-in page**, because CI has no Onshape credentials. See [Path B](#7-path-b-onshape). |

---

## 0. The OT-2 lid, from Opentrons' CAD

Opentrons publishes a STEP model of the OT-2 and DXFs of its windows at
[github.com/Opentrons/ot2](https://github.com/Opentrons/ot2) (2018).
[`cad/ot2_context.py`](cad/ot2_context.py) downloads it and measures it; the file itself
isn't committed here, because that repo has no licence file.

| | | |
|---|---|---|
| Top window | **5.00 mm** thick, 564.9 × 455.1 mm | measured from the STEP |
| Deck surface → underside of the window | **585.2 mm** | measured from the STEP. #84's options doc estimated ~400 mm from the robot's outside height; that estimate is wrong, and the real ~590 mm from deck to lid is the "~24 in" case |
| Pipette-head top cover → underside of the window | **9.1 mm**, and the head can travel under the whole window | measured from the STEP. **Nothing may hang more than a few mm below the lid**, which is why the bolts below have low heads |
| How it's held | 4 × M4 × 12 low-profile screws in corner slots; the front and back edges rest on ledges, and the sides tuck under 2 mm lips | [manual](https://opentrons-landing-img.s3.amazonaws.com/Manuals/OT2_Manual.pdf), [window DXF](https://github.com/Opentrons/ot2/blob/master/windows/TOP_WINDOW_RevA2.DXF) |
| Removable? | **Yes**: unscrew the 4 screws, slide it, lift it off. That means it can be drilled on a bench | [Opentrons support](https://support.opentrons.com/s/article/HEPA-Module) |
| Material | The 2018 drawing says acrylic; the current specs and the manual say polycarbonate. **Check yours, and machine it as if it were acrylic.** | [specs](https://docs.opentrons.com/ot-2/system-description/specs/) |

Two more constraints. The HEPA Module replaces the top window, so this mount doesn't
work on a HEPA-equipped OT-2. The window also presses a safety switch: if the door
safety switch is enabled in Robot Settings, the robot won't run while the window is off.

---

## 1. What's in the box

| Part | File | Notes |
|---|---|---|
| Base | [`exports/base.stl`](exports/base.stl) | 112 × 112 mm plate (144 mm across the tape tabs), a Ø46 mm lens aperture inside a 14 mm light collar, four 10 mm posts, and four M4 nut traps |
| Deck | [`exports/deck.stl`](exports/deck.stl) | The camera hangs underneath from its four M2.5 holes, the Pi 5 sits on top, and a slot passes the ribbon cable |
| Drill template | [`exports/drill_template.stl`](exports/drill_template.stl), or print [`exports/drill_template_1to1.pdf`](exports/drill_template_1to1.pdf) on paper | Marks the lens cutout and the four bolt holes |
| Spacers | [`exports/spacers.stl`](exports/spacers.stl) | 4 × 5 mm Pi 5 standoffs, plus 4 × 2 mm shims that raise the deck if the lens ever needs to sit higher |
| Everything, in colour | [`exports/assembly.step`](exports/assembly.step) | With reference models of the lid, camera, adapter, lens and Pi 5 |

STEP files for every printed part sit next to the STLs. The drill template also comes as a
[DXF](exports/drill_template_1to1.dxf) for a laser cutter.

**Print** in black PETG or PLA, which is opaque and cuts stray light. Use 0.2 mm layers,
3–4 walls (the screw bosses need them) and 20–30 % infill. Every STL is already in print
orientation, and **none needs supports** (see [`renders/print_layout.png`](renders/print_layout.png)).

### Hardware

| Qty | Part | Where |
|---|---|---|
| 4 | M2.5 × 16 mm screw + M2.5 nut | camera → deck (nuts sit in traps on the deck top) |
| 4 | M2.5 × 16 mm screw + M2.5 nut | Pi 5 → spacers → deck (nuts in traps on the deck underside) |
| 4 | M3 × 16 mm screw | deck → posts (self-tapping into Ø2.6 pilots; set `post_pilot_d = 4.0` for heat-set inserts) |
| 4 | **M4 × 16 button-head (ISO 7380)** + M4 nut + thin nylon washer | base → lid, **phase 2 only**. The low 2.2 mm head keeps the screw clear of the pipette head underneath. M4 × 12 also works; it just reaches through the nut |
| – | Painter's or gaffer tape, or removable double-sided mounting strips | **phase 1** |
| – | Optional: 1–2 mm black adhesive foam | light seal under the base, around the aperture |

The camera, lens, C–CS adapter, Pi 5, Active Cooler and 200 mm Pi 5 camera cable are the
parts already bought on ME order 12704 (see #84).

---

## 2. Assemble

1. Drop four **M4 nuts** into the hex traps on the base.
2. Drop four **M2.5 nuts** into the traps on the top of the deck. Hang the camera under the
   deck with M2.5 × 16 screws, driven up from the lens side through the camera's corner
   holes. The **ribbon connector goes toward the cable slot**, the side marked by the
   arrow engraved on the base (−Y).
3. Plug the camera cable into the camera and feed it up through the slot.
4. Screw on the lens with **one** C–CS adapter. The lens and the camera each ship with one,
   and in July the camera wouldn't focus because the adapter ring had been pushed in too far
   (#84). Set the zoom to **about 25 mm**. At the lid, the lens front is 585 mm from the top
   of a plate, which gives a 152 × 114 mm field of view: the plate plus a margin on every
   side, at 26.7 px/mm (~180 px across each well). Above about 27.6 mm the margin
   around the plate drops below 5 mm.
5. Screw the deck onto the posts with the M3 screws.
6. Fit the Pi 5 on the four printed spacers with M2.5 × 16 screws down into the nuts on the
   deck underside, with its power/HDMI edge toward the cable slot. Connect the cable to
   either CAM/DISP port.

The zoom, focus and iris rings stay reachable through the 84 mm windows between the posts.
Their thumbscrews sweep about Ø55 mm, and the posts are 33 mm clear of that.

---

## 3. Where on the lid

The mount fits over **slots 4–11**. Over the front row (slots 1–3) the base would run into
the frame at the window's front edge; `ot2_context.py` finds 210 mm³ of overlap there.
**Slot 5** is the natural choice. It's in the middle column, clear of the gantry's home
position at the back right, and 81 mm in front of the window's centre. That is closer
to the front edge, which carries the panel, so it sags less there than in the middle.

Where the lens axis goes, measured on the window from its centre. The centre is the middle
of the four screw slots; +x points right and +y points toward the back:

| Slot | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|
| x (mm) | −132.5 | **0** | +132.5 | −132.5 | 0 | +132.5 | −132.5 | 0 |
| y (mm) | −81.0 | **−81.0** | −81.0 | +9.5 | +9.5 | +9.5 | +100.0 | +100.0 |

These come from 2018 CAD, so treat them as a starting point and let the live preview in
phase 1 decide. The same numbers, measured from the window's front-left corner, are in
[`exports/ot2_fit.json`](exports/ot2_fit.json).

Because the sensor's long axis is X, the plate's 12 columns should run **left to right**
across the OT-2, which is how labware normally sits on the deck.

## 4. Install, phase 1: tape, no cutting

1. Home the robot (the gantry parks at the back right, out of view) and put a plate in
   the slot you picked.
2. Put the mount on the lid above that slot, with the arrow on the base pointing at the door.
3. Start `preview_server.py`
   ([#84](https://github.com/vertical-cloud-lab/byu-vcl/blob/e949ad0/ot2-overhead-camera/README.md#5-zoom-and-focus-live-preview))
   and slide the mount until the plate is centred and square in the preview. Zoom first,
   then focus.
4. Tape the four tabs down.

At this stage it images **through the window**. The collar keeps room light off the patch
of window under the lens, which is where reflections would come from. If the images are
good enough like this, the cutout is optional.

## 5. Install, phase 2: cutout and bolts

1. With the mount in its final spot, **trace the base outline and the four tab notches**
   onto the window with a fine marker, then lift the mount off.
2. **Take the window off** (4 screws, slide, lift) and drill it on a bench. That keeps chips
   out of the robot and avoids leaning on the panel.
3. Print [`drill_template_1to1.pdf`](exports/drill_template_1to1.pdf) at 100 % /
   "Actual size", **check the 50 mm and 2 in scale bars with a ruler**, and line it up
   with the tracing. Alternatively, use the printed drill template. Centre-punch the
   five marks.
4. Drill the four **Ø5 mm** bolt holes. The extra 1 mm over M4 gives the panel room to
   expand. Clamp the panel over a wooden backer board, leave any protective film on, and
   use a sharp plastic-cutting or step drill at low speed with light pressure.
5. Cut the lens hole with a **2 in (50.8 mm) hole saw** at low speed and deburr it.
6. Put the window back so it presses the safety switch again. Bolt the base down with
   the M4 button-heads from **inside** the robot, up into the trapped nuts, with the
   nylon washer under the head. Tighten them snug and no more; over-tightening cracks
   acrylic.
7. **Check the clearance.** With the robot homed (head fully up), jog the gantry slowly
   under the mount and look along the lid. The screw heads plus washers hang about 3 mm
   below the window, against 9.1 mm of clearance in the CAD. The window already sags
   about 1 mm under its own weight across the 450 mm span, and the ~0.4 kg mount adds up
   to about 0.5 mm; both are simply-supported beam estimates, not measurements.

Why 2 in: the view cone from the lens front clears a 50.8 mm hole across the **whole 8–50
mm zoom range**. At the 25 mm working zoom it is only ~40 mm across at the window's
underside, so a 1¾ in (44.5 mm) saw would also work. There is 19 mm of panel between the
cutout and each bolt hole.

---

## 6. Design and checks

Coordinates: the optical axis is at X = Y = 0, Z = 0 is the top face of the window, and +Z
is up. Every height follows from the camera and lens stack:

| Z (mm) | |
|---:|---|
| −590.2 | deck surface (Opentrons CAD) |
| 0 | top of the window |
| 9.0 | lens front, 3 mm above the base and inside the collar |
| 20.0 | top of the collar |
| 72.8 | lens flange |
| 77.8 | camera CS seat (after one 5.03 mm C–CS adapter) |
| 93.7 | back of the camera PCB |
| 99.7 | deck underside = top of the posts (6 mm standoff clears the FPC connector) |
| ~127 | top of the Pi 5 and cooler, the tallest point |

`python cad/lid_mount.py` rebuilds the parts and runs these checks, saved to
[`exports/checks.json`](exports/checks.json). `python cad/ot2_context.py` adds the OT-2
checks, saved to [`exports/ot2_fit.json`](exports/ot2_fit.json). Everything passes except
the front-row slots, which is why the mount goes over slots 4–11:

| Check | Result |
|---|---|
| Interference, 12 pairs: base and deck against the camera, lens, Pi 5, spacers and window, plus the thumbscrew sweep and the view cones | 0 mm³ for every pair |
| Lens front barrel to collar | 3.0 mm radial gap |
| Thumbscrews to the nearest post | 32.8 mm |
| View cone vs. base aperture and lid cutout | clear from 7.5 mm focal length up, i.e. the full 8–50 mm zoom range |
| Pi 5 board to the deck screw heads (plan view) | 4.25 mm, so the deck comes off without removing the Pi |
| Base vs. the OT-2 frame, mount over each slot | 0 mm³ for slots 4–11; overlaps for 1–3 |

Sources for the numbers:
- The HQ Camera's
  [official mechanical drawing](https://datasheets.raspberrypi.com/hq-camera/hq-camera-cs-mechanical-drawing.pdf):
  38 mm board, Ø2.5 holes 4 mm from each edge on a 30 mm square, and 18.58 mm overall depth
  including the 2.75 mm connector.
- Waveshare's [8–50 mm lens spec](https://www.waveshare.com/8-50mm-Zoom-Lens-for-Pi.htm):
  Φ40 × 68.3 mm, 148 g, minimum object distance 0.20 m.
- Opentrons' OT-2 model, as described above.

**Estimates to check on the bench.** Each one is a single number in `Params`:
- `lens_thread_len = 4.5` and the layout of the rings and thumbscrews come from product
  photos, not a drawing. If the lens front ends up lower than expected, there are still
  9 mm before it touches the window. Add a 2 mm shim under the deck for each 2 mm you need.
- `ring_sweep_d = 64` is generous; the modelled thumbscrews reach Ø55 mm.
- The simulated view's pinhole sits 20 mm inside the lens front (`PUPIL_IN_LENS`). Moving
  it changes the field of view by about 3 %.

At 585 mm the view is close to straight down but not telecentric. Toward the plate's
edges the camera sees about 1 mm of each well's wall, which is visible in the simulated
view. Keep that in mind when you segment wells near the edges.

To rebuild:

```bash
pip install -r cad/requirements.txt
cd cad
python lid_mount.py                  # checks + STEP/STL/assembly -> ../exports
python template.py                   # 1:1 SVG/DXF/PDF drill template
xvfb-run -a -s "-screen 0 1920x1080x24" python render.py        # PNG renders
xvfb-run -a -s "-screen 0 1920x1080x24" python ot2_context.py   # OT-2 fit, FOV, context renders
```

Drop `xvfb-run ...` on a machine with a display.

---

## 7. Path B: Onshape

**There are no Onshape credentials in CI**, so nothing below has touched an Onshape
account yet. No `ONSHAPE_*` variable reaches the runner, and `claude.yml` passes none.
What could be tested without an account, was:

| Script | Tested here | Still untested |
|---|---|---|
| [`onshape_api.py`](onshape/onshape_api.py): REST API. It creates a document, builds the base as native sketch and extrude features in a "Base (native features)" Part Studio, imports every STEP file, and optionally shares the document | The whole flow against a stub (`--dry-run`): **27 requests**, and every payload is in [`dry_run.json`](onshape/dry_run.json) | The real API |
| [`onshape_ui.py`](onshape/onshape_ui.py): Playwright. It signs in, creates a document, then draws, dimensions, extrudes and mirrors the base with mouse clicks, drags and typed values | From a GitHub runner, the sign-in page loads and its selectors resolve ([screenshot](onshape/evidence/signin-page.png)). Onshape's own [browser check](onshape/evidence/onshape-browser-check.png) passes in headless Chrome 153 with SwiftShader WebGL: WebGL, WebSockets, and 1.5 M triangles/s | Everything after sign-in |

> ⚠️ **Onshape's [Terms of Use](https://www.onshape.com/en/legal/terms-of-use), section 4(a)(ix), forbid
> "any robot, spider, scraper or other automated means to access the Service."** The REST
> API is the sanctioned route, so use `onshape_api.py` for real work. Run `onshape_ui.py`
> only if the account owner accepts that; otherwise treat it as the manual recipe below.

### Turning it on (human steps)

1. On the Onshape account that should own the documents, go to **My Account → Developer →
   API keys** and create a key with the **Read** and **Write** scopes, plus **Share** if the
   script should share documents. Individual accounts get at most two keys.
2. Add repo secrets `ONSHAPE_ACCESS_KEY` and `ONSHAPE_SECRET_KEY`. For the UI script, also
   add `ONSHAPE_EMAIL` and `ONSHAPE_PASSWORD`, for an email-and-password login without 2FA
   (not Google or Microsoft sign-in).
3. Pass them through the `env:` block of `.github/workflows/claude.yml`. The Claude app
   can't edit workflows, so this has to be a human commit:
   ```yaml
             ONSHAPE_ACCESS_KEY: ${{ secrets.ONSHAPE_ACCESS_KEY }}
             ONSHAPE_SECRET_KEY: ${{ secrets.ONSHAPE_SECRET_KEY }}
             ONSHAPE_EMAIL: ${{ secrets.ONSHAPE_EMAIL }}          # UI script only
             ONSHAPE_PASSWORD: ${{ secrets.ONSHAPE_PASSWORD }}    # UI script only
   ```
   and list them in CLAUDE.md's secret inventory.
4. Ask `@claude` to run it:
   ```bash
   pip install -r onshape/requirements.txt
   python onshape/onshape_api.py --share someone@byu.edu     # add --public on a Free plan
   python onshape/onshape_ui.py --chrome /usr/bin/google-chrome
   ```

Budget: a run of `onshape_api.py` costs about 30–50 calls, depending on how long each
import takes to finish. Free, Standard and EDU Student plans get
[2,500 a year](https://onshape-public.github.io/docs/auth/limits/).

### Manual recipe

This is the sequence `onshape_ui.py` automates. Everything is sketched on the **Top**
plane, and it takes about ten minutes by hand:

| # | Sketch | Feature |
|---|---|---|
| 1 | Centre-point rectangle on the origin, 112 × 112 | Extrude 6 mm, **New** |
| 2 | Circle on the origin, Ø52 | Extrude 20 mm, **Add** |
| 3 | Circle on the origin, Ø46 | Extrude **Through all**, **Remove** |
| 4 | Centre-point rectangle 10 × 10, centre 47 mm right of and 47 mm above the origin | Extrude 99.66 mm, **Add**; then **Mirror** (Feature mirror) across *Right*, then the extrude and that mirror across *Front* |
| 5 | Circle Ø4.5, centre at (33, 33) | Extrude **Through all**, **Remove**; mirror the same way |

To check it, import [`exports/base.step`](exports/base.step) into the same document. The
two should coincide apart from the nut traps, tape tabs, fillets and engraved arrow,
which only the CadQuery model has.
