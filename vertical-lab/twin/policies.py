"""Baseline policies that exercise the twin. They are deliberately simple and transparent; the twin is the point.
DAL's own BOFN/pKGFN implementations (benchmarks/bofn-prelim/bofn_alloy.py) can drive it through the same
``propose(view, n_free)`` interface (notes/twin.md, "Plugging in another optimizer").

* ``Random``: a random design (composition and process) through the whole chain, one after another: the
  "pre-registered random baseline" FLAIME's acceleration factor is measured against.
* ``Tiered``: the funnel both proposals argue against. Screen many compositions with the open CALPHAD node, keep the
  ones it calls printable and sound, rank them by a metallurgist's strength proxy, then make and test them in order,
  tuning the process on each powder.
* ``CostAware``: a function-network surrogate with partial evaluation, in the spirit of BOFN with powder reuse (the
  most robust policy in DAL's prelim): Gaussian processes per measured node (printability from composition + process
  + simulator outputs; strength and ductility, or corrosion, from composition), and each decision buys the action
  with the highest expected improvement per dollar among: simulate new compositions, make a powder, print or deposit
  an existing powder at new settings, test an existing part. It pays for the cheap simulators on every candidate
  before it buys powder.
"""
from __future__ import annotations

import math
import warnings

import numpy as np

from twin import spaces, usgs

warnings.filterwarnings("ignore")

AL_PROC = dict(superheat_K=150.0, pour_mbar=200.0, amplitude=0.8, P_W=300.0, v_mm_s=1000.0, h_um=110.0, t_um=30.0,
               T0_C=150.0)
CU_PROC = dict(superheat_K=120.0, pour_mbar=220.0, amplitude=0.8, P_W=600.0, v_mm_min=600.0, feed_g_min=6.0)
AL_REF_C = None


def _ref_cmdri():
    global AL_REF_C
    if AL_REF_C is None:
        AL_REF_C = usgs.mineral_burden({"Al": 89.65, "Si": 10.0, "Mg": 0.35})["cmdri_log"]
    return AL_REF_C


def d_(x, lo, hi):
    return float(np.clip((x - lo) / (hi - lo), 0, 1))


def al_obs_utility(ys, el, comp, dense, crack_free):
    """The utility the policy can compute from its own measurements (it knows the USGS data too)."""
    b = usgs.mineral_burden(comp)
    ref = _ref_cmdri()
    if not (dense >= 0.995 and crack_free) or b["mbs_lin"] > 0.174:
        return 0.0
    return (d_(ys, 150, 400) * d_(el, 2, 15) * d_(1.5 * ref - b["cmdri_log"], 0, 1.5 * ref)) ** (1 / 3)


def cu_obs_utility(ys, el, rate30, ni, dense, crack_free, ref_rate=9.0):
    if not (dense >= 0.99 and crack_free):
        return 0.0
    return (d_(ys, 100, 400) * d_(el, 5, 35) * d_(3.0 * ref_rate - rate30, 0, 2.5 * ref_rate) * d_(30 - ni, 0, 30)) ** 0.25


def perturb(space, proc, rng, scale=0.15):
    out = dict(proc)
    for v in space.process:
        if v.name in ("superheat_K", "pour_mbar", "amplitude"):
            continue
        u = np.clip(v.to_unit(out[v.name]) + rng.normal(0, scale), 0, 1)
        out[v.name] = float(v.from_unit(u))
    return out


def with_proc(design, proc):
    d = dict(design)
    d.update(proc)
    return d


