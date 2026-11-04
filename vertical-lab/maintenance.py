"""Getting a tray, or what is on it, out of the VLM for maintenance, with the backup rail in front of the opening (#303).

    python3 maintenance.py        # -> out/maintenance_access.png, out/maintenance_access.json

A plan and a side view at the opening, to scale. The geometry is read from the scene modules' own constants (vlm.py,
instruments.py's RAIL, line.py, animate.py, services.py, warehouse.py) by parsing their source, so the drawing follows
the models without loading CadQuery or any meshes.

Kardex's own routes for heavy goods (Shuttle XP brochure): "With the full tray extraction device, a tray is placed in
front of the access opening for loading and unloading purposes. This can be loaded onto the optional transport cart";
and "up to six access openings placed on the front or rear side of the unit". Kardex publishes no size for the
extraction device or the cart, so the drawing shows only the tray itself pulled clear of the opening: the least floor
that extraction can need. Everything marked "estimate" is ours.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def consts(name: str, **given) -> SimpleNamespace:
    """The module-level constants of a sibling module, evaluated from its source: plain literals and arithmetic on
    constants already found (and on the namespaces passed in). Anything else (functions, CadQuery) is skipped."""
    ns = dict(given)
    for node in ast.parse((HERE / name).read_text()).body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            val = eval(compile(ast.Expression(node.value), name, "eval"), {"__builtins__": {"dict": dict}}, ns)
        except Exception:
            continue
        for t in node.targets:
            if isinstance(t, ast.Name):
                ns[t.id] = val
            elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
                for e, v in zip(t.elts, val):
                    ns[e.id] = v
    return SimpleNamespace(**ns)


V = consts("vlm.py")
P = consts("props.py")
A = consts("animate.py", V=V, P=P)
I = consts("instruments.py")
L = consts("line.py", A=A, V=V, I=I)
S = consts("services.py", V=V, I=I)
W = consts("warehouse.py", line=L, A=A, V=V, P=P)

# ------------------------------------------------------------------------------------------------ the geometry
R = I.RAIL
FACE_F = L.Y_FACE                              # -1562: the cladding's front face
FACE_R = -FACE_F                               # +1562: the back
X_OUT = V.UNIT_W / 2 + V.SKIN
TRAY_F = (V.Y_FRONT - V.TRAY_D / 2, V.Y_FRONT + V.TRAY_D / 2)          # the tray at the front opening, y
TRAY_R = (V.Y_REAR - V.TRAY_D / 2, V.Y_REAR + V.TRAY_D / 2)            # the same at a rear opening
Z_TRAY = V.Z_OPEN + V.T_FLOOR                  # top of the presented tray's floor
RAIL_Y = L.RAIL_Y
BEAM = (RAIL_Y - R["beam_w"] / 2, RAIL_Y + R["beam_w"] / 2)
Z_BEAM_TOP = R["top"] - R["car_t"] - 30.0      # as instruments.rail(): z1
Z_BEAM_BOT = Z_BEAM_TOP - R["beam_h"]
PLATE = 202.5                                  # half the legs' 405 mm floor plates (instruments.rail)
CHAIN = (BEAM[1], BEAM[1] + 90.0)              # the drag-chain tray on the VLM's side of the beam
CAR = (RAIL_Y - R["car_w"] / 2, RAIL_Y + R["car_w"] / 2)
MOTOR_Y0 = RAIL_Y - R["car_w"] / 2 - 115.0     # the gearmotor hangs off the carriage's outer edge
RAIL_NEAR = max(CHAIN[1], RAIL_Y + PLATE)      # the rail's edge nearest the VLM
RAIL_FAR = RAIL_Y - PLATE                      # its farthest fixed point (a leg's plate)
RAIL_LEN = L.RAIL_X[1] - L.RAIL_X[0]
RC = sum(L.RAIL_X) / 2
N_LEGS = max(2, int(round(RAIL_LEN / R["leg_pitch"])) + 1)
LEGS_X = [RC - RAIL_LEN / 2 + 150 + i * (RAIL_LEN - 300) / (N_LEGS - 1) for i in range(N_LEGS)]
EXTRACT = V.TRAY_D + (TRAY_F[0] - FACE_F)      # travel that takes the tray's back edge clear of the cladding
OUT_F = (FACE_F - V.TRAY_D, FACE_F)            # the tray, fully out in front: the least floor extraction needs
OUT_R = (FACE_R, FACE_R + V.TRAY_D)
RACK_Y = [y0 for (x0, y0, n, along) in W.RACKS if along == "x"][0]      # warehouse.py: pallet racks behind the VLM
DOCK_Y = V.Y_FRONT + S.PLATE_Y                 # the bay's dock (services.py): the plate's centre along y
# a rear opening at the front one's height takes the rear column's positions across its mouth, as the front one does
# (vlm.py has no front slot below F1): any slot whose tray, goods and clearance reach into [Z_SILL, Z_OPEN_TOP]
HOMES = {**A.HOME, **{k: v[0] for k, v in L.EXTRA.items()}}             # tray -> slot (animate.HOME, line.EXTRA)
LOST = sorted(k for k, (y, z) in V.SLOTS.items() if y == V.Y_REAR and z < V.Z_OPEN_TOP
              and z + V.T_FLOOR + V.MAX_GOODS_H + V.GOODS_CLEAR > V.Z_SILL)

NUMBERS = {
    "vlm_front_face_y_mm": FACE_F,
    "opening_width_mm": V.OPEN_W, "access_table_z_mm": V.Z_SILL, "header_z_mm": V.Z_OPEN_TOP,
    "tray_at_opening_mm": {"front_edge_behind_face": round(TRAY_F[0] - FACE_F, 1),
                           "back_edge_behind_face": round(TRAY_F[1] - FACE_F, 1), "floor_z": Z_TRAY},
    "rail": {"centre_y": RAIL_Y, "x_extent": list(L.RAIL_X), "legs_x": [round(x, 1) for x in LEGS_X],
             "leg_in_front_of_opening_x": [round(x, 1) for x in LEGS_X if abs(x) < V.OPEN_W / 2 + PLATE],
             "nearest_to_face_mm": round(FACE_F - RAIL_NEAR, 2), "farthest_fixed_from_face_mm": round(FACE_F - RAIL_FAR, 2),
             "carriage_and_gearmotor_from_face_mm": round(FACE_F - MOTOR_Y0, 2),
             "beam_z_mm": [Z_BEAM_BOT, Z_BEAM_TOP], "carriage_top_z_mm": R["top"]},
    "reach_from_beam_outer_face_mm": {"tray_front_edge": round(TRAY_F[0] - BEAM[0], 2),
                                      "tray_back_edge": round(TRAY_F[1] - BEAM[0], 2)},
    "full_extraction": {"tray_travel_out_mm": round(EXTRACT, 1),
                        "least_floor_in_front_of_face_mm": V.TRAY_D,
                        "overlaps_rail_mm": round(min(OUT_F[1], RAIL_NEAR) - max(OUT_F[0], RAIL_FAR), 1),
                        "note": "the tray alone; Kardex publishes no size for the extraction device or the cart"},
    "rear_opening": {"tray_out_behind_mm": [FACE_R, FACE_R + V.TRAY_D],
                     "rear_slots_lost_at_the_front_openings_height": LOST,
                     "trays_in_them": sorted(t for t, k in HOMES.items() if k in LOST),
                     "warehouse_racks_behind_face_mm": RACK_Y - FACE_R},
    "bay_dock_y_mm": DOCK_Y,
    "sources": {
        "kardex_extraction": "Kardex Remstar Shuttle XP brochure, p.6: 'With the full tray extraction device, a tray is "
                             "placed in front of the access opening for loading and unloading purposes. This can be "
                             "loaded onto the optional transport cart'; options list: automatic and manual tray "
                             "extraction, transit trolley, factory-fitted crane, up to six access openings per unit",
        "kardex_rear": "Same brochure, p.6: 'up to six access openings placed on the front or rear side of the unit'; "
                       "Kardex Shuttle brochure (2021), p.5: 'an access opening on the front and rear of the device'",
        "geometry": "vlm.py, instruments.RAIL and rail(), line.py (RAIL_Y, RAIL_X, PARK_X), services.py (the dock), "
                    "warehouse.py (RACKS)",
    },
}

# ------------------------------------------------------------------------------------------------ the drawing
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
BAD, GOOD = "#d03b3b", "#0ca30c"                # status: critical / good, always with a label and a hatch
SKIN, TRAY_C, RAIL_C, ARM_C = "#cbd0cc", "#6b7380", "#1f3873", "#c9ced6"


def draw():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(15.0, 7.4), gridspec_kw=dict(width_ratios=[1.0, 0.92]))
    fig.patch.set_facecolor(SURF)
    lead = dict(arrowstyle="-", color=INK2, lw=0.8)

    def rect(a, x0, y0, x1, y1, **kw):
        a.add_patch(Rectangle((min(x0, x1), min(y0, y1)), abs(x1 - x0), abs(y1 - y0), **kw))

    # ======================================================================== plan
    ax.set_facecolor(SURF)
    rect(ax, -X_OUT, FACE_F, X_OUT, FACE_R, fc=SKIN, ec=INK2, lw=1.0, zorder=1)
    for y in (-515.0, 515.0):                   # the column / extractor boundaries
        ax.plot([-X_OUT, X_OUT], [y, y], color=INK2, lw=0.6, ls=(0, (4, 3)), zorder=2)
    ax.text(0, 0, "extractor (the lift)", ha="center", va="center", color=INK2, fontsize=8.5)
    ax.text(-3280, 450, "Kardex Shuttle XP 500\n2780 x 3074 mm, plus\nits cladding", ha="left", va="center",
            color=INK2, fontsize=8.5)
    rect(ax, -V.TRAY_W / 2, TRAY_F[0], V.TRAY_W / 2, TRAY_F[1], fc="none", ec=TRAY_C, lw=1.6, zorder=3)
    ax.text(0, V.Y_FRONT + 60, "tray at the front opening", ha="center", va="center", color=INK, fontsize=8.5)
    ax.plot([-V.OPEN_W / 2, V.OPEN_W / 2], [FACE_F, FACE_F], color=INK, lw=3.2, zorder=4, solid_capstyle="butt")
    # the bay's dock: the coupling in the right-hand side wall (services.py)
    rect(ax, V.TRAY_W / 2, DOCK_Y - S.PLATE_L / 2, V.TRAY_W / 2 + 70, DOCK_Y + S.PLATE_L / 2, fc=INK, ec=INK, zorder=5)
    ax.annotate("tray service dock (round 4's coupling)\nin the bay's side wall: inside the\n"
                "VLM, so the rail doesn't affect it", xy=(V.TRAY_W / 2 + 70, DOCK_Y), xytext=(1560, -250),
                fontsize=8, color=INK, arrowprops=lead, zorder=6)
    # option: a rear opening, and the tray fully out behind
    ax.plot([-V.OPEN_W / 2, V.OPEN_W / 2], [FACE_R, FACE_R], color=GOOD, lw=3.2, zorder=4, solid_capstyle="butt")
    rect(ax, -V.TRAY_W / 2, TRAY_R[0], V.TRAY_W / 2, TRAY_R[1], fc="none", ec=GOOD, lw=1.2, ls="--", zorder=3)
    ax.text(0, V.Y_REAR + 80, "tray at a rear opening", ha="center", va="center", color=INK, fontsize=8.5)
    rect(ax, -V.TRAY_W / 2, OUT_R[0], V.TRAY_W / 2, OUT_R[1], fc=GOOD, alpha=0.16, ec=GOOD, lw=1.2, hatch="\\\\",
         zorder=3)
    ax.text(0, (OUT_R[0] + OUT_R[1]) / 2, "OPTION: a rear opening for service.\nThe tray fully out behind it: "
            f"{V.TRAY_D:.0f} mm\nof floor, then the cart. Nothing in the way", ha="center", va="center", color=INK,
            fontsize=8.5, zorder=6)
    # the rail, as line.py places it
    x0, x1 = -3400, 3400
    for lx in LEGS_X:
        if x0 < lx < x1:
            rect(ax, lx - PLATE, RAIL_Y - PLATE, lx + PLATE, RAIL_Y + PLATE, fc=RAIL_C, alpha=0.55, ec=RAIL_C, zorder=4)
    rect(ax, x0, BEAM[0], x1, BEAM[1], fc=RAIL_C, ec=RAIL_C, zorder=5)
    rect(ax, x0, CHAIN[0], x1, CHAIN[1], fc=RAIL_C, alpha=0.45, ec=RAIL_C, lw=0.6, zorder=5)
    px = L.PARK_X
    rect(ax, px - R["car_l"] / 2, CAR[0], px + R["car_l"] / 2, CAR[1], fc="#2d4f9a", ec=INK, lw=0.8, zorder=6)
    rect(ax, px - 60, MOTOR_Y0, px + 60, CAR[0], fc="#202022", ec=INK, lw=0.8, zorder=6)
    ax.add_patch(Circle((px, RAIL_Y), 95.0, fc=ARM_C, ec=INK, lw=0.8, zorder=7))
    ax.annotate("UR10e on the carriage,\nparked at the opening (line.py)", xy=(px + 120, RAIL_Y - 80),
                xytext=(1560, -1330), fontsize=8, color=INK, arrowprops=lead, zorder=8)
    ax.annotate("a leg of the rail\nin front of the opening", xy=(LEGS_X[2] - 150, RAIL_Y + PLATE),
                xytext=(-3280, -1200), fontsize=8, color=INK, arrowprops=lead, zorder=8)
    ax.text(-3280, RAIL_Y, "Vention rail", color=SURF, fontsize=8, va="center", ha="left", zorder=8,
            fontweight="bold")
    # Kardex's full tray extraction at the front: the tray alone, pulled clear
    rect(ax, -V.TRAY_W / 2, OUT_F[0], V.TRAY_W / 2, OUT_F[1], fc=BAD, alpha=0.14, ec=BAD, lw=1.4, hatch="//",
         zorder=8)
    ax.text(-3280, OUT_F[0] - 120, "CONFLICT: Kardex's full tray extraction brings the tray out here, onto a table\n"
            f"and then a transport cart: {V.TRAY_D:.0f} mm of floor in front of the opening. The rail runs through it.",
            color=BAD, fontsize=8.5, va="top", ha="left", zorder=9, fontweight="bold")
    ax.set_xlim(-3400, 3400)
    ax.set_ylim(-3200, 2750)
    ax.set_aspect("equal")
    ax.set_title("Plan of the rail layout. The arm's side, the front, is at the bottom", color=INK,
                 fontsize=10.5, loc="left")
    ax.set_xlabel("x, mm")
    ax.set_ylabel("y, mm")

    # ======================================================================== side view at the opening
    bx.set_facecolor(SURF)
    bx.axhline(0, color=INK2, lw=1.2)
    zt, yr = 2600.0, 200.0
    rect(bx, FACE_F + V.SKIN, 140, yr, zt, fc=SKIN, alpha=0.35, ec="none")
    rect(bx, FACE_F, 140, FACE_F + V.SKIN, V.Z_SILL, fc=SKIN, ec=INK2, lw=0.8)                  # below the opening
    rect(bx, FACE_F, V.Z_OPEN_TOP, FACE_F + V.SKIN, zt, fc=SKIN, ec=INK2, lw=0.8)              # the header and above
    rect(bx, FACE_F, 0, yr, 140, fc="#3a3d42", ec=INK2, lw=0.6)                               # the plinth
    bx.text(FACE_F + 70, zt - 60, "VLM, cut at the\nopening's centre", color=INK2, fontsize=8, va="top")
    bx.plot([V.Y_SHUTTER, V.Y_SHUTTER], [V.Z_SILL, V.Z_OPEN_TOP], color="#7096a4", lw=2.0)
    bx.text(V.Y_SHUTTER + 40, V.Z_OPEN_TOP + 30, "shutter", color=INK2, fontsize=8, va="bottom")
    rect(bx, TRAY_F[0], V.Z_OPEN, TRAY_F[1], V.Z_OPEN + V.T_RIM, fc=TRAY_C, ec=INK, lw=0.8)
    rect(bx, TRAY_F[0], Z_TRAY, TRAY_F[1], Z_TRAY + V.MAX_GOODS_H, fc="none", ec=INK2, lw=0.8, ls=(0, (3, 2)))
    bx.text((TRAY_F[0] + TRAY_F[1]) / 2, Z_TRAY + V.MAX_GOODS_H / 2, "tray at the opening,\nits 727.5 mm\n"
            "product height", ha="center", va="center", color=INK, fontsize=8)
    # the rail; the leg at x = -590 seen beyond the cut
    rect(bx, RAIL_Y - PLATE, 0, RAIL_Y + PLATE, 20, fc=RAIL_C, alpha=0.55, ec=RAIL_C)
    rect(bx, RAIL_Y - 123.75, 20, RAIL_Y + 123.75, Z_BEAM_BOT, fc=RAIL_C, alpha=0.55, ec=RAIL_C)
    rect(bx, BEAM[0], Z_BEAM_BOT, BEAM[1], Z_BEAM_TOP + 15, fc=RAIL_C, ec=RAIL_C)
    rect(bx, CHAIN[0], Z_BEAM_BOT + 20, CHAIN[1], Z_BEAM_BOT + 70, fc=RAIL_C, alpha=0.45, ec=RAIL_C)
    bx.text(RAIL_Y, (Z_BEAM_BOT + Z_BEAM_TOP) / 2, "rail", ha="center", va="center", color=SURF, fontsize=8,
            fontweight="bold")
    bx.text(-3080, zt - 60, f"The carriage and the arm have driven off along\nthe rail. Its beam, {Z_BEAM_BOT:.0f}-"
            f"{Z_BEAM_TOP + 15:.0f} mm high,\nstays between the person and the tray.", ha="left", va="top",
            color=INK, fontsize=8)
    # a person standing against the beam (a stand-in figure, 1750 mm)
    yp = BEAM[0] - 145.0
    fig_c = "#a7adb3"
    bx.add_patch(Circle((yp, 1640), 105, fc=fig_c, ec=INK2))
    rect(bx, yp - 125, 900, yp + 125, 1520, fc=fig_c, ec=INK2)
    rect(bx, yp - 105, 0, yp + 105, 900, fc=fig_c, ec=INK2)
    bx.plot([yp + 60, yp + 600], [1420, 1060], color=fig_c, lw=9, solid_capstyle="round")

    def dim(a, ya, yb, z, text, color=INK, dz=40):
        a.annotate("", xy=(ya, z), xytext=(yb, z), arrowprops=dict(arrowstyle="<->", color=color, lw=0.9))
        a.plot([ya, ya], [z - 60, z + 60], color=color, lw=0.6)
        a.plot([yb, yb], [z - 60, z + 60], color=color, lw=0.6)
        a.text((ya + yb) / 2, z + dz, text, ha="center", va="bottom", color=color, fontsize=8,
               bbox=dict(fc=SURF, ec="none", pad=0.6))
    dim(bx, BEAM[0], TRAY_F[0], 1860, f"{TRAY_F[0] - BEAM[0]:.0f} mm to the tray's front edge")
    dim(bx, BEAM[0], TRAY_F[1], 2130, f"{TRAY_F[1] - BEAM[0]:.0f} mm to its back edge, over the beam")
    dim(bx, RAIL_FAR, FACE_F, -230, f"the rail fills {FACE_F - RAIL_NEAR:.0f}-{FACE_F - RAIL_FAR:.0f} mm "
        "in front of the face", dz=-190)
    bx.set_xlim(-3150, yr)
    bx.set_ylim(-420, zt + 50)
    bx.set_aspect("equal")
    bx.set_title("Side view at the opening. Front on the left", color=INK, fontsize=10.5, loc="left")
    bx.set_xlabel("y, mm")
    bx.set_ylabel("z, mm")
    fig.suptitle("Getting at a tray for maintenance, with the backup rail in front of the VLM", color=INK,
                 fontsize=12.5, x=0.01, ha="left")
    fig.text(0.01, 0.012, "Geometry from the scene modules (vlm.py, instruments.RAIL, line.py, services.py). Kardex "
             "publishes no size for its extraction table or transport cart, so the hatched areas are the tray alone: "
             "the least floor extraction can need.", color=INK2, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    OUT.mkdir(exist_ok=True)
    path = OUT / "maintenance_access.png"
    fig.savefig(path, dpi=130, facecolor=SURF)
    return path


if __name__ == "__main__":
    (OUT / "maintenance_access.json").write_text(json.dumps(NUMBERS, indent=1) + "\n")
    print(json.dumps({k: NUMBERS[k] for k in ("tray_at_opening_mm", "rail", "reach_from_beam_outer_face_mm",
                                               "full_extraction", "rear_opening", "bay_dock_y_mm")}, indent=1))
    print(draw())
