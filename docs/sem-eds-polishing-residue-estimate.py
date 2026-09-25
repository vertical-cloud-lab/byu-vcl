"""First-order estimate of how polishing residue biases SEM-EDS of AlSi10Mg.

Used for the tables in sem-eds-polishing-silicon-free-final-polish.md. Run with
`python docs/sem-eds-polishing-residue-estimate.py` (needs `pip install xraylib`).

Model, the same one used for the 2026-09-25 silica estimate in #110, applied per X-ray line:

    f_X        = (rho * t)_residue / (rho * R_x)_X      share of line X's generation depth that is residue
    C_X(app)   = (1 - f_X) * C_X(alloy) + f_X * C_X(residue)

R_x is the Anderson-Hasler X-ray range, rho*R_x [g/cm^3 * um] = 0.064 * (E0^1.68 - Ec^1.68).
The residue is treated as a uniform layer of equivalent solid thickness t. Surface weighting
(phi(0) > 1, and absorption favouring shallow X-rays) would make residue effects ~20-50 %
larger than shown, so read the numbers as a lower bound on the bias.
"""
import math

import xraylib as xl

ALLOY = {"Al": 89.65, "Si": 10.0, "Mg": 0.35}  # wt%; Mg is the middle of the 0.20-0.45 spec
EC = {"Al": 1.560, "Si": 1.839, "Mg": 1.303, "O": 0.532, "C": 0.284}  # K edges, keV
TAKEOFF_DEG = 35.1  # the Octane Plus take-off angle from the lab's eZAF reports

RESIDUES = {
    "colloidal silica": {"rho": 2.2, "comp": {"Si": 46.74, "O": 53.26}},
    "alumina": {"rho": 3.9, "comp": {"Al": 52.93, "O": 47.07}},
    "diamond": {"rho": 3.51, "comp": {"C": 100.0}},
}

# 25 nm = a close-packed monolayer of the ~42 nm spheres in Gage's 2026-05-22 image
LAYERS_NM = (25.0, 2.5, 0.25)
VOLTAGES_KV = (5, 10, 15)


def xray_range_mass(e0_kv, ec_kv):
    return 0.064 * (e0_kv**1.68 - ec_kv**1.68)


def apparent(e0_kv, residue, t_nm):
    out = {}
    for el in ("Al", "Si", "Mg", "O", "C"):
        f = residue["rho"] * t_nm / 1000.0 / xray_range_mass(e0_kv, EC[el])
        out[el] = (1 - f) * ALLOY.get(el, 0.0) + f * residue["comp"].get(el, 0.0)
    return out


def alloy_only(c):
    """Renormalize Al+Si+Mg to 100, i.e. O and C excluded from the quant."""
    s = c["Al"] + c["Si"] + c["Mg"]
    return {k: 100 * c[k] / s for k in ("Al", "Si", "Mg")}


def main():
    print("X-ray generation depth in AlSi10Mg (um):")
    for e0 in VOLTAGES_KV:
        depths = "  ".join(f"{el} {xray_range_mass(e0, EC[el]) / 2.68:.2f}" for el in ("O", "Mg", "Al", "Si"))
        print(f"  {e0:2d} kV  {depths}")

    for t in LAYERS_NM:
        print(f"\nResidue equivalent to a {t} nm solid layer")
        print("  kV  residue            O add  C add |   Al     Si (rel)          Mg (rel)")
        for e0 in VOLTAGES_KV:
            for name, res in RESIDUES.items():
                c = apparent(e0, res, t)
                n = alloy_only(c)
                print(
                    f"  {e0:2d}  {name:17s} {c['O']:6.2f} {c['C']:6.2f} | {n['Al']:6.2f} "
                    f"{n['Si']:6.2f} ({100 * (n['Si'] / ALLOY['Si'] - 1):+5.1f}%)  "
                    f"{n['Mg']:5.3f} ({100 * (n['Mg'] / ALLOY['Mg'] - 1):+5.1f}%)"
                )

    print(f"\nShare of each line absorbed by a carbon layer, {TAKEOFF_DEG} deg take-off:")
    lines = {"O Ka": 8, "Mg Ka": 12, "Al Ka": 13, "Si Ka": 14}
    for t_nm, rho, label in ((25, 3.51, "diamond"), (2.5, 3.51, "diamond"), (20, 2.0, "evaporated C coat")):
        cells = []
        for name, z in lines.items():
            mu = xl.CS_Total(6, xl.LineEnergy(z, xl.KL3_LINE))
            lost = 1 - math.exp(-mu * rho * t_nm * 1e-7 / math.sin(math.radians(TAKEOFF_DEG)))
            cells.append(f"{name} {100 * lost:.2f}%")
        print(f"  {t_nm:>4} nm {label:17s} " + "  ".join(cells))


if __name__ == "__main__":
    main()
