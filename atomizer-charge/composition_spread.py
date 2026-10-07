"""Composition spread: 4047 powder in 6063 cups, 0 to ~30 wt% powder (#222, #264).

Uses the cups and plugs as made (#222, #248), not the older drawing in cad/:
3/4" 6063 bar, cup 2.750" long with a 1/2" drill 2.25" deep (118 deg point),
plug .508" x .5625" with a #60 vent, pressed flush.  The top of the range needs a
bigger bore, so the "thin" cup is the same cup with a 5/8" drill and a 1/4" plug.

Every composition here is a nominal-spec envelope: the low end takes each alloy at its
minimum, the high end at its maximum.  One bar lot and one powder lot sit at a single
point inside it, so once their compositions are measured the spread between runs is
set by weighing, not by the specs.

    python atomizer-charge/composition_spread.py   # prints the tables, writes the .json
"""

import json
import math
from pathlib import Path

IN = 25.4  # mm
RHO_6063 = 2.69  # g/cm^3, as in cad/charge_cad.py
RHO_TAP = 1.60  # 4047 powder tapped by hand: same as AlSi10Mg (2.66 vs 2.67 g/cm^3 solid)
POINT_DEG = 118.0
VENT_D = 0.040 * IN  # #60
STOCK_D = 0.750 * IN  # +/-.014" (McMaster 1640T16), ~+/-5 % on cup mass: weigh it

# wt%, (min, max).  Aluminum Association limits; "max only" elements have min 0.
SPEC = {
    "6063": {"Si": (0.20, 0.60), "Mg": (0.45, 0.90), "Fe": (0, 0.35), "Cu": (0, 0.10),
             "Mn": (0, 0.10), "Cr": (0, 0.10), "Zn": (0, 0.10), "Ti": (0, 0.10)},
    "4047": {"Si": (11.0, 13.0), "Mg": (0, 0.10), "Fe": (0, 0.80), "Cu": (0, 0.30),
             "Mn": (0, 0.15), "Cr": (0, 0.05), "Zn": (0, 0.20), "Ti": (0, 0.05)},
}  # 4047 has no Cr/Ti line, so they fall under "others, each 0.05"

CUPS = {
    # bore = as drilled; .5075" is the .508" plug less the .0005" fit.  depth = 2.25",
    # which may have been measured to the drill tip or to full diameter: both are run.
    "as_made": {"bore_in": 0.5075, "plug_d_in": 0.508, "plug_l_in": 0.5625},
    "thin": {"bore_in": 0.627, "plug_d_in": 0.6275, "plug_l_in": 0.250},  # 5/8" drill
}
CUP_L_IN, DEPTH_IN = 2.750, 2.25


def cup_numbers(bore_in, plug_d_in, plug_l_in, depth_to_tip):
    """6063 mass (cup + plug) and full-fill powder mass under a flush plug, in g."""
    r = bore_in * IN / 2
    cone_h = r / math.tan(math.radians(POINT_DEG / 2))
    cyl_l = DEPTH_IN * IN - (cone_h if depth_to_tip else 0.0)
    a = math.pi * r**2
    hole = a * cyl_l + a * cone_h / 3
    cup = math.pi * (STOCK_D / 2) ** 2 * CUP_L_IN * IN - hole
    plug_l = plug_l_in * IN
    plug = (math.pi * (plug_d_in * IN / 2) ** 2 - math.pi * (VENT_D / 2) ** 2) * plug_l
    powder_space = hole - a * plug_l
    return {
        "al_6063_g": (cup + plug) / 1000 * RHO_6063,
        "full_powder_g": powder_space / 1000 * RHO_TAP,
        "wall_in": (0.750 - bore_in) / 2,
    }


def cup(name):
    """Average of the two depth readings, with the half-spread as the uncertainty."""
    lo, hi = (cup_numbers(**CUPS[name], depth_to_tip=t) for t in (True, False))
    out = {k: round((lo[k] + hi[k]) / 2, 2) for k in lo}
    out["full_powder_pm_g"] = round(abs(hi["full_powder_g"] - lo["full_powder_g"]) / 2, 2)
    out["al_6063_pm_g"] = round(abs(hi["al_6063_g"] - lo["al_6063_g"]) / 2, 2)
    w_full = out["full_powder_g"] / (out["full_powder_g"] + out["al_6063_g"])
    out["full_powder_wt_pct"] = round(100 * w_full, 1)
    return out


def envelope(w, el):
    """(min, nominal mid, max) wt% of one element at powder mass fraction w."""
    a, b = SPEC["6063"][el], SPEC["4047"][el]
    lo = (1 - w) * a[0] + w * b[0]
    hi = (1 - w) * a[1] + w * b[1]
    return round(lo, 2), round((lo + hi) / 2, 2), round(hi, 2)


def charge_composition(pieces):
    """Melt Si/Mg envelope from weighed pieces: [("6063", g), ("4047", g), ...]."""
    total = sum(m for _, m in pieces)
    out = {}
    for el in ("Si", "Mg", "Fe"):
        lo = sum(m * SPEC[a][el][0] for a, m in pieces) / total
        hi = sum(m * SPEC[a][el][1] for a, m in pieces) / total
        out[el] = (round(lo, 2), round(hi, 2))
    return out


# The run points: powder wt% of (cup + plug + powder), and which cup carries it.
POINTS = [(0.0, None), (7.5, "as_made"), (15.0, "as_made"), (22.5, "thin"), (30.0, "thin")]


def main():
    cups = {k: cup(k) for k in CUPS}
    rows = []
    for pct, kind in POINTS:
        w = pct / 100
        row = {"powder_wt_pct": pct, "cup": kind or "6063 only (#261 baseline)"}
        if kind:
            al = cups[kind]["al_6063_g"]
            row["powder_g"] = round(al * w / (1 - w), 1)
            row["fill_frac_of_full"] = round(row["powder_g"] / cups[kind]["full_powder_g"], 2)
        for el in ("Si", "Mg", "Fe"):
            row[el] = envelope(w, el)
        rows.append(row)
    oct2 = cups["as_made"]
    oct2_w = oct2["full_powder_g"] / (oct2["full_powder_g"] + oct2["al_6063_g"])
    result = {
        "cups": cups,
        "points": rows,
        "oct2_full_as_made_cup": {
            "powder_wt_pct": round(100 * oct2_w, 1),
            **{el: envelope(oct2_w, el) for el in ("Si", "Mg", "Fe")},
        },
        "spec": SPEC,
        "rho_tap_g_cm3": RHO_TAP,
        "rho_6063_g_cm3": RHO_6063,
    }
    for k, c in cups.items():
        print(f"{k:8s} wall {c['wall_in']:.3f}\"  6063 {c['al_6063_g']:.1f}+/-{c['al_6063_pm_g']} g"
              f"  full {c['full_powder_g']:.1f}+/-{c['full_powder_pm_g']} g"
              f" = {c['full_powder_wt_pct']} wt% powder")
    print("\nwt% powder  cup       powder g  fill   Si min/mid/max     Mg min/mid/max     Fe max")
    for r in rows:
        g = f"{r.get('powder_g', 0):5.1f}"
        f = f"{r.get('fill_frac_of_full', 0):4.0%}" if "fill_frac_of_full" in r else "   -"
        print(f"{r['powder_wt_pct']:6.1f}     {r['cup'][:8]:8s}  {g}    {f}  {r['Si']}  {r['Mg']}  {r['Fe'][2]}")
    print("\nOct 2 (u23y78, full as-made cup):", result["oct2_full_as_made_cup"])
    Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    main()
