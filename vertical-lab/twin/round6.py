"""Round 6 of the twin: money tracked instead of limited, used equipment from the market, crucibles, the HPC at scale.

Round 5 gave each campaign two years' money at t = 0, and the automated lab spent it in ten to fourteen months and
then sat idle. Round 6 changes what Sterling asked for on PR 405 (2026-11-27 17:46 UTC):

1. **Money isn't limited for either lab; it's tracked.** Every rule that stopped spending is gone (``GATES_REMOVED``):
   the budget and the spending plan, round 4's reserve for the standing slots, round 5's money kept for the work in
   progress, the three money rules of the stock heuristic, the optimizers' check that money is left for a new design,
   and their cap on copper's blend screens. What limits work is what limits it in a lab (``GATES_KEPT``): stations,
   robots, people, fixtures, stock and its lead times, decision windows, and round 4's WIP limit before the first
   fabrication step. Every dollar is recorded with a category (``Campaign6.cash``, ``Twin6.spend_report``): capital
   (new and used), consumables, stock, partners and services, labour, facility, and the scale-up stages.
2. **Used equipment from the market.** The used price, lead time, fault risk and whether a used market exists come
   per station from ``out/twin6/market/summary.csv`` (issue 424's survey of listings) when that file is there, and
   from round 5's stand-ins when it isn't (``load_market``, ``build_schedule6``). Every row says which.
3. **Pre-coated crucibles, explicitly** (``CRUCIBLES``, ``CruciblePool``, ``ResourceAtom6``): each alloy family has
   crucibles in rotation; a crucible is out of service for its clean, respray and overnight dry after every melt; the
   pool is bought at t = 0 and arrives after its lead time; until then there is one crucible per family, about one
   run a day. Wear (melts per crucible) goes through the stores as before.
4. **The HPC stream at scale** (``Twin6._stream_tick``): the candidates the policies see are scaled (``hpc.scale``:
   64 x scale new ones a day, the newest 128 x scale unexplored ones kept visible), without keeping every
   candidate ever simulated in memory.
5. Reproducibility is twin/repro.py's and twin/gpcheck6.py's business.
6. **Copper's optimizers without their cap on blend screens** (``opt/net6.py``), with the reasons a policy proposes
   nothing new counted, so an idle stretch can be explained.

Everything else is round 5's: two years from t = 0, the facility window, the conventional atomizer at most 8 runs a
week and the automated one 24/7, decision windows, shared stations, the reorder-point stock heuristic. Round 5's code
is unchanged; round 6 subclasses ``Facility5``, ``Campaign5`` and ``Twin5``. Everything is simulated.
"""
from __future__ import annotations

import bisect
import csv
import heapq
import itertools
import math
from pathlib import Path

import numpy as np

from twin import campaign as C
from twin import facility as fac
from twin import round4 as R4
from twin import round5 as R5
from twin import supply

H, WEEK = 24.0, 168.0
HERE = Path(__file__).resolve().parent
MARKET_CSV = HERE.parent / "out" / "twin6" / "market" / "summary.csv"

# Sterling's `Round 6 note:` comments on PR 405 or PR 427 while round 6 is built; every row records the ones applied.
NOTES: dict = {}
NOTES_APPLIED: tuple = ()

# ------------------------------------------------------------------------------------------------- item 1: money
# The two years of round 3's money a year (round 5's budgets): no longer a limit, kept as a reference line for the
# reports and as the campaigns' shares of the shared atomizer and of the lab's fixed costs (2 : 1).
REFERENCE_USD = {"flaime_al": 240_000.0, "onr_cu": 120_000.0}
GATES_REMOVED = {
    "budget": "Campaign.submit3: an action dearer than the money left was refused ('money')",
    "spending plan": "Campaign.submit3 and Campaign.plan: spend so far plus the action within the plan ('plan'); "
                     "round 5 had already set the plan to the whole budget",
    "standing-slot reserve": "Campaign4.reserve and Campaign4.submit3: money kept for the coming week's unfilled "
                             "partner slots ('plan_reserve')",
    "money for the work in progress": "Campaign5.wip_reserve and Campaign5.submit3: a new composition waited until "
                                      "the lots already made could be paid through their next steps ('money_wip')",
    "stock: days the money lasts": "Campaign5._reorder: no item stocked beyond the days the money left lasts at the "
                                   "last 30 days' rate of spending, or beyond the campaign's end",
    "stock: work-in-progress money": "Campaign5._reorder: stock never spent the money kept for the work in progress",
    "stock: 20 % cap": "Campaign5._reorder: stock on hand and on order worth at most 20 % of the money left",
    "the run loop": "Twin5.run_async: a campaign with no money left was not asked; after a 'plan' refusal the rest "
                    "of a decision's actions over $50 were held back",
    "policies: money for a new design": "policies2.Base2.can_start_new: a new design only with more than $1,500 "
                                        "(aluminium) or $3,000 (copper) left",
    "optimizers: blend-screen cap": "net3.Net3._screen_share_ok: copper's blend screens at most a quarter of the "
                                    "money spent so far plus $2,500",
}
GATES_KEPT = {
    "capacity": "an action starts only if its gating station (and a crucible, for the atomizer) can take it within "
                "2 h; partner slots are filled as late as possible (rounds 3-5)",
    "WIP limit": "round 4's limit before the first fabrication step: a new design starts only while the lots waiting "
                 "for their first build or deposit are fewer than two weeks of that step's capacity (at least 3). It "
                 "counts lots against capacity, not dollars",
    "decision windows": "people's reviews and meetings, and the automated lab's sign-off for a step estimated at "
                        "$2,000 or more (round 5): a wait for a person, not a refusal",
    "stock": "metal and consumables arrive after their lead times; a charge waits for what is short",
}
# cash categories of a campaign's own spending, and of the lab's
CATS = ("stock", "consumables", "partners_services", "stages")
LAB_CATS = ("capital_new", "capital_used", "facility", "labour")
CAT_LABEL = {
    "stock": "stock (metal and stocked consumables ordered into the stores)",
    "consumables": "consumables (in-house station fees: plates, argon, wire, cones; per-action supplies)",
    "partners_services": "partners and services (the partners' sessions, BYU core facilities, outside services, visits)",
    "stages": "scale-up stages after discovery (gas lot, validation network, full-part test; a line of its own)",
    "capital_new": "capital, bought new", "capital_used": "capital, bought used (with refurbishment)",
    "facility": "facility (the space's fit-out, service contracts, utilities and space)",
    "labour": "labour (fixed staff, and hands-on hours at the student rate)",
}

# ------------------------------------------------------------------------------------------------- item 2: used market
USED5 = dict(R5.USED)


def _num(row, *names, default=None):
    for n in names:
        v = row.get(n)
        if v not in (None, ""):
            try:
                return float(v)
            except ValueError:
                continue
    return default


def _flag(row, *names, default=None):
    for n in names:
        v = row.get(n)
        if v not in (None, ""):
            return str(v).strip().lower() in ("1", "true", "yes", "y", "t")
    return default


def market_file(path=None) -> Path:
    return Path(path) if path is not None else MARKET_CSV


