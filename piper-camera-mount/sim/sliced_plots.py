#!/usr/bin/env python3
"""Pictures for sliced_fea.py, from sim/sliced_fea.json and the cache in sim/build_sliced/.

  renders/sliced_model.png    one layer of the bracket: the G-code raster, and the voxels made from it
  renders/sliced_clamp.png    the clamp: split gap and peak failure index against screw force
  renders/sliced_section.png  the section through the first clamp screws at 500 N: what is printed
                              there, and how close each voxel is to failing
  renders/sliced_loads.png    force to the first failure for the cable yank, the pod bump and the clamp

    python piper-camera-mount/sim/sliced_plots.py
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, ListedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
MOUNT = HERE.parent
RENDERS = MOUNT / "renders"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(MOUNT / "cad"))
from split_plots import AXIS, BLUES, CRITICAL, GRID, INK, INK2, MUTED, SURFACE  # noqa: E402,F401

import sliced_fea as S  # noqa: E402

ORDER = ["h2d_pahtcf_06", "h2d_pahtcf_04", "a1m_pla_04"]
COLOR = {"h2d_pahtcf_06": "#2a78d6", "h2d_pahtcf_04": "#eb6834", "a1m_pla_04": "#1baf7a"}   # slots 1-3
SHORT = {"h2d_pahtcf_06": "PAHT-CF, H2D 0.6 mm nozzle", "h2d_pahtcf_04": "PAHT-CF, H2D 0.4 mm nozzle",
         "a1m_pla_04": "PLA, A1 mini 0.4 mm nozzle"}
SOLID = "#898781"
CMAP = LinearSegmentedColormap.from_list("fi", BLUES)
CMAP.set_over(CRITICAL)
FEATURE_COLORS = ["#3987e5", "#86b6ef", "#e1e0d9"]       # wall, solid infill or skin, sparse infill
Y_CUT = 22.0


def results() -> dict:
    return json.loads((HERE / "sliced_fea.json").read_text())


def get(res: dict, cfg: str, case: str, solid: bool = False, h: float = S.H_VOX):
    return res.get(f"{cfg} / {'solid' if solid else 'as printed'} / {h:.2f} mm / {case}")


def voxels(cfg: str, part: str, h: float = S.H_VOX, solid: bool = False) -> dict:
    """Part's voxels as sliced_fea.Part keeps them (same order), without building the stiffness."""
    g = S.voxel_grid(cfg, part, h)
    tr = S.transforms(S.load_params((S.EX / "params.json").read_text()))
    R, t = tr[part]
    frac = (g["cin"] if solid else g["cnt"]) / g["npix"]
    keep = frac >= (0.5 if solid else S.F_MIN)
    sel = np.flatnonzero(keep)[S.largest_component(g["ijk"][keep])]
    cw = (g["origin"] + (g["ijk"][sel] + 0.5) * g["h"] - t) @ R
    return {"cw": cw, "frac": frac[sel], "feat": g["feat"][sel], "h": g["h"], "R": R}


# --- the model ------------------------------------------------------------------------------------

