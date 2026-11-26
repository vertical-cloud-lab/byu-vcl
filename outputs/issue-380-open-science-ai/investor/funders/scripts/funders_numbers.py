#!/usr/bin/env python3
"""Headline numbers quoted in FUNDERS.md, written to data/funders_numbers.json. Run from funders/ after
build_funders.py and check_sources.py."""
import collections, csv, json, os, re

D = "data"


def rd(p):
    return list(csv.DictReader(open(os.path.join(D, p)))) if os.path.exists(os.path.join(D, p)) else []


def main():
    V, Dl, L, I = rd("ventures.csv"), rd("deals.csv"), rd("investor_links.csv"), rd("investors.csv")
    out = {}
    for u in ("U1", "U2", "U3", "U4", "U1-U3"):
        us = ("U1", "U2", "U3") if u == "U1-U3" else (u,)
        vs = [v for v in V if v["universe"] in us and v.get("in_scope", "yes") == "yes"]
        res = [v for v in vs if v["researched"] == "1"]
        cd = [d for d in Dl if d["universe"] in us and d["counted"] == "yes"]
        rid = collections.defaultdict(list)
        for d in cd:
            rid[d["round_id"]].append(d)
        real = {r: g for r, g in rid.items() if not all("adds to existing round" in x["note"].lower() for x in g)}
        ls = [l for l in L if l["universe"] in us]
        invs = {l["investor"] for l in ls}
        cnt = collections.Counter(l["investor"] for l in ls)
        out[u] = {"ventures": len(vs), "researched": len(res),
                  "with_funding": sum(v["funding_found"] == "yes" for v in res),
                  "none_found": sum(v["funding_found"] == "none_found" for v in res),
                  "bootstrapped_stated": sum(v["funding_found"] == "bootstrapped_stated" for v in res),
                  "out_of_scope": sum(1 for v in V if v["universe"] in us and v.get("in_scope", "yes") != "yes"),
                  "rounds": len(real),
                  "rounds_named": sum(1 for g in real.values() if any(x["lead"] or x["investors"] for x in g)),
                  "round_records": sum(1 for d in cd if "adds to existing round" not in d["note"].lower()),
                  "rows_all": sum(1 for d in Dl if d["universe"] in us),
                  "rows_not_counted": sum(1 for d in Dl if d["universe"] in us and d["counted"] != "yes"),
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
    sc = [r for r in rd("source_checks_deals.csv") if r.get("counted", "yes") == "yes"]  # names in counted rounds only
    if sc:
        av = [r for r in sc if r["check"] != "unavailable"]
        f = sum(r["check"] == "found" for r in av); m = sum(r["check"].startswith("in page markup") for r in av)
        out["source_check"] = {"mentions": len(sc), "fetched": len(av), "found": f, "markup_only": m,
                               "not_on_page": len(av) - f - m,
                               "share_found": round(f / max(1, len(av)), 3),
                               "share_found_or_markup": round((f + m) / max(1, len(av)), 3)}
    pm = rd("portfolio/matches.csv")
    if pm:
        dom = [r for r in pm if r["match"] == "domain"]
        have = {(l["investor"], l["key"]) for l in L}
        out["portfolio_check"] = {"domain_links": len(dom), "already_in_deals": sum((r["investor"], r["key"]) in have for r in dom)}
    out["thesis_funders"] = [(r["investor"], r["ventures"]) for r in I if r.get("stated_open_source_thesis")]
    out["n_thesis_funders"] = len(out["thesis_funders"])
    grp = collections.defaultdict(set)
    for r in rd("investor_types.csv"):
        pass
    gmap = {r["investor"]: r["group"] for r in rd("investor_types.csv") if r.get("group")}
    for l in L:
        g = gmap.get(l["investor"])
        if g:
            grp[g].add(l["key"])
    out["groups"] = {re.sub(r"[^a-z0-9]+", "_", g.lower()).strip("_"): len(v) for g, v in grp.items()}
    # counts for funders named in the text (all groups, U1-U4), keyed by a slug
    named = ["OSS Capital", "Runa Capital", "Open Core Ventures", "Heavybit", "Uncorrelated Ventures", "Boldstart Ventures",
             "Crane Venture Partners", "Amplify Partners", "Bessemer Venture Partners", "GV", "Y Combinator", "SOSV",
             "Kickstarter backers", "Khosla Ventures", "True Ventures", "Foundry Group", "Spark Capital", "Eclipse Ventures",
             "Lux Capital", "Guillermo Rauch", "Clem Delangue", "David Cramer", "Tom Preston-Werner", "Nat Friedman",
             "Paul Copplestone", "Tristan Handy", "NVIDIA (incl. NVentures)", "Intel Capital", "Accel", "Sequoia Capital",
             "Andreessen Horowitz"]
    by = {r["investor"]: r for r in I}
    out["focus"] = {re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_"): int(by[n]["ventures"]) if n in by else 0 for n in named}
    # sensitivity (PROTOCOL.md): drop links supported only by databases or Wikipedia
    core = [l for l in L if l["universe"] in ("U1", "U2", "U3")]
    c_all = collections.Counter(l["investor"] for l in core)
    c_strict = collections.Counter(l["investor"] for l in core if l["database_only"] != "1")
    t_all = [n for n, _ in c_all.most_common(20)]
    t_strict = [n for n, _ in c_strict.most_common(20)]
    out["sensitivity_db"] = {"links_db_only": sum(1 for l in core if l["database_only"] == "1"), "links": len(core),
                             "top20_overlap": len(set(t_all) & set(t_strict)),
                             "dropped_from_top20": [n for n in t_all if n not in t_strict]}
    ea = rd("edison_audit_comparison.csv")
    if ea:
        ed = sum(int(r["edison"]) for r in ea); ours = sum(int(r["ours"]) for r in ea); both = sum(int(r["both"]) for r in ea)
        out["edison_audit"] = {"ventures": len(ea), "edison_names": ed, "our_names": ours, "both": both,
                               "recall_vs_edison": round(both / max(1, ed), 3), "ours_confirmed_by_edison": round(both / max(1, ours), 3),
                               "ventures_we_missed_entirely": sum(1 for r in ea if int(r["ours"]) == 0 and int(r["edison"]) > 0),
                               "ventures_edison_missed_entirely": sum(1 for r in ea if int(r["edison"]) == 0 and int(r["ours"]) > 0)}
    vd = rd("verify/verdicts.csv")
    if vd:
        c = collections.Counter(r["verdict"] for r in vd)
        out["verify"] = {"checked": len(vd), "confirmed": c["confirmed"], "other_source": c["confirmed_other_source"],
                         "not_supported": c["not_supported"], "unclear": c["unclear"]}
    lc = rd("edison_literature_check.csv")
    if lc:
        out["edison_literature"] = {"named": len(lc), "found": sum(1 for r in lc if r["in_deal_data"] != "no" or r["in_program_passes"] == "yes")}
    import glob
    xs = set()
    for f in glob.glob(os.path.join(D, "deal_passes", "input_x*.csv")):
        xs |= {r["key"] for r in csv.DictReader(open(f))}
    out["deepened"] = len(xs)
    out["deepen_passes"] = len(glob.glob(os.path.join(D, "deal_passes", "input_x*.csv")))
    out["deal_passes"] = len([f for f in glob.glob(os.path.join(D, "deal_passes", "input_*.csv")) if "input_x" not in f])
    # rows kept in deals.csv but not counted, by reason (all groups)
    nc = collections.Counter()
    for d in Dl:
        c = d["counted"]
        if c == "yes":
            continue
        nc["exit" if "exit" in c else "out_of_scope" if "out of scope" in c else "duplicate" if "duplicate" in c else
           "unconfirmed" if "unconfirmed" in c else "ownership_transfer" if "ownership transfer" in c else "other"] += 1
    out["not_counted"] = dict(nc)
    out["not_counted_total"] = sum(nc.values())
    out["out_of_scope_ventures"] = sum(1 for v in V if v.get("in_scope", "yes") != "yes")
    out["out_of_scope_by_reason"] = dict(collections.Counter(
        "duplicate" if "duplicate of" in v["in_scope"] else "nonprofit" if "nonprofit" in v["in_scope"] else "not_open"
        for v in V if v.get("in_scope", "yes") != "yes"))
    # sensitivity: only ventures whose main product passed the openness test outright (open_ok = yes), U1-U3
    okv = {v["key"] for v in V if v["open_ok"] == "yes"}
    c_open = collections.Counter(l["investor"] for l in core if l["key"] in okv)
    t_open = [n for n, _ in c_open.most_common(20)]
    out["sensitivity_open_yes"] = {
        "ventures_partial_with_links": len({l["key"] for l in core if l["key"] not in okv}),
        "ventures_yes_with_links": len({l["key"] for l in core if l["key"] in okv}),
        "links": sum(c_open.values()), "top20_overlap": len(set(t_all) & set(t_open)),
        "dropped_from_top20": [n for n in t_all if n not in t_open],
        "entered_top20": [n for n in t_open if n not in t_all]}
    # source-quality sensitivity across all four groups
    out["sensitivity_db_all"] = {"links": len(L), "funders": len({l["investor"] for l in L}),
                                 "links_strict": sum(1 for l in L if l["database_only"] != "1"),
                                 "funders_strict": len({l["investor"] for l in L if l["database_only"] != "1"})}
    out["thesis_kinds"] = dict(collections.Counter(r["thesis_kind"] for r in I if r.get("stated_open_source_thesis")))
    # U2 by funder type: links and ventures (for the crowdfunding wording)
    u2 = [l for l in L if l["universe"] == "U2"]
    out["u2_types"] = {t: {"links": sum(1 for l in u2 if tmap.get(l["investor"]) == t),
                           "ventures": len({l["key"] for l in u2 if tmap.get(l["investor"]) == t})}
                       for t in ("venture_firm", "corporate_venture", "crowdfunding", "angel", "government_grant",
                                 "philanthropy", "accelerator", "public_investor")}
    out["u2_kickstarter"] = len({l["key"] for l in u2 if l["investor"] == "Kickstarter backers"})
    # early rounds (pre-seed to Series A): records and distinct ventures for YC, for the wording of that table
    early = {"pre_seed", "seed", "angel", "accelerator", "series_a"}
    yc = [d for d in Dl if d["counted"] == "yes" and d["type"] in early and "Y Combinator" in (d["lead"] + " | " + d["investors"]).split(" | ")]
    out["yc_early"] = {"records": len(yc), "ventures": len({d["key"] for d in yc})}
    sp = rd("verify/spot_check_verdicts.csv")
    if sp:
        c = collections.Counter(r["verdict"].split(" (")[0] for r in sp)
        out["spot_check"] = {"links": len(sp), "confirmed": c["confirmed"], "unreadable": c["page not readable"],
                             "readable": len(sp) - c["page not readable"], "not_closed": c["round not closed"],
                             "not_checkable": c["not checkable"], "unclear_role": c["unclear role"],
                             "logo_or_loose": sum(1 for r in sp if r["verdict"].startswith("confirmed ("))}
    json.dump(out, open(os.path.join(D, "funders_numbers.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("U1-U3", "U1", "U2", "U3", "U4")}, indent=0)[:3500])


if __name__ == "__main__":
    main()
