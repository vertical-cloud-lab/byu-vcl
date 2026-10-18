"""Draw the proposed CubXL deck and head layout for corrosion spots, and check it.

Writes deck-layout.png (three panels) and deck-layout-check.json (the static
clearance check). Every number is a proposal in the CubOS deck frame of Ben's
2026-10-02 calibration (cub_xl_ben_3_instrument.yaml): origin front-left-bottom,
+X right, +Y away from the operator, +Z up, millimetres. Re-jog before use.

Design: the electrodes travel as a magnetic "electrode cap" that the existing
capper picks up and sets down, the way it handles vial caps. No fourth tool goes
on the head. A head-mounted probe was checked first and failed: 50 mm in front
of the pipette it lands on the 138 mm tip racks during tip pickup, and beside
the pipette it puts the pipette on the tray lid whenever the probe is in a well.

The check is the rigid-head rule: the capper and pipette hang from one carriage
at fixed offsets, so whenever one is lowered onto a target the other is at the
same carriage height somewhere else. For each planned "tool down" event the
script places the other tool and reports anything it would hit. It is a plan
check, not a CubOS validation.

    python plot_deck_layout.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent

# Gantry: Ben's 2026-10-02 file. The working volume is what the capper (offset
# 0, 0) reaches; the pipette reaches deck = gantry + (55, 11).
GANTRY = {"x": (0.0, 361.0), "y": (0.0, 278.0), "z": (0.0, 122.0)}
TRAVEL_Z = 122.0  # every XY move rides z_max (multi_tool_safe_travel_z)
PIP_OFF = (55.0, 11.0)

# How far each tool's lowest point hangs below the carriage reference.
HANG = {
    "capper": 16.0,            # magnet face (depth -16 in the gantry file)
    "capper+cap": 16.0 + 20.5,  # carrying the electrode cap: 16 mm body + 4.5 mm electrodes
    "pipette": 35.0,           # with a 35 mm tip on
    "pipette_bare": 0.0,       # no tip: the nozzle is the carriage reference
}
RADIUS = {"capper": 10.0, "capper+cap": 11.0, "pipette": 6.0, "pipette_bare": 6.0}

# Deck items. Rect: (x0, y0, x1, y1). Circle: (cx, cy, r). "top" is the highest
# point in deck z that a tool can hit.
TRAY = {"rect": (170.0, 220.0, 275.0, 260.0), "top": 26.0, "face_z": 20.0}
STATION_X = [185.0, 210.0, 235.0, 260.0]
STATION_Y = 240.0
WELL_DY = 4.5  # two 3 mm wells per station, 9 mm apart, for pieces >= 15 mm
CAP_ON_STATION_TOP = 42.0  # tray lid 26 + electrode cap body 16

TIP_RACK_1 = {"a1": (291.332, 89.0), "a2": (282.832, 89.0), "pickup_z": 59.0}  # Ben's, unchanged
TIP_RACK_2 = {"a1": (108.0, 89.0), "a2": (99.5, 89.0), "pickup_z": 59.0}  # proposed
ROWS, ROW_PITCH = 15, 8.5
TIP_TOP = 66.0


def rack_rect(rack):
    xs = [rack["a1"][0], rack["a2"][0]]
    return (min(xs) - 5.75, rack["a1"][1] - 4.0, max(xs) + 5.75, rack["a1"][1] + (ROWS - 1) * ROW_PITCH + 4.0)


def rack_tips(rack):
    for r in range(ROWS):
        for col in ("a1", "a2"):
            yield (rack[col][0], rack[col][1] + r * ROW_PITCH)


STOCK_VIALS = {  # 20 mL vials with magnetic caps, in Ben's 28 mm holder: rim 56, cap top 71
    "0.6 M NaCl": (318.0, 101.0),
    "0.06 M NaCl": (318.0, 134.0),
    "0.006 M NaCl": (318.0, 167.0),
    "DI water": (318.0, 200.0),
}
VIAL_R, VIAL_RIM, VIAL_CAP_TOP = 14.0, 56.0, 71.0

CUPS = {"rinse cup": (60.0, 245.0), "park cup": (90.0, 245.0)}  # the cap sits on these
CUP_R, CUP_RIM = 7.5, 45.0

TUBE_RACK = {"rect": (170.0, 20.0, 266.0, 54.0), "top": 32.0}  # 2 x 8 open 0.5 mL PP tubes
TUBE_X = [176.0 + 12.0 * k for k in range(8)]
TUBE_Y = [28.0, 46.0]

TIP_WASTE = {"c": (335.0, 40.0), "r": 15.0, "top": 50.0}
PSTAT_BOX = {"rect": (0.0, 290.0, 80.0, 330.0), "top": 40.0}  # behind the working volume


def obstacles():
    obs = [("coupon tray", "rect", TRAY["rect"], TRAY["top"])]
    for i, sx in enumerate(STATION_X, start=1):
        obs.append((f"electrode cap on S{i}", "circle", (sx, STATION_Y, 10.0), CAP_ON_STATION_TOP))
    obs.append(("tip rack 1 (Ben's)", "rect", rack_rect(TIP_RACK_1), TIP_TOP))
    obs.append(("tip rack 2", "rect", rack_rect(TIP_RACK_2), TIP_TOP))
    for name, (cx, cy) in STOCK_VIALS.items():
        obs.append((f"vial {name}", "circle", (cx, cy, VIAL_R), VIAL_CAP_TOP))
    for name, (cx, cy) in CUPS.items():
        obs.append((name, "circle", (cx, cy, CUP_R), CUP_RIM + 16.0))  # with the cap parked on it
    obs.append(("tube rack", "rect", TUBE_RACK["rect"], TUBE_RACK["top"]))
    obs.append(("tip waste", "circle", (*TIP_WASTE["c"], TIP_WASTE["r"]), TIP_WASTE["top"]))
    obs.append(("potentiostat box", "rect", PSTAT_BOX["rect"], PSTAT_BOX["top"]))
    return obs


def overlaps(kind, geom, cx, cy, r):
    if kind == "rect":
        x0, y0, x1, y1 = geom
        nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
        return (nx - cx) ** 2 + (ny - cy) ** 2 < r * r
    gx, gy, gr = geom
    return (gx - cx) ** 2 + (gy - cy) ** 2 < (gr + r) ** 2


def events():
    """(label, tool, deck xy of the tool's lowest point, deck z of it, obstacles it may
    touch, other tool state, which stations may carry the cap meanwhile)."""
    ev = []
    n = len(STATION_X)
    for i, x in enumerate(STATION_X, start=1):
        # the cap sits on S_{i+1} while S_i is collected; never elsewhere during pipetting at S_i
        cap_on = {f"electrode cap on S{i + 1}"} if i < n else set()
        for dy in (-WELL_DY, WELL_DY):
            ev.append((f"pipette in S{i} well y{STATION_Y + dy:.1f}", "pipette", (x, STATION_Y + dy), TRAY["face_z"] + 1.0, {"coupon tray"}, "capper", cap_on))
        ev.append((f"capper sets electrode cap on S{i}", "capper+cap", (x, STATION_Y), TRAY["face_z"] + 1.5, {"coupon tray"}, "pipette_bare", set()))
    for name, (cx, cy) in STOCK_VIALS.items():
        ev.append((f"pipette draws {name}", "pipette", (cx, cy), 35.0, {f"vial {name}"}, "capper", ALL_CAPS))
        ev.append((f"capper decaps {name}", "capper", (cx, cy), VIAL_CAP_TOP, {f"vial {name}"}, "pipette_bare", ALL_CAPS))
    for name, (cx, cy) in CUPS.items():
        ev.append((f"capper sets electrode cap on {name}", "capper+cap", (cx, cy), CUP_RIM - 4.5, {name}, "pipette_bare", set()))
    for tx in TUBE_X:
        for ty in TUBE_Y:
            ev.append((f"pipette fills tube ({tx:.0f},{ty:.0f})", "pipette", (tx, ty), 40.0, {"tube rack"}, "capper", ALL_CAPS))
    for i, rack in enumerate((TIP_RACK_1, TIP_RACK_2), start=1):
        rname = "tip rack 1 (Ben's)" if i == 1 else "tip rack 2"
        for (tx, ty) in rack_tips(rack):
            ev.append((f"pipette picks {rname} ({tx:.1f},{ty:.1f})", "pipette_bare", (tx, ty), rack["pickup_z"], {rname}, "capper", ALL_CAPS))
    ev.append(("pipette drops tip", "pipette", TIP_WASTE["c"], 95.0 - 35.0, {"tip waste"}, "capper", ALL_CAPS))
    return ev


ALL_CAPS = {f"electrode cap on S{i}" for i in range(1, len(STATION_X) + 1)}


def tool_offset(tool):
    return PIP_OFF if tool.startswith("pipette") else (0.0, 0.0)


def check():
    obs = obstacles()
    results, tight = [], {}
    for label, tool, (tx, ty), tz, targets, other, cap_on in events():
        carriage_z = tz + HANG[tool]
        off = tool_offset(tool)
        gx, gy = tx - off[0], ty - off[1]
        problems = []
        if not (GANTRY["x"][0] <= gx <= GANTRY["x"][1] and GANTRY["y"][0] <= gy <= GANTRY["y"][1] and GANTRY["z"][0] <= carriage_z <= GANTRY["z"][1]):
            problems.append(f"gantry ({gx:.1f}, {gy:.1f}, {carriage_z:.1f}) is outside the working volume")
        live = [o for o in obs if o[0] not in targets and (not o[0].startswith("electrode cap") or o[0] in cap_on)]
        # the active tool against everything that is not its target
        for name, kind, geom, top in live:
            if overlaps(kind, geom, tx, ty, RADIUS[tool]) and tz < top + 2.0:
                problems.append(f"{tool} itself at ({tx:.0f},{ty:.0f}) z {tz:.0f} over {name} (top {top:.0f})")
        # the other tool, at the same carriage height
        ooff = tool_offset(other)
        ox, oy, oz = gx + ooff[0], gy + ooff[1], carriage_z - HANG[other]
        for name, kind, geom, top in live:
            if overlaps(kind, geom, ox, oy, RADIUS[other]):
                if oz < top + 2.0:
                    problems.append(f"{other} at ({ox:.0f},{oy:.0f}) z {oz:.0f} over {name} (top {top:.0f})")
                else:
                    key = f"{other} over {name}"
                    tight[key] = min(tight.get(key, 1e9), oz - top)
        results.append({"event": label, "tool": tool, "other": other, "carriage_z": round(carriage_z, 1), "gantry_xy": [round(gx, 1), round(gy, 1)], "problems": problems})
    return {
        "events_checked": len(results),
        "events_with_problems": sum(1 for r in results if r["problems"]),
        "tightest_pass_mm": {k: round(v, 1) for k, v in sorted(tight.items(), key=lambda kv: kv[1])[:8]},
        "travel_clearance_mm": {
            "pipette tip end at travel": TRAVEL_Z - HANG["pipette"],
            "electrode cap tips at travel": TRAVEL_Z - HANG["capper+cap"],
            "tallest deck item": VIAL_CAP_TOP,
        },
        "hang_mm": HANG,
        "events": results,
    }


# ---------------------------------------------------------------------------
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # liquid handling / cell / head


def draw_top(ax):
    ax.set_facecolor(SURFACE)
    ax.add_patch(Rectangle((-50, -45), 480, 490, fc="#f3f2ee", ec=GRID, lw=1))
    ax.add_patch(Rectangle((0, 0), 361, 278, fill=False, ec=MUTED, lw=1, ls="--"))
    ax.add_patch(Rectangle((55, 11), 361, 278, fill=False, ec=BLUE, lw=1, ls=":"))

    for i, rack in enumerate((TIP_RACK_1, TIP_RACK_2), start=1):
        x0, y0, x1, y1 = rack_rect(rack)
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#dbe8f8", ec=BLUE, lw=1))
        for (tx, ty) in rack_tips(rack):
            ax.add_patch(Circle((tx, ty), 1.6, fc=BLUE, ec="none"))
        ax.text((x0 + x1) / 2, y1 + 4, "tips 1 (Ben's, unmoved)" if i == 1 else "tips 2 (add)", ha="center", va="bottom", fontsize=7, color=INK2)

    for name, (cx, cy) in STOCK_VIALS.items():
        ax.add_patch(Circle((cx, cy), VIAL_R, fc="#dbe8f8", ec=BLUE, lw=1.2))
        ax.add_patch(Circle((cx, cy), 8, fill=False, ec=BLUE, lw=0.6))
        ax.text(cx, cy, name.replace(" NaCl", "\nNaCl"), ha="center", va="center", fontsize=6, color=INK)
    ax.text(318 + VIAL_R + 4, 150, "capped 20 mL\nstocks (the\ncapper opens\nthem)", ha="left", va="center", fontsize=7, color=INK2)

    for name, (cx, cy) in CUPS.items():
        ax.add_patch(Circle((cx, cy), CUP_R, fc="#fde3d8", ec=ORANGE, lw=1.2))
        ax.text(cx, cy + CUP_R + 2, name, ha="center", va="bottom", fontsize=6.5, color=INK2)
    # the electrode cap, parked
    ax.add_patch(Circle(CUPS["park cup"], 10, fill=False, ec=ORANGE, lw=1.6))
    ax.text(40, 262, "electrode cap,\nparked wet", ha="center", va="bottom", fontsize=6.5, color=ORANGE)

    x0, y0, x1, y1 = TUBE_RACK["rect"]
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#dbe8f8", ec=BLUE, lw=1))
    for tx in TUBE_X:
        for ty in TUBE_Y:
            ax.add_patch(Circle((tx, ty), 4.0, fc=SURFACE, ec=BLUE, lw=0.8))
    ax.text((x0 + x1) / 2, y0 - 4, "16 open 0.5 mL PP tubes: each spot's electrolyte, for ICP", ha="center", va="top", fontsize=7, color=INK2)

    x0, y0, x1, y1 = TRAY["rect"]
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=3", fc="#fde3d8", ec=ORANGE, lw=1.4))
    for i, sx in enumerate(STATION_X, start=1):
        ax.add_patch(Rectangle((sx - 8, STATION_Y - 8), 16, 16, fc="#cfcfcb", ec=INK2, lw=0.8))
        ax.add_patch(Circle((sx, STATION_Y), 1.0, fc=INK, ec="none"))
        for dy in (-WELL_DY, WELL_DY):
            ax.add_patch(Circle((sx, STATION_Y + dy), 1.5, fc=ORANGE, ec="none"))
            ax.add_patch(Circle((sx, STATION_Y + dy), 4.0, fill=False, ec=ORANGE, lw=0.6))
        for px in (sx - 11, sx + 11):  # RE / CE pads the cap's pogo pins land on
            ax.add_patch(Rectangle((px - 1.5, STATION_Y - 3), 3, 6, fc=INK2, ec="none"))
        ax.text(sx, y0 - 3, f"S{i}", ha="center", va="top", fontsize=7, color=INK2)
    ax.text((x0 + x1) / 2, y1 + 3, "coupon tray: 4 polished pieces, 2 O-ring wells each,\npogo pin (WE) under each piece, RE/CE pads beside each", ha="center", va="bottom", fontsize=7, color=INK2)

    cx, cy = TIP_WASTE["c"]
    ax.add_patch(Circle((cx, cy), TIP_WASTE["r"], fc="#eeeeea", ec=INK2, lw=1))
    ax.text(cx, cy, "tip\nwaste", ha="center", va="center", fontsize=6.5, color=INK2)
    x0, y0, x1, y1 = PSTAT_BOX["rect"]
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#eeeeea", ec=INK2, lw=1, ls="--"))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, "potentiostat + Pi cable\n(outside the head's reach)", ha="center", va="center", fontsize=6.5, color=INK2)
    ax.plot([80, 170], [310, 258], color=INK2, lw=0.8, ls="--")
    ax.text(125, 290, "WE / RE / CE bus", fontsize=6.5, color=INK2, rotation=-30)

    # head pose: capper setting the electrode cap on S2; the pipette is 55 right, 11 back
    sx = STATION_X[1]
    pose = {"capper + cap": (sx, STATION_Y), "pipette": (sx + 55, STATION_Y + 11), "camera": (sx - 40, STATION_Y + 10)}
    for name, (hx, hy) in pose.items():
        col = ORANGE if "cap" in name else AQUA
        ax.add_patch(Circle((hx, hy), 6, fill=False, ec=col, lw=1.6))
        ax.text(hx + (8 if name == "pipette" else 0), hy - (9 if name != "pipette" else 0), name, fontsize=6.5, color=col, ha="center" if name != "pipette" else "left", va="top" if name != "pipette" else "center")
    ax.plot([pose["camera"][0], pose["capper + cap"][0], pose["pipette"][0]], [pose["camera"][1], pose["capper + cap"][1], pose["pipette"][1]], color=AQUA, lw=0.9)
    ax.annotate("one carriage: while the capper sets the\ncap on S2 the pipette is here, tipless", xy=pose["pipette"], xytext=(330, 295), fontsize=7, color=INK2, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    ax.set_xlim(-55, 435)
    ax.set_ylim(-50, 450)
    ax.set_aspect("equal")
    ax.set_xlabel("CubOS deck x, mm (operator stands at the bottom)", color=INK2, fontsize=8)
    ax.set_ylabel("CubOS deck y, mm", color=INK2, fontsize=8)
    ax.tick_params(colors=MUTED, labelsize=7)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.text(-50, 440, "A  Deck, top view", fontsize=10, fontweight="bold", color=INK, va="top")
    ax.text(2, -3, "capper reach = working volume (dashed)", fontsize=6.5, color=MUTED, va="top")
    ax.text(418, 13, "pipette reach (dotted)", fontsize=6.5, color=BLUE, ha="right", va="bottom")
    ax.text(190, -40, "deck plate (PandaDeck, 480 x 490)", fontsize=6.5, color=MUTED)


def draw_side(ax):
    """Looking from the front along +Y: x across, z up. Head over station S2."""
    ax.set_facecolor(SURFACE)
    ax.axhline(0, color=INK2, lw=1.2)
    x0, _, x1, _ = TRAY["rect"]
    ax.add_patch(Rectangle((x0, 0), x1 - x0, TRAY["top"], fc="#fde3d8", ec=ORANGE, lw=1))
    ax.text((x0 + x1) / 2, 2, "tray: coupon face at 20, lid top 26", ha="center", fontsize=6.5, color=INK2)
    for sx in STATION_X:
        ax.add_patch(Rectangle((sx - 1.5, TRAY["face_z"]), 3, 6, fc="#cfe6f9", ec="none"))
    for rack, lab in ((TIP_RACK_1, "tips 1: 66"), (TIP_RACK_2, "tips 2")):
        rx0, _, rx1, _ = rack_rect(rack)
        ax.add_patch(Rectangle((rx0, 0), rx1 - rx0, TIP_TOP, fc="#dbe8f8", ec=BLUE, lw=1))
        ax.text((rx0 + rx1) / 2, TIP_TOP + 2, lab.split(":")[0], ha="center", va="bottom", fontsize=6.5, color=INK2)
    ax.add_patch(Rectangle((318 - VIAL_R, 0), 2 * VIAL_R, VIAL_RIM, fc="#dbe8f8", ec=BLUE, lw=1, alpha=0.6))
    ax.add_patch(Rectangle((318 - 9, VIAL_RIM), 18, VIAL_CAP_TOP - VIAL_RIM, fc="#cfcfcb", ec=INK2, lw=0.8))
    ax.text(318, VIAL_CAP_TOP + 2, "caps 71", ha="center", va="bottom", fontsize=6.5, color=INK2)
    for cx in CUPS.values():
        ax.add_patch(Rectangle((cx[0] - CUP_R, 0), 2 * CUP_R, CUP_RIM, fc="#fde3d8", ec=ORANGE, lw=1, alpha=0.6))
    ax.text(75, CUP_RIM + 2, "cups 45", ha="center", fontsize=6.5, color=INK2)

    sx = STATION_X[1]
    for cz, lab, alpha in ((TRAVEL_Z, "travel: carriage at 122", 0.4), (TRAY["face_z"] + 1.5 + HANG["capper+cap"], "setting the cap: carriage at 58", 1.0)):
        ax.add_patch(Rectangle((sx - 50, cz), 115, 6, fc="#d6f1e6", ec=AQUA, lw=1, alpha=alpha))
        ax.text(sx - 48, cz + 8, lab, fontsize=6.5, color=AQUA if alpha == 1 else MUTED)
        # capper body + electrode cap
        ax.plot([sx, sx], [cz, cz - HANG["capper"]], color=AQUA, lw=6, alpha=alpha, solid_capstyle="butt")
        ax.add_patch(Rectangle((sx - 10, cz - HANG["capper"] - 16), 20, 16, fc="#fde3d8", ec=ORANGE, lw=1, alpha=alpha))
        ax.plot([sx, sx], [cz - HANG["capper"] - 16, cz - HANG["capper+cap"]], color=ORANGE, lw=1.5, alpha=alpha)
        # pipette, tipless during cap moves
        ax.plot([sx + 55, sx + 55], [cz, cz - 1], color=AQUA, lw=4, alpha=alpha, solid_capstyle="butt")
        ax.plot([sx - 40, sx - 40], [cz, cz - 12], color=AQUA, lw=4, alpha=alpha, solid_capstyle="butt")
        if alpha == 1:
            ax.text(sx + 58, cz + 10, "pipette nozzle,\nno tip, at 58", ha="left", va="bottom", fontsize=6.5, color=INK2)
            ax.text(sx - 40, cz - 15, "camera", ha="center", va="top", fontsize=6.5, color=INK2)
            ax.text(sx + 13, cz - 24, "electrode cap:\nsteel disc, 16 mm body,\nelectrodes 4.5 below", fontsize=6.5, color=INK2, va="top")
    ax.annotate("", xy=(345, TRAVEL_Z - HANG["capper+cap"]), xytext=(345, VIAL_CAP_TOP), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
    ax.text(349, (TRAVEL_Z - HANG["capper+cap"] + VIAL_CAP_TOP) / 2, "14.5 mm", fontsize=6.5, color=INK2, va="center", ha="left")
    ax.text(349, TRAVEL_Z - HANG["capper+cap"] + 1, "cap tips at\ntravel: 85.5", fontsize=6.5, color=INK2, ha="left", va="bottom")
    ax.plot([318, 345], [TRAVEL_Z - HANG["capper+cap"]] * 2, color=MUTED, lw=0.6, ls=":")

    ax.set_xlim(40, 400)
    ax.set_ylim(-5, 150)
    ax.set_aspect("equal")
    ax.set_xlabel("deck x, mm", color=INK2, fontsize=8)
    ax.set_ylabel("deck z, mm", color=INK2, fontsize=8)
    ax.tick_params(colors=MUTED, labelsize=7)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.text(42, 147, "B  Head over station S2, seen from the front", fontsize=10, fontweight="bold", color=INK, va="top")


def draw_well(ax):
    """Cross-section of one station with the electrode cap on it. Millimetres."""
    ax.set_facecolor(SURFACE)
    ax.add_patch(Rectangle((-16, -12), 32, 10, fc="#fde3d8", ec=ORANGE, lw=1))
    ax.add_patch(Rectangle((-0.6, -6), 1.2, 4.6, fc=INK, ec="none"))
    ax.plot([0, 0, 15], [-6, -9, -9], color=INK, lw=0.8)
    ax.text(15.5, -9, "WE", fontsize=7, color=INK, va="center")
    ax.add_patch(Rectangle((-5, -1.5), 10, 1.5, fc="#cfcfcb", ec=INK2, lw=0.8))
    ax.text(0, -2.3, "polished piece, bare back on a pogo pin", ha="center", va="top", fontsize=6.5, color=INK2)
    for sgn in (-1, 1):  # tray lid with the stepped bore
        xs = [sgn * 1.5, sgn * 1.5, sgn * 4, sgn * 4, sgn * 16, sgn * 16, sgn * 1.5]
        zs = [0, 1.6, 1.6, 6, 6, 0, 0]
        ax.fill(xs, zs, fc="#fde3d8", ec=ORANGE, lw=1)
        ax.add_patch(Circle((sgn * 2.4, 0.9), 0.9, fc="#444", ec="none"))
        ax.add_patch(Rectangle((sgn * 11 - 1.5, 6), 3, 0.6, fc=INK2, ec="none"))  # RE / CE pad
    ax.add_patch(Rectangle((-1.5, 0), 3, 1.6, fc="#cfe6f9", ec="none"))
    ax.add_patch(Rectangle((-4, 1.6), 8, 2.9, fc="#cfe6f9", ec="none"))
    ax.text(4.6, 3.0, "150 µL", fontsize=6.5, color=INK2, va="center")
    # the electrode cap: skirt, body, steel disc
    xs = [-13, -13, -9, -9, 9, 9, 13, 13, -13]
    zs = [6, 10, 10, 22, 22, 10, 10, 6, 6]
    ax.fill(xs, zs, fc="#f7f1ee", ec=ORANGE, lw=1.2)
    ax.add_patch(Rectangle((-6, 22), 12, 1.2, fc="#777", ec="none"))
    ax.text(7, 22.6, "steel disc for the magnet", fontsize=6.5, color=INK2, va="center")
    for sgn in (-1, 1):  # pogo pins to the pads
        ax.plot([sgn * 11, sgn * 11], [6.6, 10], color=INK, lw=1.2)
    ax.text(-11, 11, "pogo pins\nto RE / CE pads", fontsize=6, color=INK2, ha="center", va="bottom")
    ax.add_patch(Rectangle((-1.0, 1.5), 2.0, 20.5, fc="#eeeeea", ec=INK2, lw=0.8))
    ax.text(1.6, 16, "leak-free Ag/AgCl,\n2 mm", fontsize=6.5, color=INK2, va="center")
    for z in (2.4, 3.2, 4.0):
        ax.plot([-2.6, 2.6], [z, z], color="#777", lw=1.2)
    ax.plot([2.6, 2.6], [2.4, 10], color="#777", lw=1.2)
    ax.text(3.2, 8.5, "Pt coil", fontsize=6.5, color=INK2, va="center")
    ax.text(0, 25, "the P20 tip visits the same 8 mm bore while the cap is off", ha="center", fontsize=6.5, color=INK2)
    ax.set_xlim(-18, 24)
    ax.set_ylim(-13, 30)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(-18, 29.5, "C  One station, section, cap on", fontsize=10, fontweight="bold", color=INK, va="top")


def main():
    summary = check()
    (HERE / "deck-layout-check.json").write_text(json.dumps(summary, indent=1) + "\n")
    fig = plt.figure(figsize=(15, 8.6), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1.1, 1], wspace=0.12, hspace=0.25)
    draw_top(fig.add_subplot(gs[:, 0]))
    draw_side(fig.add_subplot(gs[0, 1]))
    draw_well(fig.add_subplot(gs[1, 1]))
    fig.text(0.5, 0.012,
             f"Proposal in the CubOS deck frame of Ben's 2026-10-02 calibration. Static tool-shadow check: "
             f"{summary['events_checked']} tool-down events, {summary['events_with_problems']} with a collision. Re-jog every coordinate before use.",
             ha="center", fontsize=8, color=INK2)
    fig.savefig(HERE / "deck-layout.png", dpi=150, facecolor=SURFACE, bbox_inches="tight")
    print(json.dumps({k: v for k, v in summary.items() if k != "events"}, indent=1))
    for r in summary["events"]:
        if r["problems"]:
            print("PROBLEM", r["event"], r["problems"])


if __name__ == "__main__":
    main()
