"""Round 3: BOFN and pKGFN on every node of every part, on the asynchronous engine (``Twin(mode="async")``).

Round 2's BOFN (``policies2.BOFN``, ``BOFNBlend``) chose new designs by network expected improvement (EI) per dollar,
ran the cheap nodes (PIP, section, screen) on every sound part at once, and decided the dear steps (bars, a 1 kg
deposit) by EI per dollar, all under a cap on work in flight. Round 3 keeps its network (the same nodes, inputs and
data) and changes how it decides:

* **Every node of every part competes.** Each decision ranks a new design, a print or deposit from powder already
  made (including another print at new settings when a lot's first parts were unsound), PIP and section or screen on
  a sound part, bars, a 1 kg deposit, tensile, immersion, and stopping a coupon in immersion, against each other.
  The engine admits them in that order as stations, fixtures and the spending plan allow.
* **Pending evaluations** (kriging believer): a part whose final result is in flight counts at its posterior mean
  utility in the incumbent, and a new design is not proposed within 0.08 (composition features) of a design already
  started or in the list.
* **Interim immersion readings** (copper): a node ``imm_cond`` maps a coupon's interim mass-loss rate at day d (and
  d, and the immersion node's inputs) to its 30-day rate. After each reading the coupon is stopped if continuing
  can't pay (EI or KG of finishing below 1e-4).
* **Two acquisitions.** ``acq='ei'`` (BOFN): EI of the part's utility over the incumbent, per cost of the remaining
  path to a demonstrated alloy (DAL's pKGFN fallback, ``bofn-cu-ded/policies.py``). ``acq='kg'`` (pKGFN, Buathong
  et al. 2024; DAL's ``partial_kgfn`` port): the knowledge gradient of the next node (or bundle: powder + print, PIP +
  section, PIP + screen, the full chain for a 1 kg deposit), per cost of that node: Monte Carlo fantasies of the
  node's outputs (F = 8), each propagated through the rest of the network with common random numbers (S = 32), the
  value E[max(mu_part(y), c)] - max(mu_part, c), with c the best alternative's posterior mean or the incumbent. The
  learning effect of a fantasy on other parts' posteriors (through the node GP's covariance) is left out: an
  independent-alternatives approximation of the inner max. When every KG is flat, EI per cost to completion decides.
* **Two denominators.** ``denom='usd'``: dollars (round 2's rule). ``denom='time'``: bottleneck-hours, the station-
  hours the step occupies weighted by each station's current load (the share of its next 72 h booked; floor 0.05),
  plus 0.001 h per dollar so money still breaks ties. Money is a constraint in both, through the engine's plan.
"""
from __future__ import annotations

import math

import numpy as np

from twin import policies as P1
from twin.opt import policies2 as P2
from twin.opt.gp import Node
from twin.opt.policies2 import _ann, _feat_comp, al_u, cu_u, logit, sigm

# station-hours of each step, from the routes in twin/campaign.py
PATHS = {
    "flaime_al": {
        "powder": {"shop": 5.0, "doser": 2.0, "atomizer": 5.0, "sieve": 0.75, "psd": 0.25, "byu_sem": 0.5},
        "print": {"utah_midi": 5.0, "density": 0.5, "byu_sem": 1.0},
        "pipsec": {"furnace": 3.0, "prep": 2.0, "pip": 0.5, "byu_sem": 1.0, "hardness": 0.25},
        "test": {"edm": 0.75, "furnace": 3.0, "shop": 1.0, "tensile": 0.6},
    },
    "onr_cu": {
        "blend": {"doser": 0.5, "utah_mxlab": 3.0, "byu_sem": 1.0},
        "powder": {"shop": 3.0, "doser": 3.0, "atomizer": 7.5, "sieve": 0.75, "psd": 0.25, "byu_sem": 0.5},
        "small": {"utah_mxlab": 4.0, "byu_sem": 2.0},
        "pipscreen": {"prep": 0.5, "pip": 0.5, "cubxl": 1.2, "byu_icpms": 0.1},
        "large": {"utah_mxlab": 8.0, "byu_sem": 1.0},
        "large_conv": {"mines_x2": 5.0, "byu_sem": 2.0},
        "tensile": {"shop": 1.0, "tensile": 0.6},
        "immersion": {"immersion": 720.0, "byu_sem": 1.0, "byu_icpms": 0.4},
    },
}
TO_DONE = {   # the remaining path to a demonstrated alloy from each stage
    "flaime_al": {"new": ("powder", "print", "pipsec", "test"), "lot": ("print", "pipsec", "test"),
                  "build": ("pipsec", "test"), "pipsec": ("test",)},
    "onr_cu": {"new": ("blend", "pipscreen", "powder", "large", "tensile", "immersion"),
               "dep_small": ("pipscreen", "powder", "large", "tensile", "immersion"),
               "screened": ("powder", "large", "tensile", "immersion"),
               "large": ("tensile", "immersion")},
}


