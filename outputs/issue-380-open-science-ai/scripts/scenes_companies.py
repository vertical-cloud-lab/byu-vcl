#!/usr/bin/env python3
"""Animated scenes from the case-study dataset (companies/companies_master.csv, companies/events.csv)
and market prices (data/prices_weekly_close.csv). Usage: python scenes_companies.py <scene> <dur> [--png-only]"""
import sys, re, json, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
import viz_style
from viz_style import *
import matplotlib.ticker as mt
from matplotlib.patches import Patch
OUT = "video/scenes"; FIG = "figures"
M = pd.read_csv("companies/companies_master.csv"); E = pd.read_csv("companies/events.csv")
SHORT = {}
PREFIX = {"AlphaFold 2": "AlphaFold 2 / AFDB", "AlphaFold 3": "AlphaFold 3", "Boltz": "Boltz-1/2", "Chai-1": "Chai-1", "CHGNet": "CHGNet",
          "ESM protein": "ESM models", "Evo 2": "Evo 2 (Arc)", "GNoME": "GNoME (DeepMind)", "M3GNet": "M3GNet / MatGL", "MACE": "MACE models",
          "Matbench": "Matbench (Discovery)", "MatterGen": "MatterGen (Microsoft)", "MatterSim": "MatterSim (Microsoft)", "Meta FAIR Chemistry": "Meta FAIR Chemistry",
          "NVIDIA BioNeMo": "NVIDIA BioNeMo/ALCHEMI", "OpenFold": "OpenFold / OpenFold3", "Orb models": "Orb (Orbital)", "RoseTTAFold": "RoseTTAFold / RFdiffusion",
          "SevenNet": "SevenNet",
          "Pivotal": "Pivotal / SpringSource", "RCSB Protein Data Bank": "Protein Data Bank (RCSB)", "LAMMPS": "LAMMPS (Sandia)",
          "DOE CODE": "DOE CODE (national labs)", "The Apache Software": "Apache Software Fdn.", "MySQL AB": "MySQL AB", "Google DeepMind": "DeepMind (science)",
          "International Business": "IBM", "Alibaba": "Alibaba (Qwen)", "Allen Institute": "Ai2", "Raspberry Pi": "Raspberry Pi", "Open Compute": "Open Compute Project",
          "RISC-V": "RISC-V International", "Tiger Data": "Timescale / Tiger Data", "The Materials Project": "Materials Project", "The Linux Foundation": "Linux Foundation",
          "The HDF Group": "HDF Group", "Zenodo": "Zenodo (CERN)", "OpenFlexure": "OpenFlexure", "Jubilee": "Jubilee (UW)", "Quantum ESPRESSO": "Quantum ESPRESSO",
          "Recursion": "Recursion", "Opentrons": "Opentrons", "Seeed": "Seeed Studio", "LulzBot": "LulzBot / Aleph Objects", "UltiMaker": "UltiMaker", "Bambu": "Bambu Lab",
          "Creality": "Creality", "Arduino": "Arduino", "MakerBot": "MakerBot", "Prusa": "Prusa Research", "Sentry": "Sentry", "Cloudera": "Cloudera / Hortonworks",
          "Redis": "Redis", "Elastic": "Elastic", "Confluent": "Confluent", "HashiCorp": "HashiCorp", "Docker": "Docker", "Neo4j": "Neo4j", "InfluxData": "InfluxData",
          "Kong": "Kong", "Lightbend": "Lightbend (Akka)", "MariaDB": "MariaDB", "MongoDB": "MongoDB", "Grafana": "Grafana Labs", "xAI": "xAI", "OpenAI": "OpenAI",
          "Anthropic": "Anthropic", "Meta Platforms": "Meta", "Alphabet": "Google", "Amazon": "Amazon / AWS", "Mistral": "Mistral AI", "EleutherAI": "EleutherAI",
          "Stability": "Stability AI", "Microsoft": "Microsoft", "NVIDIA": "NVIDIA", "Oracle": "Oracle", "Apple": "Apple", "DeepSeek": "DeepSeek"}
