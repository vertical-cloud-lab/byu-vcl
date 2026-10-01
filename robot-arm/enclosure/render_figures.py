"""Figures for issue #229: PiPER reach vs. enclosure options.

Run headless with:  xvfb-run -a python render_figures.py [reach] [options] [floor]
Needs numpy, scipy, matplotlib, pyvista, trimesh, pycollada and pymupdf.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import trimesh
from matplotlib import patches
from scipy import ndimage

from piper_fk import Piper, fk_points, sample_joints

OUT = Path(__file__).parent
SURFACE = "#fcfcfb"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8983", "#e4e2dd"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
PLY = "#e3d2ad"  # plywood

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

PIPER = Piper()
REST = np.zeros(6)
SHOULDER_Z = 0.123


# ----------------------------------------------------------------------------- kinematics
def envelope_grid(n=3_000_000, seed=0, res=0.005, key="tip", fill=True):
    """Occupancy of the (r, z) half-plane reachable by `key`, r >= 0."""
    r_edges = np.arange(0, 0.80 + res, res)
    z_edges = np.arange(-0.45, 0.95 + res, res)
    H = np.zeros((len(r_edges) - 1, len(z_edges) - 1), bool)
    for k in range(n // 500_000):
        pts = fk_points(PIPER, sample_joints(PIPER, 500_000, seed=seed + k))[key]
        r = np.hypot(pts[:, 0], pts[:, 1])
        h, _, _ = np.histogram2d(r, pts[:, 2], bins=[r_edges, z_edges])
        H |= h > 0
    if fill:
        H = ndimage.binary_fill_holes(ndimage.binary_closing(H, iterations=3))
    return r_edges, z_edges, H


def outer_profile(key="tip", n=2_000_000, seed=10):
    """Max distance from the shoulder per elevation angle -> surface-of-revolution profile."""
    phis = np.radians(np.arange(-90, 90.5, 1.0))
    best = np.zeros_like(phis)
    for k in range(n // 500_000):
        pts = fk_points(PIPER, sample_joints(PIPER, 500_000, seed=seed + k))[key]
        r = np.hypot(pts[:, 0], pts[:, 1])
        dz = pts[:, 2] - SHOULDER_Z
        d = np.hypot(r, dz)
        phi = np.arctan2(dz, r)
        idx = np.clip(np.round(np.degrees(phi) + 90).astype(int), 0, len(phis) - 1)
        np.maximum.at(best, idx, d)
    best = ndimage.maximum_filter1d(best, 3)
    return phis, best


def chain(q):
    P = PIPER.fk(q)
    pts = [np.zeros(3)] + [P[n][:3, 3] for n in ("link2", "link3", "link4", "link6")] + [PIPER.tip(q)]
    return np.array(pts)


# ----------------------------------------------------------------------------- 3D helpers
_PARTS = None


def arm_parts():
    global _PARTS
    if _PARTS is None:
        _PARTS = {}
        for name, path in PIPER.meshes.items():
            scene = trimesh.load(path, force="scene")
            parts = []
            for node in scene.graph.nodes_geometry:
                T, gname = scene.graph[node]
                g = scene.geometry[gname]
                if len(g.faces) < 10:
                    continue
                try:
                    c = np.array(g.visual.material.main_color[:3]) / 255
                except AttributeError:
                    c = np.array([0.6, 0.6, 0.6])
                v = trimesh.transform_points(g.vertices, T)
                faces = np.hstack([np.full((len(g.faces), 1), 3), g.faces]).ravel()
                parts.append((pv.PolyData(v, faces), c))
            _PARTS[name] = parts
    return _PARTS


def add_arm(pl, q, base=np.eye(4), grip=0.015, opacity=1.0):
    poses = PIPER.fk(q, grip=grip)
    for name, parts in arm_parts().items():
        T = base @ poses[name] @ PIPER.visual_origin[name]
        for mesh, c in parts:
            pl.add_mesh(mesh.transform(T, inplace=False), color=c, smooth_shading=True,
                        specular=0.25, specular_power=15, opacity=opacity)


def dome_mesh(phis, dist, center, zmin=0.0, n_theta=120):
    """Surface of revolution of the reach profile about the J1 axis, clipped at the mount plane."""
    th = np.linspace(0, 2 * np.pi, n_theta)
    P, TH = np.meshgrid(phis, th, indexing="ij")
    D = np.repeat(dist[:, None], len(th), axis=1)
    x = center[0] + D * np.cos(P) * np.cos(TH)
    y = center[1] + D * np.cos(P) * np.sin(TH)
    z = center[2] + SHOULDER_Z + D * np.sin(P)
    grid = pv.StructuredGrid(x, y, z).extract_surface(algorithm="dataset_surface").triangulate()
    return grid.clip("z", origin=(0, 0, center[2] + zmin), invert=False)


def add_frame(pl, lo, hi, tube_r=0.0167, color="#f4f4f2"):
    """Box frame of 1 in PVC (OD 33 mm) between corners lo and hi."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    c = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in edges:
        pl.add_mesh(pv.Tube(pointa=c[a], pointb=c[b], radius=tube_r, n_sides=20), color=color,
                    smooth_shading=True, specular=0.4)


