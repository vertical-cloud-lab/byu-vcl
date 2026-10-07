# PiPER ↔ CubXL vial handling

Figures and numbers behind the review in
[#266](https://github.com/vertical-cloud-lab/byu-vcl/issues/266): what Chris's CubXL mock-up
covers, what it leaves out, and a proposed handoff dock for the PiPER.

| File | What it is |
|---|---|
| `sketch-2d.png` | Plan, a section on the arm's centre line, and a detail of the dock |
| `layout-3d.png` | The same layout in 3D, with a close-up of the 45° grasp on the carrier's handle post |
| `geometry.py` | Fetches the mock-up parts and Cubware's real deck, and places the CubXL, dock and carrier |
| `analysis.py` | Measures the parts, then works out tool windows, payload and grip, reach and IK, and tolerances. Writes `results.json` |
| `render.py` | Draws the two figures |
| `piper_fk.py` | PiPER kinematics from AgileX's URDF, copied from `robot-arm/enclosure/` on #254 |

To regenerate, run `python analysis.py && xvfb-run -a python render.py`. The scripts fetch three
things into `/tmp`, so nothing third-party is vendored here:
- Chris's parts, from the zip attached to #266
- the PandaDeck plate from [Ursa-Laboratories/Cubware](https://github.com/Ursa-Laboratories/Cubware) at `352aa95`
- `agilexrobotics/piper_ros` at `ac41fcb`, for the URDF and meshes

They need `trimesh`, `manifold3d`, `pycollada`, `scipy`, `pyvista` and `matplotlib`.

## Findings

**The mock-up against the real deck.**

| | Mock-up | CubXL+ deck (Cubware `PandaDeck`) |
|---|---|---|
| Plate | 310 × 305 × 10 mm, PLA, on four 38 mm legs (top 58.6 mm up) | 480 × 490 × 10 mm, polycarbonate |
| Slots | 42 (7 × 6), 24.9 × 9.8 mm | 180 (18 × 10), 24.9 × 10.0 mm |
| Pitch | 45 mm along the slot, **35.6 mm** across | 45 mm along the slot, **25 mm** across |
| Key in slot | 0.0 mm clearance | 0.2 mm clearance |

Neither slot has a chamfer. The holder's two keys are 225 mm apart and go 10 mm deep.

**The holder and the vials.**
- **Holder:** a single row of nine pockets, 33 mm apart, with the vial seat 18 mm up.
- **Pockets:** each is four printed fingers, 17 mm tall. Their inner radius narrows from 13.76 mm
  at the seat to 12.93 mm at the top, against a 13.5 mm vial body. That is a 0.57 mm squeeze,
  the "tight fit" that holds the vial down while the electromagnet pulls the cap.
- **Printed vial:** 64.2 mm tall, a 27 mm body with a 28 mm cap from 45.5 mm up, and 46.8 g if
  printed solid. The CubOS deck files list vials as 83 mm tall, so check which is right.

**Tool windows.** CubOS turns a deck position into a gantry move by subtracting each tool's
offset. With the 2026-09-26 calibration, the capper and the pipette (offset 54.0, 13.0 mm) can
both reach:
- **Along X:** 334 mm (54–388), enough for 11 vials at 33 mm.
- **Along Y:** 220.7 mm (13–233.7), enough for only **7**.

A 9-position holder spans 264 mm, so it fits only along X.

**Reach.** These come from the URDF, with the pad centre 120 mm past the flange.
- **Straight down:** J5 stops at ±70°, so the gripper can point straight down only below about
  0.10 m above the arm's base and within about 0.34 m of J1. With 15° kept clear of every joint
  limit, it can't go above 0.05 m.
- **At 45°, 15° clear of every limit:** the pad can reach 0.23–0.65 m at 0.10 m height and
  0.13–0.64 m at 0.15 m.
- **Carrier direction:** a 45° grasp along a carrier that points at J1 works. Along a carrier
  that runs across the arm's line, IK finds no solution.

| Handoff point (grasp 117 mm above the bench) | Radius | Smallest joint margin |
|---|---|---|
| Handle post, 45° | 0.519 m | 54.6° |
| Handle post, 60° | 0.519 m | 27.4° |
| Nearest vial (slot 1), 45° | 0.387 m | 44.0° |
| Farthest vial (slot 9), 45° | 0.651 m | 19.8° |
| Single-vial pocket, 45° | 0.408 m | 50.1° |
| Handle post, straight down | 0.519 m | unreachable |
| Far deck corner (direct reach-in), 45° | 0.824 m | unreachable |

**Payload and grip.**
- **Mass:** a full carrier weighs 0.53–0.66 kg, depending on the holder's infill. That is 35–44%
  of the PiPER's 1.5 kg, or 53–66% if the 0.5 kg gripper counts against it.
- **Vertical slip:** at 40 N, the grip holds 20 N with bare fingers on glass (μ 0.25), or 56 N
  with silicone pads (μ 0.7).
- **Lopsided load:** with four full vials on one side of a centre handle, the twist on the grip
  is 0.149 N·m. Bare 20 × 20 mm pads resist 0.153 N·m, so they are right at slipping. Silicone
  pads resist 0.429 N·m.
- **End grip:** holding the carrier by one end puts 0.74 N·m on the grip. That needs pins or a
  dovetail; friction alone won't hold it.

**Placement tolerance.**
- **Arm error budget:** ±0.10 mm arm repeatability, ±0.5 mm gripper, ±0.3 mm teaching and
  registration, ±0.25 mm structure and humidity. That gives ±0.64 mm combined (RSS) and ±1.15 mm
  worst case.
- **Capture range of each feature:**
  - pill key: ±0.2 mm
  - tight pocket: ±0.6 mm
  - a 3 mm lead-in nest: ±3 mm
  - a chamfered loose pocket: ±2.5 mm

## Assumptions

- **CubXL frame:** rail, member, beam and backboard positions are placeholders scaled from the
  #133 photos, and the gantry's travel is assumed centred on the deck. Only SainSmart's overall
  641 × 755.5 × 580 mm and the configs' working volume are real. Measure the rest before
  trusting a clearance.
- **Deck height:** taken from Chris's mock-up (58.6 mm). Measure the real one.
- **Masses:** 20 g glass, 6 g cap and 20 g water per vial, and a 75 g holder at 15% infill
  (202 g solid). Weigh yours.
- **Friction:** μ 0.25 for bare PLA or aluminium on glass, 0.7 for silicone on glass.
- **Holder size:** the holder Chris attached is 33.4 × 297.4 mm, while Cubware's
  `9VialHolder.yaml` says 36.2 × 300.2 mm. The analysis uses the attached part.
