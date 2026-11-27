"""Round 5 of the twin: two years from the day the money arrives, the automated lab against a conventional lab.

Round 4 counted from the funding with a spending plan, a room that took four months and every station bought new.
Round 5 changes what Sterling asked for on PR 400 (2026-11-27), and what his notes while it ran added (``NOTES``):

* **All money at t = 0.** Each campaign has its whole two-year budget from day 0 (``Campaign5.plan``); no tranches.
* **The facility window.** The new space is ready between day 60 and day 100 (uniform, drawn per seed; a stand-in).
  Equipment is ordered on day 0 and may arrive before then, but installation and commissioning start only when the
  space is ready (``build_schedule5``). Round 4's commissioning, learning curve and breakdowns are kept.
* **Used equipment** for stations with a real used market (``USED_OK``): a shorter lead and a lower price, a higher
  chance of arriving faulty or needing refurbishment. Chosen by a rule (``used_rule``): buy used when the expected
  days saved, against the expected date the space is ready, are at least ``USED['rule_days']``. Every lead, price and
  risk is a stand-in until the BOM has quotes.
* **Experiments from day 0** (round 4's parallel plan): the existing atomizer, BYU's core facilities and the partners,
  moving in house as stations come online.
* **Stock bought early by a reorder-point heuristic** (``stock='reorder'``): for each item a reorder point
  ``s = d L + z sigma_d sqrt(L)`` and an order-up-to level ``S = s + d T`` from its median lead time ``L`` and its
  expected daily use ``d`` (a prior from round 2's standing stock, updated from the campaign's own use as it runs).
  ``stock='lean'`` orders each charge's metal when it is needed (round 3b's lean). Stock-outs and the stock's cost
  are recorded (``Campaign5.stock_report``).
* **Shared equipment as the real process uses it** (``CU_STEPS``, ``AL_STEPS``): copper's deposits are cut by wire
  EDM, heat treated, sectioned, polished, hardness-mapped and PIP-tested, its screen and immersion coupons are
  prepared, and aluminium's builds are sectioned for the crack check. Stand-in hours, marked.
* **Decisions made by people take time** (``DECISIONS``, ``Decide``). A person's decision waits for the next review
  (routine next steps and stopping a test: working days, with batching) or the next weekly meeting (choosing new
  compositions and promoting an alloy), after DAL #256's Friday decision meeting and DAL PR 297's Monday rounds. The
  conventional lab's decisions are all people's; in the automated lab the rule-of-thumb heuristic is a person's
  (weekly meeting) and the optimizers and the funnel decide by themselves, hourly, with a sign-off window for
  expensive steps (gas-atomized lots, full-part tests, any action over ``signoff_usd``).
* **Note 1** (05:37): the conventional lab runs at most 8 atomizations a week (``ATOM_MANUAL``).
* **Note 2** (05:41): the automated lab's atomizer runs 24/7 at a derived cycle per unique composition
  (``ATOM_CYCLE``), a design target, once the cell is integrated (the robots tend it); people run it before.
* **Note 3** (05:51): both campaigns use the automated atomizer as they need it (no weekday split); idle time per
  station and campaign with a cause for each stretch (``idle_report``); unambiguous counters.

Round 4's code is unchanged but for a hook (``Facility4.schedule``), so its results still reproduce. Everything is
simulated: synthetic truths, simulated instruments, assumed capacities, prices, lead times and schedules.
"""
from __future__ import annotations

import heapq
import itertools
import math

import numpy as np

from twin import campaign as C
from twin import facility as fac
from twin import round4 as R4
from twin import supply

H, WEEK = 24.0, 168.0

# ------------------------------------------------------------------------------------------------- the notes
# Sterling's notes on PR 400 while round 5 ran; every row records the ones its set-up includes.
NOTES = {
    "n1": dict(t="2026-11-27T05:37:32Z", comment=7210796066, by="sgbaird",
               text="For the conventional lab, assume at most 8 atomizations per week."),
    "n2": dict(t="2026-11-27T05:41:00Z", comment=7210847455, by="sgbaird",
               text="The automated lab's atomizer runs 24/7 at a much higher rate ... derive the cycle time for a "
                    "unique composition from the lab's record, use it as the design rate, with a sensitivity."),
    "n3": dict(t="2026-11-27T05:51:02Z", comment=7210999554, by="sgbaird",
               text="The automated lab sat idle for long stretches in round 3: its own 24/7 atomizer used by both "
                    "campaigns as needed, not by weekday; idle time per station and campaign with causes; counters."),
}
NOTES["n4"] = dict(t="2026-11-27T06:11:40Z", comment=7211302355, by="sgbaird",
                  text="'Designed' should run at full computational capacity, outside the cost-aware choice: model "
                       "the compute available, keep it running through both years, the simulation nodes not part of "
                       "pKGFN's p or BOFN's cost; report HPC utilization, candidates evaluated, and whether more "
                       "compute would have changed anything.")
NOTES_APPLIED = ("n1", "n2", "n3", "n4")

# ------------------------------------------------------------------------------------------------- note 4: the HPC
# The simulated candidates ("designed") come from a stream that runs on the HPC allocation continuously, outside the
# campaigns' money and outside the acquisitions' cost-aware choice. The open-CALPHAD node (pycalphad, what the
# policies' candidate pools use) scales with cores: 0.05 core-hours a candidate (rounds 1-4's figure), on a stand-in
# allocation of 256 cores (BYU's Office of Research Computing; FLAIME App. 2 counts ~28,000 cores on the cluster),
# is 122,880 candidates a day. Thermo-Calc's nodes are limited by licence seats, not cores, and stay as before.
# The policies can't use that many: the twin keeps a rolling pool of the newest ``keep`` unexplored candidates
# visible to them, ``add_per_day`` new ones a day spread over the day (every candidate the policies make, build or
# test stays visible), and counts the rest as evaluated.
HPC = dict(cores=256, node="sim_open", core_h=0.05, keep=128, add_per_day=64,
           source="stand-in allocation: 256 cores of BYU's Office of Research Computing (FLAIME App. 2: ~28,000 "
                  "cores on the cluster); 0.05 core-h a candidate for the open-CALPHAD node (rounds 1-4)")

# ------------------------------------------------------------------------------------------------- facility window
ROOM_DAYS = (60.0, 100.0)
ROOM_SOURCE = ("stand-in (Sterling, PR 400, 2026-11-27): the facility is ready between day 60 and day 100, drawn per "
               "seed from a uniform distribution; round 4's room took about four months (the atomizer room's 16 weeks)")

# ------------------------------------------------------------------------------------------------- used equipment
# Stations with a real used market (listings on LabX, eBay, machine-tool and instrument dealers). Not listed: the
# Aconity MIDI and InssTek MX-Lab (rare, and the vendors' installation and qualification are tied to new machines),
# the MiR + UR units, the Kardex Shuttles and docks (integration), the doser, sieve cell and machining cell (custom),
# the Plastometrex benchtop (a new product), the CubXL (owned).
USED_OK = {
    "edm": "used wire EDMs (Sodick, Mitsubishi, Makino, Fanuc) are common at machine-tool dealers and on eBay",
    "instron": "used Instron and MTS frames are common on LabX and eBay",
    "zwick": "used zwick frames are listed by dealers",
    "chamber": "used environmental chambers for frames are common",
    "icpms": "used Agilent 7700/7900 ICP-MS are listed on LabX",
    "sem": "used tabletop SEMs (Hitachi TM, Phenom) are listed on LabX",
    "xrd": "used benchtop diffractometers (MiniFlex) are listed on LabX",
    "xrf": "used benchtop XRF is listed on LabX",
    "mastersizer": "used Mastersizer 2000/3000 units are common on LabX",
    "hardness": "used micro-Vickers testers are common",
    "nanoindenter": "used nanoindenters (G200, Hysitron) are listed on LabX",
    "polish": "used Buehler and Struers mounting presses and polishers are common",
    "furnaces": "used box furnaces are common",
    "vhx": "used digital microscopes are listed",
}
USED = dict(lead_w=2.0, lead_sigma=0.35, price_frac=0.45, p_fault=0.25, refurb_w=6.0, refurb_sigma=0.4,
            refurb_frac=0.15, extra_com_w=1.0, rule_days=14.0, room_expected_d=80.0,
            source="stand-ins until the BOM has quotes: a used unit ships 2 weeks after BYU's purchase order (2 "
                   "weeks, DAL PR 266) and costs 45 % of new; 1 in 4 arrives faulty or needs refurbishment (6 weeks, "
                   "15 % of the new price); a week more commissioning (a service engineer's check and calibration)")


