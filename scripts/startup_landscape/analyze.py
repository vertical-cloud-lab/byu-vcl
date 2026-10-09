#!/usr/bin/env python3
"""Aggregate the per-company JSON files into figures and summary tables.

    python scripts/startup_landscape/analyze.py

Reads docs/startup-landscape/data/*.json (schema in docs/startup-landscape/README.md)
and writes docs/startup-landscape/figures/*.png plus
docs/startup-landscape/summary.md and docs/startup-landscape/data/funding_response.csv.
"""
import csv
import glob
import json
import math
import os
import re
import statistics
import sys
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "docs", "startup-landscape")
TODAY = date(2026, 10, 9)

# Reference palette from the dataviz skill; first three categorical slots
# validate all-pairs (scatter, small multiples), so no chart uses more than three.
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a"]
# Six adjacent slots for the stacked openings chart (adjacent pairs validated).
SLOTS6 = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
FUNCTIONS = ["ml-research", "materials-science", "lab-automation", "software-eng",
             "business-ops", "leadership"]

REGION = {"US": "United States", "UK": "Europe", "FR": "Europe", "DE": "Europe",
          "CH": "Europe", "NL": "Europe", "CA": "Canada & Asia", "CN": "Canada & Asia",
          "JP": "Canada & Asia", "SG": "Canada & Asia"}
REGIONS = ["United States", "Europe", "Canada & Asia"]
KIND = {
    "AI-for-materials (computational)": "Computational / software",
    "materials informatics software": "Computational / software",
    "self-driving lab": "Self-driving or cloud lab",
    "cloud lab": "Self-driving or cloud lab",
    "AI + high-throughput experimentation": "AI + high-throughput experimentation",
}
KINDS = ["Computational / software", "Self-driving or cloud lab",
         "AI + high-throughput experimentation"]
CAPITAL = {"equity", "jv-capital", "ipo"}  # grants, debt and contracts are listed, not summed
# Which headcount source to believe when several fall within a year of each other.
METHOD_RANK = ["registry", "team-page", "press", "job-ad", "linkedin-band", "openalex", "other"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-",
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 8,
    "axes.titlesize": 9, "axes.titleweight": "bold", "legend.frameon": False,
})


