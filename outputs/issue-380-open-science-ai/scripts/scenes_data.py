#!/usr/bin/env python3
"""Animated scenes built from the quantitative datasets (Epoch, OpenAlex, literature values, prices,
language). Each scene(duration, out_mp4, out_png) renders one silent clip plus its final frame.
Usage: python scenes_data.py <scene> <duration_s> [--png-only]"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
OUT = "video/scenes"; FIG = "figures"

def money(v):
    if v >= 1e12: return f"${v/1e12:g}T"
    if v >= 1e9: return f"${v/1e9:g}B" if v/1e9 >= 10 or float(v/1e9).is_integer() else f"${v/1e9:.2f}B"
    return f"${v/1e6:g}M"

# ---------------------------------------------------------------- S2: what OSS is worth
def s_oss_value(duration, mp4, png):
    items = [("Cost to recreate the open-source code firms use\n(supply side; Hoffmann, Nagle & Zhou 2024)", 4.15e9, "$4.15B"),
             ("US investment in open-source software, 2019\n(national-accounts method; Robbins et al. 2021, BEA 2022)", 38.4e9, "$36–38B / yr"),
             ("EU GDP impact of open source, 2018\n(Blind et al. 2021; €65–95B)", 94e9, "≈$77–112B / yr"),
             ("Value to firms of the open source they use\n(demand side: cost to rebuild it themselves)", 8.8e12, "$8.8T")]
    fig, ax = fig_ax("What is open-source software worth?",
                     "Different questions, different numbers: the cost to build it is tiny next to the value of using it",
                     rect=(0.40, 0.14, 0.52, 0.66))
    source_note(fig, "Sources: Hoffmann, Nagle & Zhou (HBS WP 24-038, 2024); Robbins et al. (2021); Santiago Calderón et al. (BEA WP2022-10); Blind et al. (EC, 2021). Log scale.")
    ax.set_xscale("log"); ax.set_xlim(1e9, 3e13); ax.set_ylim(-0.6, len(items) - 0.4); ax.invert_yaxis()
    ax.set_yticks(range(len(items))); ax.set_yticklabels([i[0] for i in items], fontsize=16, color=TEXT)
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: money(v))); ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    bars = ax.barh(range(len(items)), [1e9] * len(items), left=0, height=0.56, color=BLUE)
    labels = [ax.text(1e9, i, "", va="center", ha="left", fontsize=22, color=TEXT, fontweight="bold") for i in range(len(items))]
    call = ax.text(1.3e9, 2.5, "", fontsize=23, color=TEXT, ha="left", va="center")
    def update(p):
        for i, (lab, v, s) in enumerate(items):
            q = ease((p - i * 0.2) / 0.32)
            w = 10 ** (9 + q * (np.log10(v) - 9))
            bars[i].set_width(w)
            labels[i].set_x(w * 1.15); labels[i].set_text(s if q > 0.98 else "")
        call.set_text("≈2,100× between the cost to build\nand the value of use" if p > 0.95 else "")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- S3: cost vs value in open science & hardware
def s_open_science_value(duration, mp4, png):
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "Open science is cheap to run and expensive to lose", fontsize=36, fontweight="bold")
    fig.text(0.06, 0.865, "Annual cost vs measured value of the Protein Data Bank; savings from open scientific hardware", fontsize=21, color=TEXT2)
    ax1 = fig.add_axes((0.06, 0.16, 0.42, 0.6)); ax2 = fig.add_axes((0.56, 0.16, 0.39, 0.6))
    source_note(fig, "Sources: Sullivan, Brennan-Tonetta & Marxen (RCSB PDB economic impact, 2017; 2016 activity); Pearce (2020), 119 open hardware designs vs commercial equivalents.")
    rows = [("PDB operating cost", 6.9e6), ("R&D return (conservative)", 1.1e9), ("Efficiency gain", 2.5e9), ("Use value (researcher time)", 5.5e9)]
    ax1.set_xscale("log"); ax1.set_xlim(1e6, 3e10); ax1.invert_yaxis(); ax1.set_ylim(-0.6, 3.6)
    ax1.set_yticks(range(4)); ax1.set_yticklabels([r[0] for r in rows], fontsize=17, color=TEXT); ax1.tick_params(axis="y", length=0)
    ax1.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: money(v) + "/yr")); ax1.grid(axis="y", visible=False)
    ax1.set_title("Protein Data Bank, per year", loc="left", fontsize=22, color=TEXT2)
    b1 = ax1.barh(range(4), [1e6] * 4, height=0.55, color=[ORANGE, BLUE, BLUE, BLUE])
    t1 = [ax1.text(1e6, i, "", va="center", fontsize=20, fontweight="bold") for i in range(4)]
    hw = [("Average, 119 designs", 87), ("Arduino-based", 89), ("3D-printed", 92), ("Arduino + 3D-printed", 94)]
    ax2.set_xlim(0, 100); ax2.invert_yaxis(); ax2.set_ylim(-0.6, 3.6)
    ax2.set_yticks(range(4)); ax2.set_yticklabels([h[0] for h in hw], fontsize=17, color=TEXT); ax2.tick_params(axis="y", length=0)
    ax2.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:.0f}%")); ax2.grid(axis="y", visible=False)
    ax2.set_title("Open scientific hardware: savings vs commercial", loc="left", fontsize=22, color=TEXT2)
    b2 = ax2.barh(range(4), [0] * 4, height=0.55, color=AQUA)
    t2 = [ax2.text(0, i, "", va="center", fontsize=20, fontweight="bold") for i in range(4)]
    call = fig.text(0.06, 0.80, "", fontsize=22, color=TEXT)
    def update(p):
        for i, (lab, v) in enumerate(rows):
            q = ease((p - i * 0.12) / 0.4); w = 10 ** (6 + q * (np.log10(v) - 6))
            b1[i].set_width(w); t1[i].set_x(w * 1.2); t1[i].set_text(money(v) if q > 0.98 else "")
        for i, (lab, v) in enumerate(hw):
            q = ease((p - 0.35 - i * 0.1) / 0.35); w = q * v
            b2[i].set_width(w); t2[i].set_x(w + 1.5); t2[i].set_text(f"{v}%" if q > 0.98 else "")
        call.set_text("$6.9M a year to run → about $5.5B a year of research use: roughly 800×" if p > 0.6 else "")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- S9: model openness by sector (Epoch, US)
def s_epoch_sector(duration, mp4, png):
    b = pd.read_csv("data/epoch_openness_by_year_sector.csv")
    b = b[(b.scope == "US") & b.year.between(2016, 2025)].copy(); b["open_n"] = b.n * b.open_any
    series = [("Academia", BLUE), ("Industry", ORANGE), ("Industry+Academia", AQUA)]
    fig, ax = fig_ax("Who releases model weights? US AI models by sector",
                     "Share of models with downloadable weights, 2-year pooled (Epoch AI database, n = models with known access)",
                     rect=(0.08, 0.13, 0.72, 0.68))
    source_note(fig, "Source: Epoch AI, 'Data on AI Models' (CC-BY), downloaded 2026-11-23; US-affiliated organizations; 'open' = open weights (unrestricted, restricted or non-commercial).")
    ax.set_xlim(2017.8, 2025.3); ax.set_ylim(0, 1.0); ax.yaxis.set_major_formatter(mt.PercentFormatter(1.0))
    data = {}
    for s, c in series:
        t = b[b.sector == s].set_index("year").reindex(range(2016, 2026)).fillna(0)
        pooled = (t.open_n + t.open_n.shift(1).fillna(0)) / (t.n + t.n.shift(1).fillna(0)).replace(0, np.nan)
        data[s] = pooled.loc[2018:2025]
    lines = {s: ax.plot([], [], color=c, label=s)[0] for s, c in series}
    dots = {s: ax.plot([], [], "o", ms=10, color=c, markeredgecolor=SURFACE, markeredgewidth=2)[0] for s, c in series}
    labs = {s: ax.text(0, 0, "", fontsize=20, color=TEXT, va="center") for s, c in series}
    ax.legend(loc="upper left", ncol=3, bbox_to_anchor=(0, 1.08))
    def update(p):
        xmax = 2018 + p * 7
        for s, c in series:
            d = data[s].dropna(); d = d[d.index <= xmax + 1e-9]
            if len(d) == 0: continue
            xs = list(d.index); ys = list(d.values)
            if xmax < 2025 and xmax > xs[-1]:
                nxt = data[s].dropna(); nxt = nxt[nxt.index > xs[-1]]
                if len(nxt):
                    f = (xmax - xs[-1]); xs.append(xmax); ys.append(ys[-1] + f * (nxt.values[0] - ys[-1]))
            lines[s].set_data(xs, ys); dots[s].set_data([xs[-1]], [ys[-1]])
            labs[s].set_position((xs[-1] + 0.12, ys[-1])); labs[s].set_text(f"{s} {ys[-1]:.0%}")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- S10: open-access share by sector (OpenAlex)
def s_openalex(duration, mp4, png):
    df = pd.read_csv("data/openalex_us_oa_by_sector.csv")
    series = [("education", "Academia", BLUE), ("company", "Industry", ORANGE), ("government", "Government", AQUA), ("facility", "Facilities incl. national labs", YELLOW)]
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "Papers went open everywhere, industry included", fontsize=36, fontweight="bold")
    fig.text(0.06, 0.865, "Share of US-affiliated journal articles that are free to read (any open-access route), by author institution type", fontsize=21, color=TEXT2)
    source_note(fig, "Source: OpenAlex API (works: type=article, US institutions, grouped by year and open_access.is_oa), queried 2026-11-23. Institution types follow ROR.")
    axes = [fig.add_axes((0.06, 0.14, 0.40, 0.62)), fig.add_axes((0.55, 0.14, 0.40, 0.62))]
    scopes = [("all", "All fields"), ("physical_sciences", "Physical sciences")]
    art = []
    for ax, (sc, title) in zip(axes, scopes):
        ax.set_xlim(2000, 2025); ax.set_ylim(0, 1); ax.yaxis.set_major_formatter(mt.PercentFormatter(1.0))
        ax.set_title(title, loc="left", fontsize=24, color=TEXT2)
        for key, lab, c in series:
            t = df[(df.scope == sc) & (df.inst_type == key) & df.year.between(2000, 2025)].sort_values("year")
            ln, = ax.plot([], [], color=c, label=lab)
            tx = ax.text(0, 0, "", fontsize=17, color=TEXT, va="center")
            art.append((t.year.values, t.oa_share.values, ln, tx, lab))
    axes[0].legend(loc="upper left", ncol=4, bbox_to_anchor=(0, 1.16), fontsize=18)
    def update(p):
        xmax = 2000 + p * 25
        for xs, ys, ln, tx, lab in art:
            m = xs <= xmax
            if m.sum() == 0: continue
            ln.set_data(xs[m], ys[m])
        if p >= 1:
            for ax in axes:
                mine = [a for a in art if a[3].axes is ax]
                order = sorted(mine, key=lambda a: a[1][-1]); last = -1
                for xs, ys, ln, tx, lab in order:
                    y = max(ys[-1], last + 0.04); last = y
                    tx.set_position((2025.4, y)); tx.set_text(f"{ys[-1]:.0%}")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- S10c: compute gap open vs closed
def s_compute_gap(duration, mp4, png):
    c = pd.read_csv("data/epoch_max_compute_open_vs_closed.csv").set_index("year")
    c = c[(c.index >= 2016) & (c.index <= 2026)]
    fig, ax = fig_ax("Open papers, closed frontier", "Largest training run of the year (FLOP, log scale): open-weight models vs closed or unreleased models")
    source_note(fig, "Source: Epoch AI 'Data on AI Models' (CC-BY), all countries, downloaded 2026-11-23; 2026 is year-to-date.")
    ax.set_yscale("log"); ax.set_xlim(2016, 2026.6); ax.set_ylim(1e19, 1e28)
    ser = [("closed (API/unreleased)", "Closed or unreleased", ORANGE), ("open weights", "Open weights", BLUE)]
    lines = {}; labs = {}
    for k, lab, col in ser:
        lines[k], = ax.plot([], [], color=col, marker="o", ms=9, markeredgecolor=SURFACE, markeredgewidth=2, label=lab)
        labs[k] = ax.text(0, 0, "", fontsize=19, color=TEXT, va="center")
    ax.legend(loc="upper left")
    note = ax.text(2021.2, 3e19, "", fontsize=21, color=TEXT)
    def update(p):
        xmax = 2016 + p * 10
        for k, lab, col in ser:
            s = c[k].dropna(); s = s[s.index <= xmax + 1e-9]
            lines[k].set_data(s.index, s.values)
            if len(s): labs[k].set_position((s.index[-1] + 0.15, s.values[-1])); labs[k].set_text(f"{np.log10(s.values[-1]):.1f}")
        if p >= 1:
            g25 = np.log10(c.loc[2025, "closed (API/unreleased)"]) - np.log10(c.loc[2025, "open weights"])
            g26 = np.log10(c.loc[2026, "closed (API/unreleased)"]) - np.log10(c.loc[2026, "open weights"])
            note.set_text(f"Gap: {10**g25:.0f}× in 2025, {10**g26:.0f}× in 2026 so far\n(log₁₀ FLOP shown at line ends)")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- S11: language of the labs
def s_language(duration, mp4, png):
    t = pd.read_csv("language/term_rates_by_org.csv").set_index("org")
    orgs = ["Anthropic", "OpenAI", "Meta", "GoogleDeepMind"]
    names = {"GoogleDeepMind": "Google DeepMind"}
    t["open_terms"] = t.open_source_per_1k + t.open_weights_per_1k + t.open_science_per_1k
    meas = [("open_terms", "Open source / open weights / open science", BLUE), ("safety_risk_per_1k", "Safety & risk", ORANGE),
            ("science_per_1k", "Science & discovery", AQUA), ("physical_sci_per_1k", "Labs, instruments & physical sciences", YELLOW)]
    fig, ax = fig_ax("How the labs talk: mentions per 1,000 words",
                     "Primary documents fetched through the lab Pi's browser: blogs, charters, policy filings, essays, 2015–2026")
    docs = {o: int(t.loc[o, "docs"]) for o in orgs}; words = {o: int(t.loc[o, "words"]) for o in orgs}
    source_note(fig, "Corpus: " + "; ".join(f"{names.get(o,o)} {docs[o]} docs ({words[o]//1000}k words)" for o in orgs) + ". Meta and DeepMind corpora are small. Regex counts.")
    x = np.arange(len(orgs)); wbar = 0.19
    ax.set_xticks(x); ax.set_xticklabels([names.get(o, o) for o in orgs], fontsize=22, color=TEXT); ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(t.loc[orgs, [m[0] for m in meas]].max()) * 1.18); ax.set_ylabel("mentions per 1,000 words")
    bars = []
    for j, (k, lab, col) in enumerate(meas):
        bars.append(ax.bar(x + (j - 1.5) * (wbar + 0.012), [0] * len(orgs), width=wbar, color=col, label=lab))
    ax.legend(loc="upper right", ncol=2, fontsize=17)
    txt = []
    for j, (k, lab, col) in enumerate(meas):
        txt.append([ax.text(xi + (j - 1.5) * (wbar + 0.012), 0, "", ha="center", va="bottom", fontsize=15, color=TEXT2) for xi in x])
    def update(p):
        for j, (k, lab, col) in enumerate(meas):
            q = ease((p - j * 0.15) / 0.5)
            for i, o in enumerate(orgs):
                v = t.loc[o, k] * q; bars[j][i].set_height(v)
                txt[j][i].set_y(v + 0.05); txt[j][i].set_text(f"{t.loc[o, k]:.1f}" if q > 0.98 else "")
    render(fig, update, duration, mp4, png)

SCENES = {"oss_value": s_oss_value, "open_science_value": s_open_science_value, "epoch_sector": s_epoch_sector,
          "openalex": s_openalex, "compute_gap": s_compute_gap, "language": s_language}
if __name__ == "__main__":
    name = sys.argv[1]; dur = float(sys.argv[2]); png_only = "--png-only" in sys.argv
    fn = SCENES[name]
    if png_only:
        import viz_style
        viz_style.render = lambda fig, update, duration, out_mp4, out_png=None, build=0.7: (update(1.0), fig.savefig(out_png, dpi=DPI), plt.close(fig))
        globals()["render"] = viz_style.render
        fn(dur, None, f"{FIG}/{name}.png")
    else:
        fn(dur, f"{OUT}/{name}.mp4", f"{FIG}/{name}.png")
    print("done", name)
