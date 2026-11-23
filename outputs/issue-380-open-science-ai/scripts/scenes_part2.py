#!/usr/bin/env python3
"""Part 2 scenes: openness over time, the open-science commons, language over time, US licence mix,
AM busts, DAL/#318 audit. Usage: python scenes_part2.py <scene> <duration_s> [--png-only]"""
import sys, textwrap, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
from matplotlib.patches import FancyBboxPatch
OUT = "video/scenes"; FIG = "figures"

def blank():
    fig = plt.figure(figsize=(W, H), dpi=DPI); ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); return fig, ax

def p2_title(duration, mp4, png):
    fig, ax = blank()
    t1 = ax.text(0.08, 0.60, "The value of open science\nin the age of AI — Part 2", fontsize=60, fontweight="bold", va="center", linespacing=1.15)
    t2 = ax.text(0.08, 0.36, "Openness over time · the open-science commons · how the labs talk · our own lab", fontsize=27, color=TEXT2)
    t3 = ax.text(0.08, 0.18, "143 case files, a second verification pass, and new data gathered after Part 1\ngithub.com/vertical-cloud-lab/byu-vcl · issue #380", fontsize=19, color=MUTED, linespacing=1.6)
    bar = ax.plot([0.08, 0.08], [0.30, 0.30], color=AQUA, lw=8, solid_capstyle="butt")[0]
    def update(p):
        for t, a in [(t1, ease(p / 0.4)), (t2, ease((p - 0.3) / 0.4)), (t3, ease((p - 0.55) / 0.4))]: t.set_alpha(a)
        bar.set_data([0.08, 0.08 + 0.5 * ease(p / 0.8)], [0.30, 0.30])
    render(fig, update, duration, mp4, png)

def p2_time(duration, mp4, png):
    t = pd.read_csv("data/openness_by_year_sector.csv")
    series = [("Commercial OSS software", BLUE), ("Hardware", ORANGE), ("Physical science (companies & infrastructure)", AQUA), ("Big Tech & AI labs", YELLOW)]
    fig, ax = fig_ax("Openness as a function of time, by sector", "Mean openness (0 closed – 4 open + open governance) of case-study organizations operating each year (n ≥ 5)", rect=(0.07, 0.13, 0.70, 0.68))
    source_note(fig, "Source: data/openness_by_year_sector.csv, rebuilt from 143 case files. VC-era minus incumbent openness change: −0.67 (95% bootstrap CI −1.04 to −0.31).")
    ax.set_xlim(1995, 2026.5); ax.set_ylim(0, 4); ax.set_ylabel("mean openness score")
    lines = {s: ax.plot([], [], color=c, label=s)[0] for s, c in series}; labs = {s: ax.text(0, 0, "", fontsize=16, color=TEXT, va="center") for s, c in series}
    ax.legend(loc="upper left", fontsize=15, ncol=2)
    def update(p):
        xmax = 1995 + p * 31.5
        for s, c in series:
            x = t[(t.sector == s) & (t.n >= 5) & (t.year <= xmax)]; lines[s].set_data(x.year, x.mean_open)
            if len(x): labs[s].set_position((x.year.iloc[-1] + 0.3, x.mean_open.iloc[-1])); labs[s].set_text(f"{x.mean_open.iloc[-1]:.2f}" if p >= 1 else "")
        if p >= 1:
            last = -9
            for s, c in sorted(series, key=lambda q: labs[q[0]].get_position()[1]):
                xx, yy = labs[s].get_position(); yy = max(yy, last + 0.12); labs[s].set_position((xx, yy)); last = yy
    render(fig, update, duration, mp4, png)

