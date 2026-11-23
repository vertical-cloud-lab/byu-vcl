#!/usr/bin/env python3
"""Flatten gh_dump.py output into one corpus and score each item for open-source commercialization relevance."""
import json, re, sys, os, csv
KW = [r"commerciali[sz]", r"\bcommercial\b", r"\bbusiness", r"start-?up", r"\bcompany\b", r"\bcompanies\b", r"spin-?(off|out)",
      r"\bsell", r"\bsold\b", r"\bpric(e|ing)", r"\brevenue", r"\bprofit", r"\bcustomer", r"\bmarket", r"\bkits?\b",
      r"tindie", r"kickstarter", r"crowd ?supply", r"\betsy\b", r"licen[cs]", r"\bpatent", r"intellectual property", r"\bIP\b",
      r"open[- ]source", r"open hardware", r"oshwa", r"cern[- ]ohl", r"\bGPL", r"\bMIT\b", r"creative commons|\bCC[- ]BY",
      r"sponsor", r"\bgrant", r"funding", r"\binvest", r"venture", r"\bVC\b", r"monetiz", r"\bproduct\b", r"vendor",
      r"digi-?key", r"adafruit", r"sparkfun", r"opentrons", r"prusa", r"bambu", r"arduino", r"consult", r"saas",
      r"cloud lab", r"subscription", r"donat", r"numfocus", r"non-?profit", r"sustainab", r"open science", r"\bmitacs\b",
      r"industry partner", r"\bpartner", r"\bquote\b", r"purchase", r"\bbuy", r"\bcost", r"\$\d", r"\bCAD\b", r"\bUSD\b",
      r"manufactur", r"\bPCB", r"jlcpcb", r"pcbway", r"supplier"]
CORE = [r"commerciali[sz]", r"business", r"start-?up", r"spin-?(off|out)", r"\bsell", r"\brevenue", r"\bcustomer", r"\bmarket",
        r"tindie|kickstarter|crowd ?supply|etsy", r"licen[cs]", r"\bpatent|intellectual property", r"open[- ]source|open hardware|open science",
        r"monetiz", r"venture|\bVC\b|\binvest", r"\bkits?\b", r"\bpric(e|ing)"]
rx = [re.compile(k, re.I) for k in KW]; crx = [re.compile(k, re.I) for k in CORE]

def recs(repo, d):
    iss = json.load(open(f"{d}/issues.json")); bynum = {i["number"]: i for i in iss}
    for i in iss:
        yield dict(repo=repo, kind="pr" if "pull_request" in i else "issue", number=i["number"], title=i["title"],
                   url=i["html_url"], author=(i.get("user") or {}).get("login"), created=i["created_at"], body=i.get("body") or "")
    for c in json.load(open(f"{d}/issue_comments.json")):
        n = int(c["issue_url"].rsplit("/", 1)[1]); t = bynum.get(n, {}).get("title", "")
        yield dict(repo=repo, kind="comment", number=n, title=t, url=c["html_url"], author=(c.get("user") or {}).get("login"),
                   created=c["created_at"], body=c.get("body") or "")
    for c in json.load(open(f"{d}/review_comments.json")):
        n = int(c["pull_request_url"].rsplit("/", 1)[1]); t = bynum.get(n, {}).get("title", "")
        yield dict(repo=repo, kind="review_comment", number=n, title=t, url=c["html_url"], author=(c.get("user") or {}).get("login"),
                   created=c["created_at"], body=c.get("body") or "")
    for r in json.load(open(f"{d}/review_bodies.json")):
        n = r["pr"]; yield dict(repo=repo, kind="review", number=n, title=bynum.get(n, {}).get("title", ""), url=r["url"],
                                author=(r.get("author") or {}).get("login"), created=r["createdAt"], body=r["body"] or "")
    for x in json.load(open(f"{d}/discussions.json")):
        yield dict(repo=repo, kind="discussion", number=x["number"], title=x["title"], url=x["url"],
                   author=(x.get("author") or {}).get("login"), created=x["createdAt"], body=x["body"] or "")
        for c in x["comments"]["nodes"]:
            yield dict(repo=repo, kind="discussion_comment", number=x["number"], title=x["title"], url=c["url"],
                       author=(c.get("author") or {}).get("login"), created=c["createdAt"], body=c["body"] or "")
            for r in c["replies"]["nodes"]:
                yield dict(repo=repo, kind="discussion_reply", number=x["number"], title=x["title"], url=r["url"],
                           author=(r.get("author") or {}).get("login"), created=r["createdAt"], body=r["body"] or "")

def score(text):
    return sum(len(r.findall(text)) for r in rx), sum(1 for r in crx if r.search(text))

if __name__ == "__main__":
    allr = []
    for repo, d in [("AccelerationConsortium/ac-dev-lab", "/tmp/ghdump/ac-dev-lab"), ("sparks-baird/self-driving-lab-demo", "/tmp/ghdump/self-driving-lab-demo")]:
        for r in recs(repo, d):
            s, c = score(r["title"] + " \n" + r["body"]); r["kw_hits"] = s; r["core_hits"] = c; allr.append(r)
    json.dump(allr, open("/tmp/ghdump/corpus.json", "w"))
    print("total records", len(allr))
    rel = [r for r in allr if r["core_hits"] >= 2 or (r["core_hits"] >= 1 and r["kw_hits"] >= 4)]
    print("relevant records", len(rel))
    # thread-level aggregation
    th = {}
    for r in rel:
        k = (r["repo"], r["number"], r["kind"].startswith("discussion"))
        t = th.setdefault(k, dict(repo=r["repo"], number=r["number"], title=r["title"], n=0, hits=0, core=0, first=r["created"]))
        t["n"] += 1; t["hits"] += r["kw_hits"]; t["core"] += r["core_hits"]; t["first"] = min(t["first"], r["created"])
    rows = sorted(th.values(), key=lambda t: -t["core"])
    os.makedirs("gh-mining", exist_ok=True)
    with open("gh-mining/relevant_threads.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(rel, open("/tmp/ghdump/relevant_records.json", "w"), indent=1)
    print("relevant threads", len(rows))
    for t in rows[:40]:
        print(t["core"], t["n"], t["repo"].split("/")[1], t["number"], t["title"][:80])