class Base:
    full_chain = False            # True: every candidate goes through every step, whatever the screens say

    def __init__(self, key: str, seed: int = 0):
        self.todo = []
        self.key = key
        self.space = spaces.SPACES[key]
        self.rng = np.random.default_rng(seed + (11 if key == "flaime_al" else 13))
        self.al = key == "flaime_al"
        self.proc0 = AL_PROC if self.al else CU_PROC
        self.started = set()          # design ids sent to powder
        self.queued = {}              # design dicts waiting for a powder slot

    def new_design(self):
        d = self.space.sample(1, seed=int(self.rng.integers(1 << 30)))[0]
        return d

    # the downstream steps every policy takes the same way: advance what exists before starting anything new
    def advance(self, v, n, tested_ok=None):
        """Queue the downstream step of every artifact that has come back, once; return the queue's head."""
        acts = self.todo
        if self.al:
            for lid, L in v["lots"].items():
                if L["remaining_g"] >= 30 and not L.get("_printed"):
                    L["_printed"] = True
                    acts.append(self.print_action(v, lid))
            for bid, B in v["builds"].items():
                if not B.get("tested") and not B.get("_asked"):
                    m = B["measured"][B["bars_at"]]
                    if self.full_chain or (m["rel_density"] >= 0.98 and m["crack_density"] < 0.3):
                        B["_asked"] = True
                        acts.append(dict(kind="test", build=bid))
                    else:
                        B["_asked"] = True
                        B["skip"] = True
        else:
            for lid, L in v["lots"].items():
                st = L.setdefault("_stage", "new")
                if st == "new" and L["remaining_g"] >= 450:
                    acts.append(dict(kind="small_ded", lot=lid, params=self.ded_params(v, lid)))
                    L["_stage"] = "small"
                elif st == "small_done" and L["remaining_g"] >= 2000 and not L.get("nsl") and not L.get("_nsl"):
                    acts.append(dict(kind="nsl", lot=lid))
                    L["_nsl"] = True
                elif st == "small_done" and L.get("nsl") and L["remaining_g"] >= 2000:
                    acts.append(dict(kind="large_ded", lot=lid, params=L["_best_params"]))
                    L["_stage"] = "large"
            for did, D in v["deposits"].items():
                L = v["lots"][D["lot"]]
                if D["mode"] == "blown_small" and not D.get("_seen"):
                    D["_seen"] = True
                    ok = [m for m in D["measured"] if m["rel_density"] >= 0.98 and m["crack_density"] < 0.3]
                    if self.full_chain:
                        ok = list(D["measured"])
                    if ok and (self.full_chain or self.go_large(v, D)):
                        best = max(ok, key=lambda m: m["rel_density"] - m.get("beta_prime", 0) * 0.05
                                   - (1 if m["crack_density"] > 0.05 else 0))
                        L["_best_params"] = best["params"]
                        L["_stage"] = "small_done"
                        if L["remaining_g"] < 2000:
                            runs = int(math.ceil((2000 - L["remaining_g"]) / 450.0)) + 1
                            acts.append(dict(kind="powder", design=v["design_inputs"][L["design"]], runs=runs,
                                             into=D["lot"]))
                    else:
                        L["_stage"] = "dropped"
                if D["mode"] == "blown_large" and not D.get("_tested"):
                    D["_tested"] = True
                    m = D["measured"][0]
                    if self.full_chain or (m["rel_density"] >= 0.97 and m["crack_density"] < 0.5):
                        acts += [dict(kind="tensile", deposit=did), dict(kind="immersion", deposit=did),
                                 dict(kind="screen", deposit=did)]
        return acts

    def take(self, n):
        out, self.todo = self.todo[:n], self.todo[n:]
        return out

    def go_large(self, v, D):
        return True

    def print_action(self, v, lid):
        L = v["lots"][lid]
        base = {k: v["design_inputs"][L["design"]].get(k, self.proc0[k]) for k in self.proc0}
        params = [base] + [perturb(self.space, base, self.rng) for _ in range(8)]
        return dict(kind="print", lot=lid, params=params, bars_at=0)

    def ded_params(self, v, lid):
        L = v["lots"][lid]
        base = {k: v["design_inputs"][L["design"]].get(k, self.proc0[k]) for k in self.proc0}
        return [base] + [perturb(self.space, base, self.rng, 0.2) for _ in range(3)]

    def powder_action(self, design):
        return dict(kind="powder", design=design, runs=2 if self.al else 3)


def _merge_topups(v):
    """Cu: a top-up lot's grams join the original lot (same design, same atomizer settings)."""
    return v


class Random(Base):
    name = "random"
    full_chain = True

    def propose(self, v, n):
        self.advance(v, n)
        acts = self.take(n)
        while len(acts) < n:
            d = self.new_design()
            acts.append(self.powder_action(d))
        return acts[:n]


