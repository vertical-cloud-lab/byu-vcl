"""Numbers behind the runs plan: repeat counts, the spread's powder masses, MIDI batch count.

Run with `python plan_numbers.py`. It prints the tables quoted in README.md and writes
plan_numbers.json next to this file. Needs numpy and scipy only.

Inputs that come from elsewhere, with their sources:
- Cup powder capacities (as-made 8.82 g, thin 15.94 g) and 6063 per cup: PR #232,
  atomizer-charge/composition_spread.json at e639fbd.
- Alloy spec limits (wt%): Aluminum Association, as used in that same file.
- Crucible fits four 3/4 in cups easily and five if pushed to the wall: PR #232, 323adba.
- MIDI full build cylinder about 440 g, 55 mm build-reduction kit about 30 g: issue #77.
"""

import json
import math
from pathlib import Path

from scipy import stats

CHARGE_G = 250.0  # proposed fixed charge mass for blocks A, B and C
SPREAD_WT_PCT = [0.0, 7.5, 15.0, 22.5, 30.0]  # 4047 powder in the charge, PR #232
CUP_POWDER_FULL_G = {"as_made": 8.82, "thin": 15.94}
CUP_6063_G = {"as_made": 38.71, "thin": 26.75}
MAX_CUPS_EASY, MAX_CUPS_TIGHT = 4, 5
SPEC = {  # wt%, (min, max); 4047 Mg and 6063 Fe minimums taken as 0
    "6063": {"Si": (0.20, 0.60), "Mg": (0.45, 0.90)},
    "4047": {"Si": (11.0, 13.0), "Mg": (0.0, 0.10)},
}
MIDI_G = {"full_cylinder": 440.0, "55mm_kit": 30.0}


def sigma_ci(n, conf=0.95):
    """95 % CI on the true SD as a multiple of the sample SD, from n runs (chi-square)."""
    df = n - 1
    lo = math.sqrt(df / stats.chi2.ppf(1 - (1 - conf) / 2, df))
    hi = math.sqrt(df / stats.chi2.ppf((1 - conf) / 2, df))
    return lo, hi


def runs_per_arm(d, power=0.80, alpha=0.05):
    """Smallest n per arm for a two-sided two-sample t-test to detect a d-sigma difference."""
    for n in range(2, 200):
        df = 2 * n - 2
        t_crit = stats.t.ppf(1 - alpha / 2, df)
        nc = d * math.sqrt(n / 2)
        p = stats.nct.sf(t_crit, df, nc) + stats.nct.cdf(-t_crit, df, nc)
        if p >= power:
            return n
    return None


def spread_point(wt_pct, charge_g=CHARGE_G):
    """Powder mass, cheapest cup layout and spec-limit composition for one spread point."""
    x = wt_pct / 100
    powder_g = x * charge_g
    comp = {}
    for el in ("Si", "Mg"):
        lo = (1 - x) * SPEC["6063"][el][0] + x * SPEC["4047"][el][0]
        hi = (1 - x) * SPEC["6063"][el][1] + x * SPEC["4047"][el][1]
        comp[el] = [round(lo, 2), round(hi, 2)]
    layout = None
    if powder_g > 0:
        # Prefer a layout that fits easily, then as-made cups (no new machining) over thin.
        options = [
            (max_cups, cup)
            for max_cups in (MAX_CUPS_EASY, MAX_CUPS_TIGHT)
            for cup in ("as_made", "thin")
        ]
        for max_cups, cup in options:
            n = math.ceil(powder_g / CUP_POWDER_FULL_G[cup])
            plain_g = charge_g - powder_g - n * CUP_6063_G[cup]
            if n <= max_cups and plain_g >= 0:
                layout = {
                    "cup": cup,
                    "n_cups": n,
                    "fill_frac": round(powder_g / (n * CUP_POWDER_FULL_G[cup]), 2),
                    "fits": "easily" if n <= MAX_CUPS_EASY else "only if pushed to the wall",
                    "plain_6063_rod_g": round(plain_g, 1),
                }
                break
    return {"powder_wt_pct": wt_pct, "powder_g": round(powder_g, 2), "layout": layout, **comp}


def midi_runs(in_range_yield, target_g, charge_g=CHARGE_G):
    return math.ceil(target_g / (charge_g * in_range_yield))