def used_rule(k: str) -> dict:
    """Buy item ``k`` used if the expected days saved, against the expected date the space is ready, are at least
    ``rule_days``: the medians the lab would know on day 0 (the quoted leads, the expected readiness), with the risk
    of a fault priced in. An item that arrives new before the space is ready saves nothing used."""
    lead_w, inst_w, com_w, _ = R4.BUILD[k]
    R = USED["room_expected_d"] * H
    new_on = max(lead_w * WEEK, R) + (inst_w + com_w) * WEEK
    arr_u = (R4.PO_W + USED["lead_w"]) * WEEK + USED["p_fault"] * USED["refurb_w"] * WEEK
    used_on = max(arr_u, R) + (inst_w + com_w + USED["extra_com_w"]) * WEEK
    saved = (new_on - used_on) / H
    return dict(ok=k in USED_OK and saved >= USED["rule_days"], expected_days_saved=round(saved, 1))


def build_schedule5(seed: int, plan: str, opts: dict | None = None) -> dict:
    """Round 4's build-out with the facility window and used equipment. Every item is ordered on day 0; the new-item
    lead draws are round 4's for the same seed. Each item is installed when it and the space are there."""
    from twin import econ as E
    opts = opts or {}
    items = {it.key: it for it in E.items("vertical_lab")}
    rng = np.random.default_rng(60_000 + seed)
    out = dict(items={}, payments=[], stations={}, cell_h=None, start_h=0.0, room_h=None, used={})
    if plan == "external":
        return out
    t_arr = {}
    for k in sorted(R4.BUILD):
        lead_w, inst_w, com_w, src = R4.BUILD[k]
        t_arr[k] = lead_w * WEEK * math.exp(rng.normal(0, R4.LEAD_SIGMA)) if lead_w > 0 else 0.0
    room_h = float(np.random.default_rng(61_000 + seed).uniform(*ROOM_DAYS)) * H
    out["room_h"] = room_h
    ru = np.random.default_rng(62_000 + seed)
    allow_used = bool(opts.get("used", True))
    for k in sorted(R4.BUILD):
        lead_w, inst_w, com_w, src = R4.BUILD[k]
        # used draws for every item in a fixed order, so the stream doesn't depend on the rule
        lu = (R4.PO_W + USED["lead_w"]) * WEEK * math.exp(ru.normal(0, USED["lead_sigma"]))
        fault = bool(ru.random() < USED["p_fault"])
        refurb = USED["refurb_w"] * WEEK * math.exp(ru.normal(0, USED["refurb_sigma"]))
        if k not in items:
            continue
        it = items[k]
        if k == "cubxl" or it.kind == "owned":
            continue
        if k == "services":                       # the space itself: ready in the facility window
            out["items"][k] = dict(name=it.name, capex=it.capex, order_h=0.0, arrive_h=room_h, install_h=room_h,
                                   commission_h=room_h, online_h=room_h, used=False, source=ROOM_SOURCE)
            dep = R4.DEPOSIT[0] if it.capex >= R4.DEPOSIT[1] else 0.0
            if dep:
                out["payments"].append((0.0, it.capex * dep, k))
            out["payments"].append((room_h, it.capex * (1 - dep), k))
            continue
        inst_n = max(t_arr[k], room_h)
        on_new = inst_n + (inst_w + com_w) * WEEK
        rule = used_rule(k)
        if allow_used and rule["ok"]:
            arr = lu + (refurb if fault else 0.0)
            inst0 = max(arr, room_h)
            online = inst0 + (inst_w + com_w + USED["extra_com_w"]) * WEEK
            price = it.capex * USED["price_frac"]
            ref_usd = it.capex * USED["refurb_frac"] if fault else 0.0
            out["payments"].append((0.0, price, k + " (used)"))
            if ref_usd:
                out["payments"].append((lu, ref_usd, k + " (refurbishment)"))
            out["used"][k] = dict(name=it.name, fault=fault, arrive_h=round(arr, 1), online_h=round(online, 1),
                                  online_new_h=round(on_new, 1), days_bought=round((on_new - online) / H, 1),
                                  expected_days_saved=rule["expected_days_saved"], capex_new=it.capex,
                                  usd_paid=round(price + ref_usd, 2), usd_saved=round(it.capex - price - ref_usd, 2),
                                  market=USED_OK[k])
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


# ------------------------------------------------------------------------------------------------- the atomizer
# Note 1: the conventional lab, and the automated lab before its cell is integrated (people run it): at most 8 runs a
# week, two attended starts a day (08:00 and 13:00), aluminium Mon-Wed and copper on Friday (DAL #256 puts copper on
# Fridays "so the ~1 h clean that follows each one doesn't eat into an Al week"; Thursday is #256's flex slot).
ATOM_MANUAL = dict(hours="day", starts=(8.0, 13.0), sat_starts=None, attended_h=1.0, weekdays=None,
                   campaign_weekdays={"flaime_al": (0, 1, 2), "onr_cu": (4,)},
                   source="note 1 (sgbaird, PR 400, 2026-11-27 05:37): at most 8 atomizations a week; 2 attended "
                          "starts a day, Al Mon-Wed, Cu Fri as DAL #256, Thursday its flex slot")
# Note 2: the automated lab's atomizer, 24/7, any campaign at any time (note 3), booked for its cycle per unique
# composition. ``derived`` is the cycle derived from the lab's record (notes/twin_round5.md, section 2): with
# pre-coated spare crucibles swapped in (the BN coat dries overnight, so a crucible is out of service 14-16 h), an
# aluminium run is about 2.2 h end to end (charge in 5 min, washes 20, melt 8, pour 4, about 1 h of cooling with the
# powder collected meanwhile, then the crucible swap, lid and leak check), about 76 a week; bronze 2.5-3 h, 3.4 h in
# the twin's yield model. Those are the twin's own per-run hours (twin/instruments/atomize_yield.charge_plan: 2.21 h
# Al, 3.36 h Cu at 225 cm3), so ``derived`` books the charge plan's hours (``None``). ``3h`` is the note's figure,
# 56 a week. ``slow``: DAL #256's untimed step estimates one after another (2.5-3.5 h run, 1 h cool, 1-2 h clean),
# 4.5-6.5 h, and an hour more for copper. A switch between an aluminium and a copper melt costs ``changeover_h``
# (the SOP's "full clean (about 1 h)" plus the copper crucible, nozzle and booster swap: 1-2 h).
ATOM_CYCLE = {"derived": dict(flaime_al=None, onr_cu=None, changeover_h=1.5),
              "3h": dict(flaime_al=3.0, onr_cu=3.0, changeover_h=1.5),
              "slow": dict(flaime_al=5.5, onr_cu=6.5, changeover_h=2.0)}
ATOM_RUN_H = {"flaime_al": 2.209, "onr_cu": 3.357}   # the charge plan's hours at 225 cm3


class ResourceAtom(R4.Resource4):
    """The atomizer: run by people (``st_manual``) until ``switch_h``, then 24/7 by the cell (``st_auto``)."""

    def __init__(self, old: R4.Resource4, st_manual, st_auto, switch_h, changeover_auto_h):
        super().__init__(st_manual, np.random.default_rng(0), 0.0, 0.0, old.curve, old.n0)
        self.down = list(old.down)                # round 4's breakdown draws for the same seed
        self.st_manual, self.st_auto, self.switch_h = st_manual, st_auto, switch_h
        self.changeover_auto_h = changeover_auto_h

    def auto_at(self, t) -> bool:
        return self.switch_h is not None and t >= self.switch_h - 1e-9

    def find(self, t, dur, campaign, changeover_h=0.0, empty=False):
        if self.switch_h is None:
            self.st = self.st_manual
            return super().find(t, dur, campaign, changeover_h, empty)
        if t < self.switch_h:
            self.st = self.st_manual
            s, d, i = super().find(t, dur, campaign, changeover_h, empty)
            if s < self.switch_h:
                return s, d, i
            t = self.switch_h
        self.st = self.st_auto
        return super().find(t, dur, campaign, self.changeover_auto_h if changeover_h > 0 else 0.0, empty)


