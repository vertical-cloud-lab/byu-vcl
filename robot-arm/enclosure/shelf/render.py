"""3D view and 2D dimensioned drawing of the pick-up shelf (#229).

    xvfb-run -a python render.py [view] [drawing]      # shelf-3d.png, shelf-drawing.png
"""

import json
import sys

import matplotlib
import numpy as np
import pyvista as pv
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

import build as B  # noqa: E402
from piper_fk import Piper  # noqa: E402

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8983"
BLUE, BLUE_FILL, ORANGE = "#2a78d6", "#d7e6f7", "#eb6834"
PLY, PLY_EDGE = "#e3d2ad", "#8c7650"
S = B.SHELF
RES = json.loads((B.HERE / "shelf-results.json").read_text())
REACH = B.REACH
MM = 1000


def side_poses(piper):
    """Picks straight off the arm's side (x = 0), so they lie in the section plane."""
    out = []
    for row, above in ((B.ROWS[0], 0.020), (B.ROWS[1], 0.045)):
        tgt = B.SHELF_TO_WORLD @ np.r_[0.0, S["front"] + row["y"], S["top"] + B.PLATE_T + above, 1]
        out.append(B.ik(piper, tgt[:3], -45.0)[0])
    return out


# ------------------------------------------------------------------ 3D view
def view(path, size=(1500, 1000)):
    piper = Piper()
    pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
    pl.set_background(SURFACE)
    tx, ty = B.TABLE["x"] / 2, B.TABLE["y"] / 2
    for y0, y1 in ((-ty, -0.0015), (0.0015, ty)):
        pl.add_mesh(pv.Box((-tx, tx, y0, y1, -0.03, 0)), color="#26272a", ambient=0.2)
    pl.add_mesh(pv.Box((-0.9, 0.9, B.WALL_Y, B.WALL_Y + 0.05, -0.03, 0.75)), color="#ecebe6", ambient=0.3)
    for z in np.arange(0.20, 0.75, 0.203):          # block courses, 8 in
        pl.add_mesh(pv.Line((-0.9, B.WALL_Y - 0.0005, z), (0.9, B.WALL_Y - 0.0005, z)), color="#c9c7c0", line_width=1)
    plate = B.base_plate()
    pl.add_mesh(pv.wrap(plate), color="#eadcbe", ambient=0.15)
    for p in B.parts() + B.items():
        w = p.world
        ply = "ply" in p.tags or "plate" in p.tags
        pl.add_mesh(pv.wrap(w), color=p.color, smooth_shading=not ply, split_sharp_edges=True, specular=0.2,
                    ambient=0.15)
        if "ply" in p.tags:
            e = pv.wrap(w).extract_feature_edges(feature_angle=60, boundary_edges=False, manifold_edges=False)
            pl.add_mesh(e, color=PLY_EDGE, line_width=1.2)
    for it in B.dome_frame():
        pl.add_mesh(pv.wrap(it.world), color="#f4f4f1", smooth_shading=True, specular=0.3, ambient=0.2)
    q = np.radians(RES["pick_pose_deg"])
    for link, m, c in B.arm_meshes(piper, q, keep=None, grip=0.0155):
        pl.add_mesh(pv.wrap(m), color=c, smooth_shading=True, specular=0.25)
    pl.camera_position = [(-0.98, -0.80, 0.78), (0.04, 0.40, 0.12), (0, 0, 1)]
    pl.camera.view_angle = 28
    pl.enable_anti_aliasing("ssaa")
    Image.fromarray(pl.screenshot(return_img=True)).save(path)
    pl.close()
    print(path.name)


# ------------------------------------------------------------------ 2D drawing
def silhouette(ax, piper, q, proj, color, alpha=1.0, z=3, keep=0.2):
    polys = []
    for link, m, c in B.arm_meshes(piper, q, keep=keep):
        v = proj(m.vertices)
        polys.append(v[m.faces])
    pc = PolyCollection(np.concatenate(polys), facecolors=color, edgecolors="none", alpha=alpha, zorder=z)
    ax.add_collection(pc)