def p2_pdb(duration, mp4, png):
    d = pd.read_csv("data/pdb_released_per_year.csv"); d = d[d.year >= 1976]
    fig, ax = fig_ax("Fifty years of open data trained the AI: the Protein Data Bank", "Structures released per year; all free to reuse (CC0 since 2021)", rect=(0.08, 0.13, 0.82, 0.66))
    source_note(fig, "Source: RCSB PDB Search API, entries by initial release year (queried 2026-11-23; 2026 year to date).")
    ax.set_xlim(1975, 2027); ax.set_ylim(0, d.released.max() * 1.15); ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1000:g}k"))
    bars = ax.bar(d.year, [0] * len(d), color=BLUE, width=0.8)
    c2020 = int(d[d.year == 2020].cumulative.iloc[0]); total = int(d.cumulative.iloc[-1])
    big = ax.text(1977, d.released.max() * 1.02, "", fontsize=24, color=TEXT, fontweight="bold", va="top")
    ann = ax.text(2019.6, d.released.max() * 0.95, "", ha="right", va="top", fontsize=18, color=TEXT)
    vl = ax.axvline(2020, color=TEXT2, lw=1.2, ls=(0, (4, 4)), alpha=0)
    def update(p):
        xmax = 1976 + p * 50.5; cum = 0
        for b, (y, n, c) in zip(bars, d[["year", "released", "cumulative"]].values):
            b.set_height(n if y <= xmax else 0)
            if y <= xmax: cum = c
        big.set_text(f"{int(cum):,} structures, all open")
        if xmax >= 2020: vl.set_alpha(1); ann.set_text(f"2020: AlphaFold 2 at CASP14\n{c2020:,} open structures by then")
    render(fig, update, duration, mp4, png)

def p2_commons(duration, mp4, png):
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "The open-science commons is under AI-era strain", fontsize=34, fontweight="bold", va="center")
    fig.text(0.06, 0.865, "Volume up, funding thin: arXiv, the Open Science Framework and Papers with Code in 2025–26", fontsize=21, color=TEXT2, va="center")
    source_note(fig, "Sources: arXiv FY26 budget, 2025 annual report and blog (2026-06-30, 09-23, 10-01); COS blog (2026-08-11, 08-14) and cos.io/osf-changes; paperswithcode GitHub and Hugging Face.\nCase files companies/G/arxiv.json, center-for-open-science.json, papers-with-code.json.")
    ax = fig.add_axes((0.07, 0.16, 0.36, 0.6))
    vals = [("arXiv, Sept 2024", 20569), ("arXiv, Sept 2026", 40363)]
    ax.set_ylim(0, 48000); ax.set_xlim(-0.6, 1.6); ax.set_xticks([0, 1]); ax.set_xticklabels([v[0] for v in vals], fontsize=18, color=TEXT)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k")); ax.set_title("arXiv submissions per month", loc="left", fontsize=22, color=TEXT2); ax.grid(axis="x", visible=False)
    bars = ax.bar([0, 1], [0, 0], width=0.55, color=[BLUE, ORANGE]); tx = [ax.text(i, 0, "", ha="center", va="bottom", fontsize=20, color=TEXT) for i in range(2)]
    cards = [("arXiv", "Left Cornell on 2026-07-01; FY2025 deficit of $297k on $6.7M of costs\nand 28 staff; submission limits and LLM bans; $17.2M multiyear gift in 2026-09.", BLUE),
             ("Open Science Framework", "Full platform needs $4–5M a year (about half of COS's budget); earned\nrevenue covers 10–20%. No new projects since 2026-11-16; read-only 2027-02-19.", ORANGE),
             ("Papers with Code", "Run inside Meta AI with no funding of its own; redirected to Hugging Face\nin 2025. A community archive survives because the dumps were CC BY-SA.", AQUA)]
    cx = fig.add_axes((0.48, 0.12, 0.48, 0.68)); cx.axis("off"); cx.set_xlim(0, 1); cx.set_ylim(0, 1); objs = []
    for i, (h, body, col) in enumerate(cards):
        y0 = 0.68 - i * 0.33
        b = FancyBboxPatch((0.0, y0), 0.98, 0.28, boxstyle="round,pad=0.01,rounding_size=0.02", fc="#232322", ec=col, lw=2.5, alpha=0); cx.add_patch(b)
        t1 = cx.text(0.03, y0 + 0.22, h, fontsize=20, fontweight="bold", color=TEXT, alpha=0, va="center")
        t2 = cx.text(0.03, y0 + 0.10, body, fontsize=15, color=TEXT2, alpha=0, va="center", linespacing=1.4)
        objs.append((b, t1, t2))
    def update(p):
        for i, (lab, v) in enumerate(vals):
            q = ease((p - i * 0.15) / 0.35); bars[i].set_height(v * q); tx[i].set_y(v * q + 600); tx[i].set_text(f"{v:,}" if q > 0.98 else "")
        for i, o in enumerate(objs):
            a = ease((p - 0.3 - i * 0.15) / 0.2)
            for x in o: x.set_alpha(a)
    render(fig, update, duration, mp4, png)

