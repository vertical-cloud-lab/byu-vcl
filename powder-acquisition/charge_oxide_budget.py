"""Oxide/oxygen budget for the three ways of getting ~85 g of aluminium into a 100 g charge.

Answers the question raised in issue #161 on 2026-09-09: if the non-Al elements are dispensed
into a *sacrificial aluminium cup* that is then set inside the atomizer's graphite crucible,
how much surface oxide does the aluminium base carry into the melt, compared with dosing the
same mass as powder?

Native oxide thickness on Al is 2-4 nm (Sun et al. 2006, cited in the Edison corroboration
report); 3 nm is used here. Oxygen mass fraction of a particle/part is

    w_O  =  (A_surface * delta * rho_Al2O3 / m_part) * (M_O3 / M_Al2O3)

which for a sphere reduces to the familiar 6*delta*rho_ox/(d*rho_Al) scaling.

Run:  python3 charge_oxide_budget.py
"""

import math

DELTA_M = 3e-9  # native Al2O3 film thickness, m
RHO_AL2O3 = 3950.0  # kg/m3
RHO_AL = 2700.0  # kg/m3
O_FRAC_AL2O3 = 3 * 15.999 / (2 * 26.982 + 3 * 15.999)  # 0.4707

AL_MASS_G = 85.0  # aluminium in a 100 g charge


def ppm_o_from_area(area_m2: float, mass_kg: float) -> float:
    """Oxygen delivered, in ppm of the part's own mass."""
    oxide_kg = area_m2 * DELTA_M * RHO_AL2O3
    return 1e6 * oxide_kg * O_FRAC_AL2O3 / mass_kg


def ppm_o_powder(d_um: float) -> float:
    """Spherical powder of diameter d: area/mass = 6/(d*rho)."""
    d = d_um * 1e-6
    area_per_kg = 6.0 / (d * RHO_AL)
    return ppm_o_from_area(area_per_kg, 1.0)


def cup(od_mm, height_mm, wall_mm, base_mm):
    """Right-cylindrical open cup. Returns (mass_g, area_m2)."""
    ro, h, t, b = od_mm / 2, height_mm, wall_mm, base_mm
    ri, hi = ro - t, h - b
    vol = math.pi * ro**2 * h - math.pi * ri**2 * hi  # mm3
    area = (
        2 * math.pi * ro * h  # outer wall
        + math.pi * ro**2  # outer base
        + 2 * math.pi * ri * hi  # inner wall
        + math.pi * ri**2  # inner base
        + math.pi * (ro**2 - ri**2)  # rim
    )  # mm2
    return vol * 1e-3 * RHO_AL / 1000, area * 1e-6


if __name__ == "__main__":
    print(f"native oxide {DELTA_M*1e9:.0f} nm, O fraction of Al2O3 = {O_FRAC_AL2O3:.4f}")
    print(f"\naluminium base = {AL_MASS_G:.0f} g of a 100 g charge\n")
    print(f"{'route':<44}{'ppm O in Al':>12}{'ppm O in batch':>16}")
    print("-" * 72)

    for label, d in [
        ("LPBF-grade Al powder, 30 um", 30),
        ("-100 mesh Al powder, ~60 um mean", 60),
        ("AEE AL-111, -50+100 mesh, ~212 um mean", 212),
        ("4N Al shot, 9.5 mm", 9500),
    ]:
        p = ppm_o_powder(d)
        print(f"{label:<44}{p:>12.1f}{p * AL_MASS_G / 100:>16.2f}")

    # A cup sized to hold ~85 g of Al and still fit a small induction crucible.
    for od, h, wall, base in [(35, 45, 6.0, 8.0), (30, 55, 6.5, 8.0), (40, 40, 5.5, 8.0)]:
        m, a = cup(od, h, wall, base)
        p = ppm_o_from_area(a, m / 1000)
        label = f"machined Al cup OD{od} H{h} wall{wall} ({m:.0f} g)"
        print(f"{label:<44}{p:>12.2f}{p * m / 100:>16.3f}")

    print("\nsolute oxide, for scale (own mass basis):")
    for el, d_um, rho, rho_ox, o_frac, wt_pct in [
        ("Cr, -325 mesh (~18 um)", 18, 7190, 5220, 48 / 152, 5.0),
        ("Mn, -100 mesh (~75 um)", 75, 7210, 5370, 32 / 158.9, 5.0),
        ("Ti, -325 mesh (~18 um)", 18, 4510, 4230, 32 / 79.9, 1.0),
        ("Mg, -50+100 mesh (~212 um)", 212, 1740, 3580, 16 / 40.3, 4.0),
    ]:
        area_per_kg = 6.0 / (d_um * 1e-6 * rho)
        ppm = 1e6 * area_per_kg * DELTA_M * rho_ox * o_frac
        print(f"  {el:<42}{ppm:>12.0f}{ppm * wt_pct / 100:>16.2f}")
