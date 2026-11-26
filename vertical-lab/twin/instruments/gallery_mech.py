"""Figures of the mechanical, powder and corrosion instrument simulators: raw data and the values extracted from it.

Run from ``vertical-lab``::

    nice -n 10 /tmp/venv/bin/python -m twin.instruments.gallery_mech

Writes ``out/twin2/instruments/*.png`` (PSD, atomizer yield and mass balance, PIP profile and fitted curve, tensile
curves, Vickers and nanoindentation, corrosion screen: OCP, LPR, Nyquist, cyclic polarization; immersion; powder
reuse; PIP against tensile over the calibration set) and the 512 x 512 transparent thumbnails
``out/twin2/thumbs/{psd,tensile,pip,hardness,corrosion,yield}.png`` for the video's DAG icons. Samples are built
through the truths the way ``truth_al.reference_table()`` / ``truth_cu.reference_table()`` do
(``calibrate_mech.reference_samples``): AlSi10Mg, Scalmalloy and a porous, cracked 7075 for FLAIME; 70-30 Cu-Ni and
NAB for ONR.
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from twin.instruments import (atomize_yield, calibrate_mech as cm, corrosion, hardness, pip, psd, reuse,  # noqa: E402
                              tensile)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "twin2" / "instruments"
THUMBS = ROOT / "out" / "twin2" / "thumbs"
# fixed categorical order (the dataviz skill's reference palette): one hue per sample, never cycled
COLORS = {"AlSi10Mg": "#257de0", "Scalmalloy": "#f47230", "7075 porous, cracked": "#00b894",
          "C71500 70-30 Cu-Ni": "#f2a600", "C95800 NAB": "#ee7fac"}
SHORT = {"AlSi10Mg": "AlSi10Mg", "Scalmalloy": "Scalmalloy", "7075 porous, cracked": "7075, porous + cracked",
         "C71500 70-30 Cu-Ni": "70-30 Cu-Ni", "C95800 NAB": "NAB (C95800)"}
AL = ["AlSi10Mg", "Scalmalloy", "7075 porous, cracked"]
CU = ["C71500 70-30 Cu-Ni", "C95800 NAB"]
TEXT, TEXT2 = "#191919", "#666666"


def _style():
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": TEXT2, "axes.labelcolor": TEXT, "xtick.color": TEXT2,
                         "ytick.color": TEXT2, "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6,
                         "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                         "figure.dpi": 110, "savefig.dpi": 160})


def _title(ax, text):
    ax.set_title(text, fontsize=8.5, color=TEXT, loc="left")


def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    return OUT / name


def fig_psd(refs, rng):
    labs = ["AlSi10Mg", "Scalmalloy", "C71500 70-30 Cu-Ni", "C95800 NAB"]
    fig, axs = plt.subplots(2, 4, figsize=(13, 5.6))
    for j, lab in enumerate(labs):
        lot = refs[lab][0]
        r = psd.measure(lot, lot["campaign"], rng, "full")
        psd.draw(r, [axs[0, j], axs[1, j]])
        _title(axs[0, j], f"{SHORT[lab]}: d10/d50/d90 {r['d10_um']:.0f}/{r['d50_um']:.0f}/{r['d90_um']:.0f} um, "
                          f"span {r['span']:.2f}\ncut {100 * r['cut_frac']:.0f} %, fines {100 * r['fines_frac']:.1f} %")
        if j:
            for a in axs[:, j]:
                leg = a.get_legend()
                if leg:
                    leg.remove()
    fig.suptitle("Laser diffraction (Mastersizer 3000 + Aero S): the lot's true distribution and the instrument's reading",
                 x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return _save(fig, "psd.png")


def fig_yield(refs, rng):
    labs = ["AlSi10Mg", "C95800 NAB"]
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.4))
    for i, lab in enumerate(labs):
        lot = refs[lab][0]
        r = atomize_yield.measure(lot, lot["campaign"], rng, "full")
        atomize_yield.draw(r, axs[i])
        _title(axs[i, 0], f"{SHORT[lab]}: charged {r['charge_g']:.0f} g, collected {r['collected_g']:.0f} g "
                          f"({100 * r['yield_frac']:.0f} %), in the cut {r['cut_g']:.0f} g "
                          f"({100 * r['cut_yield_frac']:.0f} %)")
    plans = []
    for camp in ("flaime_al", "onr_cu"):
        for cm3 in (225, 400):
            p = atomize_yield.charge_plan(camp, cm3)
            plans.append(f"{'Al' if camp == 'flaime_al' else 'Cu'} {cm3} cm3: {p['charge_g']:.0f} g/run, "
                         f"{p['run_h']:.2f} h, +{100 * p['p_fail_add']:.1f} % drip risk")
    fig.text(0.01, -0.02, "Crucible plans (charge_plan, default fill):  " + ";  ".join(plans), fontsize=7.5,
             color=TEXT2)
    fig.suptitle("Atomizer mass balance and sieving, run by run", x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return _save(fig, "yield.png")


def fig_pip(refs, rng):
    labs = AL + CU
    fig, axs = plt.subplots(2, len(labs), figsize=(15, 5.8))
    for j, lab in enumerate(labs):
        part = refs[lab][1]
        r = pip.measure(part, part["campaign"], rng, "full")
        t = tensile.measure(part, part["campaign"], np.random.default_rng(5), "lite")
        pip.draw(r, [axs[0, j], axs[1, j]], color=COLORS[lab])
        ys_t = t.get("ys_MPa")
        _title(axs[0, j], f"{SHORT[lab]}\nPIP YS {r['ys_MPa']:.0f}, UTS {r['uts_MPa']:.0f} MPa, "
                          f"UE {r['ue_pct']:.1f} %")
        axs[1, j].text(0.03, 0.04, (f"tensile YS {ys_t:.0f}" if ys_t else "tensile: no 0.2 % yield") +
                       f", UTS {t['uts_MPa']:.0f} MPa, EL {t['el_pct']:.1f} %\nporosity {100 * part['porosity']:.1f} %, "
                       f"cracks {part['crack_density']:.2f} mm/mm2", transform=axs[1, j].transAxes, fontsize=7,
                       color=TEXT2)
        if j == 0:
            axs[0, j].legend(fontsize=7, loc="lower right")
            axs[1, j].legend(fontsize=7, loc="center right")
    fig.suptitle("Indentation plastometry: the residual indent's profile (stylus), the fitted model, and the Voce "
                 "law it implies (the sound metal under the indent, not the bar)", x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return _save(fig, "pip.png")


def fig_tensile(refs, rng):
    labs = AL + CU
    fig, axs = plt.subplots(1, len(labs), figsize=(15, 3.6))
    for j, lab in enumerate(labs):
        part = refs[lab][1]
        r = tensile.measure(part, part["campaign"], rng, "full")
        tensile.draw(r, axs[j], color=COLORS[lab], label="RT")
        st = part["strength"]
        txt = f"{SHORT[lab]}\n" + ("YS {:.0f}, ".format(r["ys_MPa"]) if "ys_MPa" in r else "no 0.2 % yield, ") + \
            f"UTS {r['uts_MPa']:.0f} MPa, EL {r['el_pct']:.1f} %\n(truth {st['ys_MPa']:.0f} / {st['uts_MPa']:.0f} / " \
            f"{st['el_pct']:.1f})"
        if part.get("strength_hot"):
            h = tensile.measure_hot(part, part["campaign"], rng, "full")
            for i, b in enumerate(h["raw"]["bars"]):
                axs[j].plot(100 * b["strain"], b["stress_MPa"], lw=1.0, color=COLORS[lab], ls="--", alpha=0.8,
                            label="250 C" if i == 0 else None)
            txt += f"\n250 C: YS {h.get('ys_MPa', float('nan')):.0f}, UTS {h['uts_MPa']:.0f}"
        _title(axs[j], txt)
        axs[j].legend(fontsize=7, loc="lower right")
    fig.suptitle("Tensile tests, three sub-size bars each: the scatter and the early breaks come from each bar's "
                 "largest defect", x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return _save(fig, "tensile.png")


def fig_hardness(refs, rng):
    labs = AL + CU
    fig, axs = plt.subplots(2, len(labs), figsize=(15, 5.6))
    for j, lab in enumerate(labs):
        part = refs[lab][1]
        v = hardness.measure_vickers(part, part["campaign"], rng, "full")
        n = hardness.measure_nanoindent(part, part["campaign"], rng, "full")
        hardness.draw(v, n, [axs[0, j], axs[1, j]], color=COLORS[lab])
        _title(axs[0, j], f"{SHORT[lab]}\nHV0.5 {v['hv']:.0f} +- {v['hv_sd']:.0f} (Tabor {v['raw']['hv_tabor']:.0f})")
        _title(axs[1, j], f"H {n['H_GPa']:.2f} GPa, E {n['E_GPa']:.0f} GPa (Oliver-Pharr)")
    fig.suptitle("Vickers (HM-220, 5 indents) and nanoindentation (iMicro, Berkovich): load-displacement curves",
                 x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return _save(fig, "hardness.png")


def fig_corrosion(refs, rng):
    fig, axs = plt.subplots(2, 4, figsize=(15, 6.2))
    for i, lab in enumerate(CU):
        part = refs[lab][1]
        r = corrosion.measure_screen(part, "onr_cu", rng, "full")
        corrosion.draw_screen(r, axs[i])
        c = part["corrosion"]
        for a in axs[i]:
            a.set_title("")
        _title(axs[i, 0], f"{SHORT[lab]}: OCP {r['ocp_mV']:.0f} mV\nearly rate {r['early_rate_um_yr']:.0f} um/yr "
                          f"(truth {c['early_rate_um_yr']:.0f})")
        _title(axs[i, 1], f"LPR: Rp {r['rp_ohm_cm2'] / 1e3:.1f} kOhm cm2, icorr {r['icorr_uA_cm2']:.2f} uA/cm2")
        _title(axs[i, 2], f"EIS: Rct {r['rct_ohm_cm2'] / 1e3:.1f} kOhm cm2")
        _title(axs[i, 3], f"CP: Eb {r.get('Eb_mV', float('nan')):.0f} mV, Erp {r.get('Erp_mV', float('nan')):.0f} mV\n"
                          f"(truth Eb {c['Eb_mV']:.0f})")
    fig.suptitle("CubXL corrosion screen in artificial seawater (0.071 cm2 well): OCP, LPR, EIS (Nyquist, Randles + "
                 "CPE + Warburg fit), cyclic polarization", x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    p1 = _save(fig, "corrosion_screen.png")
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.2))
    for i, lab in enumerate(CU):
        part = refs[lab][1]
        r = corrosion.measure_immersion(part, "onr_cu", rng, "full")
        corrosion.draw_immersion(r, axs[i])
        c = part["corrosion"]
        for a in axs[i]:
            a.set_title("")
        _title(axs[i, 0], f"{SHORT[lab]}: 30-day rate {r['rate30_um_yr']:.1f} um/yr, attack {r['attack_um']:.1f} um\n"
                          f"(truth long-term {c['rate_um_yr']:.1f} um/yr, attack {c['attack_um']:.1f} um)")
        _title(axs[i, 1], "ICP-MS: Cu {} ppb, Ni {} ppb".format(
            f"{r['cu_ppb']:.0f}" if r.get("cu_ppb") is not None else "< LOD",
            f"{r['ni_ppb']:.0f}" if r.get("ni_ppb") is not None else "< LOD"))
    fig.suptitle("30-day immersion: mass loss through ASTM G1 cleaning, SEM attack depth, ICP-MS of the solution",
                 x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return p1, _save(fig, "immersion.png")


def fig_reuse():
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
    reuse.draw(axs)
    fig.suptitle("Powder reuse: oxygen, size and satellites cycle by cycle", x=0.01, ha="left", color=TEXT)
    fig.tight_layout()
    return _save(fig, "reuse.png")


def fig_pip_vs_tensile(n=60):
    """PIP against tensile yield over the calibration designs: PIP reads the sound metal, so porous and cracked
    parts sit above the diagonal."""
    rows = []
    for camp in ("flaime_al", "onr_cu"):
        for lot, part in cm.representative(camp, n, seed=3):
            rng = np.random.default_rng(len(rows))
            t = tensile.measure(part, camp, rng, "lite")
            p = pip.measure(part, camp, rng, "lite")
            rows.append((camp, t.get("ys_MPa"), p["ys_MPa"], t["uts_MPa"], p["uts_MPa"], part["porosity"],
                         part["crack_density"]))
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
    for k, (ax, it, ip, name) in enumerate(((axs[0], 1, 2, "yield (MPa)"), (axs[1], 3, 4, "UTS (MPa)"))):
        for camp, col, lab in (("flaime_al", "#257de0", "FLAIME (Al, LPBF)"), ("onr_cu", "#f47230", "ONR (Cu, DED)")):
            r = [x for x in rows if x[0] == camp and x[it] is not None]
            sev = np.array([x[5] + 0.02 * min(x[6], 2) for x in r])
            ax.scatter([x[it] for x in r], [x[ip] for x in r], s=12 + 900 * sev, color=col, alpha=0.55, lw=0,
                       label=lab)
        lim = [0, max(max(x[ip] for x in rows), max(x[it] or 0 for x in rows)) * 1.05]
        ax.plot(lim, lim, color=TEXT2, lw=0.8)
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_xlabel(f"tensile {name}")
        ax.set_ylabel(f"PIP {name}")
        _title(ax, f"{name.split(' ')[0]}: marker area grows with porosity and cracks")
    axs[0].legend(fontsize=7, loc="upper left")
    fig.suptitle("PIP samples about 1 mm3 of sound metal; the bar fails at its worst defect", x=0.01, ha="left",
                 color=TEXT)
    fig.tight_layout()
    return _save(fig, "pip_vs_tensile.png")


# ---------------------------------------------------------------------------------------------- thumbnails
def thumbs():
    THUMBS.mkdir(parents=True, exist_ok=True)
    out = []
    for name, f in (("psd", psd.thumb), ("tensile", tensile.thumb), ("pip", pip.thumb), ("hardness", hardness.thumb),
                    ("corrosion", corrosion.thumb), ("yield", atomize_yield.thumb)):
        fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
        ax = fig.add_axes([0.06, 0.06, 0.88, 0.88])
        f(ax)
        ax.set_axis_off()
        fig.savefig(THUMBS / f"{name}.png", dpi=100, transparent=True)
        plt.close(fig)
        out.append(THUMBS / f"{name}.png")
    return out


def main():
    _style()
    refs = cm.reference_samples(seed=0)
    rng = np.random.default_rng(2026)
    written = [fig_psd(refs, rng), fig_yield(refs, rng), fig_pip(refs, rng), fig_tensile(refs, rng),
               fig_hardness(refs, rng), *fig_corrosion(refs, rng), fig_reuse(), fig_pip_vs_tensile()]
    written += thumbs()
    for p in written:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()
