#!/usr/bin/env python3
"""Anthropic vs OpenAI term rates by year (words-weighted), from language/term_counts_by_document.csv.
Writes data/language_by_year.csv and figures/language_time.png."""
import sys, pandas as pd, numpy as np
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
d = pd.read_csv("language/term_counts_by_document.csv")
d["year"] = d.date.astype(str).str[:4].astype(int)
d["open"] = d.open_source + d.open_weights + d.open_science
d["sci"] = d.science + d.physical_sci
d = d[d.org.isin(["Anthropic", "OpenAI"])]
bins = [(2015, 2019), (2020, 2023), (2024, 2024), (2025, 2025), (2026, 2026)]
rows = []
for org, g in d.groupby("org"):
    for a, b in bins:
        x = g[g.year.between(a, b)]
        if x.words.sum() == 0: continue
        rows.append(dict(org=org, period=f"{a}" if a == b else f"{a}–{b % 100:02d}", mid=(a + b) / 2, docs=len(x), words=int(x.words.sum()),
                         open_per_1k=1000 * x.open.sum() / x.words.sum(), sci_per_1k=1000 * x.sci.sum() / x.words.sum(),
                         safety_per_1k=1000 * x.safety_risk.sum() / x.words.sum()))
t = pd.DataFrame(rows); t.to_csv("data/language_by_year.csv", index=False); print(t.round(2).to_string(index=False))
fig = plt.figure(figsize=(W, H), dpi=DPI)
fig.text(0.06, 0.92, "From “open” to “science”: how often Anthropic and OpenAI use each", fontsize=32, fontweight="bold", va="center")
fig.text(0.06, 0.865, "Mentions per 1,000 words in each lab's primary documents, by period (documents fetched through the lab Pi's browser)", fontsize=20, color=TEXT2, va="center")
source_note(fig, "Open = open source/weights/models/science/data/access/standards. Science = science, discovery, physics, chemistry, materials, labs, instruments, experiments.\nCurated corpus (48 docs), weighted toward policy and science posts; not a random sample. Docs per point: data/language_by_year.csv.")
for j, (col, title) in enumerate([("open_per_1k", "Open-* terms"), ("sci_per_1k", "Science and physical-science terms")]):
    ax = fig.add_axes((0.06 + j * 0.48, 0.17, 0.40, 0.6)); ax.set_title(title, loc="left", fontsize=22, color=TEXT2)
    for org, c in [("Anthropic", AQUA), ("OpenAI", ORANGE)]:
        s = t[t.org == org]
        ax.plot(s.mid, s[col], color=c, marker="o", ms=9, markeredgecolor=SURFACE, markeredgewidth=2, label=org)
        if len(s): ax.text(s.mid.iloc[-1] + 0.2, s[col].iloc[-1], f"{org} {s[col].iloc[-1]:.1f}", fontsize=16, color=TEXT, va="center")
    ax.set_xlim(2016, 2027.8); ax.set_ylim(0, max(t[col].max() * 1.2, 1)); ax.set_ylabel("per 1,000 words")
    ax.set_xticks([b[0] if b[0] == b[1] else (b[0] + b[1]) / 2 for b in bins]); ax.set_xticklabels([r for r in ["2015–19", "2020–23", "2024", "2025", "2026"]], fontsize=15)
    if j == 0: ax.legend(loc="upper left")
fig.savefig("figures/language_time.png", dpi=DPI); print("saved")