def new_plotter(size):
    pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
    pl.set_background(SURFACE)
    return pl


def shot(pl):
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


def trim(img, pad=12):
    """Crop surface-coloured margins off a screenshot."""
    bg = np.array([int(SURFACE[i:i + 2], 16) for i in (1, 3, 5)])
    mask = np.abs(img[..., :3].astype(int) - bg).sum(-1) > 6
    ys, xs = np.where(mask)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, img.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, img.shape[1])
    return img[y0:y1, x0:x1]


# ----------------------------------------------------------------------------- figure 1
PICK = np.radians([0, 111, -90, 0, 66, 0])
UP = np.radians([0, 85, -170, 0, 0, 0])


def hero_render(size=(1300, 1300)):
    pl = new_plotter(size)
    pl.add_mesh(pv.Box(bounds=(-0.12, 0.52, -0.14, 0.36, -0.019, 0.0)), color=PLY, smooth_shading=False, ambient=0.15)
    add_arm(pl, PICK + np.radians([28, 0, 0, 0, 0, 0]), grip=0.012)
    vial = pv.Cylinder(center=(0.37, 0.20, 0.03), direction=(0, 0, 1), radius=0.0125, height=0.06)
    pl.add_mesh(vial, color="#cfe3f7", opacity=0.9, smooth_shading=True, specular=0.6)
    pl.camera_position = [(1.55, -1.65, 1.05), (0.20, 0.08, 0.22), (0, 0, 1)]
    pl.camera.view_angle = 24
    return trim(shot(pl))


def mirrored(key, n, seed):
    """Full side-view occupancy (r from -0.8 to 0.8), smoothed so the contour is not pixel-stepped."""
    r, z, H = envelope_grid(key=key, n=n, seed=seed, fill=False)
    rc, zc = (r[:-1] + r[1:]) / 2, (z[:-1] + z[1:]) / 2
    R = np.concatenate([-rc[::-1], rc])
    M = ndimage.binary_closing(np.vstack([H[::-1], H]), structure=np.ones((5, 5)), iterations=2)
    return R, zc, ndimage.gaussian_filter(M.astype(float), 1.5)


def gripper_render(size=(900, 900)):
    pl = new_plotter(size)
    q = np.radians([0, 111, -90, 0, 66, 0])
    poses = PIPER.fk(q, grip=0.035)
    T6 = poses["link6"]
    inv = np.linalg.inv(T6)
    for name in ("link6", "link7", "link8"):
        T = inv @ poses[name] @ PIPER.visual_origin[name]
        for mesh, c in arm_parts()[name]:
            pl.add_mesh(mesh.transform(T, inplace=False), color=c, smooth_shading=True, specular=0.25)
    pl.camera_position = [(0.0, -0.42, 0.10), (0.0, 0.0, 0.085), (0, 0, 1)]
    pl.camera.view_angle = 30
    pl.camera.roll = 180
    return trim(shot(pl))