def p2_language(duration, mp4, png):
    t = pd.read_csv("data/language_by_year.csv")
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "From “open” to “science”: Anthropic and OpenAI over time", fontsize=32, fontweight="bold", va="center")
    fig.text(0.06, 0.865, "Mentions per 1,000 words in 48 primary documents fetched through the lab Pi's browser", fontsize=20, color=TEXT2, va="center")
    source_note(fig, "Curated corpus weighted toward policy and science posts, not a random sample. data/language_by_year.csv; quotes in language/key_quotes.md.")
    axes = []; arts = []
    for j, (col, title) in enumerate([("open_per_1k", "Open-* terms"), ("sci_per_1k", "Science and physical-science terms")]):
        ax = fig.add_axes((0.06 + j * 0.48, 0.17, 0.40, 0.6)); ax.set_title(title, loc="left", fontsize=22, color=TEXT2)
        ax.set_xlim(2016, 2027.8); ax.set_ylim(0, max(t[col].max() * 1.2, 1)); ax.set_ylabel("per 1,000 words")
        ax.set_xticks([2017, 2021.5, 2024, 2025, 2026]); ax.set_xticklabels(["2015–19", "2020–23", "2024", "2025", "2026"], fontsize=15)
        for org, c in [("Anthropic", AQUA), ("OpenAI", ORANGE)]:
            s = t[t.org == org]; ln, = ax.plot([], [], color=c, marker="o", ms=9, markeredgecolor=SURFACE, markeredgewidth=2, label=org)
            lab = ax.text(0, 0, "", fontsize=16, color=TEXT, va="center"); arts.append((s, col, ln, lab, org))
        if j == 0: ax.legend(loc="upper left")
    def update(p):
        xmax = 2016 + p * 10.5
        for s, col, ln, lab, org in arts:
            x = s[s.mid <= xmax]; ln.set_data(x.mid, x[col])
            if len(x) and p >= 1: lab.set_position((x.mid.iloc[-1] + 0.2, x[col].iloc[-1])); lab.set_text(f"{org} {x[col].iloc[-1]:.1f}")
    render(fig, update, duration, mp4, png)

def p2_igraph(duration, mp4, png):
    share = pd.read_csv("data/innovationgraph_us_license_family_share.csv", index_col=0); dev = pd.read_csv("data/innovationgraph_us_developers.csv", index_col=0)
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "The US open-source base keeps growing, and getting more permissive", fontsize=32, fontweight="bold", va="center")
    fig.text(0.06, 0.865, "GitHub Innovation Graph (CC0): US developers, and licence families of public repos US developers push to", fontsize=20, color=TEXT2, va="center")
    source_note(fig, "Source: github/innovationgraph data/developers.csv and licenses.csv, quarterly from 2020. 'Other' includes repos with no recognised licence.")
    a1 = fig.add_axes((0.06, 0.16, 0.40, 0.6)); a2 = fig.add_axes((0.56, 0.16, 0.36, 0.6))
    a1.set_title("US developers (millions)", loc="left", fontsize=22, color=TEXT2); a1.set_xlim(dev.index.min(), dev.index.max() + 0.6); a1.set_ylim(0, dev.us_developers.max() / 1e6 * 1.2)
    l1, = a1.plot([], [], color=BLUE); t1 = a1.text(0, 0, "", fontsize=17, color=TEXT, va="center")
    a2.set_title("Licence family share of US pushers", loc="left", fontsize=22, color=TEXT2); a2.set_ylim(0, 1); a2.set_xlim(share.index.min(), share.index.max() + 0.6)
    a2.yaxis.set_major_formatter(mt.PercentFormatter(1.0))
    fams = [("Permissive", BLUE), ("Copyleft", ORANGE), ("Other / unrecognised", "#77766f")]
    l2 = {f: a2.plot([], [], color=c, label=f)[0] for f, c in fams}; t2 = {f: a2.text(0, 0, "", fontsize=16, color=TEXT, va="center") for f, c in fams}
    a2.legend(loc="center left", fontsize=15)
    def update(p):
        xm = dev.index.min() + p * (dev.index.max() - dev.index.min())
        x = dev[dev.index <= xm]; l1.set_data(x.index, x.us_developers / 1e6)
        if len(x): t1.set_position((x.index[-1] + 0.05, x.us_developers.iloc[-1] / 1e6)); t1.set_text(f"{x.us_developers.iloc[-1] / 1e6:.1f}M")
        for f, c in fams:
            s = share[f][share.index <= xm]; l2[f].set_data(s.index, s.values)
            if len(s): t2[f].set_position((s.index[-1] + 0.05, s.values[-1])); t2[f].set_text(f"{s.values[-1]:.0%}")
    render(fig, update, duration, mp4, png)