def short(n):
    for k, v in PREFIX.items():
        if str(n).startswith(k): return v
    n = re.sub(r"\s*\(.*?\)", "", str(n)); n = re.sub(r",? (Inc|LLC|Ltd|plc|S\.A\.|SAS|a\.s\.|GmbH|PBC|Limited|Corporation|Company|Co\.,? Ltd|N\.V\.)\.?$", "", n)
    n = n.replace("Platforms, Inc.", "").replace(", Inc.", "").replace(" Inc.", "").strip(" ,")
    return {"MySQL AB and Sun Microsystems": "MySQL AB", "Alphabet": "Google", "Meta Platforms": "Meta", "International Business Machines": "IBM",
            "Pivotal Software, Inc. and SpringSource": "Pivotal", "Shenzhen Tuozhu Technology": "Bambu Lab"}.get(n, n)[:26]
OPEN_COL = {4: "#86b6ef", 3: BLUE, 2: "#77766f", 1: "#b85c5c", 0: RED}
OPEN_LAB = {4: "4 Open + open governance", 3: "3 Open source", 2: "2 Open core / mixed", 1: "1 Restricted / source-available", 0: "0 Closed"}
def money(v):
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9: return f"${v/1e9:.1f}B" if v < 1e10 else f"${v/1e9:.0f}B"
    return f"${v/1e6:.0f}M"

# ---------------------------------------------------------------- commercial OSS values
def s_values(duration, mp4, png):
    d = M[M.group.isin(["A", "B"]) & M.latest_value_usd.notna() & (M.latest_value_usd > 1e8)].copy()
    d["lab"] = d["name"].map(short); d = d.sort_values("latest_value_usd", ascending=True)
    d["oc"] = d.openness_current.fillna(2).astype(int)
    fig, ax = fig_ax("Where the money went in commercial open source",
                     "Latest market cap, private valuation or exit price (log scale), coloured by how open the product is today",
                     rect=(0.15, 0.10, 0.58, 0.72))
    source_note(fig, "Source: this study's case files (companies/A, companies/B; 904 cited sources). Values are at different dates, 2008–2026; see companies_master.csv.")
    ax.set_xscale("log"); ax.set_xlim(1e8, 5e11); n = len(d); ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks(range(n)); ax.set_yticklabels(d.lab, fontsize=13.5, color=TEXT); ax.tick_params(axis="y", length=0)
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: money(v))); ax.grid(axis="y", visible=False)
    bars = ax.barh(range(n), [1e8] * n, height=0.72, color=[OPEN_COL[o] for o in d.oc])
    txt = [ax.text(1e8, i, "", va="center", fontsize=12.5, color=TEXT2) for i in range(n)]
    hs = [Patch(color=OPEN_COL[k], label=OPEN_LAB[k]) for k in [3, 2, 1]]
    fig.legend(handles=hs, loc="center left", bbox_to_anchor=(0.765, 0.5), fontsize=16, title="Openness today", title_fontsize=17, labelcolor=TEXT)
    vals = d.latest_value_usd.values; dates = d.latest_value_date.astype(str).str[:4].values
    def update(p):
        for i in range(n):
            q = ease((p - (i / n) * 0.6) / 0.4); w = 10 ** (8 + q * (np.log10(vals[i]) - 8))
            bars[i].set_width(w); txt[i].set_x(w * 1.12); txt[i].set_text(f"{money(vals[i])} ({dates[i]})" if q > 0.98 else "")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- relicensing both ways
