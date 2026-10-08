# Atomizer Holder V3

The third version of @ronnie-guymon's holder for the atomizer transducer's lines: a slotted
box instead of snap clips, to be held to the cabinet by a magnet (see
[`../rebuild/magnet/`](../rebuild/magnet/README.md)). Designed in Onshape
([*Atomizer holder*, element *Atomizer Holder V3*](https://byudesign.onshape.com/documents/3094e1d7fbb4c4351dcd0e1a/w/d3134413115bb70af771d24a/e/c785cc2846c2740d77a7bd91)).
One was printed in black PLA on the lab's A1 mini on 2026-10-06, at the request on
[PR #257](https://github.com/vertical-cloud-lab/byu-vcl/pull/257#issuecomment-6025049559).

![The part as it stood on the bed](evidence/2026-10-06/part_views.png)

| File | What |
|---|---|
| [`atomizer_holder_v3.stl`](atomizer_holder_v3.stl) | The part as designed, in millimetres and Onshape's coordinates |
| [`atomizer_holder_v3_A1mini_blackPLA.gcode.3mf`](atomizer_holder_v3_A1mini_blackPLA.gcode.3mf) | The sliced plate that was sent. Its plate G-code is byte-identical to Studio's own slice. The lab account's `DesignerUserId` is blanked |
| [`onshape/features.json`](onshape/features.json) | The element's feature list (4 sketches, 4 extrudes, 1 plane), as fetched at 20:44 UTC |
| [`evidence/2026-10-06/print.json`](evidence/2026-10-06/print.json) | Source, settings, Send options, estimates, timeline and who gave the go |
| [`evidence/2026-10-06/`](evidence/2026-10-06/) | Both pre-flights with their camera frames, `watch`'s log (`watch.jsonl.gz`) and key frames |
| [`off_the_shelf/`](off_the_shelf/README.md) | What Amazon sells that is like this holder, searched 2026-10-08 |

## The part

In Onshape's coordinates, as designed:

| | |
|---|---|
| Back plate | 50 × 70 mm, 20 mm thick. Its flat back is the face for the magnet |
| Hook | Along one 50 mm end: a 9 mm floor that runs 45 mm out from the back of the plate, ending in a 5 mm wall that stands 25 mm tall. Between the plate and that wall is a 20 mm wide channel |
| Slots | Two, 12.5 mm either side of the middle, cut through the floor and the end wall. 6.5 mm wide with a Ø6.5 mm round end, and 5.5 mm wide with a Ø5.5 mm round end. Both run about 17 mm in from the outside of the end wall, so the round ends sit 11 mm in front of the plate. The end wall is split into three fingers |
| Overall | 50 × 70 × 45 mm, 82.5 cm³, one watertight solid |

- **The 6.5 mm slot leaves 0.5 mm around the 6 mm air hose,** the clearance suggested in
  [`../rebuild/magnet/README.md`](../rebuild/magnet/README.md#the-box), so nothing has to
  flex. The 5.5 mm slot does the same for a 5 mm line.
- **Printed slots can come out 0.1–0.2 mm narrow.** Check the fit with the real hose and
  cable before relying on it.

## Getting it out of Onshape

The same route as the first version ([`../README.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/ac80509/atomizer-cable-holder/README.md#getting-it-out-of-onshape)
on `claude/issue-256-20261005-1618`). The document's link share still allows export:

| Request, with the lab's API key at `cad.onshape.com` | Status |
|---|---|
| Document, element list, feature list | 200 |
| Part Studio glTF | **200** |
| `parts`, mass properties | 403 |

The glTF is in metres, in Onshape's Z-up frame. It was converted to an STL in millimetres
with trimesh (`merge_vertices`, then a watertightness check).

## Print settings

- **Printer and material:** A1 mini, 0.4 mm nozzle, Textured PEI Plate. Bambu PLA Basic,
  black (AMS slot A3).
- **Process:** `0.20mm Standard @BBL A1M` with **no changes**: 2 walls, 15 % grid infill,
  5 top and 3 bottom layers, supports off.
- **Orientation:** stood on the bottom of the hook, which is also how the part is used.
  - Every layer lies within the one below it, so nothing overhangs and no supports are
    needed. In the STL's own orientation, the end wall would overhang the channel by 16 mm,
    and on its side the slot roofs would overhang.
  - The slots and their round ends lie in the layer plane, so their widths are set by the
    walls' paths rather than by stacked layers.
  - The magnet face is a side wall. It is as flat as the printer's walls, not as smooth as
    the plate.
  - Footprint 50 × 45 mm, 70 mm tall. The top 45 mm is the back plate alone, 50 × 20 mm in
    section.
- **Slice:** 350 layers to 70.0 mm, 29.71 g (9.80 m). Bambu's estimate was 1 h 1 min 33 s,
  of which about 4 min is timelapse moves that don't run with timelapse off.

## How it went (2026-10-06, UTC)

| | |
|---|---|
| Route | Bambu Studio's GUI on the runner, logged in to the lab's Bambu account (route 3 of the Bambu runbook in [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)). The printer was reached for pre-flight and `watch` through `RPI_STREAM_CAM`: the CubXL Pi, the runbook's default, was offline on the tailnet |
| The go | @ronnie-guymon in the request (20:40): "plate is clear". The first pre-flight (20:51) showed the red bin back at the bed's far-right corner, as on 2026-10-05, and he was asked to move it out of the bed's path. Then, with the login code (20:52:44): "box is moved, plate is clear". The 20:55:50 frame shows the bin at the far-left corner instead |
| Login | The code was typed 6 s after it was posted and worked the first time |
| Send | 20:57:45, `PREPARE` by 20:58:00, `RUNNING` by 20:58:12 |
| Layer 1 | 21:04:51, after Bambu's start sequence |
| `FINISH` | FINISH_PLACEHOLDER |

FRAMES_PLACEHOLDER
