#!/usr/bin/env python3
"""Search substitute for research passes once the session's web-search budget is spent.

    python3 scripts/find_pages.py "Company Name" [--alt "Other Name"] [--site https://company.com] [--gdelt]

Queries TechCrunch, SiliconANGLE, BetaKit and TechNode (WordPress APIs), Hacker News (Algolia), Wikipedia and
Wikidata, and the company's own site, and prints every page that mentions the name with the sentences about rounds
and investors (same code as investor_leads.py). --gdelt adds the GDELT news index (one request per 5 seconds; slow).
Leads only: open the page and confirm before recording anything. Run from funders/.
"""
import argparse, json, os, sys, time, urllib.parse as up
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import investor_leads as L  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("--alt", action="append", default=[]); ap.add_argument("--site", default="")
ap.add_argument("--gdelt", action="store_true")
a = ap.parse_args()
nm = L.names(a.name) + [x for x in a.alt if x]
leads = []
for f in (lambda: L.wp_leads(nm), lambda: L.hn_leads(nm), lambda: L.wiki_leads(nm, ""),
          lambda: L.site_leads(nm, f"site {a.site}" if a.site else "")):
    try:
        leads += f()
    except Exception as e:  # noqa: BLE001
        print("error:", repr(e)[:200])
if a.gdelt:
    q = " OR ".join(f'"{n}"' for n in nm[:2])
    r = L.get(L.S, "https://api.gdeltproject.org/api/v2/doc/doc", params={"query": f"({q}) (funding OR raises OR investors OR seed OR series)",
              "mode": "artlist", "format": "json", "maxrecords": 30, "timespan": "20y"})
    try:
        for art in (r.json().get("articles", []) if r is not None and r.status_code == 200 else []):
            leads.append({"src": "GDELT", "date": art.get("seendate", "")[:8], "title": art.get("title", ""),
                          "url": art.get("url", ""), "about": True, "sentences": []})
    except ValueError:
        print("GDELT: no JSON (rate limit?)")
for l in leads:
    print(f"- {l['src']} {l['date']} | {l['title']} | {l['url']}")
    for s in l["sentences"]:
        print(f"    > {s}")
if not leads:
    print("no pages found")