def side_view(ax):
    R, zc, F = mirrored("tip", 3_000_000, 0)
    Rf, zf, Ff = mirrored("flange", 1_500_000, 50)
    above, below = np.where(zc[None, :] >= 0, F, 0), np.where(zc[None, :] < 0, F, 0)
    ax.contourf(R, zc, above.T, levels=[0.5, 2], colors=[BLUE], alpha=0.12)
    ax.contourf(R, zc, below.T, levels=[0.5, 2], colors=[BLUE], alpha=0.05)
    ax.contour(R, zc, F.T, levels=[0.5], colors=[BLUE], linewidths=2)
    ax.contour(Rf, zf, Ff.T, levels=[0.5], colors=[MUTED], linewidths=1)
    # mount plane
    ax.axhline(0, color=INK2, lw=1.2)
    ax.fill_between([-1.1, 1.1], -0.02, 0, color=PLY, zorder=1)
    # sketch dimensions from the issue: R <= 0.93 m, 1.10 m tall
    for x in (-0.93, 0.93):
        ax.plot([x, x], [0, 1.10], color=ORANGE, lw=1.5, ls=(0, (5, 3)))
    ax.plot([-0.93, 0.93], [1.10, 1.10], color=ORANGE, lw=1.5, ls=(0, (5, 3)))
    # stick figures
    for q, col, lw in ((REST, MUTED, 3), (UP, "#b9b8b1", 3), (PICK, INK2, 3.5)):
        c = chain(q)
        x = np.hypot(c[:, 0], c[:, 1]) * np.sign(c[:, 0] + 1e-9)
        ax.plot(x, c[:, 2], color=col, lw=lw, solid_capstyle="round", zorder=5)
        ax.plot(x[1:-1], c[1:-1, 2], "o", ms=5, color=col, mec=SURFACE, mew=1.5, zorder=6)
    ax.add_patch(patches.Rectangle((-0.05, 0), 0.10, 0.123, color=INK2, zorder=4))

    kw = dict(fontsize=11.5, color=INK, zorder=10)
    lead = dict(arrowstyle="-", color=MUTED, lw=0.8)
    ax.annotate("fingertip reach 0.77 m", xy=(0.765, 0.123), xytext=(0.30, 0.62), arrowprops=lead, **kw)
    ax.annotate("flange reach 0.63 m\n(the 626 mm spec)", xy=(-0.443, 0.566), xytext=(-0.97, 0.80), arrowprops=lead, **kw)
    ax.annotate("fingertip max height 0.89 m", xy=(0, 0.888), xytext=(0.08, 0.96), arrowprops=lead, **kw)
    ax.text(-0.91, 1.13, "sketched enclosure: R 0.93 m × 1.10 m tall", fontsize=11.5, color=INK2)
    ax.annotate("rest pose: elbow sits\n0.28 m behind the base", xy=(-0.28, 0.16), xytext=(-0.90, 0.40),
                arrowprops=lead, **kw)
    ax.text(-0.90, -0.30, "below the mount plane only if the\nbase sits at a deck edge (to −0.40 m)",
            fontsize=10.5, color=INK2)
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-0.45, 1.25)
    ax.set_aspect("equal")
    ax.set_xlabel("horizontal distance from the base axis (m)")
    ax.set_ylabel("height above the mounting surface (m)")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_reach():
    img, grip = hero_render(), gripper_render()
    fig = plt.figure(figsize=(15, 7.2), dpi=150)
    a0 = fig.add_axes([0.08, 0.20, 0.34, 0.68])
    a0.imshow(img)
    a0.axis("off")
    ag = fig.add_axes([0.012, 0.09, 0.11, 0.26])
    ag.imshow(grip)
    ag.axis("off")
    fig.text(0.015, 0.025, "gripper, fully open\n0–70 mm · 40 N (50 N max)", ha="left", fontsize=10.5,
             color=INK2)
    a1 = fig.add_axes([0.46, 0.10, 0.53, 0.78])
    side_view(a1)
    fig.text(0.012, 0.955, "AgileX PiPER + parallel gripper, rendered from AgileX's own URDF and meshes",
             fontsize=16, weight="bold", color=INK)
    fig.text(0.012, 0.915, "Right: side view of everywhere the fingertip can go (blue) and the flange (gray), "
             "with pick, straight-up and rest poses; the sketched enclosure is in orange.", fontsize=11.5, color=INK2)
    fig.savefig(OUT / "piper-reach.png", dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------- figure 2
H_ENC = 1.10
OPTIONS = [
    # name, (x0, x1, y0, y1) footprint in m, base xy, J1 heading (deg) of the rest pose
    ("Quarter dome, as sketched", (0.0, 0.93, 0.0, 0.93), (0.07, 0.86), -45),
    ("Half dome, as sketched", (-0.93, 0.93, 0.0, 0.93), (0.0, 0.86), -90),
    ("Full dome, as sketched", (-0.93, 0.93, -0.93, 0.93), (0.0, 0.0), -60),
    ("Spot D with the second table, arm centred", (-0.645, 0.645, -0.68, 0.68), (0.0, 0.0), -60),
]


def outside_share(foot, base, n=3_000_000):
    """Share of the reachable fingertip volume (above the mount) that lies outside the walls.

    Treats the workspace as a solid of revolution about J1 (J1's +/-150 deg plus flipping over the top covers
    every azimuth), so each reachable (r, z) cell is a ring weighted by 2*pi*r.
    """
    r, z, H = envelope_grid(n=n, key="tip")
    rc, zc = (r[:-1] + r[1:]) / 2, (z[:-1] + z[1:]) / 2
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    x0, x1, y0, y1 = foot
    out = np.array([np.mean(~((base[0] + rr * np.cos(th) > x0) & (base[0] + rr * np.cos(th) < x1)
                              & (base[1] + rr * np.sin(th) > y0) & (base[1] + rr * np.sin(th) < y1))) for rr in rc])
    W = H[:, zc >= 0] * rc[:, None]
    return float((W * out[:, None]).sum() / W.sum())


def rest_elbow_clear(foot, base, heading):
    """Distance from the rest-pose elbow (and wrist) to the nearest wall; negative = through the wall."""
    P = PIPER.fk(REST)
    c, s = np.cos(np.radians(heading)), np.sin(np.radians(heading))
    worst = np.inf
    for link in ("link3", "link4", "link2"):
        x, y = P[link][:2, 3]
        wx, wy = base[0] + c * x - s * y, base[1] + s * x + c * y
        x0, x1, y0, y1 = foot
        worst = min(worst, wx - x0, x1 - wx, wy - y0, y1 - wy)
    return worst


def enclosure_render(foot, base, heading, phis, dist, size=(1100, 900)):
    """Same camera for every option (scene recentred on the footprint), so the panels share one scale."""
    x0, x1, y0, y1 = foot
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, x1, y0, y1 = x0 - cx, x1 - cx, y0 - cy, y1 - cy
    bx, by = base[0] - cx, base[1] - cy
    pl = new_plotter(size)
    lo, hi = (x0, y0, 0.0), (x1, y1, H_ENC)
    pl.add_mesh(pv.Box(bounds=(x0 - 0.03, x1 + 0.03, y0 - 0.03, y1 + 0.03, -0.02, 0.0)), color=PLY, ambient=0.15)
    add_frame(pl, lo, hi)
    dome = dome_mesh(phis, dist, (bx, by, 0.0), zmin=0.0)
    b = (x0, x1, y0, y1, -0.01, H_ENC)
    inside, outside = dome.clip_box(b, invert=False), dome.clip_box(b, invert=True)
    if inside.n_cells:
        pl.add_mesh(inside, color=BLUE, opacity=0.15, smooth_shading=True, specular=0.0)
    if outside.n_cells:
        pl.add_mesh(outside, color=ORANGE, opacity=0.45, smooth_shading=True, specular=0.0)
    T = np.eye(4)
    c, s = np.cos(np.radians(heading)), np.sin(np.radians(heading))
    T[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    T[:3, 3] = (bx, by, 0.0)
    add_arm(pl, REST, base=T, grip=0.0)
    pl.camera_position = [(2.9, -4.3, 3.1), (0.0, 0.0, 0.40), (0, 0, 1)]
    pl.camera.view_angle = 30
    return shot(pl)


def fig_options():
    phis, dist = outer_profile()
    imgs = [enclosure_render(foot, base, heading, phis, dist) for _, foot, base, heading in OPTIONS]
    # one crop box for all four, so the scale stays shared
    bg = np.array([int(SURFACE[i:i + 2], 16) for i in (1, 3, 5)])
    masks = [np.abs(im[..., :3].astype(int) - bg).sum(-1) > 6 for im in imgs]
    ys = np.concatenate([np.where(m)[0] for m in masks])
    xs = np.concatenate([np.where(m)[1] for m in masks])
    y0, y1, x0, x1 = ys.min() - 10, ys.max() + 10, xs.min() - 10, xs.max() + 10
    fig = plt.figure(figsize=(15, 11.2), dpi=150)
    fig.text(0.012, 0.972, "PiPER reach vs. the enclosure options (1.10 m tall, all four at the same scale)",
             fontsize=16, weight="bold", color=INK)
    fig.text(0.012, 0.947, "Blue = fingertip reach inside the frame; orange = reach that passes through a wall. "
             "The arm is in its rest pose. Cloth panels omitted.", fontsize=11.5, color=INK2)
    for k, (name, foot, base, heading) in enumerate(OPTIONS):
        col, row = k % 2, k // 2
        ax = fig.add_axes([0.01 + 0.5 * col, 0.475 - 0.455 * row, 0.48, 0.37])
        ax.imshow(imgs[k][y0:y1, x0:x1])
        ax.axis("off")
        share, clear = outside_share(foot, base), rest_elbow_clear(foot, base, heading)
        w, d = foot[1] - foot[0], foot[3] - foot[2]
        rest = ("rest pose clears the walls" if clear > 0.05 else
                f"rest-pose elbow goes {abs(clear) * 100:.0f} cm through a wall")
        if 0 < share < 0.2:
            hw = min(foot[1] - foot[0], foot[3] - foot[2]) / 2
            reach = dist.max()
            rest += (f" · overshoot ≤ {(reach - hw) * 100:.0f} cm, only below "
                     f"{SHOULDER_Z + np.sqrt(reach ** 2 - hw ** 2):.2f} m")
        fig.text(0.02 + 0.5 * col, 0.905 - 0.455 * row, f"{'abcd'[k]}) {name}", fontsize=13.5, weight="bold",
                 color=INK)
        fig.text(0.02 + 0.5 * col, 0.862 - 0.455 * row,
                 f"{w:.2f} × {d:.2f} m · {share:.0%} of the fingertip's reach is outside the walls\n{rest}",
                 fontsize=11.5, color=INK2, linespacing=1.4)
        print(name, f"outside share {share:.3f}, rest clearance {clear:.3f} m")
    fig.savefig(OUT / "enclosure-options.png", dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------- figure 3
PLAN_PDF = OUT.parents[1] / "cb154.pdf"
M_PER_PX = 25 / 72 * 0.3048 / 12.5  # plan scale 1" = 25'-0", rendered at 900 dpi (12.5 px/pt)
ORIGIN_PX = (206, 189)  # inner face of the page-top-left corner of room 154 in the crop below


def plan_image():
    import pymupdf

    page = pymupdf.open(PLAN_PDF)[0]
    s = page.rect.width / 2000
    pix = page.get_pixmap(dpi=900, clip=pymupdf.Rect(1000 * s, 690 * s, 1225 * s, 915 * s), colorspace="gray")
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    x0, y0 = ORIGIN_PX
    extent = (-x0 * M_PER_PX, (pix.width - x0) * M_PER_PX, (pix.height - y0) * M_PER_PX, -y0 * M_PER_PX)
    return img, extent


def m(px, py):
    return (px - ORIGIN_PX[0]) * M_PER_PX, (py - ORIGIN_PX[1]) * M_PER_PX


def floor_plan(ax, reach):
    img, extent = plan_image()
    ax.imshow(img, cmap="gray", extent=extent, vmin=0, vmax=255, alpha=0.75)
    box = dict(boxstyle="round,pad=0.2", fc=SURFACE, ec="none", alpha=0.9)
    lab = dict(fontsize=11, color=INK, zorder=12, bbox=box)
    # atomizer clean room, 14 x 10 ft from the page-top-left corner (#31) -- approximate
    ax.add_patch(patches.Rectangle((0, 0), 14 * 0.3048, 10 * 0.3048, facecolor="none", edgecolor=MUTED, hatch="///",
                                   lw=0, zorder=3))
    ax.text(2.13, 1.52, "atomizer clean room\n(≈14 × 10 ft, #31)", ha="center", va="center", fontsize=10.5,
            color=INK2, zorder=12, bbox=dict(boxstyle="round,pad=0.25", fc=SURFACE, ec="none"))
    # D: two tables against room 158's wall, clear of door 154-1's swing
    dx0, dy1 = m(345, 815)
    d = (dx0, dy1 - 1.36, 1.29, 1.36)
    cx, cy = d[0] + d[2] / 2, d[1] + d[3] / 2
    ax.add_patch(patches.Rectangle((cx - 0.93, cy - 0.93), 1.86, 1.86, fill=False, ec=ORANGE, lw=1.5,
                                   ls=(0, (4, 3)), zorder=8))
    ax.add_patch(patches.Rectangle(d[:2], d[2], d[3], facecolor=BLUE, alpha=0.18, ec=BLUE, lw=2, zorder=9))
    ax.add_patch(patches.Circle((cx, cy), reach, fill=False, ec=BLUE, lw=1.2, zorder=9))
    ax.plot(cx, cy, "o", ms=7, color=BLUE, mec=SURFACE, mew=2, zorder=10)
    ax.annotate("D + second table: 1.29 × 1.36 m,\narm centred (door 154-1 is locked)", xy=(d[0] + d[2], d[1] + 0.2),
                xytext=(3.0, 3.45), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8), **lab)
    ax.annotate("sketched full dome (1.86 m) centred on D\nruns into room 158 and the door swing",
                xy=(cx + 0.93, cy + 0.55), xytext=(3.0, 4.35), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8),
                fontsize=10.5, color=INK2, zorder=12, bbox=box)
    # E: centre island (approximate)
    e = (3.3, 5.9, 1.36, 1.29)
    ax.add_patch(patches.Rectangle(e[:2], e[2], e[3], facecolor=AQUA, alpha=0.15, ec=AQUA, lw=2, zorder=9))
    ax.text(e[0] + e[2] / 2, e[1] + e[3] / 2, "E ≈\n1.36 × 1.29", ha="center", va="center", **lab)
    # north arrow (the plan's own arrow points to the page's left)
    ax.annotate("", xy=(5.6, 8.35), xytext=(6.6, 8.35), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5))
    ax.text(6.1, 8.12, "N", ha="center", fontsize=11, weight="bold", color=INK)
    x, y = m(401, 584)
    ax.text(x + 0.35, y, "pillar", va="center", fontsize=9.5, color=INK2, zorder=12)
    x, y = m(640, 1250)
    ax.text(x + 0.05, y - 0.1, "entrance", ha="center", va="center", fontsize=9.5, color=INK2, zorder=12)
    ax.set_xlim(-0.6, 8.6)
    ax.set_ylim(10.4, -0.6)
    ax.set_aspect("equal")
    ax.axis("off")


