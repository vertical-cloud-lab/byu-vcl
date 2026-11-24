#!/usr/bin/env python3
"""Licence and access changes per organization-year, 2010-19 vs. 2020-26 (groups A-F).

Answers REVIEW_FINDINGS.md row 15: the raw counts compare a 10-year window with a 7-year one, and many
organizations in the sample didn't exist before 2015. Exposure is each organization's years operating inside
the window (founding year to end year, or 2026). Undated events are dropped. Also restricted to organizations
founded before 2010. Writes data/licence_events_per_org_year.csv."""
import csv

M = [r for r in csv.DictReader(open("companies/companies_master.csv")) if r["group"] in "ABCDEF"]
events = [r for r in csv.DictReader(open("companies/events.csv"))
          if r["group"] in "ABCDEF" and r["direction"] in ("closing", "opening") and r["year"].strip()]
founded = {r["slug"]: int(float(r["founded_year"])) for r in M if r["founded_year"]}
ended = {r["slug"]: (int(float(r["end_year"])) if r["end_year"] else 2026) for r in M}
windows = {"2010-19": (2010, 2019), "2020-26": (2020, 2026)}


def exposure(slugs, a, b):
    return sum(max(0, min(b, ended[s]) - max(a, founded[s]) + 1) for s in slugs if s in founded)


out = []
for scope, keep in [("all A-F", lambda s: True), ("founded before 2010", lambda s: founded.get(s, 9999) < 2010)]:
    slugs = {r["slug"] for r in M if keep(r["slug"])}
    for w, (a, b) in windows.items():
        ex = exposure(slugs, a, b)
        n = {d: sum(1 for e in events if e["slug"] in slugs and a <= int(float(e["year"])) <= b and e["direction"] == d)
             for d in ("closing", "opening")}
        out.append(dict(scope=scope, window=w, n_orgs=len(slugs), org_years=ex, closing=n["closing"], opening=n["opening"],
                        closing_per_100_org_years=round(100 * n["closing"] / ex, 2),
                        opening_per_100_org_years=round(100 * n["opening"] / ex, 2)))
        print(out[-1])
with open("data/licence_events_per_org_year.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)


# --- By starting openness (2000-26): does each kind of starter move toward the middle? ---
def band(x):
    return "closed start (0)" if x == 0 else ("mixed start (1-2)" if x <= 2 else "open start (3-4)")


init = {r["slug"]: float(r["openness_initial"]) for r in M if r["openness_initial"]}
rows2 = []
for b in ["closed start (0)", "mixed start (1-2)", "open start (3-4)"]:
    slugs = {s for s, v in init.items() if band(v) == b}
    ex = exposure(slugs, 2000, 2026)
    n = {d: sum(1 for e in events if e["slug"] in slugs and 2000 <= int(float(e["year"])) <= 2026 and e["direction"] == d)
         for d in ("closing", "opening")}
    rows2.append(dict(start=b, n_orgs=len(slugs), org_years=ex, closing=n["closing"], opening=n["opening"],
                      closing_per_100_org_years=round(100 * n["closing"] / ex, 2),
                      opening_per_100_org_years=round(100 * n["opening"] / ex, 2)))
    print(rows2[-1])
with open("data/licence_events_by_start_openness.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows2[0])); w.writeheader(); w.writerows(rows2)


# --- By sector and decade (groups A-F; group G files record no dated licence events): how often each sector opens and closes ---
MG = [r for r in csv.DictReader(open("companies/companies_master.csv")) if r["group"] in "ABCDEF"]
EG = [r for r in csv.DictReader(open("companies/events.csv"))
      if r["group"] in "ABCDEF" and r["direction"] in ("closing", "opening") and r["year"].strip()]
fy = {r["slug"]: int(float(r["founded_year"])) for r in MG if r["founded_year"]}
ey = {r["slug"]: (int(float(r["end_year"])) if r["end_year"] else 2026) for r in MG}
SECT = {"A": "Commercial OSS software", "B": "Commercial OSS software", "C": "Big Tech & AI labs", "D": "Hardware",
        "E": "Lab automation & AI-for-science firms", "F": "Science software & infrastructure", "G": "AM, lab instruments & publishing"}
rows3 = []
for sect in dict.fromkeys(SECT[r["group"]] for r in MG):
    slugs = {r["slug"] for r in MG if SECT[r["group"]] == sect}
    for w, (a, b) in {"2000-09": (2000, 2009), "2010-19": (2010, 2019), "2020-26": (2020, 2026)}.items():
        ex = sum(max(0, min(b, ey[s]) - max(a, fy[s]) + 1) for s in slugs if s in fy)
        n = {d: sum(1 for e in EG if e["slug"] in slugs and a <= int(float(e["year"])) <= b and e["direction"] == d)
             for d in ("closing", "opening")}
        rows3.append(dict(sector=sect, window=w, n_orgs=len(slugs), org_years=ex, closing=n["closing"], opening=n["opening"],
                          closing_per_100_org_years=round(100 * n["closing"] / ex, 2) if ex else None,
                          opening_per_100_org_years=round(100 * n["opening"] / ex, 2) if ex else None))
with open("data/licence_events_by_sector_decade.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows3[0])); w.writeheader(); w.writerows(rows3)
for r_ in rows3: print(r_)


# --- Robustness: the same starting-openness rates for US-headquartered organizations only (groups A-F) ---
us = {r["slug"] for r in M if r["hq_country"].strip().upper() in ("US", "USA", "UNITED STATES")}
rows4 = []
for b in ["closed start (0)", "mixed start (1-2)", "open start (3-4)"]:
    slugs = {s for s, v in init.items() if band(v) == b and s in us}
    ex = exposure(slugs, 2000, 2026)
    n = {d: sum(1 for e in events if e["slug"] in slugs and 2000 <= int(float(e["year"])) <= 2026 and e["direction"] == d)
         for d in ("closing", "opening")}
    rows4.append(dict(start=b, scope="US-headquartered", n_orgs=len(slugs), org_years=ex, closing=n["closing"], opening=n["opening"],
                      closing_per_100_org_years=round(100 * n["closing"] / ex, 2) if ex else None,
                      opening_per_100_org_years=round(100 * n["opening"] / ex, 2) if ex else None))
    print(rows4[-1])
with open("data/licence_events_by_start_openness_us.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows4[0])); w.writeheader(); w.writerows(rows4)
