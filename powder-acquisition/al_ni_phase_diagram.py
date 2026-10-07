"""Al-Ni phase diagram and Ni-disc dissolution check for the Al cup (issue #161).

Question (2026-10-07): Ni melts at 1455 degC, above the rePOWDER induction rating,
so Ni cannot be atomized on its own. Would a ~1 mm Ni 200 disc sliced from a 1/2 in
rod dissolve in the Al cup instead?

Computes, with pycalphad and the Dupin, Ansara & Sundman (2001) Al-Ni assessment
(Calphad 25, 279-298; the TDB ships in pycalphad's test databases):

1. the full Al-Ni binary diagram (figure);
2. the Al-rich liquidus, i.e. the temperature at which Al-x wt% Ni is all liquid;
3. how much Ni liquid Al can hold at a given temperature (the liquid composition
   in equilibrium with Al3Ni / Al3Ni2) -- the driving force for dissolving a disc;
4. the heat released when solid Ni dissolves into liquid Al, and the resulting
   adiabatic temperature rise of a 100 g charge.

COST507, used for Al-Ti in al_ti_melt_window.py, has no Al-Ni intermetallics.

Usage:  python al_ni_phase_diagram.py          (prints tables, writes JSON cache)
        python al_ni_phase_diagram.py --plot   (also writes al-ni-phase-diagram.png)
Requires: pycalphad (>= 0.11), matplotlib, numpy.
"""

import json
import os
import sys
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TDB_NAME = "alni_dupin_2001.tdb"
TDB_URL = ("https://raw.githubusercontent.com/pycalphad/pycalphad/develop/"
           "pycalphad/tests/databases/" + TDB_NAME)
CACHE = os.path.join(HERE, "al-ni-phase-diagram-data.json")
FIG = os.path.join(HERE, "al-ni-phase-diagram.png")

M = {"AL": 26.9815, "NI": 58.6934}
RHO = {"NI": 8.90, "AL_LIQ": 2.37}       # g/cm3 (solid Ni; liquid Al near 700 degC)
CP_AL_LIQ = 31.75                        # J/(mol K), liquid Al

_db = None


def _tdb_path():
    """Prefer the copy bundled with pycalphad; otherwise download it once."""
    try:
        import pycalphad
        p = os.path.join(os.path.dirname(pycalphad.__file__), "tests", "databases", TDB_NAME)
        if os.path.exists(p):
            return p
    except ImportError:
        pass
    p = os.path.join(HERE, TDB_NAME)
    if not os.path.exists(p):
        urllib.request.urlretrieve(TDB_URL, p)
    return p


def db():
    global _db
    if _db is None:
        from pycalphad import Database
        _db = Database(_tdb_path())
    return _db


def phases():
    return sorted(db().phases.keys())


def wt_to_x(w):
    """wt% Ni in Al -> mole fraction Ni."""
    a, b = w / M["NI"], (100.0 - w) / M["AL"]
    return a / (a + b)


def x_to_wt(x):
    a, b = x * M["NI"], (1 - x) * M["AL"]
    return 100.0 * a / (a + b)


def _eq(x, T):
    from pycalphad import equilibrium
    import pycalphad.variables as v
    return equilibrium(db(), ["AL", "NI", "VA"], phases(),
                       {v.X("NI"): x, v.T: T, v.P: 101325, v.N: 1},
                       calc_opts={"pdens": 500})


def _phase_table(eq):
    names = np.asarray(eq.Phase.values).ravel()
    fracs = np.asarray(eq.NP.values).ravel()
    xs = np.asarray(eq.X.sel(component="NI").values).reshape(len(names), -1)[:, 0] \
        if eq.X.ndim else None
    out = []
    for i, (n, f) in enumerate(zip(names, fracs)):
        if n and np.isfinite(f) and f > 1e-8:
            out.append((str(n), float(f), float(xs[i]) if xs is not None else float("nan")))
    return out


def solid_fraction(x, T):
    return sum(f for n, f, _ in _phase_table(_eq(x, T)) if n != "LIQUID")


def liquid_fraction(x, T):
    return sum(f for n, f, _ in _phase_table(_eq(x, T)) if n == "LIQUID")


def liquidus(w, lo=700.0, hi=2000.0, tol=0.25):
    """Lowest temperature (degC) at which Al-`w` wt% Ni is 100% liquid."""
    x = wt_to_x(w)
    if solid_fraction(x, hi) > 1e-6:
        return float("nan")
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if solid_fraction(x, mid) > 1e-6:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) - 273.15


