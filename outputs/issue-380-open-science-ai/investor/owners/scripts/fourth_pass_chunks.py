#!/usr/bin/env python3
"""Split the companies into chunks for the fourth finance pass and write one leads file per chunk.

Every company goes to the fourth pass (rules: fourth_pass_rules.md), thin rows first within each chunk. Each chunk
gets data/finance_passes/fourth_input_<k>.csv (the current merged row of each GitHub organization, in the pass format)
and data/finance_passes/pi_leads_<k>.md (the current row and scripts/search_leads.py's leads). One company's
organizations stay together. Run from owners/ after search_leads.py:

    python scripts/fourth_pass_chunks.py 8
"""
import json, sys
import pandas as pd

sys.path.insert(0, "scripts")
from append_finance_rows import COLS  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
F = pd.read_csv("data/core_financials.csv", dtype=str)
inp = pd.read_csv("data/finance_passes/input_all.csv", dtype=str).set_index("owner")
leads = {}
for line in open("data/finance_passes/pi_leads.jsonl"):
    if line.strip():
        r = json.loads(line)
        leads[r["owner"]] = r


def is_thin(r):
    return r.ever_1b == "unknown" or pd.isna(r.total_funding_usd) or r.status == "unknown"


groups = {}
for r in F.itertuples(index=False):
    groups.setdefault(r.entity.strip().lower(), []).append(r)
order = sorted(groups.values(), key=lambda g: (not any(is_thin(r) for r in g), -max(int(r.stars) for r in g)))
chunks = [[] for _ in range(N)]
for gi, g in enumerate(order):
    rnd, pos = divmod(gi, N)
    chunks[pos if rnd % 2 == 0 else N - 1 - pos].append(g)


def show(r):
    d = {c: getattr(r, c) for c in COLS if isinstance(getattr(r, c, None), str) and getattr(r, c)}
    d.pop("owner", None); d.pop("entity", None)
    return json.dumps(d, ensure_ascii=False)[:1400]


for k, gs in enumerate(chunks, 1):
    rows = [r for g in gs for r in g]
    pd.DataFrame([{c: getattr(r, c) for c in COLS} for r in rows]).to_csv(
        f"data/finance_passes/fourth_input_{k}.csv", index=False)
    L = [f"# Fourth-pass leads, chunk {k}: {len(gs)} companies, {len(rows)} GitHub organizations", "",
         "Rules: fourth_pass_rules.md. Thin rows (no funding figure, no $1B call or unknown status) come first.", ""]
    for g in gs:
        r0 = g[0]
        m = inp.loc[r0.owner]
        L += [f"## {', '.join(r.owner for r in g)} — {r0.entity}" + ("  (thin)" if any(is_thin(r) for r in g) else ""),
              "",
              f"Input: country {m.country}; site {m.blog}; stars {r0.stars}; basis: {m.basis}; top repos: "
              f"{str(m.top_repos)[:200]}",
              f"Current row: {show(r0)}", ""]
        rec = next((leads[r.owner] for r in g if r.owner in leads), None)
        if rec is None or rec.get("error"):
            L += [f"Leads: none ({rec.get('error') if rec else 'not searched'})", ""]
            continue
        L.append(f"Searched as: {', '.join(rec['names'])}")
        if rec["hits"]:
            L.append("Headlines (date | title | url or source | engine):")
            for h in rec["hits"]:
                L.append(f"- {h.get('date', '')} | {h['title'][:160]} | {h.get('url') or h.get('source_url', '')} | "
                         f"{h['via']}")
        else:
            L.append("Headlines: none that name the company and a deal")
        for p in rec["pages"]:
            if isinstance(p["excerpts"], list) and p["excerpts"]:
                L.append(f"Page {p['url']} ({p['date']}, via {p['route']}):")
                L += [f"  > {e}" for e in p["excerpts"]]
            elif p["excerpts"] == "FETCH FAILED":
                L.append(f"Page {p['url']}: could not be fetched by any route")
        L.append("")
    open(f"data/finance_passes/pi_leads_{k}.md", "w").write("\n".join(L) + "\n")
    print(k, len(gs), "companies", len(rows), "orgs")
