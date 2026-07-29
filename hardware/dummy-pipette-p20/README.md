# Dummy pipette for CubXL P20 dry runs

A cheap, **sacrificial** 3D-printed stand-in for the Opentrons **P20 Single-Channel GEN2**.
Mount it where the real pipette goes and run your homing / travel / clearance dry runs against
**it** instead of the ~$1k pipette. If the gantry crashes into the deck or labware, a 10-cent
printed nozzle snaps off at a designed weak point — the pipette and the gantry stay intact.

> **Parametric source:** [`dummy_pipette_p20.scad`](./dummy_pipette_p20.scad) (OpenSCAD).
> STLs are pre-rendered in [`stl/`](./stl); previews in [`img/`](./img).
> License: CC-BY-4.0 (matches the open-hardware docs in this repo).

![assembly](./img/assembly_iso.png)

## Why a dummy pipette at all

Dry runs (homing, deck traversal, tip-rack / well approaches) are exactly when a bad coordinate,
an un-calibrated tip length, or a wrong Z sends the tool into something solid. On the CubXL the
P20 is both **expensive** and **hard to re-source** (see the pipette-selection notes in
[`docs/pipette-selection-cubxl.md`](../../docs/pipette-selection-cubxl.md)), and — per
[issue #165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165) — the OT-2 pipette hardware
path on the CubXL "has not yet been validated on the physical machine." That is the highest-risk
moment to be moving the real pipette around.

This part lets you shake out the motion with a printed proxy that:

1. **Mounts on the same datum** as the real P20, so the tool origin is unchanged and every path you
   validate transfers 1:1 to the real pipette.
2. **Reproduces the collision envelope** — same body footprint and, critically, the **same lowest
   point** (installed-tip end) — so Z-clearance and side-clearance tests are truthful.
3. **Fails safe**: a deliberately weak **shear neck** just above the nozzle breaks long before the
   force reaches a level that would bend the pipette or skip the gantry steppers.

## The three design features

| Feature | What it does | Where in the SCAD |
|---|---|---|
| **Same mount interface** | Bolts to the Cubware **PAW-V2 OT2Mount / OT2Backboard** the real P20 uses | `MOUNT_STYLE`, `backplate()` |
| **Same collision envelope** | Body block + shoulder + ejector collar + nozzle + **solid modeled tip** to the real tip end | the `MEASURE ME` block |
| **Break-away nozzle** | Separate cheap part on a friction peg + thin **shear web**; snaps on impact | `SHEAR_DIA`, `SHEAR_H`, `nozzle_solid()` |

![nozzle](./img/nozzle.png)

*The sacrificial nozzle: press-peg (top) → frangible shear neck → tip cone → solid tip. Print a
handful; swap after a crash.*

## ⚠️ Measure before you trust it

The dimensions shipped in the SCAD are **ballpark estimates** for a P20 GEN2 + 20 µL tip
(they render to a **185 mm** datum→tip reach). **Put calipers on your actual pipette and overwrite
the `MEASURE ME` block before the first real dry run.** The single most safety-critical number is
the datum→tip-end reach; the model `echo`es it on every render.

Fastest safe path if you only trust one measurement: set

```scad
MATCH_TOTAL_REACH = true;
MOUNT_TO_TIP_END  = 183;   // <- your measured mount-face-to-installed-tip-end, mm
```

and the model stretches the tip so the printed part hits that exact reach even if the cosmetic
sub-dimensions are rough.

Key values to verify:

- **`MOUNT_TO_TIP_END`** — mount face (top of body / mounting datum) to the end of an installed
  20 µL tip. Most important.
- **`TIP_LENGTH`** — installed 20 µL tip length (~39 mm). This must match the `tip_length` in the
  CubOS tip-rack labware definition (`ursa_tip_rack/TipRack.yaml`) that drives Z during pipetting —
  see caveat #4 in [issue #165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165). If those
  disagree, your dry run tests the wrong reach.
- **`BODY_W` / `BODY_D` / `BODY_H`** — body block for side clearances.
- **The mount interface** — see below.

## Mounting to the CubXL (pick one)

The real P20 bolts to the Cubware **PAW-V2 "OT2Mount"**, which bolts to the **"OT2Backboard"**
(`Ursa-Laboratories/Cubware`: [`mounts/ot2_backboard`](https://github.com/Ursa-Laboratories/Cubware/tree/main/mounts/ot2_backboard)).
`MOUNT_STYLE` selects how the dummy attaches:

- **`"backboard_plate"`** (default, simplest): flat back plate with an M3 bolt grid that bolts the
  dummy **straight to the OT2Backboard**, skipping the pipette pocket. Measure your backboard's hole
  pattern and set `BOLT_DX` / `BOLT_DZ` / `BOLT_COLS` / `BOLT_ROWS`. Good enough for validating deck
  travel and Z clearance.
- **`"mount_clone"`** (truest test): a placeholder tab meant to seat in the **same OT2Mount pocket**
  the real pipette uses, so the tool sits at the identical position. The pocket isn't published
  dimensionally, so import `PAW-V2 - OT2Mount_REV. 1 - OT2Mount.stl` next to the SCAD and trim
  `MOUNT_TAB_*` until the dummy drops into the real pocket. Render `part="backplate"` to fit-check
  this **before** printing the whole thing.

## Printing

Cheap and frangible is the point — you *want* the sacrifice to be the cheap part.

| Setting | Recommendation | Why |
|---|---|---|
| Material | **PLA** (cheapest) | Brittle = predictable snap; don't use tough PETG/ABS for the nozzle |
| Nozzle infill | **10–15 %** | Keeps the shear neck weak and the part disposable |
| Body infill | 15–20 % | Rigid enough to hold the envelope, still cheap |
| Layer height | 0.2–0.28 mm | Speed over finish; this is a jig, not a showpiece |
| Supports | Body: none needed (socket prints as a blind hole facing up). Nozzle: none (print peg-up). | |

Print orientation is baked into the part selector: `part="body"` sits mount-plate-down with the
nozzle socket opening upward; `part="nozzle"` stands peg-up so the shear neck and tip print cleanly.

**Tuning the break force:** shrink `SHEAR_DIA` (default 5 mm) and/or `SHEAR_H` to make it snap
easier; a smaller neck + lower infill fails sooner. Err toward *too weak* — a nozzle that breaks a
little early costs you a reprint; one that's too strong defeats the whole purpose.

## Rendering / exporting yourself

```bash
# one STL per part
for p in assembly body nozzle backplate; do
  openscad -o stl/dummy_pipette_p20_$p.stl -D "part=\"$p\"" dummy_pipette_p20.scad
done
# a preview PNG (headless CI needs xvfb)
xvfb-run -a openscad -o img/assembly_iso.png --imgsize=900,1100 \
  --camera=0,0,-90,62,0,25,520 -D 'part="assembly"' dummy_pipette_p20.scad
```

`part` options: `assembly` (body + nozzle, preview / print-in-one), `body` (print this — has the
nozzle socket), `nozzle` (print several — the sacrificial part), `backplate` (fit-check the mount
only).

## Suggested dry-run procedure

1. Print `body` + a few `nozzle`s in PLA. Bolt the body to the CubXL via your chosen `MOUNT_STYLE`.
2. Confirm the dummy's tip end sits at the **same Z** as a real P20 + tip would (measure down from
   the mount datum; compare to `MOUNT_TO_TIP_END`).
3. Run homing, then jog to each deck / tip-rack / labware position at **reduced feedrate** and watch
   clearances. If anything contacts, the nozzle snaps — swap it, fix the coordinate, repeat.
4. Only once the paths are clean with the dummy, swap in the real P20 and re-verify at reduced speed.

## Provenance & related work

- Mount interface & wiring context: [issue #165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165)
  (Cubware `mounts/ot2_backboard`, PAW-V2 OT2Mount).
- Pipette selection / sourcing rationale: [`docs/pipette-selection-cubxl.md`](../../docs/pipette-selection-cubxl.md).
- Tip length must match the CubOS `ursa_tip_rack` labware `tip_length`.
