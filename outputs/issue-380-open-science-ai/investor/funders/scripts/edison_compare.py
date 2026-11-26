#!/usr/bin/env python3
"""Cross-checks against Edison.

1. Literature answer (fund_who_funds_open_source): every funder it names, and whether the deal data
   (data/investors.csv) or the program passes (data/programs.csv) have it.
2. Blind audit (fund_deal_audit): Edison researched 40 randomly drawn ventures without seeing ours. For each venture,
   compares the sets of named funders (after the same name normalisation): funders both found, only ours, only
   Edison's. Writes data/edison_audit_comparison.csv and prints recall and precision against Edison's list.
Run from funders/ after build_funders.py.
"""
import csv, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_funders import key_name, load_alias  # noqa: E402

LIT = ["Accel", "Sequoia Capital", "Benchmark", "Index Ventures", "Andreessen Horowitz", "Insight Partners",
       "Redpoint Ventures", "New Enterprise Associates", "Battery Ventures", "Bessemer Venture Partners", "GV",
       "Tiger Global", "OSS Capital", "Runa Capital", "Heavybit", "Open Core Ventures", "Microsoft", "Amazon", "Google",
       "Salesforce Ventures", "Intel Capital", "SOSV", "Y Combinator", "Kickstarter backers", "Crowd Supply backers",
       "Indiegogo backers", "Open Collective", "GitHub Sponsors", "NumFOCUS", "Mozilla Open Source Support",
       "Bloomberg", "Indeed", "Spotify", "Alpha-Omega", "Chan Zuckerberg Initiative", "Alfred P. Sloan Foundation",
       "Gordon and Betty Moore Foundation", "Schmidt Futures", "Footprint Coalition", "National Science Foundation",
       "Sovereign Tech Agency", "NLnet", "Prototype Fund", "National Institutes of Health", "Wellcome",
       "Open Technology Fund", "Kavli Foundation", "Mistral AI investors: Microsoft"]


def main():
    alias = load_alias()
    inv = {key_name(r["investor"]): r for r in csv.DictReader(open("data/investors.csv"))}
    prog = " ".join((r["funder"] + " " + r["program"]).lower() for r in csv.DictReader(open("data/programs.csv"))) \
        if os.path.exists("data/programs.csv") else ""
    rows = []
    for n in LIT[:-1]:
        k = key_name(alias.get(key_name(n), n))
        in_deals = inv.get(k)
        in_prog = n.lower().split(" (")[0] in prog or key_name(n) in key_name(prog)
        rows.append({"funder_named_by_edison": n, "in_deal_data": f"yes ({in_deals['ventures']} ventures)" if in_deals else "no",
                     "in_program_passes": "yes" if in_prog else "no"})
    with open("data/edison_literature_check.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    miss = [r["funder_named_by_edison"] for r in rows if r["in_deal_data"] == "no" and r["in_program_passes"] == "no"]
    print(f"literature: {len(rows)} funders named; {len(rows) - len(miss)} found here; missing: {miss}")

    audit = "edison/fund_deal_audit_files/funders_audit.csv"
    if not os.path.exists(audit):
        cand = glob.glob("edison/fund_deal_audit_files/**/funders_audit.csv", recursive=True)
        audit = cand[0] if cand else ""
    if not audit:
        print("audit file not found yet"); return
    def canon(x):
        x = re.sub(r"\s*\(person\)$", "", x.strip())
        return key_name(alias.get(key_name(x), x))
    ed = {}
    for r in csv.DictReader(open(audit)):
        if r.get("type", "") == "none_found":
            ed.setdefault(r["key"], set()); continue
        names = [x for c in ("lead", "investors") for x in (r.get(c) or "").split("|") if x.strip()]
        ed.setdefault(r["key"], set()).update(canon(x) for x in names)
    ours = {}
    for l in csv.DictReader(open("data/investor_links.csv")):
        ours.setdefault(l["key"], set()).add(key_name(l["investor"]))
    sample = list(csv.DictReader(open("edison/uploads/funders_audit_sample.csv")))
    out, both_t, ours_t, ed_t = [], 0, 0, 0
    for s in sample:
        a, b = ours.get(s["key"], set()), ed.get(s["key"], set())
        both = a & b
        both_t += len(both); ours_t += len(a); ed_t += len(b)
        out.append({"key": s["key"], "venture": s["venture"], "universe": s["universe"], "ours": len(a), "edison": len(b),
                    "both": len(both), "only_ours": "; ".join(sorted(a - b)), "only_edison": "; ".join(sorted(b - a))})
    with open("data/edison_audit_comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(f"audit: {len(sample)} ventures; funders named by Edison {ed_t}, by us {ours_t}, by both {both_t}; "
          f"share of Edison's names we also have {both_t / max(1, ed_t):.0%}; share of ours Edison also has {both_t / max(1, ours_t):.0%}")


if __name__ == "__main__":
    main()