def p2_am(duration, mp4, png):
    rows = [("Desktop Metal", 2.5e9, "SPAC, 2020", None, "Chapter 11, 2025"), ("Markforged", 2.1e9, "SPAC, 2021", 42.5e6, "sold to Stratasys, 2026"),
            ("Stratasys", 3.0e9, "Objet merger, 2012", 468.6e6, "market cap, Nov 2026")]
    fig, ax = fig_ax("The instruments are closed, and their makers are fragile", "Additive-manufacturing makers in group G: debut value vs latest (log scale); all score 0 on openness",
                     rect=(0.17, 0.16, 0.62, 0.62))
    source_note(fig, "Source: companies/G/desktop-metal.json, markforged.json, stratasys.json (SEC filings, press releases). All 13 instrument/AM makers in group G score 0–1 on openness.")
    ax.set_xscale("log"); ax.set_xlim(1e7, 1e10); ax.set_ylim(-0.6, 2.6); ax.invert_yaxis()
    ax.set_yticks(range(3)); ax.set_yticklabels([r[0] for r in rows], fontsize=20, color=TEXT); ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v/1e9:g}B" if v >= 1e9 else f"${v/1e6:g}M"))
    p0 = ax.scatter([], [], s=260, color=MUTED, zorder=3, label="Debut / deal value"); p1 = ax.scatter([], [], s=260, color=RED, zorder=4, edgecolors=SURFACE, linewidths=2, label="Latest")
    ax.legend(loc="lower left", fontsize=16)
    ar = [ax.annotate("", xy=(r[1], i), xytext=(r[1], i), arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2.5, mutation_scale=22)) for i, r in enumerate(rows)]
    tx = [ax.text(0, i - 0.32, "", fontsize=16, color=TEXT, va="center") for i in range(3)]
    def update(p):
        a, b = [], []
        for i, (n, v0, l0, v1, l1) in enumerate(rows):
            q = ease((p - i * 0.15) / 0.45); end = v1 if v1 else 1.2e7
            x = 10 ** (np.log10(v0) + q * (np.log10(end) - np.log10(v0))); a.append((v0, i)); b.append((x, i))
            ar[i].xy = (x, i); ar[i].set_position((v0, i))
            tx[i].set_position((min(v0, end) * 1.1, i - 0.3)); tx[i].set_text(f"{l0}: ${v0/1e9:.1f}B → " + (f"${v1/1e6:,.1f}M ({l1})" if v1 else l1) if q > 0.98 else "")
        p0.set_offsets(a); p1.set_offsets(b)
    render(fig, update, duration, mp4, png)

DAL2 = [("Programmable interfaces today", "4 of ~20 instruments on the alloy route: UR arms, MiR robots, the OT-2 and the CubXL"),
        ("No API", "The rePowder atomizer: the lab plans to read its settings with a camera (DAL #151)"),
        ("IP on compositions", "Proposal drafts disagree: 'published openly rather than licensed' vs a month-6 IP review"),
        ("Data timing", "Drafts promise data within 12 months; the FOA wants data behind a paper public at publication"),
        ("Licences", "MIT for code · CERN-OHL-P-2.0 for hardware designs · CC BY 4.0 (CC0 metadata) for data"),
        ("Infrastructure", "Zenodo + Materials Data Facility (+ NOMAD Oasis), JSON Schema digital thread, OSTI DOIs"),
        ("Drivers", "One small MIT, MCP-style driver per instrument; ask vendors for API rights before buying")]
