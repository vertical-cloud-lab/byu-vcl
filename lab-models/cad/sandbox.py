"""The sandbox from #199: the PiPER on a table, the sample holders around it within reach, and
an A1 mini beside it whose bed the arm can reach.

The table is spot D from #229 (1.29 x 1.36 m, arm centred). z = 0 is the table top and the
arm's base axis is the origin. Positions are a starting layout to argue about, not a design:
everything sits 250-550 mm from the base axis, inside the fingertip reach of 0.77 m (#229).
"""
from __future__ import annotations

import cadquery as cq

import equipment
import vendor
from common import Model, box, rbox

TABLE = (1290.0, 1360.0)          # spot D + second table, #229
TABLE_H = 900.0                   # assumed bench height

# key: (x, y, rotation about z in degrees); x right, y away from the viewer, mm from the base axis.
# The arm's J1 turns +-150 deg from +x (#229), so the 60 deg wedge on the -x side is left empty.
PLACES = {
    "holder_charge":        (0.0, -400.0, 0),        # cups, plugs and the press sleeve
    "arbor_press_1t":       (-321.0, -459.0, 35),    # the plug press-fit (the arm loads it, the press presses)
    "holder_vial_20ml":     (-170.0, -250.0, 34),
    "holder_sem_stubs":     (229.0, -328.0, -35),
    "crucible_replica":     (364.0, -210.0, 0),      # the rePOWDER crucible, rod and adapter (PR #232)
    "tiprack_20ul":         (241.0, 344.0, 55),
    "ot2_slot_nest":        (0.0, 430.0, 0),         # OT-2 slot replica with a NEST plate on its raised nest
    "balance_hr100a_dummy": (-276.0, 329.0, 40),     # the doser's balance, beaker under the breeze break
    "vial_20ml_water":      (60.0, -245.0, 0),
    "vial_20ml_powder":     (100.0, -245.0, 0),
    "griffin_beaker_100ml": (-10.0, -250.0, 0),
}
A1_PLACE = (470.0, 60.0, -90)     # on the arm's +x side, front of the printer facing the arm
A1_BED_Y = -80.0                  # bed run forward (towards the arm), as at the end of a print
ARM_YAW = -90.0                   # AgileX's STEP points the arm along +y; the URDF's zero is +x


def table() -> Model:
    m = Model("sandbox_table", "Sandbox table (spot D, #229)", source="assumed")
    W, D = TABLE
    m.add("top", rbox(W, D, 25.0, 6.0, z=-25.0), "wood")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.add(f"leg {sx:+d}{sy:+d}", box(sx * (W / 2 - 40) - 20, sy * (D / 2 - 40) - 20, -TABLE_H,
                                          sx * (W / 2 - 40) + 20, sy * (D / 2 - 40) + 20, -25.0), "extrusion")
    m.add("arm plate", rbox(200.0, 200.0, 12.0, 4.0, z=0.0), "aluminium")
    return m


def layout(cat: dict[str, Model], with_vendor: bool = True) -> Model:
    """Everything as one Model. with_vendor=False leaves AgileX's arm out (for the repo export)."""
    m = Model("sandbox_layout", "PiPER sandbox: holders, samples and an A1 mini on spot D",
              source="our layout; parts as listed")
    for part in table().parts:
        m.add(f"table - {part.name}", part.shape, part.material)
    for key, (x, y, rz) in PLACES.items():
        for part in cat[key].moved(x, y, 0.0, rz).parts:
            m.add(f"{key} - {part.name}", part.shape, part.material)
    x, y, rz = A1_PLACE
    for part in equipment.a1_mini(bed_y=A1_BED_Y).moved(x, y, 0.0, rz).parts:
        m.add(f"a1 mini - {part.name}", part.shape, part.material)
    if with_vendor:
        for part in vendor.piper().moved(0, 0, 12.0, ARM_YAW).parts:
            m.add(f"piper - {part.name}", part.shape, part.material)
    return m
