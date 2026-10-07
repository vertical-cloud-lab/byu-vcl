#!/usr/bin/env python3
"""Pictures for sliced_fea.py, from sim/sliced_fea.json and the cache in sim/build_sliced/.

  renders/sliced_model.png    one layer of the bracket: the G-code raster, and the voxels made from it
  renders/sliced_clamp.png    the clamp: split gap and peak failure index against screw force
  renders/sliced_section.png  the section through the first clamp screws at 1000 N: what is printed
                              there, and how close each voxel is to failing
  renders/sliced_loads.png    force to the first failure for the cable yank, the pod bump and the clamp
  renders/sliced_convergence.png  the clamp at 1.0, 0.8 and 0.6 mm voxels, against the CalculiX tets

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
Y_CUT = 22.2                    # the first row of clamp screws (y = 22), just off it: voxel faces lie on whole mm
H_CASE = {"clamp": 0.6, "zones": 0.6, "pod": 1.0, "yank": 0.6}      # voxel size each case was run at
H_STUDY = (1.0, 0.8, 0.6)                                           # the clamp's voxel sizes
PLA_X = 35.0                    # MPa: the solid models' strength (ccx_stress.py), for an index from max principal


def results() -> dict:
    return json.loads((HERE / "sliced_fea.json").read_text())


def get(res: dict, cfg: str, case: str, solid: bool = False, h: float | None = None):
    h = H_CASE[case] if h is None else h
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

def bearing_by_hand(res: dict, cfg: str, F: int) -> tuple[float, float]:
    """(head, nut) bearing exposure at F per M3: the head presses the carrier across its layers (Zc),
    the nut presses the bracket within its layers (Yc, the lower of the two in-layer strengths)."""
    z = get(res, cfg, "zones")
    per_n = z["bearing stress by hand (MPa per N of screw force)"]
    m = S.material(S.CONFIGS[cfg]["material"])
    return per_n["head on the carrier"] * F / m["Zc"], per_n["nut on the bracket"] * F / m["Yc"]


def plot_clamp(res: dict, path: Path):
    """Peak failure index at snug (200 N per M3) and overtightened (1000 N): each half's collar and
    ears from the voxel model (away from the screws' bearing zones and the split faces), the bracket at
    CalculiX's ear-root peak, and the bearing under the heads and nuts by hand, per configuration."""
    rows = ["Bracket: collar and ears", "Bracket: at the ear root", "Carrier: collar and ears",
            "Carrier: under the heads (by hand)", "Bracket: under the nuts (by hand)"]
    fig, axs = plt.subplots(1, 2, figsize=(14, 6.4), sharey=True)
    away = "outside the bearing zones and the split faces"
    for ax, F in zip(axs, (200, 1000)):
        for k, cfg in enumerate(ORDER):
            z = get(res, cfg, "zones")
            if not z:
                continue
            vals = [z[str(F)]["bracket"][away]["failure index"],
                    z[str(F)]["bracket at CalculiX's ear-root peak"]["failure index"],
                    z[str(F)]["carrier"][away]["failure index"], *bearing_by_hand(res, cfg, F)]
            for r, v in enumerate(vals):
                y = len(rows) - 1 - r + (1 - k) * 0.26
                ax.barh(y, v, height=0.24, color=COLOR[cfg], label=SHORT[cfg] if r == 0 else None)
                ax.text(v + 0.01, y, f"{v:.2f}", va="center", fontsize=9, color=INK)
        ax.axvline(1.0, color=CRITICAL, lw=1.5)
        ax.text(1.01, -0.62, "first failure", color=CRITICAL, fontsize=9, va="bottom")
        ax.set_title({200: "Snug: 200 N in each M3", 1000: "Overtightened: 1000 N in each M3 (about 0.6 N m)"}[F],
                     loc="left", fontsize=12)
        ax.set_xlabel("peak failure index (1 = first failure)")
        ax.grid(True, axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.set_xlim(0, 1.25)
        ax.set_ylim(-0.7, len(rows) - 0.4)
    axs[0].set_yticks(range(len(rows)))
    axs[0].set_yticklabels(rows[::-1])
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=10)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=110)
    plt.close(fig)


