"""Plot the three 2026-11-05 runs: Hall rpm and duty against time, one column per vial height.

usage: plot_runs.py    (reads spacer_1105.jsonl, washers_1105.jsonl, washers3_1105.jsonl;
                        writes rpm_duty_1105.png)

Time is seconds after each run's first command. `rpm` is Hall pulses counted over 2 s, so it
moves in 30 rpm steps. Grey bands are where the fan was told to stop (30,0); x marks a status
reply with `stalled` newly set, where the firmware gave up after six empty 2 s windows.
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS = [("spacer_1105", "Spacer alone (22:12 UTC)"),
        ("washers_1105", "Spacer + 2 washers (22:21 UTC)"),
        ("washers3_1105", "Spacer + 3 washers (22:28 UTC)")]
BLUE, ORANGE, RED = "#2a78d6", "#eb6834", "#e34948"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"


def secs(hms):
    h, m, s = hms.rstrip("Z").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def load(label):
    recs = [json.loads(l) for l in open(f"{label}.jsonl")]
    t0 = next(secs(r["utc"]) for r in recs if r.get("event") == "step")
    status, cmds = [], []
    for r in recs:
        t = secs(r["utc"]) - t0
        if r.get("event") in ("step", "coast", "stop"):
            cmds.append((t, r.get("cmd", "30,0")))
        elif "duty" in r:
            status.append((t, r["rpm"], r["duty"], r["setpoint"], r["stalled"]))
    return status, cmds


plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, axes = plt.subplots(2, 3, figsize=(15, 6.2), sharex="col", sharey="row",
                         gridspec_kw={"height_ratios": [1.6, 1], "hspace": 0.12, "wspace": 0.06})
for col, (label, title) in enumerate(RUNS):
    status, cmds = load(label)
    t = [s[0] for s in status]
    a_rpm, a_duty = axes[0, col], axes[1, col]
    # stop windows: from each 30,0 to the next command (or the end)
    ends = [c[0] for c in cmds[1:]] + [t[-1] + 0.5]
    for (tc, cmd), te in zip(cmds, ends):
        if cmd == "30,0":
            for ax in (a_rpm, a_duty):
                ax.axvspan(tc, te, color=GRID, lw=0, zorder=0)
        else:
            for ax in (a_rpm, a_duty):
                ax.axvline(tc, color=MUTED, lw=0.8, ls=":", zorder=1)
            a_rpm.text(tc + 0.8, 1330, cmd.split(",")[1], color=INK2, fontsize=8.5, va="top")
    a_rpm.step(t, [s[3] for s in status], where="post", color=MUTED, lw=1.5, ls="--",
               label="setpoint", zorder=2)
    a_rpm.step(t, [s[1] for s in status], where="post", color=BLUE, lw=2, label="Hall rpm", zorder=3)
    new_stall = [s for p, s in zip(status, status[1:]) if s[4] and not p[4]]
    if new_stall:
        a_rpm.plot([s[0] for s in new_stall], [0] * len(new_stall), "x", color=RED, ms=9, mew=2,
                   label="stalled: firmware stops the fan", zorder=4)
    a_duty.step(t, [s[2] for s in status], where="post", color=ORANGE, lw=2, zorder=3)
    a_rpm.set_title(title, fontsize=11, color=INK, loc="left")
    a_rpm.set_ylim(-60, 1350)
    a_duty.set_ylim(0, 1.0)
    a_duty.set_xlim(-3, 150)
    a_duty.set_xlabel("seconds after the first command")
    for ax in (a_rpm, a_duty):
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
axes[0, 0].set_ylabel("rpm (Hall, per 2 s)")
axes[1, 0].set_ylabel("PWM duty")
handles, labels = axes[0, 0].get_legend_handles_labels()
axes[0, 0].legend(handles, labels, loc="upper left", bbox_to_anchor=(0.0, 0.93), frameon=False,
                  fontsize=9)
fig.suptitle("Compact stirrer, vial of water with the 15 x 6 mm bar, started from rest: "
             "steps 300, stop, 300, stop, 300, 600, 1200 rpm (grey: fan told to stop)",
             x=0.07, ha="left", fontsize=11.5, color=INK)
fig.savefig("rpm_duty_1105.png", dpi=110, bbox_inches="tight", facecolor="white")
print("wrote rpm_duty_1105.png")
