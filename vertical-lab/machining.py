"""The numbers behind notes/machining.md (byu-vcl #367): the charge cups and plugs turned from bar in a floor cell,
cleaned in IPA (indirect ultrasonic), dried under vacuum, weighed, measured and racked.

* ``cycle()``: each operation's time for a cup and a plug in 5N Al and in OFE Cu (C10100), from published cutting data
  (the tool makers' and the German Copper Institute's) and the machine's 6,000 rpm limit; non-cutting times are
  estimates, marked as such.
* ``capacity()``: hours a day per resource at PR #332's 67 cups a day, and what the cell could make running 8 h or 24 h.
* ``costs()``: capital, and cost per cup-and-plug pair: material, tools, IPA, power, labour, capital.
* ``plot_cycle()``, ``plot_day()``: out/machining_cycle.png, out/machining_day.png.
* ``plot_floor()``: the cell on the lab's floor plan (out/machining_floor.png), from out/tray_plan.json's footprints.

    python3 machining.py        # -> out/machining.json and the three PNGs

Part geometry is charge.py's (#222's charge_cad.py). Sources are in SOURCES and in notes/machining.md. "est." marks
our estimates.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import charge as C

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

DEMAND = 67.0                    # cups a day at ten alloys a day (PR #332, notes/bottleneck.md: 16.8 runs x 4 cups)
N_MAX = 6000.0                   # rpm, Haas ST-10 (Haas 2026 model guide; Machine Tool Index)
BAR_D = 20.0                     # mm: 5N Al comes as Ø20 rod (DAL #152); OFE Cu bought at 20 mm too, so both are turned
BAR_L = 1219.0                   # mm: Haas Bar Feeder V2 takes bars up to 4 ft
REMNANT = 150.0                  # mm of each bar the feeder can't use (est.)
PLUG_OD = 12.73                  # mm: the plug's press fit in the 12.70 bore, 0.03 mm interference (assumed)
VENT_D = C.VENT_D                # 1/16 in

# Cutting data. Vc m/min, f mm/rev. Sources: SOURCES["al"], SOURCES["cu"].
CUT = {
    "Al": dict(turn=(400.0, 0.12), rough=(400.0, 0.15), drill=(150.0, 0.20), bore=(300.0, 0.08), part=(200.0, 0.05),
               vent=(60.0, 0.020), peck_d=1.5),
    "Cu": dict(turn=(220.0, 0.10), rough=(160.0, 0.15), drill=(120.0, 0.20), bore=(150.0, 0.06), part=(120.0, 0.04),
               vent=(60.0, 0.015), peck_d=1.0),
}
NONCUT = dict(bar_feed=5.0, index=0.5, rapid=1.0, peck=0.5, catch=3.0, chamfer=1.0)   # s, est.

SOURCES = {
    "al": "Pure Al is ASM machinability group E ('needs optimum tool design and machine settings to control chip and "
          "finish'); Sandvik: uncoated and PCD grades first, positive sharp edges, built-up edge worst at low speed; "
          "Haas starts wrought Al at 490 m/min with its HTSU10 insert (Haas turning-insert speeds and feeds). "
          "Drilling, "
          "boring and parting speeds here are conservative choices for MQL rather than flood (est.)",
    "cu": "German Copper Institute (DKI i.18, 2010): Cu-OFE C10100 machinability 20 (free-cutting brass 100), chip "
          "breaker recommended; carbide turning 220/160/120 m/min at chip thickness 0.1/0.32/0.8 mm; solid-carbide "
          "drilling 160 m/min at 0.24-0.29 mm/rev for Ø12-16 mm. Here drilling at 120 m/min and 0.20 mm/rev under "
          "MQL, pecking each diameter (est.)",
    "haas": "Haas ST-10: 3437 x 1596 x 2167 mm installed with chip conveyor, 3,585 kg, 44 mm bar, 15 hp, 6,000 rpm, "
            "12-station turret, US$64,995 list (Haas layout drawing 12/2024; Machine Tool Index, verified 2026-10-02); "
            "Bar Feeder V2 for bars up to 4 ft, 10-76 mm, footprint 2104 x 1283 mm",
    "ur": "UR12e (the UR10e, renamed in May 2025): 12.5 kg, 1300 mm, US$50,818-52,674 (Universal Robots press "
          "release 12 May 2025 and FAQ; distributor listings)",
    "elma": "Elmasonic P 60 H: 5.75 L, 365 x 186 x 271 mm, 37/80 kHz, US$1,999-3,361; Elma's manual: flammable "
            "liquids 'max. 1 litre' only in a separate vessel in the water-filled tank",
    "ad": "A&D AD-4212C-301 weighing module: 51 g at 0.1 mg / 320 g at 1 mg, RS-232C, US$6,736.50",
    "price_al": "5N Al: High Purity Aluminum US$475 for Ø25 x 305 mm (about $1,180/kg) and $2,350 for Ø150 x 350 mm "
                "(about $144/kg); Advent 99.9995 % (5N5, not 5N) Ø20 x 500 mm $1,535 (about $3,500/kg)",
    "price_cu": "C10100 3/4 in round, ASTM B187: Southern Copper $194.53 for 72 in (4.644 kg), about $42/kg",
}


# ------------------------------------------------------------------------------------------------ cutting times
def n_at(vc: float, d: float) -> float:
    return min(1000.0 * vc / (math.pi * d), N_MAX)


def t_turn(vc, f, d, length) -> float:
    """s for one pass along `length` mm at diameter d (constant surface speed, capped at N_MAX)."""
    return length / (f * n_at(vc, d) / 60.0)


def t_radial(vc, f, r0, r1=0.0) -> float:
    """s to feed radially from r0 in to r1 (facing, parting) at constant surface speed, the rpm capped at N_MAX."""
    rc = 1000.0 * vc / (2 * math.pi * N_MAX)              # below rc the spindle is at N_MAX
    t = 0.0
    if r0 > rc:
        hi, lo = r0, max(r1, rc)
        t += math.pi * (hi ** 2 - lo ** 2) / (f * 1000.0 * vc) * 60.0
    if r1 < min(r0, rc):
        t += (min(r0, rc) - r1) / (f * N_MAX / 60.0)
    return t


def t_drill(vc, f, d, depth, peck_d) -> float:
    """s to drill `depth` (the point included) with a retract every peck_d diameters."""
    pecks = max(0, math.ceil(depth / (peck_d * d)) - 1)
    return t_turn(vc, f, d, depth) + pecks * NONCUT["peck"]


def cycle(metal: str) -> dict:
    """{part: [(operation, seconds, kind)]} for a cup and a plug cut from the same bar; kind is the chart group."""
    c = CUT[metal]
    r0 = BAR_D / 2
    tip = (C.CUP_BORE_D / 2) / math.tan(math.radians(59.0))
    drill_d = 12.5
    cup = [
        ("bar feed, collet", NONCUT["bar_feed"], "non-cutting"),
        ("face", t_radial(*c["turn"], r0), "turn and face"),
        ("turn OD 20 -> 19.05 over 68 mm", t_turn(*c["turn"], BAR_D, 68.0), "turn and face"),
        ("drill 12.5 x 47.6 + point", t_drill(*c["drill"], drill_d, C.CUP_BORE_DEPTH + tip, c["peck_d"]),
         "drill and bore"),
        ("finish-bore 12.70 x 47.6", t_turn(*c["bore"], C.CUP_BORE_D, C.CUP_BORE_DEPTH) + NONCUT["rapid"] / 2,
         "drill and bore"),
        ("rim and OD chamfers", NONCUT["chamfer"], "turn and face"),
        ("part off, chamfering the base", t_radial(*c["part"], C.STOCK_D / 2) + NONCUT["chamfer"], "part off"),
        ("4 indexes, 5 rapids", 4 * NONCUT["index"] + 5 * NONCUT["rapid"], "non-cutting"),
        ("catch, onto the belt", NONCUT["catch"], "non-cutting"),
    ]
    rough_d = (BAR_D + PLUG_OD) / 2
    plug = [
        ("bar feed, collet", NONCUT["bar_feed"], "non-cutting"),
        ("face", t_radial(*c["turn"], r0), "turn and face"),
        ("rough OD 20 -> 13.2 (2 passes x 12 mm)", t_turn(*c["rough"], BAR_D, 12.0) + t_turn(*c["rough"], rough_d,
                                                                                               12.0),
         "turn and face"),
        ("finish OD 12.73, 15 deg lead-in, top chamfer", t_turn(*c["turn"], PLUG_OD, 12.0) + NONCUT["chamfer"],
         "turn and face"),
        ("vent 1.59 through", t_drill(*c["vent"], VENT_D, C.PLUG_L + 1.5, 1.5 if metal == "Al" else 1.0),
         "vent (plug)"),
        ("part off, chamfering the top", t_radial(*c["part"], PLUG_OD / 2) + NONCUT["chamfer"], "part off"),
        ("4 indexes, 4 rapids", 4 * NONCUT["index"] + 4 * NONCUT["rapid"], "non-cutting"),
        ("catch, onto the belt", NONCUT["catch"], "non-cutting"),
    ]
    return {"cup": [(n, round(t, 2), k) for n, t, k in cup], "plug": [(n, round(t, 2), k) for n, t, k in plug]}


def pair_seconds(metal: str) -> float:
    cy = cycle(metal)
    return sum(t for _, t, _ in cy["cup"]) + sum(t for _, t, _ in cy["plug"])


# ------------------------------------------------------------------------------------------------ the cell's day
# The arm's work per pair, from the clip's moves at the same speeds (est.): pick at the upender, blow off, into the
# basket (cup and plug each); basket to weigh module, gauge and rack (each); the basket's six transfers shared by its
# four pairs; the cassette's lid shared by eight.
ARM = dict(load_part=16.0, unload_part=32.0, basket_moves=48.0, lid=15.0)
CLEAN = dict(wash_min=5.0, rinse_min=2.0, dry_min=10.0, pairs_per_basket=4)     # DESY: 3-6 x 5 min; dryer est.
WEIGH_S, GAUGE_S = 5.0, 3.0      # settle (A&D: <= 1.3 s at 0.1 mg; with the shield's motion est.), one-shot gauge


def arm_seconds_per_pair() -> float:
    return (2 * ARM["load_part"] + 2 * ARM["unload_part"] + ARM["basket_moves"] / CLEAN["pairs_per_basket"]
            + ARM["lid"] / 8.0)


def capacity(al_share: float = 0.5) -> dict:
    lathe_s = al_share * pair_seconds("Al") + (1 - al_share) * pair_seconds("Cu")
    baskets = DEMAND / CLEAN["pairs_per_basket"]
    hours = {
        "lathe": DEMAND * lathe_s / 3600.0,
        "arm (UR10e)": DEMAND * arm_seconds_per_pair() / 3600.0,
        "wash vessel": baskets * CLEAN["wash_min"] / 60.0,
        "rinse vessel": baskets * CLEAN["rinse_min"] / 60.0,
        "vacuum dryer": baskets * CLEAN["dry_min"] / 60.0,
        "weigh module": DEMAND * 2 * WEIGH_S / 3600.0,
        "dimension gauge": DEMAND * 2 * GAUGE_S / 3600.0,
    }
    per_pair = {"lathe": lathe_s, "arm (UR10e)": arm_seconds_per_pair(),
                "vacuum dryer": CLEAN["dry_min"] * 60.0 / CLEAN["pairs_per_basket"]}
    limit = max(per_pair, key=per_pair.get)
    return dict(al_share=al_share, demand_pairs_per_day=DEMAND, hours_per_day={k: round(v, 2) for k, v in
                                                                             hours.items()},
                pair_seconds={"Al": round(pair_seconds("Al"), 1), "Cu": round(pair_seconds("Cu"), 1),
                              "mix": round(lathe_s, 1)},
                ceiling_pairs={"8 h": round(8 * 3600 / per_pair[limit]), "24 h": round(24 * 3600 / per_pair[limit])},
                limiting=limit)


# ------------------------------------------------------------------------------------------------ material and cost
def bar_per_pair() -> dict:
    """mm and g of bar per cup-and-plug pair: cup + plug + two parting grooves + two facings, the remnant shared."""
    used = C.SLUG_L + C.PLUG_L + 2 * 3.0 + 2 * 1.0
    per_bar = int((BAR_L - REMNANT) // used)
    mm = BAR_L / per_bar
    cm3 = math.pi / 4 * (BAR_D / 10) ** 2 * mm / 10
    v = C.volumes()
    out = dict(mm_used=round(used, 1), pairs_per_bar=per_bar, mm_per_pair=round(mm, 1))
    for m in ("Al", "Cu"):
        part = (v["cup"] + v["plug"]) * C.RHO[m]
        bar = cm3 * C.RHO[m]
        out[m] = dict(bar_g=round(bar, 1), parts_g=round(part, 1), chips_g=round(bar - part, 1),
                      yield_pct=round(100 * part / bar, 1))
    return out


CAPEX = [   # (item, low, high, source or "est.")
    ("Haas ST-10 turning centre", 64995, 64995, "Haas list, verified 2026-10-02"),
    ("Haas Bar Feeder V2 (4 ft bars)", 12000, 20000, "est.; Haas price not found"),
    ("auto door, parts catcher, belt and upender, tool probe", 10000, 15000, "est."),
    ("alcohol MQL unit and mist collector", 6000, 10000, "est."),
    ("UR10e / UR12e", 50818, 52674, "distributor listings, 2026"),
    ("Robotiq 2F-85 and wrist camera", 5000, 7000, "est."),
    ("pedestal, benches, fence, light curtain", 10000, 18000, "est."),
    ("two Elmasonic P 60 H baths", 3998, 6722, "US$1,999-3,361 each"),
    ("IPA vessels, lids, actuators, slot hood, duct", 4000, 8000, "est."),
    ("vacuum dryer: heated pot, lid actuator, chemistry pump, condenser", 8000, 14000, "est.; BINDER VDL 23 "
                                                                                     "(ATEX inside) $16,927-19,000"),
    ("A&D AD-4212C-301 + motorised draft shield", 7737, 9737, "$6,736.50 + est. $1-3k"),
    ("dimension gauge: Keyence IM-8000 class", 18000, 45000, "IM-8005 ~$45k (aggregator, unverified); "
                                                             "Mitutoyo LSM-9506 $12,924 + air plug est. $5k"),
    ("integration, programming, risk assessment", 30000, 50000, "est."),
]
PRICE = {"Al": (144.0, 1180.0), "Cu": (42.0, 42.0)}      # US$/kg, SOURCES["price_al"], ["price_cu"] (the PR's 5N case)

# Bar by grade, US$/kg low-high, as published (notes/machining_material.md; every price, with its page, in
# out/machining_prices.json; accessed 2026-11-22). No 25-100 kg price for 4N-5N Ø20 bar is published: bulk needs quotes.
GRADES = {
    "Al": {
        "99.7 % (1070A/1080A bar)": (8.0, 15.0, "est.: no list price found; P1020 delivered in the US is $5.3-5.5/kg "
                                                 "(LME $3.10 + Midwest premium) before drawing and the stockist"),
        "4N, 99.99 %": (141.0, 406.0, "HPA: Ø127-150 mm billet $141-146/kg (to be drawn to Ø20, quote) to Ø22 x "
                                      "540 mm rod $406/kg; China 4N ingot $3.95/kg (SMM, 20 Nov 2026)"),
        "4N6, 99.996 %": (248.0, 340.0, "HPA Ø50 rod $248-340/kg, no thinner stock; China 4N6 ingot $4.08/kg"),
        "5N, 99.999 %": (141.0, 1175.0, "HPA Ø150 mm billet $141/kg to Ø25 x 305 mm rod $1,175/kg; Thermo Ø22 rod "
                                        "$3,020/kg"),
    },
    "Cu": {
        "C10100 OFE (4N)": (39.0, 65.0, "Ø20 C101 $39/kg (1st Choice, UK, 3 m); 3/4 in C101 $52/kg (McMaster "
                                        "8965K72, 6 ft $241.10) and $65/kg (OnlineMetals, 12 ft $612.56), both read in "
                                        "a browser through the CubXL Pi"),
        "4N5, 99.995 %": (940.0, 1141.0, "Thermo Ø25.4 mm rod $940/kg; lab catalogues only"),
        "5N, 99.999 %": (1202.0, 1629.0, "Thermo 5N rod Ø9.5-19 mm; China 5N cathode-class $17.89/kg (SMM)"),
    },
}
# The grades the cups should be (notes/machining_material.md): 4N Al as the clean baseline (99.7 % when a run copies a
# commercial alloy; 5N only with Si and Mg of matching purity), and OFE copper, which is Grade A cathode cast without
# oxygen.
RECOMMENDED = {"Al": "4N, 99.99 %", "Cu": "C10100 OFE (4N)"}


def material_by_grade(al_share: float = 0.5) -> dict:
    """US$ a pair and a year of bar for each grade (94 mm of Ø20 bar a pair; half the pairs Al by default)."""
    bp = bar_per_pair()
    out = {}
    for m, gs in GRADES.items():
        share = al_share if m == "Al" else 1 - al_share
        kg_year = DEMAND * 365 * share * bp[m]["bar_g"] / 1000
        out[m] = {"bar_kg_per_year": round(kg_year), "grades": {
            g: dict(usd_per_kg=(lo, hi), per_pair_usd=(round(bp[m]["bar_g"] / 1000 * lo, 2),
                                                        round(bp[m]["bar_g"] / 1000 * hi, 2)),
                    per_year_usd=(round(kg_year * lo, -2), round(kg_year * hi, -2)), source=src)
            for g, (lo, hi, src) in gs.items()}, "recommended": RECOMMENDED[m]}
    return out


def costs(al_share: float = 0.5) -> dict:
    lo = sum(a for _, a, _, _ in CAPEX)
    hi = sum(b for _, _, b, _ in CAPEX)
    pairs_year = DEMAND * 365.0
    years = 7.0
    bp = bar_per_pair()
    per_pair = {
        "capital, 7 years straight-line": ((lo + hi) / 2) / years / pairs_year,
        "maintenance, 3 %/yr of capital": 0.03 * (lo + hi) / 2 / pairs_year,
        "tools (PCD and uncoated carbide, one set per metal)": 0.55,              # est. $0.30-0.80
        "IPA, about 1.1 L a day at $15-30/L": 1.1 * 22.5 / DEMAND,
        "spent IPA and fines to hazardous waste, $5/L": 1.1 * 5.0 / DEMAND,
        "power, about 17 kWh a day at $0.10": 17 * 0.10 / DEMAND,
        "labour, 0.15 FTE at $80k loaded": 0.15 * 80000 / pairs_year,
    }
    mat = {m: tuple(round(bp[m]["bar_g"] / 1000 * p, 2) for p in PRICE[m]) for m in ("Al", "Cu")}
    year_mat = {m: tuple(round(DEMAND * 365 * (al_share if m == "Al" else 1 - al_share) * bp[m]["bar_g"] / 1000 * p)
                         for p in PRICE[m]) for m in ("Al", "Cu")}
    return dict(capex_usd=(round(lo), round(hi)), capex_items=[dict(item=i, low=a, high=b, source=s)
                                                               for i, a, b, s in CAPEX],
                per_pair_ex_material_usd={k: round(v, 2) for k, v in per_pair.items()},
                per_pair_ex_material_total_usd=round(sum(per_pair.values()), 2),
                material_per_pair_usd=mat, material_per_year_usd=year_mat, pairs_per_year=round(pairs_year))


# ------------------------------------------------------------------------------------------------ charts
SERIES = ["turn and face", "drill and bore", "vent (plug)", "part off", "non-cutting"]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]     # dataviz reference palette, slots 1-5
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c9c8c2")
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="x", color="#e6e5df", lw=0.8)
    ax.set_axisbelow(True)


def plot_cycle(path=OUT / "machining_cycle.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [("Al", "cup"), ("Al", "plug"), ("Cu", "cup"), ("Cu", "plug")]
    names = {"Al": "5N Al", "Cu": "OFE Cu"}
    fig, ax = plt.subplots(figsize=(9.6, 3.9), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, (m, part) in enumerate(rows):
        ops = cycle(m)[part]
        left = 0.0
        for s, col in zip(SERIES, COLORS):
            w = sum(t for _, t, k in ops if k == s)
            if w <= 0:
                continue
            ax.barh(i, w - 0.25, left=left, height=0.56, color=col, edgecolor=SURFACE, linewidth=0)
            left += w
        ax.text(left + 0.8, i, f"{left:.0f} s", va="center", ha="left", fontsize=9, color=INK)
    ax.set_yticks(range(len(rows)), [f"{names[m]} {p}" for m, p in rows], color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("seconds on the lathe", color=INK2, fontsize=9)
    _style(ax)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORS]
    ax.legend(handles, SERIES, ncol=5, frameon=False, fontsize=8.5, loc="lower left", bbox_to_anchor=(0.0, 1.0),
              labelcolor=INK2, handlelength=1.2, columnspacing=1.2)
    ax.set_title("A cup and its plug from Ø20 mm bar on the bar-fed lathe: one pair takes "
                 f"{pair_seconds('Al'):.0f} s in 5N Al, {pair_seconds('Cu'):.0f} s in OFE Cu",
                 loc="left", fontsize=10.5, color=INK, pad=26)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def plot_day(path=OUT / "machining_day.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cap = capacity()
    h = cap["hours_per_day"]
    keys = list(h)
    fig, ax = plt.subplots(figsize=(9.6, 3.7), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.barh(range(len(keys)), [h[k] for k in keys], height=0.56, color=COLORS[0])
    for i, k in enumerate(keys):
        ax.text(h[k] + 0.08, i, f"{h[k]:.1f} h", va="center", fontsize=9, color=INK)
    ax.axvline(8.0, color=INK2, lw=1.0, ls=(0, (4, 3)))
    ax.text(8.0, -0.75, "one 8 h shift", fontsize=8.5, color=INK2, ha="center")
    ax.set_yticks(range(len(keys)), keys, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 9.0)
    ax.set_xlabel("hours a day each resource is busy at 67 cups and plugs a day (half Al, half Cu)", color=INK2,
                  fontsize=9)
    _style(ax)
    ax.set_title(f"Nothing in the cell is near full: the {cap['limiting']} would limit it at about "
                 f"{cap['ceiling_pairs']['8 h']} pairs a shift", loc="left", fontsize=10.5, color=INK, pad=14)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


# ------------------------------------------------------------------------------------------------ the floor
# The cell's arm pedestal on the lab floor: between the Instron 68SC-2 (x -4540..-4060) and MiR charger 0 (x
# -1811..-1189) on the south row, whose front is y -6238 (out/tray_plan.json). The cell's front zone is 2.2 m wide
# there; behind the row's machines (y < -6873) the lathe and its bar feeder have the floor to themselves.
FORM_STYLE = {"shot/pellet": ("#2a78d6", "o"), "powder": ("#eb6834", "s"), "rod": ("#1baf7a", "^"),
              "ingot/block/plate": ("#eda100", "D"), "wire": ("#e87ba4", "X")}       # colour and marker: never colour alone
PURITY_ORDER = ["3N", "3N5", "4N", "4N5", "5N", "5N5", "6N"]


def plot_prices(path=OUT / "machining_prices.png"):
    """Every published price (out/machining_prices.json) by purity and form, per kg on a log scale, against the
    commodity metal, and the bar the cups would be cut from."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = json.loads((OUT / "machining_prices.json").read_text())
    import numpy as np
    rng = np.random.default_rng(1)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    refs = {"Al": [(3.10, "LME aluminium, 99.7 %"), (3.95, "4N ingot, China (SMM)")],
            "Cu": [(12.47, "LME copper, Grade A"), (17.89, "5N copper, China (SMM)")]}
    for ax, metal, name in ((axes[0], "Al", "Aluminium"), (axes[1], "Cu", "Copper")):
        for form, (col, mk) in FORM_STYLE.items():
            pts = [q for q in d["points"] if q["metal"] == metal and q["form"] == form and q.get("verified_on_page")
                   and not q.get("marketplace") and q.get("purity_group", q.get("purity_class")) in PURITY_ORDER]
            if not pts:
                continue
            x = np.array([PURITY_ORDER.index(q.get("purity_group", q.get("purity_class"))) for q in pts], float)
            x += rng.uniform(-0.22, 0.22, len(x)) + 0.0
            y = [q["price_per_kg_usd"] for q in pts]
            ax.scatter(x, y, s=34, color=col, marker=mk, edgecolor="#fcfcfb", linewidth=0.8, label=form, zorder=3)
        for k, (v, lab) in enumerate(refs[metal]):           # the lower line labelled under it, the upper over it
            ax.axhline(v, color="#7a7a78", lw=1.0, ls="--", zorder=1)
            ax.text(len(PURITY_ORDER) - 0.55, v * (0.88 if k == 0 else 1.13), lab, ha="right",
                    va="top" if k == 0 else "bottom", fontsize=8, color="#555553")
        ax.set_yscale("log")
        ax.set_xticks(range(len(PURITY_ORDER)))
        ax.set_xticklabels(PURITY_ORDER)
        ax.set_xlim(-0.6, len(PURITY_ORDER) - 0.4)
        ax.set_title(name, fontsize=11)
        ax.grid(axis="y", color="#e6e6e3", lw=0.6, which="major")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel("purity (4N5 includes HPA's 99.996 %)")
    axes[0].set_ylabel("US$ per kg, published list price (log)")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], ls="", marker=mk, color=col, markeredgecolor="#fcfcfb", markersize=7, label=form)
               for form, (col, mk) in FORM_STYLE.items()]
    axes[0].legend(handles=handles, title="form", fontsize=8, title_fontsize=8, loc="upper left", frameon=False)
    n = sum(1 for q in d["points"] if q.get("verified_on_page") and not q.get("marketplace"))
    fig.suptitle(f"What Al and Cu cost by purity and form: {n} prices read on the vendors' pages, 2026-11-22",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


# Where the cell stands on the lab's floor plan (setup_lab.FLOOR_PLAN["machining"], warehouse.py's frame): x, y of the
# cell's origin (the arm's pedestal), its turn about z, and its MiR250 dock (x, y, heading).
# Round 16 (#303; PR #371's check of 2026-11-26: "Give the machining cell a place on the floor that doesn't take unit 3's
# charger"; notes/lab_r16.md): south of the south row, front to the north, behind the 68SC-2, unit 3's charger and
# charger 0, on the x it had before. Its MiR250 has a way in of its own: from the aisle down the row's west end, between
# the Instron 68FM-100 and the EOS M 400-4's strip, then east along a corridor behind the row, onto its dock line, and
# backed in from the west, its target post beyond its back end. The numbers, from out/tray_plan.json (round 15) and
# ISO 3691-4's 0.5 m beside a driverless vehicle's path:
#   corridor (the dock line): y -8081 = the 68FM-100's back (y -7291) - 500 - 290 (half a MiR250's width)
#   the cell's front (fence):  y -8451 = the dock line - 290 - 80 (docked 80 mm off the front, as at every dock)
#   the cell's origin:         y -9401 = the front - 950 (FRONT_Y in the cell's frame)
#   the lane down the west end: x -7977 = the 68FM-100's west side (x -7187) - 500 - 290
# Until round 15 the cell's front stood on the row's face line (y -7188 here, dock (-2935, -5868)), in what is now
# floor-cleaning unit 3's charger bay (floor_cleaning.BAY; notes/lab_r15.md).
FLOOR = dict(x=-2935.0, y=-9401.0, turn=0.0, dock=(-2935.0, -8081.0, 180.0),
             lane_x=-7977.0,                       # the MiR's centre line down the west end
             corner=(-7977.0, -8081.0),            # where it turns from that lane onto the corridor (a pivot spot)
             target=(-2935.0 + 650.0, -8451.0 + 25.0 + 150.0))   # beyond the docked MiR's back end, 150 mm off the
#                                                    front's light-curtain posts (25 mm proud of the fence's line)


def cell_rects() -> list[tuple[str, tuple, str]]:
    """(label, (x0, x1, y0, y1) on the floor, colour) of the cell's parts, from machining_cell's layout."""
    import machining_cell as M
    L = M.LATHE
    X, Y = FLOOR["x"], FLOOR["y"]
    r = [("fence", (-1100, 1100, L["y1"] + 10, M.FRONT_Y), "none"),
         ("lathe (the Haas ST-10 as measured: conveyor at the left end, electrical cabinet behind; its pendant "
          "hangs over the west bench)", (L["x0"], L["x1"], L["y1"] - L["D"], M.Y_FRONT), "#9aa6b5"),
         ("bar feeder, 4 ft bars", (L["x1"], L["x1"] + L["loader_l"], M.Y_FRONT - L["loader_w"], M.Y_FRONT),
          "#b9c2cc"),
         ("chip bins: Al under the conveyor's head, Cu behind it",
          (M.X_HEAD - M.ST10["conv_x1"] - 40, M.X_HEAD - M.ST10["conv_x1"] + M.ST10["conv_head"] + 40,
           M.Y_FRONT - 1120, M.Y_FRONT - 80), "#d9d2c0"),
         ("west bench: blow-off, basket, two baths, vacuum dryer", (-1080, -590, -700, 760), "#e6e2d6"),
         ("east bench: weigh module, dimension gauge, cassette lid", (550, 1080, -700, 760), "#e6e2d6"),
         ("north bench: the cassette (charge rack), under the front window", (-590, 550, 620, 940), "#e6e2d6")]
    return [(n, (x0 + X, x1 + X, y0 + Y, y1 + Y), c) for n, (x0, x1, y0, y1), c in r]


def way_in(fl: dict | None = None) -> dict:
    """What setup_lab's fit doesn't check of the cell's MiR250 route (it checks the dock, its pivot spot on the dock line
    and the approach from there): the lane from the aisle down the row's west end to the corner, the turn there, and the
    corridor from the corner to the dock's pivot spot (the MiR's centre; the turns at either end cover its ends). Each
    against every plan rectangle, target post foot and docked MiR250 in out/tray_plan.json (the cell's own as one
    rectangle) -> the least gap of each, mm, along x or y, and its neighbour (negative: they overlap). The lane and the
    corridor are a MiR250's body (580 mm wide); ISO 3691-4 wants 500 mm more on each side where people walk."""
    fl = fl or json.loads((OUT / "tray_plan.json").read_text())["floor"]
    Lm, Wm, r_turn = 800.0, 580.0, 499.0                  # props.MIR; turning on the spot with its Class D unit
    lx, (cx, cy) = FLOOR["lane_x"], FLOOR["corner"]
    dock = fl.get("docks", {}).get("machining", {})
    piv = (dock.get("pivot") or [FLOOR["dock"][0] - 2525.0, FLOOR["dock"][1]])[0]
    a = fl["aisle_mm"]
    obst = {k: tuple(r) for k, r in fl["machines"].items()}
    for k, d in fl.get("docks", {}).items():
        tx, ty = d["target_post"]
        obst[f"post {k}"] = (tx - 150, tx + 150, ty - 150, ty + 150)
        if k != "machining":
            x, y, _ = d["dock"]
            obst[f"docked MiR {k}"] = (x - Lm / 2, x + Lm / 2, y - Wm / 2, y + Wm / 2)

    def gap(r, q):                                      # along x or y, whichever is larger (a lower bound)
        return max(q[0] - r[1], r[0] - q[1], q[2] - r[3], r[2] - q[3])

    def gap_c(c, r, q):
        dx, dy = max(q[0] - c[0], 0.0, c[0] - q[1]), max(q[2] - c[1], 0.0, c[1] - q[3])
        return math.hypot(dx, dy) - r
    legs = {"lane down the west end": ("rect", (lx - Wm / 2, lx + Wm / 2, cy, a[2])),
            "turn at the corner": ("circle", ((cx, cy), r_turn)),
            "corridor to the pivot spot": ("rect", (cx, piv, cy - Wm / 2, cy + Wm / 2))}
    out = {}
    for leg, (kind, geo) in legs.items():
        gs = {k: (gap(geo, q) if kind == "rect" else gap_c(*geo, q)) for k, q in obst.items()}
        near = sorted(gs, key=gs.get)[:3]
        out[leg] = dict(geometry=[round(v) for v in (geo if kind == "rect" else (*geo[0], geo[1]))],
                        nearest=[(k, round(gs[k])) for k in near], clear=bool(gs[near[0]] > 0.0))
    return out


def plot_floor(path=OUT / "machining_floor.png"):
    """The cell where it stands (FLOOR), its parts, its MiR250's way in from the aisle (the lane down the row's west
    end, the corridor behind the row, the pivot spots, the dock and its target post), on out/tray_plan.json's floor."""
    import textwrap
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    fl = json.loads((OUT / "tray_plan.json").read_text())["floor"]
    xl, yl = (-12300.0, 2700.0), (-12300.0, -2400.0)
    fig, ax = plt.subplots(figsize=(11.0, 7.9), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    a = fl["aisle_mm"]
    ax.add_patch(Rectangle((a[0], a[2]), a[1] - a[0], a[3] - a[2], fc="#fff6cf", ec="#d8b400", lw=0.8))
    ax.text(-10000, -2700, "aisle", fontsize=9, color="#8a7300", va="top")
    names = {"instron_floor": "Instron 68FM-100", "instron_small": "68SC-2", "fumehood": "fume hood",
             "charger0": "charger 0", "charger1": "charger 1", "charger2": "unit 3's\ncharger",
             "eos_m400": "EOS M 400-4", "repowder": "rePowder", "glovebox": "glovebox", "ded": "DED",
             "sieve_cell": "sieving cell", "vlm": "Shuttle 1"}
    for k, (x0, x1, y0, y1) in fl["machines"].items():
        if k == "machining":                       # the cell itself: drawn part by part below
            continue
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#d5d9de", ec="#6b7280", lw=0.7))
        vx0, vx1, vy0, vy1 = max(x0, xl[0]), min(x1, xl[1]), max(y0, yl[0]), min(y1, yl[1])   # the part in view
        if k in names and vx0 < vx1 and vy0 < vy1:
            inside = vx1 - vx0 > 1200 and vy1 - vy0 > 600
            ax.text((vx0 + vx1) / 2, (vy0 + vy1) / 2 if inside else y0 - 110, names[k], ha="center",
                    va="center" if inside else "top", fontsize=7, color=INK2, clip_on=True)
    Lm, Wm, iso = 800.0, 580.0, 500.0              # props.MIR; ISO 3691-4's 0.5 m each side of the path
    ins = fl["machines"]["instron_floor"]
    lx, (cx_, cy_) = FLOOR["lane_x"], FLOOR["corner"]
    dx, dy, _ = FLOOR["dock"]
    # the EOS M 400-4's clear strip, what the lane leaves it (r8_scale: 2.4 m or wider, in front of it to the aisle)
    eos = fl["machines"].get("eos_m400", (-11540, -7360, -11506, -9763))
    sx1 = lx - Wm / 2 - iso
    ax.add_patch(Rectangle((eos[0], eos[3]), sx1 - eos[0], a[2] - eos[3], fc="none", ec="#9a8f6a", lw=0.8,
                           hatch="///", alpha=0.5))
    ax.text((eos[0] + sx1) / 2, -7700, f"the EOS's clear strip\nto the aisle: {(sx1 - eos[0]) / 1000:.2f} m kept",
            ha="center", va="center", fontsize=7, color="#6b623f",
            bbox=dict(boxstyle="round,pad=0.25", fc=SURFACE, ec="none"))
    # the MiR's way in: the band its body sweeps, and ISO's 0.5 m beside it
    piv = fl.get("docks", {}).get("machining", {}).get("pivot") or [dx - 2525.0, dy]
    for (x0, x1, y0, y1), fc, al in (((lx - Wm / 2 - iso, lx + Wm / 2 + iso, cy_, a[2]), "#2e9c6a", 0.08),
                                     ((lx - Wm / 2, lx + Wm / 2, cy_, a[2]), "#2e9c6a", 0.18),
                                     ((lx, piv[0], cy_ - Wm / 2, cy_ + Wm / 2), "#2e9c6a", 0.18),
                                     ((lx, piv[0], cy_ + Wm / 2, cy_ + Wm / 2 + iso), "#2e9c6a", 0.08),
                                     ((piv[0], dx + Lm / 2, dy - Wm / 2, dy + Wm / 2), "#2e9c6a", 0.10)):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, alpha=al, ec="none"))
    r_turn = 499.0                                 # a MiR250 turning on the spot, its Class D unit on (safety.py)
    for c in ((cx_, cy_), tuple(piv)):
        ax.add_patch(Circle(c, r_turn, fc="none", ec="#2e9c6a", lw=0.8, ls=(0, (3, 2))))
    arw = dict(arrowstyle="->", color="#1f6f4c", lw=1.0)
    ax.annotate("", xy=(lx, cy_ + 650), xytext=(lx, a[2] - 150), arrowprops=arw)
    ax.annotate("", xy=(piv[0] - 560, cy_), xytext=(cx_ + 560, cy_), arrowprops=arw)
    ax.annotate("", xy=(dx + 120, dy), xytext=(piv[0] + 560, dy), arrowprops=dict(arw, ls="--"))
    ax.text(lx + Wm / 2 + iso + 120, -5900, "its MiR250's way in: down the west end,\n"
            f"{(ins[0] - lx - Wm / 2):.0f} mm off the 68FM-100", ha="left", va="top", fontsize=7, color="#1f6f4c")
    ax.text(cx_ + 700, cy_ - r_turn - 120, f"corridor behind the row,\n{(ins[2] - cy_ - Wm / 2):.0f} mm off the "
            "68FM-100's back", ha="center", va="top", fontsize=7, color="#1f6f4c")
    ax.text(piv[0] + 560, dy + 330, f"pivot, then\nbacked in {abs(piv[0] - dx):.0f} mm", ha="left", va="bottom",
            fontsize=7, color="#1f6f4c")
    # the cell
    key = []
    for i, (n, (x0, x1, y0, y1), c) in enumerate(cell_rects()):
        if n == "fence":
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#d8a400", lw=1.6, ls=(0, (5, 2))))
            continue
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=c, ec="#374151", lw=0.8))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, str(i), ha="center", va="center", fontsize=8, color=INK,
                fontweight="bold")
        key += textwrap.wrap(f"{i}  {n}", 66, subsequent_indent="     ")
    X, Y = FLOOR["x"], FLOOR["y"]
    ax.add_patch(Circle((X, Y), 1300, fc="none", ec=COLORS[0], lw=0.9, ls=(0, (3, 3))))
    ax.add_patch(Circle((X, Y), 140, fc=COLORS[0], ec="none"))
    ax.add_patch(Rectangle((dx - Lm / 2, dy - Wm / 2), Lm, Wm, fc="#2e9c6a", alpha=0.45, ec="#2e9c6a", lw=0.8))
    tx, ty = FLOOR["target"]
    ax.add_patch(Rectangle((tx - 150, ty - 150), 300, 300, fc="#222", ec="none"))
    ax.text(tx + 450, ty + 60, "MiR250 docked: its arm takes the cassette\nthrough the front window; "
            "its target post\n(black) beyond its back end", ha="left", va="center", fontsize=7, color="#1f6f4c")
    key += ["", "dashed yellow: the cell's fence;  dashed blue: the UR10e's 1.3 m reach",
            "green: the MiR250's way in (its body, and 0.5 m beside it);",
            "dashed circles: where it turns on the spot (499 mm)"]
    ax.text(0.985, 0.985, "\n".join(key), transform=ax.transAxes, ha="right", va="top", multialignment="left",
            fontsize=6.6, color=INK, bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#c9c8c2", lw=0.6))
    ax.set_aspect("equal")
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.set_xlabel("x, mm", fontsize=8, color=INK2)
    ax.set_ylabel("y, mm", fontsize=8, color=INK2)
    ax.tick_params(labelsize=7.5, colors=INK2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("The machining cell south of the south row, front to the north behind the 68SC-2 and the chargers;\n"
                 "its MiR250 comes down the row's west end and along a corridor behind the row (round 16)", loc="left",
                 fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def main():
    OUT.mkdir(exist_ok=True)
    rep = dict(
        demand_pairs_per_day=DEMAND,
        cycle={m: cycle(m) for m in ("Al", "Cu")},
        pair_seconds={m: round(pair_seconds(m), 1) for m in ("Al", "Cu")},
        capacity={str(s): capacity(s) for s in (0.0, 0.5, 1.0)},
        bar=bar_per_pair(),
        costs=costs(),
        floor=dict(FLOOR, cell=[dict(part=n, rect_mm=[round(v) for v in r]) for n, r, _ in cell_rects()],
                   way_in=way_in()),
        cutting_data=CUT, noncutting_s_est=NONCUT, arm_s_est=ARM, cleaning=CLEAN, sources=SOURCES,
        material_by_grade=material_by_grade(),
        note="Cutting times from the published data in SOURCES at the ST-10's 6,000 rpm; non-cutting times, the arm's "
             "times, tool and labour costs are estimates. The demand is PR #332's R11 (ten alloys a day).")
    (OUT / "machining.json").write_text(json.dumps(rep, indent=1) + "\n")
    for p in (plot_cycle(), plot_day(), plot_floor(), plot_prices()):
        print("wrote", p.relative_to(HERE))
    print(json.dumps(dict(pair_seconds=rep["pair_seconds"], capacity=rep["capacity"]["0.5"], bar=rep["bar"],
                          capex=rep["costs"]["capex_usd"], per_pair=rep["costs"]["per_pair_ex_material_total_usd"],
                          material=rep["costs"]["material_per_pair_usd"],
                          material_year=rep["costs"]["material_per_year_usd"]), indent=1))


if __name__ == "__main__":
    main()
