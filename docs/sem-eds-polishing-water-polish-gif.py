"""Render sem-eds-polishing-water-polish.gif: the 2 min water polish, step by step.

A schematic, not to scale. The step itself is from Maleki et al. 2023, Additive
Manufacturing Letters 5:100122 (doi:10.1016/j.addlet.2023.100122), on LPBF AlSi10Mg after
90 min of 0.05 um colloidal silica on a vibratory polisher: "the surface of vibro-polished
sample was cleaned by distilled water and soft pad with rotational speed of 40 rpm for
2 min". EBSD hit rate went from 51.26% to 81.12% (their area A2), and the silica left
behind was "mostly located inside the pores".

    python docs/sem-eds-polishing-water-polish-gif.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from PIL import Image

OUT = Path(__file__).with_name("sem-eds-polishing-water-polish.gif")
FPS = 10
W, H = 16, 9  # data units; 45 px per unit at 720 x 405

INK = "#1f2328"
MUTED = "#57606a"
METAL = "#b9c0c8"
METAL_DARK = "#7d8590"
HOLDER = "#8e969f"
BAKELITE = "#4a3426"
SILICA = "#e8a33d"
SILICA_EDGE = "#a86a0c"
WATER = "#4a9fe0"
PAD = "#f6f0dc"
CLOTH = "#9c8f7d"
MACHINE = "#d3d8de"
MILKY = "#e6ebef"
ETHANOL = "#8e7cc3"

# (step label, caption, inset caption, frames); the last scene is a held summary card
SCENES = [
    ("1", "VibroMet 2: 0.05 µm colloidal silica, ~5 h (as now)",
     "Silica spheres (~40 nm) coat the face,\nlike Gage's May 22 SEM image", 26),
    ("2", "Lift the puck out and keep the face wet: squirt DI water on it",
     "Still wet, so the spheres are still loose.\nIf they dry, they stick", 24),
    ("3", "Rotary polisher, clean soft pad, water only, 40 rpm, 2 min",
     "Water and the soft nap carry the\nloose spheres off the face", 52),
    ("4", "Rinse with DI water, then ethanol, then blow dry",
     "Far less silica on the flat face.\nSome can stay in pores", 30),
    ("✓", "Then the usual solvent clean, and on to the ion mill",
     "Far less silica on the flat face.\nSome can stay in pores", 1),
]
HOLD_MS = 5200

rng = np.random.default_rng(7)

# Inset geometry: the polished face is the line y = SURF, the pore is a notch at PORE_X
SURF, X0, X1 = 3.9, 10.45, 15.45
PORE_X, PORE_R = 14.15, 0.5
R = 0.12


def _flat_spheres():
    out = []
    for layer, y in ((0, SURF + R), (1, SURF + 3 * R * 0.9)):
        x = X0 + R + (R if layer else 0)
        while x < X1 - R:
            in_pore = abs(x - PORE_X) < PORE_R + R
            keep = rng.random() < (0.95 if layer == 0 else 0.45)
            if not in_pore and keep:
                stays = layer == 0 and len(out) % 6 == 3  # water polish reduces residue, not to zero
                out.append([x, y, np.inf if stays else rng.uniform(0.05, 0.85)])
            x += 2 * R
    return out


def _pore_spheres():
    out = []
    for row in range(4):
        y = SURF - PORE_R + R + row * 1.75 * R
        half = np.sqrt(max(PORE_R**2 - (y - SURF) ** 2, 0)) - R
        x = PORE_X - half
        while x <= PORE_X + half + 1e-6:
            out.append([x, y, np.inf if rng.random() < 0.85 else rng.uniform(0.3, 0.9)])
            x += 2 * R
    return out


FLAT, PORE = _flat_spheres(), _pore_spheres()


def text(ax, x, y, s, size=10, color=INK, family="DejaVu Sans", **kw):
    ax.text(x, y, s, fontsize=size, color=color, family=family, **kw)


def label(ax, s, xy, xytext, size=9):
    ax.annotate(s, xy=xy, xytext=xytext, fontsize=size, color=INK, family="DejaVu Sans",
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkA=2, shrinkB=2))


def squirt(ax, x0, y0, x1, y1, t, color=WATER):
    """Dashed arc from a wash-bottle nozzle to a target, dashes moving with t."""
    s = np.linspace(0, 1, 40)
    xs = x0 + (x1 - x0) * s
    ys = y0 + (y1 - y0) * s + 0.9 * np.sin(np.pi * s)
    phase = (t * 6) % 1
    for i in range(0, len(s) - 3, 4):
        j = int(i + 4 * phase) % (len(s) - 2)
        ax.plot(xs[j:j + 2], ys[j:j + 2], color=color, lw=2.4, solid_capstyle="round")


def bottle(ax, x, y, color, name):
    ax.add_patch(patches.FancyBboxPatch((x - 0.45, y - 0.8), 0.9, 1.3,
                                        boxstyle="round,pad=0.02,rounding_size=0.18",
                                        fc=color, ec=INK, lw=1, alpha=0.85))
    ax.plot([x, x + 0.35, x + 0.7], [y + 0.5, y + 0.85, y + 0.95], color=INK, lw=1.6)
    text(ax, x, y - 0.15, name, size=8, color="white", ha="center", va="center", weight="bold")


def puck_side(ax, cx, base, wet):
    """Side view of the Bakelite puck, polished face up, optional water film."""
    ax.add_patch(patches.Rectangle((cx - 1.5, base), 3.0, 1.1, fc=BAKELITE, ec=INK, lw=1))
    ax.add_patch(patches.Rectangle((cx - 0.6, base + 1.02), 1.2, 0.08, fc=METAL, ec="none"))
    if wet > 0:
        ax.add_patch(patches.Ellipse((cx, base + 1.14), 2.6 * min(1, 0.4 + wet), 0.22,
                                     fc=WATER, ec="none", alpha=0.45 * wet))


def scene_vibromet(ax, t, fade=1.0):
    a = fade
    ax.add_patch(patches.FancyBboxPatch((1.2, 1.35), 7.6, 1.0,
                                        boxstyle="round,pad=0.02,rounding_size=0.15",
                                        fc=MACHINE, ec=METAL_DARK, lw=1.2, alpha=a))
    text(ax, 5.0, 1.85, "VibroMet 2", size=10, color=MUTED, ha="center", va="center", alpha=a)
    ax.add_patch(patches.Polygon([(1.33, 3.35), (1.6, 2.35), (8.4, 2.35), (8.67, 3.35)],
                                 fc=MILKY, ec="none", alpha=a))
    ax.add_patch(patches.Rectangle((1.6, 2.35), 6.8, 0.12, fc=CLOTH, ec="none", alpha=a))
    ax.plot([0.9, 1.6, 8.4, 9.1], [4.9, 2.35, 2.35, 4.9], color=METAL_DARK, lw=2.2, alpha=a)
    jit = 0.05 if int(t * FPS) % 2 else -0.05
    hx = 4.1 + jit
    ax.add_patch(patches.Rectangle((hx, 2.47), 1.8, 1.7, fc=HOLDER, ec=INK, lw=1, alpha=a))
    ax.add_patch(patches.Rectangle((hx + 0.25, 2.47), 1.3, 0.55, fc=BAKELITE, ec="none", alpha=a))
    ax.add_patch(patches.Rectangle((hx + 0.55, 2.47), 0.7, 0.07, fc=METAL, ec="none", alpha=a))
    for side, sgn in ((hx - 0.25, -1), (hx + 2.05, 1)):
        for k in range(2):
            off = sgn * (0.18 * k + (0.08 if jit > 0 else 0))
            ax.add_patch(patches.Arc((side + off, 3.3), 0.3, 0.8, theta1=-60 if sgn > 0 else 120,
                                     theta2=60 if sgn > 0 else 240, color=MUTED, lw=1.2, alpha=a))
    if fade == 1.0:
        label(ax, "0.05 µm colloidal silica", (7.6, 2.9), (6.6, 5.4))
        label(ax, "puck in weighted holder,\nface down on the cloth", (4.3, 3.6), (1.3, 6.2))


def scene_lift(ax, t, p):
    scene_vibromet(ax, t, fade=max(0.18, 1 - 2.5 * p))
    rise = min(1, p / 0.3)
    base = 2.9 + 2.2 * rise
    puck_side(ax, 5.0, base, wet=max(0, (p - 0.3) / 0.5) if p > 0.3 else 0)
    if p > 0.3:
        bottle(ax, 1.6, 6.6, WATER, "DI")
        squirt(ax, 2.3, 7.5, 4.6, base + 1.2, t)
        label(ax, "don't let it dry", (5.8, base + 1.2), (6.9, base + 1.9))
    if p > 0.7:
        ax.annotate("", xy=(9.4, 4.4), xytext=(7.4, 4.4),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=14))
        text(ax, 8.4, 3.9, "to the\npolisher", size=8.5, color=MUTED, ha="center", va="top")


def scene_polisher(ax, t, p):
    cx, cy, rp = 5.3, 4.45, 2.6
    ax.add_patch(patches.Circle((cx, cy), rp + 0.35, fc=MACHINE, ec=METAL_DARK, lw=1.2))
    ax.add_patch(patches.Circle((cx, cy), rp, fc=PAD, ec=METAL_DARK, lw=1))
    ax.add_patch(patches.Circle((cx, cy), rp, fc=WATER, ec="none", alpha=0.10 + 0.08 * min(1, p * 4)))
    ang = -2 * np.pi * 0.55 * t
    for k in range(12):
        a = ang + k * np.pi / 6
        ax.plot([cx + (rp + 0.08) * np.cos(a), cx + (rp + 0.3) * np.cos(a)],
                [cy + (rp + 0.08) * np.sin(a), cy + (rp + 0.3) * np.sin(a)], color=METAL_DARK, lw=1.6)
    ax.add_patch(patches.FancyArrowPatch((cx + 1.9 * np.cos(2.6), cy + 1.9 * np.sin(2.6)),
                                         (cx + 1.9 * np.cos(1.7), cy + 1.9 * np.sin(1.7)),
                                         connectionstyle="arc3,rad=-0.35", arrowstyle="-|>",
                                         mutation_scale=12, color=MUTED, lw=1.2))
    # water nozzle and splash
    ax.plot([1.3, 4.1], [7.3, 5.75], color=METAL_DARK, lw=5, solid_capstyle="round")
    sx, sy = 4.15, 5.65
    ax.add_patch(patches.Circle((sx, sy), 0.12, fc=WATER, ec="none"))
    for k in range(3):
        r = 0.2 + ((t * 1.6 + k / 3) % 1) * 0.8
        ax.add_patch(patches.Circle((sx, sy), r, fc="none", ec=WATER, lw=1.2, alpha=1 - r / 1.0))
    # puck holder, face down
    hx, hy = cx + 1.1, cy - 0.35
    ax.add_patch(patches.Circle((hx, hy), 0.95, fc=HOLDER, ec=INK, lw=1))
    ax.add_patch(patches.Circle((hx, hy), 0.66, fc=BAKELITE, ec="none"))
    b = 2 * np.pi * 0.35 * t
    ax.plot([hx, hx + 0.6 * np.cos(b)], [hy, hy + 0.6 * np.sin(b)], color="white", lw=1.5)
    label(ax, "DI water on,\nno abrasive", (sx - 0.2, sy - 0.1), (0.3, 4.6))
    label(ax, "puck face down", (hx + 0.75, hy - 0.6), (7.6, 2.3))
    label(ax, "clean soft pad", (cx - 1.4, cy - 1.7), (0.3, 1.7))
    # timer
    secs = int(round(120 * p))
    ax.add_patch(patches.FancyBboxPatch((7.95, 6.55), 1.55, 0.95,
                                        boxstyle="round,pad=0.02,rounding_size=0.15",
                                        fc=INK, ec="none"))
    text(ax, 8.72, 7.02, f"{secs // 60}:{secs % 60:02d}", size=17, color="white",
         ha="center", va="center", family="DejaVu Sans Mono", weight="bold")
    text(ax, 8.72, 6.25, "of 2:00", size=8.5, color=MUTED, ha="center", va="center")
    text(ax, 8.72, 5.55, "40 rpm", size=10, color=INK, ha="center", va="center", weight="bold")


def scene_rinse(ax, t, p):
    base = 3.2
    dry = max(0, (p - 0.7) / 0.3)
    puck_side(ax, 5.0, base, wet=1 - dry)
    if p < 0.35:
        bottle(ax, 1.6, 6.6, WATER, "DI")
        squirt(ax, 2.3, 7.5, 4.6, base + 1.2, t)
        label(ax, "DI water rinse", (5.6, base + 1.25), (6.8, base + 2.0))
    elif p < 0.7:
        bottle(ax, 1.6, 6.6, ETHANOL, "EtOH")
        squirt(ax, 2.3, 7.5, 4.6, base + 1.2, t, color=ETHANOL)
        label(ax, "ethanol", (5.6, base + 1.25), (6.8, base + 2.0))
    else:
        ax.plot([1.2, 3.6], [6.9, 5.3], color=METAL_DARK, lw=5, solid_capstyle="round")
        for k in range(3):
            o = ((t * 3 + k / 3) % 1)
            x = 3.8 + 1.0 * o
            y = 5.15 - 0.65 * o
            ax.plot([x, x + 0.35], [y + 0.12 * (k - 1), y - 0.23 + 0.12 * (k - 1)],
                    color=MUTED, lw=1.4, alpha=1 - o)
        label(ax, "blow dry (air)", (5.6, base + 1.2), (6.8, base + 2.0))


def scene_summary(ax):
    ax.add_patch(patches.FancyBboxPatch((0.45, 1.35), 9.1, 6.35,
                                        boxstyle="round,pad=0.02,rounding_size=0.25",
                                        fc="#f6f8fa", ec="#d0d7de", lw=1.2))
    text(ax, 0.9, 7.1, "Why bother", size=13, weight="bold", va="center")
    lines = [
        "Silica left on the face reads as extra Si and O in",
        "EDS, and shows up as unindexed points in EBSD.",
        "",
        "Maleki et al. 2023, LPBF AlSi10Mg after 0.05 µm",
        "silica on a vibratory polisher: this 2 min step",
        "raised the EBSD hit rate from 51% to 81%.",
        "",
        "It is cheap and cuts residue, but it doesn't clear",
        "silica stuck in pores. Keep EDS spots off pores.",
    ]
    for i, s in enumerate(lines):
        text(ax, 0.9, 6.35 - 0.52 * i, s, size=10.5, va="center",
             weight="bold" if "51%" in s else "normal")


def inset(ax, scene, p, t):
    text(ax, 12.95, 7.45, "Polished face, magnified", size=9.5, color=MUTED, ha="center", va="center")
    text(ax, 12.95, 7.05, "(schematic, not to scale)", size=8, color=MUTED, ha="center", va="center")
    ax.add_patch(patches.Rectangle((X0, 2.2), X1 - X0, SURF - 2.2, fc=METAL, ec=METAL_DARK, lw=1))
    ax.add_patch(patches.Wedge((PORE_X, SURF), PORE_R, 180, 360, fc="#6e7781", ec=METAL_DARK, lw=1))
    ax.add_patch(patches.Rectangle((PORE_X - PORE_R + 0.02, SURF - 0.01), 2 * PORE_R - 0.04, 0.03,
                                   fc="#6e7781", ec="none"))
    text(ax, 10.65, 2.5, "AlSi10Mg", size=8.5, color=INK, va="center")
    text(ax, PORE_X, 2.5, "pore", size=8.5, color=INK, ha="center", va="center")
    wet = {0: 0.0, 1: 1.0, 2: 1.0, 3: max(0.0, 1 - max(0, (p - 0.7) / 0.3)), 4: 0.0}[scene]
    if scene == 0:
        wet = 0.6  # still in the suspension
    if wet > 0:
        ax.add_patch(patches.Rectangle((X0, SURF), X1 - X0, 0.95,
                                       fc=MILKY if scene == 0 else WATER, ec="none",
                                       alpha=(0.9 if scene == 0 else 0.22) * wet))
    prog = {0: 0.0, 1: 0.0, 2: p, 3: 1.2, 4: 1.2}[scene]
    for x, y, thr in FLAT + PORE:
        if prog < thr:
            dx, alpha = 0.0, 1.0
        else:
            f = (prog - thr) / 0.15
            if f >= 1:
                continue
            dx, alpha = 1.4 * f, 1 - f
        if x + dx > X1 - R:
            continue
        ax.add_patch(patches.Circle((x + dx, y + 0.5 * dx * (y > SURF)), R, fc=SILICA,
                                    ec=SILICA_EDGE, lw=0.6, alpha=alpha))
    if scene == 2:
        for k in range(3):
            o = (t * 1.3 + k / 3) % 1
            ax.annotate("", xy=(10.9 + 4.0 * o + 0.5, 4.95), xytext=(10.9 + 4.0 * o, 4.95),
                        arrowprops=dict(arrowstyle="-|>", color=WATER, lw=1.3, alpha=1 - o,
                                        mutation_scale=9))


def frame(scene_idx, p, t):
    fig = plt.figure(figsize=(7.2, 4.05), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    step, caption, inset_caption, _ = SCENES[scene_idx]
    text(ax, 0.35, 8.45, "The 2-minute water polish", size=15, weight="bold", va="center")
    text(ax, 0.35, 7.95, "between the VibroMet and the solvent clean", size=9.5, color=MUTED,
         va="center")
    for k in range(4):
        done = k < scene_idx or scene_idx == 4
        cur = k == scene_idx
        ax.add_patch(patches.Circle((13.35 + 0.62 * k, 8.45), 0.2,
                                    fc=INK if (done or cur) else "white", ec=INK, lw=1))
        text(ax, 13.35 + 0.62 * k, 8.45, str(k + 1), size=8,
             color="white" if (done or cur) else INK, ha="center", va="center", weight="bold")
    if scene_idx == 0:
        scene_vibromet(ax, t)
    elif scene_idx == 1:
        scene_lift(ax, t, p)
    elif scene_idx == 2:
        scene_polisher(ax, t, p)
    elif scene_idx == 3:
        scene_rinse(ax, t, p)
    else:
        scene_summary(ax)
    inset(ax, scene_idx, p, t)
    text(ax, 12.95, 1.55, inset_caption, size=8.5, color=INK, ha="center", va="center",
         linespacing=1.3)
    ax.plot([0.35, 15.65], [0.95, 0.95], color="#d0d7de", lw=1)
    text(ax, 0.35, 0.5, f"{step}  {caption}", size=11.5, weight="bold", va="center")
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
    plt.close(fig)
    return img


def main():
    frames, durations = [], []
    t = 0.0
    for i, (*_, n) in enumerate(SCENES):
        for k in range(n):
            frames.append(frame(i, k / max(1, n - 1), t))
            durations.append(HOLD_MS if i == len(SCENES) - 1 else 1000 // FPS)
            t += 1 / FPS
        durations[-1] += 500 if i < len(SCENES) - 1 else 0  # brief pause between steps
    # one palette per frame: a shared one drops small accents like the ethanol bottle
    frames = [f.quantize(colors=128, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
              for f in frames]
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   optimize=True, disposal=1)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB, {len(frames)} frames, "
          f"{sum(durations) / 1000:.1f} s)")


if __name__ == "__main__":
    main()
