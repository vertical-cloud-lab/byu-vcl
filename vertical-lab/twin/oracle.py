"""What the truth says, with no lab in the way: the reference alloys' true utilities (the benchmark's state of the
art and target), the distribution over the search space, the best designs a large search finds, and how well the
cheap screens rank designs (the copper investigation).

    python3 -m twin.oracle          # -> out/twin2/oracle.json

A design's true utility here is the campaign's own score (``Campaign._al_score`` / ``_cu_check``) of a part made
from a lot atomized at the true liquidus, at the best of a set of process settings: what a lab that had already
tuned the process would see. The truth's seed is 0 (the benchmark varies it per run; the landscape's random field
moves a few percent).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from twin import campaign as C
from twin import policies as P1
from twin import spaces, supply, truth_al, truth_cu, usgs
from twin.facility import Facility

OUT = Path(__file__).resolve().parent.parent / "out" / "twin2"


def _camp(key, seed=0):
    m = supply.Market("calm", 0, 400)
    return C.Campaign(C.Spec(key, 1e9, 1, seed), None, m, Facility("vertical_lab", 0, 24 * 400), 24 * 400)


def true_utility(camp, design, procs, rng, mode="blown_large"):
    """Best true utility over the process settings ``procs`` (list of dicts), and the details at the best."""
    sp, t = camp.space, camp.truth
    comp = sp.composition(design)
    TL = t.thermo(comp)["T_liquidus_C"] if camp.key == "flaime_al" else t.thermo(comp)["liquidus_C"]
    best = (-1.0, None)
    for proc in procs:
        p = dict(design)
        p.update(proc)
        run = t.atomize(comp, {k: p[k] for k in ("superheat_K", "pour_mbar", "amplitude")}, TL, rng)
        lot = dict(composition=run["composition"], oxygen_ppm=run["oxygen_ppm"], satellite_frac=run["satellite_frac"],
                   carbon_ppm=run.get("carbon_ppm", 30.0))
        if camp.key == "flaime_al":
            part = t.build(lot, p, rng)
            u, det = camp._al_score(part, t.strength(part), None)
        else:
            part = t.deposit(lot, p, mode, rng)
            s, c = t.strength(part), t.corrosion(part)
            ref = camp._cu_ref_rate()
            ni = part["composition"].get("Ni", 0.0)
            feas = part["rel_density"] >= 0.99 and part["crack_free"]
            d = [C._desir(s["ys_MPa"], 100, 400), C._desir(s["el_pct"], 5, 35),
                 C._desir(3.0 * ref - c["rate_um_yr"], 0, 2.5 * ref), C._desir(30 - ni, 0, 30)]
            u = float(np.prod(d) ** 0.25) * (1.0 if feas else 0.0)
            det = dict(ys=s["ys_MPa"], el=s["el_pct"], rate=c["rate_um_yr"], attack=c["attack_um"], ni=ni,
                       feasible=bool(feas))
        if u > best[0]:
            best = (u, dict(det, proc=proc))
    return best


def proc_grid(key, n, rng):
    sp = spaces.SPACES[key]
    base = dict(P1.AL_PROC if key == "flaime_al" else P1.CU_PROC)
    out = [base]
    for _ in range(n - 1):
        d = dict(base)
        for v in sp.process:
            if v.name in ("superheat_K", "pour_mbar", "amplitude"):
                continue
            d[v.name] = float(v.from_unit(rng.random()))
        out.append(d)
    return out


def main(n_random=3000, n_proc=24, n_refine=40, seed=0):
    out = {}
    for key in ("flaime_al", "onr_cu"):
        camp = _camp(key, seed)
        sp = camp.space
        rng = np.random.default_rng(1)
        procs = proc_grid(key, n_proc, rng)
        refs = {}
        for name, wt in spaces.REFERENCE[key].items():
            d = {e: wt.get(e, 0.0) for e in sp.elements}
            u, det = true_utility(camp, d, procs, np.random.default_rng(2))
            refs[name] = dict(utility=round(u, 4), **{k: (round(v, 3) if isinstance(v, float) else v)
                                                      for k, v in det.items() if k != "proc"})
        sota_name = max(refs, key=lambda k: refs[k]["utility"])
        # the landscape: random designs at the default process, then the best re-tuned and searched locally
        ds = sp.sample(n_random, seed=7)
        base = [procs[0]]
        us = np.array([true_utility(camp, d, base, np.random.default_rng(3))[0] for d in ds])
        top = np.argsort(-us)[:n_refine]
        best_u, best_d = -1, None
        for j in top:
            u, det = true_utility(camp, ds[j], procs, np.random.default_rng(4))
            if u > best_u:
                best_u, best_d = u, (ds[j], det)
        # local search from the best (an oracle's hill climb on the truth: an upper reference, not a lab)
        cur, cur_u = dict(best_d[0]), best_u
        r = np.random.default_rng(5)
        for it in range(300):
            uvec = sp.encode(cur)
            ne = len(sp.elements)
            uvec[:ne] = np.clip(uvec[:ne] + r.normal(0, 0.05, ne) * (r.random(ne) < 0.3), 0, 1)
            cand = sp.decode(uvec)
            if sp.check(cand):
                continue
            u, det = true_utility(camp, cand, procs[:8], np.random.default_rng(6))
            if u > cur_u:
                cur, cur_u, best_d = cand, u, (cand, det)
        # how the round-1 screen ranks designs (the Tiered policy's proxy on the open CALPHAD node)
        pol = P1.Tiered(key, 0)
        pr, ok = [], []
        for d in ds[:1500]:
            comp = sp.composition(d)
            o = camp.truth.sim_open(comp)
            pr.append(pol.proxy(comp, o))
            ok.append(pol.passes(o, comp))
        pr, ok = np.array(pr), np.array(ok)
        u15 = us[:1500]
        from scipy.stats import spearmanr
        rho = float(spearmanr(pr[u15 > 0], u15[u15 > 0]).correlation) if (u15 > 0).sum() > 5 else float("nan")
        prec = float((u15[ok] > 0).mean()) if ok.any() else float("nan")
        out[key] = dict(
            references=refs, sota=sota_name, sota_utility=refs[sota_name]["utility"],
            random_default_process=dict(n=len(us), frac_positive=float((us > 0).mean()),
                                        q50=float(np.quantile(us, 0.5)), q90=float(np.quantile(us, 0.9)),
                                        q99=float(np.quantile(us, 0.99)), max=float(us.max()),
                                        frac_above_sota=float((us >= refs[sota_name]["utility"]).mean())),
            best_found=dict(utility=round(cur_u, 4),
                            composition={e: round(v, 3) for e, v in sp.composition(cur).items() if v > 0},
                            details={k: (round(v, 3) if isinstance(v, float) else v) for k, v in best_d[1].items()
                                     if k != "proc"}),
            screen=dict(spearman_proxy_vs_utility_among_feasible=rho, screen_pass_frac=float(ok.mean()),
                        precision_of_screen=prec, base_rate=float((u15 > 0).mean())))
        print(key, json.dumps({k: out[key][k] for k in ("sota", "sota_utility", "best_found")})[:400], flush=True)
        print("   refs", {k: v["utility"] for k, v in refs.items()}, "random", out[key]["random_default_process"],
              "screen", out[key]["screen"], flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "oracle.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    main()
