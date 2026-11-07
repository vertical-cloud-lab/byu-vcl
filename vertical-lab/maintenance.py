"""Getting a tray, or what is on it, out of the VLM for maintenance, with the mobile base at the opening (#303).

    python3 maintenance.py        # -> out/maintenance_access.png, out/maintenance_access.json

A plan and a side view at the opening, to scale. The geometry is read from the scene modules' own constants (vlm.py,
animate.py, props.py, services.py, warehouse.py, setup_lab.py) by parsing their source, so the drawing follows the
models without loading CadQuery or any meshes.

Mobile manipulator only (Sterling, PR #318: "Just stick with the mobile manipulator setup"): nothing fixed stands in
front of the opening. The MiR250 docks there to work and drives off when a tray has to come out, so Kardex's own route
for heavy goods works at the front. Kardex (Shuttle XP brochure): "With the full tray extraction device, a tray is placed
in front of the access opening for loading and unloading purposes. This can be loaded onto the optional transport
cart". Kardex publishes no size for the extraction device or the cart, so the drawing shows only the tray itself pulled
clear of the opening: the least floor that extraction can need. Everything marked "estimate" is ours.
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
S = consts("services.py", V=V, I=I)
SL = consts("setup_lab.py", V=V, A=A, P=P)

# ------------------------------------------------------------------------------------------------ the geometry
FACE_F = -V.UNIT_D / 2 - V.SKIN                # -1562: the cladding's front face
X_OUT = V.UNIT_W / 2 + V.SKIN
TRAY_F = (V.Y_FRONT - V.TRAY_D / 2, V.Y_FRONT + V.TRAY_D / 2)          # the tray at the front opening, y
Z_TRAY = V.Z_OPEN + V.T_FLOOR                  # top of the presented tray's floor
EXTRACT = V.TRAY_D + (TRAY_F[0] - FACE_F)      # travel that takes the tray's back edge clear of the cladding
OUT_F = (FACE_F - V.TRAY_D, FACE_F)            # the tray, fully out in front: the least floor extraction needs
MIR = (A.AMR_XY[0] - P.MIR["L"] / 2, A.AMR_XY[0] + P.MIR["L"] / 2,
       A.AMR_XY[1] - P.MIR["W"] / 2, A.AMR_XY[1] + P.MIR["W"] / 2)     # the MiR250 docked at the opening
POST = tuple(SL.TARGET_AT["vlm"])              # its AprilTag target's post (setup_lab.TARGET_AT)
POST_FOOT = 150.0                              # half the post's foot plate (warehouse.py)
X_NEXT = V.SHUTTLE_X[2] - X_OUT                # the second Shuttle's left side
DOCK_Y = V.Y_FRONT + S.PLATE_Y                 # the bay's dock (services.py): the plate's centre along y

NUMBERS = {
    "vlm_front_face_y_mm": FACE_F,
    "opening_width_mm": V.OPEN_W, "access_table_z_mm": V.Z_SILL, "header_z_mm": V.Z_OPEN_TOP,
    "tray_at_opening_mm": {"front_edge_behind_face": round(TRAY_F[0] - FACE_F, 1),
                           "back_edge_behind_face": round(TRAY_F[1] - FACE_F, 1), "floor_z": Z_TRAY},
    "mir250_docked_mm": {"x": [MIR[0], MIR[1]], "y": [MIR[2], MIR[3]],
                         "in_front_of_face": [round(FACE_F - MIR[3], 1), round(FACE_F - MIR[2], 1)],
                         "cabinet_top_z": P.MIR["H"] + P.CAB_H, "arm_base_z": P.AMR_TOP,
                         "note": "it drives off before a tray is pulled out (warehouse.py: a dock, not a fixture)"},
    "target_post_mm": {"centre": [round(POST[0], 1), round(POST[1], 1)],
                       "clear_of_the_tray_side_mm": round(abs(POST[0]) - V.TRAY_W / 2 - 25.0, 1),
                       "note": "the VLM's AprilTag post stands outside the opening's width, beside the left post"},
    "full_extraction": {"tray_travel_out_mm": round(EXTRACT, 1), "least_floor_in_front_of_face_mm": V.TRAY_D,
                        "fixed_things_in_that_floor": [],
                        "note": "the tray alone; Kardex publishes no size for the extraction device or the cart"},
    "second_shuttle_left_side_x_mm": X_NEXT,
    "bay_dock_y_mm": DOCK_Y,
    "sources": {
        "kardex_extraction": "Kardex Remstar Shuttle XP brochure, p.6: 'With the full tray extraction device, a tray is "
                             "placed in front of the access opening for loading and unloading purposes. This can be "
                             "loaded onto the optional transport cart'; options list: automatic and manual tray "
                             "extraction, transit trolley, factory-fitted crane, up to six access openings per unit",
        "mir250": "MiR250 Specifications (2023-06-28): 800 x 580 x 300 mm (warehouse.py)",
        "geometry": "vlm.py, animate.py (AMR_XY), props.py (MIR, CAB_H), services.py (the dock), setup_lab.py "
                    "(TARGET_AT, the second Shuttle)",
    },
}

# ------------------------------------------------------------------------------------------------ the drawing
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
GOOD = "#0ca30c"
SKIN, TRAY_C, MIR_C, ARM_C = "#cbd0cc", "#6b7380", "#3a3d42", "#c9ced6"


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
    rect(ax, -X_OUT, FACE_F, X_OUT, -FACE_F, fc=SKIN, ec=INK2, lw=1.0, zorder=1)
    rect(ax, X_NEXT, FACE_F, X_NEXT + 2 * X_OUT, -FACE_F, fc=SKIN, ec=INK2, lw=1.0, alpha=0.6, zorder=1)
    ax.text(X_NEXT + 120, 1200, "second\nShuttle", ha="left", va="center", color=INK2, fontsize=8.5)
    for y in (-515.0, 515.0):                   # the column / extractor boundaries
        ax.plot([-X_OUT, X_OUT], [y, y], color=INK2, lw=0.6, ls=(0, (4, 3)), zorder=2)
    ax.text(0, 0, "extractor (the lift)", ha="center", va="center", color=INK2, fontsize=8.5)
    rect(ax, -V.TRAY_W / 2, TRAY_F[0], V.TRAY_W / 2, TRAY_F[1], fc="none", ec=TRAY_C, lw=1.6, zorder=3)
    ax.text(0, V.Y_FRONT + 60, "tray at the front opening", ha="center", va="center", color=INK, fontsize=8.5)
    ax.plot([-V.OPEN_W / 2, V.OPEN_W / 2], [FACE_F, FACE_F], color=INK, lw=3.2, zorder=4, solid_capstyle="butt")
    rect(ax, V.TRAY_W / 2, DOCK_Y - S.PLATE_L / 2, V.TRAY_W / 2 + 70, DOCK_Y + S.PLATE_L / 2, fc=INK, ec=INK, zorder=5)
    ax.annotate("tray service dock (round 4's coupling)\nin the bay's side wall, inside the VLM",
                xy=(V.TRAY_W / 2 + 70, DOCK_Y), xytext=(1560, -250), fontsize=8, color=INK, arrowprops=lead, zorder=6)
    # Kardex's full tray extraction at the front: the tray alone, pulled clear
    rect(ax, -V.TRAY_W / 2, OUT_F[0], V.TRAY_W / 2, OUT_F[1], fc=GOOD, alpha=0.16, ec=GOOD, lw=1.4, hatch="\\\\",
         zorder=3)
    ax.text(0, (OUT_F[0] + OUT_F[1]) / 2 - 40, "OK: full tray extraction at the front. The tray comes out here,\n"
            f"onto a table and a cart: {V.TRAY_D:.0f} mm of floor, with nothing fixed in it", ha="center",
            va="center", color=INK, fontsize=8.5, zorder=9)
    # the MiR250 at its dock, dashed: it drives off first
    rect(ax, MIR[0], MIR[2], MIR[1], MIR[3], fc="none", ec=MIR_C, lw=1.2, ls=(0, (4, 2)), zorder=7)
    ax.add_patch(Circle((A.AMR_XY[0] + A.ARM_LOCAL[0], A.AMR_XY[1] + A.ARM_LOCAL[1]), 95.0, fc="none", ec=MIR_C,
                        lw=1.0, ls=(0, (4, 2)), zorder=7))
    ax.annotate("MiR250 + UR10e at its dock while it works;\nit drives off before a tray comes out",
                xy=(MIR[1], (MIR[2] + MIR[3]) / 2), xytext=(1100, -2900), fontsize=8, color=INK, arrowprops=lead,
                zorder=8)
    rect(ax, POST[0] - POST_FOOT, POST[1] - POST_FOOT, POST[0] + POST_FOOT, POST[1] + POST_FOOT, fc=INK, ec=INK,
         alpha=0.25, zorder=6)
    ax.add_patch(Circle(POST, 25.0, fc=INK, ec=INK, zorder=7))
    ax.annotate("AprilTag target on its post, outside\nthe opening's width: the tray passes it",
                xy=(POST[0] - 30, POST[1]), xytext=(-3300, -2900), fontsize=8, color=INK, arrowprops=lead, zorder=8)
    ax.set_xlim(-3400, X_NEXT + 900)
    ax.set_ylim(-3200, 2000)
    ax.set_aspect("equal")
    ax.set_title("Plan at the opening. The front is at the bottom", color=INK, fontsize=10.5, loc="left")
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
    bx.text((TRAY_F[0] + TRAY_F[1]) / 2, Z_TRAY + V.MAX_GOODS_H / 2, f"tray at the opening,\n{V.MAX_GOODS_H:g} mm "
            "of\nproduct height", ha="center", va="center", color=INK, fontsize=8)
    # the tray pulled out to the front, at the access table's height
    rect(bx, OUT_F[0], V.Z_OPEN, OUT_F[1], V.Z_OPEN + V.T_RIM, fc=GOOD, alpha=0.35, ec=GOOD, lw=0.8)
    rect(bx, OUT_F[0], Z_TRAY, OUT_F[1], Z_TRAY + V.MAX_GOODS_H, fc=GOOD, alpha=0.08, ec=GOOD, lw=0.8,
         ls=(0, (3, 2)))
    bx.text((OUT_F[0] + OUT_F[1]) / 2, Z_TRAY + V.MAX_GOODS_H + 60, "pulled out to the front\n(extraction device)",
            ha="center", va="bottom", color=INK, fontsize=8)
    # the MiR250 where it docks, dashed: gone while the tray is out
    rect(bx, MIR[2], 0, MIR[3], P.MIR["H"] + P.CAB_H, fc="none", ec=MIR_C, lw=1.0, ls=(0, (4, 2)))
    bx.text((MIR[2] + MIR[3]) / 2, 250, "MiR250\n(gone)", ha="center", va="bottom", color=MIR_C, fontsize=8)
    # a person standing at the tray's front edge (a stand-in figure, 1750 mm)
    yp = OUT_F[0] - 260.0
    fig_c = "#a7adb3"
    bx.add_patch(Circle((yp, 1640), 105, fc=fig_c, ec=INK2))
    rect(bx, yp - 125, 900, yp + 125, 1520, fc=fig_c, ec=INK2)
    rect(bx, yp - 105, 0, yp + 105, 900, fc=fig_c, ec=INK2)
    bx.plot([yp + 60, yp + 330], [1420, 1180], color=fig_c, lw=9, solid_capstyle="round")

    def dim(a, ya, yb, z, text, color=INK, dz=40):
        a.annotate("", xy=(ya, z), xytext=(yb, z), arrowprops=dict(arrowstyle="<->", color=color, lw=0.9))
        a.plot([ya, ya], [z - 60, z + 60], color=color, lw=0.6)
        a.plot([yb, yb], [z - 60, z + 60], color=color, lw=0.6)
        a.text((ya + yb) / 2, z + dz, text, ha="center", va="bottom", color=color, fontsize=8,
               bbox=dict(fc=SURF, ec="none", pad=0.6))
    dim(bx, OUT_F[0], FACE_F, -230, f"{V.TRAY_D:.0f} mm of floor for the tray, nothing fixed in it", dz=-190)
    bx.set_xlim(-3150, yr)
    bx.set_ylim(-420, zt + 50)
    bx.set_aspect("equal")
    bx.set_title("Side view at the opening. Front on the left", color=INK, fontsize=10.5, loc="left")
    bx.set_xlabel("y, mm")
    bx.set_ylabel("z, mm")
    fig.suptitle("Getting at a tray for maintenance: with the mobile base, the floor in front of the opening is free",
                 color=INK, fontsize=12.5, x=0.01, ha="left")
    fig.text(0.01, 0.012, "Geometry from the scene modules (vlm.py, animate.py, props.py, services.py, setup_lab.py). "
             "Kardex publishes no size for its extraction table or transport cart, so the hatched area is the tray "
             "alone: the least floor extraction can need.", color=INK2, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    OUT.mkdir(exist_ok=True)
    path = OUT / "maintenance_access.png"
    fig.savefig(path, dpi=130, facecolor=SURF)
    return path


if __name__ == "__main__":
    (OUT / "maintenance_access.json").write_text(json.dumps(NUMBERS, indent=1) + "\n")
    print(json.dumps({k: NUMBERS[k] for k in ("tray_at_opening_mm", "mir250_docked_mm", "target_post_mm",
                                               "full_extraction")}, indent=1))
    print(draw())