def market_sha256(path=None) -> str | None:
    """The sha256 of the market summary a run read (None: there was none), recorded in every row."""
    import hashlib
    p = market_file(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def load_market(path=None) -> dict:
    """The per-station summary of the used-equipment survey (issue 424, ``twin/market6.py`` on its branch), as
    ``{item key: parameters}`` in the units ``build_schedule6`` uses, with ``source`` saying where the numbers came
    from. Missing file: ``{}`` (round 5's stand-ins apply to every station).

    The survey writes one row per station (``station``; ``component`` empty or ``(station)``) and, for a station that
    is several machines, one row per machine as well (``component`` named): only the station's own row is read, since
    it already combines its machines. A station the survey lists replaces round 5's numbers for it field by field; a
    field the survey leaves empty keeps round 5's, and ``used_ok`` (whether a real used market exists and is cheaper
    than new) replaces round 5's ``USED_OK``."""
    p = market_file(path)
    if not p.exists():
        return {}
    out = {}
    with p.open(newline="") as fh:
        for row in csv.DictReader(fh):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            k = row.get("station_key") or row.get("station") or row.get("key") or row.get("item")
            if not k or row.get("component", "") not in ("", "(station)"):
                continue
            n_l = row.get("n_listings") or row.get("listings") or "?"
            m = dict(source=f"out/twin6/market/summary.csv ({n_l} listings"
                            + (f"; market: {row['market']}" if row.get("market") else "") + ")")
            if row.get("market"):
                m["market_text"] = row["market"]
            ok = _flag(row, "used_ok", "market_exists", "has_market")
            if ok is not None:
                m["ok"] = ok
            for f, names in (("price_frac", ("price_frac", "used_price_frac", "used_frac_of_new")),
                             ("lead_w", ("lead_w", "used_lead_w", "lead_weeks")),
                             ("lead_sigma", ("lead_sigma", "used_lead_sigma")),
                             ("p_fault", ("p_fault", "fault_risk", "p_refurb")),
                             ("refurb_w", ("refurb_w", "refurb_weeks")),
                             ("refurb_sigma", ("refurb_sigma",)),
                             ("refurb_frac", ("refurb_frac", "refurb_frac_of_new")),
                             ("extra_com_w", ("extra_com_w", "checkout_w")),
                             ("n_listings", ("n_listings", "listings")),
                             ("used_price_usd", ("median_delivered_usd", "used_price_usd", "median_used_usd")),
                             ("new_price_usd", ("new_usd_each", "new_price_usd", "new_usd"))):
                v = _num(row, *names)
                if v is not None:
                    m[f] = v
            if "lead_w" not in m:
                d = _num(row, "lead_d", "used_lead_d", "lead_days")
                if d is not None:
                    m["lead_w"] = d / 7.0
            out[k] = m
    return out


def used_params(k: str, market: dict | None) -> dict:
    """Used-purchase parameters of item ``k``: round 5's stand-ins, replaced field by field by the market survey."""
    p = dict(ok=k in R5.USED_OK, lead_w=USED5["lead_w"], lead_sigma=USED5["lead_sigma"],
             price_frac=USED5["price_frac"], p_fault=USED5["p_fault"], refurb_w=USED5["refurb_w"],
             refurb_sigma=USED5["refurb_sigma"], refurb_frac=USED5["refurb_frac"], extra_com_w=USED5["extra_com_w"],
             market=R5.USED_OK.get(k, ""), source="round 5's stand-ins (twin/round5.py USED, USED_OK)")
    m = (market or {}).get(k)
    if m:
        p.update({f: v for f, v in m.items() if v is not None and f != "market_text"})
        p["market"] = m.get("market_text", m.get("source", p["market"]))
    return p


def used_rule6(k: str, p: dict) -> dict:
    """Round 5's rule with the station's own numbers: buy used when the expected days saved, against the expected
    date the space is ready, are at least ``rule_days``, with the risk of a fault priced in."""
    lead_w, inst_w, com_w, _ = R4.BUILD[k]
    Rm = USED5["room_expected_d"] * H
    new_on = max(lead_w * WEEK, Rm) + (inst_w + com_w) * WEEK
    arr_u = (R4.PO_W + p["lead_w"]) * WEEK + p["p_fault"] * p["refurb_w"] * WEEK
    used_on = max(arr_u, Rm) + (inst_w + com_w + p["extra_com_w"]) * WEEK
    saved = (new_on - used_on) / H
    return dict(ok=bool(p["ok"]) and saved >= USED5["rule_days"], expected_days_saved=round(saved, 1))


def build_schedule6(seed: int, plan: str, opts: dict | None = None, market: dict | None = None) -> dict:
    """Round 5's build-out with each station's own used-market numbers. The draws are round 5's, in round 5's order,
    so with no market file the schedule is round 5's for the same seed."""
    from twin import econ as E
    opts = opts or {}
    items = {it.key: it for it in E.items("vertical_lab")}
    rng = np.random.default_rng(60_000 + seed)
    out = dict(items={}, payments=[], stations={}, cell_h=None, start_h=0.0, room_h=None, used={},
               used_source="out/twin6/market/summary.csv" if market else "round 5's stand-ins")
    if plan == "external":
        return out
    t_arr = {}
    for k in sorted(R4.BUILD):
        lead_w, inst_w, com_w, src = R4.BUILD[k]
        t_arr[k] = lead_w * WEEK * math.exp(rng.normal(0, R4.LEAD_SIGMA)) if lead_w > 0 else 0.0
    room_h = float(np.random.default_rng(61_000 + seed).uniform(*R5.ROOM_DAYS)) * H
    out["room_h"] = room_h
    ru = np.random.default_rng(62_000 + seed)
    allow_used = bool(opts.get("used", True))
    for k in sorted(R4.BUILD):
        lead_w, inst_w, com_w, src = R4.BUILD[k]
        p = used_params(k, market)
        # used draws for every item in a fixed order, so the stream doesn't depend on the rule
        lu = (R4.PO_W + p["lead_w"]) * WEEK * math.exp(ru.normal(0, p["lead_sigma"]))
        fault = bool(ru.random() < p["p_fault"])
        refurb = p["refurb_w"] * WEEK * math.exp(ru.normal(0, p["refurb_sigma"]))
        if k not in items:
            continue
        it = items[k]
        if k == "cubxl" or it.kind == "owned":
            continue
        if k == "services":                       # the space itself: ready in the facility window
            out["items"][k] = dict(name=it.name, capex=it.capex, order_h=0.0, arrive_h=room_h, install_h=room_h,
                                   commission_h=room_h, online_h=room_h, used=False, source=R5.ROOM_SOURCE)
            dep = R4.DEPOSIT[0] if it.capex >= R4.DEPOSIT[1] else 0.0
            if dep:
                out["payments"].append((0.0, it.capex * dep, k))
            out["payments"].append((room_h, it.capex * (1 - dep), k))
            continue
        inst_n = max(t_arr[k], room_h)
        on_new = inst_n + (inst_w + com_w) * WEEK
        rule = used_rule6(k, p)
        if allow_used and rule["ok"]:
            arr = lu + (refurb if fault else 0.0)
            inst0 = max(arr, room_h)
            online = inst0 + (inst_w + com_w + p["extra_com_w"]) * WEEK
            price = it.capex * p["price_frac"]
            ref_usd = it.capex * p["refurb_frac"] if fault else 0.0
            out["payments"].append((0.0, price, k + " (used)"))
            if ref_usd:
                out["payments"].append((lu, ref_usd, k + " (refurbishment)"))
            out["used"][k] = dict(name=it.name, fault=fault, arrive_h=round(arr, 1), online_h=round(online, 1),
                                  online_new_h=round(on_new, 1), days_bought=round((on_new - online) / H, 1),
                                  expected_days_saved=rule["expected_days_saved"], capex_new=it.capex,
                                  usd_paid=round(price + ref_usd, 2), usd_saved=round(it.capex - price - ref_usd, 2),
                                  price_frac=p["price_frac"], lead_w=p["lead_w"], p_fault=p["p_fault"],
                                  market=p["market"], source=p["source"] if not (market or {}).get(k) else
                                  "out/twin6/market/summary.csv")
            out["items"][k] = dict(name=it.name, capex=price + ref_usd, order_h=0.0, arrive_h=arr, install_h=inst0,
                                   commission_h=inst0 + inst_w * WEEK, online_h=online, used=True, source=src)
            continue
        out["items"][k] = dict(name=it.name, capex=it.capex, order_h=0.0, arrive_h=t_arr[k], install_h=inst_n,
                               commission_h=inst_n + inst_w * WEEK, online_h=on_new, used=False, source=src)
        dep = R4.DEPOSIT[0] if it.capex >= R4.DEPOSIT[1] else 0.0
        if dep:
            out["payments"].append((0.0, it.capex * dep, k))
        out["payments"].append((t_arr[k], it.capex * (1 - dep), k))
    for st, its in R4.STATION_ITEMS.items():
        out["stations"][st] = max(out["items"][k]["online_h"] for k in its if k in out["items"])
    cell = max(out["items"][k]["online_h"] for k in R4.CELL) + R4.CELL_INTEGRATION_W * WEEK
    out["cell_h"] = cell
    out["full_h"] = max([cell] + list(out["stations"].values()))
    out["start_h"] = out["full_h"] if plan == "wait" else 0.0
    out["payments"].sort()
    return out


# ------------------------------------------------------------------------------------------------- item 3: crucibles
# Round 5 derived the automated atomizer's cycle (2.2 h a composition for aluminium) on the assumption of pre-coated
# spare crucibles: "Each crucible is out of service about 14-16 h for its overnight BN dry, so a cycle of 2-3 h needs
# 6-8 coated crucibles per alloy family in rotation; the lab has one per family now, which allows at most 1 run a day"
# (notes/twin_round5.md, section 2). Round 6 models them:
#   * ``n``: crucibles in rotation per family once the pool is in. The automated lab: as many as keep the atomizer
#     at its cycle, (run + 15 h) / run rounded up: 8 for aluminium (2.2 h) and 6 for copper (3.4 h), round 5's "6-8".
#     The conventional lab: 3 (two attended starts a day and a spare);
#   * ``day0``: one per family, what the lab has now;
#   * the pool is ordered at t = 0 (BYU's purchase order, then the vendor's lead, drawn per seed and family) and paid
#     for on delivery by the campaign that uses the family, as a stores order;
#   * ``turnaround_h``: after the run (the run's own hours include the cool-down) a crucible is cleaned, resprayed with
#     BN and dried: out of service 15 h (14-16 h), whoever does it;
#   * ``life``: melts per crucible, the twin's rates since round 1 (12 for aluminium, 6 for copper): each melt uses
#     1/life of a crucible from the stores, which reorder them like any other item;
#   * price and lead: ``ITEM`` (see ``CRUCIBLE_SOURCE``).
CRUCIBLE_SOURCE = (
    "web lookups on 2026-11-27 (stand-ins until a vendor quotes for the rePOWDER's own geometry): no vendor sells a "
    "factory BN-coated graphite crucible of this size, and AMAZEMET's spares have no public price or lead time "
    "(its configurator ends in a quote); a stock graphite bottom-pour crucible of about 200 mL with its sealing rod "
    "is $198 (MTI, mtixtl.com EQ-GR6083-LD), plain 220-250 mL crucibles $90-170 (MTI, Graphite Store, Indutherm): "
    "$200 each, coated in house (ZYP BN aerosol, $45 a can, about $1 a coat); stock items ship in 1-5 working days "
    "and graphite machined to print takes 7-12 days at one shop and 6-8 weeks at others (Ohio Carbon Blank, "
    "thermalprocessing.com, 2022): a 21-day median with a spread of 1.8, after BYU's purchase order. Rounds 1-5 "
    "assumed $450 and 49 days. Whether a third-party crucible fits the rePOWDER is unverified")
CRUCIBLES = dict(n={"vertical": {"flaime_al": 8, "onr_cu": 6}, "conventional": {"flaime_al": 3, "onr_cu": 3}},
                 day0=1, turnaround_h=15.0,
                 life={"flaime_al": 12, "onr_cu": 6}, late_d=0.0,
                 source="notes/twin_round5.md section 2 (6-8 per family; 14-16 h out of service; one per family "
                        "now); DAL SOP (BN sprayed the night before); twin/campaign.py AL_RUN_CONSUMABLES and "
                        "CU_RUN_CONSUMABLES (1/12 and 1/6 of a crucible a melt)")
ITEM = supply.Item("crucible_coated", "Graphite crucible for the rePOWDER, BN-coated before use", "each", 200.0,
                   "graphite", 0.3, 21, 1.8, 1, 1.0, None, "graphite supplier (stock or machined to print)",
                   CRUCIBLE_SOURCE)
supply.ITEMS.setdefault(ITEM.key, ITEM)           # a new key: rounds 1-5 never ask for it


class CruciblePool:
    """One alloy family's coated crucibles in rotation. A run holds one from its start until it is clean, resprayed
    and dry again. Crucibles of a family are interchangeable, so what is checked is the number held at any time
    against the number in rotation (not which one)."""

    def __init__(self, family: str, n0: int, n: int, arrive_h: float, turnaround_h: float):
        self.family, self.n0, self.n, self.arrive_h, self.turnaround_h = family, n0, max(n, n0), arrive_h, turnaround_h
        k = self.n - n0                            # not in rotation until the pool arrives: held from 0 to arrive_h
        self.S, self.E = [0.0] * k, [max(arrive_h, 1e-6)] * k
        self.uses = []                             # (start, ready again)
        self.waits = []                            # (start the atomizer alone allowed, start with a crucible)

    def _ok(self, x: float, dd: float) -> bool:
        S, E, n = self.S, self.E, self.n
        i = bisect.bisect_right(S, x + 1e-9)
        if i - bisect.bisect_right(E, x + 1e-9) >= n:
            return False
        end = x + dd - 1e-9
        while i < len(S) and S[i] < end:           # the count only rises at a start
            if (i + 1) - bisect.bisect_right(E, S[i] + 1e-9) >= n:
                return False
            i += 1
        return True

    def earliest(self, t: float, d: float) -> float:
        """The earliest time at or after t a crucible is free for a run of d hours and its turnaround."""
        dd = d + self.turnaround_h
        x, E = t, self.E
        for _ in range(200000):
            if self._ok(x, dd):
                return x
            j = bisect.bisect_right(E, x + 1e-9)   # nothing changes before the next crucible is ready
            if j >= len(E):
                return x
            x = E[j]
        return x

    def take(self, s: float, d: float) -> float:
        e = s + d + self.turnaround_h
        bisect.insort(self.S, s)
        bisect.insort(self.E, e)
        self.uses.append((s, e))
        return e

    def report(self, horizon_h: float) -> dict:
        u = sorted(x for x in self.uses if x[0] < horizon_h)
        w = [b - a for a, b in self.waits if a < horizon_h]
        peak, act, ev = 0, 0, sorted([(a, 1) for a, _ in u] + [(b, -1) for _, b in u])
        for _, s in ev:
            act += s
            peak = max(peak, act)
        return dict(n_day0=self.n0, n=self.n, arrive_d=round(self.arrive_h / H, 2), turnaround_h=self.turnaround_h,
                    melts=len(u), most_in_use=peak, runs_waited=len(w), wait_h_total=round(float(sum(w)), 1),
                    wait_h_max=round(float(max(w)), 1) if w else 0.0)


class ResourceAtom6(R5.ResourceAtom):
    """Round 5's atomizer, which also needs a coated crucible of the run's family."""

    def __init__(self, a5: R5.ResourceAtom, pools: dict):
        self.__dict__.update(a5.__dict__)
        self.pools = pools
        self._found = {}                           # campaign -> (start found, start an atomizer alone would give)

    def find(self, t, dur, campaign, changeover_h=0.0, empty=False):
        pool = self.pools.get(campaign)
        if empty or pool is None:
            return super().find(t, dur, campaign, changeover_h, empty)
        s_alone = None
        for _ in range(4000):
            s, d, i = super().find(t, dur, campaign, changeover_h, False)
            if s_alone is None:
                s_alone = s
            c = pool.earliest(s, d)
            if c <= s + 1e-9:
                self._found[campaign] = (s, s_alone)
                return s, d, i
            t = c
        raise RuntimeError("could not book the atomizer with a crucible")

    def commit(self, t, d, i, campaign, what, tag=None):
        pool = self.pools.get(campaign)
        if pool is not None:
            f = self._found.get(campaign)
            if f is not None and abs(f[0] - t) < 1e-9 and f[0] > f[1] + 1e-9:
                pool.waits.append((f[1], f[0]))    # the atomizer was free earlier; the crucible was not
            ready = pool.take(t, d)
            if self.on_commit is not None:
                self.on_commit(ready)              # the engine asks again when the crucible is ready
        return super().commit(t, d, i, campaign, what, tag)


# ------------------------------------------------------------------------------------------------- facility
class Facility6(R5.Facility5):
    """Round 5's facility with the market's used equipment and the crucible pools."""

    def __init__(self, plan: str, seed: int, horizon_h: float, opts: dict | None = None):
        opts = dict(opts or {})
        self.market_used = load_market(opts.get("market_csv")) if opts.get("market", True) else {}
        self.market_sha = market_sha256(opts.get("market_csv")) if opts.get("market", True) else None
        super().__init__(plan, seed, horizon_h, opts)
        self.kind = f"r6_{self.lab}_{plan}"
        cr = dict(CRUCIBLES, **(opts.get("crucibles") or {}))
        rc = np.random.default_rng(63_000 + seed)
        self.crucibles, pools = {}, {}
        for fam in ("flaime_al", "onr_cu"):         # the same draws in both labs for a seed
            n = cr["n"]
            n = n[self.lab] if isinstance(n, dict) and self.lab in n else n
            n = int(n[fam] if isinstance(n, dict) else n)
            lead_d = R4.PO_W * 7.0 + ITEM.lead_days * math.exp(rc.normal(0, math.log(ITEM.lead_gsd)))
            arrive_h = (lead_d + float(cr.get("late_d", 0.0))) * H
            pools[fam] = CruciblePool(fam, int(cr["day0"]), n, arrive_h, float(cr["turnaround_h"]))
            self.crucibles[fam] = dict(n=n, day0=int(cr["day0"]), order_n=max(n - int(cr["day0"]), 0),
                                       arrive_h=arrive_h, turnaround_h=float(cr["turnaround_h"]),
                                       life=cr["life"][fam], late_d=float(cr.get("late_d", 0.0)))
        self.cr = cr
        self.res["atomizer"] = ResourceAtom6(self.res["atomizer"], pools)
        self.pools = pools

    def schedule(self, seed, plan) -> dict:
        return build_schedule6(seed, plan, self.opts, self.market_used)

    def derived_start_h(self, fam: str):
        """When the automated atomizer's derived cycle starts for a family: the cell is integrated (the robots tend
        the runs) and the family's crucible pool is in. None where no cell is built."""
        if self.atom_switch_h is None:
            return None
        return max(self.atom_switch_h, self.pools[fam].arrive_h)


def _station_class(key: str, st) -> str:
    """Where a station's fee goes: the lab's own in-house stations charge consumables; the partners, the outside
    services and BYU's core facilities are 'partners and services'."""
    if key.endswith("@vcl"):
        return "consumables"
    return "partners_services"


# ------------------------------------------------------------------------------------------------- lazy design maps
class _Lazy(dict):
    """A campaign's design map that rebuilds a simulated candidate dropped from memory if a policy still asks for
    it (the HPC stream makes millions; the twin keeps the visible ones and the ones something was done with)."""

    def __init__(self, camp, field):
        super().__init__()
        self._camp, self._field = camp, field

    def __missing__(self, did):
        rec = self._camp._restore(did)
        if rec is None:
            raise KeyError(did)
        return rec[self._field]


# ------------------------------------------------------------------------------------------------- campaign
class Campaign6(R5.Campaign5):
    """A campaign of round 6: money without a limit and every dollar categorized, the pure reorder-point stock
    heuristic, crucible wear on the coated item."""

    def __init__(self, spec, policy, market, facility, horizon_h, lab="vertical"):
        self.cash = []                              # (t_h, usd, category, what)
        self._rs = {}                               # route money since the last charge, by category
        self._stage_cash = 0.0
        self._batches = ([], [])                    # the HPC stream's batches: first design ids, (seed, n, ids)
        self._gone = 0
        self._refs = set()                          # designs something was started with: never dropped
        self._sims_rev = 0                          # bumped whenever the stream takes results out of ``sims``
        self._defer = True
        super().__init__(spec, policy, market, facility, horizon_h, lab=lab)
        self._defer = False
        vd, vi = _Lazy(self, "composition"), _Lazy(self, "design")
        vd.update(self._vd)
        vi.update(self._vi)
        self._vd, self._vi = vd, vi
        # the crucibles on the shelf at day 0 are coated-item stock; the family's pool is ordered at t = 0
        n0 = sum(o.qty for o in self.stores.orders if o.item == "graphite_crucible" and o.placed_day < 0)
        if n0 > 0:
            self.stores.orders.append(supply.Order(ITEM.key, n0, 0.0, -1.0, -1.0, False, spec.key))
        if "graphite_crucible" in self.prior_d:
            self.prior_d[ITEM.key] = self.prior_d.pop("graphite_crucible")
        cr = getattr(facility, "crucibles", {}).get(self.key)
        if cr and cr["order_n"] > 0:
            cost = cr["order_n"] * market.price(ITEM, 0.0)
            self.stores.orders.append(supply.Order(ITEM.key, float(cr["order_n"]), cost, 0.0, cr["arrive_h"] / H,
                                                   False, spec.key))
            self.charge(0.0, cost, f"order {ITEM.key} {cr['order_n']} (crucible pool)")
            self.stock_usd += cost
            self.stock_orders.append((0.0, ITEM.key, float(cr["order_n"]), round(cost, 2), "crucible pool",
                                      round(cr["arrive_h"] / H, 2)))
        if self.stock_mode == "reorder":
            self._reorder(0.0, initial=True)

    # ---------------------------------------------------------------------------------------- money: no limit
    @property
    def budget_left(self):
        return math.inf

    def plan(self, t_h: float) -> float:
        return math.inf

    def wip_reserve(self, now_h) -> float:
        return 0.0

    def reserve(self, now_h) -> float:
        return 0.0

    def charge(self, t, usd, what):
        """Round 1's ledger, and round 6's: the same dollars by category. Money booked on stations since the last
        charge goes where the stations say (``_station_class``); the rest of the charge is an order (stock) or the
        action's own supplies (consumables)."""
        super().charge(t, usd, what)
        if what.startswith("order "):
            self.cash.append((t, usd, "stock", what))
            return
        rs, self._rs = self._rs, {}
        left = usd
        for cat, v in rs.items():
            v = min(v, left) if left > 0 else 0.0
            if v:
                self.cash.append((t, v, cat, what))
                left -= v
        if abs(left) > 1e-9:
            self.cash.append((t, left, "partners_services" if what.startswith("provenance") else "consumables", what))

    def _route(self, steps, ready_h, what, changeover=False, tag=None, handles=None):
        """Round 4's routing, with each step's money noted by where it was spent."""
        t, usd = ready_h, 0.0
        tag = dict(tag or {}, what=what)
        res_t = t
        self._last_route = []
        F = self.fac
        stage = what.startswith("stage")
        for role, hours in steps:
            if role.startswith("="):
                role = st = role[1:]
            else:
                st = F.pick(role, t, hours, self.key, what)
            hours = F.adjust(st, hours, what, self.key)
            if hours <= 0 and role not in ("nsl",):
                continue
            R = F.res[st]
            cal = R.st
            cat = _station_class(st, cal)
            for attempt in range(4):
                h_all = max(hours * R.factor(), 0.01)
                chunk = 8.0 if (cal.hours != "24/7" and cal.attended_h is None) else h_all
                left, first = h_all, True
                e = t
                while left > 1e-9:
                    h = min(left, chunk)
                    s, e, r, c, hd = F.run_step_joint(st, t, h, self.key, what,
                                                      C.CHANGEOVER_H if (changeover and role == "atomizer") else 0.0,
                                                      dict(tag, route=st, attempt=attempt))
                    if handles is not None:
                        handles.append((st, hd))
                    u = self.market.service_price(c if first else c - cal.fee_usd, s / H)
                    usd += u
                    if stage:
                        self.cash.append((s, u, "stages", what))
                        self._stage_cash += u
                    elif u:
                        self._rs[cat] = self._rs.get(cat, 0.0) + u
                    first = False
                    left -= h
                    t, res_t = e, r
                ok, t_next = F.job_done(st, e, self.key, what)
                if ok:
                    break
                t = max(t_next, res_t)
            F.route_log.append((round(ready_h, 2), self.key, role, st, what))
            self._last_route.append((role, st))
        return max(res_t, t), usd

    def view(self, now_h):
        v = super().view(now_h)
        v["sims_rev"] = self._sims_rev
        return v

    # ---------------------------------------------------------------------------------------- stock: no money rules
    def _reorder(self, day, keys=None, initial=False):
        """The reorder-point heuristic alone: at or below s, order up to S (at least the minimum order)."""
        if self._defer:
            return
        keys = sorted(set(keys) if keys is not None else (set(self.prior_d) | set(self.use_log)))
        for key in keys:
            if key not in supply.ITEMS:
                continue
            d, s, S = self._levels(key, day)
            if d <= 0:
                continue
            pos = self.stores.on_hand(key, day) + self.stores.due(key, day)
            if pos <= s + 1e-12 and S > pos + 1e-9:
                self._place(key, max(S - pos, supply.ITEMS[key].moq), day, "initial" if initial else "reorder")

    def _materials(self, bill, now_h):
        if "graphite_crucible" in bill:             # wear is on the coated crucible
            bill = dict(bill)
            bill[ITEM.key] = bill.pop("graphite_crucible")
        return super()._materials(bill, now_h)

    # ---------------------------------------------------------------------------------------- admission
    def submit3(self, a: dict, now_h: float) -> str:
        """Round 5's sign-off window, then round 4's admission (the WIP limit, the gating station). No money rule."""
        self._rs = {}
        if self.dec is not None and a.get("kind") != "stop":
            lim = self.dec.signoff_usd(self.key)
            if lim is not None:
                self.now_h = now_h
                if self.estimate(a) >= lim:
                    t0 = self._so_first.setdefault(self._so_key(a), now_h)
                    if now_h + 1e-9 < self.dec.signoff_time(t0):
                        self.status_log["signoff"] = self.status_log.get("signoff", 0) + 1
                        return "capacity"
        return R4.Campaign4.submit3(self, a, now_h)

    # ---------------------------------------------------------------------------------------- the stream's designs
    def _forget(self, did):
        """Drop a simulated candidate nothing was done with (it can be rebuilt from its batch's seed)."""
        d = self.designs.pop(did, None)
        if d is None:
            return
        self._dindex.pop(d["key"], None)
        dict.pop(self._vd, did, None)
        dict.pop(self._vi, did, None)
        self._gone += 1

    def _restore(self, did):
        starts, metas = self._batches
        j = bisect.bisect_right(starts, did) - 1
        if j < 0:
            return None
        seed, n, ids = metas[j]
        if ids is None:
            if not (starts[j] <= did < starts[j] + n):
                return None
            pos = did - starts[j]
        else:
            if did not in ids:
                return None
            pos = ids.index(did)
        ds = self.space.sample(n, seed=seed)
        if pos >= len(ds):
            return None
        design = ds[pos]
        comp = {e: round(design.get(e, 0.0), 3) for e in self.space.elements}
        key = tuple(sorted(comp.items()))
        rec = dict(key=key, composition=self.space.composition(comp), design=dict(design))
        self.designs[did] = rec
        self._dindex[key] = did
        dict.__setitem__(self._vd, did, rec["composition"])
        dict.__setitem__(self._vi, did, rec["design"])
        self._gone -= 1
        return rec


# ------------------------------------------------------------------------------------------------- the twin
class Twin6(R5.Twin5):
    """Both campaigns on round 6's facility: money tracked, not limited."""

    def __init__(self, specs: dict, policies: dict, plan="parallel", seed=0, horizon_days=730,
                 scenario="historical", opts=None, pol_names=None):
        opts = dict(opts or {})
        self.lab = opts.get("lab", "vertical")
        self.h = horizon_days * H
        self.horizon_days = horizon_days
        supply.load_private()
        self.market = supply.Market(scenario, seed, int(horizon_days) + 400)
        self.mode = "async"
        self.plan = plan
        self.opts = opts
        self.fac4 = Facility6(plan, seed, self.h + 2000 * H, opts)
        self.campaigns = {}
        for k, sp in specs.items():
            c = Campaign6(sp, policies[k], self.market, self.fac4, self.h, lab=self.lab)
            c.async_ = True
            c.start_h = self.fac4.start_h
            self.campaigns[k] = c
        self.facilities = {k: c.fac for k, c in self.campaigns.items()}
        self.seq = itertools.count()
        self.trace = None
        self._iters = {k: 0 for k in self.campaigns}
        self.stages = bool(opts.get("stages", True))
        names = pol_names or {k: getattr(policies[k], "name", "") for k in specs}
        modes = {k: ("human" if (self.lab == "conventional" or names.get(k) in R5.HUMAN_POLICIES) else "auto")
                 for k in specs}
        self.dec = R5.Decide(opts.get("decisions", "nominal"), self.lab, modes)
        for c in self.campaigns.values():
            c.dec = self.dec
        self.held_log = {k: [] for k in specs}
        self.daily = {k: {} for k in specs}
        hp = dict(R5.HPC, scale=1)
        hp.update(opts.get("hpc") or {})
        sc = float(hp.get("scale", 1))
        if "keep" not in (opts.get("hpc") or {}):
            hp["keep"] = int(round(R5.HPC["keep"] * sc))
        if "add_per_day" not in (opts.get("hpc") or {}):
            hp["add_per_day"] = R5.HPC["add_per_day"] * sc
        cap = hp["cores"] * 24.0 / hp["core_h"]
        hp["add_per_day"] = min(hp["add_per_day"], cap)     # the allocation can't simulate more than it has cores for
        self.hpc = hp
        self.stream = {k: dict(rng=np.random.default_rng(70_000 + 97 * seed + i), acc=0.0, pool=[], evaluated=0.0,
                               materialized=0, evicted=0, pool_sizes=[], live={})
                       for i, k in enumerate(specs)}

    def _day(self, k, g):
        d = int(g // H)
        D = self.daily[k].get(d)
        if D is None:
            c = self.campaigns[k]
            D = self.daily[k][d] = dict(spent=round(c.spent, 2), asked=0, proposed=0, held=0,
                                        pending=len(c.pending), st={})
        return D

    def run_async(self, verbose=False):
        """Round 5's loop without its money rules: a campaign is asked whenever something changed for it."""
        q, ends = [], []
        F = self.fac4
        for r in F.res.values():
            r.on_commit = lambda e, _ends=ends: heapq.heappush(_ends, e)
        dirty = {k: True for k in self.campaigns}
        last = {k: -1e9 for k in self.campaigns}
        tot_b = sum(REFERENCE_USD.get(k, 1.0) for k in self.campaigns)
        self._money_share = {k: REFERENCE_USD.get(k, 1.0) / tot_b for k in self.campaigns}
        keys = list(self.campaigns)
        held = {k: {"review": [], "meeting": []} for k in keys}
        g, step = 0.0, 0
        start = F.start_h

        def flush(k, c):
            for tr2, pay in c.events_out:
                heapq.heappush(q, (tr2, next(self.seq), k, pay))
            c.events_out = []

        while g <= self.h + 1e-9:
            F.now = g
            while q and q[0][0] <= g + 1e-9:
                tr, _, k, p = heapq.heappop(q)
                c = self.campaigns[k]
                cls = self.dec.classify(k, p)
                if cls is None:
                    if c.release3(tr, p):
                        dirty[k] = True
                    flush(k, c)
                else:
                    held[k][cls].append((tr, c.spent, p))
            for k in keys:
                c = self.campaigns[k]
                for cls in ("review", "meeting"):
                    L = held[k][cls]
                    if L and self.dec.due(k, cls, g, L[0][0], len(L)):
                        for tr, sp, p in L:
                            nd = len(c.demonstrated)
                            if c.release3(g, p):
                                dirty[k] = True
                            for d in c.demonstrated[nd:]:
                                d["t_h"], d["spent"], d["t_seen_h"] = tr, sp, g
                            self.held_log[k].append((cls, round(tr, 2), round(g, 2)))
                            flush(k, c)
                        held[k][cls] = []
            freed = False
            while ends and ends[0] <= g + 1e-9:
                heapq.heappop(ends)
                freed = True
            self._stream_tick(g)
            if g + 1e-9 < start:
                g += self.DT_H
                step += 1
                continue
            if step % 24 == 0:
                for k, c in self.campaigns.items():
                    if c.stock_mode == "reorder":
                        c._reorder(g / H)
                if self.stages:
                    self._stage_tick(g)
            order = keys if step % 2 == 0 else keys[::-1]
            if len(keys) == 2:
                order = sorted(order, key=lambda k: self._atom_share(k, g) - self._money_share[k])
            for k in order:
                c = self.campaigns[k]
                D = self._day(k, g)
                D["held"] = max(D["held"], len(held[k]["review"]) + len(held[k]["meeting"]))
                if not (dirty[k] or freed or g - last[k] >= 24.0):
                    continue
                dirty[k], last[k] = False, g
                v = c.view(g)
                acts = c.policy.propose(v, self.N_ASK) or []
                D["asked"] += 1
                D["proposed"] += len(acts)
                for a in acts:
                    before = dict(c.status_log)
                    st = c.submit3(a, g)
                    if st == "capacity":
                        if c.status_log.get("signoff", 0) > before.get("signoff", 0):
                            st = "signoff"
                        elif c.status_log.get("kanban", 0) > before.get("kanban", 0):
                            st = "kanban"
                    D["st"][st] = D["st"].get(st, 0) + 1
                    ok = st == "ok"
                    if ok:
                        self._keep_visible(k, c, a, g)
                    cb = getattr(c.policy, "admitted" if ok else "rejected", None)
                    if cb is not None:
                        cb(a) if ok else cb(a, "capacity" if st in ("signoff", "kanban") else st)
                flush(k, c)
            g += self.DT_H
            step += 1
        self._held_end = {k: {cls: len(v) for cls, v in held[k].items()} for k in keys}
        return self.summary()

    # ------------------------------------------------------------------------------------------ item 4: the stream
    GRACE_H = 24.0                                   # a candidate out of the pool is kept this long before it is dropped

    def _stream_tick(self, g):
        """Round 5's stream (note 4) at ``hpc.scale``: the allocation simulates candidates continuously; ``64 x
        scale`` a day become visible to the policies as open-CALPHAD results, the newest ``128 x scale`` unexplored
        ones stay visible. A candidate that has left the visible pool with nothing started on it is dropped from
        memory a day later (it can be rebuilt from its batch's seed); round 5 kept every one."""
        hp = self.hpc
        per_h = hp["cores"] / hp["core_h"]
        for k, c in self.campaigns.items():
            S = self.stream[k]
            S["evaluated"] += per_h * self.DT_H
            S["acc"] += hp["add_per_day"] / 24.0 * self.DT_H
            n = int(S["acc"])
            live = S["live"]
            if n > 0:
                S["acc"] -= n
                seed = int(S["rng"].integers(1 << 30))
                ds = c.space.sample(n, seed=seed)
                ids, made = [], []
                for d in ds:
                    n0 = len(c.designs)
                    did = c.design_id(d)
                    ids.append(did)
                    if len(c.designs) == n0:         # this composition is a design already (the stream's or not)
                        S["repeats"] = S.get("repeats", 0) + 1
                        continue
                    made.append(did)
                    comp = c.designs[did]["composition"]
                    proc = {v.name: d[v.name] for v in c.space.process if v.name in d}
                    rec = dict(kind=hp["node"], design=did, proc=proc, out=c.truth.sim_open(comp), t=g, stream=True)
                    c.sims.append(rec)
                    live[did] = rec
                    S["pool"].append(did)
                    S["materialized"] += 1
                if made:
                    run = ids == list(range(ids[0], ids[0] + len(ids)))
                    c._batches[0].append(made[0])
                    c._batches[1].append((seed, n, None if run else ids))
            if len(S["pool"]) > hp["keep"]:
                refs = c._refs
                nd = len(S["pool"]) - hp["keep"]
                drop = {did for did in S["pool"][:nd] if did not in refs}
                del S["pool"][:nd]
                if drop:
                    c.sims = [x for x in c.sims if not (x.get("stream") and x["design"] in drop)]
                    c._sims_rev += 1
                    for did in drop:
                        live.pop(did, None)
                    S["evicted"] += len(drop)
                    S.setdefault("limbo", []).append((g, drop))
            L = S.get("limbo")
            while L and L[0][0] <= g - self.GRACE_H:
                _, drop = L.pop(0)
                refs = c._refs
                for did in drop:
                    if did not in refs and did not in live:
                        c._forget(did)
            if int(g) % (24 * 7) == 0:
                S["pool_sizes"].append(len(S["pool"]))

    def _keep_visible(self, k, c, a, g):
        """A design the policy starts stays in memory and visible with its simulation, as round 5's stream promised
        ("every candidate the policies make, build or test stays visible"), also when it had left the pool."""
        kind = a.get("kind")
        if not ((kind == "powder" and not a.get("into")) or kind == "blend_ded"):
            return
        d = a.get("design")
        if not isinstance(d, dict):
            return
        S = self.stream[k]
        did = c.design_id(d)
        c._refs.add(did)
        starts, metas = c._batches
        j = bisect.bisect_right(starts, did) - 1
        if j < 0 or did in S["live"]:
            return
        seed, n, ids = metas[j]
        if (ids is None and not (starts[j] <= did < starts[j] + n)) or (ids is not None and did not in ids):
            return                                   # not a stream candidate (the policy's own design)
        proc = {v.name: d[v.name] for v in c.space.process if v.name in d}
        rec = dict(kind=self.hpc["node"], design=did, proc=proc,
                   out=c.truth.sim_open(c.designs[did]["composition"]), t=g, stream=True, kept=True)
        c.sims.append(rec)
        S["live"][did] = rec

    # ------------------------------------------------------------------------------------------ stages (money noted)
    def _stage_tick(self, g):
        before = {k: (getattr(c, "scale_usd", 0.0), c._stage_cash) for k, c in self.campaigns.items()}
        super()._stage_tick(g)
        for k, c in self.campaigns.items():
            d = getattr(c, "scale_usd", 0.0) - before[k][0]
            r = c._stage_cash - before[k][1]
            if abs(d - r) > 1e-9:                    # the gas lot's metal and the application test's fee
                c.cash.append((g, d - r, "stages", "stage (gas-lot metal, application test)"))
            c._rs = {}

    # ------------------------------------------------------------------------------------------ reports
    def _spend_events(self):
        """Every dollar of the run as dated events, by category: each campaign's own (``CATS``, from its cash
        ledger) and the lab's (``LAB_CATS``). Built once, after the run.

        Lab-level money, on a cash basis:
        * capital: the build-out's payments (new, and used with its refurbishment); none in a lab that builds nothing;
        * facility: the space's fit-out (the build-out's 'services' item), then each item's service contract,
          electricity and floor space from the day it is online (the space's open floor from the day the space is
          ready); for the equipment a lab that builds nothing already has, from day 0. Booked at each week's end;
        * labour: the lab's fixed staff from day 0 (twin/econ.py STAFF), booked at each week's end, and the hands-on
          hours booked on people, at the student rate.
        Depreciation of equipment a lab already owns and of the building is not cash and is left to the analysis."""
        if getattr(self, "_spend_ev", None) is not None:
            return self._spend_ev
        from twin import econ as E
        F = self.fac4
        camps = {}
        for k, c in self.campaigns.items():
            by = {cat: [] for cat in CATS}
            for t, u, cat, _ in c.cash:
                if t <= self.h + 1e-9:
                    by[cat].append((t, u))
            camps[k] = {cat: sorted(v) for cat, v in by.items()}
        built = self.plan != "external"
        fkey = "vertical_lab" if built else "proposed"
        lab = {cat: [] for cat in LAB_CATS}
        for t, u, what in F.sched["payments"]:
            if t > self.h:
                continue
            if what.split(" ")[0] == "services":
                lab["facility"].append((t, u))
            elif "(used)" in what or "(refurbishment)" in what:
                lab["capital_used"].append((t, u))
            else:
                lab["capital_new"].append((t, u))
        rate_fac = []                                 # (from hour, $ a year)
        for it in E.items(fkey):
            a = E.item_annual(it)
            yr = a["service"] + a["utilities"] + a["space"]
            if yr <= 0:
                continue
            if built:
                rec = F.sched["items"].get(it.key)
                if rec is None and it.kind != "owned":
                    continue
                t0 = rec["online_h"] if rec is not None else 0.0
            else:
                t0 = 0.0
            rate_fac.append((t0, yr))
        open_yr = E.OPEN_FLOOR_M2[E.facility_key(fkey)][0] * E.RATES["space_om_usd_m2_yr"][0]
        rate_fac.append(((F.sched.get("room_h") or 0.0) if built else 0.0, open_yr))
        staff_yr = E.fixed_labour(fkey)
        op = F.res.get("operator")
        op_h = sorted((j[0], j[1] - j[0]) for j in (op.jobs if op is not None else []) if j[0] < self.h)
        hourly = E.hourly("grad_student")
        nw = int(math.ceil(self.h / WEEK)) + 1
        for i in range(1, nw):
            a, b = (i - 1) * WEEK, min(i * WEEK, self.h)
            if b <= a:
                break
            fa = sum(yr * max(0.0, b - max(a, t0)) / E.H_YEAR for t0, yr in rate_fac)
            lab["facility"].append((b, fa))
            lab["labour"].append((b, staff_yr * (b - a) / E.H_YEAR))
        for t0, hh in op_h:
            lab["labour"].append((t0, hh * hourly))
        lab = {cat: sorted(v) for cat, v in lab.items()}
        basis = dict(facility_key=fkey, staff_usd_yr=round(staff_yr, 2), student_usd_h=round(hourly, 2),
                     operator_h=round(sum(h for _, h in op_h), 1), open_floor_usd_yr=round(open_yr, 2),
                     fixed_annual_round3={kk: round(vv, 2) for kk, vv in E.annual_cost(fkey).items()})
        self._spend_ev = (camps, lab, basis)
        return self._spend_ev

    def spend_at(self, t_h: float) -> dict:
        """Cumulative spend up to hour ``t_h``, by category."""
        camps, lab, _ = self._spend_events()
        tot = lambda ev: round(sum(u for t, u in ev if t <= t_h + 1e-9), 2)
        return dict(campaigns={k: {cat: tot(v) for cat, v in d.items()} for k, d in camps.items()},
                    lab={cat: tot(v) for cat, v in lab.items()})

    def spend_report(self) -> dict:
        """Cumulative spend by week and category (``_spend_events``), the totals at the horizon, and the campaigns'
        shares of the lab's fixed costs (2 : 1, as round 5's budgets were)."""
        camps, lab, basis = self._spend_events()
        nw = int(math.ceil(self.h / WEEK)) + 1
        days = [7 * i for i in range(nw)]

        def cum(ev):
            out, tot, i = [], 0.0, 0
            for d in days:
                while i < len(ev) and ev[i][0] <= d * H + 1e-9:
                    tot += ev[i][1]
                    i += 1
                out.append(round(tot, 2))
            return out

        cw = {k: {cat: cum(v) for cat, v in d.items()} for k, d in camps.items()}
        lw = {cat: cum(v) for cat, v in lab.items()}
        end = self.spend_at(self.h)
        share = {k: REFERENCE_USD.get(k, 1.0) / sum(REFERENCE_USD.get(x, 1.0) for x in self.campaigns)
                 for k in self.campaigns}
        return dict(days=days, campaigns=cw, lab=lw, totals=end, fixed_share=share, basis=basis,
                    reference_usd={k: REFERENCE_USD.get(k) for k in self.campaigns},
                    stock_left_usd={k: c.stock_report(self.h)["left_usd"] for k, c in self.campaigns.items()})

    def report6(self) -> dict:
        """A run's record beyond round 4's: round 5's fields (the build-out's window and used items, the atomizer,
        decisions, stock, shared stations, counters) and round 6's (money, crucibles, the stream, idle causes)."""
        F = self.fac4
        sch = F.sched
        R = F.res["atomizer"]
        jobs = [j for j in R.jobs if j[0] < self.h]
        cr = {}
        for fam, pool in F.pools.items():
            ds = F.derived_start_h(fam)
            cr[fam] = dict(pool.report(self.h), order_n=F.crucibles[fam]["order_n"], life=F.crucibles[fam]["life"],
                           late_d=F.crucibles[fam]["late_d"],
                           derived_cycle_start_d=None if ds is None else round(ds / H, 2))
        starts = [v["derived_cycle_start_d"] for v in cr.values() if v["derived_cycle_start_d"] is not None]
        hp = self.hpc
        return dict(lab=self.lab, plan=self.plan, notes=list(NOTES_APPLIED), room_h=sch.get("room_h"),
                    money=dict(limited=False, gates_removed=sorted(GATES_REMOVED), gates_kept=sorted(GATES_KEPT)),
                    used=dict(source=sch.get("used_source"), n_market=len(F.market_used), file_sha256=F.market_sha,
                              items=sch.get("used", {})),
                    atom=dict(switch_h=F.atom_switch_h, cycle=F.atom_cycle,
                              runs=sum(1 for j in jobs if j[3] == "atomize"), runs_by=R5._count_by(jobs, "atomize")),
                    crucibles=dict(families=cr, cell_d=None if F.atom_switch_h is None else
                                   round(F.atom_switch_h / H, 2),
                                   derived_cycle_start_d=max(starts) if starts else None,
                                   item=dict(key=ITEM.key, price_usd=ITEM.price, lead_d=ITEM.lead_days,
                                             lead_gsd=ITEM.lead_gsd, source=CRUCIBLE_SOURCE)),
                    decisions=dict(level=self.dec.level, modes=self.dec.modes,
                                   held={k: R5._held_stats(v) for k, v in self.held_log.items()},
                                   held_end=getattr(self, "_held_end", None)),
                    stock={k: c.stock_report(self.h) for k, c in self.campaigns.items()},
                    counters={k: dict(R5.counters(c), designed=len(c.designs) + c._gone)
                              for k, c in self.campaigns.items()},
                    shared=R5.shared_use(self), idle=idle_report6(self), spend=self.spend_report(),
                    hpc=dict(scale=hp.get("scale", 1), cores=hp["cores"], core_h=hp["core_h"], keep=hp["keep"],
                             add_per_day=hp["add_per_day"], capacity_per_day=hp["cores"] * 24.0 / hp["core_h"],
                             utilization=1.0,
                             campaigns={k: dict(evaluated=round(S["evaluated"]), materialized=S["materialized"],
                                                evicted=S["evicted"], dropped_from_memory=c._gone,
                                                designs_in_memory=len(c.designs),
                                                own_sims=sum(1 for x in c.sims if not x.get("stream")),
                                                pool_weekly=S["pool_sizes"][:120])
                                        for (k, S), c in zip(self.stream.items(), self.campaigns.values())}))


# ------------------------------------------------------------------------------------------------- idle stretches
def _could_start(F, keys, k, a_d, b_d, horizon_h) -> bool:
    """Whether campaign ``k`` could have started a job at one of these stations in days [a, b): a partner's standing
    slot went by unused (the stretch is longer than the slot's cadence plus a week, and fewer sessions were booked
    than offered); a station with fixed starts (the atomizer run by people) offered the campaign a start; or a
    station that works by the hour was busy less than half its open hours. Stations online for under a week of the
    stretch don't count."""
    A, B = a_d * H, min(b_d * H, horizon_h)
    for key in keys:
        r = F.res[key]
        lo = max(A, r.online_h)
        if B - lo < 7 * H:
            continue
        sts = [r.st]
        if isinstance(r, R5.ResourceAtom):
            sts = [(r.st_manual, lo, min(B, r.switch_h if r.switch_h is not None else B)),
                   (r.st_auto, max(lo, r.switch_h if r.switch_h is not None else B), B)]
        else:
            sts = [(r.st, lo, B)]
        for st, x, y in sts:
            if y - x < 7 * H:
                continue
            if st.per_period:
                n, days = st.per_period
                used = sum(1 for s in r.period_starts if x <= s < y)
                if (y - x) >= (days / n + 7) * H and int((y - x) / (days * H / n)) - used >= 1:
                    return True
            elif st.starts and st.hours != "24/7":
                wd = (st.campaign_weekdays or {}).get(k, st.weekdays)
                d0, d1 = int(math.ceil(x / H)), int(y // H)
                if any((wd is None or d % 7 in wd) and d % 7 < 5 for d in range(d0, d1)):
                    return True
            else:
                busy = sum(min(j[1], y) - max(j[0], x) for j in r.jobs if j[0] < y and j[1] > x) / max(st.units, 1)
                if busy < 0.5 * R4._cal_hours(st.hours, x, y):
                    return True
    return False


def idle_report6(tw) -> dict:
    """Round 5's idle report without money as a cause: for each campaign, stretches of at least a week with no start
    at its pacing stations (the atomizer; its first fabrication step), each with a cause read off the daily log:
    sign-off, capacity (a busy station, no crucible) or the WIP limit, decision time (results waiting on a person),
    or the policy waiting (asked, proposed nothing it could start, nothing turned away; 'results in flight' when it
    had actions pending). A stretch of two weeks or more is flagged when the policy was waiting and the campaign
    could have started a job (``_could_start``): with money no longer a limit, nothing else explains it. Round 5
    called a station free when it was busy under half of every hour of the day, which flags the gap between a
    partner's monthly sessions; round 6 counts the sessions offered."""
    F = tw.fac4
    nd = int(tw.h // H) + 1
    out = {}
    for k, c in tw.campaigns.items():
        fab = ("utah_midi", "lpbf_3dpt") if k == "flaime_al" else ("utah_mxlab", "mines_x2")
        keys = {"atomizer": [], "fab": []}
        starts = {"atomizer": np.zeros(nd), "fab": np.zeros(nd)}
        busy = {"atomizer": np.zeros(nd), "fab": np.zeros(nd)}
        for key, r in F.res.items():
            role = key.split("@")[0]
            grp = "atomizer" if role == "atomizer" else ("fab" if role in fab else None)
            if grp is None:
                continue
            keys[grp].append(key)
            for j in r.jobs:
                if j[2] == k and j[0] < tw.h and not (isinstance(j[4], dict) and j[4].get("helper_for")):
                    starts[grp][int(j[0] // H)] += 1
                a, b = j[0], min(j[1], tw.h)
                t = a
                while t < b - 1e-9:
                    d = int(t // H)
                    e = min(b, (d + 1) * H)
                    busy[grp][d] += (e - t) / max(r.st.units, 1)
                    t = e
        D = tw.daily[k]
        res = {}
        for grp in ("atomizer", "fab"):
            stretches, run0 = [], None
            for d in range(nd + 1):
                idle = d < nd and starts[grp][d] == 0
                if idle and run0 is None:
                    run0 = d
                if (not idle) and run0 is not None:
                    if d - run0 >= R5.IDLE_MIN_D:
                        stretches.append((run0, d))
                    run0 = None
            items = []
            for a, b in stretches:
                cnt = {}
                asked = none = 0
                pend = []
                for d in range(a, b):
                    x = D.get(d)
                    if x is None:
                        cnt["not asked (before start)"] = cnt.get("not asked (before start)", 0) + 1
                        continue
                    stt = x["st"]
                    asked += 1 if x["asked"] else 0
                    none += 1 if (x["asked"] and not x["proposed"]) else 0
                    pend.append(x["pending"])
                    if stt.get("signoff"):
                        cause = "sign-off"
                    elif stt.get("capacity") or stt.get("kanban"):
                        cause = "capacity" if stt.get("capacity", 0) >= stt.get("kanban", 0) else "WIP limit"
                    elif x["held"] > 0:
                        cause = "decision time"
                    elif x["pending"] > 0:
                        cause = "policy waiting (results in flight)"
                    else:
                        cause = "policy waiting"
                    cnt[cause] = cnt.get(cause, 0) + 1
                bf = float(np.mean(busy[grp][a:b])) / 24.0 if b > a else 0.0
                main = max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else "?"
                free = _could_start(F, keys[grp], k, a, b, tw.h)
                flag = free and main.startswith("policy waiting") and (b - a) >= 14
                items.append(dict(start_d=a, end_d=b, days=b - a, cause=main, causes=cnt, could_start=bool(free),
                                  days_asked=asked, days_nothing_proposed=none,
                                  pending_median=float(np.median(pend)) if pend else 0.0,
                                  station_busy_frac=round(bf, 3), flag=bool(flag)))
            res[grp] = items
        out[k] = res
    wk = {}
    for k in tw.campaigns:
        D = tw.daily[k]
        nw = int(math.ceil(nd / 7))
        rows = []
        for w in range(nw):
            ds = [D[d] for d in range(w * 7, min(nd, w * 7 + 7)) if d in D]
            if not ds:
                rows.append(None)
                continue
            st = {}
            for x in ds:
                for s, n in x["st"].items():
                    st[s] = st.get(s, 0) + n
            rows.append(dict(spent=ds[-1]["spent"], asked=sum(x["asked"] for x in ds),
                             proposed=sum(x["proposed"] for x in ds), held=max(x["held"] for x in ds),
                             pending=max(x["pending"] for x in ds), st=st))
        wk[k] = rows
    return dict(stretches=out, weekly=wk, min_days=R5.IDLE_MIN_D)
