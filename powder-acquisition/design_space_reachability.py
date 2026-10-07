"""Minimum feedstock set for full access to the alloy design space (issue #161).

Question (2026-10-07): whatever we do with master alloys, can every composition in the
optimization campaign's search space still be made in a 100 g crucible charge? What is the
minimum set of feedstocks, and for each master alloy the minimum non-Al weight fraction?

Framing
-------
The search space is a box in solute wt.% (one [L, U] per non-Al element) sliced by the
compositional constraint sum(x) <= S (aluminium is the balance, >= 100 - S). Mixing
feedstocks is a convex combination, so the set of compositions a feedstock set can make is
the convex hull of the feedstock composition vectors. Full access means the design polytope
P lies inside that hull.

With the natural architecture -- pure Al plus one source per element, the source for element
i carrying a non-Al mass fraction y_i (y_i = 1 for an elemental powder, 0.02 for Al-2Sc,
...) -- the reachable set is exactly

    { x >= 0 :  sum_i x_i / y_i  <= 1 }           (x as mass fractions)

because delivering x_i grams of element i per gram of batch takes x_i / y_i grams of its
source, and the sources plus pure Al must sum to one. So master alloys do not change the
*shape* of the problem: they replace the compositional constraint sum(x) <= S by a second,
tilted half-space with weights 1/y_i. P is fully reachable iff

    V(y) := max_{x in P} sum_i x_i / y_i  <= 1,

a linear program over a box with a single budget constraint, which the continuous-knapsack
greedy solves exactly: start every element at its lower bound, then hand the remaining
solute budget S - sum(L) to elements in decreasing order of 1/y_i (least concentrated source
first), each up to its upper bound. The maximizing vertex is the worst-case recipe.

Consequences (all exact):
  * The minimum number of feedstocks is n + 1 (n solutes + Al): P is n-dimensional, so its
    hull needs at least n + 1 affinely independent points; and if 0 is in every [L_i, U_i]
    then pure Al itself is one of them, because no mixture of solute-bearing feedstocks can
    have zero solute.
  * One source per element is enough provided V(y) <= 1. Multi-element masters never reduce
    the count below n + 1 (each element must still be varied independently); they can only
    *add* reach as an extra feedstock if they are more concentrated than the binaries.
  * The per-element floor on y_i (necessary, all other sources elemental) is
        y_i >= U_i / (1 - O_i),   O_i = the most solute the other elements can carry alongside
    U_i inside the budget. The joint condition couples the elements: every master alloy
    spends batch mass on its own aluminium, and the worst vertex stacks the least
    concentrated sources together.

Edit DESIGN_SPACE / S_TOTAL / SCENARIOS and re-run:

    python design_space_reachability.py            # tables to stdout
    python design_space_reachability.py --json out.json

Only numpy is required. If scipy is importable the LP result is cross-checked with
scipy.optimize.linprog.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys

import numpy as np

# --------------------------------------------------------------------------------------
# Design space: wt.% bounds per non-Al element.
# Provenance: the 20-run purchase model families (purchase_quantity_model.py), the erbium
# bounds analysis (erbium-bounds-and-lot-size.md, [0, 3]), and the melt-window docs.
# NONE of these is ratified -- they are the numbers on record. Edit freely.
# --------------------------------------------------------------------------------------
DESIGN_SPACE = {
    # element: (lower wt.%, upper wt.%)
    "Mn": (0.0, 5.0),
    "Cr": (0.0, 2.0),
    "Zr": (0.0, 2.0),
    "Mg": (0.0, 6.0),
    "Si": (0.0, 12.0),
    "Cu": (0.0, 4.0),
    "Ti": (0.0, 0.5),
    "Fe": (0.0, 1.0),
    "Ni": (0.0, 2.0),
    "Ce": (0.0, 10.0),
    "Sc": (0.0, 0.8),
    "Li": (0.0, 2.0),
    "Er": (0.0, 3.0),
    "Zn": (0.0, 8.0),
    "Sn": (0.0, 1.0),
}
S_TOTAL = 20.0  # wt.% maximum total solute (Al >= 80 wt.%)
S_SWEEP = (10.0, 15.0, 20.0, 25.0, 30.0)

# --------------------------------------------------------------------------------------
# Feedstock scenarios: element -> (label, y = non-Al mass fraction of its source).
# Elements not listed are elemental (y = 1).
# --------------------------------------------------------------------------------------
SCENARIOS = {
    "A. all elemental": {},
    "B. 2026-08 shopping chart": {
        "Zr": ("Al-10Zr", 0.10), "Ce": ("Al-20Ce", 0.20), "Sc": ("Al-2Sc", 0.02),
        "Er": ("Al-10Er", 0.10), "Li": ("Al-10Li", 0.10),
    },
    "C. every reactive element as a commercial master": {
        "Li": ("Al-5Li", 0.05), "Sc": ("Al-2Sc", 0.02), "Zr": ("Al-10Zr", 0.10),
        "Er": ("Al-10Er", 0.10), "Ti": ("Al-10Ti", 0.10), "Ce": ("Al-20Ce", 0.20),
        "Mg": ("Al-50Mg", 0.50),
    },
    "D. 2026-09 plan (Thermo/ESPI elemental RE, ESPI Al-Zr pieces)": {
        "Li": ("Al-5Li", 0.05), "Zr": ("Al-10Zr pieces (ESPI Knd2760)", 0.10),
        "Ti": ("Al-10Ti pieces (ESPI Knc6829)", 0.10),
        # Sc chips, Er powder, Ce ingot, Mg pieces are elemental (y = 1)
    },
    "F. plan D but Sc as Al-2Sc": {
        "Li": ("Al-5Li", 0.05), "Zr": ("Al-10Zr pieces", 0.10), "Ti": ("Al-10Ti pieces", 0.10),
        "Sc": ("Al-2Sc", 0.02),
    },
    "G. all-master but Al-10Li": {
        "Li": ("Al-10Li", 0.10), "Sc": ("Al-2Sc", 0.02), "Zr": ("Al-10Zr pieces", 0.10),
        "Ti": ("Al-10Ti pieces", 0.10), "Er": ("Al-10Er", 0.10), "Ce": ("Al-20Ce", 0.20),
    },
    "E. recommended (see report)": {
        "Li": ("Al-10Li (or Al-5Li if Sc/Zr/Ce are elemental)", 0.10),
        "Zr": ("Al-Zr50 pieces (ESPI Knd2756), crushed", 0.50),
        "Ti": ("Al-10Ti pieces", 0.10),
        # Sc chips, Er powder, Ce pieces, Mg pieces elemental
    },
}

# Impurity model (ppm by mass of 'tramp' delivered to the alloy). Used only for the
# impurity-limited floors; edit if a CoA says otherwise.
IMPURITY = {
    "al_base_ppm": 100.0,          # 4N aluminium cup/shot
    "master_base_ppm_commercial": 3000.0,   # masters cast on 99.7 % P1020-type Al
    "master_base_ppm_4N": 100.0,            # masters cast in-house on 4N Al
    "solute_ppm": 1000.0,          # 3N elemental powders / solute part of a master
    "tolerance_ppm": 2000.0,       # e.g. Fe <= 0.20 wt.% (Scalmalloy datasheet)
}

MC_SAMPLES = 2_000_000
RNG_SEED = 161


# --------------------------------------------------------------------------------------
# Exact pieces
# --------------------------------------------------------------------------------------
def _arrays(space):
    els = list(space)
    L = np.array([space[e][0] for e in els], float) / 100.0
    U = np.array([space[e][1] for e in els], float) / 100.0
    return els, L, U


def worst_vertex(L, U, S, z):
    """max z.x over {L <= x <= U, sum x <= S}. Exact (continuous knapsack)."""
    x = L.copy()
    budget = S - L.sum()
    if budget < -1e-12:
        raise ValueError("lower bounds alone exceed the total-solute cap")
    for i in np.argsort(-z, kind="stable"):
        if budget <= 0:
            break
        if z[i] <= 0:
            continue
        d = min(U[i] - L[i], budget)
        x[i] += d
        budget -= d
    return x, float(z @ x)


def y_vector(els, scenario):
    return np.array([scenario[e][1] if e in scenario else 1.0 for e in els], float)


def check_scenario(els, L, U, S, y):
    z = 1.0 / y
    x, V = worst_vertex(L, U, S, z)
    return {
        "V": V,
        "feasible": V <= 1 + 1e-9,
        "worst_vertex_wtpct": {e: round(100 * v, 3) for e, v in zip(els, x) if v > 0},
        "source_grams_per_100g": {e: round(100 * v / yy, 2) for e, v, yy in zip(els, x, y) if v > 0},
        "pure_Al_grams": round(100 * (1 - V), 2),
    }


def floor_y(els, L, U, S, i):
    """Necessary y_i (all other sources elemental). Closed form."""
    others = [j for j in range(len(els)) if j != i]
    Lo = L[others].sum()
    room = S - U[i] - Lo
    if room < 0:
        return None  # U_i alone cannot coexist with the other lower bounds under S
    O = Lo + min(room, (U[others] - L[others]).sum())
    return U[i] / (1 - O)


def min_y_given_others(els, L, U, S, y, i, lo=1e-4):
    """Smallest y_i keeping V <= 1 with the other y fixed; None if impossible even at y_i=1."""
    y = y.copy()
    y[i] = 1.0
    if check_scenario(els, L, U, S, y)["V"] > 1 + 1e-9:
        return None
    a, b = lo, 1.0
    for _ in range(60):
        m = math.sqrt(a * b)
        y[i] = m
        if check_scenario(els, L, U, S, y)["V"] <= 1:
            b = m
        else:
            a = m
    return b


def min_uniform_scale(els, L, U, S, y0, master_idx):
    """Smallest lambda such that y_i = min(1, lambda*y0_i) on the masters gives V <= 1."""
    def V_of(lam):
        y = y0.copy()
        for i in master_idx:
            y[i] = min(1.0, lam * y0[i])
        return check_scenario(els, L, U, S, y)["V"]
    if V_of(1.0) <= 1:
        return 1.0
    if V_of(1e9) > 1 + 1e-9:
        return None
    a, b = 1.0, 1e9
    for _ in range(80):
        m = math.sqrt(a * b)
        if V_of(m) <= 1:
            b = m
        else:
            a = m
    return b


def box_slice_volume_fraction(U, S):
    """Exact Vol{x in [0,U] : sum x <= S} / prod(U) by inclusion-exclusion.
    (Lower bounds assumed zero; shift the box first otherwise.)"""
    n = len(U)
    tot = 0.0
    for k in range(n + 1):
        for J in itertools.combinations(range(n), k):
            s = S - sum(U[j] for j in J)
            if s > 0:
                tot += (-1) ** k * s ** n
    return tot / math.factorial(n) / float(np.prod(U))


def reachable_fraction_mc(L, U, S, y, n=MC_SAMPLES, seed=RNG_SEED):
    """Monte-Carlo share of P (uniform in composition) that the scenario can make."""
    rng = np.random.default_rng(seed)
    z = 1.0 / y
    inP = 0
    ok = 0
    chunk = 250_000
    done = 0
    while done < n:
        m = min(chunk, n - done)
        x = L + (U - L) * rng.random((m, len(U)))
        mask = x.sum(axis=1) <= S
        inP += int(mask.sum())
        ok += int(((x[mask] * z).sum(axis=1) <= 1).sum())
        done += m
    frac = ok / inP if inP else float("nan")
    se = math.sqrt(frac * (1 - frac) / inP) if inP else float("nan")
    return frac, se, inP


def impurity_worst_case(els, L, U, S, y, master_base_ppm):
    """Worst-case tramp ppm in the alloy: 4N Al balance, masters on the given base."""
    imp_al = IMPURITY["al_base_ppm"]
    imp_sol = IMPURITY["solute_ppm"]
    w = np.empty(len(els))
    for i, yy in enumerate(y):
        imp_source = yy * imp_sol + (1 - yy) * master_base_ppm if yy < 1 else imp_sol
        w[i] = (imp_source - imp_al) / yy
    x, extra = worst_vertex(L, U, S, w)
    return imp_al + extra, {e: round(100 * v, 3) for e, v in zip(els, x) if v > 0}


def impurity_floor_y(els, L, U, S, i, master_base_ppm, tol=None):
    """Smallest y_i such that element i alone at U_i (others ideal) stays within tolerance."""
    tol = IMPURITY["tolerance_ppm"] if tol is None else tol
    imp_al, imp_sol = IMPURITY["al_base_ppm"], IMPURITY["solute_ppm"]
    budget = tol - imp_al - U[i] * (imp_sol - imp_al)
    if budget <= 0:
        return None
    # U_i/y (1-y)(base - al) <= budget  ->  y >= U_i*d / (budget + U_i*d)
    d = master_base_ppm - imp_al
    if d <= 0:
        return 0.0
    return U[i] * d / (budget + U[i] * d)


def scipy_crosscheck(L, U, S, z):
    try:
        from scipy.optimize import linprog
    except Exception:
        return None
    res = linprog(-z, A_ub=np.ones((1, len(z))), b_ub=[S], bounds=list(zip(L, U)), method="highs")
    return -res.fun if res.success else None


# --------------------------------------------------------------------------------------
def run(space=DESIGN_SPACE, S=S_TOTAL, scenarios=SCENARIOS, mc=True, verbose=True):
    els, L, U = _arrays(space)
    out = {"design_space_wtpct": space, "S_total_wtpct": S, "elements": els}
    P = lambda *a, **k: print(*a, **k) if verbose else None
    S_pct, S = S, S / 100.0  # everything below works in mass fractions

    P(f"Design space: {len(els)} solutes, box sum of uppers = {100*U.sum():.1f} wt.%, "
      f"total-solute cap S = {S_pct:.1f} wt.% (Al >= {100-S_pct:.0f} wt.%)")
    vf = box_slice_volume_fraction(U, S)
    out["box_fraction_inside_cap"] = vf
    P(f"Share of the raw hypercube that survives the cap (exact): {100*vf:.3g} %")
    P("Share for other caps: " + ", ".join(
        f"S={s:g}: {100*box_slice_volume_fraction(U, s/100):.3g} %" for s in S_SWEEP))

    # --- per-element floors (necessary conditions) -----------------------------------
    P("\n1. Necessary floor on each source's non-Al fraction y_i (all other sources elemental)")
    P(f"{'el':<4}{'U wt.%':>8}{'y_floor %':>11}  {'worst-case companions'}")
    floors = {}
    for i, e in enumerate(els):
        f = floor_y(els, L, U, S, i)
        floors[e] = f
        P(f"{e:<4}{100*U[i]:>8.2f}{(100*f if f else float('nan')):>11.2f}")
    out["y_floor_percent"] = {e: (100 * f if f else None) for e, f in floors.items()}

    # --- scenarios ---------------------------------------------------------------------
    P("\n2. Scenarios: V = worst-case (source grams / 100 g batch); feasible iff V <= 1")
    out["scenarios"] = {}
    for name, sc in scenarios.items():
        y = y_vector(els, sc)
        r = check_scenario(els, L, U, S, y)
        z = 1.0 / y
        lp = scipy_crosscheck(L, U, S, z)
        r["scipy_V"] = lp
        if mc:
            frac, se, nP = reachable_fraction_mc(L, U, S, y)
            r["reachable_fraction_mc"] = frac
            r["reachable_fraction_se"] = se
        r["sources"] = {e: sc[e][0] for e in sc}
        # contextual minima: min y_i given the other sources as in the scenario
        ctx = {}
        for i, e in enumerate(els):
            if e in sc:
                ctx[e] = min_y_given_others(els, L, U, S, y, i)
        r["min_y_given_others_percent"] = {e: (100 * v if v else None) for e, v in ctx.items()}
        midx = [i for i, e in enumerate(els) if e in sc]
        lam = min_uniform_scale(els, L, U, S, y, midx) if midx else 1.0
        r["uniform_concentration_factor_needed"] = lam
        # impurity
        for tag, base in (("commercial", IMPURITY["master_base_ppm_commercial"]),
                          ("4N", IMPURITY["master_base_ppm_4N"])):
            ppm, vtx = impurity_worst_case(els, L, U, S, y, base)
            r[f"impurity_worst_ppm_masters_on_{tag}_Al"] = ppm
        out["scenarios"][name] = r

        P(f"\n{name}")
        P("   sources: " + (", ".join(f"{e}: {sc[e][0]} (y={100*sc[e][1]:g} %)" for e in sc) or "all elemental"))
        P(f"   V = {r['V']:.3f}  -> {'FEASIBLE' if r['feasible'] else 'NOT feasible'}"
          + (f"   (scipy LP: {lp:.3f})" if lp is not None else ""))
        if mc:
            P(f"   reachable share of the design space: {100*frac:.2f} % (+/- {100*se:.2f})")
        P("   worst-case recipe (wt.%): " + ", ".join(f"{e} {v:g}" for e, v in r["worst_vertex_wtpct"].items()))
        P("   source grams per 100 g: " + ", ".join(f"{e} {v:g}" for e, v in r["source_grams_per_100g"].items())
          + f"  | pure Al {r['pure_Al_grams']:g} g")
        if ctx:
            P("   min y_i with the other sources as listed: " + ", ".join(
                f"{e} {100*v:.2f} %" if v else f"{e} impossible (others alone exceed 100 g)"
                for e, v in ctx.items()))
        if lam is not None and lam != 1.0:
            P(f"   every master would need to be {lam:.2f}x more concentrated (uniformly) to reach the whole space")
        P(f"   worst-case tramp: {r['impurity_worst_ppm_masters_on_commercial_Al']:.0f} ppm with masters on 99.7 % Al, "
          f"{r['impurity_worst_ppm_masters_on_4N_Al']:.0f} ppm on 4N Al (tolerance {IMPURITY['tolerance_ppm']:.0f})")

    # --- impurity-limited floors -----------------------------------------------------------
    P("\n3. Impurity-limited floor on y_i if the master is cast on 99.7 % Al "
      f"(tolerance {IMPURITY['tolerance_ppm']:.0f} ppm, 4N Al balance, 3N solute)")
    imp_floor = {}
    for i, e in enumerate(els):
        f = impurity_floor_y(els, L, U, S, i, IMPURITY["master_base_ppm_commercial"])
        imp_floor[e] = f
    P("   " + ", ".join(f"{e} {100*f:.1f} %" if f is not None else f"{e} n/a" for e, f in imp_floor.items()))
    out["impurity_floor_percent_masters_on_commercial_Al"] = {e: (100 * f if f is not None else None) for e, f in imp_floor.items()}

    # --- sweep over S ---------------------------------------------------------------------
    P("\n4. Feasibility of each scenario versus the total-solute cap S")
    out["S_sweep"] = {}
    hdr = f"{'S wt.%':>7} " + " ".join(f"{n.split('.')[0]:>6}" for n in scenarios)
    P(hdr)
    for s in S_SWEEP:
        row = {}
        for name, sc in scenarios.items():
            y = y_vector(els, sc)
            row[name] = check_scenario(els, L, U, s / 100.0, y)["V"]
        out["S_sweep"][s] = row
        P(f"{s:>7.0f} " + " ".join(f"{row[n]:>6.2f}" for n in scenarios))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write results here")
    ap.add_argument("--no-mc", action="store_true", help="skip the Monte-Carlo reachable share")
    ap.add_argument("--S", type=float, default=S_TOTAL, help="total-solute cap, wt.%")
    a = ap.parse_args()
    out = run(S=a.S, mc=not a.no_mc)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f, indent=2, default=float)


if __name__ == "__main__":
    main()
