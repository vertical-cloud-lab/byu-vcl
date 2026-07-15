"""Purchase-quantity model for atomizer feedstock (issue #161).

Recomputes every number in purchase-quantity-model.md from the assumption
tables below. Edit CAMPAIGN / OVERCHARGE / CONTINGENCY / MASTER_ALLOYS and
re-run:

    python purchase_quantity_model.py
"""

BATCH_G = 100.0
CONTINGENCY = 1.25  # spillage, weighing losses, one re-run

# (family name, number of runs, {element: max wt.% assumed for every run})
CAMPAIGN = [
    ("Al-Mn-Cr-Zr", 8, {"Mn": 5.0, "Cr": 2.0, "Zr": 2.0, "Ti": 0.5}),
    ("Al-Zr-Er-Sc", 4, {"Zr": 1.5, "Er": 1.0, "Sc": 0.8, "Ti": 0.5}),
    ("Al-Ce-Mg", 3, {"Ce": 10.0, "Mg": 6.0}),
    ("Al-Si-Mg-Cu", 2, {"Si": 12.0, "Mg": 0.5, "Cu": 4.0, "Fe": 1.0, "Sn": 1.0}),
    ("Al-Zn-Mg-Cu", 2, {"Zn": 8.0, "Mg": 3.0, "Cu": 2.0, "Ni": 2.0}),
    ("Al-Li-Cu", 1, {"Li": 2.0, "Cu": 4.0}),
]

# Evaporation over-charge factors (Edison report: 5-15% for volatiles)
OVERCHARGE = {"Mg": 1.15, "Zn": 1.15, "Li": 1.15, "Mn": 1.10}

# Elements delivered via master alloys: element -> (label, solute wt. fraction)
MASTER_ALLOYS = {
    "Zr": ("Al-10Zr", 0.10),
    "Ce": ("Al-20Ce", 0.20),
    "Ti": ("Al-5Ti-1B", 0.05),
    "Er": ("Al-10Er", 0.10),
    "Sc": ("Al-2Sc", 0.02),
    "Li": ("Al-10Li", 0.10),
}


def main():
    total_runs = sum(runs for _, runs, _ in CAMPAIGN)
    total_charge = total_runs * BATCH_G

    charged = {}  # worst-case grams of each solute actually in the melts
    for _, runs, comp in CAMPAIGN:
        for el, wtpct in comp.items():
            charged[el] = charged.get(el, 0.0) + runs * BATCH_G * wtpct / 100.0

    print(f"Campaign: {total_runs} runs x {BATCH_G:.0f} g = {total_charge:.0f} g total charge\n")
    header = f"{'El':<4}{'charged g':>11}{'to buy g':>11}  purchase form"
    print(header)
    print("-" * len(header))

    al_from_masters = 0.0
    for el in sorted(charged, key=charged.get, reverse=True):
        need = charged[el] * OVERCHARGE.get(el, 1.0) * CONTINGENCY
        if el in MASTER_ALLOYS:
            label, frac = MASTER_ALLOYS[el]
            master_g = need / frac
            al_from_masters += charged[el] * OVERCHARGE.get(el, 1.0) / frac * (1 - frac)
            form = f"{label} master alloy ({master_g:.0f} g)"
        else:
            form = "elemental"
        print(f"{el:<4}{charged[el]:>11.1f}{need:>11.1f}  {form}")

    solute_total = sum(charged.values())
    al_charged = total_charge - solute_total
    al_elemental = al_charged - al_from_masters
    print("-" * len(header))
    print(f"Al balance: {al_charged:.0f} g charged; ~{al_from_masters:.0f} g arrives in master alloys")
    print(f"Elemental 4N Al shot to buy: {al_elemental:.0f} g x {CONTINGENCY} = {al_elemental * CONTINGENCY:.0f} g")


if __name__ == "__main__":
    main()
