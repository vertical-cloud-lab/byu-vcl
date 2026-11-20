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
                "(about $144/kg); Advent 99.9995 % Ø20 x 500 mm $1,535 (about $3,500/kg)",
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
PRICE = {"Al": (144.0, 1180.0), "Cu": (42.0, 42.0)}      # US$/kg, SOURCES["price_al"], ["price_cu"]


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
FLOOR = dict(x=-2935.0, y=-6238.0 - 950.0, dock=(-2935.0, -5868.0, 180.0))


def cell_rects() -> list[tuple[str, tuple, str]]:
    """(label, (x0, x1, y0, y1) on the floor, colour) of the cell's parts, from machining_cell's layout."""
    import machining_cell as M
    L = M.LATHE
    X, Y = FLOOR["x"], FLOOR["y"]
    r = [("fence", (-1100, 1100, L["y1"] + 10, M.FRONT_Y), "none"),
         ("lathe (Haas ST-10 size, its chip conveyor at the left end)", (L["x0"], L["x1"], L["y1"] - L["D"], L["y1"]),
          "#9aa6b5"),
         ("bar feeder, 4 ft bars", (L["x1"], L["x1"] + L["loader_l"], M.SPIN_Y - L["loader_w"] / 2,
                                    M.SPIN_Y + L["loader_w"] / 2), "#b9c2cc"),
         ("chip bins: Al under the conveyor, Cu waiting", (L["x0"] - 560, L["x0"] - 60, M.SPIN_Y - 250,
                                                            M.SPIN_Y + 790), "#d9d2c0"),
         ("west bench: blow-off, basket, two baths, vacuum dryer", (-1080, -590, -700, 760), "#e6e2d6"),
         ("east bench: weigh module, dimension gauge, cassette lid", (550, 1080, -700, 760), "#e6e2d6"),
         ("north bench: the cassette (charge rack), under the front window", (-590, 550, 620, 940), "#e6e2d6")]
    return [(n, (x0 + X, x1 + X, y0 + Y, y1 + Y), c) for n, (x0, x1, y0, y1), c in r]


def plot_floor(path=OUT / "machining_floor.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    fl = json.loads((OUT / "tray_plan.json").read_text())["floor"]
    xl, yl = (-7600.0, 2600.0), (-10000.0, -2300.0)
    fig, ax = plt.subplots(figsize=(11.0, 7.4), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    a = fl["aisle_mm"]
    ax.add_patch(Rectangle((a[0], a[2]), a[1] - a[0], a[3] - a[2], fc="#fff6cf", ec="#d8b400", lw=0.8))
    ax.text(-7300, -3900, "aisle", fontsize=9, color="#8a7300")
    names = {"instron_floor": "Instron 68FM-100", "instron_small": "68SC-2", "fumehood": "fume hood",
             "charger0": "charger 0", "charger1": "charger 1"}
    for k, (x0, x1, y0, y1) in fl["machines"].items():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#d5d9de", ec="#6b7280", lw=0.7))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if k in names and xl[0] < cx < xl[1] and yl[0] < cy < yl[1]:
            ax.text(cx, y0 - 120, names[k], ha="center", va="top", fontsize=7, color=INK2, clip_on=True)
    key = []
    for i, (n, (x0, x1, y0, y1), c) in enumerate(cell_rects()):
        if n == "fence":
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#d8a400", lw=1.6, ls=(0, (5, 2))))
            continue
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=c, ec="#374151", lw=0.8))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, str(i), ha="center", va="center", fontsize=9, color=INK,
                fontweight="bold")
        key.append(f"{i}  {n}")
    X, Y = FLOOR["x"], FLOOR["y"]
    ax.add_patch(Circle((X, Y), 1300, fc="none", ec=COLORS[0], lw=0.9, ls=(0, (3, 3))))
    ax.add_patch(Circle((X, Y), 140, fc=COLORS[0], ec="none"))
    dx, dy, _ = FLOOR["dock"]
    ax.add_patch(Rectangle((dx - 445, dy - 290), 890, 580, fc="#2e9c6a", alpha=0.35, ec="#2e9c6a", lw=0.8))
    ax.text(dx + 520, dy + 120, "MiR250 docked: its arm takes the\ncassette through the front window",
            ha="left", va="center", fontsize=7, color="#1f6f4c")
    gap = (fl["machines"]["charger0"][0] - fl["machines"]["instron_small"][1])
    key += ["", "dashed yellow: the cell's fence;  dashed blue: the UR10e's 1.3 m reach",
            f"the front zone is 2.2 m wide: {gap:.0f} mm between the 68SC-2 and charger 0"]
    ax.text(0.47, 0.955, "\n".join(key), transform=ax.transAxes, ha="left", va="top", fontsize=7.2, color=INK,
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#c9c8c2", lw=0.6))
    ax.set_aspect("equal")
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.set_xlabel("x, mm", fontsize=8, color=INK2)
    ax.set_ylabel("y, mm", fontsize=8, color=INK2)
    ax.tick_params(labelsize=7.5, colors=INK2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("The machining cell on the south row: its front between the 68SC-2 and charger 0, "
                 "the lathe and bar feeder behind them", loc="left", fontsize=10, color=INK)
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
        floor=dict(FLOOR, cell=[dict(part=n, rect_mm=[round(v) for v in r]) for n, r, _ in cell_rects()]),
        cutting_data=CUT, noncutting_s_est=NONCUT, arm_s_est=ARM, cleaning=CLEAN, sources=SOURCES,
        note="Cutting times from the published data in SOURCES at the ST-10's 6,000 rpm; non-cutting times, the arm's "
             "times, tool and labour costs are estimates. The demand is PR #332's R11 (ten alloys a day).")
    (OUT / "machining.json").write_text(json.dumps(rep, indent=1) + "\n")
    for p in (plot_cycle(), plot_day(), plot_floor()):
        print("wrote", p.relative_to(HERE))
    print(json.dumps(dict(pair_seconds=rep["pair_seconds"], capacity=rep["capacity"]["0.5"], bar=rep["bar"],
                          capex=rep["costs"]["capex_usd"], per_pair=rep["costs"]["per_pair_ex_material_total_usd"],
                          material=rep["costs"]["material_per_pair_usd"],
                          material_year=rep["costs"]["material_per_year_usd"]), indent=1))


if __name__ == "__main__":
    main()
