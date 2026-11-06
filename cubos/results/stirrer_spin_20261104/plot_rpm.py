"""Draw what `31` reported in the 2026-11-04 holder-on runs, next to the 11-03 holder-off run.

usage: python plot_rpm.py   (from this directory; writes rpm_holderon_1104.png)
`rpm` is Hall pulses counted over a 2 s window, x 30, so it moves in 30 rpm steps.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
BLUE, ORANGE = "#2a78d6", "#eb6834"   # reference categorical slots 1 and 2 (validated)


def runs(path):
    """Split a spin log into {rpm_cmd: [(t, rpm, setpoint)]}, keeping only the status polls."""
    out = {}
    for line in Path(path).read_text().splitlines():
        r = json.loads(line)
        if "rpm" in r and "rpm_cmd" in r:
            out.setdefault(r["rpm_cmd"], []).append((r["t"], r["rpm"], r["setpoint"]))
    return out


today = runs(HERE / "holderon_1104.jsonl")
before = runs(HERE / "../stirrer_first_spins_20261103/holderoff.jsonl")

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True, facecolor=SURFACE)
for ax, (cmd, secs) in zip(axes, [(300, 30), (1200, 30)]):
    ax.set_facecolor(SURFACE)
    t, rpm, sp = zip(*today[cmd])
    t0 = [0.0] + list(t)
    ax.step(t0, [0.0] + [s if s > 0 else None for s in sp], where="post", color=MUTED,
            lw=1.5, ls=(0, (4, 3)), label="setpoint")
    ax.plot([0.0] + list(t), [0.0] + list(rpm), drawstyle="steps-post", color=BLUE, lw=2,
            label="11-04, holder on")
    ax.plot(t, rpm, "o", color=BLUE, ms=4, mec=SURFACE, mew=1)
    if cmd == 1200:
        tb, rb, _ = zip(*before[1200])
        ax.plot([0.0] + list(tb), [0.0] + list(rb), drawstyle="steps-post", color=ORANGE, lw=2,
                label="11-03, holder off (16 s run)")
        ax.plot(tb, rb, "o", color=ORANGE, ms=4, mec=SURFACE, mew=1)
        ax.annotate("1290, then 1260", xy=(22.3, 1290), xytext=(20.8, 1010), color=INK2,
                    fontsize=9, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    else:
        ax.annotate("300 steady from 16 s", xy=(20, 300), xytext=(14, 520), color=INK2,
                    fontsize=9, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.axvline(secs, color=MUTED, lw=0.8, ls=":")
    ax.text(secs + 0.3, 1500, "stop", color=MUTED, fontsize=9, va="top")
    ax.set_title(f"30,{cmd},{secs}: {cmd} rpm for {secs} s", loc="left", fontsize=11, color=INK)
    ax.set_xlabel("seconds after the command")
    ax.set_xlim(0, secs + 5)
    ax.grid(axis="y", color="#e6e5e0", lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel("rpm from the Hall sensor (2 s window)")
axes[0].set_ylim(0, 1550)
axes[1].legend(loc="upper left", frameon=False, fontsize=9)
fig.suptitle("Compact stirrer on the CubXL's Uno, 2026-11-04 22:58 UTC: no stall, one Hall pulse a turn",
             x=0.01, ha="left", fontsize=12, color=INK)
fig.tight_layout()
fig.savefig(HERE / "rpm_holderon_1104.png", dpi=150, facecolor=SURFACE)
print("wrote", HERE / "rpm_holderon_1104.png")
