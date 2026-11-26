"""Round 3's economics: round 2's model (twin/econ.py, notes/twin_econ.md) on round 3's runs.

    python3 -m twin.econ3 [NEW_POLICY]     # -> out/twin3/econ/econ_summary.json and figures

The vertical lab (one year, stocked, BOFN or pKGFN on the asynchronous engine) against the conventional lab (three
years at three years' money, metal ordered as each charge needs it, the same asynchronous freedom inside its own
facilities and booking rules). Prices, capex, fixed costs and the outside-work model are round 2's, unchanged.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

from twin import bench2 as B2
from twin import bench3 as B3
from twin import econ as E

OUT = B3.OUT / "econ"


def run(new_pol: str = "pkgfn3", n_boot: int = 1000) -> dict:
    paths = [p for p in (B3.RUNS / "main.jsonl", B3.RUNS / "conventional.jsonl") if p.exists()]
    evs = sorted(glob.glob(str(B3.OUT / "events" / "*.json")))
    G = E.group_runs(E.load_runs(paths))
    V = lambda p: ("vertical_lab", p, "historical", "")
    Cv = lambda p: ("proposed", p, "historical", "stock-lean")
    pairs = [(new_pol, new_pol), ("heuristic", new_pol), ("sobol", new_pol), ("tiered", new_pol),
             ("heuristic", "heuristic"), ("tiered", "tiered")]
    comps = [(Cv(r), V(n)) for r, n in pairs if Cv(r) in G and V(n) in G]
    T = B2.targets()
    S = E.report(runs_paths=paths, events_paths=evs, validate_path=None, out=OUT, n_boot=n_boot, comparisons=comps,
                 targets=dict(T["T1"]), new_pol=new_pol)
    # time to the halfway target (T2) as well, from the same curves (round 3's headline is days to T1 and T2)
    from twin import accel as AC
    S["acceleration_T2"] = {}
    for rk, nk in comps:
        name = f"vertical lab + {nk[1]} vs conventional + {rk[1]}"
        S["acceleration_T2"][name] = {}
        for camp in ("flaime_al", "onr_cu"):
            a = AC.acceleration_factor(AC.curves_of(G[rk], camp), AC.curves_of(G[nk], camp), T["T2"][camp], "days",
                                       n_boot=n_boot)
            S["acceleration_T2"][name][camp] = {k: a.get(k) for k in ("af", "lo", "hi", "hit_ref", "hit_new",
                                                                      "af_bound", "bound_kind", "median_ref", "median_new")}
    (OUT / "econ_summary.json").write_text(json.dumps(E._clean(S), indent=1, default=str))
    return S


if __name__ == "__main__":
    S = run(sys.argv[1] if len(sys.argv) > 1 else "pkgfn3")
    print("\n".join(S.get("headline", [])))