def s_relicense(duration, mp4, png):
    r = E[(E.kind == "relicense") & E.year.between(2008, 2026)].copy()
    r["lab"] = r["name"].map(short); r["dir"] = r.direction.str[:4]
    fig, ax = fig_ax("Licences move both ways, and faster since 2020",
                     "Each dot is one dated change in licence or access terms in this study's case files: closing above the line, opening below",
                     rect=(0.06, 0.12, 0.56, 0.70))
    source_note(fig, "Source: companies/events.csv (relicensing_events across 121 organizations).")
    ax.set_xlim(2007.5, 2026.6); ax.set_ylim(-14, 11); ax.axhline(0, color=TEXT2, lw=1.2)
    ax.set_yticks([]); ax.grid(axis="y", visible=False); ax.xaxis.set_major_locator(mt.MultipleLocator(2))
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{int(v)}"))
    pts = []
    for (y, dr), g in r.sort_values(["year", "lab"]).groupby(["year", "dir"]):
        for k in range(len(g)):
            pts.append((y, (k + 1) if dr == "clos" else -(k + 1), dr))
    sc_c = ax.scatter([], [], s=170, color=ORANGE, edgecolors=SURFACE, linewidths=2, zorder=3, label="Closing")
    sc_o = ax.scatter([], [], s=170, color=BLUE, edgecolors=SURFACE, linewidths=2, zorder=3, label="Opening")
    ax.legend(loc="lower left", ncol=2)
    n_c = {p: ((r.dir == "clos") & r.year.between(*p)).sum() for p in [(2010, 2019), (2020, 2026)]}
    n_o = {p: ((r.dir == "open") & r.year.between(*p)).sum() for p in [(2010, 2019), (2020, 2026)]}
    stat = ax.text(2008.2, 9.2, "", fontsize=19, color=TEXT, va="top")
    hl = [(2012, "MakerBot closes its printer designs", ORANGE), (2015, "Google hands Kubernetes to the CNCF", BLUE),
          (2018, "MongoDB: AGPL → SSPL", ORANGE), (2019, "OpenAI stages GPT-2, publishes less", ORANGE),
          (2021, "Elastic → SSPL/ELv2; AWS forks OpenSearch", ORANGE), (2023, "HashiCorp → BSL; OpenTofu fork", ORANGE),
          (2023, "Prusa stops publishing full CAD", ORANGE), (2024, "Redis → RSAL/SSPL; Valkey fork", ORANGE),
          (2024, "Elastic adds AGPL back", BLUE), (2025, "Redis adds AGPL back", BLUE), (2025, "DeepSeek-R1 under MIT", BLUE),
          (2025, "OpenAI gpt-oss under Apache-2.0", BLUE), (2025, "Anthropic donates MCP to Linux Fdn.", BLUE),
          (2026, "Meta's frontier model ships closed", ORANGE)]
    fig.text(0.645, 0.80, "Highlights", fontsize=22, color=TEXT2, fontweight="bold")
    htx = [fig.text(0.645, 0.76 - i * 0.045, "", fontsize=16.5, color=TEXT) for i in range(len(hl))]
    hdot = [fig.text(0.638, 0.76 - i * 0.045, "", fontsize=16.5, color=c, ha="right") for i, (_, _, c) in enumerate(hl)]
    def update(p):
        xmax = 2008 + p * 18.6
        c = [(x, y) for x, y, d in pts if d == "clos" and x <= xmax]; o = [(x, y) for x, y, d in pts if d == "open" and x <= xmax]
        sc_c.set_offsets(np.array(c) if c else np.empty((0, 2))); sc_o.set_offsets(np.array(o) if o else np.empty((0, 2)))
        for i, (y, t, col) in enumerate(hl):
            htx[i].set_text(f"{y}  {t}" if y <= xmax else ""); hdot[i].set_text("●" if y <= xmax else "")
        if p >= 1:
            stat.set_text(f"2010–19: {n_c[(2010, 2019)]} closing, {n_o[(2010, 2019)]} opening\n2020–26: {n_c[(2020, 2026)]} closing, {n_o[(2020, 2026)]} opening")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- openness lanes over time
def lanes(df, ev):
    out = []
    for _, r in df.iterrows():
        f = r.founded_year if r.founded_year == r.founded_year else None
        if f is None: continue
        end = r.end_year if (r.end_year == r.end_year and str(r.still_operating) == "False") else 2026.9
        o0 = int(r.openness_initial) if r.openness_initial == r.openness_initial else 2
        o1 = int(r.openness_current) if r.openness_current == r.openness_current else o0
        es = ev[(ev.slug == r.slug) & (ev.kind == "relicense") & ev.year.notna()].sort_values("year")
        segs, cur, start = [], o0, f
        for i, (_, e) in enumerate(es.iterrows()):
            y = max(e.year, f)
            nxt = o1 if i == len(es) - 1 else int(np.clip(cur + (-1 if str(e.direction).startswith("clos") else 1), 0, 4))
            if y > start: segs.append((start, y, cur))
            cur, start = nxt, y
        segs.append((start, end, cur if len(es) else o1 if o1 == o0 else o0))
        if not len(es) and o1 != o0: segs = [(f, end, o1)]
        out.append(dict(lab=short(r["name"]), f=f, end=end, dead=str(r.still_operating) == "False", segs=segs, exits=E[(E.slug == r.slug) & (E.kind != "relicense") & E.year.notna()]))
    return out