def plot_model(path: Path, cfg: str = "h2d_pahtcf_04", z_mm: float = 10.1):
    """A layer of the bracket at z (print frame): the raster's beads coloured by feature with their
    direction, and the voxel layer made from them, shaded by bead fraction."""
    from gcode_voxels import parse, rasterize
    bx, by = S.CONFIGS[cfg]["bed"]
    tp = parse((S.SLICE / f"build_{cfg}" / "plate_2_bracket.gcode").read_text(), offset_xy=(bx / 2, by / 2))
    r = rasterize(tp, S.EX / "bracket.stl", S.DP)
    k = int(np.searchsorted(r.z_top, z_mm))
    cls, ang = r.cls[k], r.ang[k]
    grp = np.where(cls == 0, 3, S.GROUP[cls])
    ny, nx = cls.shape
    ext = [r.origin[0], r.origin[0] + nx * S.DP, r.origin[1], r.origin[1] + ny * S.DP]
    g = S.voxel_grid(cfg, "bracket", S.H_VOX)
    K = int((r.z_top[k] - r.h[k] / 2) // g["h"][2])
    on = g["ijk"][:, 2] == K
    frac = g["cnt"][on] / g["npix"]
    ij = g["ijk"][on, :2]
    img = np.full(ij.max(axis=0)[::-1] + 1, np.nan)
    img[ij[:, 1], ij[:, 0]] = np.where(frac >= S.F_MIN, frac, np.nan)
    hv = g["h"][0]
    ext2 = [g["origin"][0], g["origin"][0] + img.shape[1] * hv, g["origin"][1], g["origin"][1] + img.shape[0] * hv]
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.6))
    cmap = ListedColormap(FEATURE_COLORS + [SURFACE])
    axs[0].imshow(grp, origin="lower", extent=ext, cmap=cmap, norm=BoundaryNorm(np.arange(-0.5, 4.5), 4),
                  interpolation="nearest")
    # bead directions: one short tick per 1 mm cell that holds bead
    step = int(round(1.0 / S.DP))
    for j in range(step // 2, ny, step):
        for i in range(step // 2, nx, step):
            if cls[j, i]:
                a = np.radians(ang[j, i])
                x, y = ext[0] + (i + 0.5) * S.DP, ext[2] + (j + 0.5) * S.DP
                axs[0].plot([x - 0.4 * np.cos(a), x + 0.4 * np.cos(a)], [y - 0.4 * np.sin(a), y + 0.4 * np.sin(a)],
                            color=INK, lw=0.5)
    axs[0].set_title(f"G-code, layer {k + 1} (z = {r.z_top[k]:.1f} mm): beads by feature, ticks along them",
                     fontsize=11, loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in FEATURE_COLORS]
    axs[0].legend(handles, S.GROUPS, loc="upper left", frameon=False, fontsize=9)
    im = axs[1].imshow(img, origin="lower", extent=ext2, cmap=LinearSegmentedColormap.from_list("f", BLUES),
                       vmin=0, vmax=1, interpolation="nearest")
    axs[1].set_title(f"The FE model: {hv:.1f} mm voxels, shaded by the bead fraction they hold", fontsize=11,
                     loc="left")
    cb = fig.colorbar(im, ax=axs[1], fraction=0.04, pad=0.02)
    cb.set_label("bead fraction (empty: under 15 %)")
    for ax in axs:
        ax.set_aspect("equal")
        ax.set_xlabel("x in the print frame (mm)")
        ax.set_ylabel("y (mm)")
    fig.suptitle(f"Bracket, {SHORT[cfg]}: from G-code to voxels", x=0.01, ha="left", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


# --- the clamp ------------------------------------------------------------------------------------

def plot_clamp(res: dict, path: Path):
    ccx = json.loads((HERE / "ccx_split.json").read_text())["designs"]["0.6 mm"]["forces"]
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.2))
    Fc = sorted(int(k) for k in ccx)
    axs[0].plot(Fc, [ccx[str(F)]["split gap (mm)"]["narrowest"] for F in Fc], color=SOLID, lw=2, ls="--",
                label="solid PLA, CalculiX tets (ccx_split.py)")
    sol = get(res, "h2d_pahtcf_04", "clamp", solid=True)
    if sol:
        F = sorted(int(k) for k in sol["forces"])
        axs[0].plot(F, [sol["forces"][str(f)]["split gap (mm)"]["narrowest"] for f in F], color=SOLID, lw=2,
                    marker="s", ms=8, ls=":", label="solid PLA, these voxels (the check)")
    for cfg in ORDER:
        r = get(res, cfg, "clamp")
        if not r:
            continue
        F = sorted(int(k) for k in r["forces"])
        fo = r["forces"]
        axs[0].plot(F, [fo[str(f)]["split gap (mm)"]["narrowest"] for f in F], color=COLOR[cfg], lw=2, marker="o",
                    ms=8, label=SHORT[cfg] + ", as sliced")
        for ax, part in ((axs[1], "bracket"), (axs[2], "carrier")):
            ax.plot(F, [fo[str(f)]["peaks"][part]["failure index"] for f in F], color=COLOR[cfg], lw=2, marker="o",
                    ms=8, label=SHORT[cfg])
    axs[0].set_ylabel("split gap, narrowest (mm)")
    axs[0].set_title("The split closes", loc="left")
    axs[0].legend(frameon=False, fontsize=9)
    for ax, part in ((axs[1], "bracket"), (axs[2], "carrier")):
        ax.axhline(1.0, color=CRITICAL, lw=1.5)
        ax.text(ax.get_xlim()[0] if False else 60, 1.02, "first failure", color=CRITICAL, fontsize=9, va="bottom")
        ax.set_ylabel("peak failure index (1 = first failure)")
        ax.set_title(f"{part.capitalize()}: peak failure index", loc="left")
        ax.set_ylim(bottom=0)
    axs[1].legend(frameon=False, fontsize=9, loc="upper left")
    for ax in axs:
        ax.set_xlabel("force in each M3 (N)")
        ax.set_xscale("log")
        ax.set_xticks([50, 100, 200, 500, 1000])
        ax.set_xticklabels(["50", "100", "200", "500", "1000"])
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def plot_section(res: dict, path: Path, F: int = 500, window=(-24.0, 8.0, 18.0, 50.0)):
    """Section y = Y_CUT through both halves, at the top pair of ears: per config, the feature in each
    voxel, and its failure index at F per M3."""
    cfgs = [c for c in ORDER if (S.CACHE / f"viz_{c}_printed_{S.H_VOX:.2f}.pkl").exists()]
    if not cfgs:
        return
    fig, axs = plt.subplots(2, len(cfgs), figsize=(5.2 * len(cfgs), 10.2), squeeze=False)
    for col, cfg in enumerate(cfgs):
        viz = pickle.loads((S.CACHE / f"viz_{cfg}_printed_{S.H_VOX:.2f}.pkl").read_bytes())
        Fk = F if F in viz["fi"]["bracket"] else min(viz["fi"]["bracket"], key=lambda f: abs(f - F))
        for part in ("bracket", "carrier"):
            v = voxels(cfg, part)
            h = v["h"]
            hw = (abs(v["R"].T) @ h)            # voxel size along world x, y, z
            on = abs(v["cw"][:, 1] - Y_CUT) < hw[1] / 2
            x, z = v["cw"][on, 0], v["cw"][on, 2]
            feat = np.argmax(v["feat"][on], axis=1)
            fi = viz["fi"][part][Fk][on]
            for row, val, cmap, norm in ((0, feat, ListedColormap(FEATURE_COLORS), BoundaryNorm(np.arange(-0.5, 3.5), 3)),
                                         (1, fi, CMAP, plt.Normalize(0, 1))):
                axs[row, col].scatter(x, z, c=val, cmap=cmap, norm=norm, marker="s", s=(hw[0] * 7.2) ** 2,
                                      linewidths=0)
        p = S.load_params((S.EX / "params.json").read_text())
        for row in range(2):
            ax = axs[row, col]
            ax.add_patch(plt.Circle((p.ax_x, p.ax_z), p.body_r, fill=False, color=MUTED, lw=1, ls="--"))
            ax.set_xlim(window[0], window[1])
            ax.set_ylim(window[2], window[3])
            ax.set_aspect("equal")
            ax.set_xlabel("x (mm)")
            if col == 0:
                ax.set_ylabel("z (mm)")
        axs[0, col].set_title(f"{SHORT[cfg]}\nwhat is printed (y = {Y_CUT:g} mm)", loc="left", fontsize=10)
        axs[1, col].set_title(f"failure index at {Fk} N per M3", loc="left", fontsize=10)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in FEATURE_COLORS]
    axs[0, 0].legend(handles, S.GROUPS, loc="lower left", frameon=False, fontsize=9)
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=axs[1, :].tolist(), fraction=0.03, pad=0.02, extend="max")
    cb.set_label("failure index (red: over 1)")
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


