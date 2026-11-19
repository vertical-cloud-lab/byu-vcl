"""2D sketch and 3D view of the proposed CubXL handoff dock and mock-up v2 (#266).

    python analysis.py && xvfb-run -a python render.py      # sketch-2d.png, layout-3d.png
"""

import json

import matplotlib
import numpy as np
import pyvista as pv
import trimesh
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

import geometry as G  # noqa: E402
from piper_fk import Piper  # noqa: E402

RES = json.loads((G.HERE / "results.json").read_text())
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8983"
BLUE, BLUE_FILL, ORANGE, ORANGE_FILL = "#2a78d6", "#d7e6f7", "#eb6834", "#fbe3d8"
PLY, PLY_EDGE, HOLDER, VIALC, POSTC, DECKC = "#e3d2ad", "#8c7650", "#8474a1", "#9dcfed", "#d9480f", "#e6ecf1"
MM = 1000
Q_GRASP = np.radians(RES["handoff_ik"]["carrier radial, 45 deg along it (post)"]["q_deg"])


# ------------------------------------------------------------------ meshes
def arm_meshes(piper, q, grip=0.0135, keep=None):
    out = []
    poses = piper.fk(q, grip=grip)
    for name, path in piper.meshes.items():
        scene = trimesh.load(path, force="scene")
        for node in scene.graph.nodes_geometry:
            Tn, g = scene.graph[node]
            m = scene.geometry[g]
            if len(m.faces) < 10:
                continue
            try:
                c = np.array(m.visual.material.main_color[:3]) / 255
            except AttributeError:
                c = np.array([0.6, 0.6, 0.6])
            m = trimesh.Trimesh(trimesh.transform_points(m.vertices, Tn), m.faces, process=False)
            if keep and len(m.faces) > 400:
                pd = pv.wrap(m).decimate(1 - keep)
                m = trimesh.Trimesh(pd.points, pd.faces.reshape(-1, 4)[:, 1:], process=False)
            m.apply_transform(piper.visual_origin[name])
            m.apply_transform(poses[name])
            out.append((name, m, c))
    return out


def _tf(t=(0, 0, 0), rz=0.0, s=1.0):
    T = trimesh.transformations.rotation_matrix(np.radians(rz), [0, 0, 1])
    T[:3, :3] *= s
    T[:3, 3] = t
    return T


def box(b):
    (x0, x1), (y0, y1), (z0, z1) = b
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def scene_meshes():
    """[(mesh, colour, opacity, tag)] for everything except the arm, world metres."""
    parts = G.mockup_parts()
    out = []
    deck = G.panda_deck().copy()
    deck.apply_transform(_tf(G.deck_origin(), 90, 0.001))
    out.append((deck, "#cfdbe4", 0.9, "deck"))
    d0 = G.deck_origin()
    for x in (d0[0] + 0.03, d0[0] + G.DECK["x"] - 0.03):          # supports down to the bench
        out.append((box(((x - 0.02, x + 0.02), (d0[1] + 0.02, d0[1] + G.DECK["y"] - 0.02), (0, d0[2]))),
                    "#9a9a96", 1.0, "support"))
    for name, b in G.frame_boxes():
        out.append((box(b), ORANGE, 0.28 if "rail" in name or "member" in name else 0.45, "keepout"))
    # dock
    z0, zc = G.DECK_TOP, G.carrier_z0()
    y0, y1 = G.CARRIER["near_y"] - 0.02, G.CARRIER["near_y"] + G.CARRIER["len"] + 0.02
    out.append((box(((-0.032, 0.080), (y0, y1), (z0, zc))), PLY, 1.0, "dock"))
    w = G.CARRIER["wid"] / 2 + 0.0005
    for sx in (-1, 1):
        out.append((box(((sx * w, sx * (w + 0.006)) if sx > 0 else (-(w + 0.006), -w), (y0 + 0.01, y1 - 0.01),
                         (zc, zc + G.DOCK["wall_h"]))), PLY, 1.0, "dock"))
    for (x, y) in G.SINGLE_POCKETS:
        ring = trimesh.creation.annulus(r_min=0.0145, r_max=0.019, height=0.025)
        ring.apply_translation([x, y, zc + 0.0125])
        out.append((ring, PLY, 1.0, "dock"))
    # carrier, vials and handle post
    holder = parts["holder"].copy()
    holder.apply_transform(_tf((0, G.slot_y(1), zc), 180, 0.001))
    out.append((holder, HOLDER, 1.0, "carrier"))
    for i in (1, 2, 3, 4, 6, 7, 8, 9):
        v = parts["vial"].copy()
        v.apply_transform(_tf((0, G.slot_y(i), zc + G.CARRIER["seat"]), 0, 0.001))
        out.append((v, VIALC, 1.0, "vial"))
    v = parts["vial"].copy()
    v.apply_transform(_tf((*G.SINGLE_POCKETS[0], zc + 0.002), 0, 0.001))
    out.append((v, VIALC, 1.0, "vial"))
    post = trimesh.creation.cylinder(radius=G.POST["d"] / 2, height=G.VIAL["h"], sections=48)
    post.apply_translation([0, G.slot_y(5), zc + G.CARRIER["seat"] + G.VIAL["h"] / 2])
    groove = trimesh.creation.annulus(r_min=G.POST["d"] / 2 - G.POST["groove_depth"], r_max=0.02,
                                      height=G.POST["groove_h"], sections=48)
    groove.apply_translation([0, G.slot_y(5), zc + G.POST["groove_z"]])
    try:
        post = trimesh.boolean.difference([post, groove], engine="manifold")
    except Exception:  # noqa: BLE001 - boolean backend missing: show the plain post
        pass
    out.append((post, POSTC, 1.0, "post"))
    return out


