# Floor space: three labs, the same equipment (video segment)

Sterling, on PR 400 (2026-11-27): a video segment that compares three labs on floor space: a conventional lab, an
automated "flat" lab on the same floor plan, and the vertical lab, as one continuous animation from a whole-lab view,
with each layout's area computed from its footprints, clearances and aisles, Emerald Cloud Lab as a reference point,
and instruments per square foot as well as total area. A standalone preview, uploaded private for review, written as
reusable modules in `twin/video/` so round 5's re-cut can drop it in next to the lab comparison.

**Everything here is a design layout, not a built lab.** The equipment is the 3-D lab's (PR 318's scene). The three
floor plans, their rules and their areas are ours.

**Preview:** [RUXoZQPodyU](https://www.youtube.com/watch?v=RUXoZQPodyU), **private**, for review (1:58, uploaded
2026-11-27 from commit 0902898; `out/youtube.json`, key `floorspace/floorspace_preview.mp4`). The record is
[`out/floorspace/floorspace_preview.json`](../out/floorspace/floorspace_preview.json) and the contact sheet
[`out/floorspace/sheet.png`](../out/floorspace/sheet.png).

![Contact sheet of the floor-space preview](../out/floorspace/sheet.png)

## The result

| Layout | Length × width | Area | Instruments per 1,000 sq ft | sq ft per instrument |
|---|---|---|---|---|
| Conventional lab | 28.9 × 13.8 m | 398 m² (4,280 sq ft) | 10.0 | 100 |
| Automated, same floor plan | 28.9 × 13.8 m | 398 m² (4,280 sq ft) | 10.0 | 100 |
| Vertical lab | 23.8 × 11.8 m | 281 m² (3,029 sq ft) | 14.2 | 70 |

- **The vertical lab needs 29 % less floor** than the conventional lab for the same 43 instruments.
- **The saving is the benches and their aisles.** The two Shuttles take every benchtop instrument on its tray in 18 m²
  of floor. The 12 floor machines don't fit on trays: they, their service clearance and the 3.0 m MiR aisle are most of
  what is left (181 of 281 m²).
- **It needs a high bay.** The Shuttles are 9.15 m tall. The conventional lab's tallest machine is the Meltio cell,
  3.16 m.
- **Automating the conventional plan changes nothing on the floor**, by construction (Sterling asked for the same plan).
  It does make the aisles tight: a MiR250 (580 mm wide) docked in a 5 ft aisle leaves 0.94 m, and the spec sheet asks
  for 1.45 m for one to drive by, so robots wait for each other there.
- **Without the two scale-up printers** (the EOS M 400-4 and the Meltio cell, both large and in all three labs): 3,692 sq
  ft against 2,439, 34 % less (`layouts.json`, `without_scaleup`).

Where the floor goes (m², rasterized at 25 mm; `floorspace.breakdown`):

| | Floor machines | Benches, shelves, Shuttles | Service clearance | Aisles and corridor | Walls | Other floor |
|---|---|---|---|---|---|---|
| Conventional | 47 | 28 | 66 | 121 | 25 | 111 |
| Automated, same plan | 48 | 28 | 66 | 120 | 25 | 111 |
| Vertical | 48 | 18 | 62 | 71 | 12 | 72 |

