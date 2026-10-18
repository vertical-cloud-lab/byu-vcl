"""cad_section.png: the seated station cut through the well axis in the y = 0 plane (x to the
right, z up, both in the well frame W), sliced from the CAD solids, with the dimensions that
the bench and the simulation share.

    python plot_cad_section.py
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
META = json.loads((HERE / "cad_parts.json").read_text())
P = META["parameters"]
LT = P["lid_top"]

PARTS = [  # name, frame, colour
    ("coupon_20x20x6", "W", "#b89a8a"), ("well_lid", "W", "#e9a47c"), ("face_oring_006", "W", "#1d1d1d"),
    ("lid_pads", "W", "#c77a3a"), ("electrode_cap", "C", "#efe9e2"), ("electrode_carrier", "C", "#9c9b97"),
    ("steel_disc", "C", "#8d9196"), ("ag_agcl_ref", "C", "#e9e6df"), ("pt_coil", "C", "#9ea3a8"), ("cap_pogo_pins", "C", "#c9a64a"),
]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"


def slice_y0(shape):
    """Faces of the solid cut by the plane y = 0, as matplotlib paths in (x, z)."""
    slab = cq.Solid.makeBox(200, 0.002, 200, cq.Vector(-100, -0.001, -100))
    cut = shape.intersect(slab)
    paths = []
    for f in cut.Faces():
        n = f.normalAt()
        if abs(n.y) < 0.99 or f.Center().y < 0:
            continue
        verts, codes = [], []
        for w in [f.outerWire()] + f.innerWires():
            pts = []
            for e in w.Edges():
                k = 24 if e.geomType() != "LINE" else 2
                seg = [e.positionAt(t / (k - 1)) for t in range(k)]
                if pts and (seg[0] - pts[-1]).Length > 1e-6 and (seg[-1] - pts[-1]).Length < (seg[0] - pts[-1]).Length:
                    seg = seg[::-1]
                pts.extend(seg)
            xy = [(p.x, p.z) for p in pts]
            verts += xy + [xy[0]]
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 1) + [MPath.CLOSEPOLY]
        paths.append(MPath(verts, codes))
    return paths


def dim(ax, x0, y0, x1, y1, text, off=(0, 0), ha="center"):
    ax.annotate("", xy=(x0, y0), xytext=(x1, y1), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], text, fontsize=7.5, color=INK, ha=ha, va="center",
            bbox=dict(fc="#fcfcfb", ec="none", pad=0.6))


def main():
    fig, ax = plt.subplots(figsize=(13, 9.6), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    # the liquid, 150 uL to about 4.5 mm with the reference in (sim_well.py)
    fo = META["face_oring_section_rz"]
    import math
    c_in = META["face_oring_contact_on_metal_r"][0]
    for sgn in (-1, 1):
        semi = [(c_in + 0.70 * math.cos(math.radians(t)), 0.70 + 0.70 * math.sin(math.radians(t))) for t in range(-90, -271, -10)]
        poly = [(0, 0), (c_in, 0)] + semi + [(1.45, 1.40), (1.45, 1.60), (4.0, 1.60), (4.0, 4.5), (1.0, 4.5), (1.0, 3.0), (0, 3.0)]
        ax.fill([sgn * r for r, z in poly], [z for r, z in poly], color="#cfe6f9", lw=0)
    for name, frame, col in PARTS:
        shape = cq.importers.importStep(str(HERE / f"{name}.step")).val()
        if frame == "C":
            shape = shape.translate(cq.Vector(0, 0, LT))
        for pth in slice_y0(shape):
            ax.add_patch(PathPatch(pth, fc=col, ec=INK2 if name != "face_oring_006" else "#1d1d1d", lw=0.5))
    ax.set_aspect("equal")
    ax.set_xlim(-16.5, 21.5)
    ax.set_ylim(-7, 24.5)
    ax.axhline(0, color=MUTED, lw=0.4, ls=":")
    ax.axvline(0, color=MUTED, lw=0.4, ls=":")
    # dimensions
    dim(ax, 15.0, 0, 15.0, LT, "lid 6.0", off=(1.7, 0))
    dim(ax, 15.0, LT, 15.0, LT + P["boss_h"], "boss 4.0", off=(1.9, 0))
    dim(ax, 15.0, LT, 15.0, LT + P["cap_top"], "", off=(0, 0))
    ax.text(16.6, LT + 12.5, "cap 16.0 to the\nmagnet contact", fontsize=7.5, color=INK, va="center")
    dim(ax, -4.0, 4.9, 4.0, 4.9, "bore 8.0", off=(0, 0.45))
    dim(ax, -8.0, 10.6, 8.0, 10.6, "boss 16.0 (cap bore 16.24)", off=(0, 0.5))
    dim(ax, -1.45, -1.0, 1.45, -1.0, "O-ring ID 2.90", off=(0, -0.55))
    dim(ax, -c_in, -2.6, c_in, -2.6, f"wetted to r {c_in:.2f}: {math.pi * (c_in / 10) ** 2:.3f} cm²", off=(0, -0.55))
    dim(ax, -3.65, -4.2, 3.65, -4.2, "counterbore 7.30 x 1.40", off=(0, -0.55))
    dim(ax, 0.6, 0, 0.6, 3.0, "3.0", off=(0.55, 0))
    ax.text(-1.2, 3.6, "Ag/AgCl\n2.0", fontsize=7, color=INK, ha="right")
    ax.text(3.1, 2.0, "Pt coil r 2.625,\nz 2.4-4.0", fontsize=7, color=INK, ha="left")
    ax.text(11, LT + 1.6, "CE pin\non pad", fontsize=7, color=INK, ha="center")
    ax.text(-11, LT + 1.6, "RE pin\non pad", fontsize=7, color=INK, ha="center")
    ax.text(0, LT + P["cap_top"] + 0.9, "steel disc 25.4 x 1.0 on the vial cap's 25.4 recess; 28 mm flange as on the vial cap",
            fontsize=7.5, color=INK, ha="center")
    ax.text(4.3, 4.9, "~150 µL\nto z 4.5", fontsize=7, color="#256abf", ha="left", va="center")
    ax.text(-15.8, -6.4, "coupon 20 x 20 x 6 (face at z 0), on a WE spring pin from below", fontsize=7.5, color=INK2)
    ax.text(21.3, 3.2, "pins drawn free (1.0 mm out);\nseated they compress 0.93 mm\nonto the 0.07 mm foil pads.\n\nThe carrier's three coil legs\n(30, 150, 270 deg) and the two\nhold-down magnets (60, 240 deg)\nare out of this plane.",
            fontsize=7.2, color=INK2, ha="right", va="center")
    ax.set_xlabel("x through the well axis, mm (W frame)", fontsize=9, color=INK2)
    ax.set_ylabel("z above the coupon face, mm", fontsize=9, color=INK2)
    ax.tick_params(labelsize=8, colors=MUTED)
    for s in ax.spines.values():
        s.set_color("#e1e0d9")
    ax.set_title("One copper station, seated, cut at y = 0 (sliced from the CAD). Recommended cap: 0.12 mm clearance skirt, no O-ring",
                 fontsize=10, color=INK, loc="left")
    fig.savefig(HERE / "cad_section.png", dpi=130, facecolor="#fcfcfb", bbox_inches="tight")
    print("cad_section.png")


if __name__ == "__main__":
    main()