def plot_section(res: dict, path: Path, F: int = 1000, window=(-24.0, 8.0, 18.0, 50.0)):
    """Section y = Y_CUT through both halves, at the top pair of ears: per config, the feature in each
    voxel, and its failure index at F per M3."""
    hc = H_CASE["clamp"]
    cfgs = [c for c in ORDER if (S.CACHE / f"viz_{c}_printed_{hc:.2f}.pkl").exists()]
    if not cfgs:
        return
    fig, axs = plt.subplots(2, len(cfgs), figsize=(5.2 * len(cfgs), 10.2), squeeze=False)
    for col, cfg in enumerate(cfgs):
        viz = pickle.loads((S.CACHE / f"viz_{cfg}_printed_{hc:.2f}.pkl").read_bytes())
        Fk = F if F in viz["fi"]["bracket"] else min(viz["fi"]["bracket"], key=lambda f: abs(f - F))
        for part in ("bracket", "carrier"):
            v = voxels(cfg, part, hc)
            h = v["h"]
            hw = (abs(v["R"].T) @ h)            # voxel size along world x, y, z
            on = abs(v["cw"][:, 1] - Y_CUT) < hw[1] / 2
            x, z = v["cw"][on, 0], v["cw"][on, 2]
            feat = np.argmax(v["feat"][on], axis=1)
            fi = viz["fi"][part][Fk][on]
            from matplotlib.collections import PatchCollection
            for row, val, cmap, norm in ((0, feat, ListedColormap(FEATURE_COLORS), BoundaryNorm(np.arange(-0.5, 3.5), 3)),
                                         (1, fi, CMAP, plt.Normalize(0, 1))):
                rects = [plt.Rectangle((a - hw[0] / 2, b - hw[2] / 2), hw[0], hw[2]) for a, b in zip(x, z)]
                pc = PatchCollection(rects, cmap=cmap, norm=norm, linewidths=0)
                pc.set_array(np.asarray(val, float))
                axs[row, col].add_collection(pc)
        p = S.load_params((S.EX / "params.json").read_text())
        for row in range(2):
            ax = axs[row, col]
            ax.add_patch(plt.Circle((p.ax_x, p.ax_z), p.body_r, fill=False, color=MUTED, lw=1, ls="--"))
            if row == 1:            # the nut and head bearing zones (sliced_fea.bearing_zone), set apart
                for xf in (p.ax_x - p.ear_w + p.m3_nut_depth, p.ax_x + p.clamp_head_seat):
                    ax.add_patch(plt.Rectangle((xf - 4.0, p.ax_z + p.clamp_r - 4.5), 8.0, 9.0, fill=False,
                                               color=INK2, lw=1.2, ls=":"))
                for sx in (-1, 1):  # the split faces' zone (sliced_fea.split_zone)
                    ax.axvline(p.ax_x + sx * (p.split_gap / 2 + S.SPLIT_DEPTH), color=INK2, lw=0.9, ls=(0, (1, 2)))
                ax.text(window[0] + 0.5, window[3] - 1.0, "dotted: bearing zones under the nut and head,\n"
                        "and the split faces' zone", fontsize=8, color=INK2, va="top")
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


def convergence(res: dict) -> dict:
    """{series: {quantity: {F: [value at each of H_STUDY, or None]}}} for the clamp, plus CalculiX's
    solid-PLA values. Series: the three prints, and the solid-PLA voxels (h2d_pahtcf_04's grid)."""
    ccx = json.loads((HERE / "ccx_split.json").read_text())["designs"]["0.6 mm"]["forces"]
    series = [(cfg, False) for cfg in ORDER] + [("h2d_pahtcf_04", True)]
    out = {}
    for cfg, solid in series:
        name = "solid" if solid else cfg
        out[name] = {"faces": {}, "squeeze": {}, "ear": {}, "peak": {}, "edge": {}}
        for F in (200, 1000):
            for key in out[name]:
                out[name][key][F] = []
            for h in H_STUDY:
                c, z = get(res, cfg, "clamp", solid, h), get(res, cfg, "zones", solid, h)
                r = c["forces"].get(str(F)) if c else None
                out[name]["faces"][F].append(r["split contact force (N)"] if r else None)
                out[name]["squeeze"][F].append(r["body: radial contact force, summed (N)"]["bracket"] if r else None)
                zz = z.get(str(F)) if z else None
                away, face = "outside the bearing zones and the split faces", "at the split faces, outside the bearing zones"
                if zz is None:
                    ear = peak = edge = None
                elif solid:
                    ear = zz["bracket at CalculiX's ear-root peak"]["max principal (MPa)"]["value"] / PLA_X
                    peak = zz["bracket"][away]["max principal (MPa)"]["value"] / PLA_X
                    edge = zz["bracket"][face]["max principal (MPa)"]["value"] / PLA_X
                else:
                    ear = zz["bracket at CalculiX's ear-root peak"]["failure index"]
                    peak = zz["bracket"][away]["failure index"]
                    edge = zz["bracket"][face]["failure index"]
                out[name]["ear"][F].append(ear)
                out[name]["peak"][F].append(peak)
                out[name]["edge"][F].append(edge)
    pk = "peaks away from the screw seats"
    out["CalculiX"] = {"faces": {F: ccx[str(F)]["split contact force (N)"]["total"] for F in (200, 1000)},
                       "squeeze": {F: ccx[str(F)]["body: radial contact force, summed (N)"]["bracket"] for F in (200, 1000)},
                       "ear": {F: ccx[str(F)][pk]["max principal (MPa)"]["bracket"]["value"] / PLA_X for F in (200, 1000)}}
    return out


