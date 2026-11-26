"""Common seed sets: the designs every policy starts from, so that a policy's lead is not only a warm start.

DAL #275 ("Initialization trials (seeding data) for BOFN") recommends a three-way mix, about 6-7 seeds rather than
3 + 3 + 3 (its ledger: D1, D2, B30, B15, S1, S2, S3), and the same seeds for every policy in a benchmark (its Edison q1: otherwise "the AI policy's advantage is
only a warm start"):

* known baselines (the alloys to beat),
* agent picks (from the literature and databases, chosen by an agent with Edison),
* space-filling picks (IMSE: greedy integrated-variance reduction on the CALPHAD-screened pool; #275 found it covered
  better than plain Sobol or maximin, which picked corners).

``seeds(name, campaign)`` -> [(label, composition wt% without the base element)]. ``policies2.make(...,
seeding=name)`` adds each policy's default process settings and projects each seed onto the campaign's design box.

    python -m twin.seeding            # print both sets, and the twin's own IMSE pick for each campaign
"""
from __future__ import annotations

import numpy as np

# DAL #275's plan (bofn-seeding/README.md L52-L66 and L139-L150, seeds.csv, at DAL ce39407 on branch
# claude/issue-275-20261120-1832): D1 and D2 are the baselines, B30 and B15 the dosing checks (4047 powder in 6063
# cups: does the measured Si follow the charge?), S1 and S2 the agent's literature picks, S3 the IMSE pick; seven
# seeds, with #275's S4 left to the optimizer (its first pick). S2 is over the FLAIME box for Fe (cap 0.5 wt%) and Zr
# (cap 1.0 wt%), as #275 itself notes ("over the PR #72 caps for both"); the twin projects it onto the box, so it runs
# as Al-0.5Fe-1.02Mg-1.0Zr.
DAL275 = {
    "flaime_al": [
        ("D1 baseline: Al-10Si-0.35Mg (the alloy to beat)", {"Si": 10.0, "Mg": 0.35}),
        ("D2 baseline: Al-4.5Mg-0.7Sc-0.3Zr (Scalmalloy-type)", {"Mg": 4.5, "Sc": 0.7, "Zr": 0.3}),
        ("B30 dosing check: 30 % 4047 powder in 6063 cups, Al-3.9Si-0.5Mg", {"Si": 3.9, "Mg": 0.5}),
        ("B15 dosing check: 15 % 4047 powder in 6063 cups, Al-2.1Si-0.6Mg", {"Si": 2.1, "Mg": 0.6}),
        ("S1 agent pick: Al-4Mn-0.5Ti-0.5Zr (Mair et al.; Sc-free)", {"Mn": 4.0, "Ti": 0.5, "Zr": 0.5}),
        ("S2 agent pick: Al-1.87Fe-1.02Mg-1.03Zr (Li et al.; projected onto the box)",
         {"Fe": 1.87, "Mg": 1.02, "Zr": 1.03}),
        ("S3 space-filling: Al-3.2Mn-1.5Cr (IMSE on DAL's CALPHAD-screened pool)", {"Mn": 3.2, "Cr": 1.5}),
    ],
    # #275 plans the aluminium campaign only. The copper set follows the same three-way recipe: the ONR proposal's
    # two references as baselines, two agent picks from the literature DAL's Edison runs cite (see COPPER_SOURCES),
    # and the twin's own IMSE pick on its open-CALPHAD-screened pool (imse_pick below; fixed here so the set does not
    # move with code changes).
    "onr_cu": [
        ("D1 baseline: C70600 90-10 Cu-Ni", {"Ni": 10.0, "Fe": 1.4, "Mn": 0.8}),
        ("D2 baseline: C95800 nickel-aluminium bronze", {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}),
        ("S1 agent pick: C71640 Cu-30Ni-2Fe-2Mn (erosion-resistant Cu-Ni for seawater)",
         {"Ni": 30.0, "Fe": 2.0, "Mn": 2.0}),
        ("S2 agent pick: C63000 Cu-10Al-5Ni-3Fe (wrought NAB; Al projected to the box)",
         {"Al": 10.0, "Ni": 5.0, "Fe": 3.0}),
        ("S3 space-filling: Cu-0.73Al-0.07Ni (the twin's IMSE pick on 1,249 screened designs, after D1-S2)",
         {"Ni": 0.07, "Al": 0.73}),
    ],
}
COPPER_SOURCES = {
    "C71640": "ASM/CDA: Cu-30Ni-2Fe-2Mn, the 70-30 variant with more Fe and Mn for erosion resistance in seawater",
    "C63000": "ASM/CDA: Cu-10Al-5Ni-3Fe, the wrought nickel-aluminium bronze",
}
SETS = {"dal275": DAL275}


def seeds(name: str, campaign: str) -> list:
    return list(SETS[name][campaign])


def imse_pick(campaign: str, existing: list, n_pool: int = 2048, lengthscale: float = 0.35, seed: int = 0):
    """The candidate that most lowers the GP's mean posterior variance over the CALPHAD-screened pool (greedy IMSE,
    as DAL #275's seed_design.py --method imse), given the seeds already chosen. Compositions only, scaled to the
    box; a squared-exponential kernel. Returns (composition, mean variance before, after)."""
    from twin import spaces
    from twin import policies as P1
    from twin import truth_al, truth_cu
    sp = spaces.SPACES[campaign]
    truth = truth_al.AlTruth(0) if campaign == "flaime_al" else truth_cu.CuTruth(0)
    tier = P1.Tiered(campaign, 0)
    pool = []
    for d in sp.sample(n_pool, seed=seed, kind="sobol"):
        comp = sp.composition(d)
        out = truth.sim_open(comp)
        if P1.Tiered.passes(tier, out, comp):
            pool.append(d)
    enc = lambda d: np.array([d.get(e, 0.0) / sp.bounds[e][1] for e in sp.elements])
    P = np.array([enc(d) for d in pool])
    S = np.array([enc(sp.repair({**{e: 0.0 for e in sp.elements}, **c})) for c in existing])

    def k(A, B):
        d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
        return np.exp(-0.5 * d2 / lengthscale ** 2)

    def mean_var(Sx):
        K = k(Sx, Sx) + 1e-6 * np.eye(len(Sx))
        kp = k(P, Sx)
        return float(np.mean(1.0 - np.einsum("ij,ij->i", kp @ np.linalg.inv(K), kp)))

    before = mean_var(S)
    scores = [mean_var(np.vstack([S, P[i:i + 1]])) for i in range(len(P))]
    j = int(np.argmin(scores))
    comp = {e: round(float(pool[j][e]), 2) for e in sp.elements if pool[j][e] > 0}
    return comp, before, scores[j], len(pool)


if __name__ == "__main__":
    for camp in ("flaime_al", "onr_cu"):
        print(camp)
        for lab, c in seeds("dal275", camp):
            print("  ", lab, c)
        comp, b, a, n = imse_pick(camp, [c for _, c in seeds("dal275", camp)[:4]])
        print(f"   twin's IMSE pick after D1, D2, S1, S2 on {n} screened designs: {comp} (mean variance {b:.3f} -> {a:.3f})")
