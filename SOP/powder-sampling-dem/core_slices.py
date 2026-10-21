"""Score the tube cores as if they were sliced into thirds inside the tube, instead of laid out.

    python core_slices.py open_tube piston

Reads the raw trajectory ($DEM_OUT/<name>.npz) and adds "sliced_in_tube" to results/<name>.json:
the core split into thirds by height, just before it was pushed out over the tray.
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("DEM_OUT", "/tmp/dem-out")
RES = os.path.join(HERE, "results")


def main(name):
    d = np.load(os.path.join(OUT, f"{name}.npz"))
    extra = json.loads(str(d["extra"]))
    core = np.array(extra["core"])
    cap = [str(c) for c in d["caption"]]
    k = max(i for i, c in enumerate(cap) if c == "lower to just above the tray")
    alive = d["M"][k, core] != 1
    core = core[alive]
    order = core[np.argsort(d["X"][k, core, 2])]
    g, lab = d["group"], d["label"]
    names = ["bottom slice", "middle slice", "top slice"]
    sliced = []
    for nm, th in zip(names, np.array_split(order, 3)):
        sliced.append(dict(name=nm, n=int(len(th)), counts=np.bincount(g[th], minlength=4).tolist(),
                           mean_label=float(lab[th].mean())))
    p = os.path.join(RES, f"{name}.json")
    r = json.load(open(p))
    r["sliced_in_tube"] = sliced
    json.dump(r, open(p, "w"), indent=2)
    for s in sliced:
        print(name, s["name"], s["n"], s["counts"], round(s["mean_label"], 3))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        main(n)