def dim(ax, a, b, text, off=(0, 0), ha="center", va="center", fs=9, color=INK, rot=0):
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.8, shrinkA=0, shrinkB=0,
                                                    mutation_scale=7))
    mid = (np.add(a, b)) / 2 + off
    ax.text(*mid, text, fontsize=fs, color=color, ha=ha, va=va, rotation=rot,
            bbox=dict(fc=SURFACE, ec="none", pad=0.6))


def ext(ax, p0, p1):
    ax.plot(*zip(p0, p1), color=MUTED, lw=0.5, zorder=1)


def plan(ax, piper):
    L, F, Dp = S["length"] * MM, S["front"] * MM, S["depth"] * MM
    T = B.T * MM
    wall = (B.WALL_Y - B.Y_J1) * MM
    band = REACH["comfortable_band_by_shelf_height_m"][f"{S['top']:.3f}"]
    j1 = REACH["j1_limit_deg"]
    marg = REACH["margin_deg"]
    # wall and plate
    ax.add_patch(patches.Rectangle((-760, wall), 1520, 40, fc="#ecebe7", ec=INK2, lw=0.8, hatch="///", zorder=1))
    ax.text(-740, wall + 52, "wall (room 158)", fontsize=9, color=INK2)
    px = B.BASE["x"] / 2 * MM
    yb = (B.RAIL_Y - B.RAIL_GAP - B.Y_J1) * MM
    ax.add_patch(patches.Rectangle((-px, yb - B.BASE["y"] * MM), 2 * px, B.BASE["y"] * MM, fc="#f6efe0",
                                   ec=MUTED, lw=0.8, ls="--", zorder=0))
    ax.text(-px + 10, -300, "arm's plate (4 × 4 ft, trimmed to 47 1/2 in across)", fontsize=8.5, color=MUTED)
    rail = (B.RAIL_Y - B.Y_J1) * MM
    ax.add_patch(patches.Rectangle((-760, rail), 1520, B.P.PIPE_OD * MM, fc="#f1f1ee", ec=MUTED, lw=0.8, zorder=1))
    ax.text(740, rail + 13, "dome's back bottom rail", fontsize=8, color=INK2, ha="right", va="center")
    # reach: comfortable band (blue) over the J1 range, dead wedge behind the base (orange)
    # In this layout the arm faces -x, so its back (J1 = +/-180) points +x.
    th_ok = np.radians(np.linspace(-(j1 - marg), j1 - marg, 200)) + np.pi       # world angles
    ring = np.r_[np.c_[band[1] * MM * np.cos(th_ok), band[1] * MM * np.sin(th_ok)],
                 np.c_[band[0] * MM * np.cos(th_ok[::-1]), band[0] * MM * np.sin(th_ok[::-1])]]
    ax.add_patch(patches.Polygon(ring, fc=BLUE_FILL, ec=BLUE, lw=0.8, alpha=0.75, zorder=1))
    ax.add_patch(patches.Wedge((0, 0), 620, -(180 - j1), 180 - j1, fc="#fbe3d8", ec=ORANGE, lw=0.8, zorder=1,
                               hatch="\\\\\\", alpha=0.8))
    for a in (180 - j1 + marg, -(180 - j1 + marg)):
        ax.plot([0, 620 * np.cos(np.radians(a))], [0, 620 * np.sin(np.radians(a))], color=ORANGE, lw=0.7, ls=":")
    ax.text(470, -20, f"J1 stops at ±{j1:.0f}°:\nout of reach", fontsize=8.5, color=ORANGE, ha="left", va="center",
            bbox=dict(fc=SURFACE, ec="none", pad=0.5), zorder=6)
    # parked arm and its sweep
    silhouette(ax, piper, np.zeros(6), lambda v: (v[:, :2] - [B.X_J1, B.Y_J1]) * MM, "#bfc3c8", z=3)
    ax.add_patch(patches.Circle((0, 0), REACH["rest_pose"]["swept_radius_m"] * MM, fc="none", ec=INK2, lw=0.8,
                                ls="--", zorder=4))
    ax.annotate(f"parked arm (all joints 0) sweeps\nr = {REACH['rest_pose']['swept_radius_m'] * MM:.0f} mm "
                "if J1 turns while folded", xy=(-224, -224), xytext=(-720, -150), fontsize=8.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.plot([-12, 12], [0, 0], color=INK, lw=0.9, zorder=6)
    ax.plot([0, 0], [-12, 12], color=INK, lw=0.9, zorder=6)
    ax.annotate("J1 axis\n(arm faces −x;\ncable exits +x)", xy=(0, 0), xytext=(-250, 95), fontsize=8.5,
                color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=INK, lw=0.6), zorder=7)
    # shelf: legs (hidden), top, fence, pockets, pins
    for x in B.leg_x() * MM:
        ax.add_patch(patches.Rectangle((x - T / 2, F), T, Dp, fc="none", ec=PLY_EDGE, lw=0.7, ls="--", zorder=5))
    ax.add_patch(patches.Rectangle((-L / 2, F), L, Dp, fc=PLY, ec=PLY_EDGE, lw=1.0, alpha=0.9, zorder=4))
    ax.add_patch(patches.Rectangle((-L / 2, F + Dp), L, T, fc="#d9c49b", ec=PLY_EDGE, lw=1.0, zorder=4))
    for row in B.ROWS:
        r = (row["item"]["d"] + B.POCKET_CLEAR) / 2 * MM
        for x in row["xs"] * MM:
            ax.add_patch(patches.Circle((x, F + row["y"] * MM), r, fc="#f4f1ea", ec=INK2, lw=0.6, zorder=5))
    for x, y in B.PLATE_PINS:
        ax.add_patch(patches.Circle((x * MM, F + y * MM), 3, fc=INK2, ec="none", zorder=6))
    # dimensions
    xs = B.leg_x() * MM
    yl = F - 40
    yL = F - 85
    ext(ax, (-L / 2, F), (-L / 2, yL - 8))
    ext(ax, (L / 2, F), (L / 2, yL - 8))
    dim(ax, (-L / 2, yL), (L / 2, yL), f"{L:.0f} overall")
    for x in xs:
        ext(ax, (x, F), (x, yl - 8))
    for a, b in zip(xs[:-1], xs[1:]):
        dim(ax, (a, yl), (b, yl), f"{b - a:.0f}", fs=8)
    ax.text(xs[0] - 25, yl, "legs, c/c", fontsize=8, color=INK2, ha="right", va="center")
    xd = L / 2 + 330
    ext(ax, (L / 2, F), (xd + 10, F))
    ext(ax, (L / 2, F + Dp), (xd + 10, F + Dp))
    ext(ax, (20, 0), (xd + 200, 0))
    dim(ax, (xd, F), (xd, F + Dp), f"{Dp:.0f}", ha="left", off=(8, 0))
    dim(ax, (xd + 70, 0), (xd + 70, F), f"{F:.0f}\nJ1 to\nfront edge", ha="left", off=(8, 0))
    ext(ax, (L / 2, F + Dp + T), (xd + 200, F + Dp + T))
    dim(ax, (xd + 140, 0), (xd + 140, F + Dp + T), f"{F + Dp + T:.0f}\nJ1 to back\nof fence", ha="left", off=(8, 0))
    ext(ax, (760, wall), (xd + 360, wall))
    dim(ax, (xd + 330, 0), (xd + 330, wall), f"{wall:.0f}\nJ1 to wall", ha="left", off=(8, 0))
    for row, lab in zip(B.ROWS, ("20 mL vials", "50 mL tubes")):
        y = F + row["y"] * MM
        ax.text(-L / 2 - 12, y, f"{lab}: {y:.0f} from J1, {np.diff(row['xs'])[0] * MM:.0f} pitch", fontsize=8,
                color=INK2, ha="right", va="center")
    ax.text(-L / 2 - 12, F + Dp + T / 2, "fence", fontsize=8, color=INK2, ha="right", va="center")
    ax.text(-990, 230, f"blue: comfortable picks,\n{band[0] * MM:.0f}–{band[1] * MM:.0f} mm from J1\n"
            f"(45° ± 15° approach,\njoints ≥ {marg:.0f}° off their stops)", fontsize=8.5, color=BLUE, va="top")
    ax.set_xlim(-1000, 1260)
    ax.set_ylim(-330, wall + 80)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Plan, looking down (mm from the J1 axis)", loc="left", fontsize=11, color=INK, weight="bold")


