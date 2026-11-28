import os, sys, time, json
os.environ["TWIN6_DAYS"] = sys.argv[1]
os.environ.setdefault("TWIN6_OUT", "/tmp/twin6speed")
sys.path.insert(0, "/tmp/wt6c/vertical-lab")
from twin import bench6 as B6
from twin.opt import net6, net3, policies2
if sys.argv[2] == "old":                    # round 5's search: one prediction per candidate, features from the design
    del net6._Six.atomizer_settings
    del net6._Six._p_powder
t = time.time()
cfg = B6._cfg("vertical", "parallel", "bofn3", "reorder", 0, hpc=dict(scale=1))
out, tw = B6.simulate(cfg)
print(json.dumps(dict(mode=sys.argv[2], seconds=round(time.time() - t, 1), fits=out["gp"]["fits"],
                      T={k: [round(d["t_h"], 2) for d in c["demonstrated"]][:4] for k, c in out["campaigns"].items()},
                      n_lots={k: c["n_lots"] for k, c in out["campaigns"].items()})))