def s_lanes(duration, mp4, png, groups, title, subtitle, start=1965):
    d = M[M.group.isin(groups)].copy(); d = d.sort_values("founded_year", ascending=False)
    L = lanes(d, E); n = len(L)
    fig, ax = fig_ax(title, subtitle, rect=(0.15, 0.08, 0.63, 0.76))
    ax.set_xlim(start, 2027.5); ax.set_ylim(-0.7, n - 0.3); ax.set_yticks(range(n))
    ax.set_yticklabels([l["lab"] for l in L], fontsize=max(10, min(15, 420 / n)), color=TEXT); ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
    hs = [Patch(color=OPEN_COL[k], label=OPEN_LAB[k]) for k in [4, 3, 2, 1, 0]]
    fig.legend(handles=hs, loc="center left", bbox_to_anchor=(0.79, 0.55), fontsize=14, title="Openness", title_fontsize=16, labelcolor=TEXT)
    fig.text(0.795, 0.3, "◆ exit (IPO, sale)\n✕ shut down", fontsize=15, color=TEXT2)
    rects = []
    for i, l in enumerate(L):
        for (a, b, o) in l["segs"]:
            rects.append((a, b, i, ax.barh(i, 0, left=a, height=0.62, color=OPEN_COL[o])[0]))
    marks = []
    for i, l in enumerate(L):
        for _, e in l["exits"].iterrows():
            if e.kind in ("IPO", "acquisition", "merger", "take_private"):
                marks.append((e.year, ax.plot([], [], marker="D", ms=9, color=TEXT, markeredgecolor=SURFACE, lw=0)[0], i))
        if l["dead"]:
            marks.append((l["end"], ax.plot([], [], marker="x", ms=13, mew=3, color=TEXT, lw=0)[0], i))
    yr = ax.text(start + 1, n - 1, "", fontsize=26, color=TEXT2, va="center")
    def update(p):
        xmax = start + p * (2026.9 - start)
        for a, b, i, rc in rects:
            rc.set_width(max(0, min(b, xmax) - a))
        for x, mk, i in marks:
            mk.set_data(([x], [i]) if x <= xmax else ([], []))
        yr.set_text(f"{int(min(xmax, 2026))}" if p < 1 else "")
    source_note(fig, "Source: this study's case files. Segments change colour at each dated licence or access change; levels are the study's 0–4 rubric (companies/SCHEMA.md).")
    render(fig, update, duration, mp4, png)

def s_lanes_software(d, m, p): s_lanes(d, m, p, ["A", "B"], "Openness over time: commercial open-source software", "Each lane runs from founding to today (or shutdown); colour is the openness of the main product", start=1990)
def s_lanes_hardware(d, m, p): s_lanes(d, m, p, ["D"], "Openness over time: hardware makers", "Open hardware pioneers, the firms that closed, and the closed newcomers", start=2000)
def s_lanes_science(d, m, p): s_lanes(d, m, p, ["E", "F"], "Openness over time: physical-science infrastructure and companies", "Government and academic open infrastructure next to closed commercial codes and startups", start=1965)
def s_lanes_ai(d, m, p): s_lanes(d, m, p, ["C"], "Openness over time: Big Tech and AI labs", "Who opened what, and when it closed again", start=1970)

