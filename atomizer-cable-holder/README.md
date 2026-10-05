# Atomizer transducer cable holder

A two-clip cable holder for the atomizer's transducer cables, designed by @ronnie-guymon in
Onshape ([document](https://byudesign.onshape.com/documents/3094e1d7fbb4c4351dcd0e1a/w/d3134413115bb70af771d24a/e/ef669eb623cfc76bb11527a4),
*Atomizer holder*, Part Studio 1). It was printed on request in
[#256](https://github.com/vertical-cloud-lab/byu-vcl/issues/256).

| File | What |
|---|---|
| [`atomizer_holder.stl`](atomizer_holder.stl) | The part as designed, in millimetres and in Onshape's coordinates |
| [`atomizer_holder_A1mini_blackPLA.gcode.3mf`](atomizer_holder_A1mini_blackPLA.gcode.3mf) | The sliced plate, for the A1 mini in Bambu PLA Basic, black |
| [`evidence/2026-10-05/`](evidence/2026-10-05/) | Pre-flight, camera frame, part render and slice preview |

## The part

- **Base:** a 50 × 10 mm bar, 15 mm deep.
- **Two C-clips** hang under it:
  - **Ø11 mm** bore with a 1.6 mm wall, 10 mm deep;
  - **Ø7 mm** bore with a 1 mm wall, 5 mm deep.
- **Each clip** has a 3.2 mm gap with a flared lead-in.
- **Fillets:** 1 mm and 0.7 mm.
- **Overall:** 50 × 15 × 26.6 mm, 8.2 cm³. The mesh is one watertight solid.

## Getting it out of Onshape

The document is in BYU's `byudesign` enterprise. The lab's Onshape API key belongs to
Sterling's personal EDU account, which has no company attached. What each request returned:

| Request | Before sharing | Link share, view only | Link share with export |
|---|---|---|---|
| Document metadata, feature list | 403 | 200 | 200 |
| `parts`, `stl`, `tessellatedfaces`, mass properties, anonymous or keyed at `byudesign` | 403 | 401 "Unauthenticated API request" | 401 |
| `stl`, keyed at `cad.onshape.com` | 403 | 403 | 400 "Element must be a part studio" |
| `gltf`, keyed at `cad.onshape.com` | 403 | — | **200** |

- **The working route:** turn on export for the link, then ask for **glTF** with the key at
  `cad.onshape.com`. Then convert the mesh to STL in millimetres with trimesh.
- **The glTF is in Onshape's Z-up world coordinates and in metres.**
- **Why this is simpler next time:** ask for an STL to be exported and attached, or have the
  document shared with export allowed.

## Print settings (2026-10-05)

- **Printer and material:** A1 mini, 0.4 mm nozzle, Textured PEI Plate. Bambu PLA Basic,
  black (AMS slot A3).
- **Process:** `0.20mm Standard @BBL A1M`, with one change: supports on, `normal(auto)`,
  30°, on build plate only.
- **Orientation:** on its side, so the clip profiles lie in the layer plane.
  - The C-clips have to open from 3.2 mm to the cable's diameter. Printed this way, they
    flex along their extruded perimeters rather than across layer lines.
  - The clips are narrower than the bar and centred on it. So on its side, the Ø11 clip
    starts 2.5 mm above the bed and the Ø7 clip 5 mm above it, and both stand on supports.
- **Slice:** 88 layers to 15.0 mm, 5.06 g (0.48 g of it support). Bambu's estimate is
  18 min 51 s.
