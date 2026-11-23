#!/usr/bin/env python3
"""Monthly activity (issues, PRs, comments, reviews, discussion posts) in the 118 threads coded as related to
open-source commercialization, by repo, from the gh api corpus. Figure + CSV."""
import sys, json, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
c = pd.DataFrame(json.load(open("/tmp/ghdump/corpus.json")))
c["rs"] = c.repo.str.split("/").str[-1]; c["month"] = pd.to_datetime(c.created).dt.to_period("Q").dt.to_timestamp()
coded = pd.read_csv("gh-mining/coded_threads.csv"); coded["rs"] = coded.repo.str.split("/").str[-1]
keys = set(zip(coded.rs, coded.number))
c["coded"] = [(r, n) in keys for r, n in zip(c.rs, c.number)]
t = c[c.coded].groupby(["month", "rs"]).size().unstack(fill_value=0)
allr = c.groupby(["month", "rs"]).size().unstack(fill_value=0)
t.to_csv("data/gh_coded_activity_by_quarter.csv")
fig, ax = fig_ax("Commercialization talk in our repos, by quarter", "Records (issues, PRs, comments, reviews, discussion posts) in the 118 threads coded as open-source commercialization",
                 rect=(0.07, 0.14, 0.86, 0.66))
source_note(fig, "Source: gh api dump of both repos (4,928 records), coded in gh-mining/coded_threads.csv; data/gh_coded_activity_by_quarter.csv.")
cols = [("self-driving-lab-demo", ORANGE, "self-driving-lab-demo (individual)"), ("ac-dev-lab", BLUE, "ac-dev-lab (institutional)")]
bottom = None; w = 70
for k, col, lab in cols:
    if k not in t: continue
    ax.bar(t.index, t[k], width=w, bottom=bottom, color=col, label=lab, edgecolor=SURFACE, linewidth=1)
    bottom = t[k] if bottom is None else bottom + t[k]
ax.set_ylabel("records per quarter"); ax.legend(loc="upper left")
fig.savefig("figures/gh_timeline.png", dpi=DPI)
share = (t.sum() / allr.sum()).round(3); print("share of each repo's records in coded threads:", share.to_dict()); print(t.sum().to_dict())
