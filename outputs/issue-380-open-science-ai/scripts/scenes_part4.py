#!/usr/bin/env python3
"""Part 4 scenes: corrections after the independent review (REVIEW_FINDINGS.md).
Usage: python scenes_part4.py <scene> <dur> [--png-only]"""
import sys, textwrap, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
OUT = "video/scenes"; FIG = "figures"


def blank():
    fig = plt.figure(figsize=(W, H), dpi=DPI); ax = fig.add_axes((0, 0, 1, 1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); return fig, ax


def p4_title(duration, mp4, png):
    fig, ax = blank()
    t1 = ax.text(0.08, 0.60, "The value of open science\nin the age of AI — Part 4", fontsize=60, fontweight="bold", va="center", linespacing=1.15)
    t2 = ax.text(0.08, 0.36, "Corrections after an independent review: 39 issues found, all resolved in the report", fontsize=26, color=TEXT2)
    t3 = ax.text(0.08, 0.18, "Resolution log: REVIEW_FINDINGS.md\ngithub.com/vertical-cloud-lab/byu-vcl · issue #380", fontsize=19, color=MUTED, linespacing=1.6)
    bar = ax.plot([0.08, 0.08], [0.30, 0.30], color=BLUE, lw=8, solid_capstyle="butt")[0]

    def update(p):
        for t, a in [(t1, ease(p / 0.4)), (t2, ease((p - 0.3) / 0.4)), (t3, ease((p - 0.55) / 0.4))]: t.set_alpha(a)
        bar.set_data([0.08, 0.08 + 0.5 * ease(p / 0.8)], [0.30, 0.30])
    render(fig, update, duration, mp4, png)


def p4_kinds(duration, mp4, png):
    """Founding-era gap: first version vs corrected raw vs adjusted for starting openness (point and 95% CI)."""
    rows = [("Earlier videos (infrastructure\ncounted as pre-2000 firms)", -0.67, -1.04, -0.31, MUTED),
            ("Corrected grouping, raw gap", -0.61, -0.97, -0.24, ORANGE),
            ("Corrected, adjusted for\nstarting openness", -0.09, -0.45, 0.28, BLUE)]
    fig, ax = fig_ax("Do VC-era firms close up? Mostly a starting-point effect",
                     "Change in openness (0–4 scale), firms founded since 2000 minus firms founded before 2000, with 95% CI",
                     rect=(0.30, 0.30, 0.62, 0.50))
    source_note(fig, "Source: data/kinds_corrected.csv (scripts/kinds_corrected.py; bootstrap CIs, OLS of change on era plus starting score). Public and non-profit infrastructure classified first.")
    ax.set_xlim(-1.2, 0.5); ax.set_ylim(-0.6, 2.6); ax.invert_yaxis()
    ax.set_yticks(range(3)); ax.set_yticklabels([r[0] for r in rows], fontsize=18, color=TEXT); ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False); ax.axvline(0, color=TEXT2, lw=1.2, ls=(0, (4, 4)))
    ax.set_xlabel("difference in mean change of openness (points)")
    segs = [ax.plot([], [], color=c, lw=4, solid_capstyle="round")[0] for *_, c in rows]
    dots = [ax.plot([], [], "o", ms=14, color=c, mec=SURFACE, mew=2.5, zorder=5)[0] for *_, c in rows]
    labs = [ax.text(0, i - 0.32, "", fontsize=17, color=TEXT, ha="center") for i in range(3)]
    note = fig.text(0.30, 0.17, "", fontsize=20, color=TEXT2)

    def update(p):
        for i, (lab, m, lo, hi, c) in enumerate(rows):
            a = ease((p - i * 0.25) / 0.3)
            if a <= 0: segs[i].set_data([], []); dots[i].set_data([], []); labs[i].set_text(""); continue
            segs[i].set_data([m - (m - lo) * a, m + (hi - m) * a], [i, i]); dots[i].set_data([m], [i])
            labs[i].set_position((m, i - 0.32)); labs[i].set_text(f"{m:+.2f}  [{lo:+.2f}, {hi:+.2f}]".replace("-", "−") if a >= 1 else "")
        note.set_text("VC-era firms started far more open (1.80 vs 0.68): open starters close, closed starters open." if p >= 0.85 else "")
    render(fig, update, duration, mp4, png)


ORDER = ["Commercial OSS software", "Big Tech & AI labs", "Hardware",
         "Lab automation & AI-for-science firms", "Science software & infrastructure", "AM, lab instruments & publishing"]