# ------------------------------------------------------------------ 3D view
def view3d(path):
    piper = Piper()
    meshes = scene_meshes()
    arm = arm_meshes(piper, Q_GRASP)
    shots = []
    for cam, size in (([(-1.05, -0.62, 0.78), (0.06, 0.40, 0.10), (0, 0, 1)], (1100, 820)),
                      ([(0.30, 0.31, 0.36), (0.02, 0.48, 0.10), (0, 0, 1)], (1100, 820))):
        pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
        pl.set_background(SURFACE)
        pl.add_mesh(pv.Box((-0.45, 0.62, -0.42, 0.95, -0.02, 0)), color="#d8d4cb", ambient=0.25)
        for m, c, op, tag in meshes:
            if not (shots and tag == "keepout"):     # the close-up shows the keep-out as edges only
                pl.add_mesh(pv.wrap(m), color=c, opacity=op, smooth_shading=tag in ("vial", "post"),
                            specular=0.2, ambient=0.18)
            if tag == "keepout":
                pl.add_mesh(pv.wrap(m).extract_feature_edges(feature_angle=60), color=ORANGE, line_width=1.5)
        for _, m, c in arm:
            pl.add_mesh(pv.wrap(m), color=c, smooth_shading=True, specular=0.25)
        pl.camera_position = cam
        pl.camera.view_angle = 30
        pl.enable_anti_aliasing("ssaa")
        shots.append(Image.fromarray(pl.screenshot(return_img=True)))
        pl.close()
    W = sum(s.width for s in shots)
    canvas = Image.new("RGB", (W, shots[0].height), SURFACE)
    x = 0
    for s in shots:
        canvas.paste(s, (x, 0))
        x += s.width
    canvas.save(path)
    print(path.name)


# ------------------------------------------------------------------ 2D sketch
def silhouette(ax, arm, axes, color="#a9a8a2", z=4, alpha=0.55):
    polys = [m.vertices[:, axes][m.faces] * MM for _, m, _ in arm]
    ax.add_collection(PolyCollection(np.concatenate(polys), facecolors=color, edgecolors="none", zorder=z,
                                     alpha=alpha, rasterized=True))


def dim(ax, a, b, text, off=(0, 0), fs=8.5, color=INK, rot=0):
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.8, shrinkA=0,
                                                    shrinkB=0, mutation_scale=7), zorder=9)
    mid = (np.add(a, b)) / 2 + off
    ax.text(*mid, text, fontsize=fs, color=color, ha="center", va="center", rotation=rot, zorder=10,
            bbox=dict(fc=SURFACE, ec="none", pad=0.5))


def rect(ax, x0, x1, y0, y1, **kw):
    ax.add_patch(patches.Rectangle((x0 * MM, y0 * MM), (x1 - x0) * MM, (y1 - y0) * MM, **kw))


