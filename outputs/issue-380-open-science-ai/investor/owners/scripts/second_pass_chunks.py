#!/usr/bin/env python3
"""Split the second-pass companies into chunks and write one leads file per chunk for the research agents.

A company goes to the second pass if its first-pass row has no source URL at all, or its notes say it was not
researched, rests on memory, or was not verified (data/finance_passes/second_pass_targets.csv). Each chunk file,
data/finance_passes/leads_<k>.md, shows the first-pass row and the leads that scripts/news_leads.py found. The
agents write corrected rows to data/finance_passes/second_<k>.csv through scripts/append_finance_rows.py; at merge
time a second-pass row replaces the first-pass row for the same owner. Run from owners/.
"""
import glob, json, os, sys
import pandas as pd

sys.path.insert(0, "scripts")
from news_leads import to_md  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
inp = pd.read_csv("data/finance_passes/input_all.csv", dtype=str)
tg = pd.read_csv("data/finance_passes/second_pass_targets.csv", dtype=str)
parts = sorted(glob.glob("data/finance_passes/output_*.csv"))
F = pd.concat([pd.read_csv(p, dtype=str) for p in parts], ignore_index=True).drop_duplicates("owner", keep="last")
F = F.set_index("owner")
leads = {}
for line in open("data/finance_passes/leads.jsonl"):
    r = json.loads(line)
    leads[r["owner"]] = r
order = [o for o in inp.owner if o in set(tg.owner)]
# keep one company's GitHub orgs together
ent = inp.set_index("owner").entity.str.lower().to_dict()
groups, seen = [], {}
for o in order:
    k = ent[o]
    if k in seen:
        groups[seen[k]].append(o)
    else:
        seen[k] = len(groups); groups.append([o])
chunks = [[] for _ in range(N)]
for gi, g in enumerate(groups):
    rnd, pos = divmod(gi, N)
    chunks[pos if rnd % 2 == 0 else N - 1 - pos].extend(g)
for k, owners in enumerate(chunks, 1):
    meta = inp.set_index("owner").loc[owners].reset_index()
    meta.to_csv(f"data/finance_passes/second_input_{k}.csv", index=False)
    with open(f"data/finance_passes/leads_{k}.md", "w") as fh:
        fh.write(f"# Second-pass leads, chunk {k}: {len(owners)} companies\n\n")
        for o in owners:
            m = meta[meta.owner == o].iloc[0]
            info = (f"Input: country {m.country}; basis: {m.basis}; status_hint: {m.status_hint}; site: {m.blog}; "
                    f"stars {m.stars}; h9_addition {m.h9_addition}; top repos: {str(m.top_repos)[:160]}\n")
            fp = F.loc[o].to_dict() if o in F.index else None
            if fp is not None:
                fp["owner"] = o
            rec = leads.get(o) or {"owner": o, "entity": m.entity, "names": [], "domain": "", "titles": [],
                                   "pages": [], "wikipedia": None}
            if "error" in rec:
                rec = {"owner": o, "entity": m.entity, "names": [], "domain": "", "titles": [], "pages": [],
                       "wikipedia": None}
            head, rest = to_md(rec, fp).split("\n", 1)
            fh.write(head + "\n" + info + rest + "\n")
    print(k, len(owners), os.path.getsize(f"data/finance_passes/leads_{k}.md"))
