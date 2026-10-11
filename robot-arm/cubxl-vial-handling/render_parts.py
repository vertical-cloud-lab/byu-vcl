"""Figures of the printable parts (#266): the assembly at the post grasp, sections through the grasp,
the offset plates, and the A1 mini beds.

    python parts.py && python checks.py && xvfb-run -a python render_parts.py
    # -> parts-assembly.png, grasp-sections.png, offset-plates.png, print-beds.png
"""

from __future__ import annotations

import io
import json
import math
import zipfile

import cadquery as cq
import matplotlib
import numpy as np
import pyvista as pv
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Dir, gp_Pln, gp_Pnt
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import checks as C  # noqa: E402
import parts as PT  # noqa: E402

HERE = PT.HERE
P = PT.P
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8983"
COL = {"deck": "#cfdbe4", "plate": "#c9b98f", "dowel": "#7d7d7d", "dock": "#e3d2ad", "carrier": "#8474a1",
       "post": "#d9480f", "vial": "#9dcfed", "insert": "#2a78d6", "pads": "#2b8a3e", "gripper": "#9a9a96",
       "carriage": "#6f6f6b", "bearing": "#444444"}


GRIPPER_BODY = ("motor housing", "linear rail", "finger plate", "back cover", "flange (proxy)")


def colour(name):
    if name in GRIPPER_BODY:
        return COL["gripper"]
    for k in ("plate", "dowel", "dock", "deck", "post", "vial", "pads", "insert", "carriage", "bearing"):
        if k in name:
            return COL[k]
    if "carrier" in name:
        return COL["carrier"]
    return COL["gripper"]


def mesh(shape, tol=0.2):
    v, f = shape.tessellate(tol, 0.3)
    v = np.array([(p.x, p.y, p.z) for p in v])
    f = np.asarray(f)
    return pv.PolyData(v, np.c_[np.full(len(f), 3), f].ravel())


def shot(meshes, cam, size=(1100, 820), edges=()):
    pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
    pl.set_background(SURFACE)
    for m, c, op in meshes:
        pl.add_mesh(m, color=c, opacity=op, smooth_shading=False, specular=0.2, ambient=0.2)
    for m in edges:
        pl.add_mesh(m.extract_feature_edges(feature_angle=35), color=INK2, line_width=1)
    pl.camera_position = cam
    pl.camera.view_angle = 28
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(return_img=True)
    pl.close()
    return Image.fromarray(img)


def assembly(parts):
    sc = C.scene(parts)
    _, states = PT.grip_states()
    R, t = C.grasp_pose((0, 0, P.groove_z))
    gp = C.posed(C.gripper_parts(parts, states["post"]["carriage_travel"]), R, t)
    world = [(mesh(s, 0.3 if k == "deck" else 0.15), colour(k), 1.0) for k, s in sc.items()]
    grip = [(mesh(s, 0.15), colour(k), 1.0) for k, s in gp.items() if "proxy" not in k]
    full = shot(world + grip, [(-360, 300, 250), (0, 10, 30), (0, 0, 1)])
    near = {k: v for k, v in sc.items() if k in ("handle post", "carrier half A", "carrier half B", "vial 4", "vial 6")}
    close = shot([(mesh(s, 0.1), colour(k), 0.35 if k.startswith("vial") else 1.0) for k, s in near.items()] +
                 [(mesh(s, 0.1), colour(k), 1.0) for k, s in gp.items() if k not in GRIPPER_BODY],
                 [(-150, -150, 135), (0, 0, 46), (0, 0, 1)])
    # exploded carrier: halves apart, post lifted, from below to show the pin hole and slot
    ex = [(mesh(parts["carrier_half_a"].translate(cq.Vector(0, 25, 0))), COL["carrier"], 1.0),
          (mesh(parts["carrier_half_b"].translate(cq.Vector(0, -25, 0))), COL["carrier"], 1.0),
          (mesh(parts["handle_post"].translate(cq.Vector(0, 0, 45))), COL["post"], 1.0)]
    below = shot(ex, [(-430, 210, -270), (0, 0, 20), (0, 0, 1)])
    dock = [(mesh(at), c, 1.0) for at, c in (
        (C.at_end(parts["dock_block"].translate(cq.Vector(0, 0, -P.floor_t)), "A").translate(cq.Vector(0, 0, 30)),
         COL["dock"]),
        (C.at_end(parts["plate_0"].translate(cq.Vector(0, 0, -P.floor_t)), "A"), COL["plate"]))]
    dock_img = shot(dock, [(-150, 210, 110), (0, 110, -5), (0, 0, 1)])
    W = full.width + close.width
    top = Image.new("RGB", (W, full.height), SURFACE)
    top.paste(full, (0, 0))
    top.paste(close, (full.width, 0))
    bot = Image.new("RGB", (W, below.height), SURFACE)
    bot.paste(below, (0, 0))
    bot.paste(dock_img, (below.width, 0))
    out = Image.new("RGB", (W, top.height + bot.height), SURFACE)
    out.paste(top, (0, 0))
    out.paste(bot, (0, top.height))
    out.save(HERE / "parts-assembly.png")