def p2_dal(duration, mp4, png):
    fig, ax = blank()
    ax.text(0.06, 0.92, "A closer audit of DAL and #318", fontsize=36, fontweight="bold", va="center")
    ax.text(0.06, 0.865, "Findings (top) and recommendations (bottom) from dal/dal_openness_audit.md, cited to DAL e7a01b3 and #318 75c0ed0", fontsize=20, color=TEXT2, va="center")
    rows = []
    for i, (h, b) in enumerate(DAL2):
        y = 0.77 - i * 0.1; col = ORANGE if i < 4 else BLUE
        chip = FancyBboxPatch((0.06, y - 0.03), 0.26, 0.06, boxstyle="round,pad=0.004,rounding_size=0.01", fc=col, ec="none", alpha=0); ax.add_patch(chip)
        c = ax.text(0.19, y, h, fontsize=17, fontweight="bold", ha="center", va="center", color=TEXT, alpha=0)
        t = ax.text(0.34, y, b, fontsize=18, va="center", color=TEXT, alpha=0); rows.append((chip, c, t))
    ax.text(0.06, 0.04, "Audit: outputs/issue-380-open-science-ai/dal/dal_openness_audit.md", fontsize=14, color=MUTED)
    def update(p):
        for i, r in enumerate(rows):
            a = ease((p - i * 0.09) / 0.18)
            for o in r: o.set_alpha(a)
    render(fig, update, duration, mp4, png)

TAKE2 = ["Every sector is converging on 'open core / mixed': open starters close, closed incumbents open what they don't sell.",
         "Young, VC-backed firms close up (−0.67 vs incumbents, 95% CI excludes zero); public infrastructure stays open.",
         "The open commons that trained the AI (PDB, arXiv, OSF) is strained by AI-era volume and thin funding.",
         "AI labs now court science and the national labs with access, not open weights.",
         "For our lab: own and open the driver and data layer between closed instruments and AI."]
def p2_takeaways(duration, mp4, png):
    fig, ax = blank(); ax.text(0.06, 0.90, "What Part 2 adds", fontsize=40, fontweight="bold", va="center"); items = []
    for i, t in enumerate(TAKE2):
        y = 0.74 - i * 0.14
        n = ax.text(0.06, y, f"{i+1}", fontsize=34, fontweight="bold", color=CAT[i % 4], va="center", alpha=0)
        tx = ax.text(0.11, y, textwrap.fill(t, 92), fontsize=22, va="center", color=TEXT, alpha=0, linespacing=1.25); items.append((n, tx))
    def update(p):
        for i, (n, tx) in enumerate(items):
            a = ease((p - i * 0.13) / 0.2); n.set_alpha(a); tx.set_alpha(a)
    render(fig, update, duration, mp4, png)

def p2_end(duration, mp4, png):
    fig, ax = blank()
    a1 = ax.text(0.5, 0.6, "Data, code and sources for both parts", fontsize=42, fontweight="bold", ha="center", va="center")
    a2 = ax.text(0.5, 0.42, "github.com/vertical-cloud-lab/byu-vcl  ·  issue #380\noutputs/issue-380-open-science-ai", fontsize=26, color=BLUE, ha="center", va="center", linespacing=1.6)
    a3 = ax.text(0.5, 0.16, "Narration: Kokoro-82M (Apache-2.0). Charts: matplotlib. Made by Claude (Anthropic) for the BYU Vertical Cloud Lab.", fontsize=16, color=MUTED, ha="center")
    def update(p):
        for i, t in enumerate([a1, a2, a3]): t.set_alpha(ease((p - i * 0.2) / 0.3))
    render(fig, update, duration, mp4, png)

SCENES = {k: v for k, v in globals().items() if k.startswith("p2_")}
if __name__ == "__main__":
    name = sys.argv[1]; dur = float(sys.argv[2])
    if "--png-only" in sys.argv:
        globals()["render"] = lambda fig, update, duration, out_mp4, out_png=None, build=0.7: (update(1.0), fig.savefig(out_png, dpi=DPI), plt.close(fig))
        SCENES[name](dur, None, f"{FIG}/{name}.png")
    else:
        SCENES[name](dur, f"{OUT}/{name}.mp4", f"{FIG}/{name}.png")
    print("done", name)
