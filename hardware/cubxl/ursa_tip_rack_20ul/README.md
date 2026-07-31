# Cub-XL tip rack — 20 µL variant (Ø5.0 mm bores)

![Tip rack comparison](TipRack20uL.png)

A re-bored version of the Ursa 2 × 15 tip rack for the PANDA-BEAR / Cub-XL deck.
The stock part holds 300 µL tips; this one has straight **Ø5.000 mm** bores sized
for 20 µL tips, per [#151](https://github.com/vertical-cloud-lab/byu-vcl/issues/151).

Everything except the bores is untouched — same envelope, same 8.5 mm grid, same
side walls, end gussets, bottom rail and deck key pockets — so it drops onto the
Cub-XL deck exactly where the stock rack does.

## Files

| File | Purpose |
| --- | --- |
| `TipRack20uL.3mf` | **Print this.** Already in the recommended print orientation (bores up), positive octant, 21 × 138 × 66 mm, units = millimetre. |
| `TipRack20uL.stl` | Same solid in the *stock* `TipRack.stl` coordinate frame (21 × 66 × 138, +y up), so it is a drop-in geometric replacement anywhere CubOS/Cubware reference the original mesh. |
| `TipRack20uL.yaml` | CubOS labware config. Grid geometry is final; **`pickup_z` / `drop_z` are placeholders and must be measured** — see below. |
| `make_tip_rack_20ul.py` | Parametric generator. Re-run with `--diameter` for any other bore size. |
| `TipRack20uL.png` | Preview above — stock vs. new, isometric and top-down. |
| `TipRack.stl` | Vendored upstream source, sha256 `4a7e64a9…`, from [`Ursa-Laboratories/Cubware`](https://github.com/Ursa-Laboratories/Cubware/blob/main/labware/ursa_tip_rack/TipRack.stl). |

## What changed

The stock bores are a 300 µL tip seat: a **Ø6.980 → Ø6.424 taper over 16 mm**
(≈1.0° half-angle) followed by a **Ø4.32 through-bore** for the last 2 mm of the
18 mm plate. A 20 µL tip drops straight through that.

Each of the 30 bores is now a **straight Ø5.000 mm hole through the full 18 mm
plate**. A straight bore is deliberate: the tip cone contacts the rim at the top
face, so every tip seats at the same height and stays square, with no dependence
on how well the printed taper matches a particular tip brand.

Unchanged: 21 × 66 × 138 mm envelope · 2 columns at x = 6.25 / 14.75 · 15 rows at
z = −5 → −124 · 8.5 mm pitch both ways · 18 mm top plate · 2 mm side walls · 5 mm
bottom rail · 17 × 43 mm cavity · two 2 mm-deep triangular deck key pockets,
7.4 × 6.7 mm, centres 90.00 mm apart.

## Verification

Checks run by `make_tip_rack_20ul.py` and after export:

- Result is **watertight**, consistently wound, **genus 31** — a clean solid with exactly 30 through-bores.
- All 30 bores measure **5.0000 mm across flats** at every depth from the top face to the plate underside.
- Volume 79 654.8 mm³ (79.65 cm³), within 3.7 mm³ of the analytic prediction (facet discretisation).
- **Symmetric difference against the stock part below the tip plate = 0.000000 mm³** — the deck keys, walls, gussets and bottom rail are bit-for-bit identical.
- No material outside the 21 × 66 × 138 mm envelope.
- `.3mf` round-trips through `trimesh` watertight, `unit="millimeter"`, single build item.

## Printing

Print as oriented in the `.3mf`: bottom rail on the bed, bores facing up. The
bores then print vertically (round, no support) and their seating rims print
last, clear of first-layer elephant's foot. The only overhang is the plate
underside bridging the 17 mm cavity — routine for any modern printer.

- PLA or PETG, 0.2 mm layers, 3 perimeters, ~20 % infill. No supports.
- **Check the bore fit before printing all 30.** Most FDM printers come out
  0.1–0.2 mm undersize on vertical holes. If your 20 µL tips bind, regenerate:

  ```bash
  pip install trimesh manifold3d numpy lxml
  python make_tip_rack_20ul.py --diameter 5.2
  ```

## Calibration — do this before running a protocol

`TipRack20uL.yaml` carries the correct grid, but the **tip seats higher than in
the stock 300 µL rack** (the tip now rests on the top face rather than partway
down a 16 mm taper). `pickup_z` and `drop_z` are therefore carried over from
upstream only as starting points and **will be wrong for these tips**. Measure
them against the actual tips and pipette before running any hardware protocol,
and set `tip_length` to the physical tips in use — CubOS relies on it for
collision safety.