# Block B run order and its 4047 wt% (README, "Runs and what each is meant to show")
BLOCK_B = {"B1": 22.5, "B2": 7.5, "B3": 30.0, "B4": 0.0, "B5": 15.0, "B6": 30.0, "B7": 7.5}
BLOCK_A_MAX_RUNS = 8
SPARE_RUNS = 2  # charges lost to runs that fail the gate
# Each cup starts as 3/4 in bar faced to 2.75 in from a piece cut 1/4 in long (SOP, LATHE).
BAR_PER_CUP_G = math.pi * (0.75 / 2) ** 2 * 3.0 * 2.54**3 * 2.69


def bar_6063_budget():
    """6063 bar for Blocks A and B: charges, plus what boring the cups turns into chips."""
    block_a = BLOCK_A_MAX_RUNS * CHARGE_G
    block_b, chips, n_cups = 0.0, 0.0, 0
    for wt in BLOCK_B.values():
        p = spread_point(wt)
        block_b += CHARGE_G - p["powder_g"]
        if p["layout"]:
            n = p["layout"]["n_cups"]
            n_cups += n
            chips += n * (BAR_PER_CUP_G - CUP_6063_G[p["layout"]["cup"]])
    spare = SPARE_RUNS * CHARGE_G
    return {
        "block_a_g": round(block_a),
        "block_b_g": round(block_b),
        "cups_in_block_b": n_cups,
        "chips_g": round(chips),
        "spare_runs_g": round(spare),
        "total_g": round(block_a + block_b + chips + spare),
    }


def main():
    out = {"charge_g": CHARGE_G}

    out["sigma_ci"] = {n: [round(v, 2) for v in sigma_ci(n)] for n in (3, 4, 5, 6, 8, 10)}
    print("95 % CI on the run-to-run SD, as a multiple of the measured SD")
    for n, (lo, hi) in out["sigma_ci"].items():
        print(f"  n = {n:2d}: {lo:.2f}-{hi:.2f} x s")

    out["runs_per_arm"] = {d: runs_per_arm(d) for d in (1, 1.5, 2, 3, 4)}
    print("\nRuns per setting to detect a difference of d sigma (80 % power, alpha 0.05)")
    for d, n in out["runs_per_arm"].items():
        print(f"  d = {d}: {n}")

    out["spread"] = [spread_point(w) for w in SPREAD_WT_PCT]
    print(f"\nComposition spread at a fixed {CHARGE_G:.0f} g charge")
    for p in out["spread"]:
        lay = p["layout"]
        how = (
            f"{lay['n_cups']} {lay['cup']} cups at {lay['fill_frac']:.0%} full "
            f"({lay['fits']}), + {lay['plain_6063_rod_g']} g plain rod"
            if lay
            else "plain 6063 rod only"
        )
        print(
            f"  {p['powder_wt_pct']:4.1f} wt%: {p['powder_g']:5.1f} g 4047 powder; "
            f"Si {p['Si'][0]}-{p['Si'][1]}, Mg {p['Mg'][0]}-{p['Mg'][1]} wt%; {how}"
        )
    one_pass = sum(p["powder_g"] for p in out["spread"])
    with_reps = one_pass + out["spread"][1]["powder_g"] + out["spread"][-1]["powder_g"]
    out["spread_4047_powder_g"] = {"one_pass": one_pass, "endpoints_repeated": with_reps}
    print(f"  4047 powder: {one_pass:.0f} g for one run per point, {with_reps:.0f} g with both endpoints repeated")

    out["bar_6063"] = bar_6063_budget()
    b = out["bar_6063"]
    print(
        f"\n6063 bar for Blocks A (up to {BLOCK_A_MAX_RUNS} runs) and B: {b['block_a_g']} g + {b['block_b_g']} g of charge, "
        f"{b['chips_g']} g of chips from {b['cups_in_block_b']} cups, {b['spare_runs_g']} g for {SPARE_RUNS} failed runs "
        f"= {b['total_g']} g"
    )

    yields = (0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
    out["midi_runs"] = {
        name: {y: midi_runs(y, g) for y in yields} for name, g in MIDI_G.items()
    }
    print(f"\nRuns at {CHARGE_G:.0f} g needed for MIDI powder, by in-range yield (sieved powder / charge)")
    print("  yield:        " + "  ".join(f"{y:>4.0%}" for y in yields))
    for name, row in out["midi_runs"].items():
        print(f"  {name:13s} " + "  ".join(f"{row[y]:>4d}" for y in yields))
    top = out["spread"][-1]["powder_g"]
    out["midi_4047_powder_g_per_run_at_top_point"] = top
    print(f"  Each run at the {SPREAD_WT_PCT[-1]:.0f} wt% point uses {top:.0f} g of 4047 powder.")

    Path(__file__).with_name("plan_numbers.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