def section(ax, piper):
    F, Dp, top, lip = S["front"] * MM, S["depth"] * MM, S["top"] * MM, S["lip"] * MM
    T, PTm = B.T * MM, B.PLATE_T * MM
    wall = (B.WALL_Y - B.Y_J1) * MM
    rp = REACH["rest_pose"]
    # comfortable cells from the reach map, front side (r > 0), as fingertip positions
    d = np.load(B.HERE / "reach-map.npz")
    feas, R, Z, Pd = d["feas"], d["r_bins"], d["z_bins"], d["pitches"]
    sel = (Pd >= REACH["approach_pitch_deg"][0]) & (Pd <= REACH["approach_pitch_deg"][1])
    comf = feas[sel].all(axis=0)
    for i in range(len(R) - 1):
        for k in range(len(Z) - 1):
            if comf[i, k] and R[i] >= 0 and Z[k] >= -0.0001:
                ax.add_patch(patches.Rectangle((R[i] * MM, Z[k] * MM), 10, 10, fc=BLUE_FILL, ec="none", zorder=0))
    ax.text(640, 250, "blue: fingertip positions where\na 45° ± 15° pick is comfortable\n(every joint ≥ 15° off its stop)",
            fontsize=8.5, color=BLUE, va="top")
    # plate, wall
    ax.add_patch(patches.Rectangle((-260, -T), wall + 260 + 5, T, fc="#eadcbe", ec=MUTED, lw=0.8, zorder=2))
    ax.add_patch(patches.Rectangle((wall, -T - 30), 40, 560, fc="#ecebe7", ec=INK2, lw=0.8, hatch="///", zorder=2))
    ax.add_patch(patches.Rectangle((-260, -T - 30), wall + 260, 30, fc="#26272a", ec="none", zorder=2))
    # shelf section at x = 0: top, fence, legs beyond (dashed), plate, items
    ax.add_patch(patches.Rectangle((F, 0), Dp, top - T, fc="none", ec=PLY_EDGE, lw=0.7, ls="--", zorder=3))
    ax.add_patch(patches.Rectangle((F, top - T), Dp, T, fc=PLY, ec=PLY_EDGE, lw=1.0, zorder=4))
    ax.add_patch(patches.Rectangle((F + Dp, 0), T, top + lip, fc="#d9c49b", ec=PLY_EDGE, lw=1.0, zorder=4))
    ax.add_patch(patches.Rectangle((F, top), Dp - 2, PTm, fc="#f4f1ea", ec=INK2, lw=0.6, zorder=4))
    for row in B.ROWS:
        it = row["item"]
        y = F + row["y"] * MM
        ax.add_patch(patches.Rectangle((y - it["d"] / 2 * MM, top), it["d"] * MM, (it["h"] - it["cap"]) * MM,
                                       fc=it["color"], ec=INK2, lw=0.6, zorder=5))
        ax.add_patch(patches.Rectangle((y - it["d"] / 2 * MM, top + (it["h"] - it["cap"]) * MM), it["d"] * MM,
                                       it["cap"] * MM, fc=it["cap_color"], ec=INK2, lw=0.6, zorder=5))
    # arms: picking the tube (ghost) and the vial, both at x = 0, in the section plane
    proj = lambda v: np.c_[(v[:, 1] - B.Y_J1) * MM, (v[:, 2] - B.PT) * MM]  # noqa: E731
    qv, qt = side_poses(piper)
    silhouette(ax, piper, qt, proj, "#9aa3ad", alpha=0.35, z=6)
    silhouette(ax, piper, qv, proj, "#5b6168", alpha=0.95, z=7)
    # the parked arm's sweep: a cylinder r = 317 mm from z = 89 to 231 mm
    r0 = rp["swept_radius_m"] * MM
    ax.add_patch(patches.Rectangle((r0 - 2, rp["underside_behind_m"] * MM), 4,
                                   (rp["top_behind_m"] - rp["underside_behind_m"]) * MM, fc=INK2, ec="none", zorder=8))
    ax.annotate(f"parked arm's sweep, r = {r0:.0f}\n(z {rp['underside_behind_m'] * MM:.0f}–"
                f"{rp['top_behind_m'] * MM:.0f} mm)", xy=(r0, rp["underside_behind_m"] * MM), xytext=(640, 120),
                fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6), zorder=9)
    ax.add_patch(patches.Circle(((B.D.SPAN["y"] / 2 - B.Y_J1) * MM, (B.D.Z0 - B.PT) * MM), B.P.PIPE_OD / 2 * MM,
                                fc="#f1f1ee", ec=INK2, lw=0.7, zorder=4))
    ax.plot([0, 0], [-T - 30, 480], color=INK, lw=0.7, ls="-.", zorder=2)
    ax.text(6, 470, "J1 axis", fontsize=8.5, color=INK)
    # dimensions
    xh = F - 40
    ext(ax, (F, top), (xh - 10, top))
    dim(ax, (xh, 0), (xh, top), f"{top:.0f}", ha="right", off=(-8, 0))
    ext(ax, (F, top - T), (xh - 60, top - T))
    dim(ax, (xh - 50, 0), (xh - 50, top - T), f"leg\n{top - T:.0f}", ha="right", off=(-8, 0), fs=8)
    xf = F + Dp + T + 30
    ext(ax, (F + Dp + T, top + lip), (xf + 10, top + lip))
    dim(ax, (xf, 0), (xf, top + lip), f"{top + lip:.0f}", ha="left", off=(6, 0), fs=8)
    yd = -T - 70
    for x in (0, F, F + B.ROWS[0]["y"] * MM, F + B.ROWS[1]["y"] * MM, F + Dp + T, wall):
        ext(ax, (x, -T - 30), (x, yd - 8))
    dim(ax, (0, yd), (F, yd), f"{F:.0f}")
    dim(ax, (0, yd - 45), (F + B.ROWS[0]["y"] * MM, yd - 45), f"{F + B.ROWS[0]['y'] * MM:.0f} vials")
    dim(ax, (0, yd - 90), (F + B.ROWS[1]["y"] * MM, yd - 90), f"{F + B.ROWS[1]['y'] * MM:.0f} tubes")
    dim(ax, (0, yd - 135), (F + Dp + T, yd - 135), f"{F + Dp + T:.0f} back of fence")
    dim(ax, (0, yd - 180), (wall, yd - 180), f"{wall:.0f} wall")
    ax.text(-275, 300, "dark: picking a vial\ngrey: picking a tube\ngripper 45° down", fontsize=8.5, color=INK2)
    # height table
    rows = REACH["comfortable_band_by_shelf_height_m"]
    txt = ["shelf top above the plate → comfortable band"]
    for h, b in rows.items():
        txt.append(f"{float(h) * MM:4.0f} mm → " + (f"{b[0] * MM:.0f}–{b[1] * MM:.0f} mm from J1" if b else "none"))
    ax.text(700, 470, "\n".join(txt), fontsize=8.3, color=INK2, va="top", family="monospace",
            bbox=dict(fc=SURFACE, ec=MUTED, lw=0.6, pad=4))
    ax.set_xlim(-280, 1180)
    ax.set_ylim(yd - 210, 500)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Section through the J1 axis, square to the wall (mm above the arm's plate)", loc="left",
                 fontsize=11, color=INK, weight="bold")


def drawing(path):
    piper = Piper()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 12.6), dpi=110, facecolor=SURFACE,
                                 gridspec_kw=dict(height_ratios=[4.6, 5.5], hspace=0.08))
    for a in (a1, a2):
        a.set_facecolor(SURFACE)
    plan(a1, piper)
    section(a2, piper)
    fig.suptitle("Pick-up shelf behind the PiPER at spot D: the arm turned 90°, the shelf off its side",
                 x=0.06, ha="left", y=0.995, fontsize=13.5, weight="bold", color=INK)
    fig.text(0.06, 0.975, f"3/4 in plywood: top {S['length'] * MM:.0f} × {S['depth'] * MM:.0f}, four "
             f"{(S['top'] - B.T) * MM:.0f} mm legs, a {(S['top'] + S['lip']) * MM:.0f} mm fence; a 6 mm nest plate "
             "on two pins. Fingertips 10–60 mm above the shelf.", fontsize=10, color=INK2)
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(path.name)


if __name__ == "__main__":
    what = sys.argv[1:] or ["view", "drawing"]
    if "view" in what:
        view(B.HERE / "shelf-3d.png")
    if "drawing" in what:
        drawing(B.HERE / "shelf-drawing.png")
