"""Check views of the measured stack (stack_model.py):

    renders/landing_window.png   side elevation in the axis's vertical plane, measured against the earlier estimate:
                                 where a vertical melt stream can land on the plate without meeting the upper
                                 sonotrode first, with the plate hanging straight down the stack's slope
    renders/stack_3d.png         the tip of the stack in the chamber's orientation, from the front view port's side
                                 (as in the Oct 6 photo in byu-vcl issue 261) and from above the plate's face

    xvfb-run -a python renders.py
"""
from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
import numpy as np                                   # noqa: E402
from matplotlib.patches import Arc, Polygon          # noqa: E402

import stack_model as S                              # noqa: E402

OUT = S.HERE / "renders"
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
GOOD, CRITICAL = "#0ca30c", "#d03b3b"                # status colours, always with a text label beside them
MELT = "#f28c28"
RUN_T = 75.0                                         # the measured set-up's landing point, mm from the hole


def to_rgb(c):
    return tuple(c)


def side(ax, d: S.Dims, run_t: float, title: str, subtitle: str, extra_stream: float | None = None):
    """The stack in the axis's vertical plane (x right, into the chamber; z up), the hole's centre on the plate's face
    at the origin. The plate is edge-on: its 20.8 mm width runs into the page."""
    a = math.radians(d.stack_angle)
    n = np.array([math.cos(a), math.sin(a)])         # the axis
    u = np.array([math.sin(a), -math.cos(a)])        # along the plate, straight down the slope
    T, R, e, Lp, Lu = d.plate_t, d.upper_d / 2, d.hole_e, d.plate_l, d.upper_l
    rs = S.STREAM_R
    face0 = np.zeros(2)                               # hole centre on the plate's melt-side face
    back0 = face0 - T * n                             # ... on its back face = the Ti sonotrode's tip face

    def quad(p0, du0, du1, dn0, dn1, base):
        return [base + du0 * u + dn0 * n, base + du1 * u + dn0 * n, base + du1 * u + dn1 * n, base + du0 * u + dn1 * n]

    # Ti sonotrode (cut off 60 mm back), plate, upper sonotrode
    ax.add_patch(Polygon(quad(None, -S.MEASURED.sono_d / 2 if d is S.MEASURED else -d.sono_d / 2, d.sono_d / 2,
                              -60.0, 0.0, back0), closed=True, fc=S.TITANIUM, ec=INK2, lw=0.6, zorder=2))
    ax.add_patch(Polygon(quad(None, -e, Lp - e, 0.0, T, back0), closed=True, fc=S.CARBON, ec=S.CARBON, lw=0.6,
                         zorder=3))
    ax.add_patch(Polygon(quad(None, -R, R, 0.0, Lu, face0), closed=True, fc=S.W_ALLOY, ec=INK2, lw=0.6, zorder=3))
    brk = back0 - 60.0 * n
    ax.plot(*np.array([brk - (d.sono_d / 2 + 3) * u, brk + (d.sono_d / 2 + 3) * u]).T, color=INK2, lw=0.8, ls=(0, (3, 2)),
            zorder=4)

    # the upper sonotrode's shadow: plate points whose vertical line meets it first
    lo, hi = S.landing_window(d)
    top_right = face0 + R * u + Lu * n
    shadow_end = face0 + (R + Lu / math.tan(a)) * u
    ax.add_patch(Polygon([face0 + R * u, top_right, shadow_end], closed=True, fc=CRITICAL, alpha=0.12, ec="none",
                         zorder=1))
    ax.plot(*np.array([top_right, shadow_end]).T, color=CRITICAL, lw=0.8, ls=(0, (4, 2)), zorder=4)
    # bands on the plate's face: blocked, then the landing window
    off = 1.6
    for t0, t1, c in ((-e, lo, CRITICAL), (lo, hi, GOOD)):
        p = np.array([face0 + t0 * u + off * n, face0 + t1 * u + off * n])
        ax.plot(*p.T, color=c, lw=3.2, solid_capstyle="butt", zorder=5)

    # the stream where the set-up puts it, and optionally the Oct 6 one
    land = face0 + run_t * u
    ax.add_patch(Polygon([land + [-rs, 0], land + [rs, 0], land + [rs, 120], land + [-rs, 120]], closed=True, fc=MELT,
                         ec="none", zorder=6))
    if extra_stream is not None:
        # with the stack slid in, the stream's line sits extra_stream mm from the hole along the plate; it meets the
        # upper sonotrode's top first
        x = (face0 + extra_stream * u)[0]
        z_hit = None
        for z in np.linspace(130, -40, 3400):
            w = np.array([x, z]) - face0
            ta, tr = w @ n, w @ u
            if 0 <= ta <= Lu and abs(tr) <= R + rs:
                z_hit = z
                break
        if z_hit is not None:
            ax.plot([x, x], [120, z_hit], color=MELT, lw=2.2, ls=(0, (2, 2)), zorder=6)
            ax.annotate("slid in (Oct 6):\nthe stream meets the\nupper sonotrode", (x, z_hit + 4), (x - 70, z_hit + 60),
                        fontsize=8.5, color=INK2, ha="left", arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))

    # labels
    c_up = face0 + Lu * 0.55 * n - (R + 2) * u
    ax.annotate(f"upper sonotrode\nØ{d.upper_d:.1f} × {d.upper_l:.1f}", c_up, c_up + np.array([-75, 18]),
                fontsize=9, color=INK, ha="left", arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    c_pl = face0 + (Lp - e - 8) * u
    ax.annotate(f"plate {d.plate_l:.1f} × {d.plate_w:.1f}\n(hole {e:.1f} from its back end)", c_pl,
                c_pl + np.array([6, -24]), fontsize=9, color=INK, ha="left",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    c_ti = back0 - 40 * n - (d.sono_d / 2) * u
    ax.annotate("Ti sonotrode", c_ti, c_ti + np.array([-62, 14]), fontsize=9, color=INK, ha="left",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    mid = face0 + (lo + hi) / 2 * u + 4 * n
    ax.annotate(f"landing window\n{lo:.1f} to {hi:.1f} mm from the hole\n({hi - lo:.0f} mm of plate)", mid,
                mid + np.array([20, 34]), fontsize=9, color=INK, ha="left", fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=GOOD, lw=0.9))
    sh = face0 + (lo * 0.45) * u + 3 * n
    ax.annotate("upper sonotrode in\nthe stream's way", sh, sh + np.array([-4, -52]), fontsize=8.5, color=INK2,
                ha="center", arrowprops=dict(arrowstyle="-", color=CRITICAL, lw=0.9))
    ax.text(land[0] + 4, land[1] + 104, f"melt stream, landing\n{run_t:.0f} mm from the hole", fontsize=8.5, color=INK2,
            ha="left", va="top")
    # the stack's angle, at the Ti sonotrode
    pivot = back0 - 48 * n
    ax.plot([pivot[0], pivot[0] + 30], [pivot[1], pivot[1]], color=INK2, lw=0.6)
    ax.add_patch(Arc(pivot, 44, 44, theta1=0, theta2=d.stack_angle, color=INK2, lw=0.8))
    ax.text(pivot[0] + 25, pivot[1] + 6, f"{d.stack_angle:.0f}°", fontsize=9.5, color=INK)

    ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold", pad=18)
    ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom")
    ax.set_aspect("equal")
    ax.set_xlim(-135, 200)
    ax.set_ylim(-125, 128)
    ax.axis("off")
    # 20 mm scale bar
    ax.plot([-125, -105], [-118, -118], color=INK, lw=1.5)
    ax.text(-115, -114, "20 mm", fontsize=8, color=INK2, ha="center")


def landing_figure():
    fig, axs = plt.subplots(1, 2, figsize=(16, 7.4), facecolor=SURFACE)
    lo_e, hi_e = S.landing_window(S.ESTIMATED_2026_10_07)
    side(axs[0], S.MEASURED, RUN_T, "Measured (byu-vcl issue 261, 2026-10-08)",
         "stack at 45°, plate square to it, hanging straight down its slope", extra_stream=31.0)
    side(axs[1], S.ESTIMATED_2026_10_07, (lo_e + hi_e) / 2, "Earlier estimate (video frames, 2026-10-07)",
         "stack at 40°, plate 100 × 20, upper sonotrode Ø20 × 55, same clocking")
    fig.suptitle("Where a vertical melt stream can land on the plate, side view in the stack's vertical plane",
                 x=0.012, ha="left", fontsize=13.5, color=INK, y=0.985)
    fig.text(0.012, 0.015, "Sizes in mm. Measured: upper sonotrode, plate length and width, the hole flush with the "
             "sonotrodes' edge, 45°. Estimates: plate thickness 2.5, Ti sonotrode as wide as the upper one, "
             f"stream radius {S.STREAM_R}.\nThe stack slides along its axis in its housing, so how far it is slid in "
             "sets where the stream lands. The plate's 20.8 mm width runs into the page.", fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.08, wspace=0.03)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "landing_window.png", dpi=130, facecolor=SURFACE)
    plt.close(fig)


def view_3d():
    """PyVista render of the stack's tip (Ti sonotrode end, plate, upper sonotrode) at 45 deg in the chamber's frame,
    with the stream landing RUN_T from the hole."""
    import pyvista as pv
    import cadquery as cq

    d = S.MEASURED
    n, al, ac = S.axes(d, clock=0.0)
    # place the stack frame: origin at the tip face's centre, so the hole centre on the plate's face is at T * n
    land_local = np.array([RUN_T, 0.0, d.plate_t])
    origin = -(land_local[0] * al + land_local[2] * n)          # the landing point at the world origin

    def world(shape):
        from OCP.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf
        t = gp_Trsf()
        t.SetDisplacement(gp_Ax3(), gp_Ax3(gp_Pnt(*map(float, origin)), gp_Dir(*map(float, n)),
                                           gp_Dir(*map(float, al))))
        return shape.moved(cq.Location(t))

    def mesh(shape, tol=0.05):
        vs, fs = shape.tessellate(tol, 0.2)
        v = np.array([(p.x, p.y, p.z) for p in vs])
        f = np.hstack([[3, *tri] for tri in fs])
        return pv.PolyData(v, f).compute_normals(split_vertices=True, feature_angle=35)

    shapes = S.parts(d)
    shapes["ti_sonotrode"] = (S.ti_sonotrode(d).intersect(S.zc(40, -70, 5)), S.TITANIUM)
    pl = pv.Plotter(off_screen=True, window_size=(1700, 900), shape=(1, 2), border=False)
    for col, (cam, label) in enumerate((((0.02, -1.0, 0.38), "from the front view port's side (cf. the Oct 6 photo)"),
                                        ((0.55, -0.55, 0.62), "from above the plate, front right"))):
        pl.subplot(0, col)
        pl.set_background(SURFACE)
        for k, (s, rgb) in shapes.items():
            if k == "connector_m8":
                continue
            pl.add_mesh(mesh(world(s)), color=rgb, smooth_shading=True, specular=0.25, specular_power=12)
        stream = pv.Cylinder(center=(0, 0, 60), direction=(0, 0, 1), radius=S.STREAM_R, height=120, resolution=24)
        pl.add_mesh(stream, color=MELT, smooth_shading=True)
        focus = np.array([-38.0, 0.0, 36.0])
        cam = np.array(cam) / np.linalg.norm(cam)
        pl.camera.position = tuple(focus + 470 * cam)
        pl.camera.focal_point = tuple(focus)
        pl.camera.up = (0, 0, 1)
        pl.camera.view_angle = 26
        pl.add_text(label, position="upper_left", font_size=12, color=INK2)
    pl.screenshot(str(OUT / "stack_3d.png"))
    pl.close()


if __name__ == "__main__":
    landing_figure()
    view_3d()
    print("wrote", *(p.name for p in sorted(OUT.glob("*.png"))))