def solidus(w, lo=700.0, hi=1000.0, tol=0.25):
    """Highest temperature (degC) at which Al-`w` wt% Ni is still 100% solid."""
    x = wt_to_x(w)
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if liquid_fraction(x, mid) > 1e-6:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi) - 273.15


def ni_capacity_of_liquid(T_c):
    """wt% Ni in the liquid that coexists with Al3Ni (or Al3Ni2 above ~854 degC):
    the most Ni liquid Al can carry at T before an aluminide must form. This is the
    saturation concentration C_s that drives dissolution of a solid Ni disc.
    Probes overall compositions inside the L + aluminide field until one is two-phase."""
    for x_overall in (0.22, 0.30, 0.36, 0.45):
        rows = _phase_table(_eq(x_overall, T_c + 273.15))
        liq = [x for n, f, x in rows if n == "LIQUID"]
        solids = [n for n, f, x in rows if n != "LIQUID"]
        if liq and solids:
            return x_to_wt(liq[0]), solids
    return float("nan"), []


def dissolution_enthalpy(T_c=750.0, w=2.0):
    """kJ released per mol Ni when solid fcc Ni dissolves into liquid Al to
    give Al-w wt% Ni at T, and the adiabatic temperature rise of 100 g."""
    from pycalphad import calculate
    import pycalphad.variables as v
    T = T_c + 273.15
    x = wt_to_x(w)
    h_liq = calculate(db(), ["AL", "NI", "VA"], "LIQUID", T=T, P=101325,
                      points=np.array([[1 - x, x]]), output="HM").HM.values.ravel()[0]
    h_al = calculate(db(), ["AL", "VA"], "LIQUID", T=T, P=101325,
                     points=np.array([[1.0]]), output="HM").HM.values.ravel()[0]
    h_ni = calculate(db(), ["NI", "VA"], "FCC_A1", T=T, P=101325,
                     points=np.array([[1.0, 1.0]]), output="HM").HM.values.ravel()[0]
    dh_mix = h_liq - ((1 - x) * h_al + x * h_ni)      # J per mol of atoms of mixture
    dh_per_mol_ni = dh_mix / x                        # J per mol Ni dissolved
    m_ni = w                                          # g Ni in a 100 g charge
    n_ni = m_ni / M["NI"]
    n_al = (100.0 - w) / M["AL"]
    q = -dh_per_mol_ni * n_ni                         # J released
    dT = q / ((n_al + n_ni) * CP_AL_LIQ)
    return dh_per_mol_ni / 1000.0, q, dT


COMPARE = ["FE", "MN", "CR", "TI", "ZR"]   # computed with COST507 (al_ti_melt_window.py)
M.update({"FE": 55.845, "MN": 54.938, "CR": 51.996, "TI": 47.867, "ZR": 91.224})


def solubility_in_liquid_al(el, T_c):
    """wt% of `el` the liquid holds next to its Al-richest aluminide at T. Dissolution of
    a solid addition is boundary-layer diffusion controlled and its rate scales with this
    number (Darby, Jugle & Kleppa 1963), so it ranks how easily each solute goes in."""
    from pycalphad import equilibrium
    import pycalphad.variables as v
    if el == "NI":
        return ni_capacity_of_liquid(T_c)[0]
    from pycalphad.core.utils import filter_phases, unpack_species
    import al_ti_melt_window as alti
    cdb = alti._get_db()
    comps = ["AL", el, "VA"]
    ph = alti.PHASE_SETS.get(el) or filter_phases(cdb, unpack_species(cdb, comps))
    for x_overall in (0.02, 0.05, 0.1, 0.2, 0.3):
        eq = equilibrium(cdb, comps, ph, {v.X(el): x_overall, v.T: T_c + 273.15,
                                          v.P: 101325, v.N: 1}, calc_opts={"pdens": 500})
        names = np.asarray(eq.Phase.values).ravel()
        fr = np.asarray(eq.NP.values).ravel()
        xs = np.asarray(eq.X.sel(component=el).values).reshape(len(names), -1)[:, 0]
        liq = [xs[i] for i, n in enumerate(names) if n == "LIQUID" and fr[i] > 1e-8]
        sol = [n for i, n in enumerate(names) if n not in ("", "LIQUID")
               and np.isfinite(fr[i]) and fr[i] > 1e-8]
        if liq and sol:
            a, b = liq[0] * M[el], (1 - liq[0]) * M["AL"]
            return 100.0 * a / (a + b)
    return float("nan")