def elevation(ax, profile):
    """Height budget for the two-level idea, drawn to scale (m)."""
    phis, dist = profile
    ceiling, sprinkler = 103 * 0.0254, 18 * 0.0254

    def arm_envelope(x0, z0):
        r = dist * np.cos(phis)
        z = np.maximum(z0 + SHOULDER_Z + dist * np.sin(phis), z0)
        xs, zs = np.concatenate([x0 - r[::-1], x0 + r]), np.concatenate([z[::-1], z])
        ax.fill(xs, zs, color=BLUE, alpha=0.14, lw=0, zorder=3)
        ax.plot(xs, zs, color=BLUE, lw=1.5, zorder=4)
        ax.add_patch(patches.Rectangle((x0 - 0.05, z0), 0.10, SHOULDER_Z, color=INK2, zorder=5))

    def stack(x0, lower, clear, enc, title, sub):
        w, t, deck = 1.8, 0.04, lower + clear
        ax.add_patch(patches.Rectangle((x0, lower - t), w, t, color="#b9b8b1", zorder=2))
        ax.add_patch(patches.Rectangle((x0, deck), w, t, color="#b9b8b1", zorder=2))
        for x in (x0 + 0.03, x0 + w - 0.07):
            ax.add_patch(patches.Rectangle((x, 0), 0.04, deck, color="#d6d4cd", zorder=1))
        ax.add_patch(patches.Rectangle((x0, deck + t), w, enc, fill=False, ec=ORANGE, lw=1.5, ls=(0, (5, 3)),
                                       zorder=6))
        arm_envelope(x0 + w / 2, deck + t)
        ax.text(x0 + w / 2, lower + clear / 2, f"{clear:.1f} m clear\nfor other projects", ha="center",
                va="center", fontsize=10, color=INK2)
        top = deck + t + enc
        ax.text(x0 + w / 2, 3.32, title, ha="center", fontsize=11.5, weight="bold", color=INK)
        ax.text(x0 + w / 2, 3.03, sub.format(deck=deck + t, top=top, spare=ceiling - top), ha="center",
                fontsize=10.5, color=INK2, linespacing=1.35)

    stack(0.0, 0.91, 0.60, 1.10, "As imagined: bench + deck + 1.1 m cell",
          "deck at {deck:.2f} m (about eye height)\ntop at {top:.2f} m: above the ceiling")
    stack(2.2, 0.76, 0.50, 0.95, "Hutch: desk + 0.5 m + trimmed cell",
          "deck at {deck:.2f} m, 0.95 m cell\ntop at {top:.2f} m, {spare:.2f} m spare")
    ax.axhline(ceiling, color=INK, lw=1.2)
    ax.text(4.0, ceiling + 0.035, f"usable ceiling ≈ 103 in ({ceiling:.2f} m, #7)", ha="right", fontsize=10,
            color=INK2)
    ax.axhspan(ceiling - sprinkler, ceiling, color=ORANGE, alpha=0.08, lw=0)
    ax.text(4.0, ceiling - sprinkler / 2 + 0.04, "18 in clearance below sprinkler heads,\nif the room is sprinklered",
            ha="right", va="center", fontsize=10, color=INK2)
    ax.axhline(0, color=INK2, lw=1.2)
    ax.set_xlim(-0.1, 4.05)
    ax.set_ylim(0, 3.5)
    ax.set_aspect("equal")
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])
    ax.set_ylabel("height above floor (m)")
    ax.set_xticks([])
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def fig_floor():
    profile = outer_profile()
    fig = plt.figure(figsize=(15, 8.6), dpi=150)
    fig.text(0.012, 0.965, "Where it could go in CB154 (to scale, from cb154.pdf)", fontsize=16, weight="bold",
             color=INK)
    fig.text(0.012, 0.93, "Left: room 154 is 7.8 × 9.6 m (25.8 × 31.4 ft); spots D and E are from the issue, the blue "
             "circle is the 0.77 m fingertip reach. Right: height budget for a two-level setup.", fontsize=11.5,
             color=INK2)
    floor_plan(fig.add_axes([0.0, 0.0, 0.46, 0.90]), profile[1].max())
    elevation(fig.add_axes([0.52, 0.06, 0.47, 0.82]), profile)
    fig.savefig(OUT / "cb154-arm-locations.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] or ["reach", "options", "floor"]
    if "reach" in targets:
        fig_reach()
    if "options" in targets:
        fig_options()
    if "floor" in targets:
        fig_floor()
