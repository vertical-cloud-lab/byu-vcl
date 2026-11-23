#!/usr/bin/env python3
"""Term rates in AI-lab and policy primary documents fetched through the Pi browser.

Reads language/urls_known.tsv (org, date, url) and the page text saved by pi_search.py --fetch in
/tmp/pitext/<sha1(url)[:10]>.json. Full texts are not committed (copyright); only counts per
1,000 words and short quoted sentences with their URL go into the repo."""
import json, re, hashlib, csv, os, collections
TERMS = {
 "open_source": r"open[- ]source",
 "open_weights": r"open[- ]weights?|open models?\b",
 "open_science": r"open science|open research|open data|open[- ]access|open standard|open protocol",
 "safety_risk": r"\bsafety\b|\brisks?\b|\bmisuse\b|\bdangerous\b|\bcatastroph\w*|\bbiosecurity\b",
 "science": r"\bscien(?:ce|tific|tists?)\b|\bdiscover(?:y|ies)\b",
 "physical_sci": r"\bphysics\b|\bchemi(?:stry|cal)\b|\bmaterials? science\b|\bmaterials\b|\bphysical sciences?\b|\blaborator(?:y|ies)\b|\blab\b|\binstruments?\b|\bexperiments?\b",
 "bio_health": r"\bbiolog\w*|\bdiseases?\b|\bdrugs?\b|\bproteins?\b|\bmedic\w*|\blife sciences\b",
 "geopolitics": r"\bnational security\b|\bChina\b|\bCCP\b|\badversar\w*|\bexport controls?\b|\bDeepSeek\b|\bauthoritarian\w*",
 "proprietary_closed": r"\bproprietary\b|\bclosed[- ]source\b|\bclosed models?\b|\bclosed[- ]weights?\b",
}
rows, quotes = [], collections.defaultdict(list)
for org, date, url in (l.rstrip("\n").split("\t") for l in open("language/urls_known.tsv") if l.strip()):
    p = f"/tmp/pitext/{hashlib.sha1(url.encode()).hexdigest()[:10]}.json"
    if not os.path.exists(p):
        continue
    d = json.load(open(p)); text = d["text"]
    words = len(re.findall(r"\b\w+\b", text))
    r = dict(org=org, date=date, url=url, title=d["title"][:120], words=words)
    for k, rx in TERMS.items():
        r[k] = len(re.findall(rx, text, flags=re.I))
    rows.append(r)
    for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")):
        n = len(s.split())
        if 8 <= n <= 45 and re.search(r"open[- ](?:source|weights?)|open science|open models?\b|scien(?:ce|tific)|discover|physical", s, re.I):
            quotes[(org, date, url)].append(s.strip())
os.makedirs("language", exist_ok=True)
with open("language/term_counts_by_document.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
agg = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    agg[r["org"]]["words"] += r["words"]; agg[r["org"]]["docs"] += 1
    for k in TERMS: agg[r["org"]][k] += r[k]
with open("language/term_rates_by_org.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["org", "docs", "words"] + [f"{k}_per_1k" for k in TERMS])
    for org, c in agg.items():
        w.writerow([org, c["docs"], c["words"]] + [round(1000 * c[k] / c["words"], 3) for k in TERMS])
json.dump({f"{o}|{d}|{u}": q[:40] for (o, d, u), q in quotes.items()}, open("/tmp/lang_candidate_quotes.json", "w"), indent=1)
print(open("language/term_rates_by_org.csv").read())
for r in rows: print(r["org"], r["date"], r["words"], r["open_source"], r["open_weights"], r["science"], r["physical_sci"], r["title"][:60])
