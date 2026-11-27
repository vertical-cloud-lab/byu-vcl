"""Round 6: round 3's BOFN and pKGFN (``net3``) without their money rules, and able to face a large simulated pool.

* **No money rules.** ``can_start_new`` (more than $1,500 or $3,000 left) and copper's cap on blend screens
  (``_screen_share_ok``: a quarter of the money spent so far plus $2,500) are gone, with every other money gate of the
  engine (twin/round6.py ``GATES_REMOVED``). Round 5 named that cap as the likely cause of copper's stretches with
  free capacity and nothing started.
* **Why nothing new was proposed** is counted (``counts``: ``new_none_free``, ``new_none_eligible``, ``new_low_ei``),
  so that an idle stretch that remains can be explained.
* **A large pool** (the HPC stream at scale). The network's value of a new design costs a pass through every node's
  GP for every candidate and sample, so it is computed for at most ``N_NET`` candidates a decision. When more are
  free, the pool is first cut with the screen and proxy the funnel uses and round 3's networks already use as their
  prior before they have data (``policies.Tiered.passes`` and ``proxy``, from the open-CALPHAD result): the best
  ``N_NET - N_RAND`` among those that pass, and ``N_RAND`` drawn at random from the rest so the network is not
  confined to the proxy's taste. With ``N_NET`` free candidates or fewer (round 5's pool) nothing is cut, and the
  policy is round 3's.
* The simulation feature of a design is looked up in an index (round 3 scanned the whole list per design).
* **Speed, the same policy.** A profile of an automated-lab BOFN run (300 days) put 66 % of its time in valuing new
  designs, and most of that in the atomize node's search over 64 settings per candidate (``atomizer_settings``):
  rebuilding each trial's features from the whole design, and one GP prediction per candidate. Round 6 builds a
  composition's features once and encodes only the three settings that change (the same numbers as
  ``Space.encode``: a test checks it), and ``_p_powder`` predicts the trials of ``PP_CHUNK`` candidates in one call
  (the same draws in the same order; a batched prediction can differ from 64 single ones in the last bit).
"""
from __future__ import annotations

import numpy as np

from twin import policies as P1
from twin.opt import net3 as N3
from twin.opt import policies2 as P2
from twin.opt import policies3 as P3


