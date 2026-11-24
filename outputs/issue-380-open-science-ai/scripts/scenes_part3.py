#!/usr/bin/env python3
"""Part 3 scenes: fork robustness, AI-era open-source startups, AI-for-science model licences,
academic paths, AI agents writing the lab's open record. Usage: python scenes_part3.py <scene> <dur> [--png-only]"""
import sys, textwrap, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
import viz_style
from viz_style import *
import matplotlib.ticker as mt
from matplotlib.patches import FancyBboxPatch
import scenes_companies as sc
OUT = "video/scenes"; FIG = "figures"
def blank():
    fig = plt.figure(figsize=(W, H), dpi=DPI); ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); return fig, ax

def p3_title(duration, mp4, png):
    fig, ax = blank()
    t1 = ax.text(0.08, 0.60, "The value of open science\nin the age of AI — Part 3", fontsize=60, fontweight="bold", va="center", linespacing=1.15)
    t2 = ax.text(0.08, 0.36, "Do forks survive? · AI-era open-source startups · AI-for-science models · the academic path", fontsize=26, color=TEXT2)
    t3 = ax.text(0.08, 0.18, "179 case files, 15 Edison literature reviews, GitHub API data\ngithub.com/vertical-cloud-lab/byu-vcl · issue #380", fontsize=19, color=MUTED, linespacing=1.6)
    bar = ax.plot([0.08, 0.08], [0.30, 0.30], color=YELLOW, lw=8, solid_capstyle="butt")[0]
    def update(p):
        for t, a in [(t1, ease(p / 0.4)), (t2, ease((p - 0.3) / 0.4)), (t3, ease((p - 0.55) / 0.4))]: t.set_alpha(a)
        bar.set_data([0.08, 0.08 + 0.5 * ease(p / 0.8)], [0.30, 0.30])
    render(fig, update, duration, mp4, png)

def p3_forks(duration, mp4, png):
    d = pd.read_csv("data/fork_vs_original.csv")
    d["label"] = d.case.str.replace(r" \(\d{4}\)", "", regex=True)
    fig, ax = fig_ax("Do forks survive closing moves?", "Commits in the last 12 months: the original project vs its open fork (GitHub API, 2026-11-23; log scale)",
                     rect=(0.27, 0.13, 0.66, 0.68))
    source_note(fig, "Source: data/fork_vs_original.csv (default-branch commits since 2025-11-24). Commit counts include automation; read as relative activity.")
    n = len(d); y = np.arange(n); h = 0.38
    ax.set_xscale("log"); ax.set_xlim(1, 5e4); ax.set_ylim(-0.6, n - 0.4); ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_yticks(y); ax.set_yticklabels(d.label, fontsize=16, color=TEXT); ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
    bo = ax.barh(y - h / 2, [1] * n, height=h, color=ORANGE, label="Original (after closing)")
    bf = ax.barh(y + h / 2, [1] * n, height=h, color=BLUE, label="Open fork")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.09), ncol=2, fontsize=16)
    vo = d.orig_commits_12m.fillna(0).clip(lower=1).values; vf = d.fork_commits_12m.fillna(0).clip(lower=1).values
    to = [ax.text(1, i - h / 2, "", va="center", fontsize=13, color=TEXT2) for i in y]; tf = [ax.text(1, i + h / 2, "", va="center", fontsize=13, color=TEXT2) for i in y]
    def update(p):
        for i in range(n):
            q = ease((p - i * 0.06) / 0.45)
            a = 10 ** (q * np.log10(vo[i])); b = 10 ** (q * np.log10(vf[i]))
            bo[i].set_width(a); bf[i].set_width(b); to[i].set_x(a * 1.15); tf[i].set_x(b * 1.15)
            to[i].set_text(f"{int(d.orig_commits_12m.iloc[i]):,}" if q > 0.98 else ""); tf[i].set_text(f"{int(d.fork_commits_12m.iloc[i]):,}" if q > 0.98 else "")
    render(fig, update, duration, mp4, png)

