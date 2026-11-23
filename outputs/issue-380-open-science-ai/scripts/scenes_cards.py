#!/usr/bin/env python3
"""Text and diagram scenes: title, lab quotes, DAL/#318 openness stack, takeaways, end card.
Usage: python scenes_cards.py <scene> <duration_s> [--png-only]"""
import sys, textwrap
sys.path.insert(0, "scripts")
from viz_style import *
from matplotlib.patches import FancyBboxPatch
import numpy as np
import matplotlib.ticker as mt
OUT = "video/scenes"; FIG = "figures"

def blank():
    fig = plt.figure(figsize=(W, H), dpi=DPI); ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    return fig, ax

def s_title(duration, mp4, png):
    fig, ax = blank()
    t1 = ax.text(0.08, 0.60, "The value of open science\nin the age of AI", fontsize=66, fontweight="bold", va="center", linespacing=1.15)
    t2 = ax.text(0.08, 0.36, "What the numbers show: software, hardware and the physical sciences, 1971–2026", fontsize=28, color=TEXT2)
    t3 = ax.text(0.08, 0.18, "BYU Vertical Cloud Lab · research run for issue #380 · November 2026\nData, code and 1,000+ sources: github.com/vertical-cloud-lab/byu-vcl (outputs/issue-380-open-science-ai)",
                 fontsize=19, color=MUTED, linespacing=1.6)
    bar = ax.plot([0.08, 0.08], [0.30, 0.30], color=BLUE, lw=8, solid_capstyle="butt")[0]
    def update(p):
        for t, a in [(t1, ease(p / 0.4)), (t2, ease((p - 0.3) / 0.4)), (t3, ease((p - 0.55) / 0.4))]:
            t.set_alpha(a)
        bar.set_data([0.08, 0.08 + 0.5 * ease(p / 0.8)], [0.30, 0.30])
    render(fig, update, duration, mp4, png)

QUOTES = [
 ("“Researchers will be strongly encouraged to publish their work, whether as papers, blog posts, or code, and our patents (if any) will be shared with the world.”", "OpenAI, “Introducing OpenAI”, Dec 2015"),
 ("“The Open in openAI means that everyone should benefit from the fruits of AI after its built, but it's totally OK to not share the science…”", "Ilya Sutskever, 2016 email, published by OpenAI, Mar 2024"),
 ("“We expect that safety and security concerns will reduce our traditional publishing in the future…”", "OpenAI Charter, 2018"),
 ("“Open-weights models that don't have dangerous capabilities are a public good… Anthropic has never advocated for a ban on open-weights models.”", "Dario Amodei, “Our position on open-weights models”, Jul 2026"),
 ("“…a shared specification for AI agents to safely operate physical devices… ahead of making the standard open source.”", "Anthropic, “Previewing the Model Hardware Standard”, Aug 2026"),
 ("“We'll need to be rigorous about mitigating these risks and careful about what we choose to open source.”", "Mark Zuckerberg, “Personal Superintelligence”, Jul 2025"),
]
def s_quotes(duration, mp4, png):
    fig, ax = blank()
    ax.text(0.06, 0.92, "In their own words: “open” at the AI labs", fontsize=36, fontweight="bold", va="center")
    boxes = []
    for i, (q, who) in enumerate(QUOTES):
        col, row = i % 2, i // 2
        x0, y0 = 0.06 + col * 0.455, 0.62 - row * 0.255
        b = FancyBboxPatch((x0, y0), 0.425, 0.21, boxstyle="round,pad=0.008,rounding_size=0.012", fc="#232322", ec=[BLUE, BLUE, ORANGE, AQUA, AQUA, ORANGE][i], lw=2.5, alpha=0)
        ax.add_patch(b)
        t = ax.text(x0 + 0.015, y0 + 0.19, textwrap.fill(q, 62), fontsize=16.5, va="top", color=TEXT, alpha=0, linespacing=1.3)
        w = ax.text(x0 + 0.015, y0 + 0.02, "— " + who, fontsize=14, va="bottom", color=TEXT2, alpha=0)
        boxes.append((b, t, w))
    ax.text(0.06, 0.04, "Full texts fetched through the lab Pi's browser on 2026-11-23; URLs in language/key_quotes.md.", fontsize=14, color=MUTED)
    def update(p):
        for i, (b, t, w) in enumerate(boxes):
            a = ease((p - i * 0.13) / 0.2); b.set_alpha(a); t.set_alpha(a); w.set_alpha(a)
    render(fig, update, duration, mp4, png)