def compute():
    w_grid = sorted(set([0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 5.5,
                         5.75, 6.0, 6.25, 6.5, 7.0] + [float(w) for w in range(8, 43)]))
    data = {"source": "Dupin, Ansara & Sundman, Calphad 25 (2001) 279",
            "liquidus": [[w, liquidus(w)] for w in w_grid]}
    data["solidus_2wt"] = solidus(2.0)
    data["capacity"] = {}
    for t in (650, 700, 750, 800, 850, 900, 950, 1000, 1100, 1200, 1300):
        c, s = ni_capacity_of_liquid(t)
        data["capacity"][str(t)] = [c, s]
    data["solubility_vs_other_solutes"] = {
        str(t): {el: solubility_in_liquid_al(el, t) for el in ["NI"] + COMPARE}
        for t in (750, 800)}
    data["enthalpy"] = {}
    for t in (700, 750, 800):
        for w in (1.0, 2.0):
            data["enthalpy"][f"{t}C_{w}wt"] = list(dissolution_enthalpy(t, w))
    with open(CACHE, "w") as fh:
        json.dump(data, fh, indent=1)
    return data


def load():
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            return json.load(fh)
    return compute()


def report(d):
    print(f"\nAl-rich Al-Ni liquidus ({d['source']})")
    print(f"{'wt% Ni':>8} {'at% Ni':>8} {'liquidus C':>11}")
    for w, T in d["liquidus"]:
        print(f"{w:8.2f} {100 * wt_to_x(w):8.3f} {T:11.1f}")
    print(f"\nSolidus of Al-2 wt% Ni (= eutectic temperature): {d['solidus_2wt']:.1f} C")
    print("\nNi that liquid Al can hold before an aluminide forms (C_s)")
    for t, (c, s) in d["capacity"].items():
        print(f"  {t:>5} C: {c:6.2f} wt% Ni   (coexisting with {', '.join(s)})")
    if "solubility_vs_other_solutes" in d:
        print("\nHow much of each solute liquid Al holds (wt%; Ni: Dupin 2001, others: COST507)")
        for t, row in d["solubility_vs_other_solutes"].items():
            print(f"  {t} C: " + ", ".join(f"{el.title()} {w:.2f}" for el, w in row.items()))
    print("\nHeat of dissolving solid Ni into liquid Al")
    for k, (dh, q, dT) in d["enthalpy"].items():
        print(f"  {k:>10}: {dh:7.1f} kJ/mol Ni, {q / 1000:5.2f} kJ per 100 g charge,"
              f" adiabatic rise {dT:5.1f} K")


INK, INK2 = "#0b0b0b", "#52514e"          # text tokens
BLUE, YELLOW, RED = "#2a78d6", "#eda100", "#e34948"


def _ink_legend(phase_names):
    """binplot legend_generator: draw every boundary in ink; fields are labelled
    directly instead of through an eight-colour legend."""
    return [], {p: INK for p in phase_names}


