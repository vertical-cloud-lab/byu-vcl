"""The copper deck on the CubXL, and the same static tool-shadow check as the aluminium plan.

Reuses ../plot_deck_layout.py (geometry, the rigid-head rule, the check) and changes only
what copper changes: the stocks, a second rinse cup, the full 9-position vial holder,
the tip waste that the holder displaces, and station S4 as a PTFE blank. Writes
deck-check-cu.json. render_cubxl_cu.py imports the positions from here, so the
animation and the check share one source.

Every coordinate is in the CubOS deck frame of Ben's 2026-10-02 calibration
(cub_xl_ben_3_instrument.yaml): origin front-left-bottom, +X right, +Y away from the
operator, +Z up, mm. A proposal to re-jog, not a measurement.

    python deck_cu.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("al_deck", HERE.parent / "plot_deck_layout.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

# Ben's 9-position 20 mL holder (modules/electromagnetic-capper/cad/9VialHolder20mL_TightFit.step):
# 33.0 mm pitch, 33.4 x 297.4 x 35 mm. At x 318 its positions fall at y 35 + 33k, which keeps the
# aluminium plan's four stock positions (101-200).
HOLDER_X = 318.0
HOLDER_Y = [35.0 + 33.0 * k for k in range(9)]
HOLDER_RECT = (HOLDER_X - 16.7, HOLDER_Y[0] - 16.7, HOLDER_X + 16.7, HOLDER_Y[-1] + 16.7)
HOLDER_TOP = 35.0

STOCKS = {  # name: (x, y). 20 mL VOA vials with magnetic caps: rim 56, cap top 71
    "1 M HNO3, trace metal": (HOLDER_X, HOLDER_Y[1]),
    "ASW (D1141, no heavy metals)": (HOLDER_X, HOLDER_Y[2]),
    "ASW + 10 mg/L S": (HOLDER_X, HOLDER_Y[3]),
    "ASW + 0.1 mg/L S": (HOLDER_X, HOLDER_Y[4]),
    "DI water": (HOLDER_X, HOLDER_Y[5]),
}
SPARE = {"spare (FeSO4 nights only)": (HOLDER_X, HOLDER_Y[0])}  # y 233 and 266 sit under the pipette while the capper works at S3-S4
CUPS = {"rinse 2 (ASW)": (30.0, 245.0), "rinse 1 (DI)": (60.0, 245.0), "park cup": (90.0, 245.0)}
TIP_WASTE = {"c": (385.0, 150.0), "r": 15.0, "top": 50.0}  # the full holder now covers (335, 40)
STATION_ROLE = {1: "specimen", 2: "specimen", 3: "specimen", 4: "PTFE blank (fixture and carry-over blanks)"}

# The electrode cap for copper is the CAD in cad/ (cad_cu_cell.py, cad_parts.json): reference tip 3.0 mm
# above the metal (cap B in sim_well.py), a 0.12 mm clearance skirt over the lid's 16 mm boss, a 28 mm
# flange like the vial caps. Carried, its lowest points (the carrier's coil legs) hang 35.8 mm below the
# carriage: magnet face 16, cap 16, legs 3.8 below the skirt. They sit 2.2 mm above the metal when seated.
CAP_HANG = 16.0 + 16.0 + 3.8
CAP_RADIUS = 14.0
CAP_LOWEST_ABOVE_SKIRT = -3.8


def apply():
    base.STOCK_VIALS = dict(STOCKS)
    base.CUPS = dict(CUPS)
    base.TIP_WASTE = dict(TIP_WASTE)
    # the copper cap's lowest point is 3.8 mm below the skirt, not the aluminium cap's 4.5
    base.HANG["capper+cap"] = CAP_HANG
    base.RADIUS["capper+cap"] = CAP_RADIUS
    al_obstacles, al_events = base.obstacles, base.events

    def obstacles():
        obs = []
        for name, kind, geom, top in al_obstacles():
            if name.startswith("electrode cap on S"):
                geom = (geom[0], geom[1], CAP_RADIUS)
            obs.append((name, kind, geom, top))
        obs.append(("vial holder", "rect", HOLDER_RECT, HOLDER_TOP))
        for name, (cx, cy) in SPARE.items():
            obs.append((f"vial {name}", "circle", (cx, cy, base.VIAL_R), base.VIAL_CAP_TOP))
        return obs

    def events():
        out = []
        for ev in al_events():
            label, tool, xy, z, targets, other, cap_on = ev
            if label.startswith(("pipette draws", "capper decaps")):
                targets = set(targets) | {"vial holder"}
            if label.startswith("capper sets electrode cap on"):
                z += 4.5 + CAP_LOWEST_ABOVE_SKIRT  # lowest point 3.8 mm below the skirt, not the aluminium cap's 4.5
            out.append((label, tool, xy, z, targets, other, cap_on))
        # acid from above the rim of each filled tube, with the night's one acid tip
        for tx in base.TUBE_X:
            for ty in base.TUBE_Y:
                out.append((f"acid tip over tube ({tx:.0f},{ty:.0f})", "pipette", (tx, ty), base.TUBE_RACK["top"] + 5.0,
                            {"tube rack"}, "capper", base.ALL_CAPS))
        return out

    base.obstacles = obstacles
    base.events = events


def main():
    apply()
    summary = base.check()
    summary["deck"] = {"stocks": STOCKS, "spare": SPARE, "cups": CUPS, "tip_waste": TIP_WASTE,
                       "holder": {"x": HOLDER_X, "y": HOLDER_Y, "rect": HOLDER_RECT, "top": HOLDER_TOP},
                       "stations": {f"S{i}": [x, base.STATION_Y, STATION_ROLE[i]] for i, x in enumerate(base.STATION_X, start=1)}}
    (HERE / "deck-check-cu.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("events", "deck")}, indent=1))
    for r in summary["events"]:
        if r["problems"]:
            print("PROBLEM", r["event"], r["problems"])


if __name__ == "__main__":
    main()
