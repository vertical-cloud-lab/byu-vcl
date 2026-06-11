# P20 Fake-Tip CAD — Test Array, Deck Plate, and Mock Sensor Package

Parametric [build123d](https://build123d.readthedocs.io/) models implementing the
test-array strategy from [`../p20-fake-tip-design.md`](../p20-fake-tip-design.md).
Requested in [issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33)
/ [PR #114](https://github.com/vertical-cloud-lab/byu-vcl/pull/114); workflow
conventions follow
[vertical-cloud-lab/powder-doser](https://github.com/vertical-cloud-lab/powder-doser)
(`cad_model.py` + `Params` dataclass, per-part STL/STEP exports, `renders/`).

## Provenance: measured from the original P300 part

The original Acceleration Consortium
[`Sensor package main enclosure.step`](https://github.com/AccelerationConsortium/wireless-color-sensor/blob/main/CAD-File/STEP/Sensor%20package%20main%20enclosure.step)
(P300 version) was imported and measured with build123d/OpenCascade:

| Feature | Measured value |
|---|---|
| Fake-tip post | Ø9.5 mm × 13 mm (R2 fillet into top face) |
| Bore | entry Ø≈5.15 mm → Ø≈4.19 mm over 14.5 mm depth |
| Bore taper half-angle | **1.78°** (conical surface in the STEP) |
| Overall part height | 84 mm (matches the team's labware `tipLength: 84`) |
| Body footprint | 40 × 60 mm |

The 1.78° half-angle is the empirical GEN2 nozzle taper from the working P300
design and is reused for the P20 socket bores here (the design doc's "~2–3°"
estimate, refined).

## Parts

| File | What it is |
|---|---|
| `stl/fake_tip_test_array.stl` | 10 round-1 test tips, bore ID 3.40–3.85 mm in 0.05 mm steps (straight bore, no slits). Each tip: body Ø8 × 10, flange Ø10 × 2, socket Ø6 × 8 mm; the 2-digit size code (e.g. `55` = 3.55 mm) is engraved on the underside. Laid out in the same 2 × 5 / 18 mm-pitch grid as the deck-plate pockets. |
| `stl/deck_plate_base.stl` | ANSI/SLAS-footprint (127.76 × 85.48 × 24 mm) plate that sits in an OT-2 deck slot. 10 drop-in pockets register the test tips without locking them down; bore sizes, a title, and an `A1` corner marker are engraved on top. Underside is hollowed (3 mm shell + columns under each pocket). |
| `stl/fake_tip_insert.stl` | Final-geometry modular insert per the design-doc table: peg Ø6 × 5 + flange Ø8 × 2 + socket Ø6 × 8 with **tapered bore (1.78°)** and **3 spring-finger slits** (0.5 mm wide, 6 mm deep, rounded roots). |
| `stl/mock_sensor_package.stl` | Drop-in stand-in for the wireless color sensor: original 40 × 60 mm footprint and **84 mm overall height**, topped with the P20 socket (tapered bore + spring fingers at the nominal 3.55 mm mid-bore). Because the envelope matches the original P300 part, the existing `byu_color_sensor_charging_port` labware definition (`tipLength: 84`) from PR #116 works unchanged. |

STEP equivalents are in `step/`; PNG renders (iso/front/top per part) in `renders/`.

### Renders

| | iso | top |
|---|---|---|
| Test array | ![array iso](renders/fake_tip_test_array_iso.png) | ![array top](renders/fake_tip_test_array_top.png) |
| Deck plate | ![plate iso](renders/deck_plate_base_iso.png) | ![plate top](renders/deck_plate_base_top.png) |
| Insert | ![insert iso](renders/fake_tip_insert_iso.png) | ![insert top](renders/fake_tip_insert_top.png) |
| Mock package | ![mock iso](renders/mock_sensor_package_iso.png) | ![mock front](renders/mock_sensor_package_front.png) |

## Printing (Bambu Lab A1 mini, 180 × 180 × 180 mm)

All parts fit the A1 mini bed (the deck plate is 127.8 × 85.5 mm).

- **Material:** PETG, black (per design doc; PLA acceptable for the round-1 array).
- **Test array & insert:** as oriented (sockets up), 0.12–0.16 mm layers,
  100 % infill, no supports, enable hole/X-Y contour compensation in Bambu
  Studio. Print the whole array in one batch so all bores share identical
  printer error.
- **Deck plate:** as oriented, 0.20 mm layers, 15 % infill, no supports
  (the hollow underside prints as bridges over the 3 mm shell; enable
  "bridge" defaults).
- **Mock package:** as oriented, 0.20 mm layers, **~8 % gyroid infill** so
  the printed mass lands near the real sensor package (~40–50 g) — solid
  PETG would be ~200 g and over-test retention.

## OT-2 testing

`protocol_test_array.py` is a self-contained OT-2 protocol (API 2.12, same
upload path as the working scripts in
[PR #116 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/116#issuecomment-4665074566)):

1. Put the deck plate in **slot 8**, engraved `A1` marker at the **back-left**.
2. Drop the 10 test tips into their pockets (sizes engraved next to each pocket).
3. Run the protocol: for each pocket it picks the tip up, lifts, pauses for a
   retention check, then ejects it back over its pocket and pauses for a
   drop-off check. Record pass/fail per the evaluation criteria in the design doc.

The mock sensor package needs no new script — it is a drop-in replacement for
the real sensor in the existing PR #116 pick-and-place protocols.

### Why the current 7.5 mm adapter can't eject (Opentrons mechanics)

Per the [Opentrons GEN2 pipette white paper](https://opentrons-landing-img.s3.amazonaws.com/pipettes/Opentrons-Master-Pipette-White-Paper.pdf)
and support docs, GEN2 tips seat on the **nozzle proper** (P20: ~3.6–3.8 mm OD)
and the **ejector sleeve** surrounding the nozzle pushes the tip collar off.
A 7.5 mm bore grips the sleeve itself, so the ejector has nothing to push
against — matching the observed "picks up fine, won't eject" failure
([PR #116](https://github.com/vertical-cloud-lab/byu-vcl/pull/116)). The test
array's 3.40–3.85 mm bores engage the nozzle below the sleeve, and the Ø6 mm
socket rim gives the sleeve a proper shoulder to push on.

Two Opentrons details encoded in the labware/protocol:

- During `pick_up_tip` the nozzle presses ~`tipLength + 4.5 mm` below the
  well top, so the plate is 24 mm tall (tip seat at z = 11.8 mm) to keep the
  press above the deck (verified with `opentrons.simulate`).
- `tipOverlap: 8.0` mirrors the stock 20 µL tip overlap (8.25 mm) so motion
  planning assumes a realistic nozzle engagement depth.

## Regenerating

```bash
pip install build123d trimesh matplotlib shapely networkx opentrons
python cad_model.py        # exports stl/ + step/
python render_views.py     # renders renders/*.png
python -m opentrons.simulate protocol_test_array.py   # sanity-check protocol
```

Edit the `Params` dataclass in `cad_model.py` to iterate (e.g. set
`bore_ids` to the round-2 ±0.02 mm sweep once a round-1 winner is found).
