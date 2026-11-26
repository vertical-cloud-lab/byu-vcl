"""Two campaigns at once, kept apart, on one lab and one market.

Each campaign has its own search space (twin/spaces.py), function network (the actions below), ground truth
(twin/truth_al.py or twin/truth_cu.py, with its own seed), objectives, budget, stores of feedstock, observation log
and policy. Nothing of one campaign's is visible to the other's policy. They meet in three places only, as they would
in the lab:

* **the shared stations**: one atomizer, the same SEM, the same Utah facility; a booking by one delays the other, and
  switching the atomizer between an aluminium and a copper melt costs a changeover (AMAZEMET: "2-4 hours for full
  material change, including purging and cleaning", bottleneck.py);
* **the market**: both buy on the same price and lead-time paths (twin/supply.py);
* **the calendar**: one clock.

``Twin(...).run()`` returns both campaigns' ledgers. ``isolated=True`` gives each campaign a facility of its own, so
the cost of sharing can be measured.

**The networks, as actions a policy can buy** (partial evaluation: any action can be bought on its own, as long as
its inputs exist):

FLAIME (Al, LPBF), after DAL's FLAIME DAG (figures/flaime_pipeline_dag.py on consolidation-2):
``sim_open`` (pycalphad, open databases), ``sim_tc`` (TC-Python TCAL Scheil), ``sim_am`` (Thermo-Calc AM Module) ->
``powder`` (cups machined, doser, atomizer, sieve, PSD, SEM/EDS, ICP-MS optional) -> ``print`` (a 55 mm-kit build: up
to 9 density cubes at different settings and miniature tensile blanks at one of them; density and crack checks) ->
``test`` (EDM, heat treatment, miniature tensile, optionally at 250 degC) -> ``promote`` (a full plate of ASTM E8
sub-size bars, 440 g of powder: FLAIME's gate G3 needs >= 3 E8 replicates).

ONR (Cu, blown-powder DED), after the proposal's Fig. 1 (DAL PR 117): ``sim_open`` (pycalphad mc_ni), ``sim_tc``
(TCCU), ``sim_heat`` (heat flow + CALPHAD along the thermal history) -> ``powder`` -> ``nsl`` (certified O, C and
composition, needed before Mines) -> ``preplaced`` (pre-placed tracks at Utah) -> ``small_ded`` (blown-powder tracks
and blocks from a 0.5 kg lot at Utah) -> ``large_ded`` (2 kg at Mines: blocks for bars and coupons, and a repair
coupon) -> ``tensile`` / ``screen`` (one-hour CubXL corrosion screen) / ``immersion`` (30 days).

**Scoring** (what the benchmark reports; the policies never see it): the true utility of every alloy the campaign
has *demonstrated*, i.e. tensile-tested (FLAIME) or tensile- and immersion-tested on a Mines deposit (ONR), as a
geometric mean of desirabilities (Derringer & Suich 1980) times feasibility:

* FLAIME: yield strength 150 -> 400 MPa, elongation 2 -> 15 %, mineral burden CMDRI_log 1.5x AlSi10Mg's -> 0;
  feasible if >= 99.5 % dense and crack-free (gate G2) and MBS_lin <= 10 % of Scalmalloy's (gate G3a).
  Discovery: YS >= 250 and EL >= 5, or YS >= 200 and EL >= 8 (FLAIME's family thresholds, gate G3).
* ONR: yield 100 -> 400 MPa, elongation 5 -> 35 %, long-term corrosion rate 3x 70-30 Cu-Ni's -> 0.5x, nickel
  30 -> 0 wt%; feasible if >= 99 % dense and crack-free. Pass (H5): rate <= 70-30's and selective attack <= 3 um.
"""
from __future__ import annotations

import heapq
import itertools
import math
from dataclasses import dataclass, field

import numpy as np

from twin import facility as fac
from twin import instruments as INS
from twin import spaces, supply, truth_al, truth_cu, usgs

H = 24.0


def _desir(x, lo, hi):
    return float(np.clip((x - lo) / (hi - lo), 0.0, 1.0))


# --------------------------------------------------------------------------------------------- action catalogue
# (steps as (station, hours per unit), unit 'job' or 'run'), money besides station fees, what it consumes
ACTIONS = {
    "flaime_al": {
        "sim_open": dict(steps=[("hpc", 0.05)], usd=1.0, note="pycalphad, open databases (fast dilute model)"),
        "sim_tc": dict(steps=[("hpc", 0.5)], usd=10.0, note="TC-Python + TCAL Scheil (DAL prelim: $10 a call)"),
        "sim_am": dict(steps=[("hpc", 2.0)], usd=25.0, note="Thermo-Calc AM Module, 0.5-2 CPU-h (FLAIME)"),
        "powder": dict(note="cups machined (about 40 min a cup, 4 a run: DAL #250), dosed and pressed, one run "
                            "of the atomizer each (2.5 h), sieved, sized, SEM/EDS; ICP-MS on request"),
        "print": dict(note="a 55 mm-kit build: up to 9 cubes plus miniature tensile blanks, ~30 g of powder"),
        "test": dict(note="EDM, heat treatment, 3 miniature bars; optionally 250 degC"),
        "promote": dict(note="a full 170 mm plate of ASTM E8 sub-size bars (440 g), EDM, heat treatment, 3 bars"),
        "gas_atomize": dict(note="Valimet gas atomization, >= 50 kg (FLAIME's scale-up; about $8k a run)"),
    },
    "onr_cu": {
        "sim_open": dict(steps=[("hpc", 0.05)], usd=1.0, note="pycalphad, MatCalc mc_ni (emulated)"),
        "sim_tc": dict(steps=[("hpc", 0.5)], usd=10.0, note="TC-Python + TCCU"),
        "sim_heat": dict(steps=[("hpc", 0.5)], usd=5.0, note="Rosenthal heat flow + CALPHAD on the thermal history"),
        "powder": dict(note="OFE cups, additions dosed, 0.8 kg a run (DAL #219), sieved to 45-150 um"),
        "nsl": dict(note="NSL Analytical: O, C and composition of a lot (required before Mines)"),
        "preplaced": dict(note="pre-placed tracks in grooves on NAB and Cu-Ni plates, Utah MX-Lab, half a day"),
        "small_ded": dict(note="blown-powder tracks, walls, small blocks at up to 4 settings, Utah, 0.5 kg"),
        "large_ded": dict(note="Mines FormAlloy X2: 2 kg, blocks for bars and coupons plus a repair coupon"),
        "tensile": dict(note="3 sub-size bars machined and pulled"),
        "screen": dict(note="CubXL: OCP, LPR, EIS, cyclic polarization, and ICP-MS of the electrolyte"),
        "immersion": dict(note="30 days in vials on the gantry deck, sectioned for selective attack"),
        "gas_atomize": dict(note="Ames National Laboratory gas atomization, one run a year (a purchased service)"),
    },
}
AL_CHARGE_KG, CU_CHARGE_KG = 0.30, 0.80
AL_RUN_CONSUMABLES = {"argon": 0.07, "cc_plate": 1 / 5, "graphite_crucible": 1 / 12, "bn_spray": 1 / 300}
CU_RUN_CONSUMABLES = {"argon": 0.16, "cc_plate": 1.0, "bn_nozzle": 1.0, "graphite_crucible": 1 / 6,
                      "bn_spray": 1 / 300}
CHANGEOVER_H = 3.0
# round 2: the standing inventory of a stocked lab (Spec.stock = 'stocked'), assumed: about a month's use at the
# vertical lab's pace of consumables and of every feedstock but Sc and Er (kg, or each)
STOCKED = {
    "flaime_al": {"al_bar_hp": 20.0, "si_lump": 1.0, "mg_turnings": 2.3, "cu_shot": 0.45, "zn_shot": 0.3,
                  "al_mn20": 0.3, "al_cr20": 0.2, "al_zr10": 0.2, "al_ti10": 0.1, "al_fe10": 0.25, "al_ni20": 0.1,
                  "al_ce20": 0.2, "sn_shot": 0.1, "li_metal": 1.0, "argon": 10.0, "cc_plate": 6.0,
                  "graphite_crucible": 3.0, "build_plate": 20.0, "bn_spray": 2.0},
    "onr_cu": {"cu_ofe_bar": 30.0, "ni_pellet": 3.0, "al_shot": 0.45, "fe_powder": 0.5, "mn_flake": 0.5,
               "cr_powder": 0.2, "si_lump_cu": 0.25, "nb_powder": 0.2, "ti_sponge": 0.1, "argon": 10.0,
               "cc_plate": 12.0, "bn_nozzle": 12.0, "graphite_crucible": 3.0, "bn_spray": 2.0, "ded_substrate": 5.0},
}
# on hand at day 0 (sunk, not charged): what DAL has bought by November 2026 (its procurement threads: McMaster 6063
# rod, the ESPI order of Mn, Cr, Zn, Sn, Mg pieces, Sc, Er and Ti, Si on hand, the 630 bronze rod, argon, plates);
# everything else is ordered when a charge first needs it
PRESTOCK = {
    "flaime_al": {"al_bar_hp": 10.0, "si_lump": 0.45, "al_mn20": 0.1, "al_cr20": 0.1, "zn_shot": 0.1, "sn_shot": 0.1,
                  "mg_turnings": 0.1, "al_sc2": 0.005, "al_er10": 0.025, "al_ti10": 0.2, "argon": 3.0,
                  "cc_plate": 4.0, "graphite_crucible": 2.0, "bn_spray": 1.0},
    "onr_cu": {"cu_ofe_bar": 2.0, "argon": 2.0, "cc_plate": 2.0, "graphite_crucible": 1.0, "bn_spray": 1.0,
               "bn_nozzle": 2.0},
}