def parse_date(s):
    """'2025', '2025-09' or '2025-09-30' -> date (mid-period for partial dates)."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()[:10]
    try:
        parts = [int(p) for p in s.split("-")]
    except ValueError:
        if len(s) >= 6 and s[4] == "Q":
            y, q = int(s[:4]), int(s[5])
            return date(y, 3 * q - 1, 15)
        return None
    if len(parts) == 1:
        return date(parts[0], 7, 1)
    if len(parts) == 2:
        return date(parts[0], parts[1], 15)
    return date(*parts)


def quarter_mid(period):
    try:
        y, q = int(period[:4]), int(period[-1])
        return date(y, 3 * q - 1, 15)
    except (TypeError, ValueError, IndexError):
        return None


def money(m):
    if m is None:
        return "n/d"
    return f"${m / 1000:.2f}B" if m >= 1000 else f"${m:.0f}M" if m >= 10 else f"${m:.1f}M"


def load():
    cos = []
    for path in sorted(glob.glob(os.path.join(OUT, "data", "*.json"))):
        with open(path) as fh:
            d = json.load(fh)
        d["_funding"] = sorted(
            [{**f, "_d": parse_date(f.get("date"))} for f in d.get("funding") or []
             if parse_date(f.get("date"))], key=lambda f: f["_d"])
        hc = []
        for h in d.get("headcount") or []:
            when = parse_date(h.get("date"))
            v, lo, hi = h.get("value"), h.get("low"), h.get("high")
            if when is None or (v is None and lo is None):
                continue
            if v is None:
                hi = hi if hi else lo
                v = math.sqrt(max(lo, 1) * max(hi, 1))
            # A count of part of the company (one subsidiary, the leadership page) is plotted
            # hollow and never used as the company's team size.
            partial = h.get("partial") or re.search(
                r"not a total|leadership (team )?only|subsidiary only|uk (entity|subsidiary) only|"
                r"aggregator|unverified", h.get("note") or "", re.I)
            hc.append({**h, "_d": when, "_v": float(v), "_band": h.get("value") is None,
                       "_lo": lo, "_hi": hi, "_weak": bool(partial) or h.get("method") == "other"})
        d["_headcount"] = sorted(hc, key=lambda h: h["_d"])
        d["_postings"] = sorted(
            [{**p, "_d": quarter_mid(p.get("period"))} for p in d.get("postings") or []
             if quarter_mid(p.get("period")) and p.get("new_postings") is not None],
            key=lambda p: p["_d"])
        # Chart label: drop parentheticals in scripts the plotting font lacks (e.g. CJK names).
        d["_name"] = re.sub(r"\s*\([^)]*[^\x00-\x7f][^)]*\)", "", d["company"]).strip()
        d["_region"] = REGION.get(d.get("country"), "Canada & Asia")
        d["_kind"] = KIND.get(d.get("category"), "Computational / software")
        cos.append(d)
    return cos


def capital_to(co, when):
    return sum(f.get("amount_usd_m") or 0 for f in co["_funding"]
               if f["_d"] <= when and (f.get("type") or "equity") in CAPITAL)


def best_headcount(co):
    """Most trustworthy datapoint from the latest year of data: exact counts beat bands,
    then by METHOD_RANK, then the most recent."""
    hc = co["_headcount"]
    if not hc:
        return None
    hc = [h for h in hc if not h["_weak"]] or hc
    recent = [h for h in hc if (hc[-1]["_d"] - h["_d"]).days <= 120]

    def rank(h):
        m = h.get("method")
        return (h["_band"], METHOD_RANK.index(m) if m in METHOD_RANK else len(METHOD_RANK),
                -h["_d"].toordinal())
    return min(recent, key=rank)


def fmt_hc(h):
    if h is None:
        return "n/d"
    val = f'{int(h["value"])}' if not h["_band"] else f'{h["_lo"]}–{h["_hi"] or "?"}'
    return f'{val} ({h["_d"]:%Y-%m}, {h.get("method")})'


def short_round(f, width=34):
    r = (f.get("round") or "").replace("Series ", "").replace("extension", "ext.")
    r = r if len(r) <= width else r[: width - 1].rstrip() + "…"
    if f.get("type") in ("grant", "debt", "other") and f["type"] not in r.lower():
        r = f"{r} ({f['type']})".strip()
    return f'{money(f.get("amount_usd_m"))} {r}'.strip()


def timeline_grid(cos):
    """One panel per company: headcount over time, funding events as labelled hairlines."""
    cos = [c for c in cos if c["_headcount"] or c["_funding"]]
    cos.sort(key=lambda c: (-(capital_to(c, TODAY)), c["company"]))
    n, ncol = len(cos), 4
    nrow = math.ceil(n / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(13, 2.9 * nrow), squeeze=False)
    for ax, co in zip(axes.flat, cos):
        dates = [h["_d"] for h in co["_headcount"]] + [f["_d"] for f in co["_funding"]]
        start = min(dates + [parse_date(co.get("founded")) or min(dates)])
        x0 = date(start.year, 1, 1)
        ax.set_xlim(x0, date(2026, 12, 31))
        ymax = max([h["_hi"] or h["_v"] for h in co["_headcount"]] + [10]) * 1.35
        ax.set_ylim(0, ymax)
        for f in co["_funding"]:
            grant = (f.get("type") or "equity") not in CAPITAL
            ax.axvline(f["_d"], color=AXIS if grant else INK2, lw=0.7, zorder=1)
            ax.text(f["_d"], ymax * 0.98, " " + short_round(f), rotation=90, va="top",
                    ha="right", fontsize=5.6, color=MUTED if grant else INK2, zorder=2)
        exact = [h for h in co["_headcount"] if not h["_band"] and not h["_weak"]]
        weak = [h for h in co["_headcount"] if not h["_band"] and h["_weak"]]
        bands = [h for h in co["_headcount"] if h["_band"]]
        if exact:
            ax.plot([h["_d"] for h in exact], [h["_v"] for h in exact], "-", color=SLOTS[0],
                    lw=1.1, zorder=3, alpha=0.5)
            ax.plot([h["_d"] for h in exact], [h["_v"] for h in exact], "o", ms=4.2,
                    color=SLOTS[0], mec=SURFACE, mew=0.8, zorder=4)
        if weak:
            ax.plot([h["_d"] for h in weak], [h["_v"] for h in weak], "o", ms=4.2,
                    mfc=SURFACE, mec=SLOTS[0], mew=1.0, zorder=4)
        for h in bands:
            ax.vlines(h["_d"], h["_lo"], h["_hi"] or h["_lo"], color=SLOTS[0], lw=2.2,
                      alpha=0.45, zorder=3)
        ax.set_title(f'{co["_name"]} ({co.get("country")})', loc="left")
        ax.xaxis.set_major_locator(mdates.YearLocator(base=max(1, (2027 - x0.year) // 4)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(length=0, labelsize=6.5)
        if not co["_headcount"]:
            ax.text(0.5, 0.45, "no dated headcount found", transform=ax.transAxes,
                    ha="center", color=MUTED, fontsize=7)
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    fig.suptitle("Team size over time (filled: counted or stated; hollow: partial or aggregator; bars: size band) "
                 "against funding (dark lines: equity; light: grants, debt, contracts)",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.text(0.01, 0.005, "Sources per company in docs/startup-landscape/companies/. "
             "Panels sorted by capital raised.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.01, 1, 0.97))
    fig.savefig(os.path.join(OUT, "figures", "team_size_vs_funding_timeline.png"), dpi=170)
    plt.close(fig)


def scatter(cos):
    """Headcount against capital raised to date, one trajectory per company."""
    fig, ax = plt.subplots(figsize=(8.5, 6))
    for co in cos:
        pts = [(capital_to(co, h["_d"]), h["_v"]) for h in co["_headcount"] if not h["_weak"]]
        pts = [(x, y) for x, y in pts if x > 0 and y > 0]
        if not pts:
            continue
        col = SLOTS[REGIONS.index(co["_region"])]
        xs, ys = zip(*pts)
        ax.plot(xs, ys, "-", color=col, lw=0.9, alpha=0.45, zorder=2)
        ax.plot(xs, ys, "o", color=col, ms=4, mec=SURFACE, mew=0.8, zorder=3)
        ax.annotate(co["_name"], (xs[-1], ys[-1]), xytext=(4, 2), textcoords="offset points",
                    fontsize=6.5, color=INK2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    for k in (1, 3, 10):  # reference lines: $k M of capital per employee
        lo, hi = ax.get_xlim()
        xs = [lo, hi]
        ax.plot(xs, [x / k for x in xs], color=AXIS, lw=0.6, zorder=1)
    ax.set_xlim(left=max(ax.get_xlim()[0], 0.3))
    ax.set_ylim(bottom=max(ax.get_ylim()[0], 1))
    for k in (1, 3, 10):
        x = ax.get_xlim()[1] / 1.6
        if ax.get_ylim()[0] < x / k < ax.get_ylim()[1]:
            ax.text(x, x / k, f"${k}M per head", fontsize=6.5, color=MUTED, ha="right", va="bottom")
    ax.set_xlabel("Capital raised to date (USD M, log; equity and JV capital, excluding grants and debt)")
    ax.set_ylabel("Team size (log; band midpoints where only a size band is known)")
    ax.set_title("Team size against capital raised", loc="left")
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=r) for c, r in zip(SLOTS, REGIONS)]
    ax.legend(handles=handles, loc="upper left", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "figures", "team_size_vs_capital.png"), dpi=170)
    plt.close(fig)


def postings_grid(cos):
    cos = [c for c in cos if len(c["_postings"]) >= 2]
    if not cos:
        return
    cos.sort(key=lambda c: -sum(p["new_postings"] for p in c["_postings"]))
    ncol = 3
    nrow = math.ceil(len(cos) / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(12, 2.6 * nrow), squeeze=False)
    for ax, co in zip(axes.flat, cos):
        xs = [p["_d"] for p in co["_postings"]]
        ys = [p["new_postings"] for p in co["_postings"]]
        ax.bar(xs, ys, width=70, color=SLOTS[0], zorder=3)
        top = max(ys) * 1.45
        ax.set_ylim(0, top)
        lo = min(xs + [f["_d"] for f in co["_funding"] if f["_d"] >= min(xs) - (max(xs) - min(xs))])
        ax.set_xlim(date(lo.year, 1, 1), date(2026, 12, 31))
        for f in co["_funding"]:
            if f["_d"] < date(lo.year, 1, 1):
                continue
            ax.axvline(f["_d"], color=INK2, lw=0.7, zorder=1)
            ax.text(f["_d"], top * 0.98, " " + short_round(f), rotation=90, va="top", ha="right",
                    fontsize=5.6, color=INK2)
        ax.set_title(co["_name"], loc="left")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(length=0, labelsize=6.5)
    for ax in list(axes.flat)[len(cos):]:
        ax.axis("off")
    fig.suptitle("Job postings first captured per quarter (Wayback/ATS; a lower bound) against funding rounds",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(OUT, "figures", "postings_vs_funding.png"), dpi=170)
    plt.close(fig)


def per_head(cos):
    rows = []
    for co in cos:
        h = best_headcount(co)
        cap = capital_to(co, TODAY)
        if h and cap > 0:
            rows.append((cap / h["_v"], co))
    if not rows:
        return
    rows.sort(key=lambda r: r[0])
    fig, ax = plt.subplots(figsize=(8, 0.32 * len(rows) + 1.2))
    ys = range(len(rows))
    ax.barh(list(ys), [r[0] for r in rows], height=0.62,
            color=[SLOTS[KINDS.index(r[1]["_kind"])] for r in rows], zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([r[1]["_name"] for r in rows], fontsize=7, color=INK2)
    for y, (v, co) in zip(ys, rows):
        ax.text(v, y, f"  {v:.2f}" if v < 10 else f"  {v:.0f}", va="center", fontsize=6.5, color=INK2)
    ax.set_xscale("log")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Capital raised to date per team member (USD M, log)")
    ax.set_title("Capital per head at the latest team-size datapoint", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=k) for c, k in zip(SLOTS, KINDS)]
    ax.legend(handles=handles, loc="lower right", fontsize=7)
    ax.tick_params(length=0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "figures", "capital_per_head.png"), dpi=170)
    plt.close(fig)


def openings_by_function(cos):
    rows = []
    for co in cos:
        op = co.get("current_openings") or {}
        byf = {k: v for k, v in (op.get("by_function") or {}).items() if v}
        if op.get("count"):
            other = max(op["count"] - sum(byf.get(f, 0) for f in FUNCTIONS), 0)
            rows.append((co, [byf.get(f, 0) for f in FUNCTIONS], other))
    if not rows:
        return []
    rows.sort(key=lambda r: sum(r[1]) + r[2])
    fig, ax = plt.subplots(figsize=(8.5, 0.34 * len(rows) + 1.4))
    for y, (co, vals, other) in enumerate(rows):
        left = 0
        for f, v, col in zip(FUNCTIONS, vals, SLOTS6):
            if v:
                ax.barh(y, v, left=left, height=0.62, color=col, edgecolor=SURFACE, lw=1.2, zorder=3)
                left += v
        if other:
            ax.barh(y, other, left=left, height=0.62, color=AXIS, edgecolor=SURFACE, lw=1.2, zorder=3)
            left += other
        ax.text(left, y, f"  {left}", va="center", fontsize=6.5, color=INK2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0]["_name"] for r in rows], fontsize=7, color=INK2)
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    ax.set_xlabel("Open roles on the public job board, 9 Oct 2026")
    ax.set_title("What they are hiring for now", loc="left")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=f) for c, f in zip(SLOTS6, FUNCTIONS)]
    handles.append(plt.Rectangle((0, 0), 1, 1, color=AXIS, label="unclassified"))
    ax.legend(handles=handles, loc="lower right", fontsize=6.5, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "figures", "openings_by_function.png"), dpi=170)
    plt.close(fig)
    return rows


BACKGROUND_TAGS = {
    "PhD": r"\bph\.?d|doctor",
    "professor / faculty": r"professor|faculty|\blecturer",
    "frontier AI lab / big tech": r"openai|deepmind|google|\bmeta\b|facebook|microsoft|anthropic|nvidia|amazon|apple|ibm research",
    "national lab": r"national lab|nrel|argonne|lbnl|berkeley lab|ornl|oak ridge|pnnl|sandia|los alamos|llnl|lawrence livermore|nist\b|riken|aist",
    "chemicals / materials industry": r"basf|\bdow\b|dupont|3m\b|johnson matthey|corning|saint-gobain|merck|evonik|toyota|panasonic|tesla|eneos|mitsui|shell|bp\b|exxon|chevron|unilever|procter|novartis|pfizer|astrazeneca",
    "prior startup / founder": r"founded|co-founder|cofounder|startup|start-up",
    "finance / consulting": r"mckinsey|bain|bcg|boston consulting|goldman|morgan stanley|venture|investment|banker|consult",
}


def backgrounds(cos):
    import re
    lines = ["| Company | Leaders tracked | " + " | ".join(BACKGROUND_TAGS) + " |",
             "|---|---|" + "---|" * len(BACKGROUND_TAGS)]
    totals = {k: 0 for k in BACKGROUND_TAGS}
    n_all = 0
    for co in sorted(cos, key=lambda c: c["company"]):
        ppl = [p for p in co.get("people") or [] if p.get("seniority") in ("founder", "exec", "head")]
        if not ppl:
            continue
        n_all += len(ppl)
        counts = []
        for k, rx in BACKGROUND_TAGS.items():
            c = sum(1 for p in ppl if re.search(rx, (p.get("background") or "").lower()))
            totals[k] += c
            counts.append(str(c) if c else "·")
        lines.append(f'| {co["company"]} | {len(ppl)} | ' + " | ".join(counts) + " |")
    lines.append(f"| **All** | **{n_all}** | " + " | ".join(f"**{v}**" for v in totals.values()) + " |")
    return "\n".join(lines)


TITLE_RULES = [  # first match wins
    ("leadership", r"\bhead of|\bchief\b|\bvp\b|vice president|\bdirector\b|general manager"),
    ("lab-automation", r"automation|robot|mechanical|mechatron|electrical|equipment|technician|hardware|"
                       r"controls|process engineer|process safety|facilit|\behs\b|safety|maintenance|"
                       r"lab operations|laboratory|instrument"),
    ("ml-research", r"machine learning|\bml\b|\bai\b|\brl\b|deep learning|\bllm|pretrain|midtrain|"
                    r"post-?train|scaling|research scientist, data|data scien|reinforcement"),
    ("materials-science", r"chemist|material|synthes|characteri|thin film|electrochem|catal|polymer|"
                          r"physic|condensed matter|computational scientist|\bdft\b|simulation|"
                          r"research associate|scientist|crystal|semiconductor|battery|powder"),
    ("software-eng", r"software|engineer|developer|devops|infrastructure|platform|front-?end|back-?end|"
                     r"full[- ]?stack|systems|security|\bsre\b"),
]


def classify(title):
    t = (title or "").lower()
    for func, rx in TITLE_RULES:
        if re.search(rx, t):
            return func
    return "business-ops"


def board_tokens(co):
    """(vendor, token) pairs for the company's public job board, read from the cited source URL."""
    src = ((co.get("current_openings") or {}).get("source") or "")
    m = re.search(r"ashbyhq\.com/(?:posting-api/job-board/)?([^/?#]+)", src)
    if m:
        return [("ashby", m.group(1))]
    m = re.search(r"greenhouse\.io/(?:v1/boards/)?([^/?#]+)", src)
    if m and m.group(1) not in ("embed",):
        return [("greenhouse", m.group(1))]
    return []


