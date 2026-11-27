import os, sys, time, json
os.environ["TWIN6_DAYS"] = sys.argv[1]
os.environ.setdefault("TWIN6_OUT", "/tmp/twin6cbwr")
sys.path.insert(0, "/tmp/wt6c/vertical-lab")
from twin import bench6 as B6
cfg = B6._cfg(sys.argv[2], "parallel" if sys.argv[2] == "vertical" else "external", "bofn3", "reorder", 0, hpc=dict(scale=1))
t = time.time(); out, tw = B6.simulate(cfg)
print(json.dumps(dict(cbwr=os.environ.get("MKL_CBWR"), seconds=round(time.time() - t, 1), fits=out["gp"],
                      T={k: [d["t_h"] for d in c["demonstrated"]][:3] for k, c in out["campaigns"].items()},
                      mkl=out["env"].get("mkl"))))
