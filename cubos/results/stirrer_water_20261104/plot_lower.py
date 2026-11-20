"""rpm (Hall) and duty through the 23:32 run: fan started with the vial out, vial lowered in.

usage: plot_lower.py   (reads lower_1104.jsonl, writes rpm_lower_1104.png)
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

recs = [json.loads(l) for l in open("lower_1104.jsonl")]
step = next(r for r in recs if r.get("event") == "step")
stop = next(r for r in recs if r.get("event") == "stop")
secs = lambda u: sum(float(x) * m for x, m in zip(u.rstrip("Z").split(":"), (3600, 60, 1)))
t0 = secs(step["utc"])
pts = [(secs(r["utc"]) - t0, r["rpm"], r["duty"]) for r in recs if "rpm" in r]
t, rpm, duty = zip(*pts)
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.step(t, rpm, where="post", color="#d1495b", lw=1.4, label="Hall rpm (pulses over the last 2 s)")
ax.axhline(300, color="#d1495b", lw=0.8, ls=":")
ax.set_xlabel("s after 30,300 (23:32:13.8 UTC)")
ax.set_ylabel("rpm from the Hall sensor", color="#d1495b")
ax.axvline(secs(stop["utc"]) - t0, color="black", lw=0.8, ls="--")
ax.text(secs(stop["utc"]) - t0 + 0.5, 760, "30,0", fontsize=8)
ax2 = ax.twinx()
ax2.step(t, duty, where="post", color="#00798c", lw=1.2, label="duty")
ax2.set_ylabel("duty", color="#00798c")
ax2.set_ylim(0, 1)
ax.set_ylim(0, 900)
ax.set_title("2026-11-04 23:32, 300 rpm asked: started with the vial out; the vial went in at +2 to +6 s", fontsize=10)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig("rpm_lower_1104.png", dpi=130)
