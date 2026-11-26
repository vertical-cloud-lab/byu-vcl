#!/usr/bin/env python3
"""Headline numbers quoted in FUNDERS.md, written to data/funders_numbers.json. Run from funders/ after
build_funders.py and check_sources.py."""
import collections, csv, json, os

D = "data"


def rd(p):
    return list(csv.DictReader(open(os.path.join(D, p)))) if os.path.exists(os.path.join(D, p)) else []


def main():
    V, Dl, L, I = rd("ventures.csv"), rd("deals.csv"), rd("investor_links.csv"), rd("investors.csv")
    out = {}
    for u in ("U1", "U2", "U3", "U4", "U1-U3"):
        us = ("U1", "U2", "U3") if u == "U1-U3" else (u,)
        vs = [v for v in V if v["universe"] in us]
        res = [v for v in vs if v["researched"] == "1"]
        ls = [l for l in L if l["universe"] in us]
        invs = {l["investor"] for l in ls}
        cnt = collections.Counter(l["investor"] for l in ls)
        out[u] = {"ventures": len(vs), "researched": len(res),
                  "with_funding": sum(v["funding_found"] == "yes" for v in res),
                  "none_found": sum(v["funding_found"] == "none_found" for v in res),
                  "bootstrapped_stated": sum(v["funding_found"] == "bootstrapped_stated" for v in res),
                  "rounds": sum(1 for d in Dl if d["universe"] in us and "adds to existing round" not in d["note"].lower()),
                  "links": len(ls), "funders": len(invs),
                  "funders_1": sum(1 for c in cnt.values() if c == 1), "funders_3plus": sum(1 for c in cnt.values() if c >= 3),
                  "funders_5plus": sum(1 for c in cnt.values() if c >= 5), "funders_10plus": sum(1 for c in cnt.values() if c >= 10),
                  "top10_share_of_links": round(sum(c for _, c in cnt.most_common(10)) / max(1, len(ls)), 3),
                  "top50_share_of_links": round(sum(c for _, c in cnt.most_common(50)) / max(1, len(ls)), 3),
                  "top15": cnt.most_common(15)}
    tmap = {r["investor"]: r["type"] for r in I}
    out["types_all"] = dict(collections.Counter(r["type"] for r in I))
    out["led_top"] = collections.Counter({r["investor"]: int(r["led_ventures"]) for r in I}).most_common(15)
    # eras: first year an investor appears in a venture's rounds (U1-U3)
    era = collections.defaultdict(collections.Counter)
    for l in L:
        if l["universe"] in ("U1", "U2", "U3") and l["first_year"]:
            y = int(l["first_year"])
            e = "before 2010" if y < 2010 else ("2010-2019" if y < 2020 else "2020 on")
            era[e][l["investor"]] += 1
    out["era_top"] = {e: c.most_common(12) for e, c in era.items()}
    out["era_links"] = {e: sum(c.values()) for e, c in era.items()}
    sk = collections.Counter(d["source_kind"] for d in Dl)
    out["rounds_by_source_kind"] = dict(sk)
    sc = rd("source_checks_deals.csv")
    if sc:
        av = [r for r in sc if r["check"] != "unavailable"]
        out["source_check"] = {"mentions": len(sc), "fetched": len(av), "found": sum(r["check"] == "found" for r in av),
                               "share_found": round(sum(r["check"] == "found" for r in av) / max(1, len(av)), 3)}
    pm = rd("portfolio/matches.csv")
    if pm:
        dom = [r for r in pm if r["match"] == "domain"]
        have = {(l["investor"], l["key"]) for l in L}
        out["portfolio_check"] = {"domain_links": len(dom), "already_in_deals": sum((r["investor"], r["key"]) in have for r in dom)}
    out["thesis_funders"] = [(r["investor"], r["ventures"]) for r in I if r.get("stated_open_source_thesis")]
    json.dump(out, open(os.path.join(D, "funders_numbers.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("U1-U3", "U1", "U2", "U3", "U4")}, indent=0)[:3500])


if __name__ == "__main__":
    main()
