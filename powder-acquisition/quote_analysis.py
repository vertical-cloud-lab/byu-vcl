"""Quote analysis for issue #161 — feedstock impurity budget and particle-size screening.

Two independent questions are answered here, both from the quotes received on 2026-08-26
(ESPI Metals, Thermo Fisher quote #M6449, Atlantic Equipment Engineers):

1. `impurity_budget()` — is the *quoted purity* good enough? A feedstock's purity only
   matters in proportion to how much of it ends up in the alloy, so the figure of merit is
   `max_wt_frac x (1 - purity)`, i.e. the ppm of tramp element each feedstock contributes to
   the finished alloy at its worst-case (maximum) addition level.

2. `size_screen()` — is the *quoted particle size* workable? Converts every quoted mesh cut
   to microns, compares against the 150-300 um auger target, and reports the cohesion index
   (van der Waals / gravity scales as 1/d^2, normalised to the 250 um target) plus whether
   sieving on receipt can rescue the lot.

Run: python powder-acquisition/quote_analysis.py
"""

from __future__ import annotations

# US standard sieve series: mesh -> aperture in micrometres
MESH_UM = {
    20: 850, 30: 600, 40: 425, 50: 300, 60: 250, 70: 212, 80: 180,
    100: 150, 120: 125, 140: 106, 170: 90, 200: 75, 230: 63, 270: 53, 325: 45,
}

# Worst-case addition level of each element across the six alloy families in
# purchase-quantity-model.md (wt.%). Al is the balance of the leanest family.
MAX_WT_PCT = {
    "Al": 90.5, "Si": 12.0, "Ce": 10.0, "Zn": 8.0, "Mg": 6.0, "Mn": 5.0,
    "Cu": 4.0, "Cr": 2.0, "Zr": 2.0, "Ni": 2.0, "Li": 2.0, "Fe": 1.0,
    "Sn": 1.0, "Er": 1.0, "Sc": 0.8, "Ti": 0.5,
}

# (element, supplier, quoted purity, note) for every line actually quoted.
QUOTED_PURITY = [
    ("Al", "AEE AL-111",          99.7,  "-50+100 mesh, atomized"),
    ("Al", "AEE AL-130 (alt)",    99.99, "1/4-1/2 in pellets"),
    ("Mn", "ESPI",                99.9,  "no certificate of analysis with this lot"),
    ("Cr", "ESPI",                99.9,  "3N+"),
    ("Cr", "Fisher AA3566818",    99.97, ""),
    ("Zn", "ESPI",                99.99, "4N"),
    ("Zn", "Fisher AA3969422",    99.9,  "46-day lead"),
    ("Sn", "ESPI 5N",             99.999, "-40 mesh"),
    ("Sn", "ESPI 3N",             99.9,  "-325 mesh"),
    ("Sn", "Fisher AA0094122",    99.85, ""),
    ("Mg", "ESPI pieces",         99.9,  "1/2 in and down - not powder"),
    ("Mg", "Fisher AA0086930",    99.8,  "NO SOURCE"),
    ("Si", "Fisher AA0031122",    99.9,  ""),
    ("Fe", "Fisher AA4735530",    99.9,  ""),
    ("Ni", "Fisher 010579.22",    99.7,  ""),
    ("Cu", "Fisher AA4262322",    99.9,  "spherical"),
    ("Ti", "ESPI",                99.7,  "2N7, -325 mesh"),
    ("Ti", "Fisher AA4310522",    99.5,  "NO SOURCE"),
    ("Sc", "ESPI",                99.9,  "elemental, $235/g"),
    ("Er", "ESPI",                99.9,  "elemental, $32/g"),
]

# Reference impurity limits for context (wt.% -> ppm of finished alloy).
REFERENCES = {
    "Scalmalloy Fe limit (0.068 wt.%)": 680,
    "AlSi10Mg Fe limit (0.25 wt.%)": 2500,
    "1199 Al total impurity (0.01 wt.%)": 100,
}

