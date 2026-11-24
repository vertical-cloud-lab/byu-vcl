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
    },
}
AL_CHARGE_KG, CU_CHARGE_KG = 0.30, 0.80
AL_RUN_CONSUMABLES = {"argon": 0.07, "cc_plate": 1 / 5, "graphite_crucible": 1 / 12, "bn_spray": 1 / 300}
CU_RUN_CONSUMABLES = {"argon": 0.16, "cc_plate": 1.0, "bn_nozzle": 1.0, "graphite_crucible": 1 / 6,
                      "bn_spray": 1 / 300}
CHANGEOVER_H = 3.0
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


class Campaign:
    def __init__(self, spec: Spec, policy, market: supply.Market, facility: fac.Facility, horizon_h: float):
        self.spec, self.key, self.policy = spec, spec.key, policy
        self.space = spaces.SPACES[spec.key]
        self.truth = truth_al.AlTruth(spec.seed, spec.kappa) if spec.key == "flaime_al" else \
            truth_cu.CuTruth(spec.seed, spec.kappa)
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
        if spec.prestock:
            for k, q in PRESTOCK[spec.key].items():
                self.stores.orders.append(supply.Order(k, q, 0.0, -1.0, -1.0, False, spec.key))

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
    def _route(self, steps, ready_h, what, changeover=False):
        """Book steps one after another; returns (end of last step's result, money for station fees)."""
        t, usd = ready_h, 0.0
        res_t = t
        for st, hours in steps:
            if hours <= 0 and st not in ("nsl",):
                continue
            cal = self.fac.res[st].st
            # attended work on a day calendar is split into days of at most 8 h
            chunk = 8.0 if (cal.hours != "24/7" and cal.attended_h is None) else max(hours, 0.01)
            left, first = max(hours, 0.01), True
            while left > 1e-9:
                h = min(left, chunk)
                s, e, r, c = self.fac.run_step(st, t, h, self.key, what,
                                               CHANGEOVER_H if (changeover and st == "atomizer") else 0.0)
                if first:
                    usd += self.market.service_price(c, s / H)
                else:
                    usd += self.market.service_price(c - cal.fee_usd, s / H)
                first = False
                left -= h
                t, res_t = e, r
        return max(res_t, t), usd

    def _materials(self, bill, now_h):
        cost, ready_d, placed = self.stores.ensure(bill, now_h / H)
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
        if self.key == "flaime_al":
            if k == "powder":
                n = action.get("runs", 1)
                return n * (20 + 6.3 + 120 + 37.5) + 15 + (35 if action.get("icp") else 0) + 40
            if k == "print":
                return fees["utah_midi"] + 80 + 90 + 45
            if k == "test":
                return fees["edm"] + 120 + (60 if action.get("hot") else 0)
            if k == "promote":
                return fees["utah_midi"] * 1.5 + 80 + 90 + fees["edm"] + 120 + 120
        else:
            if k == "powder":
                n = action.get("runs", 1)
                return n * (60 + 14.4 + 600 + 120 + 75) + 15 + 40
            if k == "nsl":
                return fees["nsl"]
            if k in ("preplaced", "small_ded"):
                return fees["utah_mxlab"] + 40 + (60 if k == "small_ded" else 30) + 40
            if k == "large_ded":
                return fees["mines_x2"] + 150 + 60
            if k == "tensile":
                return 120
            if k == "screen":
                return 35
            if k == "immersion":
                return 30 + 140
        return 0.0

    def submit(self, action: dict, now_h: float) -> bool:
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
        t_res, usd = self._route(A["steps"], now_h, kind)
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
        did = self.design_id(a["design"])
        comp = self.designs[did]["composition"]
        proc = {v.name: a["design"][v.name] for v in spaces.ATOMIZER}
        n = int(a.get("runs", 1))
        al = self.key == "flaime_al"
        kg = AL_CHARGE_KG if al else CU_CHARGE_KG
        bill = supply.charge_bill(self.key, comp, kg * n)
        cons = AL_RUN_CONSUMABLES if al else CU_RUN_CONSUMABLES
        for k, q in cons.items():
            if k == "bn_spray" and al:
                continue
            bill[k] = bill.get(k, 0.0) + q * n
        ready = self._materials(bill, now_h)
        steps = [("shop", (2.5 if al else 1.0) * n), ("doser", 1.0 * n)]
        t = ready
        usd = 0.0
        runs = []
        TL = self.believed_liquidus(did)
        t_r, u = self._route(steps, t, "charge")
        usd += u
        t = t_r
        for i in range(n):
            t_r, u = self._route([("atomizer", 2.5)], t, "atomize", changeover=True)
            usd += u
            t = t_r
            runs.append(self.truth.atomize(comp, proc, TL, self.rng))
        steps2 = [("sieve", 0.75), ("psd", 0.25), ("byu_sem", 0.5)]
        if a.get("icp"):
            steps2.append(("byu_icpms", 0.1))
        t_r, u = self._route(steps2, t, "powder QC")
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
        lot_id = next(self.ids)
        self._lot_truth[lot_id] = dict(composition=true_comp, oxygen_ppm=ox, satellite_frac=sat, carbon_ppm=carbon,
                                       runs=runs)
        meas = dict(runs=n, failed_runs=n - len(good), cut_g=cut_g,
                    d50_um=d50 * math.exp(self.rng.normal(0, 0.05)) if good else None,
                    cut_frac=(float(np.mean([r["cut_frac"] for r in good])) + self.rng.normal(0, 0.03)) if good else None,
                    oxygen_ppm=ox * math.exp(self.rng.normal(0, 0.1)) if good else None,
                    eds={e: v * math.exp(self.rng.normal(0, 0.08)) for e, v in true_comp.items()
                         if e != self.space.balance} if good else None)
        if a.get("icp") and good:
            meas["icp"] = {e: v * math.exp(self.rng.normal(0, 0.02)) for e, v in true_comp.items()
                           if e != self.space.balance}
        self._emit(t_r, dict(type="lot", id=lot_id, design=did, measured=meas, proc=proc, into=a.get("into")))
        return True

    # ---------------------------------------------------------------------------------------- FLAIME: print, test
    def _lot(self, lot_id):
        L = self.lots.get(lot_id)
        if L is None:
            raise KeyError(lot_id)
        return L

    def _do_print(self, a, now_h):
        L = self._lot(a["lot"])
        need = 30.0                       # a 55 mm reduction kit takes about 30 g (DAL #138)
        if L["remaining_g"] < need:
            return False
        L["remaining_g"] -= need
        params = a["params"][:9]
        ready = self._materials({"build_plate": 1.0, "argon": 1.0 if self.fac.kind == "vertical_lab" else 0.0},
                                now_h)
        t_r, usd = self._route([("utah_midi", 5.0), ("density", 0.5), ("byu_sem", 1.0)], ready, "print")
        self.charge(now_h, usd, "print")
        lt = self._lot_truth[a["lot"]]
        lot = dict(lt, composition=lt["composition"])
        bid = next(self.ids)
        parts, meas = [], []
        for p in params:
            part = self.truth.build(lot, p, self.rng)
            parts.append(part)
            cd = part["crack_density"] * math.exp(self.rng.normal(0, 0.2))
            meas.append(dict(rel_density=float(np.clip(part["rel_density"] + self.rng.normal(0, 0.002), 0, 1)),
                             crack_density=cd if cd > 0.02 else 0.0, params=p))
        self._part_truth[bid] = dict(parts=parts, lot=a["lot"], bars_at=int(a.get("bars_at", 0)))
        self._emit(t_r, dict(type="build", id=bid, lot=a["lot"], design=L["design"], measured=meas,
                             bars_at=int(a.get("bars_at", 0))))
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
        t_r, usd = self._route(steps, now_h, "test")
        self.charge(now_h, usd + 120.0, "test (3 specimens machined)")
        pt = self._part_truth[a["build"]]
        part = pt["parts"][pt["bars_at"]]
        s = self.truth.strength(part)
        hot = self.truth.strength(part, 250.0) if a.get("hot") else None
        meas = dict(ys_MPa=s["ys_MPa"] * math.exp(self.rng.normal(0, 0.04 / math.sqrt(3))),
                    uts_MPa=s["uts_MPa"] * math.exp(self.rng.normal(0, 0.03 / math.sqrt(3))),
                    el_pct=s["el_pct"] * math.exp(self.rng.normal(0, 0.12 / math.sqrt(3))))
        if hot:
            meas["hot_ys_MPa"] = hot["ys_MPa"] * math.exp(self.rng.normal(0, 0.05 / math.sqrt(3)))
        u, det = self._al_score(part, s, hot)
        self._emit(t_r, dict(type="test", build=a["build"], design=B["design"], measured=meas,
                             params=B["measured"][pt["bars_at"]]["params"], score=(u, det)))
        return True

    def _do_promote(self, a, now_h):
        L = self._lot(a["lot"])
        if L["remaining_g"] < 440.0:
            return False
        L["remaining_g"] -= 440.0
        ready = self._materials({"build_plate": 1.0, "argon": 1.0}, now_h)
        t_r, usd = self._route([("utah_midi", 8.0), ("edm", 1.0), ("furnace", 3.0), ("shop", 1.5),
                                ("tensile", 0.6), ("tensile_hot", 1.5)], ready, "promote")
        self.charge(now_h, usd + self.fac.res["utah_midi"].st.fee_usd * 0.5 + 120.0, "promote (E8 plate)")
        lot = self._lot_truth[a["lot"]]
        part = self.truth.build(lot, a["params"], self.rng)
        s = self.truth.strength(part)
        hot = self.truth.strength(part, 250.0)
        meas = dict(ys_MPa=s["ys_MPa"] * math.exp(self.rng.normal(0, 0.03 / math.sqrt(3))),
                    el_pct=s["el_pct"] * math.exp(self.rng.normal(0, 0.10 / math.sqrt(3))),
                    hot_ys_MPa=hot["ys_MPa"] * math.exp(self.rng.normal(0, 0.04)),
                    rel_density=float(np.clip(part["rel_density"] + self.rng.normal(0, 0.002), 0, 1)))
        u, det = self._al_score(part, s, hot)
        det["e8"] = True
        self._emit(t_r, dict(type="test", build=None, design=L["design"], measured=meas, params=a["params"],
                             score=(u, det), e8=True))
        return True

    # ---------------------------------------------------------------------------------------- ONR: DED and tests
    def _do_nsl(self, a, now_h):
        L = self._lot(a["lot"])
        t_r, usd = self._route([("nsl", 0.01)], now_h, "nsl")
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

    def _do_large_ded(self, a, now_h):
        L = self._lot(a["lot"])
        if not L.get("nsl"):
            return False
        return self._ded(a, now_h, "blown_large", 2000.0, [("mines_x2", 5.0), ("byu_sem", 2.0)], 1.0)

    def _ded(self, a, now_h, mode, grams, steps, substrates):
        L = self._lot(a["lot"])
        if L["remaining_g"] < grams:
            return False
        L["remaining_g"] -= grams
        ready = self._materials({"ded_substrate": substrates} if substrates else {}, now_h)
        t_r, usd = self._route(steps, ready, mode)
        self.charge(now_h, usd, mode)
        lot = self._lot_truth[a["lot"]]
        params = a["params"] if isinstance(a["params"], list) else [a["params"]]
        params = params[:(4 if mode != "blown_large" else 1)]
        did = L["design"]
        nab = {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}
        parts, meas = [], []
        for p in params:
            part = self.truth.deposit(lot, p, mode, self.rng, substrate=nab if mode != "blown_small" else None)
            parts.append(part)
            cd = part["crack_density"] * math.exp(self.rng.normal(0, 0.25))
            m = dict(rel_density=float(np.clip(part["rel_density"] + self.rng.normal(0, 0.003), 0, 1)),
                     crack_density=cd if cd > 0.02 else 0.0,
                     dilution=part["dilution"] * math.exp(self.rng.normal(0, 0.1)), params=p)
            if mode != "preplaced":
                m.update(beta_prime=float(np.clip(part["beta_prime"] + self.rng.normal(0, 0.03), 0, 1)),
                         catchment=part["catchment"] * math.exp(self.rng.normal(0, 0.05)),
                         grain_um=part["grain_um"] * math.exp(self.rng.normal(0, 0.1)))
            if part["fusion_ok"] is not None:
                m["fusion_ok"] = part["fusion_ok"] if self.rng.random() > 0.05 else (not part["fusion_ok"])
            meas.append(m)
        dep = next(self.ids)
        self._part_truth[dep] = dict(parts=parts, lot=a["lot"], mode=mode)
        self._emit(t_r, dict(type="deposit", id=dep, lot=a["lot"], design=did, mode=mode, measured=meas))
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
        t_r, usd = self._route([("shop", 1.0), ("tensile", 0.6)], now_h, "tensile")
        self.charge(now_h, usd + 120.0, "tensile (3 specimens machined)")
        s = self.truth.strength(part)
        meas = dict(ys_MPa=s["ys_MPa"] * math.exp(self.rng.normal(0, 0.04 / math.sqrt(3))),
                    el_pct=s["el_pct"] * math.exp(self.rng.normal(0, 0.12 / math.sqrt(3))),
                    uts_MPa=s["uts_MPa"] * math.exp(self.rng.normal(0, 0.03 / math.sqrt(3))))
        self._emit(t_r, dict(type="cu_test", what="tensile", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _do_screen(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if D["mode"] == "preplaced":
            return False
        t_r, usd = self._route([("cubxl", 1.2), ("byu_icpms", 0.1)], now_h, "screen")
        self.charge(now_h, usd, "corrosion screen")
        c = self.truth.corrosion(part)
        meas = dict(early_rate_um_yr=c["early_rate_um_yr"] * math.exp(self.rng.normal(0, 0.3)),
                    Eb_mV=c["Eb_mV"] + self.rng.normal(0, 30))
        self._emit(t_r, dict(type="cu_test", what="screen", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    def _do_immersion(self, a, now_h):
        D, part = self._dep(a["deposit"])
        if D["mode"] != "blown_large" or "immersion" in D:
            return False
        D["immersion"] = "pending"
        t_r, usd = self._route([("immersion", 720.0), ("byu_sem", 1.0), ("byu_icpms", 0.4)], now_h, "immersion")
        self.charge(now_h, usd + 105.0, "immersion (4 ICP-MS draws)")
        c = self.truth.corrosion(part)
        r30 = c["rate_um_yr"] * (1 + 1.5 * math.exp(-30 / c["film_days"]))
        meas = dict(rate30_um_yr=r30 * math.exp(self.rng.normal(0, 0.12)),
                    attack_um=max(c["attack_um"] * math.exp(self.rng.normal(0, 0.25)) + self.rng.normal(0, 0.5), 0.0))
        self._emit(t_r, dict(type="cu_test", what="immersion", deposit=a["deposit"], design=D["design"],
                             measured=meas))
        return True

    # ---------------------------------------------------------------------------------------- results come back
    def release(self, t_h, p):
        self.inflight -= 1
        typ = p["type"]
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
                                          proc=p["proc"], t=t_h)
        elif typ == "nsl":
            self.lots[p["lot"]]["nsl"] = p["measured"]
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
        return dict(key=self.key, now_h=now_h, budget_left=self.budget_left, spent=self.spent, space=self.space,
                    designs={i: d["composition"] for i, d in self.designs.items()},
                    design_inputs={i: d["design"] for i, d in self.designs.items()},
                    sims=self.sims, lots=self.lots, builds=self.builds, tests=self.tests, deposits=self.deposits,
                    corr=self.corr, inflight=self.inflight, wip=self.spec.wip, estimate=self.estimate)


class Twin:
    """Both campaigns on one clock. ``policies``: {campaign key: policy}; ``specs``: {campaign key: Spec}."""

    def __init__(self, specs: dict, policies: dict, scenario="historical", facility="proposed", seed=0,
                 horizon_days=365, isolated=False):
        self.h = horizon_days * H
        self.market = supply.Market(scenario, seed, int(horizon_days) + 400)
        shared = fac.Facility(facility, seed, self.h + 2000 * H)
        self.campaigns = {}
        for k, sp in specs.items():
            f = fac.Facility(facility, seed, self.h + 2000 * H) if isolated else shared
            self.campaigns[k] = Campaign(sp, policies[k], self.market, f, self.h)
        self.facilities = {k: c.fac for k, c in self.campaigns.items()}
        self.seq = itertools.count()

    def run(self, verbose=False):
        """The event loop. A campaign is asked for actions whenever one of its results comes back, and once a day
        while it has nothing in flight (so it can start, and restart after waiting on materials)."""
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
                acts = c.policy.propose(c.view(t), free) or []
                for a in acts[:free]:
                    c.submit(a, t)
                for tr, pay in c.events_out:
                    heapq.heappush(q, (tr, next(self.seq), k, pay))
                c.events_out = []
            if c.inflight == 0 and c.budget_left > 0 and tick[k] <= t and t + H <= self.h:
                tick[k] = t + H
                heapq.heappush(q, (t + H, next(self.seq), k, None))
        return self.summary()

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
                          spend_by=_spend_by(c.ledger), demonstrated=c.demonstrated)
        out["utilization"] = {k: f.utilization(self.h) for k, f in
                              ({"shared": next(iter(self.facilities.values()))}.items())}
        out["market_events"] = self.market.events
        return out


def _spend_by(ledger):
    out = {}
    for _, usd, what in ledger:
        k = what.split(" ")[0]
        out[k] = out.get(k, 0.0) + usd
    return {k: round(v, 2) for k, v in sorted(out.items(), key=lambda kv: -kv[1])}
