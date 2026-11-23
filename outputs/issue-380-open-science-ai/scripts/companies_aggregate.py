#!/usr/bin/env python3
"""Flatten companies/<group>/<slug>.json case studies into one table (companies/companies_master.csv)
and an events table (companies/events.csv: relicensing and exits), tolerating partial files."""
import json, glob, os, csv, re
def num(x):
    try:
        if x is None or x == "": return None
        return float(x)
    except Exception:
        m = re.search(r"[\d.]+", str(x)); return float(m.group()) if m else None
def year(x):
    m = re.search(r"(19|20)\d\d", str(x or "")); return int(m.group()) if m else None
rows, events = [], []
for p in sorted(glob.glob("companies/*/*.json")):
    try:
        d = json.load(open(p))
    except Exception as e:
        print("bad json", p, e); continue
    g = p.split("/")[1]
    ex = d.get("exit_events") or []
    rel = d.get("relicensing_events") or []
    exv = [num(e.get("value_usd")) for e in ex if num(e.get("value_usd"))]
    r = dict(group=g, slug=d.get("slug") or os.path.basename(p)[:-5], name=d.get("name"), category=d.get("category"),
             subcategory=d.get("subcategory"), hq_country=d.get("hq_country"), origin=d.get("origin"),
             founded_year=year(d.get("founded_year")), openness_initial=num(d.get("openness_initial")),
             openness_current=num(d.get("openness_current")), business_model=d.get("business_model"),
             ownership_status=d.get("ownership_status"), still_operating=d.get("still_operating"), end_year=year(d.get("end_year")),
             funding_total_usd=num(d.get("funding_total_usd")), latest_value_usd=num(d.get("latest_value_usd")),
             latest_value_type=d.get("latest_value_type"), latest_value_date=d.get("latest_value_date"),
             max_exit_value_usd=max(exv) if exv else None, n_exits=len(ex),
             n_relicense=len(rel), n_closing=sum(1 for e in rel if str(e.get("direction", "")).lower().startswith("clos")),
             n_opening=sum(1 for e in rel if str(e.get("direction", "")).lower().startswith("open")),
             forks="; ".join(sorted({str(e.get("fork")) for e in rel if e.get("fork")})),
             revenue_latest_usd=num(d.get("revenue_latest_usd")), revenue_year=year(d.get("revenue_year")),
             employees_latest=num(d.get("employees_latest")), confidence=d.get("confidence"),
             n_sources=len(d.get("sources") or []), n_searches=len(d.get("searches") or []), n_fetched=len(d.get("fetched_urls") or []),
             search_tool=d.get("search_tool"), key_takeaway=(d.get("key_takeaway") or "")[:600])
    rows.append(r)
    for e in rel:
        events.append(dict(slug=r["slug"], name=r["name"], group=g, kind="relicense", year=year(e.get("year")), detail=f"{e.get('from')} -> {e.get('to')}",
                           direction=e.get("direction"), fork=e.get("fork"), value_usd=None, source=e.get("source")))
    for e in ex:
        events.append(dict(slug=r["slug"], name=r["name"], group=g, kind=e.get("type"), year=year(e.get("year")), detail=e.get("counterparty") or e.get("note"),
                           direction=None, fork=None, value_usd=num(e.get("value_usd")), source=e.get("source")))
with open("companies/companies_master.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open("companies/events.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(events[0].keys())); w.writeheader(); w.writerows(events)
import collections
print("orgs", len(rows), "events", len(events), "by group", dict(collections.Counter(r["group"] for r in rows)))
print("sources", sum(r["n_sources"] for r in rows), "searches", sum(r["n_searches"] for r in rows), "fetched", sum(r["n_fetched"] for r in rows))