# --- the other loads ------------------------------------------------------------------------------

def first_failure(res: dict) -> dict:
    """{case: {cfg: force to first failure (N)}} for the yank and the bump (worst direction and sign,
    linear, so 10 N / failure index), and the clamp (screw force where the peak index reaches 1,
    interpolated; None if not reached by 1000 N)."""
    out = {"cable yank (N at the plug)": {}, "pod bump (N on its edge)": {}, "clamp (N in each M3)": {}}
    for cfg in ORDER:
        y = get(res, cfg, "yank")
        if y:
            fi = max(v["carrier"][s]["failure index"] for v in y["cases"].values() for s in "+-")
            out["cable yank (N at the plug)"][cfg] = S.BUMP_N / fi
        b = get(res, cfg, "pod")
        if b:
            fi = max(v[part][s]["failure index"] for k, v in b["cases"].items() if k.startswith("bump")
                     for part in ("bracket", "pod") for s in "+-")
            out["pod bump (N on its edge)"][cfg] = S.BUMP_N / fi
        c = get(res, cfg, "clamp")
        if c:
            F = sorted(int(k) for k in c["forces"])
            fi = [max(c["forces"][str(f)]["peaks"][q]["failure index"] for q in ("bracket", "carrier")) for f in F]
            hit = None
            for (f0, a), (f1, b2) in zip(zip(F, fi), zip(F[1:], fi[1:])):
                if a < 1 <= b2:
                    hit = f0 + (1 - a) / (b2 - a) * (f1 - f0)
                    break
            out["clamp (N in each M3)"][cfg] = hit
    return out


def plot_loads(res: dict, path: Path):
    ff = first_failure(res)
    fig, axs = plt.subplots(1, 3, figsize=(16, 3.6))
    for ax, (case, vals) in zip(axs, ff.items()):
        cfgs = [c for c in ORDER if c in vals]
        ys = np.arange(len(cfgs))[::-1]
        for yy, cfg in zip(ys, cfgs):
            v = vals[cfg]
            if v is None:
                ax.barh(yy, 1000, color=COLOR[cfg], height=0.6, alpha=0.35)
                ax.text(1000, yy, "  not reached by 1000 N", va="center", color=INK2, fontsize=9)
                continue
            ax.barh(yy, v, color=COLOR[cfg], height=0.6)
            ax.text(v, yy, f"  {v:,.0f} N", va="center", color=INK, fontsize=10)
        ax.set_yticks(ys)
        ax.set_yticklabels([SHORT[c] for c in cfgs], fontsize=9)
        ax.set_title(case, loc="left", fontsize=11)
        ax.set_xlabel("force at the first failure (N)")
        ax.grid(True, axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.margins(x=0.35)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    res = results()
    plot_clamp(res, RENDERS / "sliced_clamp.png")
    plot_section(res, RENDERS / "sliced_section.png")
    plot_loads(res, RENDERS / "sliced_loads.png")
    plot_model(RENDERS / "sliced_model.png")
    print(json.dumps(first_failure(res), indent=1))


if __name__ == "__main__":
    main()
