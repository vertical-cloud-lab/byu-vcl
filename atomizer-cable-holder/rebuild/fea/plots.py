"""Figures for clip_fea.py: peak strain against the diameter pushed in, and the strain field at D = bore."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.tri as mtri  # noqa: E402
import numpy as np  # noqa: E402

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {"printed": "#2a78d6", "rebuild": "#eb6834"}  # categorical slots 1 and 2
LABEL = {"printed": "printed (17:03 UTC revision)", "rebuild": "first version (this PR's rebuild)"}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})


def strain_curves(results: dict, path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    for ax, clip in zip(axes, ("large", "small")):
        for r in (r for r in results["clips"] if r["clip"] == clip):
            v = r["version"]
            d = [r["opening_mm"]] + [c["D_mm"] for c in r["curve"]]
            e = [0.0] + [100 * c["max_tensile_strain"] for c in r["curve"]]
            ax.plot(d, e, color=SERIES[v], lw=2, label=f"{LABEL[v]}: Ø{r['bore_mm']:g} bore, {r['opening_mm']:.2f} mm opening")
            ax.plot(d[-1], e[-1], "o", ms=8, color=SERIES[v], mec=SURFACE, mew=2)
            ax.annotate(f"{e[-1]:.1f}% at D = bore", (d[-1], e[-1]), xytext=(-8, 8), textcoords="offset points",
                        ha="right", color=INK2, fontsize=9)
        for name, m in results["materials"].items():
            if name.startswith("TPU"):
                continue
            ax.axhline(100 * m["allowable_repeated"], color=INK2, lw=1, ls=(0, (4, 3)))
            if clip == "large":  # labelled once; the lines are at the same heights in both panels
                ax.text(0.01, 100 * m["allowable_repeated"], f" {name.split(' (')[0]}, repeated use",
                        transform=ax.get_yaxis_transform(), va="bottom", color=INK2, fontsize=8.5)
        if clip == "small":
            ax.axvline(6.0, color=GRID, lw=1.5)
            ax.text(5.92, 0.25, "6 mm air hose\n(6/4 mm tubing)", ha="right", color=INK2, fontsize=8.5)
        ax.set_title(f"{clip.capitalize()} clip", loc="left", color=INK, fontsize=11)
        ax.set_xlabel("diameter pushed through the opening, D (mm)")
        ax.grid(True, color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(loc="upper left", bbox_to_anchor=(0, -0.16), frameon=False, fontsize=8.5)
    axes[0].set_ylabel("peak tensile strain in the arm (%)")
    axes[0].set_ylim(0, None)
    fig.suptitle("Snap clips, CalculiX (C3D20R, nonlinear geometry): peak strain while a cable of diameter D goes in",
                 x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.87, "The strain does not depend on the material once the lip's travel is set. Each curve ends where D equals "
             "the bore.\nDashed: rule-of-thumb allowables for repeated snapping, FDM parts bent along their lines.",
             color=INK2, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def contours(results: dict, fields: dict, path) -> None:
    cases = [("printed", "large"), ("printed", "small"), ("rebuild", "large"), ("rebuild", "small")]
    vmax = max(100 * r["curve"][-1]["max_tensile_strain"] for r in results["clips"])
    fig, axes = plt.subplots(1, 4, figsize=(15, 5.2))
    for ax, key in zip(axes, cases):
        f = fields[key]
        r = next(r for r in results["clips"] if (r["version"], r["clip"]) == key)
        ids = {n: i for i, n in enumerate(f["ids"])}
        xyz, u = np.array(f["xyz"]), np.array(f["U"])
        mid = np.abs(xyz[:, 1]) < 1e-4  # the extrude's mid-plane, a symmetry plane
        tris = []
        for el in f["elements"]:
            corners = el[:8] if len(el) == 20 else el[:6]
            half = len(corners) // 2
            for face in (corners[:half], corners[half:]):
                if all(mid[ids[n]] for n in face):
                    k = [ids[n] for n in face]
                    tris += [k[:3]] if len(k) == 3 else [[k[0], k[1], k[2]], [k[0], k[2], k[3]]]
        tri = mtri.Triangulation(xyz[:, 0], xyz[:, 2], tris)
        ax.triplot(tri, color=GRID, lw=0.3)  # undeformed
        tri_d = mtri.Triangulation(xyz[:, 0] + u[:, 0], xyz[:, 2] + u[:, 2], tris)
        cs = ax.tripcolor(tri_d, 100 * np.clip(np.array(f["E1"]), 0, None), shading="gouraud", cmap="Blues",
                          vmin=0, vmax=vmax)
        end = r["curve"][-1]
        ax.plot(*end["at"], "o", ms=8, mfc="none", mec=INK, mew=1.5)
        ax.set_title(f"{key[0]}, {key[1]} clip: Ø{r['bore_mm']:g} bore\npeak {100 * end['max_tensile_strain']:.1f}% "
                     f"(circled), lip moved {r['lip_spread_at_bore_mm']:.2f} mm", loc="left", fontsize=9.5, color=INK)
        ax.set_aspect("equal")
        ax.set_xlim(f["lip"][0] - 7 if f["side"] < 0 else f["lip"][0] - 3.5, f["lip"][0] + 3.5 if f["side"] < 0 else f["lip"][0] + 7)
        ax.set_ylim(min(xyz[:, 2]) - 1.5, 1)
        ax.axis("off")
    cb = fig.colorbar(cs, ax=axes, orientation="horizontal", fraction=0.05, pad=0.04, aspect=60)
    cb.set_label("max principal (tensile) strain, % (mid-depth section, deformed; grey mesh = at rest)", color=INK2)
    fig.suptitle("One arm of each clip with a cable as wide as the bore pushed through: the strain peaks on the inside "
                 "of the arm where it meets the strip", x=0.01, y=1.04, ha="left", fontsize=12)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
