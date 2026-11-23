import sys, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
d = pd.read_csv("data/openalex_physsci_topics.csv"); d = d[d.year >= 2010]
fig = plt.figure(figsize=(W, H), dpi=DPI)
fig.text(0.06, 0.92, "Self-driving labs took off; open-hardware publishing plateaued", fontsize=32, fontweight="bold", va="center")
fig.text(0.06, 0.865, "Papers per year matching each topic in title or abstract (OpenAlex), all countries vs US-affiliated", fontsize=20, color=TEXT2, va="center")
source_note(fig, "Source: OpenAlex API (title_and_abstract.search; HardwareX by source id), queried 2026-11-23; data/openalex_physsci_topics.csv. Keyword matches undercount; trends matter more than levels.")
for j, (k, title) in enumerate([("sdl_all", "Self-driving / autonomous labs"), ("osh_all", "Open-source hardware")]):
    ax = fig.add_axes((0.06 + j * 0.48, 0.16, 0.40, 0.6)); ax.set_title(title, loc="left", fontsize=22, color=TEXT2)
    ax.plot(d.year, d[k], color=BLUE, marker="o", ms=7, label="All papers"); ax.plot(d.year, d[k + "_us"], color=ORANGE, marker="o", ms=7, label="US-affiliated")
    if k == "osh_all": ax.plot(d.year, d["hardwarex"], color=AQUA, marker="o", ms=7, label="HardwareX articles")
    for col in [k, k + "_us"] + (["hardwarex"] if k == "osh_all" else []):
        ax.text(2025.3, d[col].iloc[-1], f"{int(d[col].iloc[-1])}", fontsize=15, color=TEXT, va="center")
    ax.set_xlim(2010, 2026.6); ax.set_ylim(0, None); ax.legend(loc="upper left", fontsize=15)
fig.savefig("figures/physsci_topics.png", dpi=DPI); print("saved")
