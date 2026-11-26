"""Supply: what the lab buys, what it costs on a given day, and how long it takes to arrive.

**Commodity indices.** Each commodity's price follows a daily log process,

    d ln I = (mu - s^2/2) dt + s dW  +  jumps,

with ``s`` the annualized volatility of its USGS 2021-2025 price series (twin/usgs.py; a floor of 8 %), ``mu`` the
scenario's steady drift, and jumps of two kinds:

* **sporadic and temporary**: Poisson arrivals that lift the index and decay back with a half-life (the 2022
  episode: nickel +40 % on the LME squeeze, magnesium +115 %, silicon metal +64 %, lithium carbonate +440 % on annual
  averages, all back down by 2024);
* **stable and consistent**: steps that stay (aluminium +39 % and copper +13 % in 2025 under Section 232 tariffs;
  scandium oxide falling 10 % a year, 2021-2025).

Scenarios also stretch lead times and raise the chance of a stockout for the commodities they hit (China's export
controls: graphite, December 2023; seven rare earths including scandium, April 2025).

**Lab items.** A lab buys 5N rod, master alloys, coated plates, argon and services, not LME metal. Each item has a
price on day 0 (from the proposals' budgets, DAL's orders and #331, cited in ``CATALOGUE``), a pass-through exponent
to its commodity index (a 5N rod's price is mostly refining and machining, so it moves with about a fifth of the
metal's; a master alloy with most of it), an import share exposed to tariffs, a lognormal lead time, a minimum order,
and a hazmat class that forces ground shipping. ``Market.order`` charges the day's price and returns the arrival day.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from twin import usgs

YEAR = 365.0


@dataclass
class Item:
    key: str
    name: str
    unit: str
    price: float                     # USD per unit on day 0
    commodity: str | None = None     # USGS key ('Al', 'Sc', 'graphite', ...)
    passthrough: float = 0.3
    lead_days: float = 14.0          # median
    lead_gsd: float = 1.5
    moq: float = 1.0
    import_share: float = 0.0
    hazmat: str | None = None
    supplier: str = ""
    source: str = ""
    element: str | None = None       # the alloying element it supplies
    frac: float = 1.0                # mass fraction of that element in the item (master alloys)
    p_fail: float = 0.0              # chance the first channel fails (no supply, 'no source', a lapsed order)
    fail_days: float = 30.0          # how long until the lab learns it failed
    fallback_mult: float = 1.5       # price of the channel it falls back to, relative


# The catalogue. Day-0 prices and lead times are DAL's experience in 2026 (its procurement threads, read in full for
# this twin; aggregated and rounded here, with no vendor quote reproduced) or the proposals' budgets; "assumed"
# otherwise. What DAL found, and the model keeps:
#   * small lots cost 4-17x a 1-2 lb price and about 10x LME (Al rod $32-46/kg against $3/kg);
#   * the charges take additions as elemental powders, since no master alloy was ever bought or quoted (Al-2Sc and
#     Al-Er come from China under export licences): so scandium costs about $235 per gram, not the $1.5/g it costs
#     inside bulk Al-2Sc;
#   * cheap channels fail (a reseller that supplied none of 16 powders after a month, distributors with "no source")
#     and the fallback costs more: p_fail and fallback_mult;
#   * hazmat classes force ground shipping and add a fee.
# A git-ignored data/private/prices.json (key -> {"price": ..., "lead_days": ...}) overrides any line with private
# quotes the lab holds (load_private()).
CATALOGUE = [
    # ---- aluminium campaign feedstock (elemental additions, as DAL doses them into machined cups)
    Item("al_bar_hp", "Al rod for machined charge cups and plugs", "kg", 40.0, "Al", 0.2, 3, 1.5, 2, 0.3,
         None, "catalogue house", "DAL: 6063 rod $32-46/kg, delivered in 2 days; FLAIME: high-purity Al bar", "Al", 1.0),
    Item("si_lump", "Si powder", "kg", 120.0, "Si", 0.3, 10, 2.0, 0.25, 0.6, None, "catalogue house",
         "DAL: $118/kg (on hand); a distributor quote's ETA was 25 days", "Si", 1.0, 0.2, 30, 2.0),
    Item("mg_turnings", "Mg sticks (5 lb minimum)", "kg", 60.0, "Mg", 0.4, 14, 1.6, 2.3, 0.85, "4.3/4.2 (UN1418)",
         "metals distributor", "DAL: Mg powder unobtainable; sticks about $59/kg (5 lb min) or 3N pieces about "
         "$2,300/kg as the fallback; US Magnesium closed in 2025", "Mg", 1.0, 0.3, 30, 30.0),
    Item("cu_shot", "Cu powder", "kg", 200.0, "Cu", 0.3, 3, 1.5, 0.45, 0.4, None, "catalogue house",
         "DAL: about $200/kg list (44 um), $578/kg spherical", "Cu", 1.0, 0.1, 14, 2.9),
    Item("zn_shot", "Zn powder", "kg", 450.0, "Zn", 0.3, 30, 1.6, 0.1, 0.7, "4.3 (UN1436)", "specialty supplier",
         "DAL: about $450/kg (100 g lots); one distributor's lead was 46 days", "Zn", 1.0, 0.15, 46, 1.0),
    Item("al_mn20", "Mn powder", "kg", 350.0, "Mn", 0.5, 30, 1.8, 0.1, 1.0, None, "specialty supplier",
         "DAL: about $350/kg, 100 g lots, a lot without a certificate", "Mn", 1.0, 0.15, 30, 1.5),
    Item("al_cr20", "Cr powder", "kg", 650.0, "Cr", 0.5, 30, 1.8, 0.1, 0.8, None, "specialty supplier",
         "DAL: about $650/kg; one distributor's spherical Cr 13x that", "Cr", 1.0, 0.15, 30, 2.0),
    Item("al_zr10", "Zr powder (water-wet) or Al-10Zr master alloy", "kg", 900.0, "Zr", 0.4, 35, 1.8, 0.1, 0.6,
         "4.2 (water-wet)", "specialty supplier", "assumed: never bought by DAL; hazmat fees $100-300; Al-10Zr lists "
         "at about $60/kg but no supplier quoted the lab", "Zr", 1.0, 0.3, 30, 1.5),
    Item("al_ti10", "Ti powder", "kg", 650.0, "Ti", 0.5, 30, 1.8, 0.1, 0.6, "4.2 (UN2546)", "specialty supplier",
         "DAL: about $650/kg (200 g); 'no source' at a distributor in the target size", "Ti", 1.0, 0.25, 30, 1.0),
    Item("al_fe10", "Fe powder", "kg", 300.0, "Fe", 0.2, 10, 1.8, 0.25, 0.3, None, "catalogue house",
         "DAL: $190-490/kg (list and quote)", "Fe", 1.0, 0.15, 30, 1.5),
    Item("al_ni20", "Ni powder", "kg", 550.0, "Ni", 0.5, 10, 1.8, 0.1, 0.6, None, "catalogue house",
         "DAL: $440-690/kg", "Ni", 1.0, 0.15, 30, 1.3),
    Item("al_ce20", "Ce metal (ingot pieces)", "kg", 1500.0, "Ce", 0.4, 21, 1.8, 0.05, 1.0, None, "chemical supplier",
         "DAL: $650-3,400/kg list; an Al-Ce master alloy 'from $300', 3 weeks", "Ce", 1.0, 0.15, 21, 1.5),
    Item("al_sc2", "Sc metal (lab lots)", "kg", 235000.0, "Sc", 0.3, 28, 1.5, 0.005, 1.0, None, "specialty supplier",
         "DAL: about $235/g, 3-5 weeks (Al-2Sc master alloy is about $30/kg in bulk but needs a Chinese export licence "
         "and was discontinued at catalogue houses)", "Sc", 1.0, 0.2, 35, 1.0),
    Item("al_er10", "Er metal (lab lots)", "kg", 32000.0, "Er", 0.3, 28, 1.5, 0.025, 1.0, None, "specialty supplier",
         "DAL: about $31-32/g, 3-5 weeks; China's export-control suspension for Er lapsed on 2026-11-10", "Er", 1.0,
         0.2, 35, 1.0),
    Item("li_metal", "Al-5Li master alloy", "kg", 200.0, "Li", 0.5, 21, 1.8, 1.0, 0.8, "4.3", "metals distributor",
         "assumed (an Al-5Li listing in DAL; never bought)", "Li", 0.05, 0.3, 30, 2.0),
    Item("sn_shot", "Sn powder", "kg", 400.0, "Sn", 0.4, 30, 1.6, 0.1, 0.8, None, "specialty supplier",
         "DAL: about $400/kg (100 g)", "Sn", 1.0, 0.1, 30, 1.2),
    Item("alsi10mg_powder", "AlSi10Mg powder 15-45 um (baseline)", "kg", 194.0, "Al", 0.2, 5, 1.5, 1, 0.3,
         "4.3 (UN1396)", "powder reseller", "DAL: $194/kg paid (1 kg, Jan 2026); $135-145/kg at 10 kg", None, 1.0),
    # ---- copper campaign feedstock
    Item("cu_ofe_bar", "OFE copper bar C10100 for charge cups", "kg", 90.0, "Cu", 0.3, 3, 1.5, 2, 0.4, None,
         "metals distributor", "DAL: C10100 about $90/kg; bronze rod $88/kg, delivered in 2 days", "Cu", 1.0),
    Item("ni_pellet", "Ni rod or pellets", "kg", 440.0, "Ni", 0.5, 5, 1.8, 0.25, 0.6, None, "catalogue house",
         "DAL: Ni 200 rod about $441/kg; powder $689/kg", "Ni", 1.0, 0.1, 14, 1.5),
    Item("al_shot", "Al granules 99.7 % (Cu charges)", "kg", 43.0, "Al", 0.2, 2, 1.5, 0.45, 0.3, "4.3 (UN1396)",
         "powder maker", "DAL: $43/kg quoted, 1-2 days, ground only", "Al", 1.0),
    Item("fe_powder", "Fe powder", "kg", 300.0, "Fe", 0.2, 10, 1.8, 0.25, 0.3, None, "catalogue house",
         "DAL: $190-490/kg", "Fe", 1.0, 0.15, 30, 1.5),
    Item("mn_flake", "Mn powder", "kg", 350.0, "Mn", 0.5, 30, 1.8, 0.1, 1.0, None, "specialty supplier",
         "DAL: about $350/kg", "Mn", 1.0, 0.15, 30, 1.5),
    Item("cr_powder", "Cr powder", "kg", 650.0, "Cr", 0.5, 30, 1.8, 0.1, 0.8, None, "specialty supplier",
         "DAL: about $650/kg", "Cr", 1.0, 0.15, 30, 2.0),
    Item("si_lump_cu", "Si powder (Cu charges)", "kg", 120.0, "Si", 0.3, 10, 2.0, 0.25, 0.6, None,
         "catalogue house", "DAL", "Si", 1.0, 0.2, 30, 2.0),
    Item("nb_powder", "Nb powder", "kg", 500.0, "Nb", 0.4, 30, 1.8, 0.1, 1.0, None, "specialty supplier", "assumed",
         "Nb", 1.0, 0.2, 30, 1.5),
    Item("ti_sponge", "Ti powder (Cu charges)", "kg", 650.0, "Ti", 0.5, 30, 1.8, 0.1, 1.0, "4.2 (UN2546)",
         "specialty supplier", "DAL", "Ti", 1.0, 0.25, 30, 1.0),
    Item("cuni_powder", "Commercial 70-30 Cu-Ni powder 45-105 um (baseline)", "kg", 750.0, "Ni", 0.2, 35, 1.6, 2,
         0.5, None, "powder maker", "ONR README: at least 2 kg, $1,500 then $750 (quote needed)", None, 1.0),
    Item("nab_powder", "Commercial NAB powder 45-105 um (baseline)", "kg", 750.0, "Cu", 0.2, 35, 1.6, 2, 0.5, None,
         "powder maker", "ONR README", None, 1.0),
    # ---- consumables
    Item("argon", "Argon cylinder (UHP)", "cylinder", 90.0, None, 0.0, 3, 1.3, 1, 0.0, None, "local gas supplier",
         "ONR budget: $90 a cylinder; DAL: an Al run takes 100-160 psi of 2,000, a Cu run 300-350"),
    Item("graphite_crucible", "Graphite crucible for the rePOWDER", "each", 450.0, "graphite", 0.3, 49, 1.8, 1, 1.0,
         None, "AMAZEMET (Poland)", "assumed; AMAZEMET's spares have never been priced in DAL"),
    Item("bn_spray", "Boron nitride spray (13 oz)", "can", 53.0, None, 0.0, 3, 1.4, 1, 0.0, "UN1950 limited qty",
         "catalogue house", "DAL: $52.73 paid; a coat each run, about 1 g"),
    Item("cc_plate", "Atomizer plate (Mo for Al, W-coated C/C for Cu)", "each", 350.0, "graphite", 0.2, 56, 1.8, 1,
         1.0, None, "AMAZEMET (Poland)", "assumed price; DAL: a Mo plate lasts 4-6 Al runs, a W-dipped plate about "
         "one Cu run; only AMAZEMET sells them"),
    Item("bn_nozzle", "hBN nozzle and sealing rod", "each", 120.0, None, 0.0, 49, 1.8, 1, 1.0, None,
         "AMAZEMET (Poland)", "assumed; DAL: replaced every Cu run"),
    Item("build_plate", "LPBF build plate (55 mm kit)", "each", 80.0, "Al", 0.1, 14, 1.5, 1, 0.0, None,
         "machined in house", "assumed"),
    Item("ded_substrate", "Cast NAB / wrought C71500 plate (repair substrates)", "each", 150.0, "Cu", 0.3, 3, 1.5,
         1, 0.3, None, "metals distributor", "ONR README: $1,500/yr in all (guess); DAL: 1-day delivery of C71500"),
]
ITEMS = {i.key: i for i in CATALOGUE}

# which item supplies each alloying element in each campaign's charges
CHARGE_SOURCE = {
    "flaime_al": {"Al": "al_bar_hp", "Si": "si_lump", "Mg": "mg_turnings", "Cu": "cu_shot", "Zn": "zn_shot",
                  "Mn": "al_mn20", "Cr": "al_cr20", "Zr": "al_zr10", "Ti": "al_ti10", "Fe": "al_fe10",
                  "Ni": "al_ni20", "Ce": "al_ce20", "Sc": "al_sc2", "Er": "al_er10", "Li": "li_metal", "Sn": "sn_shot"},
    "onr_cu": {"Cu": "cu_ofe_bar", "Ni": "ni_pellet", "Al": "al_shot", "Fe": "fe_powder", "Mn": "mn_flake",
               "Cr": "cr_powder", "Si": "si_lump_cu", "Nb": "nb_powder", "Ti": "ti_sponge"},
}


def charge_bill(campaign: str, comp: dict, mass_kg: float) -> dict:
    """kg of each catalogue item for a charge of this composition. A master alloy brings Al with it, which comes off
    the Al bar."""
    src = CHARGE_SOURCE[campaign]
    base = "Al" if campaign == "flaime_al" else "Cu"
    bill = {}
    base_from_masters = 0.0
    for el, w in comp.items():
        if el == base or w <= 0:
            continue
        it = ITEMS[src[el]]
        m = mass_kg * w / 100.0 / it.frac
        bill[it.key] = bill.get(it.key, 0.0) + m
        base_from_masters += m * (1 - it.frac)
    bill[src[base]] = max(mass_kg * comp.get(base, 0) / 100.0 - base_from_masters, 0.0)
    return bill


# ----------------------------------------------------------------------------------------------------------- scenarios
@dataclass
class Shock:
    commodities: tuple            # USGS keys, or ('*',) for all
    rate_per_year: float = 0.0    # Poisson arrivals (sporadic)
    size_mean: float = 0.3        # log-size of the jump
    size_sd: float = 0.15
    half_life_days: float | None = 240.0      # None: permanent
    lead_mult: float = 1.0
    stockout_p: float = 0.0
    at_day: float | None = None   # a scheduled step instead of Poisson arrivals
    note: str = ""


@dataclass
class Scenario:
    key: str
    note: str
    drift: dict = field(default_factory=dict)     # commodity -> mu per year ('*' default)
    vol_mult: float = 1.0
    shocks: list = field(default_factory=list)
    service_drift: float = 0.03                   # per year on services, labour and consumables without a commodity
    import_tariff: float = 0.0                    # applied to the import share of lab items (permanent, from day 0)


SCENARIOS = {
    "calm": Scenario("calm", "prices flat, half the historical volatility, no shocks, quoted lead times",
                     vol_mult=0.5, service_drift=0.0),
    "historical": Scenario(
        "historical", "USGS 2021-2025 volatility and the 2022-type sporadic shocks (energy, LME squeeze) at the rate "
        "they came: about one every 6-7 years for any one metal",
        drift={"Sc": -0.10},
        shocks=[Shock(("Ni", "Mg", "Si", "Mn", "Cr", "Zn", "Al", "Li"), 0.15, 0.35, 0.2, 240.0, 1.5, 0.05,
                      note="2022-type: energy and sanctions; decays with a 240-day half-life")]),
    "tariffs": Scenario(
        "tariffs", "historical, plus a permanent tariff regime: +25 % on the import share of every lab item from day "
        "0, aluminium +35 % and copper +15 % on top (2025's Section 232 steps), lead times 1.3x on imports",
        drift={"Sc": -0.10}, import_tariff=0.25,
        shocks=[Shock(("Al",), 0, 0.30, 0.0, None, 1.3, 0.0, at_day=0.0, note="Section 232 aluminium"),
                Shock(("Cu",), 0, 0.14, 0.0, None, 1.3, 0.0, at_day=0.0, note="copper tariff"),
                Shock(("Ni", "Mg", "Si", "Mn", "Cr", "Zn", "Al", "Li"), 0.15, 0.35, 0.2, 240.0, 1.5, 0.05)]),
    "export_controls": Scenario(
        "export_controls", "historical, plus export controls on scandium, the rare earths and graphite (China, "
        "December 2023 and April 2025): a step of +70 % that decays over a year, lead times 3x and a 30 % chance "
        "that any order is backordered",
        drift={"Sc": -0.10},
        shocks=[Shock(("Sc", "Er", "Ce", "graphite"), 0, 0.53, 0.1, 365.0, 3.0, 0.30, at_day=30.0,
                      note="export licences"),
                Shock(("Ni", "Mg", "Si", "Mn", "Cr", "Zn", "Al", "Li"), 0.15, 0.35, 0.2, 240.0, 1.5, 0.05)]),
    "inflation": Scenario(
        "inflation", "historical, plus a steady +8 %/yr on every commodity and +6 %/yr on services and consumables",
        drift={"*": 0.08, "Sc": -0.02}, service_drift=0.06,
        shocks=[Shock(("Ni", "Mg", "Si", "Mn", "Cr", "Zn", "Al", "Li"), 0.15, 0.35, 0.2, 240.0, 1.5, 0.05)]),
}

COMMODITIES = list(usgs.ELEMENTS) + ["graphite"]


def annual_vol(key: str) -> float:
    r = usgs.log_returns(key)
    return max(float(np.std(r, ddof=1)) if len(r) >= 2 else 0.15, 0.08)


class Market:
    """Daily commodity indices (1.0 on day 0), lead-time multipliers and stockout chances over a horizon, all drawn
    up front from the scenario and the seed, so two campaigns in one run face the same market."""

    def __init__(self, scenario: str | Scenario = "historical", seed: int = 0, days: int = 1100):
        self.sc = SCENARIOS[scenario] if isinstance(scenario, str) else scenario
        self.days = days
        rng = np.random.default_rng(10_000 + seed)
        self.rng = np.random.default_rng(20_000 + seed)
        t = np.arange(days + 1)
        self.log_index, self.lead_mult, self.stockout, self.events = {}, {}, {}, []
        for c in COMMODITIES:
            s = annual_vol(c) * self.sc.vol_mult
            mu = self.sc.drift.get(c, self.sc.drift.get("*", 0.0))
            dW = rng.normal(0, 1, days) * s / math.sqrt(YEAR)
            x = np.concatenate([[0.0], np.cumsum((mu - 0.5 * s * s) / YEAR + dW)])
            self.log_index[c] = x
            self.lead_mult[c] = np.ones(days + 1)
            self.stockout[c] = np.zeros(days + 1)
        for sh in self.sc.shocks:
            hit = COMMODITIES if sh.commodities == ("*",) else [c for c in sh.commodities if c in COMMODITIES]
            if sh.at_day is not None:
                starts = [sh.at_day]
            else:
                n = rng.poisson(sh.rate_per_year * days / YEAR * max(len(hit), 1) / max(len(hit), 1))
                starts = sorted(rng.uniform(0, days, n))
            for d0 in starts:
                size = rng.normal(sh.size_mean, sh.size_sd)
                who = hit if sh.at_day is not None else [c for c in hit if rng.random() < 0.6]
                for c in who:
                    prof = np.where(t >= d0, 1.0, 0.0)
                    if sh.half_life_days:
                        prof = prof * np.exp(-np.maximum(t - d0, 0) * math.log(2) / sh.half_life_days)
                    self.log_index[c] = self.log_index[c] + size * prof
                    self.lead_mult[c] = np.maximum(self.lead_mult[c], 1 + (sh.lead_mult - 1) * prof)
                    self.stockout[c] = np.maximum(self.stockout[c], sh.stockout_p * prof)
                self.events.append(dict(day=float(d0), commodities=who, log_size=float(size),
                                        permanent=sh.half_life_days is None, note=sh.note))

    def index(self, commodity: str | None, day: float) -> float:
        if not commodity or commodity not in self.log_index:
            return 1.0
        d = int(min(max(day, 0), self.days))
        return float(math.exp(self.log_index[commodity][d]))

    def price(self, item: Item, day: float) -> float:
        ix = self.index(item.commodity, day) if item.commodity else 1.0
        drift = (1 + self.sc.service_drift) ** (day / YEAR) if not item.commodity else 1.0
        return item.price * ix ** item.passthrough * drift * (1 + self.sc.import_tariff * item.import_share)

    # the lab's own ordering office (DAL: one quote lapsed unplaced, another order held about four weeks)
    OFFICE_MEDIAN_DAYS, OFFICE_GSD, OFFICE_LAPSE_P, OFFICE_LAPSE_DAYS = 3.0, 2.5, 0.08, 30.0

    def office_delay(self) -> float:
        d = self.OFFICE_MEDIAN_DAYS * math.exp(self.rng.normal(0, math.log(self.OFFICE_GSD)))
        if self.rng.random() < self.OFFICE_LAPSE_P:
            d += self.OFFICE_LAPSE_DAYS
        return d

    def lead_time(self, item: Item, day: float) -> tuple[float, bool]:
        """Days to arrive, and whether the order was backordered."""
        m = self.lead_mult[item.commodity][int(min(day, self.days))] if item.commodity in self.lead_mult else 1.0
        if self.sc.import_tariff and item.import_share > 0.5:
            m *= 1.3
        lt = item.lead_days * m * math.exp(self.rng.normal(0, math.log(item.lead_gsd)))
        if item.hazmat:
            lt += self.rng.uniform(2, 5)                 # ground shipping
        p = self.stockout[item.commodity][int(min(day, self.days))] if item.commodity in self.stockout else 0.0
        back = self.rng.random() < p
        if back:
            lt += 30.0 * math.exp(self.rng.normal(0, 0.5))
        return lt, back

    def service_price(self, base: float, day: float) -> float:
        return base * (1 + self.sc.service_drift) ** (day / YEAR)


@dataclass
class Order:
    item: str
    qty: float
    cost: float
    placed_day: float
    arrival_day: float
    backordered: bool
    campaign: str


def load_private():
    """Merge a git-ignored data/private/prices.json (key -> fields) into the catalogue: private quotes the lab holds."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parent / "data" / "private" / "prices.json"
    if p.exists():
        for k, v in json.loads(p.read_text()).items():
            if k in ITEMS:
                for f, x in v.items():
                    setattr(ITEMS[k], f, x)
    return p.exists()