@dataclass
class Spec:
    key: str                      # 'flaime_al' | 'onr_cu'
    budget_usd: float
    wip: int = 6
    seed: int = 0
    kappa: float = 1.0            # FLAIME: the nucleant effect the CALPHAD nodes miss; ONR: retained beta' scale
    prestock: bool = True         # base metal, argon and plates on hand at day 0 (bought before the campaign)
    crucible_cm3: int = 225       # round 2: the rePowder's standard crucible, or the 400 cm3 upgrade (DAL #219)
    reuse: bool = True            # round 2: unfused LPBF powder and DED overspray are sieved and put back in the lot
    fidelity: str = "fast"        # round 2: instrument simulators' fidelity (twin/instruments/__init__.py)
    cu_hidden: float = 0.0        # round 2: copper's gamma-2 effect the CALPHAD nodes miss (truth_cu.CuTruth.gamma2)
    stock: str = "lean"           # round 2: 'lean' (order each charge's metal when it is needed, as DAL does now) or
                                  # 'stocked' (a standing inventory bought at day 0 and charged, reordered 4x)


class Campaign:
    def __init__(self, spec: Spec, policy, market: supply.Market, facility: fac.Facility, horizon_h: float):
        self.spec, self.key, self.policy = spec, spec.key, policy
        self.space = spaces.SPACES[spec.key]
        self.truth = truth_al.AlTruth(spec.seed, spec.kappa) if spec.key == "flaime_al" else \
            truth_cu.CuTruth(spec.seed, spec.kappa, spec.cu_hidden)
        self.rng = np.random.default_rng(spec.seed * 1009 + (1 if spec.key == "flaime_al" else 2))
        self.market, self.fac, self.horizon_h = market, facility, horizon_h
        self.stores = supply.Stores(spec.key, market)
        self.spent = 0.0
        self.ledger = []                          # money: (t_h, usd, what)
        self.inflight = 0
        self.ids = itertools.count(1)
        # released (visible to the policy)
        self.designs, self.sims, self.lots, self.builds, self.tests = {}, [], {}, {}, []
        self.deposits, self.corr = {}, []
        # hidden truth per artifact
        self._lot_truth, self._part_truth = {}, {}
        self.demonstrated = []                    # scoring: (t_h, spent, utility, design id, details)
        self.events_out = []                      # (t_result, payload) produced by submit()
        self.refused = 0
        self.fidelity = spec.fidelity
        self.vertical = facility.kind == "vertical_lab"
        self.reuse_log = []                       # (t_h, lot, grams back)
        self.results_log = []                     # every result as it came back: (t_h, type, design, node)
        # round 3 (Twin(mode="async")): actions in flight by id, what each one targets, coupons in immersion, stops
        self.async_ = False
        self.pending = {}                         # action id -> dict(kind, key, t)
        self._aids = itertools.count(1)
        self.cancelled = set()                    # action ids whose remaining events are void (a stopped coupon)
        self._imm = {}                            # deposit id -> coupon in immersion (handle, t_in, measured, aid)
        self.stops = []                           # (t_h, deposit id, day)
        self.done = {}                            # completed evaluations by kind (round 3's fairness table)
        self.status_log = {}                      # submit3 outcomes: ok / capacity / plan / money / invalid
        if spec.prestock:
            for k, q in PRESTOCK[spec.key].items():
                self.stores.orders.append(supply.Order(k, q, 0.0, -1.0, -1.0, False, spec.key))
        self.spare = 1.5
        if spec.stock == "stocked":
            # a lab running round the clock keeps what it uses every week on the shelf (assumed quantities); bought
            # at day 0 at the day's prices and charged to the campaign; Sc and Er stay order-on-demand
            self.spare = 4.0
            for k, q in STOCKED[spec.key].items():
                price = market.price(supply.ITEMS[k], 0.0) * q
                self.stores.orders.append(supply.Order(k, q, price, 0.0, 0.0, False, spec.key))
                self.charge(0.0, price, f"order {k} {q:.3g} (standing stock)")

    # ---------------------------------------------------------------------------------------- money and design
    def charge(self, t, usd, what):
        self.spent += usd
        self.ledger.append((t, usd, what))

    @property
    def budget_left(self):
        return self.spec.budget_usd - self.spent

    def design_id(self, design: dict) -> int:
        comp = {e: round(design.get(e, 0.0), 3) for e in self.space.elements}
        key = tuple(sorted(comp.items()))
        for i, d in self.designs.items():
            if d["key"] == key:
                return i
        i = next(self.ids)
        c = self.space.composition(comp)
        self.designs[i] = dict(key=key, composition=c, design=dict(design))
        return i

    # ---------------------------------------------------------------------------------------- scheduling helpers
    def _route(self, steps, ready_h, what, changeover=False, tag=None, handles=None):
        """Book steps one after another; returns (end of last step's result, money for station fees). On a physical
        facility (round 3) each step is booked together with its robot or person (``Facility.run_step_joint``), and
        ``handles`` (a list) collects the station bookings' handles, so a passive step can be ended early."""
        t, usd = ready_h, 0.0
        tag = dict(tag or {}, what=what)
        res_t = t
        for st, hours in steps:
            hours = self.fac.adjust(st, hours, what, self.key)
            if hours <= 0 and st not in ("nsl",):
                continue
            cal = self.fac.res[st].st
            # attended work on a day calendar is split into days of at most 8 h
            chunk = 8.0 if (cal.hours != "24/7" and cal.attended_h is None) else max(hours, 0.01)
            left, first = max(hours, 0.01), True
            while left > 1e-9:
                h = min(left, chunk)
                if self.fac.physical:
                    s, e, r, c, hd = self.fac.run_step_joint(st, t, h, self.key, what,
                                                             CHANGEOVER_H if (changeover and st == "atomizer") else 0.0,
                                                             tag)
                    if handles is not None:
                        handles.append((st, hd))
                else:
                    s, e, r, c = self.fac.run_step(st, t, h, self.key, what,
                                                   CHANGEOVER_H if (changeover and st == "atomizer") else 0.0, tag)
                if first:
                    usd += self.market.service_price(c, s / H)
                else:
                    usd += self.market.service_price(c - cal.fee_usd, s / H)
                first = False
                left -= h
                t, res_t = e, r
        return max(res_t, t), usd

    def _m(self, name, sample, **kw):
        """One instrument's measurement of a sample (twin/instruments)."""
        return INS.measure(name, sample, self.key, self.rng, self.fidelity, **kw)

    def _psample(self, part, did, hot=False):
        """A part as the instruments see it: the truth's part plus what the campaign knows it is meant to be."""
        smp = dict(part, campaign=self.key, design=self.designs[did]["composition"])
        smp["strength"] = self.truth.strength(part)
        if self.key == "flaime_al":
            if hot:
                smp["strength_hot"] = self.truth.strength(part, 250.0)
        else:
            smp["corrosion"] = self.truth.corrosion(part)
        return smp

    def _soundness(self, part, did):
        """What the lab reports for a fresh part: Archimedes density, and the polished section imaged in the SEM
        (porosity and cracks by image analysis). Archimedes over-reads parts with surface-connected porosity, a
        single section can miss sparse pores, so the reported density is the lower of the two."""
        smp = self._psample(part, did)
        arch = float(self._m("density", smp)["rel_density"])
        sem = self._m("sem_section", smp)
        img = 1.0 - float(sem.get("porosity", 1.0 - arch))
        cd = sem.get("crack_density")
        if cd is None:
            cd = part["crack_density"] * math.exp(self.rng.normal(0, 0.2))
        return dict(rel_density=min(arch, img), rel_density_archimedes=arch, rel_density_sem=img,
                    crack_density=float(cd) if cd > 0.02 else 0.0, pore_dmax_um=sem.get("pore_dmax_um"))

    def _lsample(self, lot_id, did):
        lt = self._lot_truth[lot_id]
        good = [r for r in lt.get("runs", []) if not r.get("failed")]
        smp = dict(lt, campaign=self.key, design=self.designs[did]["composition"])
        if good:
            w = np.array([max(r["usable_frac"] * r["cut_frac"], 1e-9) for r in good])
            w = w / w.sum()
            for k in ("d50_um", "cut_frac", "fines_frac", "gsd", "true_superheat_K"):
                if all(k in r for r in good):
                    smp[k] = float(sum(wi * r[k] for wi, r in zip(w, good)))
        return smp

    def charge_plan(self, a) -> tuple:
        """(crucible cm3, kg of metal per run, atomizer hours per run, extra consumables per run, added failure risk).
        twin/instruments/atomize_yield.charge_plan when it exists; else scaled from the 225 cm3 charge."""
        cm3 = int(a.get("crucible_cm3") or self.spec.crucible_cm3)
        al = self.key == "flaime_al"
        try:
            from twin.instruments import atomize_yield as AY
            pl = AY.charge_plan(self.key, cm3)
            return cm3, pl["charge_g"] / 1000.0, float(pl.get("run_h", 2.5)), dict(pl.get("consumables") or {}), \
                float(pl.get("p_fail_add", 0.0))
        except Exception:
            base = AL_CHARGE_KG if al else CU_CHARGE_KG
            f = cm3 / 225.0
            return cm3, base * f, 2.5 + 0.6 * (f - 1.0), {}, 0.0

    def _materials(self, bill, now_h):
        cost, ready_d, placed = self.stores.ensure(bill, now_h / H, spare=self.spare)
        for o in placed:
            self.charge(now_h, o.cost, f"order {o.item} {o.qty:.3g}")
        self.stores.consume(bill)
        return max(ready_d * H, now_h)

    # ---------------------------------------------------------------------------------------- submit an action
    def estimate(self, action) -> float:
        """Rough money for an action, for the policy and the budget check."""
        k = action["kind"]
        A = ACTIONS[self.key]
        if "usd" in A.get(k, {}):
            return A[k]["usd"]
        fees = {s: self.fac.res[s].st.fee_usd for s in self.fac.res}
        feed = self._feed_cost(action) if k == "powder" else 0.0
        if k == "gas_atomize":
            st = "valimet" if self.key == "flaime_al" else "ames"
            return self.fac.res[st].st.fee_usd + self._gas_feed(action)
        if k == "section":
            return 30.0 + fees.get("prep", 0) + self.fac.res["byu_sem"].st.rate_usd_h * 1.0 + fees.get("xrd", 0) \
                + self.fac.res["xrd"].st.rate_usd_h * 0.75
        if k == "pip":
            return 10.0 + fees.get("pip", 0) + fees.get("prep", 0)
        if k == "blend_ded":
            return 25.0 + fees.get("utah_mxlab", 0) + 0.3 * 300.0 + 40.0
        if self.key == "flaime_al":
            if k == "powder":
                n = action.get("runs", 1)
                f = int(action.get("crucible_cm3") or self.spec.crucible_cm3) / 225.0
                return n * (20 * f + 6.3 + 120 + 37.5 * (1.0 + 0.6 * (f - 1))) + 15 + (35 if action.get("icp") else 0) \
                    + 40 + feed
            if k == "print":
                return fees["utah_midi"] + 80 + 90 + 45
            if k == "test":
                return fees["edm"] + 120 + (60 if action.get("hot") else 0)
            if k == "promote":
                return fees["utah_midi"] * 1.5 + 80 + 90 + fees["edm"] + 120 + 120
        else:
            if k == "powder":
                n = action.get("runs", 1)
                f = int(action.get("crucible_cm3") or self.spec.crucible_cm3) / 225.0
                return n * (60 * f + 14.4 + 350 + 120 + 75 * (1.0 + 0.6 * (f - 1))) + 15 + 40 + feed
            if k == "nsl":
                return fees["nsl"]
            if k in ("preplaced", "small_ded"):
                return fees["utah_mxlab"] + 40 + (60 if k == "small_ded" else 30) + 40
            if k == "large_ded":
                return (fees["utah_mxlab"] + 80 + 60) if self.vertical else (fees["mines_x2"] + 150 + 60)
            if k == "tensile":
                return 120
            if k == "screen":
                return 35
            if k == "immersion":
                return 30 + 140
        return 0.0

    def _feed_cost(self, action) -> float:
        """The charge's own feedstock at today's market price (what the lab would pay for the metal in it; MOQs and
        spares aside). Scandium at about $235/g makes a Sc-bearing charge several times dearer."""
        d = action.get("design")
        if d is None:
            return 0.0
        comp = self.space.composition({e: d.get(e, 0.0) for e in self.space.elements})
        kg = self.charge_plan(action)[1] * action.get("runs", 1)
        day = getattr(self, "now_h", 0.0) / H
        return sum(q * self.market.price(supply.ITEMS[it], day)
                   for it, q in supply.charge_bill(self.key, comp, kg).items())

    def submit(self, action: dict, now_h: float) -> bool:
        self.now_h = now_h
        if self.estimate(action) > self.budget_left:
            self.refused += 1
            return False
        try:
            ok = getattr(self, "_do_" + action["kind"])(action, now_h)
        except KeyError:
            ok = False
        if ok:
            self.inflight += 1
        else:
            self.refused += 1
        return ok

    # ---------------------------------------------------------------------------------------- round 3: async
    GATE_W = 2.0                                  # hours an action may wait for other work at its gating station
    PLAN_F0, PLAN_FULL = 0.15, 0.75               # spending plan: 15 % at day 0, all by 75 % of the horizon
    IMM_DAYS = (1, 3, 7, 14)                      # interim immersion readings (days)

    def plan(self, t_h: float) -> float:
        """Round 3's spending plan, the same for every policy: what may have been spent by t_h. It replaces round 2's
        cap on work in flight as the throttle on money: 15 % of the budget at day 0, then linearly to all of it at
        75 % of the horizon (front-loaded, so early results can be bought; the rest of the year keeps some)."""
        f = self.PLAN_F0 + (1.0 - self.PLAN_F0) * t_h / (self.PLAN_FULL * self.horizon_h)
        return self.spec.budget_usd * min(1.0, f)

    def gate(self, a):
        """(steps before the gating station, the gating station, its hours) for an action, without side effects; None
        for actions with no gate (simulations, NSL, gas atomization)."""
        k = a.get("kind")
        al = self.key == "flaime_al"
        if k == "powder":
            n = int(a.get("runs", 1))
            cm3, kg, run_h, _, _ = self.charge_plan(a)
            cups_h = (2.5 if al else 1.0) * n * (kg / (AL_CHARGE_KG if al else CU_CHARGE_KG))
            return [("shop", cups_h), ("doser", 1.0 * n)], "atomizer", run_h
        return {"blend_ded": ([("doser", 0.5)], "utah_mxlab", 3.0), "print": ([], "utah_midi", 5.0),
                "promote": ([], "utah_midi", 8.0), "test": ([], "edm", 0.75), "section": ([], "prep", 1.5),
                "pip": (([("furnace", 3.0)] if al else []), "prep", 0.5), "preplaced": ([], "utah_mxlab", 4.0),
                "small_ded": ([], "utah_mxlab", 4.0),
                "large_ded": ([], "utah_mxlab", 8.0) if self.vertical else ([], "mines_x2", 5.0),
                "tensile": ([("shop", 1.0)], "tensile", 0.6), "screen": ([], "cubxl", 1.2),
                "immersion": ([], "immersion", 720.0)}.get(k)

    def gate_ok(self, a, now_h) -> bool:
        """Round 3's admission rule: an action starts only if its gating station can take it without waiting more
        than GATE_W hours behind other work (the steps after the gate may queue). So a station's next job is chosen
        when the station frees up, from everything the campaign could do then."""
        g = self.gate(a)
        if g is None:
            return True
        pre, st, h = g
        t = now_h
        for s_, hh in pre:
            s0, d0, _ = self.fac.res[s_].find(t, max(hh, 0.01), self.key)
            t = s0 + d0
        return self.fac.queue_wait(st, t, h, self.key) <= self.GATE_W

    def akey(self, a):
        """What an action targets: (kind, (artifact type, id))."""
        k = a.get("kind")
        for f in ("into", "lot", "build", "deposit"):
            if a.get(f) is not None:
                return (k, (f, a[f]))
        d = a.get("design")
        if isinstance(d, dict):
            return (k, ("design", self.design_id(d)))
        return (k, None)

    def submit3(self, a: dict, now_h: float) -> str:
        """Round 3: try an action now. 'ok', or why not: 'money' (over the budget), 'plan' (over the spending plan),
        'capacity' (its gating station is busy), 'invalid' (its inputs don't allow it)."""
        self.now_h = now_h
        k = a.get("kind")
        if k == "stop":
            st = "ok" if self._do_stop(a, now_h) else "invalid"
        else:
            est = self.estimate(a)
            if est > self.budget_left:
                st = "money"
            elif est > 50.0 and self.spent + est > self.plan(now_h):
                st = "plan"
            elif not self.gate_ok(a, now_h):
                st = "capacity"
            else:
                n0 = len(self.events_out)
                try:
                    ok = getattr(self, "_do_" + k)(a, now_h)
                except KeyError:
                    ok = False
                if ok:
                    aid = next(self._aids)
                    for ev in self.events_out[n0:]:
                        ev[1]["aid"] = aid
                    self.inflight += 1
                    self.pending[aid] = dict(kind=k, key=self.akey(a)[1], t=now_h)
                    if k == "immersion":
                        self._imm[a["deposit"]]["aid"] = aid
                    st = "ok"
                else:
                    st = "invalid"
        self.status_log[st] = self.status_log.get(st, 0) + 1
        if st in ("money", "invalid"):
            self.refused += 1
        return st

    def _interim(self, smp, meas):
        """Interim readings of a coupon in immersion at IMM_DAYS: its average corrosion rate so far from the mass
        change of the uncleaned coupon, from the same film-growth trajectory as the 30-day result
        (instruments/corrosion.py: the rate falls from the early rate to the long-term rate with the film's time
        constant). The coupon's own deviation in its 30-day result carries over (to the power 0.8); the retained
        corrosion product makes an uncleaned coupon read about 25 % low; the balance's 0.1 mg is a large error on
        day 1 and a small one by day 14. Selective attack is not in a mass change: it shows only in the day-30
        section."""
        from twin.instruments.corrosion import _r30
        c = smp["corrosion"]
        r30 = _r30(c["rate_um_yr"], c["early_rate_um_yr"], c["film_days"], 30.0)
        f = (max(meas.get("rate30_um_yr", r30), 1e-6) / max(r30, 1e-6)) ** 0.8
        bias = 0.75 * math.exp(self.rng.normal(0, 0.1))
        out = {}
        for d in self.IMM_DAYS:
            rb = _r30(c["rate_um_yr"], c["early_rate_um_yr"], c["film_days"], float(d))
            w_mg = rb * 1e-4 * 8.9 / 8766.0 * 5.8 * d * 24.0 * 1000.0
            sig = math.hypot(0.06, 0.1 / max(w_mg, 1e-3))
            out[d] = dict(rate_um_yr=float(rb * f * bias * math.exp(self.rng.normal(0, sig))), day=d,
                          mass_change_mg=float(w_mg * bias))
        return out

    def _do_stop(self, a, now_h) -> bool:
        """Round 3: take a coupon out of immersion after an interim reading. Its position is free from now; the
        day-30 section and ICP-MS are not done (nor paid for)."""
        cid = a.get("deposit")
        st = self._imm.get(cid)
        if st is None or st.get("stopped") is not None or st.get("final") or st.get("aid") is None:
            return False
        st["stopped"] = now_h
        self.cancelled.add(st["aid"])
        self.fac.res["immersion"].release_early(st["handle"], now_h)
        D = self.deposits.get(cid)
        if D is not None:
            D["immersion"] = "stopped"
            D["immersion_stopped_day"] = round((now_h - st["t_in"]) / H, 2)
        self.inflight -= 1
        self.pending.pop(st["aid"], None)
        self.stops.append((now_h, cid, round((now_h - st["t_in"]) / H, 2)))
        self.done["immersion_stopped"] = self.done.get("immersion_stopped", 0) + 1
        return True

    def release3(self, t_h, p) -> bool:
        """Round 3: a result comes back. Interim immersion readings are results but leave the action in flight; the
        day-30 booking event books the section and ICP-MS then; a stopped coupon's later events are void. Returns
        True if the policy has something new to see."""
        aid = p.get("aid")
        if aid in self.cancelled:
            return False
        typ = p["type"]
        if typ == "imm_interim":
            D = self.deposits.get(p["deposit"])
            if D is None:
                return False
            D.setdefault("imm_interim", {})[p["day"]] = p["measured"]
            self.corr.append(dict(deposit=p["deposit"], design=p["design"], what=f"imm_d{p['day']}",
                                  measured=p["measured"], t=t_h))
            self.results_log.append((t_h, "imm_interim", p.get("design"), f"imm_d{p['day']}"))
            self.done["imm_interim"] = self.done.get("imm_interim", 0) + 1
            return True
        if typ == "imm_final_book":
            st = self._imm[p["deposit"]]
            st["final"] = True
            t_r, usd = self._route([("byu_sem", 1.0), ("byu_icpms", 0.4)], t_h, "immersion",
                                   tag=dict(design=p["design"], node="immersion", sample=f"D{p['deposit']}"))
            self.charge(t_h, usd + 105.0, "immersion (section and 4 ICP-MS draws)")
            self._emit(t_r, dict(type="cu_test", what="immersion", deposit=p["deposit"], design=p["design"],
                                 measured=st["meas"], aid=aid))
            return False
        self.pending.pop(aid, None)
        self.release(t_h, p)
        return True

    def _emit(self, t_result, payload):
        self.events_out.append((t_result, payload))

    # ---------------------------------------------------------------------------------------- simulators
    def _sim(self, action, now_h, kind):
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
        A = ACTIONS[self.key][kind]
        t_res, usd = self._route(A["steps"], now_h, kind, tag=dict(design=did, node="sim"))
        self.charge(now_h, A["usd"] + usd, kind)
        self._emit(t_res, dict(type="sim", kind=kind, design=did, proc=proc, out=out))
        return True

    def _do_sim_open(self, a, t):
        return self._sim(a, t, "sim_open")

    def _do_sim_tc(self, a, t):
        return self._sim(a, t, "sim_tc")

    def _do_sim_am(self, a, t):
        return self._sim(a, t, "sim_am")

    def _do_sim_heat(self, a, t):
        return self._sim(a, t, "sim_heat")

    def believed_liquidus(self, did) -> float:
        """The liquidus the lab sets the melt by: its best simulation of this design so far (TC over open), or the
        open database's if it has run none (the lab always has that one)."""
        best = None
        for s in self.sims:
            if s["design"] == did and s["kind"] in ("sim_tc", "sim_open"):
                if best is None or s["kind"] == "sim_tc":
                    best = s
        if best is not None:
            return best["out"]["liquidus_C"]
        return self.truth.sim_open(self.designs[did]["composition"])["liquidus_C"]

    # ---------------------------------------------------------------------------------------- powder
    def _do_powder(self, a, now_h):
        """Charge cups machined, dosed and pressed; n atomizer runs (225 or 400 cm3 crucible); sieved; then the lot
        is weighed (mass balance), sized by laser diffraction, imaged and analysed (SEM/EDS), and on request
        characterised by XRD (``xrd``), XRF (``xrf``) and ICP-MS (``icp``)."""
        did = self.design_id(a["design"])
        comp = self.designs[did]["composition"]
        proc = {v.name: a["design"][v.name] for v in spaces.ATOMIZER}
        n = int(a.get("runs", 1))
        al = self.key == "flaime_al"
        cm3, kg, run_h, extra, p_add = self.charge_plan(a)
        bill = supply.charge_bill(self.key, comp, kg * n)
        cons = dict(AL_RUN_CONSUMABLES if al else CU_RUN_CONSUMABLES)
        for k, q in extra.items():
            if k in supply.ITEMS:
                cons[k] = q
        for k, q in cons.items():
            if k == "bn_spray" and al:
                continue
            if k in supply.ITEMS:
                bill[k] = bill.get(k, 0.0) + q * n
        ready = self._materials(bill, now_h)
        lot_id = next(self.ids)                   # drawn here so the bookings can name the lot (same id as before)
        tag = dict(design=did, node="powder", sample=f"L{lot_id}")
        cups_h = (2.5 if al else 1.0) * n * (kg / (AL_CHARGE_KG if al else CU_CHARGE_KG))
        steps = [("shop", cups_h), ("doser", 1.0 * n)]
        t = ready
        usd = 0.0
        runs = []
        TL = self.believed_liquidus(did)
        t_r, u = self._route(steps, t, "charge", tag=tag)
        usd += u
        t = t_r
        for i in range(n):
            t_r, u = self._route([("atomizer", run_h)], t, "atomize", changeover=True, tag=dict(tag, run=i))
            usd += u
            t = t_r
            r = self.truth.atomize(comp, proc, TL, self.rng)
            if p_add > 0 and not r["failed"] and self.rng.random() < p_add:
                r = dict(r, failed=True, usable_frac=0.0)
            r["charge_g"] = kg * 1000.0
            r["crucible_cm3"] = cm3
            runs.append(r)
        steps2 = [("sieve", 0.75), ("psd", 0.25), ("byu_sem", 0.5)]
        if a.get("xrd"):
            steps2.append(("xrd", 0.75))
        if a.get("xrf"):
            steps2.append(("xrf", 0.5))
        if a.get("icp"):
            steps2.append(("byu_icpms", 0.1))
        t_r, u = self._route(steps2, t, "powder QC", tag=tag)
        usd += u
        self.charge(now_h, usd, "powder stations")
        good = [r for r in runs if not r["failed"]]
        cut_g = sum(kg * 1000 * r["usable_frac"] * r["cut_frac"] for r in good)
        if good:
            wts = np.array([r["usable_frac"] * r["cut_frac"] for r in good])
            wts = wts / wts.sum()
            true_comp = {e: float(sum(w * r["composition"].get(e, 0.0) for w, r in zip(wts, good)))
                         for e in set().union(*[r["composition"] for r in good])}
            d50 = float(sum(w * r["d50_um"] for w, r in zip(wts, good)))
            ox = float(sum(w * r["oxygen_ppm"] for w, r in zip(wts, good)))
            sat = float(sum(w * r["satellite_frac"] for w, r in zip(wts, good)))
            carbon = float(sum(w * r.get("carbon_ppm", 0) for w, r in zip(wts, good)))
        else:
            true_comp, d50, ox, sat, carbon = dict(comp), float("nan"), float("nan"), float("nan"), 0.0
        self._lot_truth[lot_id] = dict(composition=true_comp, oxygen_ppm=ox, satellite_frac=sat, carbon_ppm=carbon,
                                       runs=runs, reuse=0.0, crucible_cm3=cm3)
        meas = dict(runs=n, failed_runs=n - len(good), cut_g=cut_g, crucible_cm3=cm3)
        smp = self._lsample(lot_id, did)
        y = self._m("yield", smp)
        meas["yield"] = y
        if good:
            meas["cut_g"] = float(max(y.get("cut_g", cut_g), 0.0))
            psd = self._m("psd", smp)
            sem = self._m("sem_powder", smp)
            eds = self._m("eds", smp)
            meas.update(psd=psd, sem=sem, d50_um=psd.get("d50_um"), cut_frac=psd.get("cut_frac"),
                        oxygen_ppm=ox * math.exp(self.rng.normal(0, 0.1)), eds=eds.get("comp"), eds_lod=eds.get("lod"))
            if a.get("xrd"):
                meas["xrd"] = self._m("xrd_powder", smp)
            if a.get("xrf"):
                meas["xrf"] = self._m("xrf", smp).get("comp")
            if a.get("icp"):
                meas["icp"] = self._m("icpms", smp).get("comp")
        else:
            meas.update(d50_um=None, cut_frac=None, oxygen_ppm=None, eds=None)
        self._emit(t_r, dict(type="lot", id=lot_id, design=did, measured=meas, proc=proc, into=a.get("into")))
        return True

    GAS_KG = {"flaime_al": 50.0, "onr_cu": 25.0}

    def _gas_feed(self, action) -> float:
        """Melting stock for a gas-atomization run at commodity prices x 3 (ingot and master alloys, not 5N rod)."""
        d = action.get("design") or {}
        comp = self.space.composition({e: d.get(e, 0.0) for e in self.space.elements})
        kg = self.GAS_KG[self.key]
        return sum(kg * w / 100.0 * 3.0 * (usgs.price(el) or 20.0) for el, w in comp.items())

    def _do_gas_atomize(self, a, now_h):
        """A powder maker's lot of the design: hot enough to dissolve everything, inert, finer and rounder than the
        ultrasonic atomizer's (FLAIME: Valimet, >= 50 kg; ONR: Ames, 25 kg assumed)."""
        did = self.design_id(a["design"])
        comp = self.designs[did]["composition"]
        al = self.key == "flaime_al"
        st = "valimet" if al else "ames"
        t_r, usd = self._route([(st, 8.0)], now_h, "gas_atomize")
        self.charge(now_h, usd + self._gas_feed(a), "gas_atomize (fee and melting stock)")
        true = dict(comp)
        for el, f in (("Mg", 0.03), ("Zn", 0.05), ("Li", 0.08), ("Mn", 0.02)):
            if true.get(el, 0) > 0:
                true[el] *= 1 - f
        bal = self.space.balance
        true[bal] = 100.0 - sum(v for k, v in true.items() if k != bal)
        from twin.physics import lognorm_frac
        d50 = (35.0 if al else 60.0) * math.exp(self.rng.normal(0, 0.05))
        cut = lognorm_frac(d50, 1.8, *((20.0, 63.0) if al else (45.0, 150.0)))
        kg = self.GAS_KG[self.key]
        lot_id = next(self.ids)
        self._lot_truth[lot_id] = dict(composition=true, oxygen_ppm=900.0 if al else 300.0, satellite_frac=0.03,
                                       carbon_ppm=20.0, runs=[])
        meas = dict(runs=1, failed_runs=0, cut_g=kg * 1000 * 0.95 * cut, d50_um=d50, cut_frac=cut,
                    oxygen_ppm=(900.0 if al else 300.0) * math.exp(self.rng.normal(0, 0.1)),
                    eds={e: v * math.exp(self.rng.normal(0, 0.03)) for e, v in true.items() if e != bal})
        proc = {v.name: a["design"].get(v.name) for v in spaces.ATOMIZER}
        self._emit(t_r, dict(type="lot", id=lot_id, design=did, measured=meas, proc=proc, gas=True))
        return True

    # ---------------------------------------------------------------------------------------- FLAIME: print, test
    def _lot(self, lot_id):
        L = self.lots.get(lot_id)
        if L is None:
            raise KeyError(lot_id)
        return L

    PRINT_FILL_G, PRINT_FUSED_G = 30.0, 12.0          # a 55 mm kit: about 30 g spread (DAL #138); 9 cubes + blanks fused (assumed)
    E8_FILL_G, E8_FUSED_G = 440.0, 70.0               # a 170 mm E8 plate (assumed fused share)

    def _return_powder(self, lot_id, spread_g, fused_g, proc, mode="lpbf", catchment=None):
        """Powder reuse: what comes back to the lot after a build (sieved unfused powder) or a deposit (overspray),
        and the state of what comes back. twin/instruments/reuse.py when it exists; else a plain model."""
        if not self.spec.reuse:
            return 0.0, None
        lt = self._lot_truth[lot_id]
        try:
            from twin.instruments import reuse as RU
            if mode == "lpbf":
                g, st = RU.after_build(lt, spread_g, fused_g, proc, self.rng)
            else:
                g, st = RU.after_ded(lt, spread_g, catchment, proc, self.rng)
            return float(max(g, 0.0)), st
        except Exception:
            if mode == "lpbf":
                g = 0.88 * max(spread_g - fused_g, 0.0)
                st = dict(lt, oxygen_ppm=lt["oxygen_ppm"] + 60.0, satellite_frac=min(lt["satellite_frac"] + 0.01, 0.6),
                          reuse=lt.get("reuse", 0.0) + 1.0)
            else:
                g = 0.55 * max(spread_g * (1.0 - (catchment or 0.6)), 0.0)
                st = dict(lt, oxygen_ppm=lt["oxygen_ppm"] + 150.0, satellite_frac=min(lt["satellite_frac"] + 0.03, 0.6),
                          reuse=lt.get("reuse", 0.0) + 1.0)
            return g, st

    def _do_print(self, a, now_h):
        L = self._lot(a["lot"])
        need = self.PRINT_FILL_G          # a 55 mm reduction kit takes about 30 g (DAL #138)
        if L["remaining_g"] < need:
            return False
        L["remaining_g"] -= need
        params = a["params"][:9]
        ready = self._materials({"build_plate": 1.0, "argon": 1.0 if self.fac.kind == "vertical_lab" else 0.0},
                                now_h)
        bid = next(self.ids)                      # drawn here so the bookings can name the build (same id as before)
        tag = dict(design=L["design"], node="print", lot=a["lot"], sample=f"B{bid}")
        t_r, usd = self._route([("utah_midi", 5.0), ("density", 0.5), ("byu_sem", 1.0)], ready, "print", tag=tag)
        self.charge(now_h, usd, "print")
        lt = self._lot_truth[a["lot"]]
        lot = dict(lt, composition=lt["composition"])
        parts, meas = [], []
        for p in params:
            part = self.truth.build(lot, p, self.rng)
            part["reuse"] = lt.get("reuse", 0.0)
            parts.append(part)
            meas.append(dict(self._soundness(part, L["design"]), params=p))
        back, st = self._return_powder(a["lot"], need, self.PRINT_FUSED_G, params[0])
        self._part_truth[bid] = dict(parts=parts, lot=a["lot"], bars_at=int(a.get("bars_at", 0)))
        self._emit(t_r, dict(type="build", id=bid, lot=a["lot"], design=L["design"], measured=meas,
                             bars_at=int(a.get("bars_at", 0)), returned_g=back, returned_state=st))
        return True

    def _do_section(self, a, now_h):
        """Cut, mount and polish one part (a cube of a build, or a block of a deposit), then SEM (BSE) and EBSD on the
        section and a Vickers row; XRD on the section on request (always for copper, for beta')."""
        al = self.key == "flaime_al"
        if al:
            B = self.builds.get(a.get("build"))
            if B is None or B.get("_sectioned"):
                return False
            B["_sectioned"] = True
            pt = self._part_truth[a["build"]]
            i = int(a.get("cube", pt["bars_at"]))
            part, did = pt["parts"][min(i, len(pt["parts"]) - 1)], B["design"]
            key = ("build", a["build"])
        else:
            D = self.deposits.get(a.get("deposit"))
            if D is None or D.get("_sectioned"):
                return False
            D["_sectioned"] = True
            pt = self._part_truth[a["deposit"]]
            i = int(a.get("block", 0))
            part, did = pt["parts"][min(i, len(pt["parts"]) - 1)], D["design"]
            key = ("deposit", a["deposit"])
        steps = [("prep", 1.5), ("byu_sem", 1.0), ("hardness", 0.25)]
        if a.get("xrd") or not al:
            steps.append(("xrd", 0.75))
        tag = dict(design=did, node="section", sample=("B" if al else "D") + str(key[1]))
        t_r, usd = self._route(steps, now_h, "section", tag=tag)
        self.charge(now_h, usd + 30.0, "section (mount, polish, SEM, EBSD, HV)")
        smp = self._psample(part, did)
        meas = dict(sem=self._m("sem_section", smp), ebsd=self._m("ebsd", smp), vickers=self._m("vickers", smp),
                    index=i)
        if a.get("xrd") or not al:
            meas["xrd"] = self._m("xrd_part", smp)
        self._emit(t_r, dict(type="section", key=key, design=did, measured=meas))
        return True

    def _do_pip(self, a, now_h):
        """Profilometry-based indentation plastometry on one part: heat-treated first (aluminium, the same treatment
        as the tensile bars), polished flat, indented and profiled. A stress-strain curve without machining bars."""
        al = self.key == "flaime_al"
        if al:
            B = self.builds.get(a.get("build"))
            if B is None or B.get("_pip"):
                return False
            B["_pip"] = True
            pt = self._part_truth[a["build"]]
            i = int(a.get("cube", pt["bars_at"]))
            key = ("build", a["build"])
            did = B["design"]
            steps = [("furnace", 3.0), ("prep", 0.5), ("pip", 0.5)]
        else:
            D = self.deposits.get(a.get("deposit"))
            if D is None or D.get("_pip"):
                return False
            D["_pip"] = True
            pt = self._part_truth[a["deposit"]]
            i = int(a.get("block", 0))
            key = ("deposit", a["deposit"])
            did = D["design"]
            steps = [("prep", 0.5), ("pip", 0.5)]
        part = pt["parts"][min(i, len(pt["parts"]) - 1)]
        t_r, usd = self._route(steps, now_h, "pip", tag=dict(design=did, node="pip",
                                                             sample=("B" if al else "D") + str(key[1])))
        self.charge(now_h, usd + 10.0, "pip")
        meas = dict(self._m("pip", self._psample(part, did)), index=i)
        self._emit(t_r, dict(type="pip", key=key, design=did, measured=meas))
        return True

    def _al_score(self, part, s, hot=None):
        comp = part["composition"]
        b = usgs.mineral_burden(comp)
        ref_c = usgs.mineral_burden({"Al": 89.65, "Si": 10.0, "Mg": 0.35})["cmdri_log"]
        ref_m = usgs.mineral_burden({"Al": 94.4, "Mg": 4.6, "Sc": 0.7, "Zr": 0.3})["mbs_lin"]
        feas = part["rel_density"] >= 0.995 and part["crack_free"] and b["mbs_lin"] <= 0.10 * ref_m
        d = [_desir(s["ys_MPa"], 150, 400), _desir(s["el_pct"], 2, 15), _desir(1.5 * ref_c - b["cmdri_log"], 0, 1.5 * ref_c)]
        u = float(np.prod(d) ** (1 / 3)) * (1.0 if feas else 0.0)
        disc = feas and ((s["ys_MPa"] >= 250 and s["el_pct"] >= 5) or (s["ys_MPa"] >= 200 and s["el_pct"] >= 8)) \
            and b["cmdri_log"] <= 1.5 * ref_c
        return u, dict(ys=s["ys_MPa"], el=s["el_pct"], cmdri=b["cmdri_log"], mbs=b["mbs_lin"], feasible=bool(feas),
                       discovery=bool(disc), rel_density=part["rel_density"], crack_free=bool(part["crack_free"]),
                       hot_ys=None if hot is None else hot["ys_MPa"])

    def _do_test(self, a, now_h):
        B = self.builds.get(a["build"])
        if B is None or B.get("tested"):
            return False
        B["tested"] = True
        steps = [("edm", 0.75), ("furnace", 3.0), ("shop", 1.0), ("tensile", 0.6)]
        if a.get("hot"):
            steps.append(("tensile_hot", 1.5))
        t_r, usd = self._route(steps, now_h, "test", tag=dict(design=B["design"], node="test", sample=f"B{a['build']}"))
        self.charge(now_h, usd + 120.0, "test (3 specimens machined)")
        pt = self._part_truth[a["build"]]
        part = pt["parts"][pt["bars_at"]]
        s = self.truth.strength(part)
        hot = self.truth.strength(part, 250.0) if a.get("hot") else None
        smp = self._psample(part, B["design"], hot=bool(a.get("hot")))
        m = self._m("tensile", smp)
        meas = dict(ys_MPa=m["ys_MPa"], uts_MPa=m["uts_MPa"], el_pct=m["el_pct"], n_bars=m.get("n_bars", 3))
        if hot:
            mh = self._m("tensile_hot", smp)
            meas["hot_ys_MPa"] = mh["ys_MPa"]
        u, det = self._al_score(part, s, hot)
        self._emit(t_r, dict(type="test", build=a["build"], design=B["design"], measured=meas,
                             params=B["measured"][pt["bars_at"]]["params"], score=(u, det)))
        return True

    def _do_promote(self, a, now_h):
        L = self._lot(a["lot"])
        if L["remaining_g"] < self.E8_FILL_G:
            return False
        L["remaining_g"] -= self.E8_FILL_G
        ready = self._materials({"build_plate": 1.0, "argon": 1.0}, now_h)
        t_r, usd = self._route([("utah_midi", 8.0), ("edm", 1.0), ("furnace", 3.0), ("shop", 1.5),
                                ("tensile", 0.6), ("tensile_hot", 1.5)], ready, "promote",
                               tag=dict(design=L["design"], node="test", lot=a["lot"], sample=f"E8-L{a['lot']}"))
        self.charge(now_h, usd + self.fac.res["utah_midi"].st.fee_usd * 0.5 + 120.0, "promote (E8 plate)")
        lot = self._lot_truth[a["lot"]]
        part = self.truth.build(lot, a["params"], self.rng)
        s = self.truth.strength(part)
        hot = self.truth.strength(part, 250.0)
        smp = self._psample(part, L["design"], hot=True)
        m, mh = self._m("tensile", smp), self._m("tensile_hot", smp)
        snd = self._soundness(part, L["design"])
        meas = dict(ys_MPa=m["ys_MPa"], el_pct=m["el_pct"], uts_MPa=m["uts_MPa"], hot_ys_MPa=mh["ys_MPa"],
                    rel_density=snd["rel_density"])
        u, det = self._al_score(part, s, hot)
        det["e8"] = True
        back, st = self._return_powder(a["lot"], self.E8_FILL_G, self.E8_FUSED_G, a["params"])
        self._emit(t_r, dict(type="test", build=None, design=L["design"], measured=meas, params=a["params"],
                             score=(u, det), e8=True, lot=a["lot"], returned_g=back, returned_state=st))
        return True

    # ---------------------------------------------------------------------------------------- ONR: DED and tests
    def _do_nsl(self, a, now_h):
        L = self._lot(a["lot"])
        t_r, usd = self._route([("nsl", 0.01)], now_h, "nsl", tag=dict(design=L["design"], node="nsl",
                                                                        sample=f"L{a['lot']}"))
        self.charge(now_h, usd, "NSL certification")
        lt = self._lot_truth[a["lot"]]
        meas = dict(oxygen_ppm=lt["oxygen_ppm"] * math.exp(self.rng.normal(0, 0.05)),
                    carbon_ppm=lt["carbon_ppm"] * math.exp(self.rng.normal(0, 0.05)),
                    composition={e: v * math.exp(self.rng.normal(0, 0.015)) for e, v in lt["composition"].items()
                                 if e != "Cu"})
        self._emit(t_r, dict(type="nsl", lot=a["lot"], measured=meas))
        return True

    def _do_preplaced(self, a, now_h):
        return self._ded(a, now_h, "preplaced", 20.0, [("utah_mxlab", 4.0), ("byu_sem", 1.0)], 0.25)

    def _do_small_ded(self, a, now_h):
        return self._ded(a, now_h, "blown_small", 450.0, [("utah_mxlab", 4.0), ("byu_sem", 2.0)], 0.0)

    BLEND_ITEMS = {"Cu": "cu_shot", "Ni": "al_ni20", "Al": "al_shot", "Fe": "fe_powder", "Mn": "mn_flake",
                   "Cr": "cr_powder", "Si": "si_lump_cu", "Nb": "nb_powder", "Ti": "ti_sponge"}

    def _do_blend_ded(self, a, now_h):
        """Copper, round 2: up to 4 blocks deposited from elemental powders blended to the design (300 g; the powder
        doser weighs the blend) on the MX-Lab: a screen before paying to atomize. No atomizer, no plate or nozzle."""
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
        dep = next(self.ids)                      # drawn here so the bookings can name the deposit (same id as before)
        tag = dict(design=did, node="ded_small", blend=True, sample=f"D{dep}")
        t_r, usd = self._route([("doser", 0.5), ("utah_mxlab", 3.0), ("byu_sem", 1.0)], ready, "blend_ded", tag=tag)
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
        return True

    def _do_large_ded(self, a, now_h):
        """Blocks for bars and coupons. In the proposals: 2 kg at Mines (an NSL certificate first). In the vertical
        lab: 1 kg on the in-house MX-Lab, an eight-hour plate (bottleneck.py), certified by its own ICP-MS."""
        L = self._lot(a["lot"])
        if self.vertical:
            return self._ded(a, now_h, "blown_large", 1000.0, [("utah_mxlab", 8.0), ("byu_sem", 1.0)], 1.0)
        if not L.get("nsl"):
            return False
        return self._ded(a, now_h, "blown_large", 2000.0, [("mines_x2", 5.0), ("byu_sem", 2.0)], 1.0)

    def _ded(self, a, now_h, mode, grams, steps, substrates):
        L = self._lot(a["lot"])
        if L["remaining_g"] < grams:
            return False
        L["remaining_g"] -= grams
        ready = self._materials({"ded_substrate": substrates} if substrates else {}, now_h)
        node = {"preplaced": "ded_small", "blown_small": "ded_small", "blown_large": "ded_large"}[mode]
        dep = next(self.ids)                      # drawn here so the bookings can name the deposit (same id as before)
        t_r, usd = self._route(steps, ready, mode, tag=dict(design=L["design"], node=node, lot=a["lot"],
                                                            sample=f"D{dep}"))
        self.charge(now_h, usd, mode)
        lot = self._lot_truth[a["lot"]]
        params = a["params"] if isinstance(a["params"], list) else [a["params"]]
        params = params[:(4 if mode != "blown_large" else 1)]
        did = L["design"]
        nab = {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}
        parts, meas = [], []
        for p in params:
            part = self.truth.deposit(lot, p, mode, self.rng, substrate=nab if mode != "blown_small" else None)
            part["reuse"] = lot.get("reuse", 0.0)
            parts.append(part)
            m = dict(self._soundness(part, did), dilution=part["dilution"] * math.exp(self.rng.normal(0, 0.1)), params=p)
            if mode != "preplaced":
                m.update(beta_prime=float(np.clip(part["beta_prime"] + self.rng.normal(0, 0.03), 0, 1)),
                         catchment=part["catchment"] * math.exp(self.rng.normal(0, 0.05)),
                         grain_um=part["grain_um"] * math.exp(self.rng.normal(0, 0.1)))
            if part["fusion_ok"] is not None:
                m["fusion_ok"] = part["fusion_ok"] if self.rng.random() > 0.05 else (not part["fusion_ok"])
            meas.append(m)
        catch = float(np.mean([pp["catchment"] for pp in parts])) if parts else 0.6
        back, st = self._return_powder(a["lot"], grams, None, params[0], mode="ded", catchment=catch) \
            if mode != "preplaced" else (0.0, None)
        self._part_truth[dep] = dict(parts=parts, lot=a["lot"], mode=mode)
        self._emit(t_r, dict(type="deposit", id=dep, lot=a["lot"], design=did, mode=mode, measured=meas,
                             returned_g=back, returned_state=st))
        return True

    def _dep(self, dep_id):
        D = self.deposits.get(dep_id)
        if D is None:
            raise KeyError(dep_id)
        return D, self._part_truth[dep_id]["parts"][0]

    def _cu_ref_rate(self):
        if not hasattr(self, "_ref_rate"):
            t = truth_cu.CuTruth(0)
            comp = {"Ni": 30.0, "Fe": 0.6, "Mn": 0.6, "Cu": 68.8}
            part = dict(composition=comp, thermo=t.thermo(comp), porosity=0.003, beta_prime=0.0, temper=0.5)
            self._ref_rate = t.corrosion(part)["rate_um_yr"]
        return self._ref_rate

    def _cu_check(self, dep_id):
        """Score a deposit once it has both a tensile and an immersion result."""
        D = self.deposits[dep_id]
        if D["mode"] != "blown_large" or "tensile" not in D or "immersion" not in D or D.get("scored"):
            return None
        D["scored"] = True
        part = self._part_truth[dep_id]["parts"][0]
        s, c = self.truth.strength(part), self.truth.corrosion(part)
        ref = self._cu_ref_rate()
        ni = part["composition"].get("Ni", 0.0)
        feas = part["rel_density"] >= 0.99 and part["crack_free"]
        d = [_desir(s["ys_MPa"], 100, 400), _desir(s["el_pct"], 5, 35),
             _desir(3.0 * ref - c["rate_um_yr"], 0, 2.5 * ref), _desir(30 - ni, 0, 30)]
        u = float(np.prod(d) ** 0.25) * (1.0 if feas else 0.0)
        passed = feas and c["rate_um_yr"] <= ref and c["attack_um"] <= 3.0
        return u, dict(ys=s["ys_MPa"], el=s["el_pct"], rate=c["rate_um_yr"], attack=c["attack_um"], ni=ni,
                       feasible=bool(feas), discovery=bool(passed and s["ys_MPa"] >= 150 and s["el_pct"] >= 15),
                       h5_pass=bool(passed), repair_ok=part.get("fusion_ok"))

    def _do_tensile(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if D["mode"] == "preplaced" or "tensile" in D:
            return False
        D["tensile"] = "pending"
        t_r, usd = self._route([("shop", 1.0), ("tensile", 0.6)], now_h, "tensile",
                               tag=dict(design=D["design"], node="tensile", sample=f"D{a['deposit']}"))
        self.charge(now_h, usd + 120.0, "tensile (3 specimens machined)")
        m = self._m("tensile", self._psample(part, D["design"]))
        meas = dict(ys_MPa=m["ys_MPa"], el_pct=m["el_pct"], uts_MPa=m["uts_MPa"], n_bars=m.get("n_bars", 3))
        self._emit(t_r, dict(type="cu_test", what="tensile", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _do_screen(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if a.get("block") is not None:
            ps = self._part_truth[a["deposit"]]["parts"]
            part = ps[min(int(a["block"]), len(ps) - 1)]
        if D["mode"] == "preplaced" or D.get("_screened"):
            return False
        D["_screened"] = True
        t_r, usd = self._route([("cubxl", 1.2), ("byu_icpms", 0.1)], now_h, "screen",
                               tag=dict(design=D["design"], node="screen", sample=f"D{a['deposit']}"))
        self.charge(now_h, usd, "corrosion screen")
        meas = self._m("corrosion_screen", self._psample(part, D["design"]))
        self._emit(t_r, dict(type="cu_test", what="screen", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _do_immersion(self, a, now_h):
        if self.async_:
            return self._do_immersion3(a, now_h)
        D, part = self._dep(a["deposit"])
        if D["mode"] != "blown_large" or "immersion" in D:
            return False
        D["immersion"] = "pending"
        t_r, usd = self._route([("immersion", 720.0), ("byu_sem", 1.0), ("byu_icpms", 0.4)], now_h, "immersion",
                               tag=dict(design=D["design"], node="immersion", sample=f"D{a['deposit']}"))
        self.charge(now_h, usd + 105.0, "immersion (4 ICP-MS draws)")
        meas = self._m("immersion", self._psample(part, D["design"]))
        self._emit(t_r, dict(type="cu_test", what="immersion", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _do_immersion3(self, a, now_h):
        """Round 3: the coupon goes into an immersion position for 30 days (the position and the coupon are all it
        holds), with interim readings at IMM_DAYS; at day 30 its section and ICP-MS are booked. The policy may stop
        it after any interim reading (``kind='stop'``)."""
        D, part = self._dep(a["deposit"])
        if D["mode"] != "blown_large" or "immersion" in D:
            return False
        D["immersion"] = "pending"
        hd = []
        tag = dict(design=D["design"], node="immersion", sample=f"D{a['deposit']}")
        t_r, usd = self._route([("immersion", 720.0)], now_h, "immersion", tag=tag, handles=hd)
        t_in = t_r - 720.0
        self.charge(now_h, usd + 30.0, "immersion (coupon cut and in)")
        smp = self._psample(part, D["design"])
        meas = self._m("immersion", smp)
        self._imm[a["deposit"]] = dict(handle=hd[0][1], t_in=t_in, meas=meas, design=D["design"], stopped=None)
        op = self.fac.res.get("operator")
        for d, m in self._interim(smp, meas).items():
            tr = t_in + d * H
            if not self.vertical and op is not None:
                tr = fac.next_open(op.st.hours, tr)          # weighed when someone is in
            self._emit(tr + 0.25, dict(type="imm_interim", deposit=a["deposit"], design=D["design"], day=d,
                                       measured=m))
        self._emit(t_in + 720.0, dict(type="imm_final_book", deposit=a["deposit"], design=D["design"]))
        return True

    # ---------------------------------------------------------------------------------------- results come back
    def _return_to_lot(self, lot_id, grams, state, t_h):
        """Blend returned powder (sieved unfused powder or overspray) into what is left of its lot, by mass."""
        if not grams or lot_id not in self.lots or state is None:
            return
        L, lt = self.lots[lot_id], self._lot_truth[lot_id]
        wa, wb = max(L["remaining_g"], 1e-9), float(grams)
        for k in ("oxygen_ppm", "satellite_frac", "carbon_ppm", "reuse"):
            if k in state:
                lt[k] = (lt.get(k, 0.0) * wa + state[k] * wb) / (wa + wb)
        L["remaining_g"] += wb
        L["returned_g"] = L.get("returned_g", 0.0) + wb
        self.reuse_log.append((t_h, lot_id, wb))

    def release(self, t_h, p):
        self.inflight -= 1
        typ = p["type"]
        # completed evaluations by kind (a counter only; round 3's fairness table counts rounds 2 and 3 alike)
        kd = {"lot": "powder_gas" if p.get("gas") else ("powder_topup" if p.get("into") else "powder"),
              "build": "print", "deposit": p.get("mode"), "cu_test": p.get("what"), "sim": p.get("kind"),
              "test": "test_e8" if p.get("e8") else "test"}.get(typ, typ)
        self.done[kd] = self.done.get(kd, 0) + 1
        self.results_log.append((t_h, typ, p.get("design"), p.get("what") or typ))
        if p.get("returned_g"):
            self._return_to_lot(p.get("lot"), p["returned_g"], p.get("returned_state"), t_h)
        if typ == "sim":
            self.sims.append(dict(kind=p["kind"], design=p["design"], proc=p["proc"], out=p["out"], t=t_h))
        elif typ == "lot":
            m = p["measured"]
            into = p.get("into")
            if into in self.lots and self.lots[into]["design"] == p["design"]:
                # a top-up: blend into the earlier lot of the same design (truth by mass)
                L, a, b = self.lots[into], self._lot_truth[into], self._lot_truth[p["id"]]
                wa, wb = max(L["remaining_g"], 1e-9), max(m["cut_g"], 0.0)
                if wb > 0:
                    for k in ("oxygen_ppm", "satellite_frac", "carbon_ppm"):
                        a[k] = (a[k] * wa + b[k] * wb) / (wa + wb)
                    a["composition"] = {e: (a["composition"].get(e, 0) * wa + b["composition"].get(e, 0) * wb)
                                        / (wa + wb) for e in set(a["composition"]) | set(b["composition"])}
                L["remaining_g"] += wb
                L["measured"]["runs"] += m["runs"]
                L["measured"]["failed_runs"] += m["failed_runs"]
                L["measured"]["cut_g"] += wb
                L["topped_up"] = L.get("topped_up", 0) + 1
                L.pop("nsl", None)                    # a blended lot needs certifying again
            else:
                self.lots[p["id"]] = dict(id=p["id"], design=p["design"], measured=m, remaining_g=m["cut_g"],
                                          proc=p["proc"], t=t_h, gas=bool(p.get("gas")))
        elif typ == "nsl":
            self.lots[p["lot"]]["nsl"] = p["measured"]
        elif typ in ("section", "pip"):
            kind, i = p["key"]
            tgt = self.builds if kind == "build" else self.deposits
            if i in tgt:
                tgt[i][typ] = p["measured"]
        elif typ == "build":
            self.builds[p["id"]] = dict(id=p["id"], lot=p["lot"], design=p["design"], measured=p["measured"],
                                        bars_at=p["bars_at"], t=t_h)
        elif typ == "deposit":
            self.deposits[p["id"]] = dict(id=p["id"], lot=p["lot"], design=p["design"], mode=p["mode"],
                                          measured=p["measured"], t=t_h)
        elif typ == "test":
            self.tests.append(dict(build=p["build"], design=p["design"], measured=p["measured"], params=p["params"],
                                   e8=p.get("e8", False), t=t_h))
            u, det = p["score"]
            self.demonstrated.append(dict(t_h=t_h, spent=self.spent, u=u, design=p["design"], **det))
        elif typ == "cu_test":
            D = self.deposits[p["deposit"]]
            D[p["what"]] = p["measured"]
            self.corr.append(dict(deposit=p["deposit"], design=p["design"], what=p["what"], measured=p["measured"],
                                  t=t_h))
            sc = self._cu_check(p["deposit"])
            if sc:
                u, det = sc
                self.demonstrated.append(dict(t_h=t_h, spent=self.spent, u=u, design=p["design"], **det))

    # ---------------------------------------------------------------------------------------- what the policy sees
    def view(self, now_h):
        self.now_h = now_h
        return dict(key=self.key, now_h=now_h, budget_left=self.budget_left, spent=self.spent, space=self.space,
                    designs={i: d["composition"] for i, d in self.designs.items()},
                    design_inputs={i: d["design"] for i, d in self.designs.items()},
                    sims=self.sims, lots=self.lots, builds=self.builds, tests=self.tests, deposits=self.deposits,
                    corr=self.corr, inflight=self.inflight, wip=(10 ** 6 if self.async_ else self.spec.wip),
                    estimate=self.estimate, vertical=self.vertical, large_g=1000.0 if self.vertical else 2000.0,
                    crucible_cm3=self.spec.crucible_cm3, async_=self.async_,
                    pending=list(self.pending.values()) if self.async_ else [],
                    imm=({k: dict(t_in=x["t_in"], stopped=x.get("stopped"), final=bool(x.get("final")))
                          for k, x in self._imm.items()} if self.async_ else {}),
                    plan_left=(self.plan(now_h) - self.spent) if self.async_ else self.budget_left,
                    horizon_h=self.horizon_h)


class Twin:
    """Both campaigns on one clock. ``policies``: {campaign key: policy}; ``specs``: {campaign key: Spec}."""

    def __init__(self, specs: dict, policies: dict, scenario="historical", facility="proposed", seed=0,
                 horizon_days=365, isolated=False, external=None, trace=False, mode="wip"):
        """``external``: a callable given each Facility before the campaigns start; it may book outside users' jobs
        (``fac.res[station].book(t, hours, "external", "user job")``), which then take their slots (twin/cloud.py)."""
        self.h = horizon_days * H
        self.horizon_days = horizon_days
        supply.load_private()
        self.market = supply.Market(scenario, seed, int(horizon_days) + 400)
        # mode='wip': rounds 1 and 2 (a cap on each campaign's actions in flight, decisions when results return);
        # mode='async': round 3 (no cap: physical capacity, helpers and fixtures, decisions whenever stations free up)
        self.mode = mode
        phys = mode == "async"
        shared = fac.Facility(facility, seed, self.h + 2000 * H, physical=phys)
        self.campaigns = {}
        for k, sp in specs.items():
            f = fac.Facility(facility, seed, self.h + 2000 * H, physical=phys) if isolated else shared
            self.campaigns[k] = Campaign(sp, policies[k], self.market, f, self.h)
            self.campaigns[k].async_ = phys
        self.facilities = {k: c.fac for k, c in self.campaigns.items()}
        if external is not None:
            for f in {id(f): f for f in self.facilities.values()}.values():
                external(f)
        self.seq = itertools.count()
        # trace=True: every iteration's proposals as the optimizer scored them (twin/trace.py writes the trace file)
        self.trace = [] if trace else None
        self._iters = {k: 0 for k in self.campaigns}

    DT_H = 1.0                   # round 3: decision grid (hours)
    N_ASK = 24                   # round 3: actions a policy may rank per decision

    def run_async(self, verbose=False):
        """Round 3's event loop. Results come back at their own times. On an hourly grid, each campaign whose results
        came back, or whose lab had a booking end (a station, robot, person or fixture freed up), or which hasn't
        been asked for a day, is asked for a ranked list of actions across all its parts; each is admitted if the
        spending plan and its gating station allow it (``Campaign.submit3``). The campaigns take turns going first.
        Policies may implement ``admitted(action)`` and ``rejected(action, why)``."""
        q, ends = [], []
        for f in {id(f): f for f in self.facilities.values()}.values():
            for r in f.res.values():
                r.on_commit = lambda e, _ends=ends: heapq.heappush(_ends, e)
        dirty = {k: True for k in self.campaigns}
        last = {k: -1e9 for k in self.campaigns}
        keys = list(self.campaigns)
        g, step = 0.0, 0
        while g <= self.h + 1e-9:
            while q and q[0][0] <= g + 1e-9:
                tr, _, k, p = heapq.heappop(q)
                c = self.campaigns[k]
                if c.release3(tr, p):
                    dirty[k] = True
                for tr2, pay in c.events_out:
                    heapq.heappush(q, (tr2, next(self.seq), k, pay))
                c.events_out = []
            freed = False
            while ends and ends[0] <= g + 1e-9:
                heapq.heappop(ends)
                freed = True
            order = keys if step % 2 == 0 else keys[::-1]
            for k in order:
                c = self.campaigns[k]
                if not (dirty[k] or freed or g - last[k] >= 24.0) or c.budget_left <= 0:
                    continue
                dirty[k], last[k] = False, g
                v = c.view(g)
                acts = c.policy.propose(v, self.N_ASK) or []
                rec = None
                if self.trace is not None and acts:
                    self._iters[k] += 1
                    rec = dict(it=self._iters[k], t_h=round(g, 3), campaign=k, n_free=None,
                               spent=round(c.spent, 2), proposals=[])
                for a in acts:
                    st = c.submit3(a, g)
                    ok = st == "ok"
                    cb = getattr(c.policy, "admitted" if ok else "rejected", None)
                    if cb is not None:
                        cb(a) if ok else cb(a, st)
                    if rec is not None:
                        rec["proposals"].append(_trace_action(c, a, ok))
                if rec is not None:
                    rec["best_obs"] = _best_obs(c.policy, v)
                    self.trace.append(rec)
                for tr2, pay in c.events_out:
                    heapq.heappush(q, (tr2, next(self.seq), k, pay))
                c.events_out = []
            g += self.DT_H
            step += 1
        return self.summary()

    def run(self, verbose=False):
        """The event loop. A campaign is asked for actions whenever one of its results comes back, and once a day
        while it has nothing in flight (so it can start, and restart after waiting on materials)."""
        if self.mode == "async":
            return self.run_async(verbose)
        q = []
        tick = {}
        for k in self.campaigns:
            heapq.heappush(q, (0.0, next(self.seq), k, None))
            tick[k] = 0.0
        while q:
            t, _, k, p = heapq.heappop(q)
            if t > self.h:
                break
            c = self.campaigns[k]
            if p is not None:
                c.release(t, p)
            free = c.spec.wip - c.inflight
            if free > 0 and c.budget_left > 0:
                v = c.view(t)
                acts = c.policy.propose(v, free) or []
                rec = None
                if self.trace is not None and acts[:free]:
                    self._iters[k] += 1
                    rec = dict(it=self._iters[k], t_h=round(t, 3), campaign=k, n_free=free,
                               spent=round(c.spent, 2), proposals=[])
                for a in acts[:free]:
                    ok = c.submit(a, t)
                    if rec is not None:
                        rec["proposals"].append(_trace_action(c, a, ok))
                if rec is not None:
                    rec["best_obs"] = _best_obs(c.policy, v)
                    self.trace.append(rec)
                for tr, pay in c.events_out:
                    heapq.heappush(q, (tr, next(self.seq), k, pay))
                c.events_out = []
            if c.inflight == 0 and c.budget_left > 0 and tick[k] <= t and t + H <= self.h:
                tick[k] = t + H
                heapq.heappush(q, (t + H, next(self.seq), k, None))
        return self.summary()

    def event_log(self, meta=None) -> dict:
        """Every booking (station, hours, campaign, design, network node), every design, every result and the
        best-so-far curves: what the video and twin/cloud.py read (schema in notes/twin.md, round 2)."""
        facs = {id(f): f for f in self.facilities.values()}
        stations, events = {}, []
        for f in facs.values():
            for k, r in f.res.items():
                if not r.jobs:
                    continue
                st = r.st
                stations[k] = dict(name=st.name, units=st.units, hours=st.hours, external=st.external)
                for j in r.jobs:
                    t0, t1, camp, what = j[:4]
                    tag = (j[4] if len(j) > 4 else None) or {}
                    ev = dict(t0_h=round(t0, 3), t1_h=round(t1, 3), station=k, campaign=camp, what=what,
                              design=tag.get("design"), node=tag.get("node"))
                    for kk in ("sample", "run", "lot", "blend"):      # round 2: which part, which atomizer run
                        if tag.get(kk) is not None:
                            ev[kk] = tag[kk]
                    events.append(ev)
        events.sort(key=lambda e: e["t0_h"])
        designs = {k: {str(i): {e: round(v, 3) for e, v in d["composition"].items()} for i, d in c.designs.items()}
                   for k, c in self.campaigns.items()}
        results = []
        for k, c in self.campaigns.items():
            best = 0.0
            for d in sorted(c.demonstrated, key=lambda d: d["t_h"]):
                best = max(best, d["u"])
                results.append(dict(t_h=round(d["t_h"], 3), campaign=k, type="demonstrated", design=d["design"],
                                    u_true=round(d["u"], 4), best_true=round(best, 4), spent=round(d["spent"], 2),
                                    ys=d.get("ys"), el=d.get("el"), discovery=d.get("discovery")))
            for (t, typ, des, node) in c.results_log:
                results.append(dict(t_h=round(t, 3), campaign=k, type=typ, design=des, node=node))
        results.sort(key=lambda r: r["t_h"])
        summ = self.summary()
        curves = {k: [[round(a, 3), round(b, 2), round(u, 4)] for a, b, u in summ[k]["curve"]] for k in self.campaigns}
        return dict(meta=dict(meta or {}, horizon_days=self.horizon_days), stations=stations, events=events,
                    designs=designs, results=results, curves=curves)

    def summary(self):
        out = {}
        for k, c in self.campaigns.items():
            best, curve = 0.0, []
            for d in sorted(c.demonstrated, key=lambda d: d["t_h"]):
                best = max(best, d["u"])
                curve.append((d["t_h"] / H, d["spent"], best))
            out[k] = dict(spent=c.spent, budget=c.spec.budget_usd, best=best, curve=curve,
                          n_demonstrated=len(c.demonstrated),
                          n_discoveries=sum(1 for d in c.demonstrated if d.get("discovery")),
                          n_designs=len(c.designs), n_lots=len(c.lots), n_sims=len(c.sims),
                          n_builds=len(c.builds) + len(c.deposits), refused=c.refused,
                          orders=len(c.stores.orders), backorders=sum(1 for o in c.stores.orders if o.backordered),
                          spend_by=_spend_by(c.ledger), demonstrated=c.demonstrated,
                          returned_g=round(sum(g for _, _, g in c.reuse_log), 1),
                          n_results={t: sum(1 for r in c.results_log if r[1] == t) for t in
                                     sorted({r[1] for r in c.results_log})},
                          done=dict(c.done), stops=list(c.stops), status=dict(c.status_log),
                          n_inflight_end=c.inflight,
                          n_alloys_made=len({L["design"] for L in c.lots.values()} |
                                            {D["design"] for D in c.deposits.values() if D.get("lot") is None}))
        out["utilization"] = {k: f.utilization(self.h) for k, f in
                              ({"shared": next(iter(self.facilities.values()))}.items())}
        out["market_events"] = self.market.events
        return out


def _trace_action(c, a, ok):
    """One proposed action as the trace records it: what it is, the point, and what the policy scored it at. Reads the
    action with dict.get (a deferred action marks its part decided when its 'kind' is read through []); a design id is
    looked up only for an accepted action, whose design already has one, so no id is drawn that a run without the
    trace wouldn't draw."""
    g = lambda kk, d=None: dict.get(a, kk, d)
    kind = g("kind")
    rec = dict(kind=kind, accepted=bool(ok), acq=g("_acq"), acq_kind=g("_acq_kind"))
    for kk in ("ei", "mu", "sd", "cost", "best_obs"):
        x = g("_" + kk)
        if x is not None:
            rec[kk] = round(float(x), 6)
    d = g("design")
    if isinstance(d, dict):
        rec["x"] = {kk: round(float(vv), 4) for kk, vv in d.items()}
        if ok:
            rec["design"] = c.design_id(d)
    for kk in ("lot", "build", "deposit", "cube", "block", "runs", "into", "crucible_cm3", "hot"):
        if g(kk) is not None:
            rec[kk] = g(kk)
    prm = g("params")
    if prm is not None:
        prm = prm if isinstance(prm, list) else [prm]
        rec["params"] = [{kk: round(float(vv), 3) for kk, vv in p.items()} for p in prm[:9] if isinstance(p, dict)]
    return rec


def _best_obs(policy, v):
    """The incumbent the policy can see: the best measured utility of a fully tested alloy (None before the first)."""
    from twin.opt.policies2 import Base2
    try:
        rows = Base2.observed(policy, v)
    except Exception:
        return None
    return round(max(u for _, u in rows), 4) if rows else None


def _spend_by(ledger):
    out = {}
    for _, usd, what in ledger:
        k = what.split(" ")[0]
        out[k] = out.get(k, 0.0) + usd
    return {k: round(v, 2) for k, v in sorted(out.items(), key=lambda kv: -kv[1])}