def plot(d):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pycalphad import binplot
    import pycalphad.variables as v

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0),
                                   gridspec_kw={"width_ratios": [1.1, 1]})

    # Left: the full binary, computed.
    binplot(db(), ["AL", "NI", "VA"], phases(),
            {v.X("NI"): (0, 1, 0.01), v.T: (500, 2000, 10), v.P: 101325, v.N: 1},
            plot_kwargs={"ax": ax1, "tielines": False, "legend_generator": _ink_legend,
                         "tie_triangle_color": INK})
    if ax1.get_legend() is not None:
        ax1.get_legend().remove()
    for coll in ax1.collections:
        coll.set_linewidth(1.3)
    K = 273.15
    ax1.set_xlim(0, 1)
    ax1.set_ylim(500, 2000)
    yt = np.arange(300, 1800, 200)
    ax1.set_yticks(yt + K)
    ax1.set_yticklabels([str(t) for t in yt])
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_xlabel("Mole fraction Ni")
    ax1.axhline(1300 + K, color=RED, lw=1.4, ls="--")
    ax1.text(0.015, 1300 + K + 12, "induction module rating, 1300 °C", color=INK,
             ha="left", va="bottom", fontsize=8.5, transform=ax1.get_yaxis_transform())
    for x, T, lab, kw in [                      # positions in degC
        (0.10, 1450, "L", {"fontsize": 11}),
        (0.90, 1580, "L", {"fontsize": 11}),
        (0.18, 760, "L + Al$_3$Ni", {}),
        (0.12, 450, "(Al) + Al$_3$Ni", {}),
        (0.295, 1010, "L + Al$_3$Ni$_2$", {}),
        (0.383, 560, "Al$_3$Ni$_2$", {"rotation": 90}),
        (0.50, 1250, "NiAl (B2)", {}),
        (0.745, 900, "Ni$_3$Al (L1$_2$)", {"rotation": 90}),
        (0.90, 900, "(Ni)", {}),
        (0.255, 300, "Al$_3$Ni", {"ha": "left", "fontsize": 8}),
        (0.632, 400, "Al$_3$Ni$_5$", {"ha": "left", "fontsize": 8}),
    ]:
        ax1.text(x, T + K, lab, color=INK, ha=kw.pop("ha", "center"), va="center", **kw)
    xs = np.linspace(0, 1, 401)
    ws = np.array([x_to_wt(t) for t in xs])
    top = ax1.secondary_xaxis("top", functions=(lambda x: np.interp(x, xs, ws),
                                                lambda w: np.interp(w, ws, xs)))
    top.set_xticks([0, 10, 20, 30, 42, 60, 80, 100])
    top.set_xlabel("wt% Ni")
    ax1.set_title("Al–Ni, computed with pycalphad (Dupin, Ansara & Sundman 2001)",
                  fontsize=10, color=INK, pad=30)

    # Right: the Al-rich liquidus in wt% -- what a Ni addition has to clear.
    liq = np.array([[w, T] for w, T in d["liquidus"] if np.isfinite(T)])
    ax2.plot(liq[:, 0], liq[:, 1], color=BLUE, lw=2)
    ax2.text(31, 905, "liquidus", color=INK, fontsize=9, rotation=0)
    te = d["solidus_2wt"]
    ax2.axhline(te, color=INK2, lw=0.8, ls=":")
    ax2.text(44.5, te - 6, f"eutectic, {te:.0f} °C", ha="right", va="top", fontsize=8.5, color=INK2)
    ax2.axhline(660.3, color=INK2, lw=0.8, ls="--")
    ax2.text(44.5, 664, "pure Al melts, 660 °C", ha="right", va="bottom", fontsize=8.5, color=INK2)
    ax2.axvspan(0, 2.2, color=YELLOW, alpha=0.30, lw=0)
    ax2.text(2.6, 1210, "planned Ni: 1–2 wt%\n(1–2 discs of 1.1 g\nper 100 g charge)",
             ha="left", va="top", fontsize=8.5, color=INK)
    ax2.axvline(42.0, color=INK2, lw=0.8, ls=":")
    ax2.text(41.6, 1000, "Al$_3$Ni (42 wt% Ni)", rotation=90, ha="right", va="center",
             fontsize=8, color=INK2)
    ax2.axhline(1300, color=RED, lw=1.4, ls="--")
    ax2.text(44.5, 1290, "induction rating, 1300 °C", color=INK, ha="right", va="top", fontsize=8.5)
    cap750 = d["capacity"]["750"][0]
    ax2.annotate("", xy=(cap750, 750), xytext=(2.2, 750),
                 arrowprops=dict(arrowstyle="->", lw=1.1, color=INK))
    ax2.plot([cap750], [750], "o", ms=8, color=BLUE, mec="white", mew=2)
    ax2.text(2.8 + 0.5 * (cap750 - 2.2), 762, f"at 750 °C, liquid Al holds up to {cap750:.0f} wt% Ni",
             ha="center", va="bottom", fontsize=8.5, color=INK)
    ax2.set_xlim(0, 45)
    ax2.set_ylim(600, 1320)
    ax2.set_xlabel("wt% Ni")
    ax2.set_ylabel("Temperature (°C)")
    ax2.set_title("Al-rich side: a 2 wt% Ni charge is fully liquid at "
                  f"{np.interp(2.0, liq[:, 0], liq[:, 1]):.0f} °C", fontsize=10, color=INK)
    ax2.grid(alpha=0.18, color=INK2, lw=0.6)
    for a in (ax1, ax2):
        for sp in ("right",):
            a.spines[sp].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG, dpi=150)
    print("wrote", FIG)


if __name__ == "__main__":
    data = compute() if "--recompute" in sys.argv or not os.path.exists(CACHE) else load()
    report(data)
    if "--plot" in sys.argv:
        plot(data)