class Stores:
    """One campaign's stock of each item, and its open orders. Campaigns keep separate stores (their budgets are
    separate), so one cannot use the other's Sc master alloy."""

    def __init__(self, campaign: str, market: Market):
        self.campaign, self.market = campaign, market
        self.stock: dict = {}
        self.orders: list[Order] = []

    def on_hand(self, key, day) -> float:
        got = sum(o.qty for o in self.orders if o.item == key and o.arrival_day <= day)
        return got - self.stock.get(("used", key), 0.0)

    def due(self, key, day) -> float:
        return sum(o.qty for o in self.orders if o.item == key and o.arrival_day > day)

    def ensure(self, bill: dict, day: float, spare: float = 1.5) -> tuple[float, float, list]:
        """Order what the bill needs beyond stock and open orders (at least the MOQ, `spare` times the shortfall).
        Returns (cost, the day everything is on hand, the orders placed)."""
        cost, ready, placed = 0.0, day, []
        for key, q in bill.items():
            it = ITEMS[key]
            have = self.on_hand(key, day) + self.due(key, day)
            if have >= q - 1e-12:
                pend = [o.arrival_day for o in self.orders if o.item == key and o.arrival_day > day]
                if self.on_hand(key, day) < q and pend:
                    ready = max(ready, min(pend))
                continue
            need = max(it.moq, spare * (q - have))
            price = self.market.price(it, day)
            lt, back = self.market.lead_time(it, day)
            lt += self.market.office_delay()
            fee = 0.0
            if it.hazmat:
                fee += 45.0 + (self.market.rng.uniform(100, 300) if "4.2" in it.hazmat else 0.0)
            if self.market.rng.random() < it.p_fail:      # the cheap channel fails; the fallback costs more
                lt += it.fail_days
                price *= it.fallback_mult
                need = max(spare * (q - have), min(it.moq, 0.1))   # and sells small lots
                back = True
            o = Order(key, need, need * price + fee, day, day + lt, back, self.campaign)
            self.orders.append(o)
            placed.append(o)
            cost += o.cost
            ready = max(ready, o.arrival_day)
        return cost, ready, placed

    def consume(self, bill: dict):
        for key, q in bill.items():
            self.stock[("used", key)] = self.stock.get(("used", key), 0.0) + q
