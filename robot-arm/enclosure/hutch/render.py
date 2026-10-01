"""Figures and the assembly GIF for the spot D hutch (#229).

    xvfb-run -a python render.py [side] [exploded] [still] [options] [sheets] [gif]

The GIF is kept light: 600 x 450, one camera, one shared palette, about 70 frames.
"""

import json
import sys
import time

import matplotlib
import numpy as np
import pyvista as pv
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402

import build as B  # noqa: E402
import hutch as H  # noqa: E402
from piper_fk import Piper  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8983", "#e4e2dd"
BLUE, ORANGE = "#2a78d6", "#eb6834"
PLY, PLY_CUT = "#e3d2ad", "#c9a86a"
REACH_Q = None


def ease(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def translate(v):
    M = np.eye(4)
    M[:3, 3] = v
    return M


def full_reach():
    """Joint angles for the stretched arm (the FE load case), from loads.py."""
    global REACH_Q
    if REACH_Q is None:
        REACH_Q = np.radians(json.loads((B.HERE / "fea-results.json").read_text())["pose_deg"])
    return REACH_Q


# ------------------------------------------------------------------ side view (a section at x = 0)
def side_view(path):
    piper = Piper()
    fig, ax = plt.subplots(figsize=(11, 10.2), dpi=120, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    th = H.TABLE["h"]
    yc, W, T, C = H.YC, H.W, H.T, H.CLEAR
    z0 = th                                   # draw from the floor: table top at z = th

    def rect(y0, y1, z_0, z_1, fc, ec=INK2, lw=0.8, **kw):
        ax.add_patch(patches.Rectangle((y0, z0 + z_0), y1 - y0, z_1 - z_0, fc=fc, ec=ec, lw=lw, **kw))

    # floor, wall, ceiling
    ax.axhline(0, color=INK2, lw=1.2)
    ax.add_patch(patches.Rectangle((H.WALL_Y, 0), 0.08, 2.75, fc="#ecebe7", ec=INK2, lw=0.8, hatch="///"))
    ceiling = 103 * H.IN
    ax.plot([-0.9, H.WALL_Y], [ceiling, ceiling], color=INK, lw=1.1)
    ax.text(-0.88, ceiling + 0.03, "usable ceiling ≈ 103 in (2.62 m, #7)", fontsize=9.5, color=INK2)
    # tables: two tops and schematic legs, height assumed
    ty = H.TABLE["y"] / 2
    for a, b in ((-ty, -0.0015), (0.0015, ty)):
        rect(a, b, -0.03, 0, "#26272a", ec="#26272a")
        for y in (a + 0.04, b - 0.07):
            ax.add_patch(patches.Rectangle((y, 0), 0.03, th - 0.03, fc="#d6d4cd", ec=INK2, lw=0.6))
    ax.text(-0.66, th / 2, f"tables at D\n(top at {th:.2f} m,\nassumed; measure it)", fontsize=9, color=INK2,
            va="center")

    # far side panel as a backdrop, then the cut parts
    rect(yc - W / 2, yc + W / 2, 0, C, "#f3ead6", ec=INK2)
    for b in H.boards(H.RECOMMENDED):
        if "side" in b.tags:
            continue
        y0, y1 = b.lo[1] + yc, b.hi[1] + yc
        rect(y0, y1, b.lo[2], b.hi[2], PLY_CUT if "deck" not in b.tags else PLY, ec=INK, lw=0.9)
    for s in (-1, 1):                          # foot cleat outline, beyond
        ax.plot([yc - B.CLEAT["l"] / 2, yc + B.CLEAT["l"] / 2], [z0 + B.CLEAT["w"]] * 2, color=INK2, lw=0.6, ls=":")

    # the dome: posts beyond, rails in section, canvas as lines
    zt = H.deck_top()
    sp, od = B.D.SPAN, B.P.PIPE_OD
    for s in (-1, 1):
        y = yc + s * sp["y"] / 2
        ax.add_patch(patches.Rectangle((y - od / 2, z0 + zt), od, B.D.OUTER["z"], fc="#f1f1ee", ec=INK2, lw=0.7))
        for z in (zt + B.D.Z0, zt + B.D.Z0 + sp["z"]):
            ax.add_patch(patches.Circle((y, z0 + z), od / 2, fc="#f1f1ee", ec=INK2, lw=0.7))
    top = z0 + zt + B.D.OUTER["z"]
    ax.plot([yc - W / 2, yc + W / 2], [top, top], color="#b8ab8e", lw=2.2)
    ax.plot([yc + W / 2 + 0.004] * 2, [z0 + zt, top], color="#b8ab8e", lw=2.2)
    roll_y, roll_z = yc - sp["y"] / 2 - 0.03, top - 0.05
    ax.add_patch(patches.Circle((roll_y, roll_z), 0.03, fc="#e8dfcb", ec=INK2, lw=0.7))
    ax.text(roll_y - 0.05, roll_z + 0.05, "front flap,\nrolled up", fontsize=9, color=INK2, ha="right")

    # the arm at full reach toward the room, with the 1.5 kg payload, projected onto y-z
    q = full_reach()
    for link, m, c in B.arm_meshes(piper, q=q, keep=0.3):
        tri = m.vertices[m.faces][:, :, 1:3] + np.array([0, z0])
        from matplotlib.collections import PolyCollection
        ax.add_collection(PolyCollection(tri, facecolors=matplotlib.colors.to_hex(c * 0.85 + 0.1), edgecolors="none",
                                         zorder=5))
    tip = B.arm_base() @ np.r_[Piper().tip(q), 1]
    ax.add_patch(patches.Circle((tip[1], z0 + tip[2]), 0.025, fc=ORANGE, ec=INK, lw=0.6, zorder=6))
    ax.annotate("1.5 kg at the fingertip,\n0.77 m out (the FE load case)", xy=(tip[1], z0 + tip[2]),
                xytext=(tip[1] - 0.05, z0 + tip[2] + 0.42), fontsize=9.5, color=INK2, ha="left",
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

    # dimensions
    def dim_v(y, za, zb, text, side=1):
        ax.annotate("", xy=(y, za), xytext=(y, zb), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9,
                                                                      shrinkA=0, shrinkB=0))
        ax.text(y + side * 0.02, (za + zb) / 2, text, fontsize=9.5, color=INK, va="center",
                ha="left" if side > 0 else "right")

    hs = B.heights()
    dim_v(yc - 0.47, z0, z0 + C, f"{C * 1000:.0f} mm\nclear", side=1)
    dim_v(yc, z0, z0 + hs["under_spine"], f"{hs['under_spine'] * 1000:.0f} mm\nunder\nthe spine", side=1)
    dim_v(H.WALL_Y + 0.2, 0, z0 + hs["deck_top"], f"deck top\n{hs['floor_deck']:.2f} m", side=1)
    dim_v(H.WALL_Y + 0.2, z0 + hs["deck_top"], top, f"dome\n{B.D.OUTER['z']:.2f} m", side=1)
    ax.text(H.WALL_Y + 0.22, top + 0.03, f"top {hs['floor_top']:.2f} m", fontsize=9.5, color=INK)
    ax.annotate("spine box: two webs,\na bottom and a doubler\npad under the arm", xy=(yc + H.SPINE_Y + 0.01, z0 + C - 0.06),
                xytext=(yc + 0.25, z0 + 0.27), fontsize=9.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.annotate("back panel", xy=(yc + W / 2 - T / 2, z0 + 0.25), xytext=(yc + 0.30, z0 + 0.06), fontsize=9.5,
                color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.text(yc + 0.08, z0 + C + 0.035, "deck: the 4 × 4 ft sheet", fontsize=9.5, color=INK2)
    ax.text(yc - 0.36, z0 + 0.06, "side panel (beyond)", fontsize=9, color=MUTED)
    ax.text(-0.9, 2.84, "Spot D hutch, section through the arm (looking at the left side panel)",
            fontsize=13, color=INK, weight="bold")
    ax.text(-0.9, 2.76, "Room to the left, wall to the right. Recommended build: spine box + back panel. "
            "Floor to top assumes a 0.76 m table.", fontsize=10, color=INK2)
    ax.set_xlim(-0.95, 1.2)
    ax.set_ylim(-0.05, 2.9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(path.name)


# ------------------------------------------------------------------ 3D scenes
def plotter(size):
    pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
    pl.set_background(SURFACE)
    return pl


def add_tables(pl):
    tx, ty = B.D.TABLE["x"] / 2, B.D.TABLE["y"] / 2
    for y0, y1 in ((-ty, -0.0015), (0.0015, ty)):
        pl.add_mesh(pv.Box((-tx, tx, y0, y1, -0.03, 0)), color="#26272a", ambient=0.2)


def add_item(pl, it, offset=(0, 0, 0)):
    ply = "ply" in it.tags
    cloth = "cloth" in it.tags
    a = pl.add_mesh(pv.wrap(it.mesh), color=it.color, smooth_shading=not ply, split_sharp_edges=not ply,
                    show_edges=False, specular=0.0 if cloth else 0.25, ambient=0.35 if cloth else 0.14,
                    diffuse=0.7 if cloth else 1.0)
    e = None
    if ply:
        edges = pv.wrap(it.mesh).extract_feature_edges(feature_angle=60, boundary_edges=False, manifold_edges=False)
        e = pl.add_mesh(edges, color="#8c7650", line_width=1.2)
        e.position = offset
    a.position = offset
    return a, e


def exploded(path, size=(1300, 1200)):
    pl = plotter(size)
    piper = Piper()
    items = [it for it in B.layout() if "dome" not in it.tags]
    ex = {"deck": (0, 0, 0.80), "spine-pad": (0, 0, 0.48), "spine-web-front": (0, -0.06, 0.24),
          "spine-web-rear": (0, 0.06, 0.24), "spine-bottom": (0, 0, 0.0), "back": (0, 0.40, 0.0),
          "side-left": (-0.42, 0, 0), "side-right": (0.42, 0, 0), "cleat-left": (-0.56, 0, 0),
          "cleat-right": (0.56, 0, 0), "m5x45-socket-cap": (0, 0, -0.16)}
    labels, pts = [], []
    names = {"deck": "Deck (4 × 4 ft sheet)", "spine-pad": "Doubler pad", "spine-web-front": "Spine webs (2)",
             "spine-bottom": "Spine bottom, access holes", "back": "Back panel", "side-left": "Side panels (2)",
             "cleat-left": "Foot cleats (2)", "m5x45-socket-cap": "M5 × 45 (4)"}
    for it in items:
        off = ex.get(it.name, (0, 0, 0))
        add_item(pl, it, off)
        if it.name in names and it.name not in [n for n, _ in labels]:
            c = it.mesh.bounds.mean(axis=0) + off
            if it.name.startswith("side"):
                c = c + (0, -0.35, 0.18)
            labels.append((it.name, names[it.name]))
            pts.append(c)
    for link, m, c in B.arm_meshes(piper, q=B.D.REST, keep=None):
        pl.add_mesh(pv.wrap(m.copy().apply_translation((0, 0, 0.80 + 0.14))), color=c, smooth_shading=True,
                    specular=0.25)
    pts.append(np.array([0.0, H.YC - 0.25, H.deck_top() + 0.80 + 0.14 + 0.30]))
    labels.append(("arm", "PiPER, bolted from below"))
    pl.add_point_labels(np.array(pts), [n for _, n in labels], font_size=15, text_color=INK, shape_color="#ffffff",
                        shape_opacity=0.85, point_size=0, show_points=False, always_visible=True, margin=4)
    pl.camera_position = [(-3.5, -4.1, 1.75), (0.0, H.YC, 0.78), (0, 0, 1)]
    pl.camera.view_angle = 30
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(return_img=True)
    pl.close()
    Image.fromarray(img).save(path)
    print(path.name)


def still(path, size=(1400, 1200)):
    pl = plotter(size)
    add_tables(pl)
    piper = Piper()
    for it in B.layout():
        if "flap" in it.tags:
            continue
        add_item(pl, it)
    pl.add_mesh(pv.wrap(B.flap_roll()), color="#e8dfcb", smooth_shading=True)
    for link, m, c in B.arm_meshes(piper, q=B.D.PICK, keep=None):
        pl.add_mesh(pv.wrap(m), color=c, smooth_shading=True, specular=0.25)
    pl.camera_position = [(-2.25, -3.55, 2.3), (0.0, 0.0, 0.8), (0, 0, 1)]
    pl.camera.view_angle = 30
    pl.enable_anti_aliasing("ssaa")
    Image.fromarray(pl.screenshot(return_img=True)).save(path)
    pl.close()
    print(path.name)


# ------------------------------------------------------------------ FE comparison
def options_chart(path):
    res = json.loads((B.HERE / "fea-results.json").read_text())["options"]
    keys = list(res)
    labels = [f"{res[k]['label']}\n{res[k]['note']}" for k in keys]
    panels = [("payload_mm", "Deflection: fingertip shift when\nthe 1.5 kg payload is picked up (mm)", 0.1),
              ("sway_mm", "Sway: fingertip, J1 braking from\n180°/s at full reach (mm)", 0.1),
              ("f_hz", "First natural frequency (Hz)\nhigher settles faster", None)]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.9), dpi=120, facecolor=SURFACE, sharey=True)
    y = np.arange(len(keys))[::-1]
    for ax, (k, title, ref) in zip(axs, panels):
        v = np.array([res[o][k][0] if k == "f_hz" else res[o][k] for o in keys])
        ax.set_facecolor(SURFACE)
        ax.barh(y, v, height=0.56, color=BLUE, edgecolor=SURFACE, linewidth=2)
        for yi, vi in zip(y, v):
            ax.text(vi, yi, f"  {vi:.2f}" if k != "f_hz" else f"  {vi:.0f}", va="center", fontsize=10.5, color=INK)
        if ref:
            ax.axvline(ref, color=INK, lw=1.0, ls=(0, (4, 3)))
            ax.text(ref, -0.8, " arm's ±0.1 mm repeatability", fontsize=9, color=INK2, va="center")
        ax.set_title(title, fontsize=11.5, color=INK, loc="left")
        ax.set_xlim(0, v.max() * 1.3)
        ax.set_ylim(-1.1, len(keys) - 0.5)
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)
        ax.tick_params(colors=INK2, labelsize=9.5, left=False)
    axs[0].set_yticks(y)
    axs[0].set_yticklabels(labels, fontsize=10, color=INK)
    rec = keys.index(H.RECOMMENDED)
    axs[0].get_yticklabels()[rec].set_fontweight("bold")
    fig.text(0.01, 0.98, "Hutch options from the plywood shell model: arm at full reach with 1.5 kg, worst J1 direction",
             fontsize=13, color=INK, weight="bold", va="top")
    fig.text(0.01, 0.925, "Deflection repeats every time the arm reaches there, so it only costs accuracy when the load "
             "changes. Sway is the swing that has to die out after each move.", fontsize=10, color=INK2, va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(path.name)


def sheets(path):
    plan, left = B.sheet_plan()
    fig, axs = plt.subplots(1, 2, figsize=(11, 8.2), dpi=120, facecolor=SURFACE,
                            gridspec_kw=dict(width_ratios=[1, 1]))
    names = {"deck": "Deck", "side-left": "Side", "side-right": "Side", "spine-web-front": "Web",
             "spine-web-rear": "Web", "back": "Back", "spine-bottom": "Spine bottom", "spine-pad": "Pad",
             "cleat-left": "Cleat", "cleat-right": "Cleat"}
    for ax, sheet, (sw, sl) in ((axs[0], plan[0][0], B.SHEET_4x4), (axs[1], plan[1][0], B.SHEET_4x8)):
        ax.set_facecolor(SURFACE)
        ax.add_patch(patches.Rectangle((0, 0), sw, sl, fc="#f4efe4", ec=INK, lw=1.2))
        for s, nm, x, y, w, l in plan:
            if s != sheet:
                continue
            ax.add_patch(patches.Rectangle((x, y), w, l, fc=PLY, ec="#8c7650", lw=1.0))
            rot = 90 if l > 2.2 * w else 0
            if nm == "cleat-right":
                continue
            txt = f"{names[nm]}\n{l * 1000:.0f} × {w * 1000:.0f}" if w > 0.15 else \
                (f"{names[nm]} {l * 1000:.0f} × {w * 1000:.0f}" if w > 0.06 else "Cleats (2), 1180 × 40")
            xt = x + w / 2 if nm != "cleat-left" else x + w + 0.015
            ax.text(xt, y + l / 2, txt, ha="center", va="center", fontsize=8.5, color=INK, rotation=rot)
        ax.annotate("", xy=(-0.05, sl * 0.72), xytext=(-0.05, sl * 0.28),
                    arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.9))
        ax.text(-0.07, sl / 2, "face grain", rotation=90, ha="right", va="center", fontsize=9, color=INK2)
        ax.set_title(sheet, fontsize=11.5, color=INK, loc="left")
        ax.set_xlim(-0.12, B.SHEET_4x8[0] + 0.02)
        ax.set_ylim(-0.02, B.SHEET_4x8[1] + 0.02)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.01, 0.985, "Cut plan, mm (1/8 in kerf between parts)", fontsize=13, color=INK, weight="bold", va="top")
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(path.name)


# ------------------------------------------------------------------ GIF
MOVE, LAST = 7, 16
MOVE_MS, HOLD_MS = 70, 1300
CAMERA = [(-2.5, -3.75, 2.45), (0.0, 0.0, 0.78), (0, 0, 1)]


def gif(path, size=(600, 450)):
    t0 = time.time()
    pl = plotter(size)
    add_tables(pl)
    items = B.layout()
    pairs = [add_item(pl, it) for it in items]
    actors = [a for a, _ in pairs]
    edges = [e for _, e in pairs]
    flap = next(a for a, it in zip(actors, items) if "flap" in it.tags)
    roll = pl.add_mesh(pv.wrap(B.flap_roll()), color="#e8dfcb", smooth_shading=True)
    piper = Piper()
    arm = []
    for link, m, c in B.arm_meshes(piper, keep=0.3, world=False):
        arm.append((link, pl.add_mesh(pv.wrap(m), color=c, smooth_shading=True, specular=0.25)))
    pl.camera_position = CAMERA
    pl.camera.view_angle = 30
    pl.enable_anti_aliasing("fxaa")
    caption = None
    frames, ms = [], []
    last = len(B.STEPS) - 1
    for s in range(len(B.STEPS)):
        n = 1 if s == 0 else (LAST if s == last else MOVE)
        for k in range(n):
            u = (k + 1) / n
            for it, a, e in zip(items, actors, edges):
                vis = s >= it.step
                off = np.zeros(3)
                if s == it.step:
                    off = np.asarray(it.entry, float) * (1 - ease(u / 0.8))
                a.visibility = vis
                a.position = off
                if e is not None:
                    e.visibility = vis
                    e.position = off
            q = B.D.REST
            if s == last:
                q = B.D.REST + (B.D.PICK - B.D.REST) * ease((u - 0.35) / 0.65)
            poses = piper.fk(q, grip=0.01)
            aoff = np.asarray((0, 0, 0.45)) * (1 - ease(u / 0.8)) if s == B.ARM_STEP else np.zeros(3)
            for link, a in arm:
                a.visibility = s >= B.ARM_STEP
                a.user_matrix = translate(aoff) @ B.arm_base() @ poses[link]
            ru = ease(u / 0.35) if s == last else 0.0
            topz = H.deck_top() + B.D.Z0 + B.D.SPAN["z"]
            flap.origin = (0, flap.center[1], topz)
            flap.scale = (1, 1, max(1 - ru, 1e-3))
            flap.visibility = bool(s >= B.CLOTH_STEP and ru < 0.97)
            roll.visibility = bool(s == last and ru > 0.3)
            if caption is not None:
                pl.remove_actor(caption)
            caption = pl.add_text(f"{s + 1}/{len(B.STEPS)}  {B.STEPS[s]}", position="upper_left", font_size=11,
                                  color=INK)
            pl.render()
            frames.append(Image.fromarray(pl.screenshot(return_img=True)))
            ms.append(HOLD_MS if k == n - 1 else MOVE_MS)
    ms[-1] = 3000
    pl.close()
    pal = frames[-1].quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=False, disposal=1)
    print(f"{path.name}: {len(frames)} frames, {path.stat().st_size / 1e6:.2f} MB, {time.time() - t0:.0f} s")


if __name__ == "__main__":
    what = sys.argv[1:] or ["side", "exploded", "still", "options", "sheets", "gif"]
    if "side" in what:
        side_view(B.HERE / "hutch-side.png")
    if "options" in what:
        options_chart(B.HERE / "hutch-options.png")
    if "sheets" in what:
        sheets(B.HERE / "sheet-layout.png")
    if "exploded" in what:
        exploded(B.HERE / "hutch-exploded.png")
    if "still" in what:
        still(B.HERE / "hutch-finished.png")
    if "gif" in what:
        gif(B.HERE / "hutch-assembly.gif")