# Quoted particle-size cuts: (element, supplier, top mesh or None, bottom mesh or None)
# None on top = no upper screen; None on bottom = no lower screen (fines present).
QUOTED_CUTS = [
    ("Al", "AEE AL-111",        50, 100),
    ("Mn", "ESPI",              100, None),
    ("Cr", "ESPI",              325, None),
    ("Cr", "Fisher",            100, 325),
    ("Zn", "ESPI",              100, None),
    ("Zn", "Fisher",            140, 325),
    ("Sn", "ESPI 5N",           40, None),
    ("Sn", "ESPI 3N",           325, None),
    ("Sn", "Fisher",            100, None),
    ("Si", "Fisher",            100, None),
    ("Fe", "Fisher",            20, None),
    ("Ni", "Fisher",            60, 170),
    ("Cu", "Fisher (spherical)", 100, 325),
    ("Ti", "ESPI",              325, None),
    ("Ti", "Fisher (no source)", 60, 100),
    ("Mg", "Fisher (no source)", 20, 100),
    ("Sc", "ESPI",              40, None),
    ("Er", "ESPI",              40, None),
]

TARGET_LO_UM, TARGET_HI_UM = 150, 300
TARGET_MID_UM = 250.0


def impurity_budget() -> None:
    print("=" * 92)
    print("1. IMPURITY BUDGET - ppm of tramp element each feedstock puts into the finished alloy")
    print("=" * 92)
    print(f"{'El':<4}{'Supplier':<22}{'Purity':>9}{'Max wt.%':>10}{'ppm to alloy':>15}  Note")
    print("-" * 92)
    rows = []
    for el, sup, purity, note in QUOTED_PURITY:
        ppm = MAX_WT_PCT[el] / 100.0 * (1 - purity / 100.0) * 1e6
        rows.append((ppm, el, sup, purity, note))
    for ppm, el, sup, purity, note in sorted(rows, reverse=True):
        print(f"{el:<4}{sup:<22}{purity:>8.3f}%{MAX_WT_PCT[el]:>10.1f}{ppm:>15.0f}  {note}")

    print()
    # Worst-case stack using the recommended buy for each element (one supplier per element).
    best = {
        "Al": 99.7, "Si": 99.9, "Zn": 99.99, "Mg": 99.9, "Mn": 99.9, "Cu": 99.9,
        "Cr": 99.9, "Ni": 99.7, "Fe": 99.9, "Sn": 99.85, "Er": 99.9, "Sc": 99.9,
        "Ti": 99.7,
    }
    total = sum(MAX_WT_PCT[e] / 100.0 * (1 - p / 100.0) * 1e6 for e, p in best.items())
    al_share = MAX_WT_PCT["Al"] / 100.0 * (1 - 99.7 / 100.0) * 1e6
    total_4n_al = total - al_share + MAX_WT_PCT["Al"] / 100.0 * (1 - 99.99 / 100.0) * 1e6
    print(f"Worst-case total with 99.7% Al base : {total:>7.0f} ppm  "
          f"(aluminium alone contributes {al_share:.0f} ppm = {100*al_share/total:.0f}%)")
    print(f"Worst-case total with 99.99% Al base: {total_4n_al:>7.0f} ppm  "
          f"({total/total_4n_al:.1f}x lower)")
    print()
    print("Reference points:")
    for name, ppm in REFERENCES.items():
        print(f"  {name:<40} {ppm:>6} ppm")
    print()
    # Fe specifically: typical commercial 99.7% Al powder splits its 0.3% as ~0.15 Fe / 0.10 Si.
    fe_from_al = MAX_WT_PCT["Al"] / 100.0 * 0.0015 * 1e6
    print(f"If AEE AL-111's 0.3% impurity is a typical Fe 0.15 / Si 0.10 / other 0.05 split,")
    print(f"the Al base alone delivers ~{fe_from_al:.0f} ppm Fe ({fe_from_al/1e4:.3f} wt.%) to the alloy")
    print(f"  -> {fe_from_al/REFERENCES['Scalmalloy Fe limit (0.068 wt.%)']:.1f}x the Scalmalloy Fe limit;"
          f" {fe_from_al/REFERENCES['AlSi10Mg Fe limit (0.25 wt.%)']:.2f}x the AlSi10Mg limit.")
    print("  ACTION: request the AL-111 certificate of analysis before assuming this split.")


