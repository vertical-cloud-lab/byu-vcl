# 3-D step animations of the rePowder atomizer

CAD-based replacements for draft 1's flat matplotlib schematics (removed after review; they are in the git history at
`3803f3b`): the machine is modelled in CadQuery, tessellated into PyVista and rendered off-screen, the same pipeline as
the PiPER camera-mount (#239), OT-2 lid-mount and atomizer charge (#222) renders. Parts move along their real assembly
paths: the lid hinges, the door swings on its back-edge hinge with the ultrasonic unit in it, the sealing rod lifts, the
nozzle holder screws into the crucible and the graphite nut onto the holder, several slow turns each. There is no
operator figure: hands are implied by the parts moving.

**Cutaways come in only when the step needs the inside.** Every animation opens on the closed machine, as the operator
sees it. The furnace and chamber are cut open at the furnace axis (front half removed) at the moment the action moves
inside, and close again for outside actions: in the furnace step the lid opens on the closed furnace and the cut appears
with the nozzle; the chamber goes back to whole to vent and open the door. `load_machine(..., defer=True)` adds both the
whole and the halved part, and `set_cut()` blends between them.

![machine](out/machine.png)

![section](out/section.png)

## Files

| File | What it is |
| --- | --- |
| [`model.py`](model.py) | The machine as named CadQuery parts with colours: cabinet, melting control panel, HMI, main switch; furnace body, faceted lid (window, HOT label, knob), coil, insulation (bottom, side, top/filling cone), graphite crucible with its cone floor and pour hole, nozzle (white side up) and holder, sealing rod, adapter, holder arm and lift post, wall thermocouple, the four charge rods; chamber, door with three clamps, view port, catch bowl, splash plate; ultrasonic stack (transducer, booster, sonotrode with KF50 flange, plate on its stud, protective cover); chute cone, valve, flange clamp, powder container; argon cylinder and regulator, vacuum pump, heat exchanger, air filter-regulator, and the utility lines. `meshes()` tessellates everything (whole, and halved at y = 0 with the cut faces tinted) and caches it in `.cache/`. |
| [`scene.py`](scene.py) | The `Scene` framework (after #239's `animate.py`): actors in groups that move together (groups can ride on other groups: the stack on the door, the rod on the arm), eased moves, opacity fades, colour and glow changes, camera moves, leader-line labels, gauge readouts, step label and wrapped caption. Each `step()` is one sub-step (one action, one caption) followed by a hold of at least 1 s; where particles, flow dots or the plate's vibration are running, the hold keeps them moving (`live=True`) instead of freezing the frame. Every frame is rendered once at 1280 × 720 and written to the MP4 (15 fps) and, every 1.5th frame, to the GIF (800 × 450, 10 fps, one palette, `gifsicle -O3 --lossy`). Text is drawn with PIL at each output's own size, so the GIF's text stays legible. |
| [`steps.py`](steps.py) | One animation per SOP step, under draft 1's step names so the tutorial build could switch over, plus `00_machine` (a tour) and `03b_chamber` (container, splash plate, door). |
| [`render.py`](render.py) | Hero stills at 1600 × 900: `out/machine.png` (labelled), `out/machine_clean.png` (no text; the machine in the right 60 %, artwork for title cards), `out/section.png` (the column cut at the furnace axis, with the furnace close up) and `out/compare.png` (the model beside the 720p video frames in [`ref/`](ref/), from about the same viewpoints). |
| `out/<name>.gif` | 800 × 450, 10 fps, ≤ 5 MB, for GitHub. |
| `out/mp4/<name>.mp4` | 1280 × 720, 15 fps, h264 yuv420p, no audio, for the narrated tutorials. Not committed (see `.gitignore`); regenerate with `steps.py`. |
| `out/<name>_still.png` | One representative 1280 × 720 frame. |
| `out/<name>.json` | `{name, fps, n_frames, size, substeps: [{label, caption, start_frame, end_frame}]}`: the MP4 frame range of every sub-step (motion plus its hold), for timing narration sentence by sentence. Every animation opens with 1 s of establishing view, counted in its first sub-step. |

## Running

```bash
export PIP_TIMEOUT=600 PIP_RETRIES=2
pip install cadquery pyvista                       # plus: apt-get install xvfb libgl1-mesa-dri gifsicle ffmpeg
xvfb-run -a -s "-screen 0 1920x1080x24" python render.py          # hero stills
xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py           # every animation
xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py 06_pour   # one (or several) by name
PREVIEW=1 xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py 06_pour   # last frame of each sub-step only, as a contact sheet in /tmp
```

A frame takes about 0.25 s (software OpenGL, SSAA and depth peeling for the see-through parts), so an animation takes
two to three minutes. The first run builds the CadQuery model (about 15 s) and caches the meshes; editing `model.py`
invalidates the cache. When two renders run at once, give each its own display (`xvfb-run -n 201 …`, `-n 202 …`):
`-a` can hand both the same one.

## The animations

| | |
| --- | --- |
| **0 · Tour of the machine** — furnace, controls, chamber and door, ultrasonic unit, cone and container, utilities, then the cutaway ![](out/00_machine.gif) | **1 · Utilities on** — main switch, chilled water, heat exchanger, compressed air, argon; flow shown as dots along each line ![](out/01_utilities.gif) |
| **2 · Ultrasonic stack** — built into the door while it is locked open: transducer → booster (65 N·m) → sonotrode (60 N·m) → into the door housing → plate (50 N·m) → scan → wet test → cover ![](out/02_stack.gif) | **3 · Furnace prep and loading** — lid opens (closed machine), then the cutaway: holder screwed into the crucible, crucible straight down into the coil, nut threaded on from below through the left door with the crucible held at the top (snug, never forced), insulation, thermocouple from the back right, sealing rod before metal, charge, lid ![](out/03_furnace_load.gif) |
| **3b · Chamber** — container lifted and clamped, catch bowl and splash plate (the only see-through moment), door shut, three star-knob bolts ![](out/03b_chamber.gif) | **4 · Gas wash** — furnace pumped and back-filled while the chamber holds overpressure, then the chamber, then washes at 250 and 500 °C ![](out/04_gas_wash.gif) |
| **5 · Melt** — overshoot, melt cues, rods slump into a pool, setpoint down to ~800 °C, 2 min hold ![](out/05_melt.gif) | **6 · Pour and atomize** — vibration, draining pressure, rod up, first drops bounce, turbo, spray off the plate, powder into the container ![](out/06_pour.gif) |
| **7 · End, cooldown, collect** — turbo, rod down, stops, cool to ≤400 °C, vent, door open, brush down, container off ![](out/07_end_cooldown.gif) | **8 · Clean and reset** — brush, plate off, rod out, nozzle check, reassemble ![](out/08_clean.gif) |

Heat is shown as colour, not physics: the charge goes grey → dull red → orange with the readout temperature, the coil
brightens while the generator runs, the melt is an emissive orange. The argon is a light-blue translucent volume that
fades out under vacuum. Droplets and powder are a small ballistic particle model in slow motion, kept to the back half
so they read against the cutaway. The plate's vibration is exaggerated (±1.2 mm) so it shows. Numbers in captions and
readouts are those used in training ([`../sop.md`](../sop.md)); they are illustrative, not a recipe.

## Measured vs. assumed

The proportions were re-measured for draft 3. Nothing has been measured with a rule yet. The sources are:

- **720p frames** of the training videos, pulled through the stream-cam Pi with `../tools/hls_sections.py`:
  - front, low: `9kn-HhXCr1o` 25:00;
  - front-left: `FDRTt68Vfvo` 51:00 and 17:00, `wRc8p2_FnJo` 41:00;
  - left, door closed: `58wJ_Khwgyk` 77:00;
  - door open: `58wJ_Khwgyk` 25:00;
  - frame open: `wRc8p2_FnJo` 5:00;
  - the thermocouple going in: `HTlUrAr5HVU` 4:10–4:35.
- **AMAZEMET's 2025–26 "rePOWDER Induction" renders**, Blue Power's AUS 500 photo, and PR #240's rough model.
- **The documented numbers**, which set the scale:
  - envelope 1000 × 800 × 1600 mm (O&MM);
  - feet Ø50 at 714 × 600 (Facility Guide);
  - chamber 57 L;
  - crucible (#222).

Ratios read off the frames were scaled to those numbers. The videos come from phones, some of them wide-angle, so lengths
near the frame edges were not used.

| Part | Source | Status |
| --- | --- | --- |
| Crucible: Ø57.1 bore, 81 mm straight, 36° cone floor, 9.1 mm wall, Ø6.9 pour hole; Ø12.6 ball-tipped sealing rod; coil r 47 | #222 `charge_cad.py` (Indutherm GU500 section scaled to the quoted 225 cm³); Bartosz's 20 mm gap and 10–12 cm depth | Documented, scaled |
| Overall: blue frame 745 W × 500 D × 1600 H on base rails, feet at 714 × 600; ultrasonic unit sticking out ~250 mm on the left, so ~1000 W overall | O&MM envelope, Facility Guide feet, AMAZEMET 2026 render scaled to 1600 mm | Envelope documented; frame depth inferred |
| Electronics: induction generator, PLC, relays and pneumatics inside the blue frame, behind side doors. No separate electrical cabinet | `wRc8p2_FnJo` 0:54 (Bartosz: cabinet and induction module combined), 4:00–10:00 (frame open) | Observed |
| Chamber: D-shaped in plan, flat front 400 mm, half-round right end r 110, 240 deep, 710 tall. Left wall vertical for the top half, then the underside slopes 45° down to a round bottom under the rounded end; 59 L inside | Front frames (`9kn-HhXCr1o` 25:00: slope from the left wall to the outlet at the bottom right), AMAZEMET render (taller than wide, W:H ≈ 0.8), the 57 L volume for the depth | Shape observed; size scaled, ±15 % |
| Outlet, cone, valve, container under the rounded end; container bottom ~60 mm off the floor | Frames (`58wJ_Khwgyk` 77:00), render | Position observed; sizes assumed |
| Door: U-shaped (flat top, round bottom), 200 × 325, on the left face, hinged on its back edge. Three swing bolts with star knobs (two on the front edge, one under it); small sight glass | `58wJ_Khwgyk` 25:00 and 77:00, `FDRTt68Vfvo` 17:00 | Observed; size scaled |
| Ultrasonic stack through the door's lower half at 40°, plate under the nozzle. 40 kHz, plate 20 × 100 Ti, booster 1.5:1, torques 65 / 60 / 50 N·m | Quote, O&MM, SOP; angle from the front and side frames (35–45°) | Torques documented; lengths assumed |
| View port: 12-sided cover on the front face under the furnace, tilted down at the plate | Front-left frames | Observed; size scaled |
| Furnace body Ø270 on the chamber's top plate, axis 170 mm in from the left face; faceted lid hinged on the left; coil leads on the left; connector plate at the back left | Frames (`wRc8p2_FnJo` 41:00 and 47:00), render | Observed; proportions scaled |
| Thermocouple at the back right: plug on the rim, sheath down into the crucible wall | `HTlUrAr5HVU` 4:10–4:35 (the operator threads it in at the back right) | Observed |
| Nozzle holder: its threaded shank passes the bottom insulation, the furnace floor and the chamber's top plate. A thin graphite nut (Ø60 × 12, a few threads) and a lower seal go on it inside the chamber | `wRc8p2_FnJo` 36:52, 37:27 ("from the bottom a graphite nut and seal, from the top the nozzle holder and one more seal") and 46:29–47:19 ("the thread is in the chamber … secure it with the nut") | Order and access observed; sizes assumed |
| Insulation sizes, charge (4 × Ø17 × 100 mm 6063 ≈245 g) | SOP order of parts; SOP charge limits | Assumed / chosen to fit |
| HMI: 15.6 in Weintek cMT2166X, 400 × 263, on an arm at the frame's right front edge; GU 500 panel in a recess at the upper right; main switch under it | Datasheet, frames | Observed; sizes partly documented |
| Utilities (argon, vacuum pump, heat exchanger, air) and their hose routes | Frames | Schematic |

When anything is measured, change the constants at the top of `model.py`; every animation follows.

## Known issues

- The chamber's exact size and the door's width are scaled from frames (±15 %). A tape measure at the machine would
  settle them; the constants are `CH_X`, `CH_Y`, `CH_BOTTOM`, `SLOPE_C`, `DOOR_W` and `DOOR_Z` in `model.py`.
- In cutaways the three star-knob bolts stay whole, so the front one floats slightly in front of the cut.
- No lettering on any part ("BLUE POWER", "aus500", "GU 500 AMA"); the HMI screen is placeholder rectangles.