class Tiered(Base):
    """Screen with the open CALPHAD node, then make the shortlist in order."""
    name = "tiered"
    N_SCREEN = 256
    KEEP = 24

    def __init__(self, key, seed=0):
        super().__init__(key, seed)
        self.screened = False
        self.shortlist = []

    def proxy(self, comp, out):
        if self.al:
            ss = sum(dict(Mg=18, Cu=12, Zn=4, Si=8, Mn=32, Cr=25, Li=12, Fe=20, Ni=10, Ti=15, Zr=15, Sc=20, Er=10,
                          Ce=5, Sn=2).get(e, 0) * w ** 0.75 for e, w in comp.items() if e != "Al")
            ppt = 300 * math.sqrt(comp.get("Sc", 0)) + 120 * math.sqrt(comp.get("Zr", 0))
            b = usgs.mineral_burden(comp)["cmdri_log"]
            return ss + ppt - 3000 * b
        ni, al = comp.get("Ni", 0), comp.get("Al", 0)
        return 14 * al + 2.6 * ni + 6 * comp.get("Mn", 0) - 3 * ni - 200 * out.get("beta_900", 0)

    def passes(self, out):
        if self.al:
            return 1.3 * out["kou_K"] < 250 and out["liquidus_C"] < 900
        return out["liquidus_C"] <= 1250 and out["freezing_range_K"] < 110 and out["beta_900"] < 0.3

    def propose(self, v, n):
        acts = []
        if not self.screened:
            self.screened = True
            self.cands = self.space.sample(self.N_SCREEN, seed=int(self.rng.integers(1 << 30)))
            return [dict(kind="sim_open", design=d) for d in self.cands[:n]] + \
                [dict(kind="sim_open", design=d) for d in self.cands[n:]][:0]
        done = {s["design"] for s in v["sims"]}
        if len(v["sims"]) < self.N_SCREEN and not self.shortlist:
            pend = [d for d in self.cands if True][len(v["sims"]):len(v["sims"]) + n]
            if v["inflight"] < v["wip"]:
                return [dict(kind="sim_open", design=d) for d in pend]
        if not self.shortlist and len(v["sims"]) >= self.N_SCREEN - v["wip"]:
            ok = [(self.proxy(v["designs"][s["design"]], s["out"]), s["design"]) for s in v["sims"]
                  if self.passes(s["out"])]
            ok.sort(reverse=True)
            self.shortlist = [did for _, did in ok[:self.KEEP]] or [s["design"] for s in v["sims"][:self.KEEP]]
        self.advance(v, n)
        acts = self.take(n)
        while len(acts) < n and self.shortlist:
            did = self.shortlist.pop(0)
            acts.append(self.powder_action(v["design_inputs"][did]))
        if len(acts) < n and not self.shortlist and v["inflight"] == 0:
            # shortlist exhausted: tune the process on the best powders seen (powder reuse)
            pass
        return acts[:n]


