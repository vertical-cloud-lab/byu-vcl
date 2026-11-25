"""Round-2 policies: the baselines an optimizer has to beat, standard Bayesian optimization, SAASBO, and Bayesian
optimization of function networks with partial evaluations (BOFN), all on ``propose(view, n_free)``.

* ``Sobol``: a scrambled Sobol design of the whole space (composition and process), made and tested in order. The
  design-of-experiments baseline.
* ``Heuristic``: what a metallurgist does without a model: start from the reference alloys (AlSi10Mg, Al-Mn-Cr-Zr,
  Al-Zr; 90-10, 70-30, NAB), keep the best measured alloy, and try a few elements up or down from it, keeping the
  process settings that worked.
* ``GPBO``: one Gaussian process from the design (composition and process, d = 23 for FLAIME, 14 for copper) to the
  utility the lab measures at the end of the chain, expected improvement per dollar over a candidate pool, every
  sound part taken through the whole chain. ``SAASBO`` is the same with the sparse axis-aligned subspace prior
  (fully Bayesian, NUTS; Eriksson & Jankowiak, UAI 2021) and ``SAASMAP`` with that prior at its MAP point.
* ``BOFN``: a GP per network node (Astudillo & Frazier, NeurIPS 2021), each node's inputs its parents' measured
  outputs plus the design variables that act on it, the final utility computed from the sampled network. Partial
  evaluations (the spirit of pKGFN, Buathong et al. 2024): every step is a separate purchase, and a part goes on
  to the next, dearer step only when the network's expected improvement of finishing it, per dollar, beats that of
  starting something new. The vertical lab's cheap instruments are what makes the intermediate nodes informative:
  PIP gives a stress-strain curve from a polished coupon, the CubXL an hour's corrosion screen, the SEM/EBSD and XRD
  the microstructure.

Networks (inputs -> outputs, all as the lab measures them):

FLAIME: print [composition, Kou index and liquidus (open CALPHAD node), LPBF power/speed/hatch/layer/plate T,
powder O and satellites] -> (logit density, log crack density); pip [composition, print outputs] -> (YS, UTS,
uniform elongation); test [pip outputs, print outputs] -> (YS, log elongation); utility(YS, EL, mineral burden,
gates).

ONR: ded [composition, freezing range, beta at 900 C and kappa at 700 C (CALPHAD), DED power/speed/feed, powder O]
-> (logit density, log crack density, beta'); pip [composition, ded outputs] -> (YS, UTS, UE); screen [composition,
ded outputs] -> (log early rate, breakdown potential); tensile [pip outputs, ded outputs] -> (YS, log EL) of the
larger deposit; immersion [screen outputs, beta', Ni, Fe, Al] -> (log 30-day rate, log selective attack); utility(YS,
EL, 30-day rate, Ni, gates).
"""
from __future__ import annotations

import math

import numpy as np

from twin import policies as P1
from twin import spaces, usgs
from twin.opt.gp import Node

AL, CU = spaces.AL, spaces.CU
REF_ALLOYS = {
    "flaime_al": [{"Si": 10.0, "Mg": 0.35}, {"Mn": 3.6, "Cr": 0.5, "Zr": 0.9}, {"Zr": 1.0}],
    "onr_cu": [{"Ni": 10.0, "Fe": 1.4, "Mn": 0.8}, {"Ni": 30.0, "Fe": 0.6, "Mn": 0.6},
               {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}],
}


def logit(p):
    p = np.clip(np.asarray(p, float), 0.5, 0.99995)
    return np.log(p / (1 - p))


def sigm(z):
    return 1.0 / (1.0 + np.exp(-np.asarray(z, float)))


def clip01(x):
    return np.clip(x, 0.0, 1.0)


_BURDEN = {}


def al_cfactor(comp: dict) -> float:
    """The mineral-burden desirability and gate, which the lab computes from the composition (USGS data)."""
    key = tuple(sorted((k, round(v, 3)) for k, v in comp.items()))
    if key not in _BURDEN:
        b = usgs.mineral_burden(comp)
        ref = P1._ref_cmdri()
        _BURDEN[key] = 0.0 if b["mbs_lin"] > 0.174 else float(clip01((1.5 * ref - b["cmdri_log"]) / (1.5 * ref)))
    return _BURDEN[key]


def al_u(ys, el, cf, dens, crack):
    d = clip01((ys - 150.0) / 250.0) * clip01((el - 2.0) / 13.0) * cf
    return np.cbrt(d) * ((dens >= 0.995) & (crack < 0.05))


def cu_u(ys, el, rate30, ni, dens, crack, ref=9.0):
    d = clip01((ys - 100.0) / 300.0) * clip01((el - 5.0) / 30.0) * clip01((3 * ref - rate30) / (2.5 * ref)) \
        * clip01((30.0 - ni) / 30.0)
    return d ** 0.25 * ((dens >= 0.99) & (crack < 0.05))