def size_screen() -> None:
    print()
    print("=" * 92)
    print(f"2. PARTICLE SIZE - quoted cuts vs the {TARGET_LO_UM}-{TARGET_HI_UM} um auger target")
    print("=" * 92)
    print(f"{'El':<4}{'Supplier':<22}{'Cut (um)':>14}{'Cohesion':>10}{'In band?':>10}  Sieve rescue?")
    print("-" * 92)
    for el, sup, top, bot in QUOTED_CUTS:
        hi = MESH_UM[top] if top else float("inf")
        lo = MESH_UM[bot] if bot else 0.0
        cut = f"{lo:.0f}-{hi:.0f}" if hi != float("inf") else f">{lo:.0f}"
        # Characteristic size: geometric mean of the screened band; for an un-bottom-screened
        # cut, assume the mass median sits at ~40% of the top aperture (typical for -X mesh
        # milled/HDH product).
        d_char = (lo * hi) ** 0.5 if lo > 0 else 0.40 * hi
        cohesion = (TARGET_MID_UM / d_char) ** 2  # van der Waals / gravity scales as 1/d^2
        in_band = "yes" if lo >= TARGET_LO_UM and hi <= TARGET_HI_UM else (
            "partial" if hi > TARGET_LO_UM else "NO")
        if hi <= TARGET_LO_UM:
            rescue = "impossible - no coarse fraction exists"
        elif lo >= TARGET_LO_UM and hi <= TARGET_HI_UM:
            rescue = "not needed"
        elif hi > TARGET_HI_UM and lo < TARGET_LO_UM:
            rescue = "yes - screen both ends, moderate yield"
        elif hi > TARGET_HI_UM:
            rescue = "yes - top screen only, high yield"
        else:
            rescue = "yes - bottom screen at +100 mesh, moderate yield"
        print(f"{el:<4}{sup:<22}{cut:>14}{cohesion:>9.1f}x{in_band:>10}  {rescue}")
    print()
    print("Cohesion column = (250 um / d_char)^2, the ratio of van der Waals to gravitational")
    print("force relative to a particle at the middle of the target band. >10x means the powder")
    print("is cohesive: it bridges and rat-holes in a small screw feeder instead of flowing.")


def dose_error() -> None:
    print()
    print("=" * 92)
    print("3. WHY FLOWABILITY MATTERS FOR A COMBINATORIAL CAMPAIGN")
    print("=" * 92)
    batch = 100.0
    for el, wt_pct, scatter in [("Ti", 0.5, 0.20), ("Sc", 0.8, 0.20), ("Cr", 2.0, 0.20),
                                ("Mn", 5.0, 0.20), ("Si", 12.0, 0.20)]:
        target_g = batch * wt_pct / 100.0
        err_g = target_g * scatter
        print(f"{el:<3} target {target_g:>5.2f} g in a {batch:.0f} g batch; a +/-{scatter:.0%} "
              f"feeder scatter = +/-{err_g:.3f} g = +/-{err_g/batch*100:.3f} wt.% absolute "
              f"({scatter:.0%} relative composition error)")
    print()
    print("Cohesive powders in small screw feeders routinely show +/-10-30% dose scatter until")
    print("they are agitated/vibrated. For the microalloyed elements (Ti, Sc, Zr, Er) that")
    print("scatter is the same size as the composition steps the campaign is trying to resolve.")


def campaign_mass_ranking() -> None:
    print()
    print("=" * 92)
    print("4. CAMPAIGN MASS RANKING - which elements actually need automated dosing")
    print("=" * 92)
    # Total grams consumed across 20 x 100 g runs, from purchase-quantity-model.md section 3.
    need_g = {
        "Al": 1428, "Al-10Zr": 275, "Al-2Sc": 200, "Al-20Ce": 188, "Al-5Li": 58,
        "Mn": 55, "Al-10Er": 50, "Mg": 36, "Si": 30, "Zn": 23, "Cr": 20, "Cu": 20,
        "Ni": 5, "Ti": 7.5, "Fe": 2.5, "Sn": 2.5,
    }
    print(f"{'Item':<12}{'g needed for 20 runs':>22}  {'dosing recommendation'}")
    print("-" * 92)
    for item, g in sorted(need_g.items(), key=lambda kv: -kv[1]):
        if g >= 100:
            rec = "auger-dose - size/flow really matters here"
        elif g >= 20:
            rec = "auger-dose if the cut allows, else pre-weigh"
        else:
            rec = "pre-weigh into capsules; auger buys almost nothing"
        print(f"{item:<12}{g:>22.1f}  {rec}")
    print()
    small = sum(g for item, g in need_g.items() if g < 20)
    print(f"The six smallest items total {small:.1f} g across the whole 20-run campaign -")
    print("less than one Fisher pack. Fighting for a 150-300 um cut on those is not worth it.")




