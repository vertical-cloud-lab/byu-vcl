"""Shared look for every figure and animation in this study (dark video surface).

Palette: the dataviz skill's validated reference palette, dark steps, categorical slots in fixed
order (validated: `validate_palette.js "#3987e5,#d95926,#199e70,#c98500" --mode dark` -> all pass).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

SURFACE = "#1a1a19"; TEXT = "#f0efec"; TEXT2 = "#c3c2b7"; MUTED = "#8a897f"; GRID = "#383835"
CAT = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9", "#e66767"]
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = CAT
W, H, DPI, FPS = 19.2, 10.8, 100, 24
LW = 3.0      # ~3 px at 1080p; a touch heavier than 2 px for video legibility

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": TEXT, "axes.labelcolor": TEXT2, "xtick.color": TEXT2, "ytick.color": TEXT2,
    "axes.edgecolor": GRID, "grid.color": GRID, "grid.linewidth": 0.8, "axes.grid": True,
    "font.family": "DejaVu Sans", "font.size": 20, "axes.titlesize": 30, "axes.labelsize": 20,
    "xtick.labelsize": 18, "ytick.labelsize": 18, "legend.fontsize": 18, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": LW, "lines.solid_capstyle": "round",
})

def fig_ax(title=None, subtitle=None, rect=(0.08, 0.13, 0.86, 0.68)):
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    ax = fig.add_axes(rect)
    if title:
        fig.text(0.08, 0.92, title, fontsize=36, fontweight="bold", color=TEXT, va="center")
    if subtitle:
        fig.text(0.08, 0.865, subtitle, fontsize=21, color=TEXT2, va="center")
    return fig, ax

def source_note(fig, text):
    fig.text(0.08, 0.035, text, fontsize=14, color=MUTED, va="center")

def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * t)

def render(fig, update, duration, out_mp4, out_png=None, build=0.7):
    """update(p) draws the frame for build progress p in [0, 1]; the last (1-build) of the clip holds."""
    n = int(round(duration * FPS))
    def f(i):
        p = min(1.0, (i / max(1, n - 1)) / build)
        update(p)
        return []
    anim = animation.FuncAnimation(fig, f, frames=n, blit=False)
    anim.save(out_mp4, writer=animation.FFMpegWriter(fps=FPS, codec="libx264",
              extra_args=["-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20"]), dpi=DPI)
    if out_png:
        update(1.0); fig.savefig(out_png, dpi=DPI)
    plt.close(fig)