def note(ax, xy, text, xytext, fs=8.5):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=INK, ha="left", va="center", zorder=11,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7, shrinkA=2, shrinkB=2),
                bbox=dict(fc=SURFACE, ec="none", pad=0.5))


def plan(ax, arm):
    ax.set_title("Plan", loc="left", fontsize=11, color=INK)
    band = RES["reach_bands"]["pitch45_margin15"]["0.10"]
    ax.add_patch(patches.Wedge((0, 0), band[1] * MM, -45, 225, width=(band[1] - band[0]) * MM, fc=BLUE_FILL,
                               ec=BLUE, lw=0.6, alpha=0.55, zorder=0))
    ax.add_patch(patches.Wedge((0, 0), 330, 225, 315, fc="#f1f0ec", ec=MUTED, lw=0.6, zorder=0))
    ax.text(0, -250, "J1 stop (±150°)", fontsize=8, color=INK2, ha="center")
    ax.text(-560, 100, "45° grasps,\nevery joint 15° clear\nof its limit:\n%d–%d mm" % (band[0] * MM, band[1] * MM),
            fontsize=8, color=BLUE, ha="left", va="center")
    # CubXL envelope
    fx0, fx1 = G.FRAME_FRONT_X, G.FRAME_FRONT_X + G.FRAME["y"]
    fy0, fy1 = G.FRAME_NEAR_Y, G.FRAME_NEAR_Y + G.FRAME["x"]
    rect(ax, fx0, fx1, fy0, fy1, fc="none", ec=INK2, lw=0.8, ls="--", zorder=1)
    d0 = G.deck_origin()
    rect(ax, d0[0], d0[0] + G.DECK["x"], d0[1], d0[1] + G.DECK["y"], fc=DECKC, ec=MUTED, lw=0.7, zorder=1)
    for i in range(18):           # PandaDeck slots: 25 mm pitch across gantry X, 45 mm along gantry Y
        for j in range(10):
            cx = d0[0] + 0.040 + j * 0.045
            cy = d0[1] + 0.0275 + i * 0.025
            rect(ax, cx - 0.01245, cx + 0.01245, cy - 0.005, cy + 0.005, fc="#ffffff", ec="#b8c3cc", lw=0.4,
                 zorder=1)
    for name, ((x0, x1), (y0, y1), _) in G.frame_boxes():
        if "tools" in name:
            continue
        rect(ax, x0, x1, y0, y1, fc=ORANGE_FILL, ec=ORANGE, lw=0.8, hatch="///" if "parked" in name else None,
             alpha=0.9, zorder=2)
    (wx0, wx1), (wy0, wy1) = G.window_world()
    rect(ax, wx0, wx1, wy0, wy1, fc="none", ec=BLUE, lw=1.0, ls="-.", zorder=3)
    ax.text(wx0 * MM, wy1 * MM + 10, "capper ∩ pipette reach, %.0f × %.0f mm" % ((wx1 - wx0) * MM, (wy1 - wy0) * MM),
            fontsize=8, color=BLUE, ha="left", va="bottom", zorder=3, bbox=dict(fc=SURFACE, ec="none", pad=0.4))
    # dock, carrier, vials, post, single pockets
    y0, y1 = G.CARRIER["near_y"] - 0.02, G.CARRIER["near_y"] + G.CARRIER["len"] + 0.02
    rect(ax, -0.032, 0.080, y0, y1, fc=PLY, ec=PLY_EDGE, lw=0.8, zorder=4)
    rect(ax, -G.CARRIER["wid"] / 2, G.CARRIER["wid"] / 2, G.CARRIER["near_y"], G.CARRIER["near_y"] + G.CARRIER["len"],
         fc=HOLDER, ec=INK2, lw=0.6, alpha=0.85, zorder=5)
    for i in range(1, 10):
        c = (0, G.slot_y(i) * MM)
        if i == 5:
            ax.add_patch(patches.Circle(c, 13.5, fc=POSTC, ec=INK, lw=0.6, zorder=6))
        else:
            ax.add_patch(patches.Circle(c, 14, fc=VIALC, ec=INK2, lw=0.5, zorder=6))
    for k, (x, y) in enumerate(G.SINGLE_POCKETS):
        ax.add_patch(patches.Circle((x * MM, y * MM), 19, fc=PLY, ec=PLY_EDGE, lw=0.8, zorder=5))
        ax.add_patch(patches.Circle((x * MM, y * MM), 14.5, fc="white" if k else VIALC, ec=PLY_EDGE, lw=0.6,
                                    zorder=6))
    silhouette(ax, arm, [0, 1], z=7)
    ax.plot(0, 0, "+", color=INK, ms=9, mew=1.2, zorder=8)
    ax.text(18, -22, "J1", fontsize=8.5, color=INK)
    # dimensions
    gy = G.slot_y(5) * MM
    dim(ax, (-120, 0), (-120, gy), "%.0f" % gy, rot=90)
    ax.plot([-130, -14], [gy, gy], color=MUTED, lw=0.5, zorder=8)
    ax.plot([-130, -40], [0, 0], color=MUTED, lw=0.5, zorder=8)
    dim(ax, (-215, 0), (-215, fy0 * MM), "%.0f" % (fy0 * MM), rot=90)
    ax.plot([-225, -150], [fy0 * MM] * 2, color=MUTED, lw=0.5, zorder=8)
    dim(ax, (110, G.CARRIER["near_y"] * MM), (110, (G.CARRIER["near_y"] + G.CARRIER["len"]) * MM),
        "%.0f" % (G.CARRIER["len"] * MM), rot=90)
    # callouts
    note(ax, (fx0 * MM + 20, (fy0 + 0.03) * MM), "① keep-out: rails, front/back members", (-640, 330))
    note(ax, (0.255 * MM, 0.62 * MM), "② gantry parked at Y max,\n    carriage at the far X end", (300, 960))
    note(ax, (-32, (y1 - 0.01) * MM), "③ dock: pill-keyed and screwed to the deck,\n    3 mm lead-in nest + 2 cone pins", (-640, 820))
    note(ax, (-14, gy), "④ 8 + 1 carrier: vial-sized\n    handle post in slot 5", (-640, 600))
    note(ax, (G.SINGLE_POCKETS[1][0] * MM + 15, G.SINGLE_POCKETS[1][1] * MM), "⑤ 2 loose single-vial pockets",
         (210, 330))
    ax.text(fx0 * MM - 14, (fy0 + fy1) / 2 * MM, "CubXL front (operator side)", fontsize=8, color=INK2, ha="right",
            va="center", rotation=90)
    ax.set_xlim(-650, 560)
    ax.set_ylim(-360, 1010)
    ax.set_aspect("equal")
    ax.set_xlabel("mm, from J1", fontsize=8.5, color=INK2)


