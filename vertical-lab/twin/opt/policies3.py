"""Round-3 policies: every policy on the asynchronous engine (``Twin(mode="async")``), with the same capacity and the
same freedom to fill it.

Round 2 asked a policy for ``wip - inflight`` actions whenever one of its results came back. Round 3 asks, every hour a
station, robot, person or fixture frees up (or results come back), for a ranked list of actions across everything the
campaign could do; the engine admits each one whose gating station can take it now and which the spending plan allows
(``Campaign.submit3``). Pending evaluations are the policies' business, as in asynchronous BO.

* ``Async``: rounds 1 and 2's baselines (random, Sobol, the heuristic) unchanged, behind an adapter: an action the
  engine turns away for capacity or the plan is offered again first at the next decision, so nothing a policy decided
  is lost and nothing is proposed twice.
* ``Tiered3`` (and its mis-specified and ablated variants): the funnel, screening its 256 designs once (round 2's
  screen requested them a few at a time under the cap), then making its shortlist as capacity allows.
* ``GPBO3``: round 2's GP-BO (one GP from the design to the measured utility, expected improvement per dollar) with
  the kriging believer for designs in flight (Ginsbourger et al. 2010): each started design whose result is not back
  is a pseudo-observation at its posterior mean, so the next design is not proposed on top of it.
* ``Net3``: BOFN and pKGFN on every node of every part (``twin/opt/net3.py``).
"""
from __future__ import annotations

import numpy as np

from twin import policies as P1
from twin.opt import policies2 as P2
from twin.opt.tinygp import TinyGP


def _is_new(a):
    k = a.get("kind", "")
    return (k == "powder" and not a.get("into")) or k == "blend_ded" or k.startswith("sim_")


class Async:
    """A round-1/2 policy on the asynchronous engine: its own decisions, offered again when turned away. Every
    downstream step its rules call for is offered at once (and again until a station takes it); new designs at most
    N_NEW at a time (the atomizer takes about one per slot), the turned-away ones first."""
    N_NEW = 4

    def __init__(self, inner, name=None):
        self.inner = inner
        self.name = name or getattr(inner, "name", "policy")
        self.retry = []

    def __getattr__(self, k):                     # observed(), key, al, ... for the trace and the summaries
        if k == "inner":
            raise AttributeError(k)
        return getattr(self.inner, k)

    def propose(self, v, n):
        inner = self.inner
        if isinstance(inner, P2.Base2):
            inner.advance2(v)
        else:
            inner.advance(v, n)
        down = inner.take(len(inner.todo))
        old_new = [a for a in self.retry if _is_new(a)]
        old_down = [a for a in self.retry if not _is_new(a)]
        self.retry = []
        k_new = max(0, self.N_NEW - len(old_new))
        fresh = (inner.propose(v, k_new) or []) if k_new > 0 else []
        return old_down + down + old_new + fresh

    def rejected(self, a, why):
        if why in ("capacity", "plan"):
            self.retry.append(a)

    def admitted(self, a):
        pass


class _Tiered3:
    """The funnel on the asynchronous engine: all 256 screening simulations requested at once (the cluster has 50
    cores, so they are back within the hour), the shortlist made when the screen is complete, then made in order as
    the atomizer frees up. The screened designs are round 2's for the same seed (same random draw).

    When its shortlist is made and capacity and money are left, the funnel goes on down its own ranking: the next
    KEEP designs (by its rule) among the screened designs it has not made, and another 256 screened designs when
    those run out. (Round 2's funnel rebuilt the same shortlist when it ran out under the cap and made the same
    designs again; round 3 lets it reach further instead.)"""

    def propose(self, v, n):
        if not self.screened:
            self.screened = True
            self.cands = self.space.sample(self.N_SCREEN, seed=int(self.rng.integers(1 << 30)))
            self._shortlisted, self._made, self._asked = False, set(), len(self.cands)
            return [dict(kind=self.sim_kind, design=d) for d in self.cands]
        if not self._shortlisted:
            if len(v["sims"]) < self._asked:
                return []
            v2 = dict(v, sims=[x for x in v["sims"] if x["design"] not in self._made])
            self.shortlist = [d for d in self._shortlist(v2) if d not in self._made] if v2["sims"] else []
            self._shortlisted = True
            if not self.shortlist:                       # everything this screen offers is made: screen more
                more = self.space.sample(self.N_SCREEN, seed=int(self.rng.integers(1 << 30)))
                self._asked += len(more)
                self._shortlisted = False
                return [dict(kind=self.sim_kind, design=d) for d in more]
        self.advance(v, n)
        acts = self.take(n)
        while len(acts) < n and self.shortlist:
            did = self.shortlist.pop(0)
            self._made.add(did)
            acts.append(self.powder_action(v["design_inputs"][did]))
        if not self.shortlist:
            self._shortlisted = False                    # next time: the next KEEP down the ranking
        return acts


class Tiered3(_Tiered3, P1.Tiered):
    name = "tiered"