LAYERS = [
 ("Papers, preprints, talks, YouTube walkthroughs", "Open", "open access; this repo's videos"),
 ("Optimisation and orchestration code (BOFN/pKGFN demos, Honegumi; FLAIME)", "Open", "DAL repo is MIT; Honegumi in JOSS; proposal promises a fully open FLAIME release"),
 ("Digital twin of the vertical cloud lab (#318: VLM trays, arms, instruments)", "Open", "scripts and renders in byu-vcl"),
 ("Instrument drivers and interfaces (MCP / MHS-style)", "Rec. open", "recommended here: shared drivers are what other labs reuse"),
 ("Data, digital-thread schema, campaign logs", "Open*", "FAIR deposit (Zenodo); embargo only where IP review needs it"),
 ("Top alloy compositions", "Decide", "drafts disagree: latest says \"published openly rather than licensed\"; earlier, a month-6 IP review"),
 ("CALPHAD databases (Thermo-Calc TCAL) and process tools", "Closed", "licensed; pycalphad for open screening"),
 ("Instruments: Aconity LPBF printer, rePowder atomizer, Kardex VLM, UR10e on MiR", "Closed", "commercial hardware, orchestrated and documented in the open (#318)"),
 ("Budgets, signed letters, CVs", "Private", "kept out when DAL went public (Oct 2026)"),
]
STATUS_COL = {"Rec. open": "#2f6fbd", "Open": BLUE, "Open*": BLUE, "Decide": "#77766f", "Closed": RED, "Private": "#4a4945"}
def s_dal(duration, mp4, png):
    fig, ax = blank()
    ax.text(0.06, 0.92, "DAL and the vertical cloud lab (#318): open stack, closed instruments", fontsize=31, fontweight="bold", va="center")
    ax.text(0.06, 0.865, "What is open, what is closed, and what is still a decision — from DAL's own README, proposal drafts and PR #318", fontsize=20, color=TEXT2, va="center")
    rows = []
    for i, (lab, st, note) in enumerate(LAYERS):
        y = 0.76 - i * 0.078
        chip = FancyBboxPatch((0.06, y - 0.025), 0.10, 0.05, boxstyle="round,pad=0.004,rounding_size=0.01", fc=STATUS_COL[st], ec="none", alpha=0)
        ax.add_patch(chip)
        c = ax.text(0.11, y, st, fontsize=18, fontweight="bold", ha="center", va="center", color=TEXT, alpha=0)
        t = ax.text(0.18, y + 0.008, lab, fontsize=19, va="center", color=TEXT, alpha=0)
        n = ax.text(0.18, y - 0.026, note, fontsize=14.5, va="center", color=TEXT2, alpha=0)
        rows.append((chip, c, t, n))
    ax.text(0.06, 0.035, "Sources: vertical-cloud-lab/digital-alloy-lab README and genesis-mission-proposal drafts (MIT, public since 2026-10); byu-vcl PR #318.", fontsize=14, color=MUTED)
    def update(p):
        for i, r in enumerate(rows):
            a = ease((p - i * 0.08) / 0.18)
            for o in r: o.set_alpha(a)
    render(fig, update, duration, mp4, png)