def posted_pay(cos):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch  # noqa: E402

    rows = []
    for co in cos:
        for vendor, token in board_tokens(co):
            try:
                jobs = fetch.pay(vendor, token)
            except Exception as err:  # a board can vanish between fetches
                print(f"pay: {co['company']}: {err}", file=sys.stderr)
                continue
            for j in jobs:
                if j.get("interval") not in (None, "1 YEAR") or not j.get("min"):
                    continue
                rows.append({"company": co["company"], "title": (j.get("title") or "").strip(),
                             "function": classify(j.get("title")), "location": j.get("location"),
                             "currency": j.get("currency"), "min": j["min"], "max": j.get("max") or j["min"],
                             "url": j.get("url")})
    if not rows:
        return []
    with open(os.path.join(OUT, "data", "posted_pay.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    usd = [r for r in rows if r["currency"] == "USD"]
    funcs = [f for f in FUNCTIONS if any(r["function"] == f for r in usd)]
    if usd:
        fig, ax = plt.subplots(figsize=(8.5, 0.75 * len(funcs) + 1.3))
        for i, f in enumerate(funcs):
            rs = sorted((r for r in usd if r["function"] == f), key=lambda r: (r["min"] + r["max"]) / 2)
            n = len(rs)
            for k, r in enumerate(rs):
                y = i + (k - (n - 1) / 2) * min(0.6 / max(n - 1, 1), 0.08)
                ax.plot([r["min"] / 1000, r["max"] / 1000], [y, y], color=SLOTS[0], lw=1.4,
                        alpha=0.55, solid_capstyle="round", zorder=3)
            med = statistics.median((r["min"] + r["max"]) / 2 for r in rs) / 1000
            ax.plot([med], [i], "|", ms=16, mew=2, color=INK, zorder=4)
            ax.text(med, i + 0.36, f"median ${med:.0f}K · n={n}", ha="center", fontsize=6.5, color=INK2)
        ax.set_yticks(range(len(funcs)))
        ax.set_yticklabels(funcs, fontsize=7.5, color=INK2)
        ax.set_ylim(-0.6, len(funcs) - 0.4)
        ax.grid(axis="y", visible=False)
        ax.tick_params(length=0)
        ax.set_xlabel("Posted base salary range, USD thousands per year (each line is one open role)")
        ax.set_title("What the open roles pay (US postings with a published range, 9 Oct 2026)", loc="left")
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, "figures", "posted_pay_by_function.png"), dpi=170)
        plt.close(fig)
    return rows


