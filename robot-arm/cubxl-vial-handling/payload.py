"""Masses of the printed parts and the full carrier's payload on the PiPER (#266).

    python payload.py     # after slice/slice_a1mini.py -> exports/payload.json

Printed masses are Bambu Studio's own estimates from slicing each part alone (slice/report.json: PLA
Basic, 3 walls, 25 % infill), not solid volume. Vial masses are analysis.py's assumptions: weigh yours.
"""

from __future__ import annotations

import json
import math

import parts as PT
import sources as S

HERE = PT.HERE
P = PT.P
G0 = 9.81
PIPER_PAYLOAD_KG = 1.5
GRIPPER_KG = 0.5               # AgileX's gripper, with its own jaws
M3X20_SHCS_G, M3_NUT_G = 1.5, 0.4
VIAL = dict(glass=20.0, cap=6.0, water=20.0)   # g, 20 mL VOA vial with a PANDA magnetic cap (analysis.py)
VIAL_DUMMY_SOLID_G = 46.8      # Chris's printed vial at 100 % infill (analysis.py)
GRIP_N, MU_SILICONE = 40.0, 0.7


def main():
    rep = json.loads((HERE / "slice" / "report.json").read_text())["per_part"]
    g = {k: v["filament_g"] for k, v in rep.items()}
    carrier = g["carrier_half_a"] + g["carrier_half_b"] + g["handle_post"]
    hardware = 2 * (M3X20_SHCS_G + M3_NUT_G)
    vial = sum(VIAL.values())
    full = carrier + hardware + 8 * vial
    dummy = carrier + hardware + 8 * VIAL_DUMMY_SOLID_G
    inserts = g["finger_insert_upper"] + g["finger_insert_lower"]
    stock = S.gripper()
    half = 4 * vial / 1000
    arm = sum(PT.slot_y(i) for i in (1, 2, 3, 4)) / 4 / 1000
    out = dict(
        printed_g={k: round(v, 2) for k, v in g.items()},
        carrier_printed_g=round(carrier, 1), carrier_hardware_g=round(hardware, 1),
        vial_full_g=vial, full_carrier_g=round(full, 1), full_carrier_with_dummy_vials_g=round(dummy, 1),
        fraction_of_piper_rating=round(full / 1000 / PIPER_PAYLOAD_KG, 3),
        fraction_if_gripper_counts=round((full / 1000 + GRIPPER_KG) / PIPER_PAYLOAD_KG, 3),
        finger_inserts_g=round(inserts, 1),
        stock_jaw_and_pad_volume_cm3_each=round((stock["jaw_volume"] + stock["pad_volume"]) / 1000, 2),
        lopsided_torque_Nm=round(half * G0 * arm, 3),
        v_jaw_wedge_factor=round(1 / math.sin(math.radians(45)), 3),
        vial_slip_force_N=round(2 * 2 * MU_SILICONE * GRIP_N / (2 * math.sin(math.radians(45))), 1),
        post_vertical_hold="positive: the rib sits in the groove, so holding the carrier up does not rely on friction",
        dock_block_g=g["dock_block"], offset_plate_g=round(sum(v for k, v in g.items() if k.startswith("plate")) /
                                                           sum(1 for k in g if k.startswith("plate")), 2),
    )
    (PT.OUT / "payload.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