class TieredMis3(_Tiered3, P1.TieredMis):
    name = "tiered_mis"


class TieredScreen3(_Tiered3, P1.TieredScreenOnly):
    name = "tiered_screen"


class TieredProxy3(_Tiered3, P1.TieredProxyOnly):
    name = "tiered_proxy"


class GPBO3(P2.GPBO):
    """Round 2's GP-BO with the kriging believer for designs in flight (and for the batch it is choosing)."""
    name = "gpbo"

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        self.inflight_x = {}               # design key -> encoded design, admitted and not yet observed

    def _dkey(self, d):
        return tuple(round(d.get(e, 0.0), 3) for e in self.space.elements)

    def admitted(self, a):
        if a.get("kind") == "powder" and not a.get("into"):
            self.inflight_x[self._dkey(a["design"])] = self.space.encode(a["design"])

    def rejected(self, a, why):
        if a.get("kind") == "powder" and not a.get("into") and a.get("_init"):
            self.init.insert(0, a["design"])                 # an initial design waits for the next free slot
            self._init_kinds.insert(0, a.get("_acq_kind", "initial design"))
        elif a.get("kind") != "powder" and why in ("capacity", "plan"):
            self.todo.insert(0, a)                           # a downstream step waits for its station

    def propose(self, v, n):
        self.advance2(v)
        acts = self.take(n)
        if len(acts) >= n:
            return acts[:n]
        if self.init is None:
            seeds = self.reference_seeds()
            more = [] if self.common_seeds is not None else \
                self.space.sample(self.N_INIT - len(P2.REF_ALLOYS[self.key]), seed=2000 + self.seed, kind="sobol")
            self.init = seeds + more
            self._init_kinds = [self.seed_label()] * len(seeds) + ["initial design (Sobol)"] * len(more)
        if not self.can_start_new(v):
            return acts[:n]
        obs = self.observed(v)
        done = {self._dkey(v["design_inputs"][d]) for d, _ in obs}
        for k in list(self.inflight_x):
            if k in done:
                del self.inflight_x[k]
        while len(acts) < n and self.init:
            a = P2._ann(self.powder_action(self.init.pop(0), v=v), self._init_kinds.pop(0))
            a["_init"] = True
            acts.append(a)
        if len(acts) >= n:
            return acts[:n]
        if len(obs) < 4:
            # nothing to learn from yet: space-filling designs, a few at a time (the atomizer takes one per slot)
            more = self.space.sample(min(n - len(acts), 2), seed=int(self.gen.integers(1 << 30)), kind="sobol")
            return acts + [P2._ann(self.powder_action(d, v=v), "space-filling while the first results come back")
                           for d in more]
        state = (len(obs), tuple(sorted(self.inflight_x)))
        if getattr(self, "_cache_state", None) == state and self._cache:
            return acts + [dict(a) for a in self._cache[:n - len(acts)]]
        X = np.array([self.space.encode(v["design_inputs"][d]) for d, _ in obs])
        y = np.array([u for _, u in obs])
        self.node.fit(X, y)
        g = TinyGP(self.node)
        Xp = np.array(list(self.inflight_x.values())) if self.inflight_x else np.zeros((0, X.shape[1]))
        if len(Xp):
            g = g.with_rows(Xp, g.predict(Xp)[0])            # the kriging believer
        cands = self.pool(v)
        Xc = np.array([self.space.encode(d) for d in cands])
        cost = np.array([self.cost_new(v, d) for d in cands])
        best = y.max()
        from scipy.stats import norm
        n0 = len(acts)
        for _ in range(3):
            mu, sd = g.predict(Xc)
            z = (mu - best) / np.maximum(sd, 1e-9)
            ei = np.maximum((mu - best) * norm.cdf(z) + sd * norm.pdf(z), 1e-12)
            score = ei / cost
            j = int(np.argmax(score))
            acts.append(P2._ann(self.powder_action(cands[j], v=v), "EI per $ (one GP; kriging believer for pending)",
                                float(score[j]), ei=ei[j], mu=mu[j], sd=sd[j], cost=cost[j], best_obs=best))
            g = g.with_rows(Xc[j:j + 1], mu[j:j + 1])
            cost[j] = np.inf
        self._cache_state, self._cache = state, [dict(a) for a in acts[n0:]]
        return acts[:n]


def make3(name, key, seed, crucible=None, seeding=None):
    """A round-3 policy by name."""
    if name in ("random", "sobol", "heuristic"):
        inner = P2.make(name, key, seed, crucible, seeding)
        return Async(inner, name)
    T = {"tiered": Tiered3, "tiered_mis": TieredMis3, "tiered_screen": TieredScreen3, "tiered_proxy": TieredProxy3}
    if name in T:
        return Async(T[name](key, seed), name)
    if name == "gpbo":
        return GPBO3(key, seed, crucible)
    from twin.opt import net3
    if name in net3.VARIANTS:
        return net3.make(name, key, seed, crucible)
    raise ValueError(name)