def p4_six(duration, mp4, png):
    t = pd.read_csv("data/openness_by_year_six_sectors.csv")
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.text(0.05, 0.935, "Science splits into closed firms and open infrastructure", fontsize=32, fontweight="bold", color=TEXT, va="center")
    fig.text(0.05, 0.885, "Mean openness (0–4) of case-study organizations operating each year (n ≥ 5). Gray: the other five sectors.", fontsize=18, color=TEXT2, va="center")
    fig.text(0.05, 0.03, "Source: data/openness_by_year_six_sectors.csv, rebuilt from case files A–G. Survivor sample, not a census; yearly means also move as firms enter.",
             fontsize=13, color=MUTED, va="center")
    axes = []
    for i, s in enumerate(ORDER):
        r, c = divmod(i, 3)
        ax = fig.add_axes((0.05 + c * 0.315, 0.50 - r * 0.40, 0.27, 0.30))
        ax.set_xlim(1995, 2026.5); ax.set_ylim(0, 4); ax.set_yticks([0, 1, 2, 3, 4]); ax.set_xticks([2000, 2010, 2020]); ax.tick_params(labelsize=15)
        if c: ax.set_yticklabels([])
        if r == 0: ax.set_xticklabels([])
        ax.set_title(s, fontsize=19, color=TEXT, loc="left", pad=8); axes.append(ax)
    ctx, main, lab, dot = {}, {}, {}, {}
    for ax, s in zip(axes, ORDER):
        ctx[s] = [ax.plot([], [], color=MUTED, lw=1.5, alpha=0.55)[0] for o in ORDER if o != s]
        main[s], = ax.plot([], [], color=BLUE, lw=LW)
        dot[s], = ax.plot([], [], "o", ms=9, color=BLUE, mec=SURFACE, mew=2, zorder=5)
        lab[s] = ax.text(2026.3, 3.85, "", fontsize=16, color=TEXT, va="top", ha="right")

    def ser(s, xmax): return t[(t.sector == s) & (t.n >= 5) & (t.year <= xmax)]

    def update(p):
        xmax = 1995 + p * 31.5
        for s in ORDER:
            for ln, o in zip(ctx[s], [o for o in ORDER if o != s]):
                x = ser(o, xmax); ln.set_data(x.year, x.mean_open)
            x = ser(s, xmax); main[s].set_data(x.year, x.mean_open)
            if p >= 1 and len(x):
                last = x.iloc[-1]; lab[s].set_text(f"2026: {last.mean_open:.2f} (n={int(last.n)})"); dot[s].set_data([last.year], [last.mean_open])
            else:
                lab[s].set_text(""); dot[s].set_data([], [])
    render(fig, update, duration, mp4, png)


def p4_rates(duration, mp4, png):
    d = pd.read_csv("data/licence_events_per_org_year.csv")
    a = d[d.scope == "all A-F"].set_index("window")
    fig, ax = fig_ax("Licence changes rose after 2020, per organization-year too",
                     "Dated licence or access changes per 100 organization-years, groups A–F (122 organizations)",
                     rect=(0.10, 0.16, 0.62, 0.64))
    source_note(fig, "Source: data/licence_events_per_org_year.csv (scripts/licence_rate_per_org_year.py). Exposure = years operating inside each window. Recent changes are better documented online.")
    wins = ["2010-19", "2020-26"]; x = np.arange(2); w = 0.34
    ax.set_xlim(-0.6, 1.6); ax.set_ylim(0, 5.2); ax.set_xticks(x); ax.set_xticklabels(["2010–19", "2020–26"], fontsize=20, color=TEXT)
    ax.grid(axis="x", visible=False); ax.set_ylabel("changes per 100 organization-years")
    bc = ax.bar(x - w / 2 - 0.01, [0, 0], width=w, color=ORANGE, label="Closing moves")
    bo = ax.bar(x + w / 2 + 0.01, [0, 0], width=w, color=BLUE, label="Opening moves")
    ax.legend(loc="upper left", fontsize=17)
    vc = [a.loc[k, "closing_per_100_org_years"] for k in wins]; vo = [a.loc[k, "opening_per_100_org_years"] for k in wins]
    tc = [ax.text(xx - w / 2 - 0.01, 0, "", ha="center", va="bottom", fontsize=18, color=TEXT) for xx in x]
    to = [ax.text(xx + w / 2 + 0.01, 0, "", ha="center", va="bottom", fontsize=18, color=TEXT) for xx in x]
    side = fig.text(0.75, 0.62, "", fontsize=19, color=TEXT2, va="top", linespacing=1.5)
    b = d[d.scope == "founded before 2010"].set_index("window")
    tot_a = [round(vc[i] + vo[i], 1) for i in range(2)]
    tot_b = [round(b.loc[k, "closing_per_100_org_years"] + b.loc[k, "opening_per_100_org_years"], 1) for k in wins]

    def update(p):
        e = ease(p / 0.6)
        for i in range(2):
            bc[i].set_height(vc[i] * e); bo[i].set_height(vo[i] * e)
            tc[i].set_position((x[i] - w / 2 - 0.01, vc[i] * e + 0.06)); to[i].set_position((x[i] + w / 2 + 0.01, vo[i] * e + 0.06))
            tc[i].set_text(f"{vc[i]:.1f}" if p >= 0.6 else ""); to[i].set_text(f"{vo[i]:.1f}" if p >= 0.6 else "")
        side.set_text(f"All changes:\n{tot_a[0]} → {tot_a[1]} per 100\n\nFounded before 2010 only:\n{tot_b[0]} → {tot_b[1]} per 100" if p >= 0.75 else "")
    render(fig, update, duration, mp4, png)