def plot_convergence(res: dict, path: Path):
    """Small multiples, snug (top) and overtightened (bottom): the faces' push, the squeeze on the body
    and the bracket's index at CalculiX's ear-root peak, against voxel size, refining to the right."""
    cv = convergence(res)
    cols = [("faces", "faces pushing at the split (N)"), ("squeeze", "squeeze on the body, bracket's half (N)"),
            ("ear", "bracket: index at the ear root"), ("edge", "bracket: index at the split faces' edges")]
    fig, axs = plt.subplots(2, 4, figsize=(19, 8.4))
    names = ORDER + ["solid"]
    for row, F in enumerate((200, 1000)):
        for col, (key, label) in enumerate(cols):
            ax = axs[row, col]
            for name in names:
                ys = cv[name][key][F]
                pts = [(h, y) for h, y in zip(H_STUDY, ys) if y is not None]
                if not pts:
                    continue
                hx, yy = zip(*pts)
                color = SOLID if name == "solid" else COLOR[name]
                ls = (0, (5, 2)) if name == "solid" else "-"
                ax.plot(hx, yy, ls=ls, lw=2, color=color, zorder=3,
                        label="solid PLA, same voxels" if name == "solid" else SHORT[name])
                ax.plot(hx, yy, "o", ms=8, color=color, mec=SURFACE, mew=2, zorder=4)
            ref = cv["CalculiX"].get(key, {}).get(F)
            if ref is not None:
                ax.axhline(ref, color=INK2, lw=1.2, ls=(0, (2, 2)), zorder=2)
                ax.text(0.585, ref, "CalculiX tets,\nsolid PLA", color=INK2, fontsize=8.5, va="center", ha="left")
            ax.set_xlim(1.04, 0.47)
            ax.set_xticks(H_STUDY)
            ax.set_ylim(bottom=0)
            ax.grid(True, color=GRID, lw=0.8)
            ax.set_axisbelow(True)
            if row == 1:
                ax.set_xlabel("voxel size (mm), finer to the right")
            ax.set_title(label, loc="left", fontsize=11)
        axs[row, 0].set_ylabel({200: "snug: 200 N per M3", 1000: "overtightened: 1000 N per M3"}[F])
    for col in (2, 3):
        axs[1, col].text(0.0, -0.17, "prints: failure index; solid: max principal / 35 MPa", transform=axs[1, col].transAxes,
                         fontsize=8.5, color=INK2, va="top")
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=110)
    plt.close(fig)


# --- the other loads ------------------------------------------------------------------------------

def first_failure(res: dict) -> dict:
    """{case: {cfg: force to first failure (N)}} for the yank and the bump: worst direction and sign,
    and linear, so 10 N / failure index."""
    out = {"cable yank (N at the USB-C plug)": {}, "pod bump (N on its outer edge)": {}}
    for cfg in ORDER:
        y = get(res, cfg, "yank")
        if y:
            fi = max(v["carrier"][s]["failure index"] for v in y["cases"].values() for s in "+-")
            out["cable yank (N at the USB-C plug)"][cfg] = S.BUMP_N / fi
        b = get(res, cfg, "pod")
        if b:
            fi = max(v[part][s]["failure index"] for k, v in b["cases"].items() if k.startswith("bump")
                     for part in ("bracket", "pod") for s in "+-")
            out["pod bump (N on its outer edge)"][cfg] = S.BUMP_N / fi
    return out


