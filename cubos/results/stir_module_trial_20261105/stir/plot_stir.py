"""Plot the stir after stir_module_trial (2026-11-05 22:55 UTC) against the 11-05 22:28 run.

usage: plot_stir.py   (run from this folder; reads trial_stir.jsonl and
                       ../../stirrer_spacer_20261105/washers3_1105.jsonl; writes rpm_duty_trial.png)

`rpm` is Hall pulses counted over 2 s, so it moves in 30 rpm steps. The reference is the 11-05
22:28 run with the same spacer + 3 washers, from its 30,600 step (it was already turning at 300).
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, INK, INK2, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"


def secs(hms):
    h, m, s = hms.rstrip("Z").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def load(path, start_cmd):
    recs = [json.loads(l) for l in open(path)]
    t0 = next(secs(r["utc"]) for r in recs if r.get("cmd", "").startswith(start_cmd))
    out = [(secs(r["utc"]) - t0, r["rpm"], r["duty"], r["setpoint"]) for r in recs
           if "duty" in r and secs(r["utc"]) >= t0]
    return out


today = load("trial_stir.jsonl", "30,600")
ref = [s for s in load("../../stirrer_spacer_20261105/washers3_1105.jsonl", "30,600") if s[0] <= 20]

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, (a_rpm, a_duty) = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True,
                                    gridspec_kw={"height_ratios": [1.6, 1], "hspace": 0.1})
a_rpm.step([s[0] for s in today], [s[3] for s in today], where="post", color=MUTED, lw=1.5, ls="--",
           label="setpoint (firmware ramp to 600)")
a_rpm.step([s[0] for s in ref], [s[1] for s in ref], where="post", color=BLUE, lw=1.5, alpha=0.35,
           label="Hall rpm, 11-05 22:30 (same spacer, before the protocol)")
a_rpm.step([s[0] for s in today], [s[1] for s in today], where="post", color=BLUE, lw=2.2,
           label="Hall rpm, after the protocol (22:55)")
a_duty.step([s[0] for s in ref], [s[2] for s in ref], where="post", color=ORANGE, lw=1.5, alpha=0.35)
a_duty.step([s[0] for s in today], [s[2] for s in today], where="post", color=ORANGE, lw=2.2)
a_rpm.set_ylim(-30, 700)
a_duty.set_ylim(0, 1.05)
a_duty.set_xlim(-1, 66)
a_rpm.set_ylabel("rpm (Hall, per 2 s)")
a_duty.set_ylabel("PWM duty")
a_duty.set_xlabel("seconds after 30,600")
for ax in (a_rpm, a_duty):
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)
a_rpm.legend(loc="upper right", frameon=False, fontsize=8.5)
a_rpm.set_title("Vial 1 stirred at 600 rpm for 60 s after stir_module_trial: it reached 540 rpm at 15 s, "
                "then turned in bursts", fontsize=10.5, loc="left")
fig.savefig("rpm_duty_trial.png", dpi=110, bbox_inches="tight", facecolor="white")