class Net3(P2.BOFNBlend):
    name = "bofn3"
    acq = "ei"
    denom = "time"
    S = 24
    F = 8
    EPS_USD = 1e-3
    PI_FLOOR = 0.05
    RECOMPUTE_H = 6.0             # new designs' scores
    RECOMPUTE_DOWN_H = 4.0        # parts' scores, unless a new part or final result came back
    GROWTH = 1.4
    SCREEN_SHARE, SCREEN_START = 0.25, 2500.0
    MIN_NEW_EI = 1e-4             # a new design must be worth at least this much expected improvement (utility units)
    K_KG = 8                      # pKGFN: KG for the top K of each stage by EI per cost to completion (DAL: 16)
    D_TAKEN, D_BATCH = 0.03, 0.08 # composition-feature distance to designs started / to the list being made
    STOP_V = 1e-4
    N_NEW_KG = 12

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        if not self.al:
            self.nodes["imm_cond"] = [Node("gp", 4, seed=seed)]
        # round 3 makes data several times faster than round 2: hyperparameters are refit when a node's data have
        # grown by its refit_every and by a quarter (in between, the GP is rebuilt on the new data with the last
        # hyperparameters, as in round 2), and the large nodes keep at most 300 rows (the newest half and a random half)
        for nodes in self.nodes.values():
            for nd in nodes:
                nd.growth = self.GROWTH
                nd.max_n = min(nd.max_n, 300)
        self._seed_q = None
        self._n_adm = 0
        self._cache_key, self._down, self._down_t = None, [], -1e9
        self._n_eligible = 0
        self._new, self._new_t = [], -1e9
        self._best_kb, self._mus = 0.0, []
        self.go_large_lots = set()
        self._imm_checked = {}
        self.fant = np.random.default_rng(seed * 31 + (7 if self.al else 9))
        self.counts = dict(calls=0, recompute=0, new_recompute=0, kg_flat=0, stops=0)

    # ------------------------------------------------------------------------------------------ data
    def _best_block(self, Dd):
        if Dd.get("_best_block") is None:
            gate = 0.96 if Dd["mode"] == "blend" else 0.98
            ok = [(i, m) for i, m in enumerate(Dd["measured"]) if m["rel_density"] >= gate and m["crack_density"] < 0.3]
            if not ok:
                return None
            i, m = max(ok, key=lambda im: im[1]["rel_density"] - im[1].get("beta_prime", 0) * 0.05
                       - (1 if im[1]["crack_density"] > 0.05 else 0))
            Dd["_best_block"], Dd["_best_params"] = i, m["params"]
        return Dd["_best_block"]

    def _small_recs(self, v):
        """Per design: its screened small (atomized, fl 0) or blend (fl 1) deposit's outputs, atomized first."""
        out = {}
        for did_, Dd in v["deposits"].items():
            if Dd["mode"] not in ("blown_small", "blend"):
                continue
            if not (isinstance(Dd.get("pip"), dict) and isinstance(Dd.get("screen"), dict)):
                continue
            bb = self._best_block(Dd)
            if bb is None:
                continue
            fl = 1.0 if Dd["mode"] == "blend" else 0.0
            blk = Dd["measured"][bb]
            pm, sm = Dd["pip"], Dd["screen"]
            rec = dict(do=[float(logit(blk["rel_density"])), math.log10(blk["crack_density"] + 0.01),
                           blk.get("beta_prime", 0.0)],
                       pip=[pm["ys_MPa"] / 400, pm["uts_MPa"] / 600, pm["ue_pct"] / 30],
                       screen=[math.log(max(sm["early_rate_um_yr"], 0.05)), sm.get("Eb_mV", 0.0) / 500], fl=fl,
                       dep=did_, params=Dd["measured"][bb]["params"])
            cur = out.get(Dd["design"])
            if cur is None or cur["fl"] > fl:
                out[Dd["design"]] = rec
        return out

    def _imm_base(self, comp, rec):
        return [rec["screen"][0], rec["screen"][1], rec["do"][2], comp.get("Ni", 0) / 30, comp.get("Fe", 0) / 4.5,
                comp.get("Al", 0) / 9.5, rec["fl"]]

    @staticmethod
    def _dflag(d):
        return math.log1p(d) / math.log(15.0)

    def datasets(self, v):
        D = super().datasets(v)
        if self.al:
            return D
        recs = self._small_recs(v)
        for Dd in v["deposits"].values():
            if Dd["mode"] != "blown_large" or not isinstance(Dd.get("immersion"), dict):
                continue
            rec = recs.get(Dd["design"])
            itm = Dd.get("imm_interim") or {}
            if rec is None or not itm:
                continue
            base = self._imm_base(v["designs"][Dd["design"]], rec)
            y = math.log(max(Dd["immersion"]["rate30_um_yr"], 0.05))
            for d, m in itm.items():
                D["imm_cond"][0].append(np.array([math.log(max(m["rate_um_yr"], 0.05)), self._dflag(d)] + base))
                D["imm_cond"][1][0].append(y)
        return D

    def utility_samples_al(self, comps, X_print, S, fixed_print=None, fixed_pip=None, fixed_section=None):
        if fixed_print is None and not self.ready("print"):
            return None
        return super().utility_samples_al(comps, X_print, S, fixed_print, fixed_pip, fixed_section)

    # ------------------------------------------------------------------------------------------ copper utility
    def _ucu(self, comps, S, X_ded=None, fd=None, fp=None, fs=None, fid=0.0, ft=None, fi=None, interim=None):
        """Utility draws (S, M) through copper's network with any of: DED outputs (fd), PIP (fp), screen (fs),
        tensile (ft: ys/400, log EL) or the 30-day rate (fi: log rate) fixed, and an interim reading (interim: log
        rate, day flag) conditioning the 30-day rate."""
        M = len(comps)
        fl = np.asarray(fid, float)
        FL = np.broadcast_to(fl.reshape(1, -1, 1) if fl.ndim else fl, (S, M, 1))
        compf = np.array([_feat_comp(self.space, c) for c in comps])
        ni = np.array([c.get("Ni", 0.0) for c in comps])
        B = lambda a, i: np.broadcast_to(a[:, i], (S, M))
        if fd is None:
            if X_ded is None or not self.ready("ded"):
                return None
            d1, d2, d3 = self._samp("ded", X_ded, S)
        else:
            d1, d2, d3 = (B(fd, i) for i in range(3))
        dens, crack = sigm(d1), 10 ** d2 - 0.01
        Xn = np.concatenate([np.broadcast_to(compf, (S, M, compf.shape[1])), d1[..., None], d2[..., None],
                             d3[..., None], FL], axis=2)
        if fp is None:
            if not self.ready("pip"):
                return None
            p1, p2, p3 = self._samp("pip", Xn, S)
        else:
            p1, p2, p3 = (B(fp, i) for i in range(3))
        if fs is None:
            if not self.ready("screen"):
                return None
            s1, s2 = self._samp("screen", Xn, S)
        else:
            s1, s2 = (B(fs, i) for i in range(2))
        if ft is not None:
            ys, el = B(ft, 0) * 400, np.exp(B(ft, 1))
        elif self.ready("tensile"):
            t1, t2 = self._samp("tensile", np.concatenate([np.stack([p1, p2, p3, d1, d2, d3], axis=2), FL], axis=2), S)
            ys, el = t1 * 400, np.exp(t2)
        else:
            # before tensile data, the PIP curve read as the test, with the spread a PIP-to-tensile link has (yield
            # about 12 %, elongation from uniform elongation a factor of about 1.4): a proxy is not a measurement
            ys = p1 * 400 * np.exp(self.gen.normal(0, 0.12, (S, M)))
            el = np.maximum(p3 * 30 * 1.2, 0.3) * np.exp(self.gen.normal(0, 0.35, (S, M)))
        if fi is not None:
            rate = np.exp(B(fi, 0))
        else:
            fe = np.broadcast_to(np.array([c.get("Fe", 0.0) / 4.5 for c in comps]), (S, M))
            al = np.broadcast_to(np.array([c.get("Al", 0.0) / 9.5 for c in comps]), (S, M))
            base = np.concatenate([np.stack([s1, s2, d3, np.broadcast_to(ni / 30, (S, M)), fe, al], axis=2), FL],
                                  axis=2)
            if interim is not None and self.ready("imm_cond"):
                Xc = np.concatenate([B(interim, 0)[..., None], B(interim, 1)[..., None], base], axis=2)
                (i1,) = self._samp("imm_cond", Xc, S)
                rate = np.exp(i1)
            elif self.ready("immersion"):
                i1, _ = self._samp("immersion", base, S)
                rate = np.exp(i1)
            else:
                # before immersion data: the film takes the early rate down (prior factor 0.6), give or take a factor
                # of 1.6; a blend's screen reads its inhomogeneity too, which the atomized alloy won't have (prior: a
                # fifth lower, give or take 35 %)
                blend = np.broadcast_to(FL[..., 0], (S, M))
                rate = np.exp(s1) * 0.6 * np.exp(self.gen.normal(0, 0.5, (S, M))) * \
                    np.exp(blend * self.gen.normal(-0.2, 0.35, (S, M)))
        return cu_u(ys, el, rate, ni[None, :], dens, crack)

    # ------------------------------------------------------------------------------------------ costs
    def _pi(self, v):
        now = v["now_h"]
        st = {s for segs in PATHS[self.key].values() for s in segs}
        return {s: max(v["load"](s, now, 720.0 if s == "immersion" else 72.0), self.PI_FLOOR) for s in st}

    def _seg_usd(self, v, seg, design=None, runs=None):
        est = v["estimate"]
        if self.al:
            if seg == "powder":
                return est(self.powder_action(design, v=v)) if design else 900.0
            return {"print": est(dict(kind="print")), "pipsec": est(dict(kind="pip")) + est(dict(kind="section")),
                    "test": est(dict(kind="test"))}[seg]
        if seg == "powder":
            return est(self.powder_action(design, runs=runs or 3, v=v)) if design else 1800.0
        return {"blend": est(dict(kind="blend_ded")), "small": est(dict(kind="small_ded")),
                "pipscreen": est(dict(kind="pip")) + est(dict(kind="screen")), "large": est(dict(kind="large_ded")),
                "tensile": est(dict(kind="tensile")), "immersion": est(dict(kind="immersion"))}[seg]

    def _seg_bh(self, v, seg, pi):
        if seg == "large" and not v.get("vertical"):
            seg = "large_conv"
        return sum(h * pi.get(s, self.PI_FLOOR) for s, h in PATHS[self.key][seg].items())

    def _denom(self, v, segs, pi, design=None, runs=None, extra_usd=0.0, extra_bh=0.0):
        usd = sum(self._seg_usd(v, s, design if s == "powder" else None, runs) for s in segs) + extra_usd
        bh = sum(self._seg_bh(v, s, pi) for s in segs) + extra_bh
        d = usd if self.denom == "usd" else bh + self.EPS_USD * usd
        return max(d, 1e-6), usd, bh

    # ------------------------------------------------------------------------------------------ values
    def _ei(self, u, best):
        """EI from the utility draws' mean and spread (the normal form), so a part with a small chance is not
        rounded to zero by 24 draws; equal to the draws' own EI when they are normal."""
        if u is None:
            return None
        u = np.asarray(u, float).reshape(-1)
        m, sd = float(u.mean()), float(u.std())
        if sd < 1e-9:
            return max(m - best, 0.0)
        from scipy.stats import norm
        z = (m - best) / sd
        return float((m - best) * norm.cdf(z) + sd * norm.pdf(z))

    def _kg_from(self, mu_f, mu0, c):
        return float(np.mean(np.maximum(mu_f, c)) - max(mu0, c))

    def _fant(self, node, X):
        """F fantasy draws of a node's outputs at one input X (d,): (F, n_outputs)."""
        z = self.fant.standard_normal((self.F, len(self.nodes[node])))
        out = []
        for j, nd in enumerate(self.nodes[node]):
            m, s = nd.predict(np.asarray(X, float)[None, :])
            out.append(m[0] + s[0] * z[:, j])
        return np.stack(out, axis=1)

    # ------------------------------------------------------------------------------------------ proposing
    def admitted(self, a):
        self._n_adm += 1
        a["_taken"] = True
        if self._seed_q:
            self._seed_q = [s for s in self._seed_q if s is not a]
        did = a.get("_did")
        if a.get("kind") in ("powder", "blend_ded") and did is not None and not a.get("into"):
            self.started.add(did)
        if a.get("_promote") is not None:
            self.blend_state[a["_promote"]] = "promoted"
        if a.get("_go_large") is not None:
            self.go_large_lots.add(a["_go_large"])
        if a.get("kind") == "stop":
            self.counts["stops"] += 1

    def rejected(self, a, why):
        pass

    def _pend(self, v):
        P = {}
        for p in v["pending"]:
            k = p.get("key")
            if k is not None:
                P.setdefault(tuple(k), set()).add(p["kind"])
        return P

    def propose(self, v, n):
        self.counts["calls"] += 1
        if self._seed_q is None:
            self.seeds = self.reference_seeds()
            self._seed_q = [_ann(self.powder_action(d, v=v), self.seed_label()) for d in self.seeds]
            sims = [_ann(dict(kind=self.sim_kind, design=d), "seed: open-CALPHAD node for each seed") for d in self.seeds]
            return sims + list(self._seed_q)
        P = self._pend(v)
        out = list(self._seed_q)
        out += self._sim_requests(v, P)
        arts = (len(v["lots"]), len(v["builds"]), len(v["deposits"]), len(v["tests"]),
                sum(1 for D in v["deposits"].values() if isinstance(D.get("immersion"), dict)))
        key = arts + (len(v["sims"]), len(v["corr"]))
        now = v["now_h"]
        # recompute when a new part or a final result came back, or every RECOMPUTE_DOWN_H while anything changed
        if arts != getattr(self, "_arts", None) or (key != self._cache_key and now - self._down_t >= self.RECOMPUTE_DOWN_H):
            self._arts, self._cache_key, self._down_t = arts, key, now
            self.counts["recompute"] += 1
            self._down = self._candidates(v, P)
        elif now - self._new_t >= 1.0 and self.can_start_new(v) and not any(
                c.get("did") is not None and not all(a.get("_taken") for a in c["acts"]) for c in self._down):
            self._refresh_new(v, P)
        return out + [a for c in self._down for a in c["acts"] if not a.get("_taken")]

    def _sim_requests(self, v, P):
        simmed = {s["design"] for s in v["sims"] if s["kind"] == self.sim_kind}
        used = {L["design"] for L in v["lots"].values()} | {D["design"] for D in v["deposits"].values()}
        free = [d for d in simmed if d not in self.started and d not in used]
        if (len(free) >= 48 and self._n_eligible >= 24) or any(p["kind"] == self.sim_kind for p in v["pending"]) \
                or not self.can_start_new(v):
            return []
        return [_ann(dict(kind=self.sim_kind, design=d), "keep the simulated pool topped up (open CALPHAD, $1)")
                for d in self.pool(v, 48, 48)[:64]]

    def _candidates(self, v, P):
        self.fit(v)
        best = self.best_obs(v)
        pi = self._pi(v) if self.denom == "time" else {}
        C = self._cands_al(v, P, pi, best) if self.al else self._cands_cu(v, P, pi, best)
        # the kriging believer on the incumbent: parts whose final result is in flight count at their posterior mean
        best_kb = max([best] + [c["mu"] for c in C if c.get("final_pending") and c.get("mu") is not None])
        now = v["now_h"]
        if now - self._new_t >= self.RECOMPUTE_H or not self._new:
            self._new = self._cands_new(v, P, pi, best_kb)
            self._new_t = now
            self.counts["new_recompute"] += 1
        else:
            done = self.started | {L["design"] for L in v["lots"].values()} | {D["design"] for D in v["deposits"].values()}
            self._new = [c for c in self._new if c["did"] not in done]
        C = [c for c in C if not c.get("final_pending")] + self._new
        self._best_kb = best_kb
        self._mus = sorted([c["mu"] for c in C if c.get("mu") is not None], reverse=True)
        self._score(C, best_kb)
        return self._rank(C)

    def _score(self, C, best_kb):
        mus = self._mus
        for c in C:
            if c.get("u") is None:
                c["value"] = None
                continue
            if self.acq == "ei" or c.get("kg") is None:
                c["value"] = self._ei(c["u"], best_kb)
            else:
                others = [m for m in mus if m != c["mu"]] or [0.0]
                c["value"] = c["kg"](max(best_kb, others[0]))
        if self.acq == "kg":
            vals = [c["value"] for c in C if c.get("value") is not None and c.get("kind") != "stop"]
            if vals and max(vals) < 1e-7:
                self.counts["kg_flat"] += 1
                for c in C:
                    if c.get("u") is not None:
                        c["value"] = self._ei(c["u"], best_kb)
                        c["den"] = c.get("den_done", c["den"])

    def _rank(self, C):
        stops, always, learn, scored, prior = [], [], [], [], []
        for c in C:
            if c.get("kind") == "stop":
                stops.append(c)
            elif c.get("always"):
                always.append(c)
            elif c.get("prior") is not None:
                prior.append(c)
            elif c.get("value") is None:
                learn.append(c)
            else:
                c["score"] = c["value"] / c["den"]
                if c["score"] > 0:
                    scored.append(c)
        scored.sort(key=lambda c: -c["score"])
        why = ("KG" if self.acq == "kg" else "EI") + (" per bottleneck-hour" if self.denom == "time" else " per $")
        for c in scored:
            for a in c["acts"]:
                _ann(a, why + f" ({c['what']})", c["score"], cost=c.get("usd"))
        for c in learn:
            for a in c["acts"]:
                _ann(a, f"fixed: the network can't value this yet ({c['what']})", None)
        for c in always:
            for a in c["acts"]:
                a.setdefault("_acq_kind", f"always: {c['what']}")
        prior.sort(key=lambda c: -c["prior"])
        for c in prior:
            for a in c["acts"]:
                _ann(a, "prior: the funnel's proxy and screen (network not ready)", c["prior"] * 1e-9)
        return stops + always + learn + scored + prior

    def _refresh_new(self, v, P):
        """New designs only (the parts' scores are kept), when the list has none left to offer."""
        pi = self._pi(v) if self.denom == "time" else {}
        self._new = self._cands_new(v, P, pi, self._best_kb)
        self._new_t = v["now_h"]
        self.counts["new_recompute"] += 1
        self._score(self._new, self._best_kb)
        keep = [c for c in self._down if c.get("did") is None and not all(a.get("_taken") for a in c["acts"] or [{}])]
        self._down = self._rank(keep + self._new)

    # ------------------------------------------------------------------------------------------ aluminium
    def _sound_al(self, B):
        m = B["measured"][B["bars_at"]]
        return m["rel_density"] >= 0.98 and m["crack_density"] < 0.3

    def _xprint(self, v, did, params, lot=None):
        return np.concatenate([_feat_comp(self.space, v["designs"][did]), self.sim_of(v, did),
                               self.proc_vec(dict(v["design_inputs"][did], **params)), self.powder_feat(v, lot)])

    def _top_kg(self, C, stage, best, make):
        """pKGFN: knowledge gradients for the K_KG candidates of a stage with the most EI per cost to completion
        (DAL's pKGFN scores 16 per stage, chosen by network EI); the rest of the stage gets none (not proposed)."""
        cs = [c for c in C if c.get("stage") == stage and c.get("u") is not None]
        cs.sort(key=lambda c: -(self._ei(c["u"], best) + 1e-9 * c["mu"]) / c["den_done"])
        for c in cs[:self.K_KG]:
            c["kg"] = make(c)
        for c in cs[self.K_KG:]:
            c["kg"] = (lambda cc: 0.0)

    def _cands_al(self, v, P, pi, best):
        C = []
        tested = {t["build"] for t in v["tests"] if t["build"]}
        kg = self.acq == "kg"
        prs = []
        for lid, L in v["lots"].items():
            if L.get("gas") or L["remaining_g"] < 30 or "print" in P.get(("lot", lid), set()):
                continue
            bl = [B for B in v["builds"].values() if B["lot"] == lid]
            if bl and (any(self._sound_al(B) for B in bl) or len(bl) >= 3):
                continue
            if self.sim_of(v, L["design"]) is None:
                continue
            prs.append((lid, L, self.print_action(v, lid), bl))
        if prs:
            comps = [v["designs"][L["design"]] for _, L, _, _ in prs]
            X = np.array([self._xprint(v, L["design"], act["params"][0], lid) for lid, L, act, _ in prs])
            U = self.utility_samples_al(comps, X, self.S)
            dd = self._denom(v, TO_DONE[self.key]["lot"], pi)
            dn = self._denom(v, ("print",), pi) if kg else dd
            for j, (lid, L, act, bl) in enumerate(prs):
                u = U[:, j:j + 1] if U is not None else None
                C.append(dict(stage="print", what="print from powder already made" if not bl else
                              "another print at new settings", acts=[act], u=u,
                              mu=float(u.mean()) if u is not None else None, comp=comps[j], x=X[j], den_done=dd[0],
                              den=dn[0], usd=dn[1], always=not bl))
        ps, ts = [], []
        for bid, B in v["builds"].items():
            if not self._sound_al(B) or B.get("tested") or bid in tested:
                continue
            pk = P.get(("build", bid), set())
            comp = v["designs"][B["design"]]
            mb = B["measured"][B["bars_at"]]
            fp = [float(logit(mb["rel_density"])), math.log10(mb["crack_density"] + 0.01)]
            has_pip, so = isinstance(B.get("pip"), dict), self.section_out(B)
            if not has_pip or so is None:
                if pk & {"pip", "section"}:
                    continue
                acts = ([] if so is not None else [dict(kind="section", build=bid, cube=B["bars_at"])]) + \
                       ([] if has_pip else [dict(kind="pip", build=bid, cube=B["bars_at"])])
                ps.append((comp, fp, acts))
                continue
            pm = B["pip"]
            ts.append((comp, fp, [pm["ys_MPa"] / 400, pm["uts_MPa"] / 500, pm["ue_pct"] / 20], so, bid,
                       "test" in pk))
        if ps:
            comps = [c for c, _, _ in ps]
            FP = np.array([f for _, f, _ in ps])
            U = self.utility_samples_al(comps, None, self.S, fixed_print=FP)
            dd = self._denom(v, TO_DONE[self.key]["build"], pi)
            dn = self._denom(v, ("pipsec",), pi) if kg else dd
            for j, (comp, fp, acts) in enumerate(ps):
                u = U[:, j:j + 1] if U is not None else None
                C.append(dict(stage="pipsec", what="PIP and section of a sound build", acts=acts, u=u,
                              mu=float(u.mean()) if u is not None else None, comp=comp, fp=np.array([fp]),
                              den_done=dd[0], den=dn[0], usd=dn[1]))
        if ts:
            comps = [t[0] for t in ts]
            U = self.utility_samples_al(comps, None, self.S, fixed_print=np.array([t[1] for t in ts]),
                                        fixed_pip=np.array([t[2] for t in ts]), fixed_section=np.array([t[3] for t in ts]))
            dd = self._denom(v, ("test",), pi)
            learn = U is None or self._fitted_at.get("test", 0) < 6
            for j, (comp, fp, fpip, so, bid, pend) in enumerate(ts):
                u = U[:, j:j + 1] if U is not None else None
                c = dict(stage="test", what="bars of a PIP'd build", acts=[dict(kind="test", build=bid)],
                         u=None if (learn and not pend) else u, mu=float(u.mean()) if u is not None else None,
                         comp=comp, fp=np.array([fp]), fpip=np.array([fpip]), fsec=np.array([so]), den_done=dd[0],
                         den=dd[0], usd=dd[1], final_pending=pend)
                C.append(c)
        if kg:
            if self.ready("print"):
                self._top_kg(C, "print", best, lambda c: self._kg_print(c["comp"], c["x"], c["u"]))
            if self.ready("section") and self.ready("pip"):
                self._top_kg(C, "pipsec", best, lambda c: self._kg_pipsec(c["comp"], c["fp"], c["u"]))
            if self.ready("test"):
                self._top_kg([c for c in C if not c.get("final_pending")], "test", best,
                             lambda c: self._kg_test(c["comp"], c["fp"], c["fpip"], c["fsec"], c["u"]))
        return C

    def _kg_print(self, comp, x, u):
        y = self._fant("print", x)                               # (F, 2)
        uf = self.utility_samples_al([comp] * self.F, None, self.S, fixed_print=y)
        mu0 = float(u.mean())
        if uf is None:
            return None
        muf = uf.mean(axis=0)
        return lambda c: self._kg_from(muf, mu0, c)

    def _kg_pipsec(self, comp, fp, u):
        po = fp[0]
        cf = _feat_comp(self.space, comp)
        sec = self._fant("section", np.concatenate([cf, po]))   # (F, 2)
        pips = np.stack([self._fant("pip", np.concatenate([cf, po, sec[f]]))[f] for f in range(self.F)])
        uf = self.utility_samples_al([comp] * self.F, None, self.S, fixed_print=np.repeat(fp, self.F, 0),
                                     fixed_pip=pips, fixed_section=sec)
        mu0 = float(u.mean())
        if uf is None:
            return None
        muf = uf.mean(axis=0)
        return lambda c: self._kg_from(muf, mu0, c)

    def _kg_test(self, comp, fp, fpip, fsec, u):
        x = np.concatenate([fpip[0], fp[0], fsec[0]])
        y = self._fant("test", x)                                # (F, 2): ys/400, log EL
        cf = P2.al_cfactor(comp)
        uf = al_u(y[:, 0] * 400, np.exp(y[:, 1]), cf, float(sigm(fp[0, 0])), 10 ** fp[0, 1] - 0.01)
        mu0 = float(u.mean())
        return lambda c: self._kg_from(uf, mu0, c)

    # ------------------------------------------------------------------------------------------ copper
    def _cands_cu(self, v, P, pi, best):
        C = []
        recs = self._small_recs(v)
        large_g = v.get("large_g", 2000.0)
        promoted = {D["design"] for D in v["deposits"].values() if D["mode"] == "blend"}
        for lid, L in v["lots"].items():
            if L.get("gas"):
                continue
            pk = P.get(("lot", lid), set()) | P.get(("into", lid), set())
            deps = [D for D in v["deposits"].values() if D["lot"] == lid]
            has_large = any(D["mode"] == "blown_large" for D in deps)
            if pk or has_large:
                continue
            did = L["design"]
            go = did in promoted or lid in self.go_large_lots
            if go:
                if L["remaining_g"] >= large_g and not v.get("vertical") and not L.get("nsl"):
                    C.append(dict(what="NSL certificate before Mines", acts=[dict(kind="nsl", lot=lid)], always=True))
                    continue
                if L["remaining_g"] >= large_g:
                    rec = recs.get(did)
                    params = rec["params"] if rec else self.best_proc_design(v)
                    C.append(dict(what="1 kg deposit from powder made for it",
                                  acts=[dict(kind="large_ded", lot=lid, params=params)], always=True))
                else:
                    runs = max(int(math.ceil((large_g - L["remaining_g"]) / self.cut_per_run(L) * 1.15)), 1)
                    C.append(dict(what="top up the lot for its 1 kg deposit",
                                  acts=[self.powder_action(v["design_inputs"][did], runs=runs, into=lid)], always=True))
            elif not deps and L["remaining_g"] >= 450:
                C.append(dict(what="small deposit from powder already made",
                              acts=[dict(kind="small_ded", lot=lid, params=self.ded_params(v, lid))], always=True))
        kg = self.acq == "kg"
        ds, sc = [], []
        for did_, Dd in v["deposits"].items():
            mode = Dd["mode"]
            comp = v["designs"][Dd["design"]]
            pk = P.get(("deposit", did_), set())
            if mode in ("blend", "blown_small"):
                bb = self._best_block(Dd)
                if bb is None:
                    continue
                fl = 1.0 if mode == "blend" else 0.0
                has_pip, has_scr = isinstance(Dd.get("pip"), dict), isinstance(Dd.get("screen"), dict)
                blk = Dd["measured"][bb]
                fd = [float(logit(blk["rel_density"])), math.log10(blk["crack_density"] + 0.01),
                      blk.get("beta_prime", 0.0)]
                if not (has_pip and has_scr):
                    if pk & {"pip", "screen"}:
                        continue
                    acts = ([] if has_pip else [dict(kind="pip", deposit=did_, block=bb)]) + \
                           ([] if has_scr else [dict(kind="screen", deposit=did_, block=bb)])
                    ds.append((comp, fd, fl, acts, mode))
                    continue
                if fl == 1.0 and (self.blend_state.get(Dd["design"]) == "promoted" or
                                  any(L["design"] == Dd["design"] for L in v["lots"].values()) or
                                  P.get(("design", Dd["design"]), set()) & {"powder"}):
                    continue
                if fl == 0.0 and (Dd["lot"] in self.go_large_lots or any(
                        D2["lot"] == Dd["lot"] and D2["mode"] == "blown_large" for D2 in v["deposits"].values())):
                    continue
                if recs.get(Dd["design"], {}).get("dep") != did_:
                    continue
                sc.append((comp, recs[Dd["design"]], Dd))
            elif mode == "blown_large":
                C += self._cands_large(v, P, pi, best, did_, Dd, comp, pk, recs)
        if ds:
            comps = [d[0] for d in ds]
            FD, FL = np.array([d[1] for d in ds]), np.array([d[2] for d in ds])
            U = self._ucu(comps, self.S, fd=FD, fid=FL)
            dd = self._denom(v, TO_DONE[self.key]["dep_small"], pi)
            dn = self._denom(v, ("pipscreen",), pi) if kg else dd
            for j, (comp, fd, fl, acts, mode) in enumerate(ds):
                u = U[:, j:j + 1] if U is not None else None
                C.append(dict(stage="pipscreen", what="PIP and screen of a sound " + ("blend" if fl else "small") +
                              " deposit", acts=acts, u=u, mu=float(u.mean()) if u is not None else None, comp=comp,
                              fd=np.array([fd]), fl=fl, den_done=dd[0], den=dn[0], usd=dn[1]))
        if sc:
            comps = [x[0] for x in sc]
            U = self._ucu(comps, self.S, fd=np.array([x[1]["do"] for x in sc]), fp=np.array([x[1]["pip"] for x in sc]),
                          fs=np.array([x[1]["screen"] for x in sc]), fid=np.array([x[1]["fl"] for x in sc]))
            # a screened blend is valued as what it would be atomized (fl 0), the blend having passed the screen:
            # its own blend-fidelity readings enter through the nodes' data (with the fl flag), not as the atomized
            # alloy's outputs, which they are biased against (inhomogeneity, dilution)
            bl = []
            if bl and self.ready("ded") and U is not None:
                bp = self.best_proc_design(v)
                Xb = []
                for j in bl:
                    did = sc[j][2]["design"]
                    dsg = dict(v["design_inputs"][did], **(sc[j][1].get("params") or {}))
                    Xb.append(np.concatenate([_feat_comp(self.space, v["designs"][did]), self.sim_of(v, did),
                                              self.proc_vec(dsg), self.powder_feat(v), [0.0]]))
                U0 = self._ucu([comps[j] for j in bl], self.S, X_ded=np.array(Xb), fid=0.0)
                if U0 is not None:
                    U = U.copy()
                    U[:, bl] = U0
            learn_t = self._fitted_at.get("tensile", 0) < 4
            for j, (comp, rec, Dd) in enumerate(sc):
                u = U[:, j:j + 1]
                did = Dd["design"]
                if rec["fl"] == 1.0:
                    cpr = 430.0 * (1.75 if (self.crucible or v.get("crucible_cm3", 225)) >= 400 else 1.0)
                    runs = int(math.ceil(large_g * 1.15 / cpr))
                    a = self.powder_action(self.atomizer_settings(v, did, dict(v["design_inputs"][did])), runs=runs, v=v)
                    a["_did"], a["_promote"] = did, did
                    what = "atomize a screened blend for its 1 kg deposit"
                else:
                    L = v["lots"][Dd["lot"]]
                    runs = max(int(math.ceil((large_g - L["remaining_g"]) / self.cut_per_run(L) * 1.15)), 0)
                    a = self.powder_action(v["design_inputs"][did], runs=runs, into=Dd["lot"]) if runs > 0 else \
                        dict(kind="large_ded", lot=Dd["lot"], params=rec["params"])
                    a["_go_large"] = Dd["lot"]
                    what = "go large from a screened small deposit"
                dd = self._denom(v, TO_DONE[self.key]["screened"], pi, design=v["design_inputs"][did], runs=max(runs, 1))
                c = dict(stage="screened", what=what, acts=[a], u=u, mu=float(u.mean()), comp=comp, den_done=dd[0],
                         den=dd[0], usd=dd[1])
                if rec["fl"] == 0.0 and learn_t:
                    c["u"] = None                          # learn the deposit-to-tensile link first (round 2)
                if rec["fl"] == 1.0 and learn_t and c["mu"] >= max(0.3, 0.8 * best):
                    c["u"] = None                          # round 2's early rule: promote the best-looking blends
                C.append(c)
        if kg:
            if self.ready("pip") and self.ready("screen"):
                self._top_kg(C, "pipscreen", best, lambda c: self._kg_pipscreen(c["comp"], c["fd"], c["fl"], c["u"]))
            self._top_kg(C, "screened", best, lambda c: (lambda uu, mu0: (lambda cc: self._kg_from(uu[:, 0], mu0, cc)))(
                c["u"], c["mu"]))
        return C

    def _cands_large(self, v, P, pi, best, did_, Dd, comp, pk, recs):
        """A 1 kg deposit: tensile and immersion (EI: both, per cost of both; KG: each, per its own cost), and a stop
        for its coupon after each new interim reading if finishing can't pay."""
        C = []
        m = Dd["measured"][0]
        if not (m["rel_density"] >= 0.97 and m["crack_density"] < 0.5):
            return C
        rec = recs.get(Dd["design"])
        if rec is None:
            return C
        has_t = isinstance(Dd.get("tensile"), dict)
        imm = Dd.get("immersion")
        if has_t and isinstance(imm, dict):
            return C
        ft = np.array([[Dd["tensile"]["ys_MPa"] / 400, math.log(max(Dd["tensile"]["el_pct"], 0.3))]]) if has_t else None
        itm = Dd.get("imm_interim") or {}
        interim = None
        if itm and imm == "pending":
            dl = max(itm)
            interim = np.array([[math.log(max(itm[dl]["rate_um_yr"], 0.05)), self._dflag(dl)]])
        kw = dict(fd=np.array([rec["do"]]), fp=np.array([rec["pip"]]), fs=np.array([rec["screen"]]), fid=rec["fl"],
                  ft=ft, interim=interim)
        u = self._ucu([comp], self.S, **kw)
        if u is None:
            return C
        mu = float(u.mean())
        running = imm == "pending"
        if running and itm and self._imm_checked.get(did_) != max(itm):
            self._imm_checked[did_] = max(itm)
            b = max(best, 0.0)
            val = self._kg_imm(comp, kw, u)(b) if self.acq == "kg" else self._ei(u, b)
            if val is not None and val < self.STOP_V:
                C.append(dict(kind="stop", what="stop a coupon whose interim readings say it can't pay",
                              acts=[_ann(dict(kind="stop", deposit=did_), f"stop after day {max(itm)}: "
                                         f"{'KG' if self.acq == 'kg' else 'EI'} of finishing {val:.1e}", val)]))
        todo = []
        if not has_t and "tensile" not in pk:
            todo.append("tensile")
        if imm is None and "immersion" not in pk:
            todo.append("immersion")
        if not todo:
            C.append(dict(what="final result in flight", acts=[], u=u, mu=mu, final_pending=True))
            return C
        dd = self._denom(v, tuple(todo), pi)
        if self.acq == "ei":
            C.append(dict(stage="final", what="tensile and immersion of a 1 kg deposit",
                          acts=[dict(kind=k, deposit=did_) for k in todo], u=u, mu=mu, den=dd[0], den_done=dd[0],
                          usd=dd[1]))
        else:
            for k in todo:
                dn = self._denom(v, (k,), pi)
                kgf = self._kg_tensile(comp, kw, u) if k == "tensile" else self._kg_imm(comp, kw, u)
                C.append(dict(stage="final_" + k, what=f"{k} of a 1 kg deposit", acts=[dict(kind=k, deposit=did_)],
                              u=u, mu=mu, den=dn[0], den_done=dd[0], usd=dn[1], kg=kgf))
        return C

    def _kg_pipscreen(self, comp, fd, fl, u):
        x = np.concatenate([_feat_comp(self.space, comp), fd[0], [fl]])
        pips, scr = self._fant("pip", x), self._fant("screen", x)
        uf = self._ucu([comp] * self.F, self.S, fd=np.repeat(fd, self.F, 0), fp=pips, fs=scr, fid=fl)
        mu0 = float(u.mean())
        if uf is None:
            return None
        muf = uf.mean(axis=0)
        return lambda c: self._kg_from(muf, mu0, c)

    def _kg_tensile(self, comp, kw, u):
        if not self.ready("tensile"):
            return lambda c: self._kg_from(u[:, 0], float(u.mean()), c)
        fd, fp = kw["fd"], kw["fp"]
        x = np.concatenate([fp[0], fd[0], [kw["fid"]]])
        y = self._fant("tensile", x)
        kw2 = dict(kw, fd=np.repeat(fd, self.F, 0), fp=np.repeat(fp, self.F, 0), fs=np.repeat(kw["fs"], self.F, 0),
                   ft=y, interim=None if kw["interim"] is None else np.repeat(kw["interim"], self.F, 0))
        uf = self._ucu([comp] * self.F, self.S, **kw2)
        mu0 = float(u.mean())
        muf = uf.mean(axis=0)
        return lambda c: self._kg_from(muf, mu0, c)

    def _kg_imm(self, comp, kw, u):
        """KG of the 30-day result: fantasies of the 30-day rate from the immersion node (or from imm_cond given the
        latest interim reading), with tensile known or sampled."""
        rec_base = np.array(self._imm_base(comp, dict(screen=kw["fs"][0], do=kw["fd"][0], fl=kw["fid"])))
        if kw["interim"] is not None and self.ready("imm_cond"):
            y = self._fant("imm_cond", np.concatenate([kw["interim"][0], rec_base]))[:, :1]
        elif self.ready("immersion"):
            y = self._fant("immersion", rec_base)[:, :1]
        else:
            return lambda c: self._kg_from(u[:, 0], float(u.mean()), c)
        kw2 = dict(kw, fd=np.repeat(kw["fd"], self.F, 0), fp=np.repeat(kw["fp"], self.F, 0),
                   fs=np.repeat(kw["fs"], self.F, 0), fi=y, interim=None,
                   ft=None if kw["ft"] is None else np.repeat(kw["ft"], self.F, 0))
        uf = self._ucu([comp] * self.F, self.S, **kw2)
        mu0 = float(u.mean())
        muf = uf.mean(axis=0)
        return lambda c: self._kg_from(muf, mu0, c)

    # ------------------------------------------------------------------------------------------ new designs
    def _screen_share_ok(self, v):
        """Copper: blend screens (with their PIP and screen) may take at most SCREEN_SHARE of the campaign's money so
        far plus SCREEN_START, about round 2's share (18 % for BOFN with blend screening) with room to start. Without
        it the network's one-step values keep choosing a fresh design's screen over atomizing one already screened
        (a fresh pick from a pool is the best of many guesses; a screened design's value is what it turned out to be)
        and the year's money goes to screens."""
        if self.al:
            return True
        est = v["estimate"]
        nb = sum(1 for D in v["deposits"].values() if D["mode"] == "blend") + \
            sum(1 for p in v["pending"] if p["kind"] == "blend_ded")
        used = nb * (est(dict(kind="blend_ded")) + est(dict(kind="pip")) + est(dict(kind="screen")))
        return used <= self.SCREEN_SHARE * v["spent"] + self.SCREEN_START

    def _cands_new(self, v, P, pi, best_kb):
        if not self.can_start_new(v) or not self._screen_share_ok(v):
            return []
        simmed = {s["design"] for s in v["sims"] if s["kind"] == self.sim_kind}
        used = {L["design"] for L in v["lots"].values()} | {D["design"] for D in v["deposits"].values()}
        pend_d = {k[1] for k, kinds in P.items() if k[0] == "design" and kinds & {"powder", "blend_ded"}}
        free = [d for d in simmed if d not in self.started and d not in used and d not in pend_d]
        if not free:
            return []
        taken = [_feat_comp(self.space, v["designs"][d]) for d in (self.started | used | pend_d) if d in v["designs"]]
        bp = self.best_proc_design(v)
        rows, keep = [], []
        T = np.array(taken) if taken else None
        for d in free:
            f = _feat_comp(self.space, v["designs"][d])
            if T is not None and float(np.min(np.linalg.norm(T - f, axis=1))) < self.D_TAKEN:
                continue
            dsg = dict(v["design_inputs"][d], **{k: bp[k] for k in bp if k not in ("superheat_K", "pour_mbar",
                                                                                    "amplitude")})
            row = [f, self.sim_of(v, d), self.proc_vec(dsg), self.powder_feat(v)]
            if not self.al:
                row.append([0.0])
            rows.append(np.concatenate(row))
            keep.append(d)
        self._n_eligible = len(keep)
        if not keep:
            return []
        X = np.array(rows)
        comps = [v["designs"][d] for d in keep]
        if not self.al:
            X = X.copy()
            X[:, -1] = 1.0                       # copper's new designs are blend screens: valued at the blend fidelity,
            X[:, -2] = 0.9                       # like the screened blends they compete with (round 2's blend powder)
        u = self.utility_samples_al(comps, X, self.S) if self.al else self._ucu(comps, self.S, X_ded=X, fid=1.0)
        p_ok = self._p_powder(v, keep)
        out = []
        if u is None:
            # the network can't run yet: round 2's prior (the funnel's proxy and screen), below any valued option
            outs = {s["design"]: s["out"] for s in v["sims"] if s["kind"] == self.sim_kind}
            pr = np.array([P1.Tiered.proxy(self, v["designs"][d], outs[d]) for d in keep])
            ok = np.array([1.0 if P1.Tiered.passes(self, outs[d], v["designs"][d]) else 0.0 for d in keep])
            pr = (pr - pr.mean()) / (pr.std() + 1e-9)
            sc = np.exp(pr) * (0.3 + ok) * (0.5 + self.gen.random(len(keep)))
            order = np.argsort(-sc)[:4]
            for j in order:
                out.append(self._new_cand(v, keep[j], None, None, pi, prior=float(sc[j])))
            return out
        ei = np.array([self._ei(u[:, j], best_kb) for j in range(u.shape[1])]) * p_ok
        order = [j for j in np.argsort(-(ei + 1e-9 * u.mean(axis=0))) if ei[j] >= self.MIN_NEW_EI][:self.N_NEW_KG]
        chosen = []
        for j in order:
            f = _feat_comp(self.space, comps[j])
            if chosen and min(float(np.linalg.norm(f - g)) for g in chosen) < self.D_BATCH:
                continue
            chosen.append(f)
            c = self._new_cand(v, keep[j], u[:, j:j + 1], X[j], pi)
            c["p_ok"] = float(p_ok[j])
            out.append(c)
            if len(out) >= 8:
                break
        return out

    def _p_powder(self, v, dids):
        """The atomize node's chance that a design gives usable powder (in-cut yield above 3 % of the charge) at the
        settings it would be run at; 1 before the node has data. The network's utility starts at the print or DED
        node, so without this a design that won't atomize looks as good as one that will."""
        if not self.ready("atomize"):
            return np.ones(len(dids))
        from scipy.stats import norm
        X = []
        for d in dids:
            dsg = self.atomizer_settings(v, d, dict(v["design_inputs"][d]))
            X.append(self.atom_x(v, d, dsg))
        m, sd = self.nodes["atomize"][0].predict(np.array(X))
        return norm.cdf((m - 0.03) / np.maximum(sd, 1e-6))

    def _new_cand(self, v, did, u, x, pi, prior=None):
        design = v["design_inputs"][did]
        if self.al:
            a = self.powder_action(self.atomizer_settings(v, did, dict(design)), v=v)
            first = ("powder", "print")
            what = "new design: powder, then a print"
        else:
            self._fid = 1.0
            params = self._settings_design(v, did, 4, 0.15)
            self._fid = 0.0
            a = dict(kind="blend_ded", design=dict(design), params=params)
            first = ("blend",)
            what = "new design: a blended-powder DED screen"
        a["_did"] = did
        c = dict(what=what, acts=[a], u=u, mu=float(u.mean()) if u is not None else None, did=did)
        c["den_done"] = self._denom(v, TO_DONE[self.key]["new"], pi, design=design)[0]
        c["den"], c["usd"], _ = self._denom(v, first if self.acq == "kg" else TO_DONE[self.key]["new"], pi,
                                            design=design)
        if u is None:
            c["u"] = None
            c["value"] = None
            c["prior"] = prior
            return c
        if self.acq == "kg":
            comp = v["designs"][did]
            if self.al:
                c["kg"] = self._kg_print(comp, x, u)
            else:
                xb = np.array(x, float).copy()                 # already the blend's DED input (fl 1)
                y = self._fant("ded", xb)
                uf = self._ucu([comp] * self.F, self.S, fd=y, fid=1.0)
                mu0 = float(u.mean())
                if uf is not None:
                    muf = uf.mean(axis=0)
                    c["kg"] = (lambda muf=muf, mu0=mu0: (lambda cc: self._kg_from(muf, mu0, cc)))()
        return c


class PKGFN3(Net3):
    name = "pkgfn3"
    acq = "kg"


VARIANTS = {
    "bofn3": (Net3, "ei", "time"),
    "bofn3_usd": (Net3, "ei", "usd"),
    "pkgfn3": (PKGFN3, "kg", "time"),
    "pkgfn3_usd": (PKGFN3, "kg", "usd"),
}


def make(name, key, seed, crucible=None):
    cls, acq, den = VARIANTS[name]
    p = cls(key, seed, crucible)
    p.name, p.acq, p.denom = name, acq, den
    return p