# ------------------------------------------------------------------------------------------------- decision windows
# A person's decision waits for the next decision point after its results are in. Two kinds (Sterling, PR 400:
# "choosing new compositions, promoting an alloy, stopping a test"):
#   * review: routine next steps on a lot, part or deposit, and stopping a test, on working days, with batching
#     (released when at least ``batch_n`` results wait, or the oldest has waited ``batch_max_h``);
#   * meeting: choosing new compositions and promoting an alloy: the results that score an alloy (tensile tests,
#     copper's screen, tensile and immersion) are seen at the weekly meeting. DAL #256 (the schedule Sterling moved to
#     #256 on Nov 24): "Friday optimizer update: refit on the data through Thursday and pick next week's batch"; "The
#     30-min meeting on Friday, so it doubles as the decision meeting"; DAL #277: "Weekly 30 minute meetings"; DAL
#     PR 297 (bofn-clocked): "rounds of 4 builds, decided at Monday 09:00 meetings once the previous round's bars are
#     back" (the slow case). "Powder handled within 48 h" (#256): the nominal review.
# Sign-off (the automated lab): an expensive step waits for a person's approval at the next working-day 10:00 at least
# 2 h after it is first proposed (``extra_days`` more working days in the slow case). Day 0 is a Monday.
DECISIONS = {
    "none": None,
    "nominal": dict(
        conventional=dict(review=dict(h=13.0, days=(0, 1, 2, 3, 4), batch_n=2, batch_max_h=40.0),
                          meeting=dict(h=13.0, days=(4,), every_w=1)),
        vertical_human=dict(review=None, meeting=dict(h=13.0, days=(4,), every_w=1)),
        signoff=dict(h=10.0, extra_days=0, usd=2000.0),
        source="DAL #256 (Friday decision meeting, data through Thursday; powder within 48 h); DAL #277 (weekly "
               "30-minute meetings); working days only"),
    "slow": dict(
        conventional=dict(review=dict(h=13.0, days=(1, 3), batch_n=4, batch_max_h=100.0),
                          meeting=dict(h=9.0, days=(0,), every_w=2)),
        vertical_human=dict(review=None, meeting=dict(h=9.0, days=(0,), every_w=2)),
        signoff=dict(h=10.0, extra_days=2, usd=2000.0),
        source="DAL PR 297 (Monday 09:00 rounds), every other week; reviews twice a week in batches of 4"),
}
MEETING_TYPES = {"test", "cu_test"}
HUMAN_POLICIES = {"heuristic"}          # a person's rule of thumb in either lab (Sterling, PR 400)