TAKEAWAYS = [
 "Open code and data create value far beyond their cost ($8.8T of use from $4B of code; PDB ~800×) — but rarely capture it.",
 "Value is captured by whoever runs the service, owns the data or sells the hardware around the open core.",
 "Licences are now strategic levers moving both ways; foundations, not companies, keep openness durable.",
 "In hardware, openness pays in cost (−87%) and longevity, not valuation — except as open standards (RISC-V, OCP).",
 "AI for science runs on open public data and mostly open models in papers, while frontier models and startups close up.",
 "For labs like ours: open the layers others build on (drivers, schemas, data, digital twins); be explicit about the rest.",
]
def s_takeaways(duration, mp4, png):
    fig, ax = blank()
    ax.text(0.06, 0.90, "What the numbers show", fontsize=40, fontweight="bold", va="center")
    items = []
    for i, t in enumerate(TAKEAWAYS):
        y = 0.76 - i * 0.12
        n = ax.text(0.06, y, f"{i+1}", fontsize=34, fontweight="bold", color=CAT[i % 4], va="center", alpha=0)
        tx = ax.text(0.11, y, textwrap.fill(t, 95), fontsize=21, va="center", color=TEXT, alpha=0, linespacing=1.25)
        items.append((n, tx))
    def update(p):
        for i, (n, tx) in enumerate(items):
            a = ease((p - i * 0.12) / 0.2); n.set_alpha(a); tx.set_alpha(a)
    render(fig, update, duration, mp4, png)

def s_end(duration, mp4, png):
    fig, ax = blank()
    a1 = ax.text(0.5, 0.62, "Everything behind this video is open", fontsize=44, fontweight="bold", ha="center", va="center")
    a2 = ax.text(0.5, 0.45, "121 case files · 9 Edison literature reviews · 4,928 GitHub records · Epoch AI, OpenAlex and COSS data\n135 searches, 58 pages and 6 YouTube transcripts pulled through a lab Raspberry Pi's browser",
                 fontsize=22, color=TEXT2, ha="center", va="center", linespacing=1.6)
    a3 = ax.text(0.5, 0.27, "github.com/vertical-cloud-lab/byu-vcl  ·  issue #380", fontsize=26, color=BLUE, ha="center", va="center")
    a4 = ax.text(0.5, 0.12, "Narration: Kokoro-82M (Apache-2.0). Charts: matplotlib. Made by Claude (Anthropic) for the BYU Vertical Cloud Lab.", fontsize=16, color=MUTED, ha="center")
    def update(p):
        for i, t in enumerate([a1, a2, a3, a4]): t.set_alpha(ease((p - i * 0.15) / 0.3))
    render(fig, update, duration, mp4, png)