# ---------------------------------------------------------------- AI lab values
def s_ai_values(duration, mp4, png):
    keep = ["Anthropic", "OpenAI", "xAI", "DeepSeek", "Hugging Face"]
    d = M[M.group.isin(["B", "C"])].copy(); d["lab"] = d["name"].map(short)
    d = d[d.lab.str.split().str[0].isin([k.split()[0] for k in keep]) & d.latest_value_usd.notna()].sort_values("latest_value_usd")
    d["oc"] = d.openness_current.fillna(1).astype(int)
    fig, ax = fig_ax("In frontier AI, the value sits with closed weights",
                     "Latest market cap, valuation or acquisition price (log scale), coloured by openness of the main models today",
                     rect=(0.17, 0.14, 0.60, 0.66))
    source_note(fig, "Sources: case files companies/C and companies/B (Anthropic: Nasdaq ANT, first trade 2026-11-19, Yahoo Finance market cap 2026-11-23).")
    n = len(d); ax.set_xscale("log"); ax.set_xlim(1e9, 3e12); ax.set_ylim(-0.6, n - 0.4)
    ax.set_yticks(range(n)); ax.set_yticklabels(d.lab, fontsize=20, color=TEXT); ax.tick_params(axis="y", length=0)
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: money(v))); ax.grid(axis="y", visible=False)
    bars = ax.barh(range(n), [1e9] * n, height=0.6, color=[OPEN_COL[o] for o in d.oc])
    note = {"Anthropic": "public, Nov 2026", "OpenAI": "private, Mar 2026", "xAI": "bought by SpaceX, Feb 2026", "DeepSeek": "pre-money, Oct 2026", "Hugging Face": "NVIDIA deal, Sep 2026"}
    txt = [ax.text(1e9, i, "", va="center", fontsize=18, color=TEXT) for i in range(n)]
    hs = [Patch(color=OPEN_COL[k], label=OPEN_LAB[k]) for k in sorted(set(d.oc), reverse=True)]
    ax.legend(handles=hs, loc="lower right", fontsize=16, title="Openness today", title_fontsize=17, labelcolor=TEXT)
    vals = d.latest_value_usd.values; labs = d.lab.values
    def update(p):
        for i in range(n):
            q = ease((p - i * 0.12) / 0.45); w = 10 ** (9 + q * (np.log10(vals[i]) - 9))
            bars[i].set_width(w); txt[i].set_x(w * 1.12)
            txt[i].set_text(f"{money(vals[i])}  {next((v for k, v in note.items() if labs[i].startswith(k)), '')}" if q > 0.98 else "")
    render(fig, update, duration, mp4, png)

# ---------------------------------------------------------------- stocks since IPO
def s_stocks(duration, mp4, png):
    px = pd.read_csv("data/prices_weekly_close.csv", index_col=0, parse_dates=True)
    oss = [("MDB", "MongoDB", BLUE), ("ESTC", "Elastic", AQUA), ("GTLB", "GitLab", YELLOW)]
    closed = ["SNOW", "DDOG", "CRWD", "OKTA", "TWLO", "ZS", "DOCU", "TEAM"]
    def aligned(t):
        s = px[t].dropna(); y = (s.index - s.index[0]).days / 365.25; return pd.Series(s.values / s.values[0], index=y)
    grid = np.round(np.arange(0, 11.01, 1 / 12), 4)
    a = pd.DataFrame({t: aligned(t).reindex(grid, method="nearest", tolerance=0.05) for t in closed})
    mc = a.median(axis=1, skipna=True); mc[a.count(axis=1) < 4] = np.nan
    fig, ax = fig_ax("Open-source-origin stocks vs closed software peers",
                     "Growth of $1 from each company's first trading week, by years since listing (log scale)",
                     rect=(0.08, 0.14, 0.74, 0.67))
    source_note(fig, "Closed peers: Snowflake, Datadog, CrowdStrike, Okta, Twilio, Zscaler, DocuSign, Atlassian (median of those listed that long). HashiCorp, Confluent and Couchbase\nleft the market in buyouts (IBM $6.4B, IBM $11B, Haveli $1.5B). Yahoo Finance weekly adjusted closes to 2026-11-23.")
    ax.set_yscale("log"); ax.set_xlim(0, 11); ax.set_ylim(0.25, 20)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:g}")); ax.set_xlabel("years since listing")
    for t in closed:
        s = aligned(t); ax.plot(s.index, s.values, color=ORANGE, alpha=0.13, lw=1.2)
    ax.axhline(1, color=TEXT2, lw=1, ls=(0, (4, 4)))
    series = [(aligned(t), lab, col) for t, lab, col in oss] + [(mc.dropna(), "Closed peers (median)", ORANGE)]
    lines = [ax.plot([], [], color=col, lw=(4 if "median" in lab else 3), label=lab)[0] for _, lab, col in series]
    tx = [ax.text(0, 0, "", fontsize=18, color=TEXT, va="center") for _ in series]
    ax.legend(loc="upper left", ncol=2)
    def update(p):
        xm = p * 11
        for (s, lab, col), ln, t in zip(series, lines, tx):
            ss = s[s.index <= xm]
            if len(ss):
                ln.set_data(ss.index, ss.values); t.set_position((ss.index[-1] + 0.12, ss.values[-1]))
                t.set_text(f"{lab.split(' (')[0]} ${ss.values[-1]:.2f}" if p >= 1 else "")
    render(fig, update, duration, mp4, png)


