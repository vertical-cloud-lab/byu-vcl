"""Pictures for ccx_split.py: the clamp's split close up, and what overtightening the screws does to it.

Every picture is the section through the first row of clamp screws (y = 22.1), cut from the C3D10
mesh: each element that crosses the plane is split into its eight linear tets and sliced in pyvista,
then drawn in matplotlib. Deformation is drawn at true scale.
"""
from __future__ import annotations

import io
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402
from matplotlib.tri import Triangulation  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {1.0: "#2a78d6", 0.6: "#eb6834"}            # categorical slots 1 and 2: before, now
CRITICAL = "#d03b3b"
BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("stress", BLUES)
CMAP.set_over(CRITICAL)
PLA = 35.0                       # MPa: Bambu PLA Basic, along the layers
Y_CUT = 22.1                     # the first row of clamp screws (y = 22), just off it: mesh nodes lie on y = 22
SUB = np.array([[0, 4, 6, 7], [4, 1, 5, 8], [6, 5, 2, 9], [7, 8, 9, 3],      # C3D10 -> 8 tets
                [6, 8, 4, 5], [6, 8, 5, 9], [6, 8, 9, 7], [6, 8, 7, 4]])
LABEL = {1.0: "1.0 mm split (before)", 0.6: "0.6 mm split (now)"}
plt.rcParams.update({"font.size": 11, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED,
                     "ytick.color": MUTED, "text.color": INK, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})