def elevation(ax, arm):
    ax.set_title("Section on the arm's centre line", loc="left", fontsize=11, color=INK)
    ax.axhline(0, color=INK2, lw=1.0, zorder=1)
    ax.add_patch(patches.Rectangle((-420, -25), 1400, 25, fc="#e7e4dc", ec="none", zorder=0))
    d0 = G.deck_origin()
    for name, (_, (y0, y1), (z0, z1)) in G.frame_boxes():
        if "member" in name:
            continue                      # parallel to the section, in front of and behind it
        far = "parked" in name
        ax.add_patch(patches.Rectangle((y0 * MM, z0 * MM), (y1 - y0) * MM, (z1 - z0) * MM,
                                       fc="none" if far else ORANGE_FILL, ec=ORANGE, lw=0.8,
                                       ls="--" if far else "-", hatch=None if far else "///", zorder=2))
    ax.text(0.61 * MM, 0.458 * MM, "parked gantry, 0.16–0.30 m behind this section", fontsize=8, color=ORANGE,
            ha="center", va="bottom")
    for x in (d0[1] + 0.03, d0[1] + G.DECK["y"] - 0.07):
        ax.add_patch(patches.Rectangle((x * MM, 0), 40, d0[2] * MM, fc="#d6d5d0", ec=MUTED, lw=0.5, zorder=2))
    rect(ax, 0, 0, 0, 0)
    ax.add_patch(patches.Rectangle((d0[1] * MM, d0[2] * MM), G.DECK["y"] * MM, 10, fc="#cfdbe4", ec=MUTED, lw=0.7,
                                   zorder=3))
    zc = G.carrier_z0()
    y0, y1 = G.CARRIER["near_y"] - 0.02, G.CARRIER["near_y"] + G.CARRIER["len"] + 0.02
    ax.add_patch(patches.Rectangle((y0 * MM, G.DECK_TOP * MM), (y1 - y0) * MM, G.DOCK["base_t"] * MM, fc=PLY,
                                   ec=PLY_EDGE, lw=0.7, zorder=4))
    cy0 = G.CARRIER["near_y"] * MM
    ax.add_patch(patches.Rectangle((cy0, zc * MM), G.CARRIER["len"] * MM, G.CARRIER["seat"] * MM, fc=HOLDER,
                                   ec=INK2, lw=0.6, zorder=5))
    ax.add_patch(patches.Rectangle((cy0, (zc + G.CARRIER["seat"]) * MM), G.CARRIER["len"] * MM,
                                   (G.CARRIER["h"] - G.CARRIER["seat"]) * MM, fc=HOLDER, ec="none", alpha=0.35,
                                   zorder=5))
    zs = zc + G.CARRIER["seat"]
    for i in range(1, 10):
        y = G.slot_y(i) * MM
        if i == 5:
            gz = (zc + G.POST["groove_z"]) * MM
            pts = [(y - 13.5, zs * MM), (y + 13.5, zs * MM), (y + 13.5, gz - 3), (y + 11.5, gz - 3), (y + 11.5, gz + 3),
                   (y + 13.5, gz + 3), (y + 13.5, (zs + G.VIAL["h"]) * MM), (y - 13.5, (zs + G.VIAL["h"]) * MM),
                   (y - 13.5, gz + 3), (y - 11.5, gz + 3), (y - 11.5, gz - 3), (y - 13.5, gz - 3)]
            ax.add_patch(patches.Polygon(pts, fc=POSTC, ec=INK, lw=0.6, zorder=6))
        else:
            ax.add_patch(patches.Rectangle((y - 13.5, zs * MM), 27, G.VIAL["body_h"] * MM, fc=VIALC, ec=INK2, lw=0.5,
                                           zorder=6))
            ax.add_patch(patches.Rectangle((y - 14, (zs + G.VIAL["body_h"]) * MM), 28,
                                           (G.VIAL["h"] - G.VIAL["body_h"]) * MM, fc="#6fb3dc", ec=INK2, lw=0.5,
                                           zorder=6))
    silhouette(ax, arm, [1, 2], z=7)
    g = G.grasp_point() * MM
    ax.annotate("", xy=(g[1] - 6, g[2] + 6), xytext=(g[1] - 150, g[2] + 150),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.4, mutation_scale=11), zorder=9)
    ax.text(g[1] - 175, g[2] + 45, "45° approach\nalong the carrier", fontsize=8.5, color=BLUE, ha="right",
            va="center", bbox=dict(fc=SURFACE, ec="none", pad=0.4), zorder=9)
    # heights
    xh = 0.86 * MM
    for z, zl, label in ((zs + G.VIAL["h"], 250, "cap tops %.0f" % ((zs + G.VIAL["h"]) * MM)),
                         (0.123, 205, "J2 axis %.0f" % 123),
                         (G.grasp_point()[2], 160, "grasp %.0f (vial body band %.0f–%.0f)" % (
                             G.grasp_point()[2] * MM, (zc + G.CARRIER["h"]) * MM, (zs + G.VIAL["body_h"]) * MM)),
                         (G.DECK_TOP, 25, "deck top %.1f (your mock-up;\nmeasure the real one)" % (G.DECK_TOP * MM))):
        ax.plot([0.30 * MM if z == 0.123 else 0.68 * MM, xh - 10, xh], [z * MM, z * MM, zl], color=MUTED, lw=0.5,
                ls=":", zorder=1)
        ax.text(xh + 6, zl, label, fontsize=8, color=INK2, va="center")
    ax.text(-410, 545, "No straight-down grasps at this height:\nJ5 stops at ±70°, so the PiPER can point\nits "
            "gripper straight down only below\n~0.10 m and within ~0.34 m of J1.", fontsize=8.5, color=INK, va="top",
            bbox=dict(fc=SURFACE, ec="#d9d8d3", pad=3))
    ax.set_xlim(-420, 1270)
    ax.set_ylim(-30, 560)
    ax.set_aspect("equal")
    ax.set_xlabel("mm along the carrier, from J1", fontsize=8.5, color=INK2)


