"""One chart and one table from results/*.json: what each method's three samples contain.

    python summary.py      # writes media/summary.png and results/summary.md
"""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
MEDIA = os.path.join(HERE, "media")

GROUP_HEX = ["#2a78d6", "#eda100", "#e34948", "#6250d6"]  # same as the animations
GROUP_TXT = ["made first (bottom third)", "middle third", "made last (top third)", "sweepings"]
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#fcfcfb"

# scenario -> (label, which group each of its three samples is meant to be, in file order)
METHODS = [
    ("open_tube", "samples", "Open tube, laid out", [0, 1, 2]),
    ("open_tube", "sliced_in_tube", "Open tube, sliced in the tube", [0, 1, 2]),
    ("piston", "samples", "Piston corer, laid out", [0, 1, 2]),
    ("piston", "sliced_in_tube", "Piston corer, sliced in the tube", [0, 1, 2]),
    ("thief", "samples", "Three-port thief", [0, 1, 2]),
    ("spoon", "samples", "Spoonula, a scoop per layer", [2, 1, 0]),
    ("peel", "samples", "Scrape off whole layers (idealised)", [2, 1, 0]),
    ("pour", "samples", "Pour along a line, thirds", [2, 1, 0]),
]
TARGET_TXT = {0: "bottom", 1: "middle", 2: "top"}
TRUE_GAP = 5 / 6 - 1 / 6  # mean production time, top third minus bottom third


def load():
    rows = []
    for key, field, label, intended in METHODS:
        p = os.path.join(RES, f"{key}.json")
        if not os.path.exists(p):
            continue
        r = json.load(open(p))
        if field not in r:
            continue
        samples = {g: s for g, s in zip(intended, r[field])}
        kept = (samples[2]["mean_label"] - samples[0]["mean_label"]) / TRUE_GAP
        rows.append(dict(key=key, label=label, samples=samples, kept=kept, raw=r))
    return rows


def chart(rows):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, ax = plt.subplots(figsize=(10.5, 9.0), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    yt, ylab = [], []
    y = 0.0
    for row in rows:
        ax.text(0.0, y - 0.88, row["label"], transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=11, fontweight="bold", color=INK)
        star = "*" if row["kept"] > 1.0 else ""
        ax.text(1.0, y - 0.88, f"drift kept {100 * row['kept']:.0f}%{star}", transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=10.5, color=INK, fontweight="bold")
        for g in (2, 1, 0):
            s = row["samples"][g]
            n = max(1, s["n"])
            left = 0.0
            for k in range(4):
                frac = s["counts"][k] / n
                if frac <= 0:
                    continue
                ax.barh(y, frac, left=left, height=0.72, color=GROUP_HEX[k], edgecolor=SURFACE, linewidth=1.5)
                if k == g and frac >= 0.12:
                    ax.text(left + frac / 2, y, f"{100 * frac:.0f}%", ha="center", va="center", fontsize=9.5,
                            color="white" if k in (0, 3) else INK, fontweight="bold")
                left += frac
            on = s["counts"][g] / n
            if on < 0.12:
                ax.text(1.008, y, f"{100 * on:.0f}% on target", transform=ax.get_yaxis_transform(), ha="left",
                        va="center", fontsize=9, color=INK2)
            yt.append(y)
            ylab.append(f"{TARGET_TXT[g]}, n={s['n']}")
            y += 1.0
        y += 0.9
    ax.set_yticks(yt, ylab, fontsize=9.5, color=INK2)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"], color=INK2)
    ax.set_xlabel("share of the sample's particles, by when they were made", color=INK2)
    ax.tick_params(length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    handles = [Patch(facecolor=c, edgecolor="none", label=t) for c, t in zip(GROUP_HEX, GROUP_TXT)]
    ax.legend(handles=handles, ncol=4, loc="lower left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=9.5,
              handlelength=1.2, columnspacing=1.4)
    fig.text(0.01, 0.985, "Which sampling method keeps the top, middle and bottom of the jar apart? (DEM)",
             fontsize=13, fontweight="bold", color=INK, va="top")
    notes = ["Labels: share of the sample from the third it was meant to come from.",
             "Drift kept: (top sample − bottom sample) ÷ (top third − bottom third), in mean making time. "
             "100% = a steady Si drift during the run would be measured in full.",
             "* Over 100%: each swab is a thin slice from near the middle of its third."]
    for k, line in enumerate(notes):
        fig.text(0.01, 0.052 - 0.019 * k, line, fontsize=8, color=MUTED)
    fig.subplots_adjust(left=0.17, right=0.87, top=0.9, bottom=0.115)
    os.makedirs(MEDIA, exist_ok=True)
    fig.savefig(os.path.join(MEDIA, "summary.png"), facecolor=SURFACE)


def table(rows):
    lines = ["| Method | Sample | n | Bottom third | Middle third | Top third | Sweepings | From the intended third |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows:
        for g in (2, 1, 0):
            s = row["samples"][g]
            n = max(1, s["n"])
            pc = [f"{100 * c / n:.0f}%" for c in s["counts"]]
            lines.append(f"| {row['label']} | {TARGET_TXT[g]} | {s['n']} | {' | '.join(pc)} | "
                         f"{100 * s['counts'][g] / n:.0f}% |")
    lines += ["", "| Method | Drift kept |", "| --- | ---: |"]
    lines += [f"| {row['label']} | {100 * row['kept']:.0f}% |" for row in rows]
    with open(os.path.join(RES, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    rows = load()
    chart(rows)
    table(rows)