# --- Surface-oxide budget ------------------------------------------------------------------
# "99.9% metals basis" says nothing about oxygen: metals-basis assays exclude O, C, N and H.
# For a passivated metal powder the adsorbed/native oxide is usually the LARGEST single
# impurity, and unlike the metallic impurities it scales with 1/particle-diameter.
#
# rho_metal (g/cm3), rho_oxide (g/cm3), oxygen mass fraction of the oxide, native film (nm)
OXIDE = {
    "Al": (2.70, 3.95, 48 / 101.96, 5.0),
    "Mg": (1.74, 3.58, 16 / 40.30, 5.0),
    "Ti": (4.51, 4.23, 32 / 79.87, 5.0),
    "Cr": (7.19, 5.22, 48 / 151.99, 3.0),
    "Si": (2.33, 2.65, 32 / 60.08, 2.0),
    "Fe": (7.87, 5.24, 48 / 159.69, 4.0),
    "Zn": (7.14, 5.61, 16 / 81.38, 8.0),
    "Cu": (8.96, 6.00, 16 / 143.09, 4.0),
    "Mn": (7.21, 4.50, 48 / 157.87, 5.0),
    "Ni": (8.91, 6.67, 16 / 74.69, 3.0),
    "Sn": (7.31, 6.95, 32 / 150.71, 4.0),
    "Sc": (2.99, 3.86, 48 / 137.91, 10.0),
    "Er": (9.07, 8.64, 48 / 382.56, 10.0),
}


def oxygen_ppm(element: str, d_um: float) -> float:
    """Oxygen carried as native surface oxide, in ppm of the feedstock's own mass."""
    rho_m, rho_ox, o_frac, delta_nm = OXIDE[element]
    shell_mass_frac = 6.0 * (delta_nm * 1e-3) / d_um * (rho_ox / rho_m)  # thin-shell 6*delta/d
    return shell_mass_frac * o_frac * 1e6


def surface_oxide() -> None:
    print()
    print("=" * 92)
    print("5. SURFACE-OXIDE BUDGET - the impurity that never appears on a 'metals basis' CoA")
    print("=" * 92)
    print(f"{'El':<4}{'Quoted cut':<26}{'d_char':>8}{'O in feedstock':>16}{'O in 100 g batch':>18}")
    print("-" * 92)
    weighted = []
    for el, sup, top, bot in QUOTED_CUTS:
        if el not in OXIDE:
            continue
        hi = MESH_UM[top] if top else float("inf")
        lo = MESH_UM[bot] if bot else 0.0
        d_char = (lo * hi) ** 0.5 if lo > 0 else 0.40 * hi
        o_own = oxygen_ppm(el, d_char)
        o_batch = o_own * MAX_WT_PCT[el] / 100.0  # ppm of the finished 100 g charge
        weighted.append((el, sup, o_batch))
        label = f"{sup} {lo:.0f}-{hi:.0f} um"
        print(f"{el:<4}{label:<26}{d_char:>7.0f}u{o_own:>15.0f}{o_batch:>18.1f}")
    print()
    print("The last column is what actually matters: feedstock oxide scaled by how much of that")
    print("element is in the alloy. A dirty-but-tiny addition is harmless; a slightly-oxidised")
    print("base metal is not.")

    print()
    print("Batch-level consequence for the 90.5 g of aluminium in a 100 g charge:")
    for label, d in [("AEE AL-111, -50+100 mesh", (150 * 300) ** 0.5),
                     ("a -100 mesh Al powder", 0.40 * 150),
                     ("a -325 mesh Al powder", 0.40 * 45),
                     ("LPBF-grade 15-45 um Al", 30.0)]:
        o_ppm_of_al = oxygen_ppm("Al", d)
        mg_o = 90.5 * o_ppm_of_al * 1e-6 * 1000
        print(f"  {label:<28} d={d:>5.0f} um -> {o_ppm_of_al:>5.0f} ppm O in the Al "
              f"= {mg_o:>5.1f} mg O = {mg_o / 100.0 * 1000:>5.0f} ppm of the finished batch")
    print()
    print("Gas-atomised AM aluminium powder is typically specified at 400-1200 ppm O TOTAL.")
    print("Charging fine Al powder would blow that budget before atomisation even starts;")
    print("the -50+100 mesh AL-111 cut lands roughly an order of magnitude below it.")
    print("This is the quantitative reason 'coarse and slightly less pure' beats")
    print("'fine and nominally 4N' for every element in this campaign.")


if __name__ == "__main__":
    impurity_budget()
    size_screen()
    dose_error()
    campaign_mass_ranking()
    surface_oxide()