class _Six:
    N_NET = 384
    N_RAND = 96

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        self._pre = np.random.default_rng(seed * 131 + (5 if self.al else 6))
        self._px = {}
        self._six, self._six_key, self._sf = {}, None, {}
        self._pre_n = 0
        for k in ("new_calls", "new_offered", "new_none_free", "new_none_eligible", "new_low_ei", "prescreened"):
            self.counts[k] = 0

    # ------------------------------------------------------------------------------------------ no money rules
    def can_start_new(self, v):
        return True

    def _screen_share_ok(self, v):
        return True

    # ------------------------------------------------------------------------------------------ speed
    PP_CHUNK = 16                                    # candidates whose 64 trial settings are predicted in one call

    def _trials(self, design):
        """policies2's 64 trial settings for a design (itself, then 63 random draws of the atomizer's three settings,
        drawn in the same order), and their encodings as ``Space.encode`` makes them."""
        pv = self.space.process[:3]
        trial = [dict(design)]
        for _ in range(63):
            d = dict(design)
            for var in pv:
                d[var.name] = float(var.from_unit(self.gen.random()))
            trial.append(d)
        U = np.clip(np.array([[var.to_unit(d[var.name]) for var in pv] for d in trial], float), 0, 1)
        return trial, U

    def _atom_rows(self, v, did, U):
        """``atom_x`` for one composition at several settings: the composition's and the simulation's features
        (the same for every trial) beside each trial's three settings."""
        base = np.concatenate([P2._feat_comp(self.space, v["designs"][did]), self.sim_of(v, did)])
        return np.hstack([np.broadcast_to(base, (len(U), len(base))), U])

    def atomizer_settings(self, v, did, design):
        """policies2's search: the atomize node's best of 64 settings for this composition (mean + half a standard
        deviation), with the features built once."""
        if not self.ready("atomize") or self.sim_of(v, did) is None:
            return design
        trial, U = self._trials(design)
        mu, sd = self.nodes["atomize"][0].predict(self._atom_rows(v, did, U))
        return trial[int(np.argmax(mu + 0.5 * sd))]

    def _p_powder(self, v, dids):
        """net3's chance of usable powder, with the 64 trial settings of ``PP_CHUNK`` candidates predicted at once."""
        if not self.ready("atomize"):
            return np.ones(len(dids))
        if any(self.sim_of(v, d) is None for d in dids):
            return super()._p_powder(v, dids)
        from scipy.stats import norm
        node = self.nodes["atomize"][0]
        X = []
        for i0 in range(0, len(dids), self.PP_CHUNK):
            part = dids[i0:i0 + self.PP_CHUNK]
            trials, rows = [], []
            for d in part:
                trial, U = self._trials(dict(v["design_inputs"][d]))
                trials.append(trial)
                rows.append(self._atom_rows(v, d, U))
            mu, sd = node.predict(np.vstack(rows))
            sc = (mu + 0.5 * sd).reshape(len(part), 64)
            for d, trial, j in zip(part, trials, np.argmax(sc, axis=1)):
                X.append(self.atom_x(v, d, trial[int(j)]))
        m, sd = node.predict(np.array(X))
        return norm.cdf((m - 0.03) / np.maximum(sd, 1e-6))

    # ------------------------------------------------------------------------------------------ a large pool
    def sim_of(self, v, did):
        sims = v["sims"]
        key = (len(sims), v.get("sims_rev"), id(sims))
        if key != self._six_key:
            idx, kind = {}, self.sim_kind
            for s in reversed(sims):                 # the first in the list wins, as in round 3's scan
                if s["kind"] == kind:
                    idx[s["design"]] = s["out"]
            self._six, self._six_key = idx, key
            if len(self._sf) > 8 * len(idx) + 4096:
                self._sf = {}
        f = self._sf.get(did)
        if f is not None:
            return f
        o = self._six.get(did)
        if o is None:
            return None
        f = (np.array([min(1.3 * o["kou_K"] / 500, 2), (o["liquidus_C"] - 600) / 300]) if self.al else
             np.array([o["freezing_range_K"] / 200, o["beta_900"], o["kappa_700"] * 5,
                       (o["liquidus_C"] - 1000) / 300]))
        self._sf[did] = f
        return f

    def _prescreen(self, v, free):
        px = self._px
        ok, pr = np.zeros(len(free), bool), np.zeros(len(free))
        for j, s in enumerate(free):
            d = s["design"]
            r = px.get(d)
            if r is None:
                comp = v["designs"][d]
                r = px[d] = (bool(P1.Tiered.passes(self, s["out"], comp)), float(P1.Tiered.proxy(self, comp, s["out"])))
            ok[j], pr[j] = r
        if len(px) > 4 * len(free) + 4096:
            self._px = {s["design"]: px[s["design"]] for s in free}
        order = np.lexsort((-pr, ~ok))               # those that pass first, then by the proxy
        n_top = self.N_NET - self.N_RAND
        rest = order[n_top:]
        rnd = self._pre.choice(rest, size=min(self.N_RAND, len(rest)), replace=False) if len(rest) else []
        return {free[int(j)]["design"] for j in list(order[:n_top]) + list(rnd)}

    def _cands_new(self, v, P, pi, best_kb):
        self.counts["new_calls"] += 1
        sims, kind = v["sims"], self.sim_kind
        used = {L["design"] for L in v["lots"].values()} | {D["design"] for D in v["deposits"].values()}
        pend_d = {k[1] for k, kinds in P.items() if k[0] == "design" and kinds & {"powder", "blend_ded"}}
        free = [s for s in sims if s["kind"] == kind and s["design"] not in self.started and s["design"] not in used
                and s["design"] not in pend_d]
        n_free = len(free)
        if n_free > self.N_NET:
            keep = self._prescreen(v, free)
            drop = {s["design"] for s in free} - keep
            self._pre_n += 1
            v = dict(v, sims=[s for s in sims if s["design"] not in drop], sims_rev=("pre", self._pre_n))
            self.counts["prescreened"] += 1
        out = super()._cands_new(v, P, pi, best_kb)
        if out:
            self.counts["new_offered"] += len(out)
        elif n_free == 0:
            self.counts["new_none_free"] += 1
        elif self._n_eligible == 0:
            self.counts["new_none_eligible"] += 1    # every free candidate is within D_TAKEN of a design started
        else:
            self.counts["new_low_ei"] += 1           # none reaches MIN_NEW_EI
        return out


class Net6(_Six, N3.Net3):
    name = "bofn3"


class PKGFN6(_Six, N3.PKGFN3):
    name = "pkgfn3"
    acq = "kg"


class _Cap:
    """For a check only (out/twin6/checks/copper_idle.py), never the grid: round 6's policy with round 5's cap on
    copper's blend screens put back, so that what the cap does can be told apart from what the rest of round 6 does.
    A call the cap refuses is counted as ``new_capped``. (The check's rows made at d865668 count such a call as
    ``new_low_ei``: net3 returns before it counts the eligible candidates, so net6 read the last call's count.)"""

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        self.counts["new_capped"] = 0

    def _screen_share_ok(self, v):
        return N3.Net3._screen_share_ok(self, v)

    def _cands_new(self, v, P, pi, best_kb):
        if not N3.Net3._screen_share_ok(self, v):
            self.counts["new_calls"] += 1
            self.counts["new_capped"] += 1
            return []
        return super()._cands_new(v, P, pi, best_kb)


class Net6Cap(_Cap, Net6):
    name = "bofn3cap"


class PKGFN6Cap(_Cap, PKGFN6):
    name = "pkgfn3cap"
    acq = "kg"


VARIANTS = {"bofn3": (Net6, "ei", "time"), "bofn3_usd": (Net6, "ei", "usd"),
            "pkgfn3": (PKGFN6, "kg", "time"), "pkgfn3_usd": (PKGFN6, "kg", "usd"),
            "bofn3cap": (Net6Cap, "ei", "time"), "pkgfn3cap": (PKGFN6Cap, "kg", "time")}


def make6(name, key, seed, crucible=None):
    """A round-6 policy by name: the network policies without money rules; every other policy is round 3's (their
    one money rule, ``can_start_new``, never binds: the engine reports no limit)."""
    if name in VARIANTS:
        cls, acq, den = VARIANTS[name]
        p = cls(key, seed, crucible)
        p.name, p.acq, p.denom = name, acq, den
        return p
    return P3.make3(name, key, seed, crucible)