# --------------------------------------------------------------------------------------------- shared machinery
class Base2(P1.Base):
    """Downstream steps shared by the round-2 policies, aware of the vertical lab (no NSL, 1 kg blocks in house)."""
    name = "base2"
    uses_network = False           # BOFN: sound parts go to the cheap nodes (PIP, screen) first; the policy decides
    N_POOL_SIM = 64

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed)
        self.crucible = crucible
        self.seed = seed
        self.gen = np.random.default_rng(seed * 7 + (3 if self.al else 5))

    # ---------------------------------------------------------------- actions
    def runs_for(self, v):
        c = self.crucible or v.get("crucible_cm3", 225)
        if self.al:
            return 1 if c >= 400 else 2
        return 2 if c >= 400 else 3

    def powder_action(self, design, runs=None, v=None, **kw):
        a = dict(kind="powder", design=design, runs=runs or (self.runs_for(v) if v else (2 if self.al else 3)), **kw)
        if self.crucible:
            a["crucible_cm3"] = self.crucible
        return a

    def cut_per_run(self, L):
        m = L["measured"]
        ok = max(m.get("runs", 1) - m.get("failed_runs", 0), 1)
        return max(m.get("cut_g", 0.0) / ok, 150.0)

    # ---------------------------------------------------------------- the chain after a powder exists
    def advance2(self, v):
        acts = self.todo
        if self.al:
            for lid, L in v["lots"].items():
                if L["remaining_g"] >= 30 and not L.get("_printed"):
                    L["_printed"] = 1
                    acts.append(self.print_action(v, lid))
            for bid, B in v["builds"].items():
                if B.get("_asked"):
                    continue
                m = B["measured"][B["bars_at"]]
                sound = m["rel_density"] >= 0.98 and m["crack_density"] < 0.3
                B["_asked"] = True
                if not sound:
                    B["skip"] = True
                    continue
                if self.uses_network:
                    acts += [dict(kind="pip", build=bid, cube=B["bars_at"]),
                             dict(kind="section", build=bid, cube=B["bars_at"])]
                    B["_await_pip"] = True
                else:
                    acts.append(dict(kind="test", build=bid))
        else:
            large_g = v.get("large_g", 2000.0)
            for lid, L in v["lots"].items():
                st = L.setdefault("_stage", "new")
                if st == "new" and L["remaining_g"] >= 450:
                    acts.append(dict(kind="small_ded", lot=lid, params=self.ded_params(v, lid)))
                    L["_stage"] = "small"
                elif st == "go_large" and L["remaining_g"] >= large_g:
                    if not v.get("vertical") and not L.get("nsl"):
                        if not L.get("_nsl"):
                            acts.append(dict(kind="nsl", lot=lid))
                            L["_nsl"] = True
                        continue
                    acts.append(dict(kind="large_ded", lot=lid, params=L["_best_params"]))
                    L["_stage"] = "large"
            for did, D in v["deposits"].items():
                if D["lot"] is None:                    # a blended-powder screen (BOFNBlend handles those)
                    continue
                L = v["lots"][D["lot"]]
                if D["mode"] == "blown_small" and not D.get("_seen"):
                    D["_seen"] = True
                    ok = [(i, m) for i, m in enumerate(D["measured"]) if m["rel_density"] >= 0.98
                          and m["crack_density"] < 0.3]
                    if not ok:
                        L["_stage"] = "dropped"
                        continue
                    i, best = max(ok, key=lambda im: im[1]["rel_density"] - im[1].get("beta_prime", 0) * 0.05
                                  - (1 if im[1]["crack_density"] > 0.05 else 0))
                    L["_best_params"], L["_best_block"], L["_small"] = best["params"], i, did
                    if self.uses_network:
                        acts += [dict(kind="pip", deposit=did, block=i), dict(kind="screen", deposit=did, block=i)]
                        L["_stage"] = "screening"
                    else:
                        self.go_large(v, L, D["lot"])
                if D["mode"] == "blown_large" and not D.get("_tested"):
                    D["_tested"] = True
                    m = D["measured"][0]
                    if m["rel_density"] >= 0.97 and m["crack_density"] < 0.5:
                        acts += [dict(kind="tensile", deposit=did), dict(kind="immersion", deposit=did)]
        return acts

    def go_large(self, v, L, lid):
        large_g = v.get("large_g", 2000.0)
        L["_stage"] = "go_large"
        if L["remaining_g"] < large_g:
            runs = int(math.ceil((large_g - L["remaining_g"]) / self.cut_per_run(L) * 1.15))
            self.todo.append(self.powder_action(v["design_inputs"][L["design"]], runs=max(runs, 1), into=lid))

    # ---------------------------------------------------------------- measured utilities (what the lab can compute)
    def observed(self, v):
        rows = []
        if self.al:
            for t in v["tests"]:
                B = v["builds"].get(t["build"]) if t["build"] else None
                m = B["measured"][B["bars_at"]] if B else dict(rel_density=t["measured"].get("rel_density", 0.996),
                                                                crack_density=0.0)
                comp = v["designs"][t["design"]]
                rows.append((t["design"], P1.al_obs_utility(t["measured"]["ys_MPa"], t["measured"]["el_pct"], comp,
                                                            m["rel_density"], m["crack_density"] < 0.05)))
        else:
            for did, D in v["deposits"].items():
                if D["mode"] == "blown_large" and isinstance(D.get("tensile"), dict) and \
                        isinstance(D.get("immersion"), dict):
                    comp = v["designs"][D["design"]]
                    m = D["measured"][0]
                    rows.append((D["design"], P1.cu_obs_utility(D["tensile"]["ys_MPa"], D["tensile"]["el_pct"],
                                                                D["immersion"]["rate30_um_yr"], comp.get("Ni", 0),
                                                                m["rel_density"], m["crack_density"] < 0.05)))
        return rows

    # ---------------------------------------------------------------- candidate pools
    def perturb_design(self, d, scale=0.08, flip=0.15):
        u = self.space.encode(d)
        ne = len(self.space.elements)
        u2 = u.copy()
        u2[:ne] = np.clip(u[:ne] + self.gen.normal(0, scale, ne) * (u[:ne] > 0), 0, 1)
        if self.gen.random() < flip:                       # switch one element on or off
            j = int(self.gen.integers(ne))
            u2[j] = 0.0 if u2[j] > 0 else self.gen.uniform(0.05, 0.5)
        u2[ne:] = np.clip(u[ne:] + self.gen.normal(0, scale, len(u) - ne), 0, 1)
        out = self.space.decode(u2)
        return out if not self.space.check(out) else None

    def reference_seeds(self):
        """The reference alloys with the default process settings: every model-based policy starts from them, as
        a lab would (the heuristic does too; Sobol and random don't)."""
        out = []
        for r in REF_ALLOYS[self.key]:
            d = {e: r.get(e, 0.0) for e in self.space.elements}
            d.update(self.proc0)
            out.append(self.space.repair(d))
        return out

    def sound_parents(self, v, k=4):
        """Designs whose parts came out sound, strongest first (by tensile, else PIP, else density)."""
        rows = []
        if self.al:
            for B in v["builds"].values():
                m = B["measured"][B["bars_at"]]
                if m["rel_density"] >= 0.99 and m["crack_density"] < 0.05:
                    pip = B.get("pip") if isinstance(B.get("pip"), dict) else None
                    rows.append(((pip or {}).get("ys_MPa", 0) + 1000 * m["rel_density"], B["design"]))
        else:
            for D in v["deposits"].values():
                ok = [m for m in D["measured"] if m["rel_density"] >= 0.99 and m["crack_density"] < 0.05]
                if ok:
                    pip = D.get("pip") if isinstance(D.get("pip"), dict) else None
                    rows.append(((pip or {}).get("ys_MPa", 0) + 1000 * max(m["rel_density"] for m in ok), D["design"]))
        rows.sort(key=lambda r: -r[0])
        seen, out = set(), []
        for _, d in rows:
            if d not in seen:
                seen.add(d)
                out.append(d)
        return out[:k]

    def pool(self, v, n_global=192, n_local=192, top=6):
        """Candidates: a fresh scrambled Sobol sample of the space plus local moves around the best measured
        alloys and around the soundest strong parts."""
        cands = self.space.sample(n_global, seed=int(self.gen.integers(1 << 30)), kind="sobol")
        obs = sorted(self.observed(v), key=lambda r: -r[1])[:top]
        obs = [(d, u) for d, u in obs] + [(d, 0.0) for d in self.sound_parents(v) if d not in {o[0] for o in obs}]
        for did, u in obs:
            base = v["design_inputs"][did]
            for _ in range(n_local // max(len(obs), 1)):
                d = self.perturb_design(base)
                if d is not None:
                    cands.append(d)
        return cands

    def can_start_new(self, v):
        """Enough money left for a new design's powder and the chain after it (else only finish what exists)."""
        return v["budget_left"] > (1500.0 if self.al else 3000.0)

    def cost_new(self, v, design):
        """What finding out about a new design costs: its powder at today's prices plus the chain after it."""
        base = v["estimate"](self.powder_action(design, v=v))
        return base + (900.0 if self.al else 2200.0)


def _feat_comp(space, comp):
    return np.array([comp.get(e, 0.0) / space.bounds[e][1] for e in space.elements])


# --------------------------------------------------------------------------------------------------- baselines
class Sobol(Base2):
    """A scrambled Sobol design, made and tested in order."""
    name = "sobol"

    def propose(self, v, n):
        self.advance2(v)
        acts = self.take(n)
        if not hasattr(self, "design_list"):
            self.design_list = self.space.sample(1024, seed=1000 + self.seed, kind="sobol")
        while len(acts) < n and self.design_list and self.can_start_new(v):
            acts.append(self.powder_action(self.design_list.pop(0), v=v))
        return acts[:n]


class Heuristic(Base2):
    """Reference alloys first, then one or two elements at a time up or down from the best measured alloy."""
    name = "heuristic"

    def propose(self, v, n):
        self.advance2(v)
        acts = self.take(n)
        if not hasattr(self, "seeds"):
            self.seeds = []
            for r in REF_ALLOYS[self.key]:
                d = {e: r.get(e, 0.0) for e in self.space.elements}
                d.update(self.proc0)
                self.seeds.append(self.space.repair(d))
        while len(acts) < n and self.seeds:
            acts.append(self.powder_action(self.seeds.pop(0), v=v))
        obs = sorted(self.observed(v), key=lambda r: -r[1])
        while len(acts) < n and self.can_start_new(v):
            if obs and obs[0][1] > 0:
                parent = v["design_inputs"][obs[min(int(self.gen.integers(0, 2)), len(obs) - 1)][0]]
            else:                                  # nothing works yet: the soundest strong part so far, or a reference
                parent = self.best_sound(v) or dict(self.space.repair({**{e: 0.0 for e in self.space.elements},
                                                                         **REF_ALLOYS[self.key][int(self.gen.integers(3))],
                                                                         **self.proc0}))
            child = None
            for _ in range(20):
                child = self.mutate(parent)
                if child is not None:
                    break
            if child is None:
                child = self.space.sample(1, seed=int(self.gen.integers(1 << 30)))[0]
            child.update({k: parent[k] for k in self.proc0 if k in parent})
            acts.append(self.powder_action(child, v=v))
        return acts[:n]

    def mutate(self, d):
        u = self.space.encode(d)
        ne = len(self.space.elements)
        k = int(self.gen.integers(1, 3))
        for j in self.gen.choice(ne, size=k, replace=False):
            u[j] = float(np.clip(u[j] + self.gen.choice([-1, 1]) * self.gen.uniform(0.1, 0.3), 0, 1))
        out = self.space.decode(u)
        return out if not self.space.check(out) else None

    def best_sound(self, v):
        best, bd = -1, None
        if self.al:
            for t in v["tests"]:
                s = t["measured"]["ys_MPa"] * min(t["measured"]["el_pct"], 10)
                if s > best:
                    best, bd = s, v["design_inputs"][t["design"]]
        else:
            for D in v["deposits"].values():
                for m in D["measured"]:
                    s = m["rel_density"] - (1 if m["crack_density"] > 0.05 else 0)
                    if s > best:
                        best, bd = s, v["design_inputs"][D["design"]]
        return dict(bd) if bd else None


class GPBO(Base2):
    """One GP from the design to the measured utility; EI per dollar; the whole chain for every sound part."""
    name = "gpbo"
    kind = "gp"
    N_INIT = 8

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        self.node = Node(self.kind, refit_every=4 if self.kind != "saas_nuts" else 1, seed=seed)
        self.init = None

    def propose(self, v, n):
        self.advance2(v)
        acts = self.take(n)
        if len(acts) >= n:
            return acts[:n]
        if self.init is None:
            self.init = self.reference_seeds() + self.space.sample(self.N_INIT - len(REF_ALLOYS[self.key]),
                                                                   seed=2000 + self.seed, kind="sobol")
        if not self.can_start_new(v):
            return acts[:n]
        obs = self.observed(v)
        while len(acts) < n and self.init:
            acts.append(self.powder_action(self.init.pop(0), v=v))
        if len(acts) >= n:
            return acts[:n]
        if len(obs) < 4:
            # nothing to learn from yet: more space-filling designs while the first ones go through the chain
            more = self.space.sample(n - len(acts), seed=int(self.gen.integers(1 << 30)), kind="sobol")
            return acts + [self.powder_action(d, v=v) for d in more]
        X = np.array([self.space.encode(v["design_inputs"][d]) for d, _ in obs])
        y = np.array([u for _, u in obs])
        self.node.fit(X, y)
        cands = self.pool(v)
        Xc = np.array([self.space.encode(d) for d in cands])
        mu, sd = self.node.predict(Xc)
        best = y.max()
        from scipy.stats import norm
        z = (mu - best) / np.maximum(sd, 1e-9)
        ei = np.maximum((mu - best) * norm.cdf(z) + sd * norm.pdf(z), 1e-12)
        cost = np.array([self.cost_new(v, d) for d in cands])
        score = ei / cost
        picked = []
        for _ in range(n - len(acts)):
            if picked:
                dmin = np.min(np.linalg.norm(Xc[:, None, :] - Xc[picked][None, :, :], axis=2), axis=1)
                s2 = score * (1 - np.exp(-(dmin / 0.15) ** 2))
            else:
                s2 = score
            j = int(np.argmax(s2))
            picked.append(j)
            score[j] = -1
            acts.append(self.powder_action(cands[j], v=v))
        return acts[:n]


class SAASBO(GPBO):
    """GPBO with the SAAS prior, fully Bayesian (NUTS: 128 warm-up, 128 samples, thinned to 16)."""
    name = "saasbo"
    kind = "saas_nuts"


class SAASMAP(GPBO):
    """GPBO with the SAAS prior at its MAP point (cheap)."""
    name = "saasmap"
    kind = "saas_map"


# ------------------------------------------------------------------------------------------------------ BOFN
class BOFN(Base2):
    """Bayesian optimization of the function network, with partial evaluations (see the module docstring)."""
    name = "bofn"
    uses_network = True
    node_kind = "gp"
    S = 64

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        k = self.node_kind
        if self.al:
            self.nodes = {"atomize": [Node("gp", 8, seed=seed)],
                          "print": [Node(k, 24, max_n=400, seed=seed), Node(k, 24, max_n=400, seed=seed)],
                          "section": [Node(k, 6, seed=seed), Node(k, 6, seed=seed)],
                          "pip": [Node(k, 6, seed=seed) for _ in range(3)],
                          "test": [Node("gp", 4, seed=seed) for _ in range(2)]}
        else:
            self.nodes = {"atomize": [Node("gp", 8, seed=seed)],
                          "ded": [Node(k, 8, seed=seed) for _ in range(3)],
                          "pip": [Node(k, 4, seed=seed) for _ in range(3)],
                          "screen": [Node(k, 4, seed=seed) for _ in range(2)],
                          "tensile": [Node("gp", 3, seed=seed) for _ in range(2)],
                          "immersion": [Node("gp", 3, seed=seed) for _ in range(2)]}
        self.sim_kind = "sim_open"
        self.asked_sims = set()
        self._fitted_at = {}

    # ---------------------------------------------------------------- features
    def sim_of(self, v, did):
        c = self.__dict__.setdefault("_simc", {})
        if did in c:
            return c[did]
        for s in v["sims"]:
            if s["design"] == did and s["kind"] == self.sim_kind:
                o = s["out"]
                c[did] = (np.array([min(1.3 * o["kou_K"] / 500, 2), (o["liquidus_C"] - 600) / 300]) if self.al else
                          np.array([o["freezing_range_K"] / 200, o["beta_900"], o["kappa_700"] * 5,
                                    (o["liquidus_C"] - 1000) / 300]))
                return c[did]
        return None

    def atom_x(self, v, did, design):
        u = self.space.encode(design)
        ne = len(self.space.elements)
        return np.concatenate([_feat_comp(self.space, v["designs"][did]), self.sim_of(v, did), u[ne:ne + 3]])

    def atomizer_settings(self, v, did, design):
        """The atomize node's best of 64 settings for this composition (mean + half a standard deviation)."""
        if not self.ready("atomize") or self.sim_of(v, did) is None:
            return design
        trial = [dict(design)]
        for _ in range(63):
            d = dict(design)
            for var in self.space.process[:3]:
                d[var.name] = float(var.from_unit(self.gen.random()))
            trial.append(d)
        X = np.array([self.atom_x(v, did, d) for d in trial])
        mu, sd = self.nodes["atomize"][0].predict(X)
        return trial[int(np.argmax(mu + 0.5 * sd))]

    def proc_vec(self, design):
        u = self.space.encode(design)
        ne = len(self.space.elements)
        return u[ne + 3:]                       # LPBF or DED settings (the atomizer's three come first)

    def powder_feat(self, v, lot=None):
        if lot is not None:
            m = v["lots"][lot]["measured"]
            ox = m.get("oxygen_ppm") or 800.0
            sat = (m.get("sem") or {}).get("satellite_frac", 0.1)
        else:
            oxs = [L["measured"].get("oxygen_ppm") for L in v["lots"].values() if L["measured"].get("oxygen_ppm")]
            ox = float(np.median(oxs)) if oxs else 800.0
            sat = 0.1
        return np.array([ox / 2000.0, sat]) if self.al else np.array([ox / 1000.0])

    # ---------------------------------------------------------------- the nodes' data, from what the lab has seen
    def datasets(self, v):
        D = {k: ([], [[] for _ in self.nodes[k]]) for k in self.nodes}

        def add(node, x, ys):
            D[node][0].append(x)
            for i, y in enumerate(ys):
                D[node][1][i].append(y)
        # the atomize node: composition, the believed liquidus and the atomizer settings -> in-cut yield per charge
        for lid, L in v["lots"].items():
            m = L["measured"]
            if L.get("gas") or "yield" not in m:
                continue
            sf = self.sim_of(v, L["design"])
            if sf is None:
                continue
            y = (m["yield"] or {}).get("cut_yield_frac")
            if y is None:
                continue
            add("atomize", self.atom_x(v, L["design"], v["design_inputs"][L["design"]]), [float(y)])
        if self.al:
            for bid, B in v["builds"].items():
                did = B["design"]
                comp = _feat_comp(self.space, v["designs"][did])
                sf = self.sim_of(v, did)
                if sf is None:
                    continue
                pf = self.powder_feat(v, B["lot"])
                for m in B["measured"]:
                    x = np.concatenate([comp, sf, self.proc_vec(dict(v["design_inputs"][did], **m["params"])), pf])
                    add("print", x, [float(logit(m["rel_density"])), math.log10(m["crack_density"] + 0.01)])
                pm, sc = B.get("pip"), B.get("section")
                mb = B["measured"][B["bars_at"]]
                po = [float(logit(mb["rel_density"])), math.log10(mb["crack_density"] + 0.01)]
                so = self.section_out(B)
                if so is not None:
                    add("section", np.concatenate([comp, po]), so)
                if isinstance(pm, dict) and so is not None:
                    add("pip", np.concatenate([comp, po, so]), [pm["ys_MPa"] / 400, pm["uts_MPa"] / 500,
                                                                pm["ue_pct"] / 20])
            for t in v["tests"]:
                B = v["builds"].get(t["build"]) if t["build"] else None
                if B is None or not isinstance(B.get("pip"), dict) or self.section_out(B) is None:
                    continue
                pm, mb = B["pip"], B["measured"][B["bars_at"]]
                x = [pm["ys_MPa"] / 400, pm["uts_MPa"] / 500, pm["ue_pct"] / 20, float(logit(mb["rel_density"])),
                     math.log10(mb["crack_density"] + 0.01)] + self.section_out(B)
                add("test", x, [t["measured"]["ys_MPa"] / 400, math.log(max(t["measured"]["el_pct"], 0.2))])
        else:
            small = {}
            for did_, Dd in v["deposits"].items():
                did = Dd["design"]
                comp = _feat_comp(self.space, v["designs"][did])
                sf = self.sim_of(v, did)
                if sf is None:
                    continue
                if Dd["mode"] in ("blown_small", "blend"):
                    fl = 1.0 if Dd["mode"] == "blend" else 0.0
                    pf = self.powder_feat(v, Dd["lot"]) if Dd["lot"] is not None else np.array([0.9])
                    for m in Dd["measured"]:
                        x = np.concatenate([comp, sf, self.proc_vec(dict(v["design_inputs"][did], **m["params"])), pf,
                                            [fl]])
                        add("ded", x, [float(logit(m["rel_density"])), math.log10(m["crack_density"] + 0.01),
                                       m.get("beta_prime", 0.0)])
                    i = Dd["measured"].index(max(Dd["measured"], key=lambda m: m["rel_density"]))
                    bb = Dd.get("_best_block")
                    if bb is None and Dd["lot"] is not None and v["lots"][Dd["lot"]].get("_small") == did_:
                        bb = v["lots"][Dd["lot"]].get("_best_block")
                    blk = Dd["measured"][bb if bb is not None else i]
                    do = [float(logit(blk["rel_density"])), math.log10(blk["crack_density"] + 0.01),
                          blk.get("beta_prime", 0.0)]
                    rec = dict(do=do, comp=comp, fl=fl)
                    if isinstance(Dd.get("pip"), dict):
                        pm = Dd["pip"]
                        rec["pip"] = [pm["ys_MPa"] / 400, pm["uts_MPa"] / 600, pm["ue_pct"] / 30]
                        add("pip", np.concatenate([comp, do, [fl]]), rec["pip"])
                    if isinstance(Dd.get("screen"), dict):
                        sm = Dd["screen"]
                        rec["screen"] = [math.log(max(sm["early_rate_um_yr"], 0.05)), sm.get("Eb_mV", 0.0) / 500]
                        add("screen", np.concatenate([comp, do, [fl]]), rec["screen"])
                    small.setdefault(did, []).append(rec)
            for did_, Dd in v["deposits"].items():
                did = Dd["design"]
                if Dd["mode"] != "blown_large" or did not in small:
                    continue
                comp = v["designs"][did]
                for rec in small[did]:
                    if isinstance(Dd.get("tensile"), dict) and "pip" in rec:
                        add("tensile", np.array(rec["pip"] + rec["do"] + [rec["fl"]]),
                            [Dd["tensile"]["ys_MPa"] / 400, math.log(max(Dd["tensile"]["el_pct"], 0.3))])
                    if isinstance(Dd.get("immersion"), dict) and "screen" in rec:
                        x = np.array(rec["screen"] + [rec["do"][2], comp.get("Ni", 0) / 30, comp.get("Fe", 0) / 4.5,
                                                      comp.get("Al", 0) / 9.5, rec["fl"]])
                        im = Dd["immersion"]
                        add("immersion", x, [math.log(max(im["rate30_um_yr"], 0.05)), math.log(im["attack_um"] + 0.5)])
        return D

    @staticmethod
    def section_out(B):
        """EBSD on the polished section: log grain size and equiaxed share (the nucleants' signature)."""
        sc = B.get("section")
        if not isinstance(sc, dict):
            return None
        e = sc.get("ebsd") or {}
        if e.get("grain_um") is None:
            return None
        return [math.log(max(e["grain_um"], 0.3)), float(e.get("equiaxed_frac", 0.0))]

    def fit(self, v):
        D = self.datasets(v)
        for k, (X, Ys) in D.items():
            n = len(X)
            if self._fitted_at.get(k) == n:
                continue
            self._fitted_at[k] = n
            if n >= 3:
                Xa = np.array(X)
                for node, y in zip(self.nodes[k], Ys):
                    node.fit(Xa, np.array(y))

    def ready(self, k):
        return all(nd.ready() for nd in self.nodes[k])

    # ---------------------------------------------------------------- sampling the network
    def _samp(self, k, X, S):
        return [nd.sample(X, S, self.gen) for nd in self.nodes[k]]

    def utility_samples_al(self, comps, X_print, S, fixed_print=None, fixed_pip=None, fixed_section=None):
        """Utility draws (S, M) for candidates. fixed_print: (M, 2) measured print outputs; fixed_pip: (M, 3);
        fixed_section: (M, 2)."""
        M = len(comps)
        cf = np.array([al_cfactor(c) for c in comps])
        compf = np.array([_feat_comp(self.space, c) for c in comps])
        if fixed_print is None:
            y1, y2 = self._samp("print", X_print, S)
        else:
            y1 = np.broadcast_to(fixed_print[:, 0], (S, M))
            y2 = np.broadcast_to(fixed_print[:, 1], (S, M))
        dens, crack = sigm(y1), 10 ** y2 - 0.01
        CF = np.broadcast_to(compf, (S, M, compf.shape[1]))
        if fixed_section is None:
            if not self.ready("section"):
                return None
            g1, g2 = self._samp("section", np.concatenate([CF, y1[..., None], y2[..., None]], axis=2), S)
        else:
            g1, g2 = (np.broadcast_to(fixed_section[:, i], (S, M)) for i in range(2))
        if fixed_pip is None:
            if self.ready("pip"):
                Xp = np.concatenate([CF, y1[..., None], y2[..., None], g1[..., None], g2[..., None]], axis=2)
                p1, p2, p3 = self._samp("pip", Xp, S)
            else:
                return None
        else:
            p1, p2, p3 = (np.broadcast_to(fixed_pip[:, i], (S, M)) for i in range(3))
        if self.ready("test"):
            Xt = np.stack([p1, p2, p3, y1, y2, g1, g2], axis=2)
            t1, t2 = self._samp("test", Xt, S)
            ys, el = t1 * 400, np.exp(t2)
        else:                                       # before tensile data: read the PIP curve as the test
            ys, el = p1 * 400, np.maximum(p3 * 20 * 1.3, 0.2)
        return al_u(ys, el, cf[None, :], dens, crack)

    def utility_samples_cu(self, comps, X_ded, S, fixed_ded=None, fixed_pip=None, fixed_screen=None, fid=0.0):
        M = len(comps)
        FL = np.full((S, M, 1), float(fid))
        compf = np.array([_feat_comp(self.space, c) for c in comps])
        ni = np.array([c.get("Ni", 0.0) for c in comps])
        if fixed_ded is None:
            d1, d2, d3 = self._samp("ded", X_ded, S)
        else:
            d1, d2, d3 = (np.broadcast_to(fixed_ded[:, i], (S, M)) for i in range(3))
        dens, crack = sigm(d1), 10 ** d2 - 0.01
        Xn = np.concatenate([np.broadcast_to(compf, (S, M, compf.shape[1])), d1[..., None], d2[..., None],
                             d3[..., None], FL], axis=2)
        if fixed_pip is None:
            if not self.ready("pip"):
                return None
            p1, p2, p3 = self._samp("pip", Xn, S)
        else:
            p1, p2, p3 = (np.broadcast_to(fixed_pip[:, i], (S, M)) for i in range(3))
        if fixed_screen is None:
            if not self.ready("screen"):
                return None
            s1, s2 = self._samp("screen", Xn, S)
        else:
            s1, s2 = (np.broadcast_to(fixed_screen[:, i], (S, M)) for i in range(2))
        if self.ready("tensile"):
            t1, t2 = self._samp("tensile", np.concatenate([np.stack([p1, p2, p3, d1, d2, d3], axis=2), FL], axis=2), S)
            ys, el = t1 * 400, np.exp(t2)
        else:
            ys, el = p1 * 400, np.maximum(p3 * 30 * 1.2, 0.3)
        if self.ready("immersion"):
            fe = np.array([c.get("Fe", 0.0) / 4.5 for c in comps])
            al = np.array([c.get("Al", 0.0) / 9.5 for c in comps])
            Xi = np.concatenate([np.stack([s1, s2, d3, np.broadcast_to(ni / 30, (S, M)), np.broadcast_to(fe, (S, M)),
                                           np.broadcast_to(al, (S, M))], axis=2), FL], axis=2)
            i1, _ = self._samp("immersion", Xi, S)
            rate = np.exp(i1)
        else:
            rate = np.exp(s1) * 0.6               # before immersion data: the film halves the early rate (prior)
        return cu_u(ys, el, rate, ni[None, :], dens, crack)

    def best_obs(self, v):
        return max([u for _, u in self.observed(v)], default=0.0)

    # ---------------------------------------------------------------- proposing
    def best_proc_design(self, v):
        return P1.CostAware.best_proc(self, v)

    def p_sound(self, v, did, params_list, lot=None):
        """The print (or DED) node's probability that a part made at each setting is dense and crack-free."""
        from scipy.stats import norm
        sf = self.sim_of(v, did)
        node = "print" if self.al else "ded"
        if sf is None or not self.ready(node):
            return None
        comp = _feat_comp(self.space, v["designs"][did])
        pf = self.powder_feat(v, lot)
        extra = [] if self.al else [[getattr(self, "_fid", 0.0)]]
        X = np.array([np.concatenate([comp, sf, self.proc_vec(dict(v["design_inputs"][did], **p)), pf] + extra)
                      for p in params_list])
        (m1, s1), (m2, s2) = self.nodes[node][0].predict(X), self.nodes[node][1].predict(X)
        dens_t = float(logit(0.995 if self.al else 0.99))
        ps = norm.cdf((m1 - dens_t) / s1) * norm.cdf((math.log10(0.06) - m2) / s2)
        if not self.al:
            m3, s3 = self.nodes[node][2].predict(X)
            ps = ps * norm.cdf((0.3 - m3) / s3)
        return ps

    def _settings(self, v, lid, n_out, scale):
        L = v["lots"][lid]
        did = L["design"]
        base = self.best_proc_design(v)
        base.update({k: v["design_inputs"][did].get(k, base[k]) for k in ("superheat_K", "pour_mbar", "amplitude")})
        trial = [base, {k: v["design_inputs"][did].get(k, base[k]) for k in base}] + \
            [P1.perturb(self.space, base, self.gen, 0.25) for _ in range(126)]
        ps = self.p_sound(v, did, trial, lid)
        if ps is not None:
            base = trial[int(np.argmax(ps))]
        return [base] + [P1.perturb(self.space, base, self.gen, scale) for _ in range(n_out - 1)]

    def print_action(self, v, lid):
        return dict(kind="print", lot=lid, params=self._settings(v, lid, 9, 0.1), bars_at=0)

    def ded_params(self, v, lid):
        return self._settings(v, lid, 4, 0.15)

    def propose(self, v, n):
        self.advance2(v)
        acts = self.take(n)
        if len(acts) >= n:
            return acts[:n]
        if not hasattr(self, "seeds"):
            self.seeds = self.reference_seeds()
            sims = [dict(kind=self.sim_kind, design=d) for d in self.seeds]
            self._sims_req = len(sims)
            self.todo += [self.powder_action(d, v=v) for d in self.seeds]
            acts = (acts + sims)[:n]
            return acts + self.take(n - len(acts))
        self.fit(v)
        best = self.best_obs(v)
        options = []                                 # (score, action-or-callable)
        new_ok = self.can_start_new(v)
        if self.al:
            options += self.test_options(v, best)
        else:
            options += self.large_options(v, best)
        # keep the simulated pool topped up (the open CALPHAD node: $1 and minutes a design)
        simmed = {s["design"] for s in v["sims"] if s["kind"] == self.sim_kind}
        free = [d for d in simmed if d not in self.started]
        sim_acts = []
        in_flight = getattr(self, "_sims_req", 0) - len(simmed)
        if len(free) < 48 and in_flight < 24 and new_ok:
            pool = self.pool(v, 48, 48)
            sim_acts = [dict(kind=self.sim_kind, design=d) for d in pool[:self.N_POOL_SIM]]
        new = self.new_options(v, best, free) if new_ok else []
        options += new
        options.sort(key=lambda o: -o[0])
        picked_x = []
        for sc, act, x in options:
            if len(acts) >= n:
                break
            if act["kind"] == "powder":
                if x is not None and picked_x:
                    dmin = min(float(np.linalg.norm(x - p)) for p in picked_x)
                    if dmin < 0.08:
                        continue
                if x is not None:
                    picked_x.append(x)
                self.started.add(act.pop("_did"))
            elif act.get("_lot") is not None:
                L = v["lots"][act.pop("_lot")]
                self.go_large(v, L, act.pop("_lid"))
                acts += self.take(max(n - len(acts), 0))
                continue
            acts.append(act)
        if len(acts) < n:
            self.advance2(v)
            acts += self.take(n - len(acts))
        if len(acts) < n and sim_acts:
            take = sim_acts[: max(n - len(acts), 1)]
            self._sims_req = getattr(self, "_sims_req", 0) + len(take)
            acts += take
        return acts[:n]

    def new_options(self, v, best, free):
        if not free:
            return []
        comps = [v["designs"][d] for d in free]
        X = []
        bp = self.best_proc_design(v)
        for d in free:
            dsg = dict(v["design_inputs"][d], **{k: bp[k] for k in bp if k not in ("superheat_K", "pour_mbar",
                                                                                    "amplitude")})
            row = [_feat_comp(self.space, v["designs"][d]), self.sim_of(v, d), self.proc_vec(dsg), self.powder_feat(v)]
            if not self.al:
                row.append([0.0])
            X.append(np.concatenate(row))
        X = np.array(X)
        node = "print" if self.al else "ded"
        u = None
        if self.ready(node):
            u = self.utility_samples_al(comps, X, self.S) if self.al else self.utility_samples_cu(comps, X, self.S)
        cost = np.array([self.cost_new(v, v["design_inputs"][d]) for d in free])
        if u is None:
            # the network can't run yet: the metallurgist's proxy and the screen as a prior (as CostAware does)
            outs = {s["design"]: s["out"] for s in v["sims"] if s["kind"] == self.sim_kind}
            pr = np.array([P1.Tiered.proxy(self, v["designs"][d], outs[d]) for d in free])
            ok = np.array([1.0 if P1.Tiered.passes(self, outs[d], v["designs"][d]) else 0.0 for d in free])
            pr = (pr - pr.mean()) / (pr.std() + 1e-9)
            score = np.exp(pr) * (0.3 + ok) * (0.5 + self.gen.random(len(free))) / cost
            score = score / score.max() * 1e-9          # below any network-based option
        else:
            score = np.maximum(u - best, 0).mean(axis=0) / cost
        out = []
        for j in np.argsort(-score)[:16]:
            d = free[j]
            a = self.powder_action(self.atomizer_settings(v, d, dict(v["design_inputs"][d])), v=v)
            a["_did"] = d
            out.append((float(score[j]), a, _feat_comp(self.space, v["designs"][d])))
        return out

    def test_options(self, v, best):
        """FLAIME: PIP'd sound builds waiting on the decision to machine and pull bars."""
        out = []
        cost = 340.0
        for bid, B in v["builds"].items():
            if not B.get("_await_pip") or not isinstance(B.get("pip"), dict) or B.get("_decided") \
                    or self.section_out(B) is None:
                continue
            pm, mb = B["pip"], B["measured"][B["bars_at"]]
            comp = v["designs"][B["design"]]
            fp = np.array([[float(logit(mb["rel_density"])), math.log10(mb["crack_density"] + 0.01)]])
            fpip = np.array([[pm["ys_MPa"] / 400, pm["uts_MPa"] / 500, pm["ue_pct"] / 20]])
            fsec = np.array([self.section_out(B)])
            u = self.utility_samples_al([comp], None, self.S, fixed_print=fp, fixed_pip=fpip, fixed_section=fsec)
            n_tests = len(self.datasets_cache_n("test", v))
            if u is None or n_tests < 6:
                sc = 1.0                                  # learn the PIP-to-tensile link first
            else:
                sc = float(np.maximum(u - best, 0).mean()) / cost
                if float(u.mean()) >= 0.9 * best and best > 0:
                    sc = max(sc, 1e-3)
            B["_decided_score"] = sc
            out.append((sc, _Decide(B, dict(kind="test", build=bid)), None))
        return out

    def datasets_cache_n(self, k, v):
        return [1] * self._fitted_at.get(k, 0)

    def large_options(self, v, best):
        """Copper: screened small deposits waiting on the decision to make a 1 kg deposit for bars and immersion."""
        out = []
        for lid, L in v["lots"].items():
            if L.get("_stage") != "screening":
                continue
            Dd = v["deposits"].get(L.get("_small"))
            if Dd is None or not isinstance(Dd.get("pip"), dict) or not isinstance(Dd.get("screen"), dict):
                continue
            comp = v["designs"][L["design"]]
            blk = Dd["measured"][L.get("_best_block", 0)]
            fd = np.array([[float(logit(blk["rel_density"])), math.log10(blk["crack_density"] + 0.01),
                            blk.get("beta_prime", 0.0)]])
            pm, sm = Dd["pip"], Dd["screen"]
            fp = np.array([[pm["ys_MPa"] / 400, pm["uts_MPa"] / 600, pm["ue_pct"] / 30]])
            fs = np.array([[math.log(max(sm["early_rate_um_yr"], 0.05)), sm.get("Eb_mV", 0.0) / 500]])
            u = self.utility_samples_cu([comp], None, self.S, fixed_ded=fd, fixed_pip=fp, fixed_screen=fs, fid=0.0)
            n_large = self._fitted_at.get("tensile", 0)
            runs = max(int(math.ceil((v.get("large_g", 2000) - L["remaining_g"]) / self.cut_per_run(L) * 1.15)), 0)
            cost = 450.0 + runs * 700.0
            if u is None or n_large < 4:
                sc = 1.0
            else:
                sc = float(np.maximum(u - best, 0).mean()) / cost
                if float(u.mean()) >= 0.9 * best and best > 0:
                    sc = max(sc, 1e-3)
            out.append((sc, _GoLarge(L, lid), None))
        return out


class _Decide(dict):
    """A deferred downstream action: marks its artifact as decided when it is taken."""

    def __init__(self, B, act):
        super().__init__(act)
        self._B = B

    def pop(self, k, *a):
        return super().pop(k, *a)

    def __getitem__(self, k):
        if k == "kind":
            self._B["_decided"] = True
        return super().__getitem__(k)


class _GoLarge(dict):
    def __init__(self, L, lid):
        super().__init__(kind="go_large", _lot=L["id"], _lid=lid)
        self._L = L


class BOFNSAAS(BOFN):
    """BOFN with the SAAS prior (MAP) on the high-dimensional nodes (print / ded, pip, screen)."""
    name = "bofn_saas"
    node_kind = "saas_map"


POLICIES2 = {"sobol": Sobol, "heuristic": Heuristic, "gpbo": GPBO, "saasbo": SAASBO, "saasmap": SAASMAP,
             "bofn": BOFN, "bofn_saas": BOFNSAAS}


def make(name, key, seed, crucible=None):
    if name in POLICIES2:
        return POLICIES2[name](key, seed, crucible)
    return P1.POLICIES[name](key, seed)


class BOFNBlend(BOFN):
    """Copper: BOFN that screens each new composition as a blended-powder DED block (no atomizer: about $250 with
    PIP and the CubXL screen), and atomizes only the compositions whose screened network posterior is worth it,
    straight to the 1 kg deposit for bars and immersion. The network's DED, PIP and screen nodes take a fidelity
    flag (blend or atomized), so the blend's bias is learned, not assumed. FLAIME runs plain BOFN."""
    name = "bofn_blend"

    def __init__(self, key, seed=0, crucible=None):
        super().__init__(key, seed, crucible)
        self.blend_state = {}            # design id -> 'blending' | 'screening' | 'promoted' | 'dropped'
        self.blend_dep = {}              # design id -> blend deposit id

    def advance2(self, v):
        if self.al:
            return super().advance2(v)
        # an atomized lot of a promoted composition goes straight to the 1 kg deposit (no small deposit first)
        for lid, L in v["lots"].items():
            if self.blend_state.get(L["design"]) == "promoted" and L.get("_stage", "new") == "new":
                D = v["deposits"][self.blend_dep[L["design"]]]
                L["_best_params"], L["_small"] = D["_best_params"], None
                self.go_large(v, L, lid)
        acts = super().advance2(v)
        for did_, D in v["deposits"].items():
            if D["mode"] != "blend" or D.get("_seen"):
                continue
            D["_seen"] = True
            ok = [(i, m) for i, m in enumerate(D["measured"]) if m["rel_density"] >= 0.96 and m["crack_density"] < 0.3]
            if not ok:
                self.blend_state[D["design"]] = "dropped"
                continue
            i, best = max(ok, key=lambda im: im[1]["rel_density"] - im[1].get("beta_prime", 0) * 0.05)
            D["_best_block"], D["_best_params"] = i, best["params"]
            self.blend_state[D["design"]] = "screening"
            self.blend_dep[D["design"]] = did_
            acts += [dict(kind="pip", deposit=did_, block=i), dict(kind="screen", deposit=did_, block=i)]
        return acts

    def promote_options(self, v, best):
        out = []
        for did, st in self.blend_state.items():
            if st != "screening":
                continue
            D = v["deposits"].get(self.blend_dep.get(did))
            if D is None or not isinstance(D.get("pip"), dict) or not isinstance(D.get("screen"), dict):
                continue
            comp = v["designs"][did]
            blk = D["measured"][D["_best_block"]]
            fd = np.array([[float(logit(blk["rel_density"])), math.log10(blk["crack_density"] + 0.01),
                            blk.get("beta_prime", 0.0)]])
            pm, sm = D["pip"], D["screen"]
            fp = np.array([[pm["ys_MPa"] / 400, pm["uts_MPa"] / 600, pm["ue_pct"] / 30]])
            fs = np.array([[math.log(max(sm["early_rate_um_yr"], 0.05)), sm.get("Eb_mV", 0.0) / 500]])
            u = self.utility_samples_cu([comp], None, self.S, fixed_ded=fd, fixed_pip=fp, fixed_screen=fs, fid=1.0)
            cost = self.cost_new(v, v["design_inputs"][did])
            if u is None or self._fitted_at.get("tensile", 0) < 4:
                # no atomized results to calibrate the blend against yet: promote the best-looking blends
                est = float(cu_u(pm["ys_MPa"], pm["ue_pct"] * 1.2, 0.6 * sm["early_rate_um_yr"], comp.get("Ni", 0),
                                 sigm(fd[0, 0]), 10 ** fd[0, 1] - 0.01))
                sc = 1.0 + est if est >= max(0.3, 0.8 * best) else est * 1e-6
            else:
                sc = float(np.maximum(u - best, 0).mean()) / cost
            out.append((sc, _Promote(self, did, v), None))
        return out

    def new_options(self, v, best, free):
        if self.al:
            return super().new_options(v, best, free)
        free = [d for d in free if d not in self.blend_state]
        opts = super().new_options(v, best, free)
        out = []
        for sc, a, x in opts:
            did = a.pop("_did")
            self._fid = 1.0
            params = self._settings_design(v, did, 4, 0.15)
            self._fid = 0.0
            b = dict(kind="blend_ded", design=dict(v["design_inputs"][did]), params=params, _did=did)
            out.append((sc * 3.0, b, x))          # a blend screen costs about a tenth of an atomized trial
        return out

    def _settings_design(self, v, did, n_out, scale):
        base = self.best_proc_design(v)
        trial = [base] + [P1.perturb(self.space, base, self.gen, 0.25) for _ in range(63)]
        ps = self.p_sound(v, did, trial, None)
        if ps is not None:
            base = trial[int(np.argmax(ps))]
        return [base] + [P1.perturb(self.space, base, self.gen, scale) for _ in range(n_out - 1)]

    def propose(self, v, n):
        if self.al:
            return super().propose(v, n)
        acts = super().propose(v, n)
        # promotions compete with the rest only for slots left over
        if len(acts) < n and self.can_start_new(v):
            best = self.best_obs(v)
            for sc, act, _ in sorted(self.promote_options(v, best), key=lambda o: -o[0]):
                if len(acts) >= n or sc <= 1e-9:
                    break
                acts.append(act.take())
        for a in acts:
            if a.get("kind") == "blend_ded":
                self.blend_state[a.pop("_did")] = "blending"
        return acts


class _Promote:
    def __init__(self, pol, did, v):
        self.pol, self.did, self.v = pol, did, v

    def take(self):
        pol, v, did = self.pol, self.v, self.did
        pol.blend_state[did] = "promoted"
        cpr = 430.0 * (1.75 if (pol.crucible or v.get("crucible_cm3", 225)) >= 400 else 1.0)
        runs = int(math.ceil(v.get("large_g", 1000.0) * 1.15 / cpr))
        d = pol.atomizer_settings(v, did, dict(v["design_inputs"][did]))
        pol.started.add(did)
        return pol.powder_action(d, runs=runs, v=v)


POLICIES2["bofn_blend"] = BOFNBlend