FIXES = [("Forks", "All eight forks we checked survive, but most closing moves drew no fork at all. Part 3 said forks always survived."),
         ("AI-era startups", "None has relicensed yet, but they are young: by age 4, 0 of 17 vs 3 of 17 firms from the relicensing era."),
         ("Science models", "2.8 vs 1.6 is indicative only: model releases and whole companies were scored on different rubric readings."),
         ("Open hardware", "The 87% saving is material cost, for the ~45 designs with a commercial comparator; labour excluded."),
         ("Protein Data Bank", "$5.5B a year is research time spent with it (use value); the conservative return is still ~160× its cost.")]


def p4_other(duration, mp4, png):
    fig, ax = blank(); ax.text(0.06, 0.90, "Smaller corrections", fontsize=40, fontweight="bold", va="center"); items = []
    for i, (head, body) in enumerate(FIXES):
        yy = 0.75 - i * 0.14
        h = ax.text(0.06, yy, head, fontsize=24, fontweight="bold", color=TEXT, va="center", alpha=0)
        tx = ax.text(0.27, yy, textwrap.fill(body, 78), fontsize=21, va="center", color=TEXT2, alpha=0, linespacing=1.25); items.append((h, tx))

    def update(p):
        for i, (h, tx) in enumerate(items):
            a = ease((p - i * 0.13) / 0.2); h.set_alpha(a); tx.set_alpha(a)
    render(fig, update, duration, mp4, png)


def p4_end(duration, mp4, png):
    fig, ax = blank()
    a1 = ax.text(0.5, 0.6, "The written report is the current version", fontsize=42, fontweight="bold", ha="center", va="center")
    a2 = ax.text(0.5, 0.42, "github.com/vertical-cloud-lab/byu-vcl  ·  issue #380\noutputs/issue-380-open-science-ai  ·  REVIEW_FINDINGS.md  ·  VIDEO_NOTES.md",
                 fontsize=24, color=BLUE, ha="center", va="center", linespacing=1.6)
    a3 = ax.text(0.5, 0.16, "Narration: Kokoro-82M (Apache-2.0). Charts: matplotlib. Made by Claude (Anthropic) for the BYU Vertical Cloud Lab.", fontsize=16, color=MUTED, ha="center")

    def update(p):
        for i, t in enumerate([a1, a2, a3]): t.set_alpha(ease((p - i * 0.2) / 0.3))
    render(fig, update, duration, mp4, png)


SCENES = {k: v for k, v in globals().items() if k.startswith("p4_")}
if __name__ == "__main__":
    name = sys.argv[1]; dur = float(sys.argv[2])
    if "--png-only" in sys.argv:
        fake = lambda fig, update, duration, out_mp4, out_png=None, build=0.7: (update(1.0), fig.savefig(out_png, dpi=DPI), plt.close(fig))
        globals()["render"] = fake
        SCENES[name](dur, None, f"{FIG}/{name}.png")
    else:
        SCENES[name](dur, f"{OUT}/{name}.mp4", f"{FIG}/{name}.png")
    print("done", name)