def pay_table(rows):
    if not rows:
        return "No posted pay ranges found."
    lines = ["| Company | Role | Function | Location | Posted range |", "|---|---|---|---|---|"]
    sym = {"USD": "$", "EUR": "€", "GBP": "£"}
    for r in sorted(rows, key=lambda r: (r["company"], FUNCTIONS.index(r["function"]), -r["max"])):
        rng = f'{sym.get(r["currency"], "")}{r["min"] / 1000:.0f}K–{r["max"] / 1000:.0f}K'
        lines.append(f'| {r["company"]} | [{r["title"]}]({r["url"]}) | {r["function"]} | {r["location"] or ""} | {rng} |')
    return "\n".join(lines)


def funding_response(cos):
    """For each equity round: postings in the two quarters before vs after, and team size
    at the nearest datapoints within 18 months either side."""
    rows = []
    for co in cos:
        for f in co["_funding"]:
            if (f.get("type") or "equity") not in CAPITAL:
                continue
            d = f["_d"]
            before = sum(p["new_postings"] for p in co["_postings"] if 0 < (d - p["_d"]).days <= 183)
            after = sum(p["new_postings"] for p in co["_postings"] if 0 <= (p["_d"] - d).days <= 183)
            hb = [h for h in co["_headcount"] if not h["_weak"] and 0 <= (d - h["_d"]).days <= 548]
            ha = [h for h in co["_headcount"] if not h["_weak"] and 0 < (h["_d"] - d).days <= 548]
            rows.append({
                "company": co["company"], "date": f["_d"].isoformat(), "round": f.get("round"),
                "amount_usd_m": f.get("amount_usd_m"),
                "postings_6mo_before": before if co["_postings"] else "",
                "postings_6mo_after": after if co["_postings"] else "",
                "team_before": round(hb[-1]["_v"]) if hb else "",
                "team_before_date": hb[-1]["_d"].isoformat() if hb else "",
                "team_after": round(ha[-1]["_v"]) if ha else "",
                "team_after_date": ha[-1]["_d"].isoformat() if ha else "",
            })
    with open(os.path.join(OUT, "data", "funding_response.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["company"])
        w.writeheader()
        w.writerows(rows)
    return rows


def summary(cos):
    lines = [
        "| Company | HQ | Founded | Type | Status | Capital raised | Latest round | Team size (date, method) | Open roles (2026-10-09) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for co in sorted(cos, key=lambda c: -capital_to(c, TODAY)):
        eq = [f for f in co["_funding"] if (f.get("type") or "equity") in CAPITAL]
        last = eq[-1] if eq else None
        grants = sum(f.get("amount_usd_m") or 0 for f in co["_funding"] if f.get("type") == "grant")
        cap = money(capital_to(co, TODAY)) + (f" (+{money(grants)} grants)" if grants else "")
        latest = f'{short_round(last)}, {last["_d"]:%Y-%m}' if last else "n/d"
        op = co.get("current_openings") or {}
        lines.append(
            f'| [{co["company"]}](companies/{co["slug"]}.md) | {co.get("hq", "")} | {co.get("founded", "")} '
            f'| {co["_kind"]} | {co.get("status", "")} | {cap} | {latest} | {fmt_hc(best_headcount(co))} '
            f'| {op.get("count") if op and op.get("count") is not None else "n/d"} |')
    opening_rows = ["| Company | " + " | ".join(FUNCTIONS) + " | unclassified | total |",
                    "|---|" + "---|" * (len(FUNCTIONS) + 2)]
    for co, vals, other in sorted(openings_by_function(cos), key=lambda r: -(sum(r[1]) + r[2])):
        opening_rows.append(f'| {co["company"]} | ' + " | ".join(str(v) if v else "·" for v in vals)
                            + f" | {other or '·'} | {sum(vals) + other} |")
    with open(os.path.join(OUT, "summary.md"), "w") as fh:
        fh.write("<!-- generated by scripts/startup_landscape/analyze.py; do not edit by hand -->\n\n")
        fh.write("## Companies\n\nCapital raised counts equity, JV capital and IPO proceeds; grants and debt are "
                 "listed separately in each profile. Team size is the latest counted figure within two "
                 "years of the latest datapoint, else the latest size band.\n\n")
        fh.write("\n".join(lines) + "\n\n")
        fh.write("## Open roles by function (table view of `figures/openings_by_function.png`)\n\n")
        fh.write("\n".join(opening_rows) + "\n\n")
        fh.write("## Leadership backgrounds\n\nFounders, executives and heads tracked in each profile, counted "
                 "by keywords in their published bios. A person can carry several tags; `·` is zero.\n\n")
        fh.write(backgrounds(cos) + "\n\n")
        fh.write("## Posted pay\n\nBase salary ranges published on the job boards (pay-transparency laws in CA, "
                 "NY, CO and WA require them). Role functions are assigned from the title by keyword "
                 "(`TITLE_RULES` in `analyze.py`).\n\n")
        fh.write(pay_table(posted_pay(cos)) + "\n")
    return "\n".join(lines)


def main():
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    cos = load()
    print(f"{len(cos)} companies")
    timeline_grid(cos)
    scatter(cos)
    postings_grid(cos)
    per_head(cos)
    funding_response(cos)
    print(summary(cos))


if __name__ == "__main__":
    main()
