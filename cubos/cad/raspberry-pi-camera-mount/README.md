# Raspberry Pi camera mount, as STEP

`RaspberryPiCameraMount.step` is a STEP version of Ursa Laboratories'
[`RaspberryPiCameraMount.stl`](https://github.com/Ursa-Laboratories/Cubware/blob/8f0f0ed/cubxl_plus/instrument_mounts/raspberry_pi_mount/RaspberryPiCameraMount.stl)
from Cubware (commit `8f0f0ed`), made so the part can be edited in Onshape
([#165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165)). Cubware's folder for this
part has only the STL, a PNG and a README.

![The part from two sides, every face outlined: flat faces blue, cylinders gray, tori orange, spheres green](preview.png)

## What is in the file

One closed solid of 156 faces, each a true flat or curved surface:

| Faces | Surface | Where |
| --- | --- | --- |
| 75 | flat | the flat faces, including the hex nut pockets |
| 41 | cylinder, r = 2 mm | the 2 mm fillets, and the curved channels |
| 13 | cylinder, r = 0.75 mm | the fillets on the legs underneath |
| 2 | cylinder, r = 0.25 mm | the small fillets under the base |
| 4 | cylinder, r = 1.15 mm | the four Ø2.3 mm screw holes |
| 4 | cylinder, r = 2.4 mm | the four Ø4.8 mm bosses |
| 1 | cylinder, r = 1.999 mm | a short piece of 2 mm fillet (see below) |
| 6 | torus, 4 mm bend radius, 2 mm tube | where the 2 mm fillets bend round a corner |
| 10 | sphere, r = 2 mm | the corners where three 2 mm fillets meet |

Most edges are exact straight lines (247) or circles and arcs (116). The 44 others are smooth
spline curves, where two curved surfaces cross along a curve that isn't a circle, such as a
boss running into a fillet.

It is the same shape as the STL: 28.8 × 31.04 × 34.0 mm, 8,761.1 mm³. That is 0.24 mm³ more
than the STL, because the STL cut each curved surface into flat facets slightly inside it.

## Importing it into Onshape

Import `RaspberryPiCameraMount.step` into an Onshape document with the **+** button at the
bottom left → **Import**. The units are millimetres.

## Editing it

- Fillets, holes and bosses are single faces now, so Onshape's direct-editing tools work on
  them: **Modify fillet** to change a fillet's radius or remove it, **Move face** or
  **Offset face** to move or resize a hole or boss, **Delete face** to remove a feature and
  heal the gap.
- Flat faces work like any Onshape face: sketch on them, extrude from them, move them.
- It is still an imported solid with no feature history, so its sizes are changed by editing
  faces, not by editing dimensions in a sketch.

## How it was made

The STL came from a CAD export, which places every STL vertex exactly on the original CAD
surfaces; only the flat facets between vertices cut corners. So each original surface can be
recovered exactly from the vertices, with no remodelling:

1. [`tools/segment.py`](tools/segment.py) sorts the triangles into faces. Triangles that lie in
   one plane and span more than 0.2 mm form the 71 large flat faces (the facets of the curved
   surfaces are all under 0.11 mm wide). The rest are grown into regions that each fit one
   plane, cylinder, sphere or torus. A region is accepted only if every one of its vertices
   lies within 0.00002 mm of the fitted surface and every facet faces the same way as the
   surface, within 8°. Every triangle ended up in a region, and no vertex is further than
   0.0000174 mm from its region's surface.
   [`tools/fit.py`](tools/fit.py) has the fitting code.
2. [`tools/build.py`](tools/build.py) builds one face per region on its fitted surface. The
   boundary between two neighbouring regions becomes one edge: a straight line or a circle
   when its STL vertices lie on one (to within 0.00002 mm), otherwise a smooth spline through
   those vertices. Corners are at the STL's own vertices. OpenCascade's `ShapeFix` then adds
   the seam lines that closed cylinders need and the 2D copies of edges on curved faces.

It needs OpenCascade 8.0 from the `cadquery-ocp` Python package, and takes about 2 minutes,
nearly all of it in the region growing:

```bash
pip install cadquery-ocp numpy scipy trimesh rtree matplotlib
python tools/segment.py RaspberryPiCameraMount.stl seg.pkl
python tools/build.py seg.pkl RaspberryPiCameraMount.step RaspberryPiCameraMount
python tools/check.py RaspberryPiCameraMount.step RaspberryPiCameraMount.stl preview.png
```

[`tools/stl_to_step.py`](tools/stl_to_step.py) is the earlier, fully faceted converter. The
new tools reuse its STL reader and plane grouping.

## Checks

[`check.txt`](check.txt) is the output of [`tools/check.py`](tools/check.py), which reads the
STEP back and compares it with the STL.

| | STL | STEP read back |
| --- | --- | --- |
| Shape | One closed mesh | One valid solid (OpenCascade's `BRepCheck`): 156 faces, 407 edges, 248 vertices |
| Volume | 8,760.891 mm³ | 8,761.134 mm³ |
| Surface area | 4,768.681 mm² | 4,768.797 mm² |
| Bounding box | x −14.4 to 14.4, y −7.27 to 23.77, z −10 to 24 mm | identical |
| STL vertices to the STEP surface | | at most 0.0006 mm |
| STEP surface to the STL's facets | | at most 0.0010 mm, 0.0003 mm on average |

The last two rows compare a 0.0005 mm tessellation of the STEP with the STL, so they include
up to 0.0005 mm of tessellation error. The largest gap, 0.001 mm, is where a curved surface
bulges out from between the STL's facets.

## Known imperfections

- One short piece of 2 mm fillet came out as r = 1.999 mm, because it has only 13 triangles
  to fit to. It is off by under 0.001 mm.
- Four tiny flat faces (under 0.05 mm across) sit where two fillets meet a boss. They are
  pieces of the face the bosses stand on, cut off by the fillets, and the STL has them too.

## License

Cubware has no license file, so this conversion carries whatever terms Ursa Laboratories sets
for the original. Check with them before using it outside the lab. Until Cubware commit
`2a8d621` the STL was called `PAW-V2 - Raspberry Pi Camera Module 3 Mount_REV. 0 Copy 1 - Part 1.stl`,
so it may derive from the PAW-V2 design, whose files in this repo are GPL-2.0.