class Section:
    """The plane y = Y_CUT through both halves, with every solved force's displacement and stress."""

    def __init__(self, v: dict):
        import pyvista as pv
        self.v = v
        self.p = v["params"]
        xr, el = v["x_real"], v["el"]
        ys = xr[el[:, :4], 1]
        tets = el[(ys.min(axis=1) <= Y_CUT) & (ys.max(axis=1) >= Y_CUT)][:, SUB].reshape(-1, 4)
        grid = pv.UnstructuredGrid({pv.CellType.TETRA: tets}, xr)
        self.forces = [0.0] + sorted(v["U"])
        for F in self.forces:
            d = np.zeros_like(xr) if F == 0 else v["x"] + v["U"][F] - xr       # where it really goes
            grid.point_data[f"d{F:g}"] = d
            grid.point_data[f"s{F:g}"] = np.zeros(len(xr)) if F == 0 else v["p1"][F]
        grid.point_data["part"] = v["part"].astype(float)
        s = grid.slice(normal="y", origin=(0, Y_CUT, 0)).triangulate().clean()
        self.s = s
        self.tri = s.faces.reshape(-1, 4)[:, 1:]
        a = np.sort(self.tri[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
        edges, count = np.unique(a, axis=0, return_counts=True)
        self.lines = edges[count == 1]                  # the section's outline
        # the screw seats under this row's top screw: carrier head seat, bracket nut seat
        p = self.p
        zc = p.ax_z + p.clamp_r
        seats = v["seats"]
        near = np.hypot(xr[seats, 1] - Y_CUT, xr[seats, 2] - zc) < 4.0
        self.head = seats[near & (v["part"][seats] == 1)]
        self.nut = seats[near & (v["part"][seats] == 0)]

    def at(self, F: float, arr: str, mesh) -> np.ndarray:
        """Point data at force F, linear between the solved forces."""
        fs = self.forces
        F = min(max(F, fs[0]), fs[-1])
        k = int(np.searchsorted(fs, F, side="right")) - 1
        k = min(k, len(fs) - 2)
        t = (F - fs[k]) / (fs[k + 1] - fs[k])
        return (1 - t) * mesh.point_data[f"{arr}{fs[k]:g}"] + t * mesh.point_data[f"{arr}{fs[k + 1]:g}"]

    def seat_dx(self, F: float, nodes: np.ndarray) -> float:
        fs = self.forces
        vals = [0.0] + [float((self.v["x"][nodes, 0] + self.v["U"][f][nodes, 0] - self.v["x_real"][nodes, 0]).mean())
                        for f in fs[1:]]
        return float(np.interp(F, fs, vals))

    def draw(self, ax, F: float, vmax: float = PLA, window=None, screw: bool = True, body: bool = True):
        p = self.p
        d = self.at(F, "d", self.s)
        xz = self.s.points[:, [0, 2]] + d[:, [0, 2]]
        st = self.at(F, "s", self.s)
        if body:
            ax.add_patch(Circle((0, 0), p.body_r, facecolor=GRID, edgecolor=AXIS, lw=0.8, zorder=0))
        tri = Triangulation(xz[:, 0] - p.ax_x, xz[:, 1] - p.ax_z, self.tri)
        if F == 0:
            ax.tripcolor(tri, np.zeros(len(self.tri)), cmap=CMAP, vmin=0, vmax=vmax, zorder=1)
        else:
            face = st[self.tri].mean(axis=1)
            pc = ax.tripcolor(tri, facecolors=np.clip(face, 0, None), cmap=CMAP, vmin=0, vmax=vmax, zorder=1)
            pc.set_clim(0, vmax)
        ax.add_collection(LineCollection((xz - [p.ax_x, p.ax_z])[self.lines], colors=INK2, linewidths=0.7,
                                         zorder=2))
        if screw:
            self.draw_screw(ax, F)
        ax.set_aspect("equal")
        if window:
            ax.set_xlim(*window[0])
            ax.set_ylim(*window[1])
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    def draw_screw(self, ax, F: float):
        """M3 x 16: head in the carrier's counterbore, nut in the bracket's pocket, each moving with its seat."""
        p = self.p
        zc = p.clamp_r
        xh = p.clamp_head_seat + self.seat_dx(F, self.head)
        xn = -p.ear_w + p.m3_nut_depth + self.seat_dx(F, self.nut)
        kw = dict(facecolor="#b9b8b2", edgecolor=INK2, lw=0.7, alpha=0.95, zorder=3)
        ax.add_patch(Rectangle((xh - p.clamp_screw_len, zc - 1.5), p.clamp_screw_len, 3.0, **kw))
        ax.add_patch(Rectangle((xh, zc - 2.75), 3.0, 5.5, **kw))
        ax.add_patch(Rectangle((xn - 2.4, zc - 2.75), 2.4, 5.5, **kw))


def chart(ax, out: dict, key, ylabel: str, ref=None, marker_F=None):
    for g in (1.0, 0.6):
        rows = out["designs"][f"{g:.1f} mm"]["forces"]
        F = np.array([0.0] + [float(k) for k in rows])
        y = np.array([key(None, g)] + [key(r, g) for r in rows.values()])
        ax.plot(F, y, color=SERIES[g], lw=2, label=LABEL[g], zorder=3)
        ax.plot(F[1:], y[1:], "o", ms=4, color=SERIES[g], mec=SURFACE, mew=1, zorder=4)
        if marker_F is not None:
            ax.plot([marker_F], [np.interp(marker_F, F, y)], "o", ms=9, color=SERIES[g], mec=SURFACE, mew=2,
                    zorder=5)
    if ref:
        for val, text, va in ref:
            ax.axhline(val, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
            ax.text(985, val + (0.6 if va == "bottom" else -0.6), text, color=INK2, fontsize=9, va=va, ha="right")
    if marker_F is not None:
        ax.axvline(marker_F, color=AXIS, lw=1, zorder=0)
    ax.set_xlim(0, 1000)
    ax.set_xlabel("force in each M3 (N)")
    ax.set_ylabel(ylabel)
    ax.grid(True, color=GRID, lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def gap_of(r, g):
    return g if r is None else max(0.0, r["split gap (mm)"]["narrowest"])


def peak_of(r, g):
    return 0.0 if r is None else r["peaks away from the screw seats"]["max principal (MPa)"]["bracket"]["value"]


def grip_of(r, g):
    return 0.0 if r is None else r["body: radial contact force, summed (N)"]["bracket"]


def touch_force(out: dict, g: float) -> float | None:
    """Screw force at which the halves first meet: the narrowest gap carried on to zero along its
    slope between the last two forces at which the split was still open."""
    rows = out["designs"][f"{g:.1f} mm"]["forces"]
    F = [0.0] + [float(k) for k in rows]
    gaps = [g] + [r["split gap (mm)"]["narrowest"] for r in rows.values()]
    for k in range(3, len(F)):          # F[0] = 0 is before the clearance is taken up, so off the line
        if gaps[k] <= 1e-3 < gaps[k - 1]:
            slope = (gaps[k - 2] - gaps[k - 1]) / (F[k - 1] - F[k - 2])
            return min(F[k], F[k - 1] + gaps[k - 1] / slope)
    return None


CLOSE = ((-11.5, 12.5), (24.5, 46.0))       # mm from the axis: the top ears


def plot_closeup(secs: dict, out: dict, path: Path):
    p = secs[0.6].p
    fig = plt.figure(figsize=(15, 6.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1, 1], wspace=0.08)
    ax = fig.add_subplot(gs[0])
    secs[0.6].draw(ax, 0.0, screw=False, window=((-48, 48), (-50, 50)))
    ax.add_patch(Rectangle((CLOSE[0][0], CLOSE[1][0]), CLOSE[0][1] - CLOSE[0][0], CLOSE[1][1] - CLOSE[1][0],
                           fill=False, ec=INK, lw=1.2, ls=(0, (3, 2)), zorder=4))
    ax.text(-30, 0, "bracket", ha="center", va="center", color=INK2)
    ax.text(30, 0, "carrier", ha="center", va="center", color=INK2)
    ax.text(0, 0, "gripper body\nO57", ha="center", va="center", color=MUTED, fontsize=10)
    ax.set_title("The collar, cut through the first pair of\nclamp screws (y = 22 mm), seen from the arm",
                 color=INK, fontsize=12, loc="left")
    for k, g in enumerate((1.0, 0.6)):
        ax = fig.add_subplot(gs[k + 1])
        s = secs[g]
        s.draw(ax, 0.0, window=CLOSE)
        h = g / 2
        y = 44.9
        ax.annotate("", xy=(-h, y), xytext=(-h - 2.2, y), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
        ax.annotate("", xy=(h, y), xytext=(h + 2.2, y), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
        ax.text(h + 2.4, y, f"{g:.1f} mm", va="center", ha="left", color=INK, fontsize=12, fontweight="bold")
        ax.text(-6.5, 27.2, "bracket", ha="center", color=INK2, fontsize=10)
        ax.text(6.5, 27.2, "carrier", ha="center", color=INK2, fontsize=10)
        ax.text(-7.2, p.clamp_r + 3.6, "nut", ha="center", color=INK2, fontsize=9)
        ax.text(p.clamp_head_seat + 1.5, p.clamp_r + 3.6, "head", ha="center", color=INK2, fontsize=9)
        Ft = touch_force(out, g)
        msg = (f"the halves meet at about {round(Ft, -1):.0f} N per screw" if Ft else
               "the halves never meet up to 1000 N")
        ax.set_title(f"{LABEL[g]}\n{msg}", color=INK, fontsize=12, loc="left")
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def plot_overtighten(secs: dict, out: dict, path: Path, forces=(200, 500, 800)):
    fig = plt.figure(figsize=(15, 14.5))
    outer = fig.add_gridspec(4, 1, height_ratios=[1, 1, 0.05, 0.72], hspace=0.28)
    for i, g in enumerate((1.0, 0.6)):
        rows = out["designs"][f"{g:.1f} mm"]["forces"]
        inner = outer[i].subgridspec(1, 3, wspace=0.06)
        for j, F in enumerate(forces):
            ax = fig.add_subplot(inner[j])
            secs[g].draw(ax, F, window=CLOSE)
            r = rows[f"{F:.0f}"]
            gap = max(0.0, r["split gap (mm)"]["narrowest"])
            pk = peak_of(r, g)
            state = (f"split open {gap:.2f} mm" if gap > 1e-3 else
                     f"split closed, faces push {r['split contact force (N)']['total']:.0f} N")
            ax.set_title(f"{LABEL[g]}, {F} N per screw\n{state}\nbracket's peak (anywhere) {pk:.0f} MPa",
                         fontsize=11, color=INK, loc="left")
    cax = fig.add_subplot(outer[2].subgridspec(1, 3, width_ratios=[0.2, 0.6, 0.2])[1])
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, PLA))
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal", extend="max")
    cb.set_label("largest principal stress in the cut (MPa); red is over 35 MPa, PLA's strength along the layers",
                 color=INK2)
    cb.outline.set_edgecolor(AXIS)
    specs = [(gap_of, "narrowest gap across the split (mm)", None),
             (peak_of, "peak tension in the bracket (MPa)", [(PLA, "PLA, along the layers", "bottom"),
                                                              (31, "PLA, across them", "top")]),
             (grip_of, "bracket's grip on the body (N)", None)]
    inner = outer[3].subgridspec(1, 3, wspace=0.3)
    for j, (key, label, ref) in enumerate(specs):
        ax = fig.add_subplot(inner[j])
        chart(ax, out, key, label, ref)
        if j == 0:
            ax.legend(frameon=False, fontsize=10, loc="upper right")
    fig.text(0.125, 0.065, "Deformation at true scale. 200 N per screw is about 0.1 N m on a dry M3, 500 N about "
                           "0.3 N m, 1000 N about 0.6 N m. Grip is the body's push on the bracket, summed over the "
                           "bore.", color=INK2, fontsize=10)
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def gif(secs: dict, out: dict, path: Path, fps: int = 8):
    from PIL import Image
    top = max(max(secs[g].forces) for g in secs)
    Fs = list(np.linspace(0, top, 61)) + [top] * 16
    frames = []
    for F in Fs:
        fig = plt.figure(figsize=(11, 9), dpi=88)
        outer = fig.add_gridspec(3, 1, height_ratios=[1.25, 0.04, 0.7], hspace=0.3)
        inner = outer[0].subgridspec(1, 2, wspace=0.06)
        for j, g in enumerate((1.0, 0.6)):
            ax = fig.add_subplot(inner[j])
            secs[g].draw(ax, F, window=CLOSE)
            rows = out["designs"][f"{g:.1f} mm"]["forces"]
            fs = [0.0] + [float(k) for k in rows]
            gp = np.interp(F, fs, [g] + [max(0.0, r["split gap (mm)"]["narrowest"]) for r in rows.values()])
            pk = np.interp(F, fs, [0.0] + [peak_of(r, g) for r in rows.values()])
            state = f"split open {gp:.2f} mm" if gp > 0.005 else "split closed"
            ax.set_title(f"{LABEL[g]}\n{state}, bracket's peak {pk:.0f} MPa", fontsize=12, color=INK, loc="left")
        cax = fig.add_subplot(outer[1].subgridspec(1, 3, width_ratios=[0.2, 0.6, 0.2])[1])
        cb = fig.colorbar(plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, PLA)), cax=cax,
                          orientation="horizontal", extend="max")
        cb.set_label("largest principal stress in the cut (MPa); red: over PLA's 35", color=INK2, fontsize=10)
        cb.outline.set_edgecolor(AXIS)
        ax = fig.add_subplot(outer[2])
        chart(ax, out, peak_of, "bracket's peak tension (MPa)", [(PLA, "PLA, along the layers", "bottom")],
              marker_F=F)
        ax.legend(frameon=False, fontsize=10, loc="lower right")
        fig.suptitle(f"Tightening the clamp screws: {F:4.0f} N in each M3 (true-scale deformation, cut through "
                     "the screw)", x=0.1, ha="left", fontsize=13, color=INK)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=SURFACE)
        plt.close(fig)
        frames.append(Image.open(buf).convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)
    if shutil.which("gifsicle"):
        subprocess.run(["gifsicle", "-O3", "--lossy=30", "-b", str(path)], check=True)
    print(f"{path.name}: {len(frames)} frames, {path.stat().st_size / 1e6:.1f} MB")


def plot_all(out: dict, viz: dict, renders: Path):
    secs = {g: Section(v) for g, v in viz.items()}
    plot_closeup(secs, out, renders / "split_closeup.png")
    plot_overtighten(secs, out, renders / "split_overtighten.png")
    gif(secs, out, renders / "split_overtighten.gif")