def p3_aiera(duration, mp4, png):
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.06, 0.92, "AI-era open-source startups stayed open, and sold to compute", fontsize=32, fontweight="bold", va="center")
    fig.text(0.06, 0.865, "Group J (17 firms: Ray, vLLM, LangChain, Ollama, llama.cpp, W&B, Modular, Chroma...) vs group A (2010s databases)", fontsize=19, color=TEXT2, va="center")
    source_note(fig, "Sources: companies/A and companies/J case files (licence histories; acquisitions 2025–26). Modular price from Wikipedia only; Anyscale deal reported, not confirmed closed.")
    ax1 = fig.add_axes((0.07, 0.16, 0.36, 0.6)); ax2 = fig.add_axes((0.56, 0.16, 0.39, 0.6))
    ax1.set_title("Mean openness, at founding → today", loc="left", fontsize=21, color=TEXT2); ax1.set_ylim(0, 4); ax1.set_xlim(-0.6, 1.6)
    ax1.set_xticks([0, 1]); ax1.set_xticklabels(["2010s databases (A)", "AI-era tools (J)"], fontsize=17, color=TEXT); ax1.grid(axis="x", visible=False)
    vals = [(2.72, 1.67), (2.29, 2.29)]; w = 0.32
    b0 = ax1.bar([-w / 2 - 0.01, 1 - w / 2 - 0.01], [0, 0], width=w, color=MUTED, label="At founding")
    b1 = ax1.bar([w / 2 + 0.01, 1 + w / 2 + 0.01], [0, 0], width=w, color=BLUE, label="Today"); ax1.legend(loc="upper right", fontsize=15)
    tx = [ax1.text(0, 0, "", ha="center", fontsize=17, color=TEXT) for _ in range(4)]
    ex = [("Weights & Biases → CoreWeave", 1.7e9, 2025), ("Anyscale → Nscale", 1.65e9, 2026), ("Modular → Qualcomm", 3.9e9, 2026),
          ("Replicate → Cloudflare", None, 2025), ("ggml.ai → Hugging Face", None, 2026), ("Chroma → Replit", None, 2026), ("Lightning AI ↔ Voltage Park", None, 2026)]
    ax2.axis("off"); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    ax2.text(0, 0.98, "Exits 2025–26 (no IPOs)", fontsize=21, color=TEXT2, va="top")
    lines = [ax2.text(0.02, 0.86 - i * 0.12, "", fontsize=18, color=TEXT, va="center") for i in range(len(ex))]
    def update(p):
        for i, (a, b) in enumerate(vals):
            q = ease((p - i * 0.15) / 0.4); b0[i].set_height(a * q); b1[i].set_height(b * q)
            for k, v, x in [(2 * i, a, b0[i].get_x() + w / 2), (2 * i + 1, b, b1[i].get_x() + w / 2)]:
                tx[k].set_position((x, v * q + 0.08)); tx[k].set_text(f"{v:.2f}" if q > 0.98 else "")
        for i, (name, v, y) in enumerate(ex):
            a = ease((p - 0.3 - i * 0.07) / 0.2)
            lines[i].set_text(f"{y}  {name}" + (f"  (${v/1e9:.2f}B)" if v else "") if a > 0.5 else "")
    render(fig, update, duration, mp4, png)

def p3_models(duration, mp4, png):
    sc.s_lanes(duration, mp4, png, ["I"], "AI-for-science models: licences over time", "Code, weights and data scored together (0–4); AlphaFold 3, Chai-1, ESM, Boltz, MatterGen, OMat24, MACE...", start=2019)

ACAD = [("Who owns the code", "Contractor-run national labs (LLNL) can hold copyright and open-source; code by federal employees has no domestic copyright (17 U.S.C. §105)"),
        ("Licensing rarely pays", "US university licensing income > $2.94B (2018, AUTM), yet most tech-transfer offices do not cover their costs"),
        ("Where the money is", "Stanford: all inventions earning > $10M net were licensed to inventor-founded startups"),
        ("The open-hardware path", "Publish the design; sell what publication does not supply: built and tested instruments, kits, support, training"),
        ("Examples", "OpenFlexure Industries · Bongo Tech sayansiScope · Opentrons · Foldscope · Sci-Bots DropBot · CERN OHR"),
        ("Our own kit", "CLSLab:Light (SDL-demo): two GroupGets rounds, 39 kits at $80 list, recorded in a 2024 review of low-cost SDLs")]
def p3_academic(duration, mp4, png):
    fig, ax = blank()
    ax.text(0.06, 0.92, "The academic path: tech transfer vs open release", fontsize=34, fontweight="bold", va="center")
    ax.text(0.06, 0.865, "Edison literature reviews (academic_techtransfer_open_source, academic_osh_commercialization)", fontsize=20, color=TEXT2, va="center")
    rows = []
    for i, (h, b) in enumerate(ACAD):
        yy = 0.75 - i * 0.115
        chip = FancyBboxPatch((0.06, yy - 0.035), 0.22, 0.07, boxstyle="round,pad=0.004,rounding_size=0.01", fc=CAT[i % 4], ec="none", alpha=0); ax.add_patch(chip)
        c = ax.text(0.17, yy, h, fontsize=17, fontweight="bold", ha="center", va="center", color=TEXT, alpha=0)
        t = ax.text(0.30, yy, textwrap.fill(b, 95), fontsize=17, va="center", color=TEXT, alpha=0, linespacing=1.3); rows.append((chip, c, t))
    ax.text(0.06, 0.04, "Sources: edison/academic_techtransfer_open_source_answer.md; edison/academic_osh_commercialization_answer.md (as cited by Edison).", fontsize=14, color=MUTED)
    def update(p):
        for i, r in enumerate(rows):
            a = ease((p - i * 0.1) / 0.2)
            for o in r: o.set_alpha(a)
    render(fig, update, duration, mp4, png)