# ---------------------------------------------------------------- who opens, who closes (by kind of organization)
def s_kinds(duration, mp4, png):
    t = pd.read_csv("data/openness_by_company_kind.csv").set_index("kind")
    rows = [("VC-era company (founded 2000+)", "Companies founded since 2000\n(mostly venture-backed)"),
            ("long-standing (founded <2000)", "Companies founded before 2000"),
            ("public/nonprofit infrastructure", "Government, academic and\nfoundation infrastructure")]
    fig, ax = fig_ax("Who opens, who closes", "Mean openness (0 closed – 4 open + open governance) at founding and today, across the 121 case files",
                     rect=(0.27, 0.16, 0.50, 0.62))
    source_note(fig, "Source: data/openness_by_company_kind.csv, from companies_master.csv (rubric in companies/SCHEMA.md). Convenience sample of notable organizations.")
    ax.set_xlim(0, 4); ax.set_ylim(-0.6, len(rows) - 0.4); ax.invert_yaxis(); ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[1] for r in rows], fontsize=18, color=TEXT); ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
    ax.set_xlabel("mean openness score")
    a0 = ax.scatter([], [], s=260, color=MUTED, zorder=3, label="At founding")
    a1 = ax.scatter([], [], s=260, color=BLUE, zorder=4, edgecolors=SURFACE, linewidths=2, label="Today")
    ax.legend(loc="lower right", fontsize=17)
    arrows = [ax.annotate("", xy=(0, i), xytext=(0, i), arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=2.5, mutation_scale=22)) for i in range(len(rows))]
    side = [fig.text(0.79, 0.0, "", fontsize=17, color=TEXT, va="center") for _ in rows]
    def update(p):
        xs0, xs1 = [], []
        for i, (k, lab) in enumerate(rows):
            o0, o1 = t.loc[k, "mean_open_initial"], t.loc[k, "mean_open_now"]
            q = ease((p - i * 0.15) / 0.45); x1 = o0 + (o1 - o0) * q
            xs0.append((o0, i)); xs1.append((x1, i))
            arrows[i].xy = (x1, i); arrows[i].set_position((o0, i))
            yfig = 0.16 + 0.62 * (1 - (i + 0.6) / (len(rows) + 0.2))
            side[i].set_y(yfig)
            side[i].set_text(f"n = {int(t.loc[k, 'n'])}\n{t.loc[k, 'mean_change']:+.2f} change\n{t.loc[k, 'share_closing_move']:.0%} made a closing move" if q > 0.98 else "")
        a0.set_offsets(xs0); a1.set_offsets(xs1)
    render(fig, update, duration, mp4, png)

SCENES = {"kinds": s_kinds, "values": s_values, "relicense": s_relicense, "lanes_software": s_lanes_software, "lanes_hardware": s_lanes_hardware,
          "lanes_science": s_lanes_science, "lanes_ai": s_lanes_ai, "ai_values": s_ai_values, "stocks": s_stocks}
if __name__ == "__main__":
    name = sys.argv[1]; dur = float(sys.argv[2])
    if "--png-only" in sys.argv:
        globals()["render"] = lambda fig, update, duration, out_mp4, out_png=None, build=0.7: (update(1.0), fig.savefig(out_png, dpi=DPI), plt.close(fig))
        SCENES[name](dur, None, f"{FIG}/{name}.png")
    else:
        SCENES[name](dur, f"{OUT}/{name}.mp4", f"{FIG}/{name}.png")
    print("done", name)