class CostAware(Base):
    """GP surrogates per measured node; expected improvement per dollar over the next actions."""
    name = "cost_aware"
    N_CAND = 400

    def __init__(self, key, seed=0):
        super().__init__(key, seed)
        self.simmed_pending = set()

    def _key(self, d):
        return tuple(round(d.get(e, 0.0), 3) for e in self.space.elements)

    # ---------------------------------------------------------------- features and models
    def feat(self, comp):
        return np.array([comp.get(e, 0.0) / self.space.bounds[e][1] for e in self.space.elements])

    def _gp(self, X, y):
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
        k = ConstantKernel(0.1, (1e-3, 10)) * Matern(length_scale=np.full(X.shape[1], 0.5), length_scale_bounds=(0.05, 20),
                                                     nu=2.5) + WhiteKernel(1e-3, (1e-6, 1e-1))
        g = GaussianProcessRegressor(k, normalize_y=True, n_restarts_optimizer=0, random_state=0)
        g.fit(X, y)
        return g

    def observed(self, v):
        """(design id, observed utility) for every tested design."""
        rows = []
        if self.al:
            for t in v["tests"]:
                B = v["builds"].get(t["build"]) if t["build"] else None
                m = B["measured"][B["bars_at"]] if B else dict(rel_density=t["measured"].get("rel_density", 0.996),
                                                                crack_density=0.0)
                comp = v["designs"][t["design"]]
                rows.append((t["design"], al_obs_utility(t["measured"]["ys_MPa"], t["measured"]["el_pct"], comp,
                                                         m["rel_density"], m["crack_density"] < 0.05)))
        else:
            for did, D in v["deposits"].items():
                if D["mode"] == "blown_large" and isinstance(D.get("tensile"), dict) and isinstance(D.get("immersion"), dict):
                    comp = v["designs"][D["design"]]
                    m = D["measured"][0]
                    rows.append((D["design"], cu_obs_utility(D["tensile"]["ys_MPa"], D["tensile"]["el_pct"],
                                                             D["immersion"]["rate30_um_yr"], comp.get("Ni", 0),
                                                             m["rel_density"], m["crack_density"] < 0.05)))
        return rows

    def screen_feature(self, v, did):
        cache = self.__dict__.setdefault("_sf", {})
        if did in cache:
            return cache[did]
        s = [x for x in v["sims"] if x["design"] == did and x["kind"] == "sim_open"]
        if not s:
            return None
        o = s[-1]["out"]
        cache[did] = self._sf_from(o)
        return cache[did]

    def _sf_from(self, o):
        if self.al:
            return np.array([min(1.3 * o["kou_K"] / 500, 2), (o["liquidus_C"] - 600) / 300])
        return np.array([o["freezing_range_K"] / 200, o["beta_900"], (o["liquidus_C"] - 1000) / 300])

    def propose(self, v, n):
        self.advance(v, n)
        acts = self.take(n)
        if len(acts) >= n:
            return acts[:n]
        # 1. simulate a fresh batch of candidates (cheap): the open CALPHAD node on every one
        if not hasattr(self, "cands") or len([s for s in v["sims"]]) < 32:
            if not hasattr(self, "cands"):
                self.cands = []
            if len(self.cands) < 64:
                new = self.space.sample(64, seed=int(self.rng.integers(1 << 30)))
                self.cands += new
                return acts + [dict(kind="sim_open", design=d) for d in new[: n - len(acts)]]
        simmed = {s["design"]: s for s in v["sims"] if s["kind"] == "sim_open"}
        keyset = getattr(self, "_keyset", set())
        for i in simmed:
            keyset.add(self._key(v["design_inputs"][i]))
        self._keyset = keyset
        unsim = [d for d in self.cands if self._key(d) not in keyset and id(d) not in self.simmed_pending]
        if unsim and len(acts) < n and len(simmed) < 48:
            take = unsim[: max(1, (n - len(acts)) // 2)]
            for d in take:
                self.simmed_pending.add(id(d))
            acts += [dict(kind="sim_open", design=d) for d in take]
        # 2. choose the next powder by EI per dollar over simulated candidates
        obs = self.observed(v)
        best = max([u for _, u in obs], default=0.0)
        cand = [i for i in simmed if i not in self.started]
        if not cand:
            more = self.space.sample(32, seed=int(self.rng.integers(1 << 30)))
            self.cands += more
            return (acts + [dict(kind="sim_open", design=d) for d in more])[:n]
        Xc = np.array([np.concatenate([self.feat(v["designs"][i]), self.screen_feature(v, i)]) for i in cand])
        if len(obs) >= 4:
            Xo = np.array([np.concatenate([self.feat(v["designs"][i]), self.screen_feature(v, i)
                                           if self.screen_feature(v, i) is not None else np.zeros(Xc.shape[1] - len(self.space.elements))])
                           for i, _ in obs])
            yo = np.array([u for _, u in obs])
            # refit only when a new test result has come back (same data, same fit: random_state is fixed)
            if getattr(self, "_gp_n", -1) != len(obs):
                self._gp_fit, self._gp_n = self._gp(Xo, yo), len(obs)
            g = self._gp_fit
            mu, sd = g.predict(Xc, return_std=True)
            z = (mu - best) / np.maximum(sd, 1e-6)
            from scipy.stats import norm
            ei = (mu - best) * norm.cdf(z) + sd * norm.pdf(z)
        else:
            # before four tests: the metallurgist's proxy as the prior, the screen as a soft preference, and noise
            pr = np.array([self.proxy(v["designs"][i], simmed[i]["out"]) for i in cand])
            ok = np.array([1.0 if self.passes(simmed[i]["out"]) else 0.0 for i in cand])
            pr = (pr - pr.mean()) / (pr.std() + 1e-9)
            ei = np.exp(pr) * (0.3 + ok) * (0.5 + self.rng.random(len(cand)))
        cost = v["estimate"](dict(kind="powder", runs=1 if self.al else 3)) + (1000 if self.al else 2500)
        order = np.argsort(-ei / cost)
        for j in order:
            if len(acts) >= n:
                break
            did = cand[j]
            self.started.add(did)
            design = with_proc(v["design_inputs"][did], self.best_proc(v))
            acts.append(self.powder_action(design))
        return acts[:n]

    def best_proc(self, v):
        """The process settings that gave the densest crack-free parts so far (powder-independent part of the
        process knowledge), else the default."""
        best, bp = -1, None
        if self.al:
            for B in v["builds"].values():
                for m in B["measured"]:
                    s = m["rel_density"] - (1 if m["crack_density"] > 0.05 else 0)
                    if s > best:
                        best, bp = s, m["params"]
        else:
            for D in v["deposits"].values():
                for m in D["measured"]:
                    s = m["rel_density"] - (1 if m["crack_density"] > 0.05 else 0)
                    if s > best:
                        best, bp = s, m["params"]
        p = dict(self.proc0)
        if bp:
            p.update({k: bp[k] for k in bp if k in p})
        return p

    def go_large(self, v, D):
        """ONR: send a composition to Mines only if its small deposits were sound and its screen-level prospects
        are among the better half of what the campaign has seen."""
        ok = [m for m in D["measured"] if m["rel_density"] >= 0.98 and m["crack_density"] < 0.1
              and m.get("beta_prime", 0) < 0.25]
        return bool(ok)

    def print_action(self, v, lid):
        L = v["lots"][lid]
        base = self.best_proc(v)
        base.update({k: v["design_inputs"][L["design"]].get(k, base[k]) for k in ("superheat_K", "pour_mbar", "amplitude")})
        params = [base] + [perturb(self.space, base, self.rng, 0.1) for _ in range(8)]
        return dict(kind="print", lot=lid, params=params, bars_at=0)


CostAware.proxy = Tiered.proxy
CostAware.passes = Tiered.passes
POLICIES = {"random": Random, "tiered": Tiered, "cost_aware": CostAware}