def p3_agents(duration, mp4, png):
    t = pd.read_csv("data/byu_vcl_chars_by_month.csv", index_col=0); t = t.loc["2026-01":]
    fig, ax = fig_ax("Our own open record is now written mostly by AI agents", "Characters written per month in vertical-cloud-lab/byu-vcl issues, PRs and comments, by author type (gh api)",
                     rect=(0.08, 0.14, 0.84, 0.66))
    source_note(fig, "Source: data/byu_vcl_chars_by_month.csv from scripts/gh_dump.py on this repository (to 2026-11-24). Totals: Claude 6.4M characters, humans 1.4M.")
    x = np.arange(len(t)); ax.set_xticks(x); ax.set_xticklabels(t.index, fontsize=15)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1e6:.1f}M")); ax.set_ylim(0, (t.sum(axis=1).max()) * 1.15)
    series = [("Humans", BLUE), ("Claude", ORANGE), ("Copilot", AQUA)]
    bars = {}; bottom = np.zeros(len(t))
    for k, c in series:
        if k in t: bars[k] = ax.bar(x, [0] * len(t), bottom=bottom, color=c, label=k, edgecolor=SURFACE, linewidth=1.5); bottom = bottom + t[k].values
    ax.legend(loc="upper left")
    def update(p):
        bottom = np.zeros(len(t))
        for k, c in series:
            if k not in t: continue
            for i, b in enumerate(bars[k]):
                q = ease((p - i * 0.05) / 0.4); b.set_y(bottom[i]); b.set_height(t[k].values[i] * q)
            bottom = bottom + t[k].values * np.array([ease((p - i * 0.05) / 0.4) for i in range(len(t))])
    render(fig, update, duration, mp4, png)

TAKE3 = ["Forks always survived closing moves; they overtook the original when the vendor stopped investing in public.",
         "AI-era open-source tools stayed permissive, sold hosted layers, and were bought by compute and chip companies.",
         "AI-for-science models are more open than frontier LLMs, and restrictions trigger open clones within months.",
         "For academic labs: publish the design and data openly; earn from what publication does not supply.",
         "Agents now write most of an open lab's public record, so openness is cheaper and verification matters more."]
def p3_takeaways(duration, mp4, png):
    fig, ax = blank(); ax.text(0.06, 0.90, "What Part 3 adds", fontsize=40, fontweight="bold", va="center"); items = []
    for i, tt in enumerate(TAKE3):
        yy = 0.74 - i * 0.14
        n = ax.text(0.06, yy, f"{i+1}", fontsize=34, fontweight="bold", color=CAT[i % 4], va="center", alpha=0)
        tx = ax.text(0.11, yy, textwrap.fill(tt, 92), fontsize=22, va="center", color=TEXT, alpha=0, linespacing=1.25); items.append((n, tx))
    def update(p):
        for i, (n, tx) in enumerate(items):
            a = ease((p - i * 0.13) / 0.2); n.set_alpha(a); tx.set_alpha(a)
    render(fig, update, duration, mp4, png)

def p3_end(duration, mp4, png):
    fig, ax = blank()
    a1 = ax.text(0.5, 0.6, "Data, code and sources for all three parts", fontsize=42, fontweight="bold", ha="center", va="center")
    a2 = ax.text(0.5, 0.42, "github.com/vertical-cloud-lab/byu-vcl  ·  issue #380\noutputs/issue-380-open-science-ai", fontsize=26, color=BLUE, ha="center", va="center", linespacing=1.6)
    a3 = ax.text(0.5, 0.16, "Narration: Kokoro-82M (Apache-2.0). Charts: matplotlib. Made by Claude (Anthropic) for the BYU Vertical Cloud Lab.", fontsize=16, color=MUTED, ha="center")
    def update(p):
        for i, t in enumerate([a1, a2, a3]): t.set_alpha(ease((p - i * 0.2) / 0.3))
    render(fig, update, duration, mp4, png)

SCENES = {k: v for k, v in globals().items() if k.startswith("p3_")}
if __name__ == "__main__":
    name = sys.argv[1]; dur = float(sys.argv[2])
    if "--png-only" in sys.argv:
        fake = lambda fig, update, duration, out_mp4, out_png=None, build=0.7: (update(1.0), fig.savefig(out_png, dpi=DPI), plt.close(fig))
        globals()["render"] = fake; sc.render = fake
        SCENES[name](dur, None, f"{FIG}/{name}.png")
    else:
        SCENES[name](dur, f"{OUT}/{name}.mp4", f"{FIG}/{name}.png")
    print("done", name)