def s_gh(duration, mp4, png):
    import pandas as pd, collections
    d = pd.read_csv("gh-mining/coded_threads.csv"); d["rs"] = d.repo.str.split("/").str[-1]
    c = collections.Counter()
    for _, r in d.iterrows():
        for t in str(r.themes).split(";"): c[(t.strip(), r.rs)] += 1
    names = {"open_hw_replication": "Open-hardware replication", "kits_bom_costs": "Kits, BOMs and costs", "sustainability_funding": "Sustainability and funding",
             "education_outreach": "Education and outreach", "cloud_access": "Cloud-lab access", "vendors_lockin": "Vendors and lock-in",
             "partners_industry": "Industry partners", "selling_venues": "Selling venues (GroupGets, Tindie...)"}
    th = list(names)[::-1]
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "Our own threads: open hardware is easy to share, hard to sell", fontsize=34, fontweight="bold", va="center")
    fig.text(0.06, 0.865, f"{len(d)} commercialization-related threads coded from 4,928 issues, PRs, discussions and comments (gh api, 2026-11-23)", fontsize=20, color=TEXT2, va="center")
    source_note(fig, "Sources: gh-mining/coded_threads.csv and commercialization_digest.md; kit costs as stated in self-driving-lab-demo discussion #124 (2023-05-04); stated items sum to $75.")
    ax1 = fig.add_axes((0.06, 0.2, 0.33, 0.52)); ax2 = fig.add_axes((0.62, 0.12, 0.34, 0.66))
    parts = [("GroupGets fee", 15.57, BLUE), ("Hardware", 51.19, ORANGE), ("Labour/testing", 6.00, AQUA), ("Not itemized", 5.00, "#4a4945"), ("Profit", 2.24, YELLOW)]
    ax1.set_xlim(0, 84); ax1.set_ylim(-1.3, 1.5); ax1.set_yticks([]); ax1.grid(axis="y", visible=False)
    ax1.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:.0f}"))
    ax1.set_title("The $80 SDL-demo kit via GroupGets, per unit (2023)", loc="left", fontsize=21, color=TEXT2)
    segs = []; left = 0
    for lab, v, col in parts:
        b = ax1.barh(0, 0, left=left, height=0.7, color=col, edgecolor=SURFACE, linewidth=2)[0]
        ypos = {"Labour/testing": -0.62, "Not itemized": 0.62, "Profit": -1.0}.get(lab, 0)
        xpos = {"Profit": 80.5}.get(lab, left + v / 2)
        t = ax1.text(xpos, ypos, "", ha="center", va="center", fontsize=15, color=TEXT)
        segs.append((b, t, left, v, lab)); left += v
    note = ax1.text(0, 1.05, "", fontsize=17, color=TEXT, va="bottom")
    ax2.set_ylim(-0.6, len(th) - 0.4); ax2.set_yticks(range(len(th))); ax2.set_yticklabels([names[t] for t in th], fontsize=15, color=TEXT)
    ax2.tick_params(axis="y", length=0); ax2.grid(axis="y", visible=False); ax2.set_xlim(0, 26)
    ax2.set_title("Threads by theme", loc="left", fontsize=22, color=TEXT2)
    y = np.arange(len(th)); h = 0.38
    ba = ax2.barh(y + h / 2, [0] * len(th), height=h, color=BLUE, label="ac-dev-lab (institutional, 2024–26)")
    bs = ax2.barh(y - h / 2, [0] * len(th), height=h, color=ORANGE, label="self-driving-lab-demo (individual, 2022–25)")
    ax2.legend(loc="lower left", bbox_to_anchor=(0.36, 0.115), fontsize=14)
    va = [c[(t, "ac-dev-lab")] for t in th]; vs = [c[(t, "self-driving-lab-demo")] for t in th]
    def update(p):
        for i, (b, t, l, v, lab) in enumerate(segs):
            q = ease((p - i * 0.12) / 0.3); b.set_width(v * q)
            t.set_text(f"{lab}\n${v:.2f}" if q > 0.98 else "")
        note.set_text("Stated profit: $2.24 a kit, before shipping overhead.\nNext step: hand ordering, assembly and testing to GroupGets." if p > 0.6 else "")
        q = ease((p - 0.3) / 0.5)
        for i in range(len(th)): ba[i].set_width(va[i] * q); bs[i].set_width(vs[i] * q)
    render(fig, update, duration, mp4, png)

SCENES = {"gh_threads": s_gh, "title": s_title, "quotes": s_quotes, "dal": s_dal, "takeaways": s_takeaways, "end": s_end}
if __name__ == "__main__":
    name = sys.argv[1]; dur = float(sys.argv[2])
    if "--png-only" in sys.argv:
        globals()["render"] = lambda fig, update, duration, out_mp4, out_png=None, build=0.7: (update(1.0), fig.savefig(out_png, dpi=DPI), plt.close(fig))
        SCENES[name](dur, None, f"{FIG}/{name}.png")
    else:
        SCENES[name](dur, f"{OUT}/{name}.mp4", f"{FIG}/{name}.png")
    print("done", name)
