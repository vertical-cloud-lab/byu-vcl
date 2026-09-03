"""Erbium bounds and lot-sizing for the atomizer campaign (issue #161).

Answers two coupled questions:

  forward  - given an Er upper bound and a number of Er-bearing runs,
             how many grams of Er must be on the shelf?
  inverse  - given a lot size already on the shelf, what Er upper bound
             can the optimization campaign actually afford to search?

The inverse direction is the one that matters at purchase time: the lot you
buy sets the ceiling of the design space, so buying short quietly truncates
the search box below the composition the published literature converged on.

    python erbium_lot_sizing.py
"""

M = {"Al": 26.9815, "Er": 167.259, "Sc": 44.9559, "Zr": 91.224, "Ni": 58.693}

BATCH_G = 100.0
CONTINGENCY = 1.25  # spillage, weighing losses, one re-run (same factor as purchase_quantity_model.py)

# Er $/g, delivered lot sizes seen in the 2026-08/09 market
PRICES = {
    "ESPI 25 g, 3N, -40 mesh": (25.0, 800.00),
    "Thermo/Alfa 044169.14, 25 g, 99.9% (REO)": (25.0, 770.65),
    "Thermo/Alfa 044169.06, 5 g, 99.9% (REO)": (5.0, 218.65),
}

# Composition anchors, at.% Er -> context
ANCHORS = [
    (0.046, "max equilibrium solid solubility in Al at 640 C (van Dalen 2009)"),
    (0.4, "Al-0.4Er-1Zr-1.33Ni optimum, ultrasonically atomized (npj Adv. Manuf. 2025)"),
    (1.019, "Al-Al3Er eutectic, 655 C"),
    (2.0, "upper edge of the published ML design box for Er"),
]


def at_to_wt(er_at_pct, others=None):
    """at.% Er (with optional other solutes in at.%) -> wt.% Er."""
    d = dict(others or {})
    d["Er"] = er_at_pct
    d["Al"] = 100.0 - sum(d.values())
    mass = {k: v * M[k] for k, v in d.items()}
    return 100.0 * mass["Er"] / sum(mass.values())


def grams_needed(ceiling_wt, n_runs, sampling="worst"):
    """Er grams to buy. 'worst' = every run at the ceiling;
    'mean' = uniform sampling over [0, ceiling] (BO initial design)."""
    per_run = ceiling_wt if sampling == "worst" else ceiling_wt / 2.0
    return n_runs * BATCH_G * per_run / 100.0 * CONTINGENCY


def affordable_ceiling(lot_g, n_runs, sampling="worst"):
    """Inverse: the Er upper bound a given lot supports."""
    base = lot_g / (n_runs * BATCH_G / 100.0 * CONTINGENCY)
    return base if sampling == "worst" else 2.0 * base


def main():
    print("=" * 74)
    print("1. Composition anchors (binary Al-Er unless noted)")
    print("=" * 74)
    print(f"{'at.% Er':>9}{'wt.% Er':>10}  context")
    for at_pct, note in ANCHORS:
        print(f"{at_pct:>9.3f}{at_to_wt(at_pct):>10.2f}  {note}")
    print(f"{0.4:>9.3f}{at_to_wt(0.4, {'Zr': 1.0, 'Ni': 1.33}):>10.2f}  "
          "  ^ same point recomputed with Zr+Ni present (paper reports 2.33)")

    print()
    print("=" * 74)
    print("2. Forward: Er grams to buy (incl. 1.25x contingency)")
    print("=" * 74)
    ceilings = [0.5, 1.0, 2.33, 3.0, 6.0]
    run_counts = [4, 8, 20]
    print(f"{'ceiling wt.%':>13}" + "".join(f"{n:>7} runs" for n in run_counts)
          + "   (worst case | BO-mean)")
    for c in ceilings:
        row = f"{c:>13.2f}"
        for n in run_counts:
            row += f"{grams_needed(c, n):>6.1f}/{grams_needed(c, n, 'mean'):<5.1f}"
        print(row)

    print()
    print("=" * 74)
    print("3. Inverse: Er ceiling (wt.%) a lot size can afford")
    print("=" * 74)
    print(f"{'lot':>8}" + "".join(f"{n:>7} runs" for n in run_counts)
          + "   (worst case | BO-mean)")
    for lot in (5.0, 10.0, 25.0):
        row = f"{lot:>6.0f} g"
        for n in run_counts:
            row += f"{affordable_ceiling(lot, n):>6.2f}/{affordable_ceiling(lot, n, 'mean'):<5.2f}"
        print(row)

    print()
    print("=" * 74)
    print("4. Price per lot and per run")
    print("=" * 74)
    print(f"{'lot':<45}{'$/g':>8}{'$/run @1.5 wt.%':>17}")
    for name, (grams, price) in PRICES.items():
        per_g = price / grams
        print(f"{name:<45}{per_g:>8.2f}{per_g * 1.5:>17.2f}")
    sc_per_g = 5875.0 / 25.0
    print(f"{'(reference) ESPI Sc 25 g elemental':<45}{sc_per_g:>8.2f}{sc_per_g * 0.4:>17.2f}"
          "   <- 0.4 wt.% Sc")

    print()
    print("=" * 74)
    print("5. Master-alloy mass ceiling check (why elemental Er still matters)")
    print("=" * 74)
    targets = {"Zr": (3.19, "Al-10Zr", 0.10), "Er": (2.33, "Al-10Er", 0.10),
               "Sc": (0.80, "Al-2Sc", 0.02)}
    total = 0.0
    for el, (wt, label, frac) in targets.items():
        m = BATCH_G * wt / 100.0 / frac
        total += m
        print(f"{el:<3} {wt:>5.2f} wt.%  via {label:<9} -> {m:>6.1f} g of master per 100 g batch")
    print(f"{'':<3} {'':>5}          {'total':<9} -> {total:>6.1f} g of a {BATCH_G:.0f} g batch"
          f"  ({100 * total / BATCH_G:.0f}% of the charge)")


if __name__ == "__main__":
    main()