"Other floor" is room the rules leave over: in the conventional lab, mostly where a room is deeper than its rows need
because rooms along one side of the corridor share one depth (the metal AM bay's sets it, at 7.4 m).

## The equipment

`twin/video/floorspace.py` takes one list for all three layouts. 43 instruments:

- **31 benchtop instruments** (on the Shuttles' trays in the 3-D lab, measured there by `setup_lab.py fit`,
  `out/tray_plan.json`): SEM (Hitachi TM4000Plus II), XRD (Rigaku MiniFlex), the powder prep station, Opentrons OT-2,
  the corrosion cell (CubXL + EZstat), the multi-doser, the vacuum press (Specac), PIP (Plastometrex), the nanoindenter
  (KLA iMicro), particle size (Mastersizer), Bambu Lab H2D and A1 mini, the polisher (LECO PX500), the furnace
  (Nabertherm), the mounting press (LECO MX400), the N₂ glovebox, the digital microscope (Keyence VHX), tensile
  (zwickiLine), hardness (Mitutoyo HM-220), XRF (Bruker S2 PUMA), the ductless hood, the CNC (Makera Carvera), the
  stencil printer, the pick-and-place (LumenPnP), the reflow oven, two Formlabs Form 4s, Form Wash, Form Cure and two
  SnowPods.
- **12 floor machines** (measured from the built scene, `out/twin2/video/birdseye/high.json`): the atomizer (AMAZEMET
  rePowder), the sieving cell, the argon glovebox, LPBF (Aconity MIDI), DED (MX-Lab), the EOS M 400-4, the Meltio cell,
  the wire EDM, the two Instrons (68FM-100 and 68SC-2), the fume hood and the packaging station.
- Not counted as instruments, but laid out and moved like them: the vial rack, the disc magazine, the quench tank, the
  two sample stores and the four racks of powder jars (on storage shelving in the conventional lab).

## The three layouts

**Conventional lab** (`floorspace.conventional`): ten zones along a 6 ft corridor, grouped by workflow. Each zone has a
back row against its far wall and, where it needs one, a front row against the corridor wall, with a 5 ft aisle between
them, and an entry at its west end (a door, or a gap in the front row).

| Zone | Enclosed | W × D (m) | What stands in it |
|---|---|---|---|
| Powder and melt room | yes | 10.0 × 7.4 | atomizer, sieving cell, argon glovebox; doser, press, SnowPods and the N₂ glovebox on benches; the powder jars on shelving |
| Metal AM bay | yes | 10.6 × 7.4 | EOS M 400-4, Meltio cell, Aconity MIDI, DED |
| Machine shop | yes | 3.9 × 7.4 | wire EDM; CNC and ductless hood on a bench |
| Furnace room | yes | 3.6 × 7.4 | the furnace and the quench tank on a bench |
| Mechanical testing | no | 6.3 × 3.9 | both Instrons; zwickiLine, hardness tester, PIP and nanoindenter on benches |
| SEM room | yes | 3.4 × 3.9 | SEM and digital microscope on a bench |
| Analytical and sample prep | no | 3.7 × 3.9 | XRD, XRF, particle size, powder prep; polisher, mounting press, disc magazine |
| Wet lab | no | 4.9 × 3.9 | fume hood; OT-2 and the corrosion cell |
| Fabrication | no | 4.3 × 3.9 | the polymer printers and the PCB line |
| Shipping and storage | no | 5.4 × 3.9 | packaging station; the sample stores on shelving |

**Automated, same floor plan** (`floorspace.flat`): nothing moves and the walls stay. Added: 4 MiR250 + UR12e mobile
manipulators (our choice: twice the vertical lab's two, for the longer routes), 24 docking targets (one per floor machine
and one per bench), 5 fixed UR arms on pedestals with sample racks (beside each bench whose row has 600 mm free at its
end), and 2 chargers in the last room on the south side.

**Vertical lab** (`floorspace.vertical`): the two Shuttles where the 3-D lab has them; the glovebox, the atomizer, the
sieving cell and the Aconity MIDI in the north row with them; the two Instrons, three chargers, the fume hood, the DED,
the wire EDM and the packaging station in the south row; the 3.0 m MiR aisle between; the EOS M 400-4 and the Meltio
cell (no MiR dock) at the aisle's east end. Each row is packed from the Shuttles outward by the same clearance rule.

## The rules

The same in every layout. An area is the outer rectangle of the layout's walls, so it counts the walls, the corridor,
every aisle and every clearance.

- **Benches** 30 in (762 mm) deep, 36 in (914 mm) where an instrument is deeper than 712 mm. **Aisles** 5 ft (1524 mm)
  between rows. NIH Office of Research Facilities, "Lab Module Design Considerations", Technical Bulletin issue 23,
  December 2013: "a 5'-6" center aisle with 30" deep lab benches on both sides, and a 5' aisle with equipment up to 36"
  deep on one side"; "5' is the minimum ADA turning radius"
  (https://orf.od.nih.gov/TechnicalResources/Documents/Technical%20Bulletins/13TB/Lab%20Module%20Design%20Considerations%20December%202013%20Bulletin_508.pdf).
- **No room narrower than one 11 ft (3.35 m) module**, the same bulletin's "ideal module width". It sets the SEM room and
  the furnace room, which would otherwise be 2.1 and 1.5 m wide.
- **The MiR aisle** is the 3-D lab's: 3.0 m, two MiR250s pass; one alone needs 1.45 m (MiR250 specification sheet,
  2023-06-28, as `warehouse.py` cites it).
- **Our choices:** 150 mm between instruments on a bench and at its ends; bench runs in whole feet; 600 mm of service
  clearance beside and behind every floor machine; a 6 ft corridor (the building code's minimum is 44 in); 150 mm walls;
  4 ft doors.
- **Not in any layout:** offices, write-up desks, restrooms, gas cylinder storage, a loading dock, mechanical rooms.
  They would add the same to each, or more to the conventional lab, which has people working in it.

## Emerald Cloud Lab, as published

- **South San Francisco:** "the 1,400 square metre (15,000 square feet) lab", where "more than 100 items of high-end
  bioscience equipment whirr away on workbenches" (The Guardian, Tom Ireland, 11 September 2022, "Cloud labs and remote
  research aren't the future of science - they're here"; reprinted by Carnegie Mellon:
  https://www.cmu.edu/ambassadors/december-2022/pdf/guardian_cloud-labs.pdf). That is more than 6.7 instruments per 1,000
  sq ft, against 10.0 for the conventional layout here and 14.2 for the vertical one. A built facility's whole lab area
  counts things these layouts leave out, and its instruments are life-science ones on benches, loaded by staff: a scale
  reference, not like for like.
- **Carnegie Mellon's cloud lab,** built and run with Emerald: "the new 1,500 square metre (16,000 square feet) site"
  (the same article).
- **Austin:** "The 105,000-square-foot facility will house over 230 unique types of instruments" (Emerald Cloud Lab
  press release, PR Newswire, 28 February 2023,
  https://www.prnewswire.com/news-releases/emerald-cloud-lab-to-relocate-state-of-the-art-facility-from-south-san-francisco-to-austin-301758704.html).
  That counts types, not instruments, so it gives no instruments-per-area figure. A Texas Department of Licensing and
  Regulation record for the project (TABS2023016373) lists 40,000 sq ft for the renovation, which may cover part of the
  building only; the sources don't say.

## The segment

1:58 at 1920 × 1080, 30 fps; the 3-D drawn at 15 fps, as the campaign video's replay. One continuous shot from a
whole-lab view, then the plans:

| Time | What happens |
|---|---|
| 0:00-0:31 | The conventional lab: six people walk between the rooms carrying sample totes, the rooms are labelled, the rules and the area come up |
| 0:31-0:51 | The same plan automated: four MiR250 + UR12e units drive in from the corridor's east door, the docking targets, fixed arms and chargers come up, four people leave, the robots take the routes people walked |
| 0:51-1:23 | The two Shuttles come down north of the building; every benchtop instrument and store flies to its tray; the walls and benches go down; the floor machines move to the vertical layout as its floor spreads from the Shuttles; the camera closes in; two units dock at the openings while the Shuttles present trays D and L, and a person works the glovebox and the atomizer |
| 1:23-1:58 | Cross-fade from straight down on the vertical lab to its plan, then the three plans side by side at one scale, the comparison, where the floor goes, and Emerald Cloud Lab |

The flights into the trays, the machines sliding and the floor spreading are animation devices, not a move plan. The
people's and robots' routes are drawn from each layout's aisles and doors (`floorspace_story`), not from a simulated
schedule.

**Narration:** ten lines, Kokoro v1.0 (open weights), voice `af_heart` at 0.96 speed, as the campaign video
(`twin/video/narration_floorspace.json`; spoken by `floorspace_voice.py` through `narration.phonemes`). Numbers with a
thousands separator are respelled for the voice ("4,280" as "four thousand two hundred eighty"): the phonemizer reads
the comma as a pause and says "four, two hundred eighty". Each line says only what is on screen when it is said, and
every number in it is `layouts.json`'s (`twin/tests/test_floorspace.py` checks).

**Heard back:** every line by faster-whisper small.en, 0.85 % word error over the script
(`out/floorspace/narration/check.json`). Two lines were reworded after the first pass: "Now automate it on the same floor
plan" came back as "now automated on the same floor plan", and "Emerald Cloud Lab's lab" read awkwardly. small.en still
writes "Kardex" as "cardiac", a word it doesn't know. The encoded file's own audio, transcribed whole: 1.7 % word error
(`out/floorspace/narration/encoded_check.json`), all of it spelling ("29%" for "29 percent", "1,000" for "thousand",
"100" for "a hundred") and "cardiac" again.

**The track:** each line levelled to -19 dBFS RMS at its time, 48 kHz, then ffmpeg's `loudnorm` in two passes to -16
LUFS and -1.5 dBTP. A single linear gain would have put the peaks over -1.5 dBTP, so `loudnorm` used its dynamic mode.
Subtitles: `out/floorspace/floorspace_preview.srt`.

**What it cost on the runner** (2026-11-27, 4 cores): the scene builds in 3 min with the tessellation cached (each of
three workers builds its own; 2.8-3.2 GB each), 1,284 renders at 1.4-1.5 s each with three workers side by side (10-11
min), and the cut with its overlays and plans in 2 min.

## Rebuilding it

```bash
cd vertical-lab
python -m twin.video.floorspace              # out/floorspace/layouts.json: the layouts, areas, breakdown
python -m twin.video.floorspace_voice tts    # the lines whose text changed (Kokoro), into out/floorspace/narration/
python -m twin.video.floorspace_voice check  # heard back by faster-whisper
# the 3-D needs the set-up movie's stack (VTK, cadquery), as twin/video/lab3d.py
TWIN_VIDEO_WORKERS=3 python -m twin.video.floorspace3d all     # /tmp/fs3d/lab3d.mp4: 1,284 renders
python -m twin.video.floorspace_cut final    # out/floorspace/floorspace_preview.mp4, .srt, .json
python -m twin.video.floorspace_cut sheet    # out/floorspace/sheet.png
python -m pytest -q twin/tests/test_floorspace.py
```

For round 5's re-cut: `floorspace_cut.Cut().frame(t, base)` draws any moment of the segment (base: the 3-D render at t
from `floorspace3d.FloorLab().render(t)`, or None in the plans), `Cut.T` is its length and `Cut.lines` its narration
with their times.

## A slip while building it

The first two checkpoint commits went to PR 400's branch as well as this one's: the action's push wrapper sends HEAD to
the branch the run started on. They were reverted there in one commit (a2dec04), which leaves PR 400's tree identical to
86517c6, and the work moved to a fresh branch (PR 406). GitHub marked the first stacked PR (404) as merged, because its
one commit had reached PR 400's branch.