def _at(g, h, days, every_w=1):
    day = int(g // H)
    if day % 7 not in days or (every_w > 1 and (day // 7) % every_w != 0):
        return False
    return abs((g - day * H) - h) < 0.5


class Decide:
    """Who decides each campaign's next step, and when a person's decision can be made."""

    def __init__(self, level: str, lab: str, modes: dict):
        self.level, self.lab, self.modes = level, lab, modes
        self.cfg = DECISIONS.get(level)

    def window(self, k):
        if self.cfg is None or self.modes.get(k) != "human":
            return None
        return self.cfg["conventional" if self.lab == "conventional" else "vertical_human"]

    def classify(self, k, p):
        """None (the policy sees it now), 'review' or 'meeting'."""
        w = self.window(k)
        if w is None or p.get("type") == "imm_final_book":
            return None
        cls = "meeting" if p.get("type") in MEETING_TYPES else "review"
        if w.get(cls) is None:
            return None
        return cls

    def due(self, k, cls, g, oldest_h, n) -> bool:
        w = self.window(k)[cls]
        if cls == "meeting":
            return _at(g, w["h"], w["days"], w.get("every_w", 1))
        if not _at(g, w["h"], w["days"]):
            return False
        return n >= w["batch_n"] or g - oldest_h >= w["batch_max_h"]

    def signoff_usd(self, k):
        if self.cfg is None or self.modes.get(k) != "auto":
            return None
        return self.cfg["signoff"]["usd"]

    def signoff_time(self, t0) -> float:
        s = self.cfg["signoff"]
        t = math.ceil(t0 + 2.0)
        extra = s["extra_days"]
        for _ in range(24 * 40):
            day = int(t // H)
            if day % 7 < 5 and abs((t - day * H) - s["h"]) < 0.5:
                if extra <= 0:
                    return float(t)
                extra -= 1
            t += 1.0
        return float(t)

    def stage_ok(self, k, g) -> bool:
        """A stage decision (a gas-atomized lot, the network's verdict, the full-part test) at the daily tick g: a
        person's campaign at the tick after a meeting; the automated lab's after a working day's sign-off."""
        if self.cfg is None:
            return True
        w = self.window(k)
        if w is not None:
            m = w["meeting"]
            return any(_at(g - dh, m["h"], m["days"], m.get("every_w", 1)) for dh in range(1, 25))
        day = int((g - 1.0) // H)
        return day % 7 < 5


# ------------------------------------------------------------------------------------------------- shared steps
# (main steps: their end is the result; side steps: booked after the result, charged, not waited for). Hours added in
# round 5 are stand-ins, and so is which steps a real process needs (notes/twin_round5.md, section 4).
CU_STEPS = dict(
    preplaced=([("utah_mxlab", 4.0), ("prep", 1.0), ("byu_sem", 1.0)], []),
    small_ded=([("utah_mxlab", 4.0), ("prep", 1.5), ("byu_sem", 2.0)], [("hardness", 0.5)]),
    blend_ded=([("doser", 0.5), ("utah_mxlab", 3.0), ("prep", 1.0), ("byu_sem", 1.0)], [("hardness", 0.25)]),
    large_vcl=([("utah_mxlab@vcl", 8.0), ("edm", 1.5), ("furnace", 3.0), ("prep", 1.5), ("byu_sem", 1.0)],
               [("hardness", 0.5), ("pip", 0.5), ("byu_icpms", 0.1)]),
    large_mines=([("mines_x2", 5.0), ("edm", 1.5), ("furnace", 3.0), ("prep", 1.5), ("byu_sem", 2.0)],
                 [("hardness", 0.5), ("pip", 0.5), ("byu_icpms", 0.1)]),
    screen=([("prep", 0.5), ("cubxl", 1.2), ("byu_icpms", 0.1)], []),
    immersion_in=([("prep", 0.5), ("immersion", 720.0)], []),
    immersion_out=([("prep", 1.0), ("byu_sem", 1.0), ("byu_icpms", 0.4)], []),
    tensile=([("shop", 1.0), ("tensile", 0.6)], []),
)
AL_STEPS = dict(print=([("utah_midi", 5.0), ("density", 0.5), ("prep", 1.0), ("byu_sem", 1.0)], []))
STEPS_ADDED = {
    "Cu small DED, pre-placed and blend deposits": "sectioned, mounted and polished (prep 1-1.5 h) before the SEM: "
        "density, cracks, dilution, beta' and grain size are read off a polished cross-section; micro-Vickers on "
        "the section (0.25-0.5 h, not waited for)",
    "Cu large DED (1 kg in house, 2 kg at Mines)": "wire EDM (1.5 h) to cut the block off its substrate and cut bar "
        "blanks, coupons and a section; heat treatment (3 h, a temper anneal before testing, as for NAB-type "
        "alloys); prep (1.5 h) before the SEM; then hardness, a PIP map on the section and ICP-MS of the deposit "
        "(booked, not waited for)",
    "Cu corrosion screen and immersion": "the coupon face ground and polished (prep 0.5 h) before the CubXL or the "
        "vials; after 30 days the coupon is sectioned (prep 1 h) for the SEM's selective-attack depth",
    "Al builds": "a cube sectioned and polished (prep 1 h) for the crack check, which reads a polished section",
    "unchanged": "Cu tensile (machining 1 h, frames 0.6 h; blanks already cut by EDM), Cu powder (cups, doser, "
                 "atomizer, sieve, PSD, SEM/EDS; ICP-MS on request), Al test, promote, PIP and section",
}

# ------------------------------------------------------------------------------------------------- stock
REORDER = dict(z=1.65, cv=1.0, cover_d=30.0, prior_w_d=30.0, window_d=60.0, cap_frac=0.2, burn_window_d=30.0,
               prior_scale={"vertical": 1.0, "conventional": 0.7},
               source="a reorder point with safety stock (Silver, Pyke & Thomas 2017, ch. 6): s = dL + z "
                      "sqrt(L sd(d)^2 + d^2 sd(L)^2), z = 1.65 (a 95 % cycle service level), sd(d) = d (lumpy demand: "
                      "a charge at a time), sd(L) = L ln(gsd) from the item's lead spread; order up to s + 30 days "
                      "of use; L the item's median lead plus the office's 3 days; d "
                      "from round 2's standing stock (about a month's use at the vertical lab's pace; 0.7 of it "
                      "for the conventional lab's 8 runs a week), blended with the last 60 days' use as the "
                      "campaign runs, or the last 30 days' if higher; checked at every charge and once a day. Three money "
                      "rules, without which the first runs ended with $110k of aluminium's stock unused, and copper's "
                      "stocked arm spent its money on plates and nozzles by day 231 and reached its targets in fewer "
                      "seeds than its lean arm: no item is stocked beyond the days the money left lasts at the last 30 "
                      "days' rate of spending, or beyond the campaign's end; stock never spends the money kept for the work "
                      "in progress; and the stock on hand and on order is worth at most 20 % of the money left")


# ------------------------------------------------------------------------------------------------- facility
class Facility5(R4.Facility4):
    """Round 4's facility with round 5's build-out (facility window, used equipment) and atomizer (notes 1-3)."""

    def __init__(self, plan: str, seed: int, horizon_h: float, opts: dict | None = None):
        opts = dict(opts or {})
        self.lab = opts.get("lab", "vertical")
        super().__init__(plan, seed, horizon_h, opts)
        self.kind = f"r5_{self.lab}_{plan}"
        old = self.res["atomizer"]
        stm = fac.Station(**dict(old.st.__dict__))
        for f_, x in ATOM_MANUAL.items():
            setattr(stm, f_, x)
        cyc = ATOM_CYCLE[opts.get("atom", "derived")]
        sta = fac.Station(**dict(old.st.__dict__))
        for f_, x in dict(hours="24/7", starts=None, sat_starts=None, attended_h=None, weekdays=None,
                          campaign_weekdays=None,
                          source=f"note 2: 24/7, {opts.get('atom', 'derived')} cycle per unique composition (a "
                                 f"design target), both campaigns as needed (note 3)").items():
            setattr(sta, f_, x)
        switch = self.cell_h if (self.lab == "vertical" and plan in ("wait", "parallel")) else None
        self.atom_switch_h = switch
        self.atom_cycle = cyc
        self.res["atomizer"] = ResourceAtom(old, stm, sta, switch, cyc["changeover_h"])

    def schedule(self, seed, plan) -> dict:
        return build_schedule5(seed, plan, self.opts)

    def adjust(self, station, hours, what, campaign):
        if station == "atomizer" and what == "atomize":
            R = self.res["atomizer"]
            cyc = self.atom_cycle.get(campaign)
            if R.auto_at(self.now) and cyc is not None:
                return cyc * hours / ATOM_RUN_H[campaign]
            return hours
        return super().adjust(station, hours, what, campaign)

    def expected_result(self, k, t, hours, campaign, what):
        """Round 4's estimate, but a long job on a day calendar is found in days of at most 8 h, as ``_route``
        books it (round 4 searched for it in one piece, which a day calendar can never fit: 'could not book')."""
        r = self.res[k]
        st = r.st
        h = self.adjust(k, hours, what, campaign) * r.factor()
        if st.hours == "24/7" or st.attended_h is not None or h <= 8.0:
            return super().expected_result(k, t, hours, campaign, what)
        t0 = t + self.ship.get(k, (0.0, 0.0))[0]
        if st.external and st.booking_days:
            t0 += st.booking_days * H
        left, tt, s0 = h, t0, None
        while left > 1e-9:
            s, d, _ = r.find(tt, min(left, 8.0), campaign)
            s0 = s if s0 is None else s0
            tt, left = s + d, left - min(left, 8.0)
        p = min(r.p_fail(), 0.9)
        back = st.turnaround_days * H + self.ship.get(k, (0.0, 0.0))[0] * (0.5 if st.external else 0.0)
        return tt + p / (1 - p) * h + back, s0

    def helpers(self, station: str, dur: float, t: float = 0.0) -> list:
        if station == "atomizer":
            R = self.res["atomizer"]
            if R.auto_at(t):
                return [("robot", fac.ROBOT_H[0])] if "robot" in self.res else []
            R.st = R.st_manual
        return super().helpers(station, dur, t)



# ------------------------------------------------------------------------------------------------- campaign
class Campaign5(R4.Campaign4):
    """A campaign of round 5: all its money at t = 0, its stock policy, the shared steps as the real process uses
    them, and sign-offs when its decisions are the automated lab's own."""

    GATE = dict(R4.Campaign4.GATE, screen=([("prep", 0.5)], "cubxl", 1.2),
                immersion=([("prep", 0.5)], "immersion", 720.0))

    def __init__(self, spec, policy, market, facility, horizon_h, lab="vertical"):
        self._dindex, self._vd, self._vi = {}, {}, {}
        super().__init__(spec, policy, market, facility, horizon_h)
        self.lab = lab
        self.dec = None
        self._so_first = {}
        self.stock_mode = "reorder" if spec.stock == "reorder" else "lean"
        self.use_log = {}                           # item -> [(day, qty)]
        self.stockouts = []                         # (day, [items short], days waited)
        self.stock_orders = []                      # (day, item, qty, usd, why, arrival day)
        self.stock_usd = 0.0
        self.n_charges = 0
        if self.stock_mode == "reorder":
            sc = REORDER["prior_scale"].get(lab, 1.0)
            self.prior_d = {k: q / 30.0 * sc for k, q in C.STOCKED[self.key].items()}
            self._reorder(0.0, initial=True)
        else:
            self.prior_d = {}

    # ---------------------------------------------------------------------------------------- designs (note 4)
    def design_id(self, design: dict) -> int:
        """Round 3's design id, with an index (the HPC stream adds tens of thousands of designs)."""
        comp = {e: round(design.get(e, 0.0), 3) for e in self.space.elements}
        key = tuple(sorted(comp.items()))
        i = self._dindex.get(key)
        if i is not None:
            return i
        i = next(self.ids)
        c = self.space.composition(comp)
        self.designs[i] = dict(key=key, composition=c, design=dict(design))
        self._dindex[key] = i
        self._vd[i] = c
        self._vi[i] = self.designs[i]["design"]
        return i

    def view(self, now_h):
        """Round 3's view, with the design maps kept up to date as designs are added instead of rebuilt."""
        designs, self.designs = self.designs, {}
        try:
            v = super().view(now_h)
        finally:
            self.designs = designs
        v["designs"], v["design_inputs"] = self._vd, self._vi
        return v

    def _sim(self, action, now_h, kind):
        """Round 3's simulation, on the HPC allocation (note 4): no money from the campaign."""
        did = self.design_id(action["design"])
        comp = self.designs[did]["composition"]
        proc = {v.name: action["design"][v.name] for v in self.space.process if v.name in action["design"]}
        if kind == "sim_open":
            out = self.truth.sim_open(comp)
        elif kind == "sim_tc":
            out = self.truth.sim_tc(comp, self.rng)
        elif kind == "sim_am":
            out = self.truth.sim_am(comp, proc, self.rng)
        else:
            out = self.truth.sim_heat(comp, proc, self.rng) if hasattr(self.truth, "sim_heat") else \
                self.truth.sim_heatflow(comp, proc, self.rng)
        A = C.ACTIONS[self.key][kind]
        t_res, usd = self._route(A["steps"], now_h, kind, tag=dict(design=did, node="sim"))
        self.charge(now_h, (A["usd"] if kind != "sim_open" else 0.0) + usd, kind)
        self._emit(t_res, dict(type="sim", kind=kind, design=did, proc=proc, out=out))
        return True

    # ---------------------------------------------------------------------------------------- money
    def plan(self, t_h: float) -> float:
        """Round 5: the whole budget from day 0, no spending plan."""
        return self.spec.budget_usd

    # ---------------------------------------------------------------------------------------- stock
    def _lead_d(self, key):
        it = supply.ITEMS[key]
        return it.lead_days + self.market.OFFICE_MEDIAN_DAYS + (3.5 if it.hazmat else 0.0)

    def _rate(self, key, day):
        pr = self.prior_d.get(key, 0.0)
        win = REORDER["window_d"]
        W = REORDER["prior_w_d"] * math.exp(-day / win)
        L = self.use_log.get(key, ())
        used = sum(q for d, q in L if d >= day - win)
        span = min(day, win)
        r60 = (pr * W + used) / (W + span) if W + span > 1e-9 else pr
        if day >= 30.0:                          # react to a surge (the cell's 24/7 atomizer) within a month
            r30 = sum(q for d, q in L if d >= day - 30.0) / 30.0
            return max(r60, r30)
        return r60

    def _levels(self, key, day):
        d = self._rate(key, day)
        L = self._lead_d(key)
        sd_L = L * math.log(supply.ITEMS[key].lead_gsd)          # the lead's spread (lognormal, gsd)
        ss = REORDER["z"] * math.sqrt(L * (REORDER["cv"] * d) ** 2 + (d * sd_L) ** 2)
        s = d * L + ss
        return d, s, s + d * REORDER["cover_d"]

    def _place(self, key, q, day, why):
        it, m = supply.ITEMS[key], self.market
        price = m.price(it, day)
        lt, back = m.lead_time(it, day)
        lt += m.office_delay()
        fee = 0.0
        if it.hazmat:
            fee += 45.0 + (m.rng.uniform(100, 300) if "4.2" in it.hazmat else 0.0)
        if m.rng.random() < it.p_fail:
            lt += it.fail_days
            price *= it.fallback_mult
            back = True
        o = supply.Order(key, q, q * price + fee, day, day + lt, back, self.key)
        self.stores.orders.append(o)
        self.charge(day * H, o.cost, f"order {key} {q:.3g} ({why})")
        self.stock_usd += o.cost
        self.stock_orders.append((round(day, 2), key, round(q, 4), round(o.cost, 2), why, round(day + lt, 2)))
        return o

    def _stock_value(self, day):
        v = 0.0
        for k in set(self.prior_d) | set(self.use_log):
            if k in supply.ITEMS:
                q = max(self.stores.on_hand(k, day), 0.0) + self.stores.due(k, day)
                if q > 0:
                    v += q * self.market.price(supply.ITEMS[k], day)
        return v

    def _money_days(self, day):
        """Days the money left lasts at the last 30 days' rate of spending (no limit at the start)."""
        if day < REORDER["burn_window_d"]:
            return 1e9
        w = REORDER["burn_window_d"]
        burn = sum(u for t, u, _ in self.ledger if t >= (day - w) * H) / w
        return self.budget_left / burn if burn > 1e-6 else 1e9

    def _reorder(self, day, keys=None, initial=False):
        keys = sorted(set(keys) if keys is not None else (set(self.prior_d) | set(self.use_log)))
        cap = REORDER["cap_frac"] * max(self.budget_left, 0.0) if REORDER["cap_frac"] else float("inf")
        # never spend on stock the money kept for the work in progress (the WIP rule's reserve)
        room_wip = self.budget_left - self.wip_reserve(day * H)
        val = None
        mdays = self._money_days(day)
        for key in keys:
            if key not in supply.ITEMS:
                continue
            d, s, S = self._levels(key, day)
            if d <= 0:
                continue
            S = min(S, d * min(mdays, max(self.horizon_h / H - day, 0.0)))
            pos = self.stores.on_hand(key, day) + self.stores.due(key, day)
            if pos <= s + 1e-12 and S > pos + 1e-9:
                it = supply.ITEMS[key]
                q = max(S - pos, it.moq)
                if val is None:
                    val = self._stock_value(day)
                price = self.market.price(it, day)
                room = min(cap - val, room_wip)
                if q * price > room:
                    q = room / price if price > 0 else 0.0
                    if q < it.moq - 1e-12:
                        self.stock_capped = getattr(self, "stock_capped", 0) + 1
                        continue
                o = self._place(key, q, day, "initial" if initial else "reorder")
                val += o.cost
                room_wip -= o.cost

    def _materials(self, bill, now_h):
        day = now_h / H
        short = sorted(k for k, q in bill.items() if self.stores.on_hand(k, day) < q - 1e-9)
        reorder = self.stock_mode == "reorder"
        cost, ready_d, placed = self.stores.ensure(bill, day, spare=1.0 if reorder else self.spare)
        for o in placed:
            self.charge(now_h, o.cost, f"order {o.item} {o.qty:.3g}" + (" (stock-out)" if reorder else ""))
            if reorder:
                self.stock_usd += o.cost
                self.stock_orders.append((round(day, 2), o.item, round(o.qty, 4), round(o.cost, 2), "stock-out",
                                          round(o.arrival_day, 2)))
        if short:
            self.stockouts.append((round(day, 2), short, round(max(ready_d - day, 0.0), 2)))
        self.stores.consume(bill)
        for k, q in bill.items():
            self.use_log.setdefault(k, []).append((round(day, 3), q))
        self.n_charges += 1
        if reorder:
            self._reorder(day, keys=list(bill))
        return max(ready_d * H, now_h)

    def stock_report(self, t_end_h):
        day = t_end_h / H
        left = 0.0
        for k in set(self.use_log) | set(self.prior_d):
            if k in supply.ITEMS:
                left += max(self.stores.on_hand(k, day), 0.0) * self.market.price(supply.ITEMS[k], day)
        bought = sum(o.cost for o in self.stores.orders if o.placed_day >= 0)
        waits = [w for _, _, w in self.stockouts]
        early = [w for d, _, w in self.stockouts if d < 90.0]
        late = [w for d, _, w in self.stockouts if d >= 90.0]
        episodes = sorted({(k, round(d + w, 1)) for d, ks, w in self.stockouts for k in ks})
        weeks = int(math.ceil(day / 7.0))
        use_w = {}
        for k, L in self.use_log.items():
            arr = [0.0] * weeks
            for d, q in L:
                arr[min(int(d // 7), weeks - 1)] += q
            use_w[k] = [round(x, 5) for x in arr]
        return dict(mode=self.stock_mode, n_charges=self.n_charges, n_stockouts=len(self.stockouts),
                    n_capped=getattr(self, "stock_capped", 0),
                    n_stockouts_wait_gt1d=sum(1 for w in waits if w > 1.0), days_waited=round(sum(waits), 2),
                    wait_mean_d=round(float(np.mean(waits)), 2) if waits else 0.0,
                    wait_p90_d=round(float(np.percentile(waits, 90)), 2) if waits else 0.0,
                    n_stockouts_first90=len(early), n_stockouts_after90=len(late),
                    days_waited_after90=round(sum(late), 2), n_episodes=len(episodes),
                    charges_short_frac=round(len(waits) / max(self.n_charges, 1), 4),
                    items_short=sorted({k for _, ks, _ in self.stockouts for k in ks}),
                    stock_usd=round(self.stock_usd, 2), bought_usd=round(bought, 2), left_usd=round(left, 2),
                    n_orders=sum(1 for o in self.stores.orders if o.placed_day >= 0),
                    stock_orders=self.stock_orders[:400], stockouts=self.stockouts[:400], use_weekly=use_w,
                    prior_d={k: round(v, 5) for k, v in self.prior_d.items()})

    # ---------------------------------------------------------------------------------------- money for the WIP
    WIP_WINDOW_D = 60.0

    def wip_reserve(self, now_h) -> float:
        """Round 5's engine rule for every policy in both labs: a new composition starts only if the money left after
        it still pays for the next steps of the lots already made (or in the making) in the last 60 days whose alloy
        has no tested result yet: aluminium a build and a test each; copper a small deposit each and, for half of
        them, a large deposit, its tensile, screen and immersion. Without it, the first runs (no spending plan, a
        24/7 atomizer) spent copper's two-year money on powders by day 330, 56 of 72 charges waiting months for
        plates and nozzles, and could not pay to test them."""
        t0 = now_h - self.WIP_WINDOW_D * H
        scored = {d["design"] for d in self.demonstrated}
        n = sum(1 for L in self.lots.values() if L.get("t", 0.0) >= t0 and L["design"] not in scored and
                L["remaining_g"] >= 30.0)
        n += sum(1 for p in self.pending.values() if p["kind"] in ("powder", "blend_ded"))
        if n == 0:
            return 0.0
        est = lambda k: self.estimate(dict(kind=k))
        if self.key == "flaime_al":
            per = est("print") + est("test")
        else:
            per = est("small_ded") + 0.5 * (est("large_ded") + est("tensile") + est("screen") + est("immersion"))
        return n * per

    # ---------------------------------------------------------------------------------------- sign-off
    def _so_key(self, a):
        k = a.get("kind")
        for f in ("into", "lot", "build", "deposit"):
            if a.get(f) is not None:
                return (k, f, a[f])
        d = a.get("design")
        if isinstance(d, dict):
            return (k, tuple(sorted((e, round(float(d.get(e, 0.0)), 3)) for e in self.space.elements)))
        return (k, None)

    def submit3(self, a: dict, now_h: float) -> str:
        k = a.get("kind")
        if (k == "powder" and not a.get("into")) or k == "blend_ded":
            self.now_h = now_h
            if self.budget_left - self.estimate(a) < self.wip_reserve(now_h):
                self.status_log["money_wip"] = self.status_log.get("money_wip", 0) + 1
                return "money"
        if self.dec is not None and a.get("kind") != "stop":
            lim = self.dec.signoff_usd(self.key)
            if lim is not None:
                self.now_h = now_h
                if self.estimate(a) >= lim:
                    t0 = self._so_first.setdefault(self._so_key(a), now_h)
                    if now_h + 1e-9 < self.dec.signoff_time(t0):
                        self.status_log["signoff"] = self.status_log.get("signoff", 0) + 1
                        return "capacity"
        return super().submit3(a, now_h)

    # ---------------------------------------------------------------------------------------- slot admission
    def gate_ok(self, a, now_h) -> bool:
        """Round 4's admission rule, with one change for an action that has steps before a standing slot (copper's
        blend screens: the doser, then Utah's MX-Lab). Round 4 admitted a slot action only once the slot started within
        its shipping time plus a day of *now*. With a doser on day shifts and the MX-Lab's slot on Tuesday at 08:00,
        no moment satisfies that: dosed on Monday the material leaves too late, dosed on Friday the slot is more than
        two days off. So copper's BOFN and pKGFN could never start a blend screen (their only way to try a new design),
        and in the first runs made three lots in two years. Round 5 counts the window in working hours from the end of
        the steps before the slot to the material's departure, so a weekend doesn't shut it out. Actions with no steps
        before the slot (every slot action of the heuristic and the funnel) keep round 4's rule exactly."""
        self.now_h = now_h
        g = self.gate(a)
        if g is None:
            return True
        pre, role, h = g
        F = self.fac
        t = now_h
        for s_, hh in pre:
            k = F.pick(s_, t, hh, self.key, a.get("kind", ""))
            R = F.res[k]
            cal = R.st
            chunk = 8.0 if (cal.hours != "24/7" and cal.attended_h is None) else max(hh, 0.01)
            left = max(hh * R.factor(), 0.01)
            while left > 1e-9:
                s0, d0, _ = R.find(t, min(left, chunk), self.key)
                t, left = s0 + d0, left - min(left, chunk)
        for k in F.cands(role, now_h, self.GATE_W):
            R = F.res[k]
            hh = h * R.factor()
            if F.queue_wait(k, t, hh, self.key) > self.GATE_W:
                continue
            if k in F.ship:
                s, _, _ = R.find(t + F.ship[k][0], hh, self.key)
                if not pre:
                    if s - now_h > F.ship[k][1] + self.GATE_W:
                        continue
                else:
                    dep = s - F.ship[k][0]
                    gap = R4._cal_hours("day", t, dep) if dep > t else 0.0
                    if gap > (F.ship[k][1] - F.ship[k][0]) + self.GATE_W:
                        continue
            return True
        return False

    # ---------------------------------------------------------------------------------------- estimates
    def estimate(self, action) -> float:
        k = action.get("kind")
        if k == "sim_open":
            return 0.0
        base = super().estimate(action)
        t = getattr(self, "now_h", 0.0)
        F = self.fac

        def fee(role):
            try:
                return F.res[F.primary(role, t)].st.fee_usd
            except Exception:
                return 0.0
        if self.key == "flaime_al" and k == "print":
            return base + fee("prep")
        if self.key == "onr_cu":
            if k in ("small_ded", "preplaced"):
                return base + fee("prep")
            if k == "blend_ded":
                return base + fee("prep")
            if k == "large_ded":
                return base + fee("edm") + fee("prep") + fee("pip") + 15.0
            if k == "screen":
                return base + fee("prep")
            if k == "immersion":
                return base + 2 * fee("prep")
        return base

    # ---------------------------------------------------------------------------------------- shared steps
    def _side(self, steps, t, what, tag):
        if steps:
            _, usd = self._route(steps, t, what + " (side)", tag=dict(tag, side=True))
            self.charge(t, usd, what + " (side steps)")

    def _do_print(self, a, now_h):
        L = self._lot(a["lot"])
        need = self.PRINT_FILL_G
        if L["remaining_g"] < need:
            return False
        L["remaining_g"] -= need
        params = a["params"][:9]
        st0 = self.fac.pick("utah_midi", now_h, 5.0, self.key, "print")
        ready = self._materials({"build_plate": 1.0, "argon": 1.0 if st0.endswith("@vcl") else 0.0}, now_h)
        bid = next(self.ids)
        tag = dict(design=L["design"], node="print", lot=a["lot"], sample=f"B{bid}")
        t_r, usd = self._route(AL_STEPS["print"][0], ready, "print", tag=tag)
        self.charge(now_h, usd, "print")
        st = self._route_of("utah_midi")
        eff, rec = self._proc_offset(st, params, now_h)
        lt = self._lot_truth[a["lot"]]
        lot = dict(lt, composition=lt["composition"])
        parts, meas = [], []
        for p, pr in zip(eff, rec):
            part = self.truth.build(lot, p, self.rng)
            part["reuse"] = lt.get("reuse", 0.0)
            parts.append(part)
            meas.append(dict(self._soundness(part, L["design"]), params=pr))
        back, stt = self._return_powder(a["lot"], need, self.PRINT_FUSED_G, eff[0])
        self._part_truth[bid] = dict(parts=parts, lot=a["lot"], bars_at=int(a.get("bars_at", 0)), route=st)
        self._emit(t_r, dict(type="build", id=bid, lot=a["lot"], design=L["design"], measured=meas,
                             bars_at=int(a.get("bars_at", 0)), returned_g=back, returned_state=stt))
        return True

    def _ded(self, a, now_h, mode, grams, steps, substrates, side=()):
        L = self._lot(a["lot"])
        if L["remaining_g"] < grams:
            return False
        L["remaining_g"] -= grams
        ready = self._materials({"ded_substrate": substrates} if substrates else {}, now_h)
        node = {"preplaced": "ded_small", "blown_small": "ded_small", "blown_large": "ded_large"}[mode]
        dep = next(self.ids)
        tag = dict(design=L["design"], node=node, lot=a["lot"], sample=f"D{dep}")
        t_r, usd = self._route(steps, ready, mode, tag=tag)
        self.charge(now_h, usd, mode)
        st = self._last_route[0][1] if self._last_route else steps[0][0]
        lot = self._lot_truth[a["lot"]]
        params = a["params"] if isinstance(a["params"], list) else [a["params"]]
        params = params[:(4 if mode != "blown_large" else 1)]
        eff, rec = self._proc_offset(st.split("@")[0] if not st.endswith("@vcl") else st, params, now_h)
        did = L["design"]
        nab = {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}
        parts, meas = [], []
        for p, pr in zip(eff, rec):
            part = self.truth.deposit(lot, p, mode, self.rng, substrate=nab if mode != "blown_small" else None)
            part["reuse"] = lot.get("reuse", 0.0)
            parts.append(part)
            m = dict(self._soundness(part, did), dilution=part["dilution"] * math.exp(self.rng.normal(0, 0.1)),
                     params=pr)
            if mode != "preplaced":
                m.update(beta_prime=float(np.clip(part["beta_prime"] + self.rng.normal(0, 0.03), 0, 1)),
                         catchment=part["catchment"] * math.exp(self.rng.normal(0, 0.05)),
                         grain_um=part["grain_um"] * math.exp(self.rng.normal(0, 0.1)))
            if part["fusion_ok"] is not None:
                m["fusion_ok"] = part["fusion_ok"] if self.rng.random() > 0.05 else (not part["fusion_ok"])
            meas.append(m)
        catch = float(np.mean([pp["catchment"] for pp in parts])) if parts else 0.6
        back, stt = self._return_powder(a["lot"], grams, None, eff[0], mode="ded", catchment=catch) \
            if mode != "preplaced" else (0.0, None)
        self._part_truth[dep] = dict(parts=parts, lot=a["lot"], mode=mode, route=st)
        self._emit(t_r, dict(type="deposit", id=dep, lot=a["lot"], design=did, mode=mode, measured=meas,
                             returned_g=back, returned_state=stt))
        self._side(list(side), t_r, mode, tag)
        return True

    def _do_preplaced(self, a, now_h):
        m, s = CU_STEPS["preplaced"]
        return self._ded(a, now_h, "preplaced", 20.0, m, 0.25, s)

    def _do_small_ded(self, a, now_h):
        m, s = CU_STEPS["small_ded"]
        return self._ded(a, now_h, "blown_small", 450.0, m, 0.0, s)

    def _do_large_ded(self, a, now_h):
        L = self._lot(a["lot"])
        F = self.fac
        if F.online("utah_mxlab@vcl", now_h) and L["remaining_g"] >= 1000.0:
            m, s = CU_STEPS["large_vcl"]
            return self._ded(a, now_h, "blown_large", 1000.0, m, 1.0, s)
        if "mines_x2" in F.cands("mines_x2") and L.get("nsl") and L["remaining_g"] >= 2000.0:
            m, s = CU_STEPS["large_mines"]
            return self._ded(a, now_h, "blown_large", 2000.0, m, 1.0, s)
        return False

    def _do_blend_ded(self, a, now_h):
        if self.key != "onr_cu":
            return False
        did = self.design_id(a["design"])
        comp = self.designs[did]["composition"]
        kg = 0.3
        bill = {}
        for el, w in comp.items():
            it = self.BLEND_ITEMS.get(el)
            if it and w > 0:
                bill[it] = bill.get(it, 0.0) + kg * w / 100.0
        bill["ded_substrate"] = 0.25
        ready = self._materials(bill, now_h)
        dep = next(self.ids)
        tag = dict(design=did, node="ded_small", blend=True, sample=f"D{dep}")
        m_, s_ = CU_STEPS["blend_ded"]
        t_r, usd = self._route(m_, ready, "blend_ded", tag=tag)
        self.charge(now_h, usd + 25.0, "blend_ded")
        params = a["params"] if isinstance(a["params"], list) else [a["params"]]
        parts, meas = [], []
        for p in params[:4]:
            part = self.truth.blend_deposit(comp, p, self.rng)
            part["reuse"] = 0.0
            parts.append(part)
            meas.append(dict(self._soundness(part, did), dilution=part["dilution"] * math.exp(self.rng.normal(0, 0.1)),
                             params=p,
                             beta_prime=float(np.clip(part["beta_prime"] + self.rng.normal(0, 0.03), 0, 1)),
                             catchment=part["catchment"] * math.exp(self.rng.normal(0, 0.05)),
                             grain_um=part["grain_um"] * math.exp(self.rng.normal(0, 0.1))))
        self._part_truth[dep] = dict(parts=parts, lot=None, mode="blend")
        self._emit(t_r, dict(type="deposit", id=dep, lot=None, design=did, mode="blend", measured=meas))
        self._side(s_, t_r, "blend_ded", tag)
        return True

    def _do_screen(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if a.get("block") is not None:
            ps = self._part_truth[a["deposit"]]["parts"]
            part = ps[min(int(a["block"]), len(ps) - 1)]
        if D["mode"] == "preplaced" or D.get("_screened"):
            return False
        D["_screened"] = True
        t_r, usd = self._route(CU_STEPS["screen"][0], now_h, "screen",
                               tag=dict(design=D["design"], node="screen", sample=f"D{a['deposit']}"))
        self.charge(now_h, usd, "corrosion screen")
        meas = self._m("corrosion_screen", self._psample(part, D["design"]))
        self._emit(t_r, dict(type="cu_test", what="screen", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _do_immersion3(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if D["mode"] != "blown_large" or "immersion" in D:
            return False
        D["immersion"] = "pending"
        hd = []
        tag = dict(design=D["design"], node="immersion", sample=f"D{a['deposit']}")
        t_r, usd = self._route(CU_STEPS["immersion_in"][0], now_h, "immersion", tag=tag, handles=hd)
        t_in = t_r - 720.0
        self.charge(now_h, usd + 30.0, "immersion (coupon cut, polished and in)")
        smp = self._psample(part, D["design"])
        meas = self._m("immersion", smp)
        handle = [h for st, h in hd if st == "immersion"][-1]
        self._imm[a["deposit"]] = dict(handle=handle, t_in=t_in, meas=meas, design=D["design"], stopped=None)
        op = self.fac.res.get("operator")
        for d, m in self._interim(smp, meas).items():
            tr = t_in + d * H
            if not self.vertical and op is not None:
                tr = fac.next_open(op.st.hours, tr)
            self._emit(tr + 0.25, dict(type="imm_interim", deposit=a["deposit"], design=D["design"], day=d,
                                       measured=m))
        self._emit(t_in + 720.0, dict(type="imm_final_book", deposit=a["deposit"], design=D["design"]))
        return True

    def release3(self, t_h, p) -> bool:
        if p.get("type") == "imm_final_book" and p.get("aid") not in self.cancelled:
            st = self._imm[p["deposit"]]
            st["final"] = True
            t_r, usd = self._route(CU_STEPS["immersion_out"][0], t_h, "immersion",
                                   tag=dict(design=p["design"], node="immersion", sample=f"D{p['deposit']}"))
            self.charge(t_h, usd + 105.0, "immersion (section and 4 ICP-MS draws)")
            self._emit(t_r, dict(type="cu_test", what="immersion", deposit=p["deposit"], design=p["design"],
                                 measured=st["meas"], aid=p.get("aid")))
            return False
        return super().release3(t_h, p)


# ------------------------------------------------------------------------------------------------- the twin
class Twin5(R4.Twin4):
    """Both campaigns on round 5's facility, from the day the money arrives."""

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
        self.fac4 = Facility5(plan, seed, self.h + 2000 * H, opts)
        self.campaigns = {}
        for k, sp in specs.items():
            c = Campaign5(sp, policies[k], self.market, self.fac4, self.h, lab=self.lab)
            c.async_ = True
            c.start_h = self.fac4.start_h
            self.campaigns[k] = c
        self.facilities = {k: c.fac for k, c in self.campaigns.items()}
        self.seq = itertools.count()
        self.trace = None
        self._iters = {k: 0 for k in self.campaigns}
        self.stages = bool(opts.get("stages", True))
        names = pol_names or {k: getattr(policies[k], "name", "") for k in specs}
        modes = {k: ("human" if (self.lab == "conventional" or names.get(k) in HUMAN_POLICIES) else "auto")
                 for k in specs}
        self.dec = Decide(opts.get("decisions", "nominal"), self.lab, modes)
        for c in self.campaigns.values():
            c.dec = self.dec
        self.held_log = {k: [] for k in specs}       # (class, t_result, t_seen)
        self.daily = {k: {} for k in specs}
        self.hpc = dict(HPC, **(opts.get("hpc") or {}))
        self.stream = {k: dict(rng=np.random.default_rng(70_000 + 97 * seed + i), acc=0.0, pool=[], evaluated=0.0,
                               materialized=0, evicted=0, pool_sizes=[])
                       for i, k in enumerate(specs)}

    def _day(self, k, g):
        d = int(g // H)
        D = self.daily[k].get(d)
        if D is None:
            c = self.campaigns[k]
            D = self.daily[k][d] = dict(budget_left=round(c.budget_left, 2), asked=0, proposed=0, held=0,
                                        pending=len(c.pending), st={})
        return D

    def run_async(self, verbose=False):
        q, ends = [], []
        F = self.fac4
        for r in F.res.values():
            r.on_commit = lambda e, _ends=ends: heapq.heappush(_ends, e)
        dirty = {k: True for k in self.campaigns}
        last = {k: -1e9 for k in self.campaigns}
        tot_b = sum(c.spec.budget_usd for c in self.campaigns.values())
        self._money_share = {k: c.spec.budget_usd / tot_b for k, c in self.campaigns.items()}
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
                if not (dirty[k] or freed or g - last[k] >= 24.0) or c.budget_left <= 0:
                    continue
                dirty[k], last[k] = False, g
                v = c.view(g)
                acts = c.policy.propose(v, self.N_ASK) or []
                D["asked"] += 1
                D["proposed"] += len(acts)
                blocked = False
                for a in acts:
                    if blocked and a.get("kind") != "stop" and c.estimate(a) > 50.0:
                        st = "plan"
                        c.status_log["plan_wait"] = c.status_log.get("plan_wait", 0) + 1
                    else:
                        before = dict(c.status_log)
                        st = c.submit3(a, g)
                        if st == "capacity":
                            if c.status_log.get("signoff", 0) > before.get("signoff", 0):
                                st = "signoff"
                            elif c.status_log.get("kanban", 0) > before.get("kanban", 0):
                                st = "kanban"
                        blocked = blocked or st == "plan"
                    D["st"][st] = D["st"].get(st, 0) + 1
                    ok = st == "ok"
                    cb = getattr(c.policy, "admitted" if ok else "rejected", None)
                    if cb is not None:
                        cb(a) if ok else cb(a, "capacity" if st in ("signoff", "kanban") else st)
                flush(k, c)
            g += self.DT_H
            step += 1
        self._held_end = {k: {cls: len(v) for cls, v in held[k].items()} for k in keys}
        return self.summary()

    def _stream_tick(self, g):
        """Note 4: the HPC allocation simulates candidates continuously; the newest unexplored ones are visible to
        the policies as simulation results (open CALPHAD), at no cost to the campaign."""
        hp = self.hpc
        per_h = hp["cores"] / hp["core_h"]
        for k, c in self.campaigns.items():
            S = self.stream[k]
            S["evaluated"] += per_h * self.DT_H
            S["acc"] += hp["add_per_day"] / 24.0 * self.DT_H
            n = int(S["acc"])
            if n <= 0:
                continue
            S["acc"] -= n
            for d in c.space.sample(n, seed=int(S["rng"].integers(1 << 30))):
                did = c.design_id(d)
                if did in S.setdefault("seen", set()):
                    continue
                S["seen"].add(did)
                comp = c.designs[did]["composition"]
                proc = {v.name: d[v.name] for v in c.space.process if v.name in d}
                c.sims.append(dict(kind=hp["node"], design=did, proc=proc, out=c.truth.sim_open(comp), t=g,
                                   stream=True))
                S["pool"].append(did)
                S["materialized"] += 1
            if len(S["pool"]) > hp["keep"]:
                used = {L["design"] for L in c.lots.values()} | {D["design"] for D in c.deposits.values()}
                used |= {tuple(p["key"])[1] for p in c.pending.values()
                         if p.get("key") and tuple(p["key"])[0] == "design"}
                drop = set()
                while len(S["pool"]) > hp["keep"]:
                    did = S["pool"].pop(0)
                    if did not in used:
                        drop.add(did)
                if drop:
                    c.sims = [x for x in c.sims if not (x.get("stream") and x["design"] in drop)]
                    S["evicted"] += len(drop)
            if int(g) % (24 * 7) == 0:
                S["pool_sizes"].append(sum(1 for x in c.sims if x.get("stream")))

    def event_log(self, meta=None) -> dict:
        """Round 3's event log, with only the designs something was done with (the HPC stream's other candidates
        are counted in ``report5``)."""
        log = super().event_log(meta)
        keep = {}
        for k, c in self.campaigns.items():
            ids = {str(e["design"]) for e in log["events"] if e.get("campaign") == k and e.get("design") is not None}
            ids |= {str(r["design"]) for r in log["results"] if r.get("campaign") == k and r.get("design") is not None}
            keep[k] = {i: d for i, d in log["designs"][k].items() if i in ids}
        log["designs"] = keep
        log["designs_note"] = "designs with a booking or a result; the HPC stream's other candidates are counted"
        return log

    def _stage_tick(self, g):
        allowed = {k: c for k, c in self.campaigns.items() if self.dec.stage_ok(k, g)}
        if not allowed:
            return
        keep = self.campaigns
        try:
            self.campaigns = allowed
            super()._stage_tick(g)
        finally:
            self.campaigns = keep

    def report5(self) -> dict:
        """What round 5 adds to a run's record."""
        F = self.fac4
        sch = F.sched
        R = F.res["atomizer"]
        out = dict(lab=self.lab, plan=self.plan, notes=list(NOTES_APPLIED), room_h=sch.get("room_h"),
                   used=sch.get("used", {}), atom=dict(switch_h=F.atom_switch_h, cycle=F.atom_cycle,
                                                       runs=sum(1 for j in R.jobs if j[3] == "atomize" and
                                                                j[0] < self.h),
                                                       runs_by=_count_by([j for j in R.jobs if j[0] < self.h],
                                                                         "atomize")),
                   decisions=dict(level=self.dec.level, modes=self.dec.modes,
                                  held={k: _held_stats(v) for k, v in self.held_log.items()},
                                  held_end=getattr(self, "_held_end", None)),
                   stock={k: c.stock_report(self.h) for k, c in self.campaigns.items()},
                   counters={k: counters(c) for k, c in self.campaigns.items()},
                   shared=shared_use(self), idle=idle_report(self),
                   hpc=dict(cores=self.hpc["cores"], core_h=self.hpc["core_h"], keep=self.hpc["keep"],
                            add_per_day=self.hpc["add_per_day"], utilization=1.0,
                            per_day=self.hpc["cores"] * 24.0 / self.hpc["core_h"],
                            campaigns={k: dict(evaluated=round(S["evaluated"]), materialized=S["materialized"],
                                               evicted=S["evicted"], pool_weekly=S["pool_sizes"][:120],
                                               own_sims=sum(1 for x in c.sims if not x.get("stream")),
                                               hpc_station_h=round(sum(j[1] - j[0] for j in
                                                                       self.fac4.res["hpc"].jobs if j[2] == k), 1))
                                       for (k, S), c in zip(self.stream.items(), self.campaigns.values())}))
        return out


def _count_by(jobs, what):
    out = {}
    for j in jobs:
        if j[3] == what:
            out[j[2]] = out.get(j[2], 0) + 1
    return out


def _held_stats(L):
    out = {}
    for cls in ("review", "meeting"):
        w = [(b - a) / H for c_, a, b in L if c_ == cls]
        if w:
            out[cls] = dict(n=len(w), mean_days=round(float(np.mean(w)), 2), median_days=round(float(np.median(w)), 2),
                            max_days=round(float(np.max(w)), 2))
    return out


def counters(c) -> dict:
    """Sterling's note 3: designed (computed candidates), lots made, alloys made, alloys printed or deposited,
    alloys tested through the full chain."""
    printed = {B["design"] for B in c.builds.values()} | {D["design"] for D in c.deposits.values()}
    tested = {d["design"] for d in c.demonstrated}
    return dict(designed=len(c.designs), lots_made=len(c.lots),
                alloys_made=len({L["design"] for L in c.lots.values()} |
                                {D["design"] for D in c.deposits.values() if D.get("lot") is None}),
                alloys_printed=len(printed), builds_or_deposits=len(c.builds) + len(c.deposits),
                alloys_tested=len(tested), tests=len(c.demonstrated))


# ------------------------------------------------------------------------------------------------- reports
ROLE_GROUPS = ("atomizer", "utah_midi", "lpbf_3dpt", "utah_mxlab", "mines_x2", "edm", "furnace", "prep", "hardness",
               "pip", "byu_sem", "byu_icpms", "tensile", "tensile_hot", "shop", "doser", "sieve", "psd", "density",
               "cubxl", "immersion", "xrd", "valimet", "ames", "nsl", "robot", "operator")


def _role(k):
    return k.split("@")[0]


def shared_use(tw) -> dict:
    """Busy unit-hours of each station kind (in house and outside routes together, and each route) by campaign and
    quarter, with the hours each offered while online: which shared stations bind."""
    F = tw.fac4
    qh = 91.25 * H
    nq = int(math.ceil(tw.h / qh))
    out = {}
    for k, r in F.res.items():
        role = _role(k)
        if role not in ROLE_GROUPS:
            continue
        busy = {}
        for j in r.jobs:
            a, b, camp = j[0], min(j[1], tw.h), j[2]
            if a >= tw.h or b <= a:
                continue
            arr = busy.setdefault(camp, [0.0] * nq)
            t = a
            while t < b - 1e-9:
                qi = min(int(t // qh), nq - 1)
                e = min(b, (qi + 1) * qh)
                arr[qi] += e - t
                t = e
        avail = []
        for qi in range(nq):
            a, b = max(qi * qh, r.online_h), min((qi + 1) * qh, tw.h)
            if b <= a:
                avail.append(0.0)
                continue
            if k == "atomizer" and isinstance(r, ResourceAtom):
                sw = r.switch_h if r.switch_h is not None else 1e18
                man = max(0.0, min(b, sw) - a) / WEEK * 8 * 2.5
                aut = max(0.0, b - max(a, sw))
                avail.append(round(man + aut, 1))
            else:
                avail.append(round(R4._cal_hours(r.st.hours, a, b) * r.st.units, 1))
        if not busy and r.online_h >= tw.h:
            continue
        out[k] = dict(role=role, busy={c: [round(x, 1) for x in v] for c, v in busy.items()}, avail=avail,
                      external=bool(r.st.external), units=r.st.units, online_h=round(r.online_h, 1))
    return out


IDLE_MIN_D = 7


def idle_report(tw) -> dict:
    """Note 3: for each campaign, stretches of at least a week with no start at its pacing stations (the atomizer,
    and its first fabrication step: LPBF for aluminium, small DED for copper), each with a cause read off the daily
    log: money, capacity (turned away: busy station or the WIP limit), sign-off, decision time (results waiting on
    a person), the spending plan, or the policy waiting (asked, proposed nothing it could start, nothing turned away;
    'in flight' when it had results coming). A stretch is flagged when the campaign had money and the station had
    free capacity and nothing started."""
    F = tw.fac4
    nd = int(tw.h // H) + 1
    out = {}
    for k, c in tw.campaigns.items():
        fab = ("utah_midi", "lpbf_3dpt") if k == "flaime_al" else ("utah_mxlab", "mines_x2")
        starts = {"atomizer": np.zeros(nd), "fab": np.zeros(nd)}
        free = {"atomizer": np.zeros(nd), "fab": np.zeros(nd)}
        for key, r in F.res.items():
            role = _role(key)
            grp = "atomizer" if role == "atomizer" else ("fab" if role in fab else None)
            if grp is None:
                continue
            for j in r.jobs:
                if j[2] == k and j[0] < tw.h and not (isinstance(j[4], dict) and j[4].get("helper_for")):
                    starts[grp][int(j[0] // H)] += 1
            for j in r.jobs:
                a, b = j[0], min(j[1], tw.h)
                t = a
                while t < b - 1e-9:
                    d = int(t // H)
                    e = min(b, (d + 1) * H)
                    free[grp][d] += (e - t) / max(r.st.units, 1)
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
                    if d - run0 >= IDLE_MIN_D:
                        stretches.append((run0, d))
                    run0 = None
            items = []
            for a, b in stretches:
                cnt = {}
                money_days = 0
                for d in range(a, b):
                    x = D.get(d)
                    if x is None:
                        cnt["not asked (before start)"] = cnt.get("not asked (before start)", 0) + 1
                        continue
                    stt = x["st"]
                    if x["budget_left"] < 500.0:
                        cause = "money"
                    elif stt.get("signoff"):
                        cause = "sign-off"
                    elif stt.get("capacity") or stt.get("kanban"):
                        cause = "capacity" if stt.get("capacity", 0) >= stt.get("kanban", 0) else "WIP limit"
                    elif stt.get("plan") or stt.get("plan_wait"):
                        cause = "spending plan"          # round 5: round 4's reserve for the standing slots
                    elif stt.get("money"):
                        cause = "money"
                    elif x["held"] > 0:
                        cause = "decision time"
                    elif x["pending"] > 0:
                        cause = "policy waiting (results in flight)"
                    else:
                        cause = "policy waiting"
                    cnt[cause] = cnt.get(cause, 0) + 1
                    if x["budget_left"] >= 5000.0:
                        money_days += 1
                busy_frac = float(np.mean(free[grp][a:b])) / 24.0 if b > a else 0.0
                main = max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else "?"
                flag = money_days >= 0.8 * (b - a) and busy_frac < 0.5 and \
                    main.startswith("policy waiting") and (b - a) >= 14
                items.append(dict(start_d=a, end_d=b, days=b - a, cause=main, causes=cnt,
                                  station_busy_frac=round(busy_frac, 3), flag=bool(flag)))
            res[grp] = items
        out[k] = res
    # the daily log in weeks, compact: budget left, asks, outcomes, results waiting on a person, actions in flight
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
            rows.append(dict(budget_left=ds[-1]["budget_left"], asked=sum(x["asked"] for x in ds),
                             held=max(x["held"] for x in ds), pending=max(x["pending"] for x in ds), st=st))
        wk[k] = rows
    return dict(stretches=out, weekly=wk, min_days=IDLE_MIN_D)