def nest_detail(ax):
    """Section across the carrier at the dock: lead-in rails, cone pin, fingers on the post."""
    ax.set_title("Detail: section across the dock at slot 5", loc="left", fontsize=11, color=INK)
    w = G.CARRIER["wid"] * MM / 2
    t, lead, wall = G.DOCK["base_t"] * MM, G.DOCK["lead_in"] * MM, G.DOCK["wall_h"] * MM
    ax.add_patch(patches.Rectangle((-60, -t), 120, t, fc=PLY, ec=PLY_EDGE, lw=0.8))
    ax.add_patch(patches.Rectangle((-60, -t - 10), 120, 10, fc="#cfdbe4", ec=MUTED, lw=0.6))
    ax.add_patch(patches.Rectangle((-6.2, -t - 10), 12.4, 10 + t, fc="#c9b88f", ec=PLY_EDGE, lw=0.6))
    ax.text(0, -t - 14, "pill key (stock)", fontsize=7.5, color=INK2, ha="center", va="top")
    for s in (-1, 1):
        x_in = s * (w + 0.5)
        pts = [(x_in, 0), (x_in + s * 6, 0), (x_in + s * 6, wall), (x_in + s * lead, wall), (x_in, wall - lead)]
        ax.add_patch(patches.Polygon(pts, fc=PLY, ec=PLY_EDGE, lw=0.8))
    ax.add_patch(patches.Polygon([(-w, 0), (w, 0), (w, 18), (-w, 18)], fc=HOLDER, ec=INK2, lw=0.6, alpha=0.9))
    ax.add_patch(patches.Polygon([(-3, 0), (3, 0), (1.2, 6), (-1.2, 6)], fc="#7d7c78", ec=INK, lw=0.5))
    ax.text(0, 3, "", fontsize=7)
    ax.add_patch(patches.Rectangle((-13.5, 18), 27, 64.2, fc=POSTC, ec=INK, lw=0.6))
    gz = G.POST["groove_z"] * MM
    for s in (-1, 1):
        ax.add_patch(patches.Rectangle((11.5 if s > 0 else -13.5, gz - 3), 2, 6, fc=SURFACE, ec="none"))
        xf = s * 13.5
        pts = [(xf, gz - 10), (xf + s * 7, gz - 10), (xf + s * 7, gz + 28), (xf, gz + 28), (xf, gz + 3),
               (xf - s * 1.8, gz + 2.5), (xf - s * 1.8, gz - 2.5), (xf, gz - 3)]
        ax.add_patch(patches.Polygon(pts, fc="#5f5e5a", ec=INK, lw=0.6))
    ax.text(26, gz + 18, "finger insert, silicone pad,\nrib in the post's groove", fontsize=7.5, color=INK,
            va="center")
    ax.text(26, wall + 3, "3 mm × 45° lead-in", fontsize=7.5, color=INK, va="bottom")
    ax.text(26, 4, "cone pin → hole + slot\nin the carrier base", fontsize=7.5, color=INK, va="center")
    ax.annotate("carrier base", xy=(-12, 9), xytext=(-58, 26), fontsize=7.5, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.annotate("handle post\n(vial-sized)", xy=(-8, 70), xytext=(-58, 70), fontsize=7.5, color=INK, va="center",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.set_xlim(-62, 80)
    ax.set_ylim(-26, 92)
    ax.set_aspect("equal")
    ax.set_xlabel("mm", fontsize=8.5, color=INK2)


def sketch(path):
    piper = Piper()
    arm = arm_meshes(piper, Q_GRASP, keep=0.15)
    fig = plt.figure(figsize=(17, 9.6), dpi=130, facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.15], height_ratios=[1.0, 0.82], wspace=0.08, hspace=0.16,
                          top=0.93)
    plan(fig.add_subplot(gs[:, 0]), arm)
    elevation(fig.add_subplot(gs[0, 1]), arm)
    nest_detail(fig.add_subplot(gs[1, 1]))
    for ax in fig.axes:
        ax.set_facecolor(SURFACE)
        ax.tick_params(labelsize=7.5, colors=MUTED)
        for s in ax.spines.values():
            s.set_color("#d9d8d3")
    fig.suptitle("Mock-up v2: the CubXL's envelope, a fixed handoff dock and an 8 + 1 carrier "
                 "(orange = keep-out; frame positions are placeholders until measured)",
                 x=0.012, y=0.975, ha="left", fontsize=12.5, color=INK)
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    print(path.name)


if __name__ == "__main__":
    sketch(G.HERE / "sketch-2d.png")
    view3d(G.HERE / "layout-3d.png")
