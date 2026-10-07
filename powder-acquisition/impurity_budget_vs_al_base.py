"""Impurity budget once the Al base is 4N or 5N (issue #161, 2026-10-07).

The 2026-10-06 McMaster note waved off solute purity ("even at 99.0% that would be
<= 400 ppm, against 2,715 ppm from the 99.7% Al base"). That comparison only holds
while the base is 99.7%. With a 4N or 5N rod the base stops dominating and every
solute line has to be re-scored. This script does that per alloy family, using the
family compositions in purchase_quantity_model.py.

Model: the metallic impurity a feedstock carries into the finished alloy is
    wt.% of that feedstock in the charge x (1 - purity).
Metals basis only: O, C, N and H are not included (see quote_analysis.py §5).

    python impurity_budget_vs_al_base.py
"""

from purchase_quantity_model import CAMPAIGN

AL_BASES = {"99.7% (P1020 / AEE AL-111)": 99.7, "4N (99.99%)": 99.99, "5N (99.999%)": 99.999}

# Purity of each solute as currently sourced (percent). Ni has two entries:
# the Nickel 200 rod's ASTM B160 floor and a typical certified heat.
AS_SOURCED = {
    "Mn": 99.9, "Cr": 99.9, "Zn": 99.99, "Sn": 99.9, "Mg": 99.9, "Si": 99.9,
    "Fe": 99.9, "Cu": 99.9, "Ti": 99.7, "Zr": 99.9, "Er": 99.9, "Sc": 99.9,
    "Ce": 99.8, "Li": 99.9, "Ni": 99.0,
}
NI_200_TYPICAL = 99.6        # Ni + Co of a typical Nickel 200 heat; the spec floor is 99.0
# Nickel 200 (ASTM B160 / UNS N02200) maxima, wt.% of the Ni: the elements it brings.
NI_200_MAX = {"Fe": 0.40, "Mn": 0.35, "Si": 0.35, "Cu": 0.25, "C": 0.15, "S": 0.01}

# Dilute master alloys carry their own aluminium. Mass of master per 100 g charge
# = solute wt.% / solute fraction in the master.
MASTER_FRACTION = {"Zr": 0.10, "Er": 0.10, "Sc": 0.02, "Ce": 0.20, "Li": 0.05}
COMMERCIAL_MASTER_AL_PURITY = 99.7   # masters are usually cast on primary (P1020-type) Al


def budget(comp, al_purity, solute_purity, masters=False, master_al_purity=99.7):
    """ppm of metallic impurity in the finished alloy, split by source."""
    out = {}
    al_wt = 100.0 - sum(comp.values())
    al_from_masters = 0.0
    for el, w in comp.items():
        out[el] = w / 100.0 * (1 - solute_purity[el] / 100.0) * 1e6
        if masters and el in MASTER_FRACTION:
            al_carried = w / MASTER_FRACTION[el] - w
            al_from_masters += al_carried
            out[f"Al in {el} master"] = al_carried / 100.0 * (1 - master_al_purity / 100.0) * 1e6
    out["Al base"] = (al_wt - al_from_masters) / 100.0 * (1 - al_purity / 100.0) * 1e6
    return out


def parity_purity(w_solute, al_purity, al_wt):
    """Purity at which a solute contributes as much impurity as the Al base itself."""
    return 100.0 * (1 - al_wt * (1 - al_purity / 100.0) / w_solute)


def main():
    print("1. TOTAL METALLIC IMPURITY (ppm of finished alloy), solutes as sourced")
    print("   (Ni at the Nickel 200 floor of 99.0%; masters not used)\n")
    head = f"{'family':<14}" + "".join(f"{k[:13]:>16}" for k in AL_BASES) + "   biggest single source at 4N"
    print(head)
    for fam, _, comp in CAMPAIGN:
        cells = []
        for p in AL_BASES.values():
            b = budget(comp, p, AS_SOURCED)
            tot = sum(b.values())
            cells.append(f"{tot:7.0f} ({100 * (tot - b['Al base']) / tot:3.0f}% sol)")
        b4 = budget(comp, 99.99, AS_SOURCED)
        top = max(b4.items(), key=lambda kv: kv[1])
        print(f"{fam:<14}" + "".join(f"{c:>16}" for c in cells) + f"   {top[0]} {top[1]:.0f} ppm")

    print("\n2. THE NICKEL LINE (Al-Zn-Mg-Cu-Ni family, 2 wt.% Ni)")
    comp = dict(CAMPAIGN[4][2])
    for label, p_ni in [("Nickel 200, spec floor 99.0%", 99.0),
                        (f"Nickel 200, typical {NI_200_TYPICAL}%", NI_200_TYPICAL),
                        ("McMaster 1402N24 label 99.9%", 99.9),
                        ("Ni 270 / carbonyl pellet 99.97%", 99.97)]:
        sp = dict(AS_SOURCED, Ni=p_ni)
        for base_label, p in AL_BASES.items():
            b = budget(comp, p, sp)
            if p == 99.7:
                continue
            print(f"  {label:<34} Al {base_label[:11]:<12} Ni brings {b['Ni']:5.0f} ppm"
                  f" vs Al base {b['Al base']:5.1f} ppm  ({b['Ni'] / b['Al base']:4.1f}x)")
    print("  Nickel 200 ceilings, as ppm of the alloy at 2 wt.% Ni:",
          ", ".join(f"{k} {v / 100 * 0.02 * 1e6:.0f}" for k, v in NI_200_MAX.items()))

    print("\n3. PARITY PURITY: a solute at this purity adds as much impurity as the base")
    for base_label, p in list(AL_BASES.items())[1:]:
        print(f"  Al base {base_label}:")
        for el, w in [("Si", 12.0), ("Ce", 10.0), ("Zn", 8.0), ("Mg", 6.0), ("Mn", 5.0),
                      ("Cu", 4.0), ("Ni", 2.0), ("Fe", 1.0), ("Sc", 0.8)]:
            print(f"    {el} at {w:4.1f} wt.%: {parity_purity(w, p, 88.0):8.4f}%")

    print("\n4. MASTER ALLOYS CARRY THEIR OWN ALUMINIUM (Al-Zr-Er-Sc family)")
    comp = dict(CAMPAIGN[1][2])
    for base_label, p in AL_BASES.items():
        el = budget(comp, p, AS_SOURCED)
        ma = budget(comp, p, AS_SOURCED, masters=True,
                    master_al_purity=COMMERCIAL_MASTER_AL_PURITY)
        al_m = sum(v for k, v in ma.items() if k.startswith("Al in"))
        print(f"  Al base {base_label[:11]:<12} elemental Sc/Er/Zr: {sum(el.values()):6.0f} ppm"
              f" | commercial masters on 99.7% Al: {sum(ma.values()):6.0f} ppm"
              f" ({al_m:.0f} of it from the masters' Al)")
    grams = sum(w / MASTER_FRACTION[e] for e, w in comp.items() if e in MASTER_FRACTION)
    print(f"  Masters for this family weigh {grams:.0f} g of each 100 g charge.")


if __name__ == "__main__":
    main()