def plot_loads(res: dict, path: Path):
    ff = first_failure(res)
    fig, axs = plt.subplots(1, 2, figsize=(14, 3.4))
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
        ax.set_xlabel("force at the first failure, voxel model (N)")
        ax.grid(True, axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.margins(x=0.35)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def tables(res: dict) -> str:
    """Markdown tables of the results, for the README."""
    out = []
    ccx = json.loads((HERE / "ccx_stress.json").read_text())
    for cfg in ORDER:
        c = get(res, cfg, "clamp")
        if not c:
            continue
        out.append(f"\nclamp, {SHORT[cfg]} ({H_CASE['clamp']} mm voxels)\n")
        out.append("| Force in each M3 | Narrowest gap | Faces pushing | Bracket: index, mode | Carrier: index, mode |")
        out.append("|---|---|---|---|---|")
        for F in sorted(int(k) for k in c["forces"]):
            r = c["forces"][str(F)]
            b, k = r["peaks"]["bracket"], r["peaks"]["carrier"]
            g = r["split gap (mm)"]["narrowest"]
            out.append(f"| {F} N | {'closed' if g < 1e-3 else f'{g:.2f} mm'} | {r['split contact force (N)']:,.0f} N | "
                       f"{b['failure index']:.2f}, {b['mode']} ({b['feature']}) | "
                       f"{k['failure index']:.2f}, {k['mode']} ({k['feature']}) |")
    for case in ("yank", "pod"):
        for h in (0.6, 0.8):
            for cfg in ORDER:
                r = get(res, cfg, case, h=h)
                if not r:
                    continue
                worst = None
                for name, v in r["cases"].items():
                    if not (name.startswith("yank") or name.startswith("bump")):
                        continue
                    for part, vv in v.items():
                        if not isinstance(vv, dict) or "+" not in vv:
                            continue
                        for sgn in "+-":
                            x = vv[sgn]
                            if worst is None or x["failure index"] > worst[0]:
                                worst = (x["failure index"], f"{sgn}{name.split()[-1]}", part, x)
                fi, d, part, x = worst
                out.append(f"{case} h {h} {SHORT[cfg]}: worst {d} in the {part}: index {fi:.3f} -> "
                           f"{S.BUMP_N / fi:.0f} N to first failure, {x['mode']}, {x['feature']}, at {x['at (mm)']}, "
                           f"tension across layers {x['largest bead tension across the layers (MPa)']['value']} MPa")
                if case == "pod":
                    for dn in "XYZ":
                        hq = r["cases"][f"HQ 1 g {dn}"]
                        out.append(f"   HQ 1 g {dn}: {hq['mean displacement (um)']:.3f} um, tilt "
                                   f"{hq['optical axis tilt (arcmin)']:.4f} arcmin, max {hq['max displacement anywhere (um)']:.2f} um")
    ref = ccx["bracket + pod"]["check against joint_fea.py (83 g at 1 g on the HQ bosses)"]
    out.append("ccx solid HQ 1 g: " + ", ".join(f"{d}: {ref[d]['mean displacement (um)']['ccx']:.3f} um / "
                                                 f"{ref[d]['optical axis tilt (arcmin)']['ccx']:.4f} arcmin" for d in "XYZ"))
    out.append("ccx solid yank peaks: " + json.dumps({k: v["max principal (MPa)"]["carrier"]["value"]
                                                       for k, v in ccx["carrier: cable yank"]["peaks (at least 2 mm from the bore)"].items()}))
    sol = get(res, "h2d_pahtcf_04", "yank", solid=True)
    if sol:
        out.append("voxel solid yank peaks: " + json.dumps({k + s: v["carrier"][s]["max principal (MPa)"]["value"]
                                                             for k, v in sol["cases"].items() for s in "+-"}))
    for cfg in ORDER:
        for part in ("bracket", "pod", "carrier"):
            fg = S.CACHE / f"{cfg}_{part}_{S.H_VOX:.2f}.pkl"
            if fg.exists():
                vc = pickle.loads(fg.read_bytes())["volume check"]["total"]
                out.append(f"volume {cfg} {part}: raster {vc['raster_mm3']:.0f} gcode {vc['gcode_mm3']:.0f} "
                           f"ratio {vc['raster / gcode']:.3f}")
    return "\n".join(out)


def main():
    res = results()
    print(tables(res))
    plot_clamp(res, RENDERS / "sliced_clamp.png")
    plot_section(res, RENDERS / "sliced_section.png")
    plot_convergence(res, RENDERS / "sliced_convergence.png")
    if "--all" in sys.argv:             # these two don't depend on the clamp
        plot_loads(res, RENDERS / "sliced_loads.png")
        plot_model(RENDERS / "sliced_model.png")
    print(json.dumps(first_failure(res), indent=1))


if __name__ == "__main__":
    main()