# ------------------------------------------------------------------ sections
def section(shape, origin, normal, xdir):
    """Edges of `shape` cut by a plane, as 2D polylines in (xdir, normal x xdir)."""
    o, n, x = (np.asarray(v, float) for v in (origin, normal, xdir))
    y = np.cross(n, x)
    sec = BRepAlgoAPI_Section(shape.wrapped, gp_Pln(gp_Pnt(*o), gp_Dir(*n)))
    sec.Build()
    lines = []
    for e in cq.Shape.cast(sec.Shape()).Edges():
        pts = np.array([e.positionAt(t).toTuple() for t in np.linspace(0, 1, 40)])
        lines.append(np.c_[(pts - o) @ x, (pts - o) @ y])
    return lines


def grasp_sections(parts):
    sc = C.scene(parts)
    _, states = PT.grip_states()
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.6), facecolor=SURFACE)
    cases = [("Handle post, closed: plan at the rib", 0.0, "post", (0, 0, P.groove_z), (0, 0, 1), (1, 0, 0)),
             ("Vial 6, closed: plan at the rib", PT.slot_y(6), "vial", (0, 0, P.groove_z), (0, 0, 1), (1, 0, 0)),
             ("Handle post, closed: section through its axis", 0.0, "post", (0, 0, 0), (0, -1, 0), (1, 0, 0))]
    for ax, (title, y, st, o, n, xd) in zip(axes, cases):
        R, t = C.grasp_pose((0, y, P.groove_z))
        gp = C.posed(C.gripper_parts(parts, states[st]["carriage_travel"]), R, t)
        shapes = {**{k: v for k, v in sc.items() if k.startswith(("vial", "handle", "carrier"))},
                  **{k: v for k, v in gp.items() if "insert" in k or "pads" in k}}
        for k, s in shapes.items():
            for ln in section(s, o, n, xd):
                ax.plot(ln[:, 0], ln[:, 1], color=colour(k), lw=1.3)
        ax.set_aspect("equal")
        ax.set_title(title, color=INK, fontsize=11, loc="left")
        ax.tick_params(colors=INK2, labelsize=8)
        for sp in ax.spines.values():
            sp.set_color(MUTED)
        if n == (0, 0, 1):
            ax.set_xlim(-34, 34)
            ax.set_ylim(y - 24, y + 24)
            ax.set_xlabel("across the carrier (mm)", color=INK2, fontsize=9)
            ax.set_ylabel("along the carrier (mm)", color=INK2, fontsize=9)
        else:
            ax.set_xlim(-34, 34)
            ax.set_ylim(14, 72)
            ax.set_xlabel("across the carrier (mm)", color=INK2, fontsize=9)
            ax.set_ylabel("height above the carrier's underside (mm)", color=INK2, fontsize=9)
    rib = PT.rib_numbers()["with pads"]
    axes[0].text(-33, -23, f"rib {rib['rib_into_groove']:.1f} mm into the groove,\n"
                           f"{rib['rib_to_groove_floor']:.1f} mm off its floor", fontsize=9, color=INK2, va="bottom")
    axes[1].text(-33, PT.slot_y(6) - 23, f"rib {rib['vial_clearance']:.1f} mm clear of the vial", fontsize=9,
                 color=INK2, va="bottom")
    handles = [plt.Line2D([], [], color=COL[k], lw=2) for k in ("insert", "pads", "post", "vial", "carrier")]
    fig.legend(handles, ["finger insert", "silicone pad", "handle post", "vial", "carrier"], loc="lower center",
               ncol=5, frameon=False, fontsize=9, labelcolor=INK2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(HERE / "grasp-sections.png", dpi=130, facecolor=SURFACE)
    plt.close(fig)


# ------------------------------------------------------------------ offset plates
def offset_plates(parts, info):
    fig, axes = plt.subplots(2, 7, figsize=(16, 6.6), facecolor=SURFACE)
    names = list(info["plates"])
    for ax, name in zip(axes.ravel(), names + [None]):
        if name is None:
            ax.axis("off")
            continue
        sh = parts[name]
        for ln in section(sh, (0, 0, -0.3), (0, 0, 1), (1, 0, 0)):
            ax.plot(ln[:, 0], ln[:, 1], color=INK2, lw=0.8)
        for ln in section(sh, (0, 0, -P.plate_t - 5), (0, 0, 1), (1, 0, 0)):
            ax.plot(ln[:, 0], ln[:, 1], color=MUTED, lw=0.8, ls="--")
        for x, y in P.dowels:
            ax.add_patch(plt.Circle((x, y), P.dowel_d / 2, fill=False, ec=MUTED, lw=0.8, ls=":"))
        pin = info["plates"][name]["pin_moves_to"]
        ax.plot([0], [0], "+", color=MUTED, ms=8)
        ax.plot([pin[0]], [pin[1]], "o", color=COL["post"], ms=4)
        ax.set_aspect("equal")
        ax.set_xlim(-28, 28)
        ax.set_ylim(-62, 12)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color(MUTED)
        ax.set_title(name.replace("plate_", ""), fontsize=10, color=INK)
        ax.text(0, 9, f"pin to ({pin[0]:+.2f}, {pin[1]:+.2f})", ha="center", fontsize=7, color=INK2)
    fig.suptitle("Offset plates, top view (block side up). Solid: top face and dowel holes. Dashed: the two "
                 "Cubware keys underneath. Dotted: dowels on the 0 plate. Orange dot: where the cone pin goes.",
                 fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(HERE / "offset-plates.png", dpi=120, facecolor=SURFACE)
    plt.close(fig)


# ------------------------------------------------------------------ beds
def print_beds():
    rep = json.loads((HERE / "slice" / "report.json").read_text())
    with zipfile.ZipFile(HERE / "slice" / "mockup_v2_A1mini_PLA.3mf") as z:
        thumbs = [(p, Image.open(io.BytesIO(z.read(f"Metadata/plate_{p['plate']}.png"))).convert("RGB"))
                  for p in rep["job"]["plates"] if f"Metadata/plate_{p['plate']}.png" in z.namelist()]
    if not thumbs:
        return
    n = len(thumbs)
    cols = 4
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4.3 * rows), facecolor=SURFACE)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, (p, im) in zip(axes.ravel(), thumbs):
        ax.imshow(im)
        h, m = divmod(round(p["print_time_s"] / 60), 60)
        ax.set_title(f"{p['plate']}. {p['name']}\n{h} h {m:02d} min, {p['filament_g']:.0f} g", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(HERE / "print-beds.png", dpi=110, facecolor=SURFACE)
    plt.close(fig)


def main():
    parts, info = PT.build()
    assembly(parts)
    grasp_sections(parts)
    offset_plates(parts, info)
    print_beds()


if __name__ == "__main__":
    main()
