# Round 15: one complete lab in `setup_lab.build` (#303, PR #318)

Sterling (2026-11-23): "pull in the latest results from all the other relevant PRs ... and re-render everything in a
self-consistent and cohesive way". Several stations designed in merged PRs and in round 14 were never put on the shared
floor. This round puts on it what fits cleanly. What doesn't fit is left off, and the reasons are below.

| Item | On the floor? | Switch | Where |
| --- | --- | --- | --- |
| Chemical waste station (PR #371, [waste.md](waste.md)) | **yes** | `VLAB_WASTE=0` leaves it out | In the ducted fume hood (`FLOOR_PLAN["fumehood"]`, x 1500, south row). Its two base cabinets' doors (solvent yellow, acid blue, each with its band) sit 2 mm in front of the hood's own. The intake tray, the delivered bottle, the empties and the etch sit on the work surface. Everything is in the hood's own frame, parented to its rig, so it comes in with the hood in the set-up movie. About 4,000 triangles. The cabinets' contents are left out, because behind opaque doors they would only cost triangles. |
| Floor-cleaning unit 3 and its charger (PR #369, [floor_cleaning.md](floor_cleaning.md)) | **yes** | `VLAB_UNIT3=0` | `floor_cleaning.BAY`: a third MiR Charge 48V at x -3,411..-2,789 in the south row, 1.6 m west of unit 1's, outside every powder zone. Unit 3 (MiR250 + cabinet + UR10e + 2F-85, orange band) is parked on it at (-3,100, -5,818), heading -90, as units 1 and 2 park on theirs. It is `F.unit3`, not one of `units`, so no clip drives it by accident. Its 118EXP vacuums (option C keeps them on wall power at their station) are not on the floor yet. |
| ICP-MS station ([icpms.md](icpms.md)) | no | - | See below. `safety_other.ICPMS_ON_FLOOR` stays `False`, so its shower and O2 monitor stay off too. |
| Cup-and-plug machining cell (PR #373, [machining.md](machining.md)) | no (round 16: **yes**, [lab_r16.md](lab_r16.md)) | `VLAB_MCELL=0` (round 16) | See below. |
| The rePowder's target post | moved | - | It now shares the sieving cell's post (`SHARED_POST`). |

## The rePowder's target post (round 14 (C)'s open fault)

The post stood at model (938, -379), which is world (-2,837, -2,079). That is inside MiR250 1's footprint at the latch
(`atom_latch.A_AT`, model x 250..1,050, y -850..-270), where `alloy_atomize` has parked it since round 14. Round 14's
set-up audit also caught the rePowder being set down onto that post (5/9, frames 259-268, 50 mm).

Nowhere between that spot, the dock line and the aisle has room for a 300 mm foot plate. So the rePowder's docked unit
now reads the sieving cell's post at (-2,350, -2,012), 737 mm beyond its front end and 218 mm to its left. Each dock
reads a different face of the cube: the rePowder's unit the west face, the sieving cell's unit the east face
(`warehouse.tag` has five faces with five patterns). `setup_lab.Floor._tape` draws the posts again without the shared
one, and every cube keeps its tag id. The post is 115 mm clear of MiR250 1 at `atom_base.PARK["right"]` and 225 mm
clear of it at `A_AT`. It is off every dock and approach lane.

`fit` reports the same docks as before; only the rePowder's `target_post` moved. The rePowder dock and the sieving
cell's dock still show their round-14 hit, `['repowder']`, and so does "machines in the aisle". All three come from
the rePowder model's own plan rectangle, which reaches into the aisle (y -3,160).

## The ICP-MS station: why it isn't on the floor

The station is 3.73 m along its row (1,829 mm hood, 100 mm gap, 1,800 mm bench) once the dewar moves behind the bench,
and 0.81 m deep.

- **Round 14 (D)'s spot (south row, x 7,850-11,580) has three problems.**
  - It is the Meltio cell's forklift strip. `r8_scale.py` and [scaleup.md](scaleup.md) give each scale-up machine "a
    2.4 m or wider clear strip in front of it running up to the aisle", and the set-up movie's step 5 caption says so.
  - The bench would cover the wire EDM's only pivot spot, at x 8,050. The pivot's circle needs the bench to start at
    x 8,421 or more, which pushes the hood's east end to about 12,150, into rack E at x 11,833.
  - The station's own two docks get no pivot spot on the dock line either. A MiR250 turns on the line only where the
    row leaves a gap of about 742 mm. A setback of at least 184 mm would fix that, but then the docked MiR stands
    264 mm or more off the hood instead of the clip's 60 mm.
- **The south row's west end is the EOS M 400-4's strip.**
- **The north row west of the glovebox has 4.13 m before rack W, which is not enough.** The glovebox's pivot spot
  (x -7,750) needs the station's east end at x -8,150 or less, which leaves 3.68 m. The glovebox's O2 monitor
  (-7,950, -500) and the argon line's drop (-7,700, -632) stand where the dewar and the bench's back would go.

**Two ways forward.** The first is the north row's west end with a 200 mm setback: hood west, bench east, the dewar
behind the bench. Its docks would be on the north dock line, the hood's backed into from the east as in the clip, with
the SPS 4 stop 920 mm east on the same line. The shower and the glovebox's O2 monitor would have to be re-placed with
`safety_other.place_search`. The second is a room of its own, which [icpms.md](icpms.md) already suggests.

`icpms.py`'s clip builds its own studio scene (`tour.studio`), not `setup_lab.build`, so it never drew a second copy
and its audit doesn't depend on the floor.

## The machining cell: why it isn't on the floor

**Round 16 put it on the floor** ([lab_r16.md](lab_r16.md)): south of the south row, front to the north behind the
68SC-2, unit 3's charger and charger 0, on its old x, with its own way in from the aisle down the row's west end and
along a corridor behind the row. Nothing that stands on the floor moved. What follows is round 15's reasoning, kept as
it was.

Its spot (`machining.FLOOR`, fence x -4,035..-1,835 between the 68SC-2 and charger 0, dock at (-2,935, -5,868)) has
three problems:

- It is unit 3's charger bay (`floor_cleaning.BAY`, x -3,411..-2,789).
- Its dock's post, by `warehouse.target_xy` at (-3,585, -6,088), stands on the 68SC-2's post at (-3,650, -6,088).
- Its dock has no pivot spot to the west (the 68SC-2 is 25 mm from the fence). To the east the approach runs about
  3.3 m along the dock line, past chargers 0 and 1. Units 1 and 2 park across that line whenever they charge (y
  -6,218..-5,418).

Placing it needs a different spot, or unit 3's charger and a different approach. One option is south of the south row,
like the scale-up machines, with its own strip. `machining_cell.py`'s `MCELL_STILL=lab` still draws it at its own spot
from `out/tray_plan.json`, which now has unit 3's charger (`charger2`) inside the cell's fence.

## Turnaround clips parked on the rePowder's vacuum pump (report only)

The pump is `repowder/model.py`'s `vacuum_pump` (`utility_parts`): model x -880..-420, y 120..340, z 0..260, which is
world x -4,655..-4,195, y -1,580..-1,360. A MiR250 body (800 x 580 mm, 30-280 mm up) stands on it in:

- `atom_crucible.py`: MiR250 2 at `MIR2_AT` (-960, -40, 90°) covers 210 x 220 mm of the motor end, for the whole of
  both clips.
- `atom_container.py`: MiR250 1 at `A_LEFT` (-700, -350, -45°). Its rear-left corner is 18 mm into the pump's front
  face, from the start until the drive at line 506. That drive also passes 41 mm from the pump.
- `atom_base.PARK["left"]` (-760, -40, 90°) would cover most of the pump, but no clip uses it.

`collide.py` doesn't check a parked MiR against the machine, so the audits never flagged these. `atom_ground.NOT_IN_LAB`
already names "left" and "crucible_left" as standing on the pump. It misses `atom_container`'s "brush" (`A_LEFT`).
